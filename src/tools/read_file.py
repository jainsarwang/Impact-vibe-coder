from langchain_core.tools import tool
from .decorators import log_io
from pymongo import MongoClient
from ..utils.session_manager import SessionManager
import logging

client = MongoClient("mongodb://localhost:27017")
db = client["impact_vibe_coder"]
db = db["session"]

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
        session_id = SessionManager.get()
        document = db.find_one({"session_id": session_id})
        
        if not document:
            return "Session not found"
            
        # Search through the checklist array
        for item in document.get("checklist", []):
            if item.get("file_path") == path:
                logging.info(f"Found file description: {item.get('description', 'No description available')}")
                return item.get("description", "No description available")
            
        logging.warning(f"File not found in checklist for path: {path}")
        return "File not found in checklist"
        
    except Exception as e:
        return f"Error reading file: {str(e)}"