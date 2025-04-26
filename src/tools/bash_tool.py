import logging
import subprocess
from typing import Annotated, Optional # Import Optional
from langchain_core.tools import tool
# Assuming .decorators import log_io exists and works
from .decorators import log_io
import os
import platform

# Initialize logger
logger = logging.getLogger(__name__)

# Define the tool with new optional parameters for file writing
@tool
@log_io
def bash_tool(
    cmd: Annotated[Optional[str], "The bash command to be executed. Use this *or* write_filepath/write_content."] = None,
    write_filepath: Annotated[Optional[str], "Optional: If provided, the tool will write the 'write_content' to this file path instead of executing 'cmd'."] = None,
    write_content: Annotated[Optional[str], "Optional: The content to write to 'write_filepath'. Required if 'write_filepath' is used."] = None,
):
    """
    Executes a bash command or writes content to a file, handling OS differences.

    Use either the 'cmd' parameter to execute a shell command, OR
    the 'write_filepath' and 'write_content' parameters together
    to write specific multi-line content to a file.

    If write_filepath is provided, the tool prioritizes writing the file.
    """
    logger.info(f"Attempting operation: cmd='{cmd}', write_filepath='{write_filepath}', write_content provided={write_content is not None}")

    # --- File Writing Logic ---
    if write_filepath is not None:
        if write_content is None:
            error_message = "Error: 'write_content' is required when 'write_filepath' is provided."
            logger.error(error_message)
            return error_message

        # Ensure the directory exists before writing the file
        dir_path = os.path.dirname(write_filepath)
        if dir_path: # Only try to create if there's a directory component in the path
            try:
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Ensured directory exists: {dir_path}")
            except Exception as e:
                error_message = f"Error ensuring directory {dir_path} exists: {str(e)}"
                logger.error(error_message)
                return error_message

        # Write the content to the file using Python's built-in functions
        try:
            # Use 'w' mode for writing (overwrites if file exists) and specify encoding
            with open(write_filepath, 'w', encoding='utf-8') as f:
                f.write(write_content)
            success_message = f"Successfully wrote content to {write_filepath}"
            logger.info(success_message)
            return success_message
        except Exception as e:
            error_message = f"Error writing content to file {write_filepath}: {str(e)}"
            logger.error(error_message)
            return error_message

    # --- Command Execution Logic (only if not writing a file) ---
    elif cmd is not None:
        logger.info(f"Executing Command: {cmd}") # Changed from Bash to generic Command
        try:
            # Removed the specific touch handler as the write_filepath logic covers file creation now
            # shell=True is necessary to handle commands like piping, redirection etc.
            result = subprocess.run(
                cmd, shell=True, check=True, text=True, capture_output=True
            )
            # Return stdout on success
            output = result.stdout
            # Optionally log stderr even on success if present (e.g., warnings)
            if result.stderr:
                logger.warning(f"Command produced stderr:\n{result.stderr}")

            return output.strip() if output else "Command executed successfully (no stdout)"
        except subprocess.CalledProcessError as e:
            error_message = f"Command failed with exit code {e.returncode}.\nStdout: {e.stdout}\nStderr: {e.stderr}"
            logger.error(error_message)
            return error_message
        except Exception as e:
            error_message = f"Error executing command: {str(e)}"
            logger.error(error_message)
            return error_message

    # --- Error case: No operation specified ---
    else:
        error_message = "Error: Either 'cmd' or 'write_filepath' and 'write_content' must be provided."
        logger.error(error_message)
        return error_message