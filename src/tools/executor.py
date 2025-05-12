import logging
import json
import os
import re # For parsing User_Manual.md
import subprocess
from typing import Annotated, Optional, Dict, Any, List, Tuple

# Assuming bash_tool and decorators are in the same directory or package
# from .decorators import log_io  # Assuming log_io is a generic decorator
# from .bash_tool import bash_tool # bash_tool is assumed to be a sync executor

# --- Mock decorators and bash_tool if not present for standalone testing ---
try:
    from .decorators import log_io
except ImportError:
    def log_io(func):
        def wrapper(*args, **kwargs):
            # Simplified mock logger for missing decorator
            # print(f"LOG_IO: Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            result = func(*args, **kwargs)
            # print(f"LOG_IO: {func.__name__} returned: {result}")
            return result
        return wrapper

try:
    from .bash_tool import bash_tool
except ImportError:
    def bash_tool(cmd: str, timeout: int):
        logger.info(f"MOCK bash_tool: cmd='{cmd}', timeout={timeout}")
        # Simulate simple echo for testing
        if "echo" in cmd:
            try:
                output = cmd.split("echo",1)[1].strip().strip("'").strip('"')
                return {"output": output, "status": "success (mocked)"}
            except IndexError:
                 return {"output": "Mock echo executed", "status": "success (mocked)"}
        return {"output": f"Mock execution of: {cmd}", "status": "success (mocked)"}
# --- End Mocks ---

# Initialize logger
logger = logging.getLogger(__name__)
# Basic logging config for demonstration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

PROJECTS_DIR = "./projects"
DEFAULT_COMMAND_TIMEOUT = 300 # seconds for synchronous commands via bash_tool
LAUNCHED_PROCESSES: Dict[str, subprocess.Popen] = {}


def sanitize_command(command: str) -> Optional[str]:
    """
    Sanitizes a command string (can be multi-line for scripts from fenced blocks).
    Rejects commands with '&&', '|', ';', '`', '$<', '${'.
    Path traversal '..' or absolute paths if they form the main command are also rejected.
    """
    command_preview = command[:100].replace('\n', '\\n') + ('...' if len(command) > 100 else '')
    if any(op in command for op in ["&&", "|", ";", "`", "$(", "${"]):
        logger.warning(f"Command sanitization failed: Forbidden operator in command. Preview: '{command_preview}'")
        return None

    # Basic check for path traversal or absolute paths as the command itself or its first part.
    # This is a heuristic. `python /path/to/script.py` might be caught if not careful.
    # For now, if a command line starts with '../' or '/', it's flagged.
    # This is to prevent `../dangerous_script.sh` or `/bin/rm -rf /` as the command.
    # It does NOT deeply inspect all arguments of a command.
    # The primary protection is running commands within the project_path CWD.
    lines = command.splitlines()
    if lines:
        first_line_stripped = lines[0].strip()
        if first_line_stripped.startswith("../") or first_line_stripped.startswith("/"):
            logger.warning(f"Command sanitization failed: Command line starts with '../' or '/'. Preview: '{command_preview}'")
            return None
    return command.strip()


def get_project_path(project_name: Optional[str]) -> Optional[str]:
    if not project_name:
        return None
    prospective_path = os.path.join(PROJECTS_DIR, project_name)
    normalized_path = os.path.normpath(prospective_path)

    # Security check: Ensure the normalized path is still within PROJECTS_DIR
    # os.path.commonprefix is not robust enough for this.
    # Check if abspath of normalized_path starts with abspath of PROJECTS_DIR
    abs_projects_dir = os.path.abspath(PROJECTS_DIR)
    abs_normalized_path = os.path.abspath(normalized_path)

    if not abs_normalized_path.startswith(abs_projects_dir):
        logger.error(f"Security Error: Project name '{project_name}' resolves to a path '{abs_normalized_path}' outside of the projects directory '{abs_projects_dir}'.")
        return None

    if not os.path.isdir(normalized_path):
        logger.info(f"Project directory not found at: {normalized_path}")
        return None
    return normalized_path


