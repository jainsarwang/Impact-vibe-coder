import os
import subprocess
import json  # Added this import
import google.generativeai as genai
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from dotenv import load_dotenv

load_dotenv()
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set.")
    raise ValueError("GEMINI_API_KEY environment variable not set.")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

class ReadmeExecutor:
    def __init__(self, project_name: str = "GestureVolumeControl"):
        self.project_dir = Path(f"{project_name}")
        self.readme_path = self.project_dir / "README.md"
        self.commands = {
            'setup': [],
            'frontend': [],
            'backend': [],
            'test': []
        }
    
    def extract_commands_with_gemini(self) -> Dict[str, List[str]]:
        """Use Gemini to intelligently extract commands from README.md"""
        try:
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
            
            prompt = f"""
            Analyze this README.md content and extract all commands that need to be executed 
            to setup and run the project. Categorize them into:
            1. Setup commands (installation, environment setup)
            2. Frontend commands (client-side execution)
            3. Backend commands (server-side execution)
            4. Test commands (testing the application)
            5. Never Execute commands (commands that should not be run) like git commands.
            6. When in readme you got the command to activate the virtual environment like this:
            ```
            source venv/bin/activate
            ```
            or
            ```
            .\venv\Scripts\activate
            ```
                you should not include the source command in the setup commands. Just run *environment_name*\Scripts\activate, Not include .bat with activate.

            Return only a JSON response with this structure:
            {{
                "setup": ["command1", "command2"],
                "frontend": ["command1", "command2"],
                "backend": ["command1", "command2"],
                "test": ["command1", "command2"]
            }}

            README.md content:
            {readme_content}
            """
            
            response = model.generate_content(prompt)
            return self._parse_gemini_response(response.text)
            
        except Exception as e:
            logger.error(f"Error extracting commands with Gemini: {e}")
            return self.commands
    
    def _parse_gemini_response(self, response: str) -> Dict[str, List[str]]:
        """Parse Gemini's response into command categories"""
        try:
            # Extract JSON from Gemini's response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            return json.loads(json_str)
        except Exception as e:
            logger.error(f"Error parsing Gemini response: {e}")
            return self.commands
    
    def execute_commands(self) -> bool:
        """Execute extracted commands in proper order"""
        if not self.readme_path.exists():
            logger.error(f"README.md not found at {self.readme_path}")
            return False
        
        self.commands = self.extract_commands_with_gemini()
        logger.info("Extracted commands:")
        logger.info(json.dumps(self.commands, indent=2))
        
        # Execute commands in sequence
        try:
            # 1. Setup commands
            if self.commands['setup']:
                logger.info("\n=== RUNNING SETUP COMMANDS ===")
                for cmd in self.commands['setup']:
                    self._run_command(cmd)
            
            # 2. Backend commands
            if self.commands['backend']:
                logger.info("\n=== RUNNING BACKEND COMMANDS ===")
                for cmd in self.commands['backend']:
                    self._run_command(cmd, new_terminal=True)
            
            # 3. Frontend commands
            if self.commands['frontend']:
                logger.info("\n=== RUNNING FRONTEND COMMANDS ===")
                for cmd in self.commands['frontend']:
                    self._run_command(cmd, new_terminal=True)
            
            # 4. Test commands
            if self.commands['test']:
                logger.info("\n=== RUNNING TEST COMMANDS ===")
                for cmd in self.commands['test']:
                    self._run_command(cmd)
            
            return True
        
        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return False
    
    def _run_command(self, command: str, new_terminal: bool = False) -> bool:
        """Execute a single command"""
        try:
            logger.info(f"Executing: {command}")
            
            if new_terminal and os.name == 'nt':  # Windows
                subprocess.Popen(
                    f'start cmd /k "{command} && pause"',
                    shell=True,
                    cwd=self.project_dir
                )
            elif new_terminal:  # Linux/Mac
                subprocess.Popen(
                    f'xterm -e "{command}; read"',
                    shell=True,
                    cwd=self.project_dir
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.project_dir,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                if result.stdout:
                    logger.info(result.stdout)
                if result.stderr:
                    logger.error(result.stderr)
            
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return False

# Example Usage
if __name__ == "__main__":
    executor = ReadmeExecutor("GestureVolumeControl")
    success = executor.execute_commands()
    if success:
        logger.info("All commands executed successfully!")
    else:
        logger.error("Some commands failed to execute")