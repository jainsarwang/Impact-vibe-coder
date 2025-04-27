import logging
import json
import os
import zipfile
from typing import Annotated, Optional
from langchain_core.tools import tool
from .decorators import log_io  # Assuming this exists

logger = logging.getLogger(__name__)

@tool
@log_io
def project_zip_tool(
    json_path: Annotated[Optional[str], "Path to the JSON file containing project requirements. Defaults to 'project_requirements.json'"] = None,
    output_dir: Annotated[Optional[str], "Directory where the zip file should be created. Defaults to current directory"] = None,
    cleanup: Annotated[Optional[bool], "Whether to delete the zip file after creation (for web delivery). Default False"] = False,
):
    """
    Creates a zip archive of a project directory specified in a JSON file.
    
    The JSON file must contain a 'project_name' field pointing to an existing directory.
    Creates a zip file with the same name as the project.
    
    Args:
        json_path: Path to JSON file (default 'project_requirements.json')
        output_dir: Where to save the zip (default current directory)
        cleanup: Remove zip after creation (for web delivery scenarios)
    
    Returns:
        str: Success message or error description
    """
    # Set defaults
    json_path = json_path or 'project_requirements.json'
    output_dir = output_dir or os.getcwd()
    
    logger.info(f"Starting project zip creation from {json_path}")
    
    try:
        # Step 1: Read JSON file
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            error_msg = f"JSON file not found at {json_path}"
            logger.error(error_msg)
            return error_msg
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON in {json_path}: {str(e)}"
            logger.error(error_msg)
            return error_msg

        # Step 2: Get project name
        project_name = data.get('project_name')
        if not project_name:
            error_msg = "No 'project_name' field found in JSON"
            logger.error(error_msg)
            return error_msg

        # Step 3: Verify project directory exists
        project_dir = os.path.abspath(project_name)
        if not os.path.isdir(project_dir):
            error_msg = f"Project directory not found: {project_dir}"
            logger.error(error_msg)
            return error_msg

        # Step 4: Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 5: Create zip file
        zip_filename = os.path.join(output_dir, f"{project_name}.zip")
        try:
            with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(project_name):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=project_name)
                        zipf.write(file_path, arcname=arcname)
        except Exception as e:
            error_msg = f"Failed to create zip: {str(e)}"
            logger.error(error_msg)
            return error_msg

        # Step 6: Return success or clean up
        success_msg = f"Successfully created {zip_filename}"
        logger.info(success_msg)
        
        if cleanup:
            try:
                os.remove(zip_filename)
                logger.info(f"Cleanup: Removed {zip_filename}")
            except Exception as e:
                logger.warning(f"Could not remove {zip_filename}: {str(e)}")
        
        return success_msg

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.exception(error_msg)
        return error_msg