def _is_process_running(pid: int) -> bool:
    if pid <= 0: return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def _terminate_launched_process(process_key: str):
    proc = LAUNCHED_PROCESSES.pop(process_key, None)
    if proc:
        if proc.poll() is None: # Still running
            logger.info(f"Terminating process {process_key} (PID: {proc.pid})...")
            proc.terminate()
            try:
                proc.wait(timeout=10)
                logger.info(f"Process {process_key} (PID: {proc.pid}) terminated gracefully (exit code {proc.returncode}).")
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {process_key} (PID: {proc.pid}) did not terminate gracefully, killing.")
                proc.kill()
                proc.wait() # Ensure kill is processed
                logger.info(f"Process {process_key} (PID: {proc.pid}) killed (exit code {proc.returncode}).")
        else:
            logger.info(f"Process {process_key} (PID: {proc.pid}) was already terminated (exit code {proc.returncode}).")
    else:
        # This is normal if trying to stop a service that wasn't started or already stopped.
        pass # logger.info(f"No active process found for key '{process_key}' to terminate.")


@log_io
def manage_project_lifecycle(
    project_name: Annotated[Optional[str], "Name of the project directory. If omitted, auto-discovers."],
    action: Annotated[str, "Action: 'read_manual', 'execute', 'status', 'stop_services'"],
    custom_command: Annotated[Optional[str], "Optional custom command for 'execute' action."] = None
) -> Dict[str, Any]:
    logger.info(f"Manager called: project_name='{project_name}', action='{action}', custom_command='{custom_command}'")

    resolved_project_name = project_name
    if not resolved_project_name:
        resolved_project_name = discover_project_name()
        if not resolved_project_name:
            return {"error": "Project discovery failed: No suitable project found.", "action": action, "project_name": None}
        logger.info(f"Auto-discovered project directory: {resolved_project_name}")

    project_path = get_project_path(resolved_project_name)
    if not project_path:
        return {"error": f"Project '{resolved_project_name}' not found or access denied within '{PROJECTS_DIR}'.", "action": action, "project_name": resolved_project_name}

    manual_path = os.path.join(project_path, "User_Manual.md")
    if action in ["read_manual", "execute"] and not custom_command and not os.path.exists(manual_path):
         return {"error": f"'User_Manual.md' not found in {project_path}. This file is required for the action '{action}' when no custom command is provided.", "action": action, "project_name": resolved_project_name}
    
    requirements_path = os.path.join(project_path, "project_requirements.json")
    if not os.path.exists(requirements_path):
        logger.warning(f"'project_requirements.json' not found in {project_path}. Proceeding, but some project metadata might be unavailable.")

    try:
        if action == "read_manual":
            return read_project_manual(project_path, resolved_project_name)
        elif action == "execute":
            return execute_project_commands(project_path, resolved_project_name, custom_command)
        elif action == "status":
            return get_project_status(project_path, resolved_project_name)
        elif action == "stop_services":
            backend_key = f"{resolved_project_name}_backend_process"
            frontend_key = f"{resolved_project_name}_frontend_process"
            _terminate_launched_process(backend_key)
            _terminate_launched_process(frontend_key)
            return {
                "message": f"Attempted to stop services for project '{resolved_project_name}'.",
                "action": "stop_services", "project_name": resolved_project_name,
                "stopped_keys": [backend_key, frontend_key]
            }
        else:
            return {"error": f"Unknown action '{action}'. Valid actions are 'read_manual', 'execute', 'status', 'stop_services'.", "action": action, "project_name": resolved_project_name}
    except Exception as e:
        logger.exception(f"Unhandled exception during action '{action}' for '{resolved_project_name}'.")
        return {"error": f"Internal error during '{action}': {str(e)}", "action": action, "project_name": resolved_project_name}


