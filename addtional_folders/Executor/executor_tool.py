# llm to extract commands from a readme.md file and execute them in parallel using threads
from datetime import datetime, da
import logging
import json
logger = logging.getLogger(__name__)
from typing import Literal


import subprocess
import shlex
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List
import logging
import queue


def commands_extractor(state: State) -> Command[Literal["supervisor"]]:
    """
    Function to extract commands from a readme.md file
    """
    
    logger.info("commands_extractor called")
    
    data = json.loads(state.get('directory_structure', '{}'))
    if not data or 'project_overview' not in data:
        logger.warning("No project overview found in directory structure")
        return Command(goto='supervisor')
    project_name = data['project_overview']['name']
    if not data or 'project_overview' not in data:
        logger.warning("Project Name not found or fetched from directory structure")
        return Command(goto='supervisor')
    
    readme_path = f"projects\{project_name}\README.md"
    prompt_vars = {
    "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
    }
    
    readme_content = ""
    with open(readme_path, 'w') as file:
        file.write(readme_content)
    logger.info(f"Dummy README.md created at: {readme_content}")
    
    system_prompt = """
    You are an expert in extracting commands from a readme.md file.
    Your task is to extract all the commands from the readme.md file and return them in a list format.
    ***Dont Include git commands in the list***
    ***Dont Include git clone and any other related commands in the list***
    ***Do not include any other information in the list, just the commands.***
    The commands should be in the format of a list of strings.
    The commands should be executable in a terminal.
    The commands should be extracted from the readme.md file located at {readme_path}.
    
    Example for Output for better understanding:
    [
        python -m venv .venv
        .venv\Scripts\activate.bat
        pip install opencv-python numpy comtypes pycaw mediapipe
        python main.py
        python -m pip install --upgrade pip       
    ]
    
    *Note: In case of python creating venv and executing virtual environment commands first
    *Note: In case of Node , React , express or vite  no creation of venv is required
    """
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": readme_content
        }
    ]
    llm = get_llm_by_type("basic")
    response = llm.invoke(messages)
    full_response = response.content

    logger.debug(f"Current state messages: {state['messages']}")
    logger.info(f"commands Extractor Response: {full_response}")
    
    execute_commands(full_response)
    
    
def execute_commands(state: State):
    """
    Function to execute commands in parallel using threads
    """
    command_list = commands_extractor(state)
    logger.info("Executing commands in parallel")
    
    def run_command(command: str):
        """Function to run a single command"""
        try:
            logger.info(f"Running command: {command}")
            result = subprocess.run(shlex.split(command), check=True, capture_output=True, text=True)
            logger.info(f"Command output: {result.stdout}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {command}\nError: {e.stderr}")
    
    # Use ThreadPoolExecutor to run commands in parallel
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(run_command, command_list)