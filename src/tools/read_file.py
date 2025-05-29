from langchain_core.tools import tool
from .decorators import log_io

@tool
@log_io
def read_file_tool(file_path):
    """
    Reads a file and returns its content.
    """
    try:
        with open(file_path, "r") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"