def discover_project_name() -> Optional[str]:
    if not os.path.exists(PROJECTS_DIR) or not os.path.isdir(PROJECTS_DIR):
        logger.warning(f"Projects directory '{PROJECTS_DIR}' not found.")
        return None
    project_candidates = []
    for item_name in os.listdir(PROJECTS_DIR):
        item_path = os.path.join(PROJECTS_DIR, item_name)
        if os.path.isdir(item_path):
            req_path = os.path.join(item_path, "project_requirements.json")
            mtime = os.path.getmtime(item_path)
            logical_name, priority = item_name, 4 # Default: dir name, low priority
            if os.path.exists(req_path):
                priority = 2 # Has requirements file
                try:
                    with open(req_path, 'r', encoding='utf-8') as f: data = json.load(f)
                    p_name_json = data.get("project_name")
                    if p_name_json and isinstance(p_name_json, str):
                        logical_name, priority = p_name_json, 1 # Best: JSON name
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse {req_path} for dir {item_name}.")
                    priority = 3 # JSON exists but is invalid
            project_candidates.append({"dir_name": item_name, "logical_name": logical_name, "priority": priority, "mtime": mtime})

    if not project_candidates:
        logger.info(f"No project candidates found in '{PROJECTS_DIR}'.")
        return None

    project_candidates.sort(key=lambda x: (x["priority"], -x["mtime"])) # Sort by prio (lower is better), then mtime (newer is better)
    selected = project_candidates[0]
    logger.info(f"Discovered project directory: '{selected['dir_name']}' (Logical name: '{selected['logical_name']}', Priority: {selected['priority']})")
    return selected["dir_name"] # Return actual directory name


def read_project_manual(project_path: str, project_dir_name: str) -> Dict[str, Any]:
    manual_path = os.path.join(project_path, "User_Manual.md")
    # This check is present in manage_project_lifecycle, but defensive coding is good.
    if not os.path.exists(manual_path):
        return {"error": f"User_Manual.md not found in {project_path}", "project_name": project_dir_name, "action": "read_manual"}
    try:
        with open(manual_path, 'r', encoding='utf-8') as f: content = f.read()
        return {"message": f"Successfully read manual for project '{project_dir_name}'.", "manual_content": content, "project_name": project_dir_name, "action": "read_manual"}
    except Exception as e:
        logger.exception(f"Error reading manual for {project_dir_name} at {manual_path}")
        return {"error": f"Could not read manual: {str(e)}", "project_name": project_dir_name, "action": "read_manual"}


def _launch_script_async(script_type: str, commands: List[str], project_path: str, project_dir_name: str) -> Tuple[Optional[int], str]:
    if not commands:
        return None, f"No {script_type} commands to launch for '{project_dir_name}'."

    full_script = " && ".join(commands) # Individual commands must be pre-sanitized
    process_key = f"{project_dir_name}_{script_type.lower()}_process"
    _terminate_launched_process(process_key) # Ensure any old one with the same key is gone

    logger.info(f"Launching {script_type} script for '{project_dir_name}' in '{project_path}': {full_script[:200]}{'...' if len(full_script)>200 else ''}")
    try:
        # For production, consider redirecting stdout/stderr to log files:
        # stdout_log = os.path.join(project_path, f"{script_type.lower()}_stdout.log")
        # stderr_log = os.path.join(project_path, f"{script_type.lower()}_stderr.log")
        # with open(stdout_log, "ab") as sout, open(stderr_log, "ab") as serr:
        #     proc = subprocess.Popen(
        #         full_script, cwd=project_path, shell=True,
        #         stdout=sout, stderr=serr,
        #         start_new_session=True # Makes it easier to terminate process group if needed
        #     )
        # For now, using PIPE for easier observation in tests/dev
        proc = subprocess.Popen(
            full_script, cwd=project_path, shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            start_new_session=True
        )
        LAUNCHED_PROCESSES[process_key] = proc
        msg = f"{script_type} script for '{project_dir_name}' launched successfully with PID {proc.pid}."
        logger.info(msg)
        return proc.pid, msg
    except Exception as e:
        msg = f"Failed to launch {script_type} script for '{project_dir_name}': {str(e)}"
        logger.exception(msg) # Log full traceback
        return None, msg


