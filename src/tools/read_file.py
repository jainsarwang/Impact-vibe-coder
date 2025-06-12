from langchain_core.tools import tool
import logging
import json

from src.graph.types import State
from .decorators import log_io
from ..service.database import db
from ..utils.session_manager import SessionManager

collection = db["session"]

def tool_parent(state: State):
    @tool()
    @log_io
    def read_file_tool(path: str) -> str:
        """
        Reads file description from database. Normalizes paths and handles errors gracefully.
        
        Args:
            path (str): File path (can be full path or relative to projects folder)
            
        Returns:
            str: JSON string with either:
                - file description if found
                - error message if not found
                - exception details if error occurs
        """
        try:
            # Normalize path
            path = path.replace("\\", "/").strip()
            
            # Remove 'projects/' prefix if present
            if path.startswith("projects/"):
                path = path[9:]  # Remove first 9 characters
            
            logging.info(f"Looking up file: {path}")
            
            session_id = state["session_id"]
            print(type(state))
            if not session_id:
                return json.dumps({"error": "No active session"})
                
            document = collection.find_one({"session_id": session_id})
            print(type(document))
            if not document:
                return json.dumps({"error": "Session not found"})
                
            # Search checklist for matching file
            for item in document["checklist"]:
                if not item:
                    continue
                if item.get("file_path") == path:
                    return json.dumps({
                        "status": "found",
                        "description": str(item.get("description", "")) 
                    })
            
            return json.dumps({"error": "File not found in checklist"})

        except Exception as e:
            return json.dumps({
                "error": "Exception occurred",
                "details": str(e)
            })
    
    return read_file_tool