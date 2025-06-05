from langchain_core.tools import tool
import logging
from .decorators import log_io
from ..service import db
from ..utils.session_manager import SessionManager

collection = db["session"]

@tool
@log_io
def read_file_tool(path: str) -> str:
    """
    Read the description of the file from mongo database.
    
    Args:
        path (str): The path of the file to look up
        
    Returns:
        str: The description of the file if found, otherwise "File not found" or error message.
    """
    logging.info(f"Reading file description for path: {path}")
    try:
        path = path.replace("\\", "/")  # Normalize path to use forward slashes
        if path.startswith("projects"):
            path = path.split("/",1)[-1]  # Remove leading slash and get the last part of the path
            if not path:
                logging.error(f"Invalid path provided: {path}")
                return
        # Get the current session I
        session_id = SessionManager.get()
        document = collection.find_one({"session_id": session_id})
        logging.info(f"Session found for session ID: {session_id}")            
        if not document:
            logging.error(f"Session not found for session ID: {session_id}")
            return "Session not found"
        # Search through the checklist array
        for item in document["checklist"]:
            if not item:
                logging.warning("Invalid item in checklist, skipping.")
                continue
            if item.get("file_path") == path:
                logging.info(f"File found in checklist for path: {item.get("file_path")}")
                logging.info(f"Found file description: {str(item.get("description"))}")
                return str(item.get("description"))
            
        logging.warning(f"File not found in checklist for path: {path}")
        return "File not found in checklist"
        
    except Exception as e:
        return f"Error reading file: {str(e)}"