def execute_project_commands(project_path: str, project_dir_name: str, custom_command_str: Optional[str]) -> Dict[str, Any]:
    if custom_command_str:
        sanitized_custom_cmd = sanitize_command(custom_command_str)
        if not sanitized_custom_cmd:
            return {"error": f"Custom command '{custom_command_str}' failed sanitization.", "project_name": project_dir_name, "action": "execute"}
        
        full_cmd_for_bash_tool = f"cd \"{project_path}\" && {sanitized_custom_cmd}"
        logger.info(f"Executing custom command for '{project_dir_name}': {full_cmd_for_bash_tool}")
        try:
            result_output = bash_tool(cmd=full_cmd_for_bash_tool, timeout=DEFAULT_COMMAND_TIMEOUT)
            return {"message": f"Custom command executed for '{project_dir_name}'.", "command": sanitized_custom_cmd, "output": result_output, "project_name": project_dir_name, "execution_type": "custom_synchronous", "action": "execute"}
        except Exception as e:
            logger.exception(f"Error executing custom command '{sanitized_custom_cmd}' for '{project_dir_name}'")
            return {"error": f"Failed to execute custom command: {str(e)}", "project_name": project_dir_name, "action": "execute"}

    # --- Manual Parsing Logic ---
    manual_path = os.path.join(project_path, "User_Manual.md")
    # This check is technically redundant due to manage_project_lifecycle, but good for direct calls.
    if not os.path.exists(manual_path): 
        return {"error": f"'User_Manual.md' not found in {project_path} (required for 'execute' without custom command).", "project_name": project_dir_name, "action": "execute"}

    backend_commands: List[str] = []
    frontend_commands: List[str] = []
    current_section_type: Optional[str] = None # "backend", "frontend", or None
    
    # Regex patterns for section identification
    explicit_backend_marker = re.compile(r"^#\s*Backend$", re.IGNORECASE)
    explicit_frontend_marker = re.compile(r"^#\s*Frontend$", re.IGNORECASE)
    # Matches "## Backend Setup", "### Run the backend", etc.
    keyword_heading_pattern = re.compile(r"^#+\s+.*?\b(?P<type>backend|frontend)\b.*", re.IGNORECASE)
    # Matches "1. **Start the Backend Service:**" or "#### Configure Frontend:"
    context_infer_pattern = re.compile(
        r"^(?:#+|\d+\.?\s*\*+)\s*.*?\b(?P<type>backend|frontend)\b.*?(?::|\*+)?$", 
        re.IGNORECASE
    )
    any_other_heading = re.compile(r"^#+\s+.*") # Any other Markdown heading to reset context

    in_fenced_code_block = False
    fenced_code_buffer: List[str] = []

    try:
        with open(manual_path, 'r', encoding='utf-f8') as f: manual_content = f.read()
        
        lines = manual_content.splitlines()
        for line_num, line_text in enumerate(lines, 1):
            stripped_line = line_text.strip()

            # --- Fenced Code Block Handling ---
            if stripped_line.startswith("```"):
                if in_fenced_code_block: # End of block
                    in_fenced_code_block = False
                    if fenced_code_buffer and current_section_type:
                        command_content = "\n".join(fenced_code_buffer).strip()
                        if command_content: # Ensure not empty block
                            sanitized_cmd = sanitize_command(command_content)
                            if sanitized_cmd:
                                if current_section_type == "backend": backend_commands.append(sanitized_cmd)
                                elif current_section_type == "frontend": frontend_commands.append(sanitized_cmd)
                                else: pass # Should not happen if current_section_type is correctly one of these
                            else: logger.warning(f"Manual Parse: Sanitization failed for fenced code block (section: {current_section_type}) near line {line_num} in '{project_dir_name}'. Content preview: '{command_content[:100].replace(chr(10), ' // ')}...'")
                    fenced_code_buffer = [] # Reset buffer
                else: # Start of block
                    in_fenced_code_block = True
                continue # Process next line

            if in_fenced_code_block:
                # Skip language hint line if it's just the language name, e.g. "bash" on its own line after ```
                if not fenced_code_buffer and re.fullmatch(r"^[a-zA-Z0-9_-]+$", stripped_line):
                    pass # It's likely a language hint like "bash", don't add to command buffer
                else:
                    fenced_code_buffer.append(line_text) # Keep original line text for multi-line scripts
                continue # Process next line
            
            # --- Section Determination (only if not in a code block) ---
            new_section_assigned_this_line = False
            # Highest precedence: explicit markers like "#Backend"
            if explicit_backend_marker.fullmatch(stripped_line):
                current_section_type = "backend"; new_section_assigned_this_line = True
            elif explicit_frontend_marker.fullmatch(stripped_line):
                current_section_type = "frontend"; new_section_assigned_this_line = True
            else:
                # Second precedence: headings with keywords like "## Backend Setup"
                match_kw_heading = keyword_heading_pattern.match(stripped_line)
                if match_kw_heading:
                    current_section_type = match_kw_heading.group("type").lower()
                    new_section_assigned_this_line = True
                else:
                    # Third precedence: inferred context from list items/subheadings like "1. **Start Backend**"
                    match_context_infer = context_infer_pattern.match(stripped_line)
                    if match_context_infer:
                        current_section_type = match_context_infer.group("type").lower()
                        new_section_assigned_this_line = True
                    # Lowest precedence: any other heading resets context to None
                    elif any_other_heading.match(stripped_line):
                        current_section_type = None; new_section_assigned_this_line = True
            
            if new_section_assigned_this_line:
                logger.debug(f"Manual Parse ({project_dir_name}, L{line_num}): Section context changed to '{current_section_type}' by line: '{stripped_line}'")
                continue # Don't process this line as a command if it defined/reset a section

            # --- Inline Command Extraction (e.g., `my-command`) ---
            if current_section_type and stripped_line.startswith('`') and stripped_line.endswith('`'):
                command_from_manual = stripped_line.strip('`').strip()
                if command_from_manual: # Ensure not empty ``
                    sanitized_cmd = sanitize_command(command_from_manual)
                    if sanitized_cmd:
                        if current_section_type == "backend": backend_commands.append(sanitized_cmd)
                        elif current_section_type == "frontend": frontend_commands.append(sanitized_cmd)
                        else: pass # Should not happen
                    else: logger.warning(f"Manual Parse: Sanitization failed for inline command '{command_from_manual}' (section: {current_section_type}) near line {line_num} in '{project_dir_name}'.")

    except Exception as e:
        logger.exception(f"Error parsing User_Manual.md for '{project_dir_name}'")
        return {"error": f"Failed to parse User_Manual.md: {str(e)}", "project_name": project_dir_name, "action": "execute"}

    if not backend_commands and not frontend_commands:
        logger.info(f"No executable backend or frontend commands found after parsing User_Manual.md for '{project_dir_name}'.")
        return {"message": f"No executable backend or frontend commands found in User_Manual.md for '{project_dir_name}'.", "project_name": project_dir_name, "action": "execute", "details": {"backend_launch": {"commands_found":[]}, "frontend_launch": {"commands_found":[]}}}

    results = {}
    backend_pid, backend_status_msg = _launch_script_async("Backend", backend_commands, project_path, project_dir_name)
    results["backend_launch"] = {"pid": backend_pid, "status_message": backend_status_msg, "commands_found": backend_commands}

    frontend_pid, frontend_status_msg = _launch_script_async("Frontend", frontend_commands, project_path, project_dir_name)
    results["frontend_launch"] = {"pid": frontend_pid, "status_message": frontend_status_msg, "commands_found": frontend_commands}
    
    return {"message": f"Service launch attempt for '{project_dir_name}' from User_Manual.md.", "project_name": project_dir_name, "execution_type": "manual_asynchronous_services", "details": results, "action": "execute"}


