import re
import os
import sys
import subprocess
import shlex
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import queue
 
# Use raw strings for Windows paths or double backslashes
file_path = r"D:\Data Science\Impact\Impact-vibe-coder-Rishabh-Git\Exector\readme.md"
file_path_2 = r"D:\Data Science\Impact\Impact-vibe-coder-Rishabh-Git\Exector"
 
def extract_commands_from_readme(file_path: str) -> Dict[str, List[str]]:
    """Extract and categorize executable commands from README.md"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return {'venv': [], 'frontend': [], 'backend': [], 'other': []}
    except Exception as e:
        print(f"Error reading file: {e}")
        return {'venv': [], 'frontend': [], 'backend': [], 'other': []}
 
    # Updated pattern to handle comma-separated commands
    pattern = r'```(?:bash|sh)?\n(.*?)```|^\$\s*(.+)$|`([^`\n]+)`'
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
   
    venv_commands = []
    frontend_commands = []
    backend_commands = []
    other_commands = []
   
    # Virtual environment indicators (highest priority)
    venv_keywords = ['venv', 'virtualenv', 'activate', 'activate.bat', 'scripts\\activate']
   
    # Frontend indicators
    frontend_keywords = ['frontend', 'npm', 'yarn', 'streamlit', 'react', 'angular',
                        'vue', 'svelte', 'webpack', 'vite', 'next', 'nuxt']
    # Backend indicators
    backend_keywords = ['backend', 'pip', 'django', 'flask', 'fastapi',
                    'uvicorn', 'gunicorn', 'node server', 'express', 'migrate']
 
    for match in matches:
        cmd = match[0] or match[1] or match[2]
        if cmd.strip():
            # Split by commas first, then by newlines
            for part in cmd.split(','):
                for line in part.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Normalize for case-insensitive comparison
                        lower_line = line.lower()
                       
                        # Check for venv commands first (highest priority)
                        if any(keyword in lower_line for keyword in venv_keywords):
                            venv_commands.append(line)
                        # Check for virtual environment creation
                        elif ('python' in lower_line and ('venv' in lower_line or 'virtualenv' in lower_line)):
                            venv_commands.append(line)
                        # Check for frontend commands
                        elif any(keyword in lower_line for keyword in frontend_keywords):
                            frontend_commands.append(line)
                        # Special case for streamlit
                        elif ('streamlit' in lower_line and 'run' in lower_line):
                            frontend_commands.append(line)
                        # Check for backend commands
                        elif any(keyword in lower_line for keyword in backend_keywords):
                            backend_commands.append(line)
                        # Python commands that aren't venv-related
                        elif 'python' in lower_line:
                            backend_commands.append(line)
                        else:
                            other_commands.append(line)
 
    def is_executable_command(cmd):
        if re.search(r'git\s+(clone|pull|fetch|remote\s+add)', cmd, re.IGNORECASE):
            return False
        return (re.search(r'[/.=-]', cmd) or
                len(cmd.split()) > 1 or
                re.match(r'^(php|npm|composer|python|pip|docker|streamlit)\b', cmd, re.IGNORECASE))
 
    return {
        'venv': [cmd for cmd in venv_commands if is_executable_command(cmd)],
        'frontend': [cmd for cmd in frontend_commands if is_executable_command(cmd)],
        'backend': [cmd for cmd in backend_commands if is_executable_command(cmd)],
        'other': [cmd for cmd in other_commands if is_executable_command(cmd)]
    }
 
def execute_in_new_terminal(cmd: str, working_dir: str, category: str) -> Tuple[bool, str]:
    """Execute command in a new terminal window"""
    try:
        if sys.platform == 'win32':
            # For Windows, use start cmd to open new terminal
            process = subprocess.run(
                f'start cmd /k "cd /d {working_dir} && {cmd} && echo [{category}] Command completed && pause"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
        else:
            # For Unix/Mac, use xterm or similar
            process = subprocess.run(
                f'xterm -e "cd {working_dir} && {cmd} && echo [{category}] Command completed && read"',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
       
        return (True, f"Command executed in new {category} terminal")
    except Exception as e:
        return (False, str(e))
 
def execute_commands_parallel(command_groups: Dict[str, List[str]], working_dir: str = None) -> Dict[str, Tuple[bool, str]]:
    """Execute commands in parallel with virtual env first"""
    results = {}
    venv_path = None
 
    # First execute venv commands sequentially
    print("\n=== Executing Virtual Environment Commands ===")
    for cmd in command_groups['venv']:
        clean_cmd = cmd.strip().lstrip('$').strip()
        print(f"\n>>> Executing: {clean_cmd}")
 
        if clean_cmd.startswith('python -m venv '):
            venv_path = clean_cmd.split('python -m venv ')[1].strip()
            result = subprocess.run(
                shlex.split(clean_cmd),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            success = result.returncode == 0
            results[cmd] = (success, result.stdout.strip() or result.stderr.strip())
            if success:
                print(f"✓ Virtual environment created at {venv_path}")
            continue
 
        if ('activate' in clean_cmd and 'Scripts' in clean_cmd) or clean_cmd.endswith('activate.bat'):
            if not venv_path:
                results[cmd] = (False, "No virtual environment created yet")
                print("✗ Cannot activate - no virtual environment created")
                continue
           
            scripts_path = os.path.join(venv_path, 'Scripts')
            os.environ['PATH'] = scripts_path + os.pathsep + os.environ['PATH']
            os.environ['VIRTUAL_ENV'] = venv_path
            results[cmd] = (True, f"Activated virtual environment at {venv_path}")
            print(f"✓ Activated virtual environment (Python: {sys.executable})")
            continue
 
    # Now execute other commands in parallel in separate terminals
    print("\n=== Executing Other Commands in Parallel ===")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Submit frontend commands
        for cmd in command_groups['frontend']:
            executor.submit(
                lambda c: results.update({c: execute_in_new_terminal(c, working_dir, 'frontend')}),
                cmd
            )
       
        # Submit backend commands
        for cmd in command_groups['backend']:
            executor.submit(
                lambda c: results.update({c: execute_in_new_terminal(c, working_dir, 'backend')}),
                cmd
            )
       
        # Submit other commands
        for cmd in command_groups['other']:
            executor.submit(
                lambda c: results.update({c: execute_in_new_terminal(c, working_dir, 'other')}),
                cmd
            )
 
    return results
 
if __name__ == "__main__":
    # Extract and categorize commands
    command_groups = extract_commands_from_readme(file_path)
   
    print("\nExtracted Commands:")
    print("\nVirtual Environment Commands:")
    for i, cmd in enumerate(command_groups['venv'], 1):
        print(f"{i}. {cmd}")
   
    print("\nFrontend Commands:")
    for i, cmd in enumerate(command_groups['frontend'], 1):
        print(f"{i}. {cmd}")
   
    print("\nBackend Commands:")
    for i, cmd in enumerate(command_groups['backend'], 1):
        print(f"{i}. {cmd}")
   
    print("\nOther Commands:")
    for i, cmd in enumerate(command_groups['other'], 1):
        print(f"{i}. {cmd}")
 
    # Execute commands
    print("\n=== Execution Started ===")
    results = execute_commands_parallel(command_groups, file_path_2)
 
    # Print summary
    print("\n=== Execution Summary ===")
    for cmd, (success, output) in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {cmd}")
        if output and not success:
            print(f"   Reason: {output}")
 
 
 