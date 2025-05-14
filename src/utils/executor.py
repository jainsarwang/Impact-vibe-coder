import json
import logging
from concurrent.futures import ThreadPoolExecutor
import os
import re
import shlex
import subprocess
import sys
import traceback
from typing import Dict, List, Tuple

from src.graph.types import State


def extract_commands_from_readme(readme_file_path: str) -> Dict[str, List[str]]:
    """Extract and categorize executable commands from README.md"""
    try:
        with open(readme_file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        logging.debug(f"Error: File not found at {readme_file_path}")
        return {'venv': [], 'frontend': [], 'backend': [], 'other': []}
    except Exception as e:
        logging.debug(f"Error reading file: {e}")
        return {'venv': [], 'frontend': [], 'backend': [], 'other': []}

    # Updated pattern to handle comma-separated commands
    pattern = r'```(?:bash|sh)?(.*?)```|^\$\s*(.+)$|`([^`]+)`'
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
                for line in part.split(''):
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
    logging.debug("=== Executing Virtual Environment Commands ===")
    for cmd in command_groups['venv']:
        clean_cmd = cmd.strip().lstrip('$').strip()
        logging.debug(f">>> Executing: {clean_cmd}")

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
                logging.debug(f"✓ Virtual environment created at {venv_path}")
            continue

        if ('activate' in clean_cmd and 'Scripts' in clean_cmd) or clean_cmd.endswith('activate.bat'):
            if not venv_path:
                results[cmd] = (False, "No virtual environment created yet")
                logging.debug("✗ Cannot activate - no virtual environment created")
                continue
            
            scripts_path = os.path.join(venv_path, 'Scripts')
            os.environ['PATH'] = scripts_path + os.pathsep + os.environ['PATH']
            os.environ['VIRTUAL_ENV'] = venv_path
            results[cmd] = (True, f"Activated virtual environment at {venv_path}")
            logging.debug(f"✓ Activated virtual environment (Python: {sys.executable})")
            continue

    # Now execute other commands in parallel in separate terminals
    logging.debug("=== Executing Other Commands in Parallel ===")
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

def execute(state: State, project_requirement: str):
    """ Execute the commands in the command groups"""

    try:
        logging.debug("Executor started execution")
        requirement = json.loads(project_requirement)
        directory_structure = json.loads(state['directory_structure'])

        logging.debug(requirement)
        logging.debug("Step 1")
        ROOT_DIR = f"projects/{requirement['project_name']}"
        logging.debug("Step 2")

        for file in directory_structure['file_documentation'].keys():
            if 'readme' in file.lower():
                README_PATH = file

        logging.debug(f"ROOT Directory Path : {ROOT_DIR}")
        logging.debug(f"README File: {README_PATH}")

        # Removing any trailing slash ('/')
        if README_PATH.startswith('/'):
            README_PATH = README_PATH[1:]
        logging.debug("Step 3")

        # If no projects folder in starting, append it to readme
        if not README_PATH.startswith('projects'):
            README_PATH = f"projects/{README_PATH}"
            
        logging.debug("step 4")
        command_groups = extract_commands_from_readme(README_PATH)

        logging.debug("Extracted Commands:")
        logging.debug("Virtual Environment Commands:")
        for i, cmd in enumerate(command_groups['venv'], 1):
            logging.debug(f"{i}. {cmd}")

        logging.debug("Frontend Commands:")
        for i, cmd in enumerate(command_groups['frontend'], 1):
            logging.debug(f"{i}. {cmd}")

        logging.debug("Backend Commands:")
        for i, cmd in enumerate(command_groups['backend'], 1):
            logging.debug(f"{i}. {cmd}")

        logging.debug("Other Commands:")
        for i, cmd in enumerate(command_groups['other'], 1):
            logging.debug(f"{i}. {cmd}")

        # Execute commands
        logging.debug("=== Execution Started ===")
        results = execute_commands_parallel(command_groups, ROOT_DIR)

        # logging.debug summary
        logging.debug("=== Execution Summary ===")
        for cmd, (success, output) in results.items():
            status = "✓ PASS" if success else "✗ FAIL"
            logging.debug(f"{status}: {cmd}")
            if output and not success:
                logging.debug(f"   Reason: {output}")

        return True
    except Exception as e:
        logging.error(e)
        logging.error(traceback.format_exc(e))
        return False