def get_project_status(project_path: str, project_dir_name: str) -> Dict[str, Any]:
    status_indicators = {
        "pid_file_generic": os.path.join(project_path, "app.pid"), # Example
        "lock_file": os.path.join(project_path, ".lock"),       # Example
    }
    checked_files: Dict[str, Dict[str, Any]] = {}
    has_file_evidence = False

    for key, path_to_check in status_indicators.items():
        exists = os.path.exists(path_to_check)
        checked_files[key] = {"path": path_to_check, "exists": exists}
        if exists: has_file_evidence = True
    
    launched_services_status = {}
    for type_key_lower in ["backend", "frontend"]: # Iterate with lowercase for process_map_key
        process_map_key = f"{project_dir_name}_{type_key_lower}_process"
        desc_capitalized = type_key_lower.capitalize()
        proc = LAUNCHED_PROCESSES.get(process_map_key) # Use get to avoid KeyError
        
        if proc:
            is_running_poll = proc.poll() is None # Check Popen's internal state
            pid = proc.pid
            
            # If poll says it's stopped, double-check with OS, then clean up if confirmed.
            # This handles cases where the process died but Popen object wasn't updated yet, or if Popen is stale.
            if not is_running_poll:
                if not _is_process_running(pid): # Confirmed dead by OS
                    logger.info(f"Process {process_map_key} (PID {pid}) confirmed stopped by OS, removing from active registry if present.")
                    LAUNCHED_PROCESSES.pop(process_map_key, None) # Ensure removal
                    launched_services_status[desc_capitalized] = {"registered_pid": pid, "status": "stopped", "return_code": proc.returncode}
                else: # Poll says stopped, but OS says running - unusual, trust OS for "running"
                    launched_services_status[desc_capitalized] = {"registered_pid": pid, "status": "running_os_override", "return_code": None}
            else: # Poll says it's running
                 launched_services_status[desc_capitalized] = {"registered_pid": pid, "status": "running", "return_code": None}
        else: # Not in LAUNCHED_PROCESSES
            launched_services_status[desc_capitalized] = {"status": "not_managed_or_stopped_previously"}
            
    return {
        "message": f"Status check for project '{project_dir_name}'.",
        "project_name": project_dir_name, "action": "status",
        "file_indicators": {"has_evidence": has_file_evidence, "checked": checked_files},
        "launched_services": launched_services_status
    }


if __name__ == '__main__':
    # --- Test Setup ---
    print("--- Setting up test environment ---")
    if os.path.exists(PROJECTS_DIR):
        import shutil
        # shutil.rmtree(PROJECTS_DIR) # Clean slate for testing
    os.makedirs(PROJECTS_DIR, exist_ok=True)

    # Create the MultiplicationTableGenerator project for testing
    p_mult_dir = "MultiplicationTableGenerator"
    p_mult_path = os.path.join(PROJECTS_DIR, p_mult_dir)
    os.makedirs(p_mult_path, exist_ok=True)
    # Create a dummy requirements.txt
    with open(os.path.join(p_mult_path, "requirements.txt"), "w") as f:
        f.write("Flask==2.0.1\n") # Example content
    # Create a dummy backend/app.py
    os.makedirs(os.path.join(p_mult_path, "backend"), exist_ok=True)
    with open(os.path.join(p_mult_path, "backend", "app.py"), "w") as f:
        f.write("print('Mock Flask backend app.py running')\n"
                "import time; time.sleep(60) # Keep alive for testing\n")
    # Create a dummy frontend/templates/index.html
    os.makedirs(os.path.join(p_mult_path, "frontend", "templates"), exist_ok=True)
    with open(os.path.join(p_mult_path, "frontend", "templates", "index.html"), "w") as f:
        f.write("<h1>Mock Frontend</h1>\n")

    # User_Manual.md for MultiplicationTableGenerator
    manual_content_mult = """
# Multiplication Table Generator Web Application

## Overview
This web application allows users to enter a number and generate its multiplication table.

## Prerequisites
Before running the application, ensure you have the following installed:
1.  **Python:** Make sure you have Python 3.6 or higher installed.
2.  **Navigate to the Project Directory:**
    ```bash
    cd MultiplicationTableGenerator
    ```

## Running the Application

1.  **Install Backend Dependencies:**
    Navigate to the `MultiplicationTableGenerator` directory and run the following command:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Start the Backend:**
    Run the Flask application:
    ```bash
    python backend/app.py
    ```
    This will start the Flask development server. The backend will be running on `http://127.0.0.1:5001` (using 5001 for test).

3.  **Start the Frontend:**
    Serve it using Python's built-in HTTP server.
    ```bash
    python -m http.server 5002 --bind 127.0.0.1
    ```
    Open your web browser and go to `http://localhost:5002/frontend/templates/index.html`.

## Using the Application
...
## Troubleshooting
...
"""
    with open(os.path.join(p_mult_path, "User_Manual.md"), "w") as f:
        f.write(manual_content_mult)

    # --- Test Execution ---
    print(f"\n--- Test: Execute '{p_mult_dir}' from its User_Manual.md ---")
    # Make sure the project is discoverable or explicitly name it
    os.utime(p_mult_path, None) # Update mtime to make it discoverable if None is used for project_name

    result_exec = manage_project_lifecycle(project_name=p_mult_dir, action="execute")
    print(json.dumps(result_exec, indent=2))

    if result_exec.get("details", {}).get("backend_launch", {}).get("pid") or \
       result_exec.get("details", {}).get("frontend_launch", {}).get("pid"):
        print("\n--- Waiting for services to potentially start (5s)... ---")
        import time
        time.sleep(5)

        print(f"\n--- Test: Get status for '{p_mult_dir}' ---")
        result_status = manage_project_lifecycle(project_name=p_mult_dir, action="status")
        print(json.dumps(result_status, indent=2))

        print(f"\n--- Test: Stop services for '{p_mult_dir}' ---")
        result_stop = manage_project_lifecycle(project_name=p_mult_dir, action="stop_services")
        print(json.dumps(result_stop, indent=2))

        time.sleep(1) # Give a moment for termination
        print(f"\n--- Test: Get status for '{p_mult_dir}' after stopping ---")
        result_status_after_stop = manage_project_lifecycle(project_name=p_mult_dir, action="status")
        print(json.dumps(result_status_after_stop, indent=2))
    else:
        print("\n--- Services did not launch, skipping status and stop tests. Check logs for parsing issues. ---")
        print("Expected backend commands:", result_exec.get("details", {}).get("backend_launch", {}).get("commands_found"))
        print("Expected frontend commands:", result_exec.get("details", {}).get("frontend_launch", {}).get("commands_found"))


    print("\n--- Test: Read manual for a non-existent project ---")
    result_read_non_existent = manage_project_lifecycle(project_name="non_existent_project_123", action="read_manual")
    print(json.dumps(result_read_non_existent, indent=2))
    assert "error" in result_read_non_existent
    assert "not found" in result_read_non_existent["error"]

    print("\n--- Test: Execute for project without User_Manual.md (but dir exists) ---")
    p_no_manual_dir = "project_no_manual"
    p_no_manual_path = os.path.join(PROJECTS_DIR, p_no_manual_dir)
    os.makedirs(p_no_manual_path, exist_ok=True)
    with open(os.path.join(p_no_manual_path, "project_requirements.json"), "w") as f:
        json.dump({"project_name": "App Without Manual"}, f) # Make it discoverable
    os.utime(p_no_manual_path, None)

    result_exec_no_manual = manage_project_lifecycle(project_name=p_no_manual_dir, action="execute")
    print(json.dumps(result_exec_no_manual, indent=2))
    assert "error" in result_exec_no_manual
    assert "'User_Manual.md' not found" in result_exec_no_manual["error"]


    # --- Final Cleanup of any stray processes ---
    print("\n--- Final process cleanup ---")
    active_keys = list(LAUNCHED_PROCESSES.keys())
    if active_keys:
        print(f"Terminating remaining managed processes: {active_keys}")
        for key_to_stop in active_keys:
            _terminate_launched_process(key_to_stop)
    else:
        print("No active managed processes found to clean up.")
    
    # Optional: remove test projects directory
    # import shutil
    # if os.path.exists(PROJECTS_DIR):
    #     shutil.rmtree(PROJECTS_DIR)
    # print(f"Test directory {PROJECTS_DIR} removed.")

    print("\n--- All Tests Complete ---")