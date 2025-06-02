from langchain_core.tools import tool
from .decorators import log_io

@tool
@log_io
def read_file_tool(file_path: str) -> str:
    """
    Reads a file and returns its content.
    Args:
        file_path (str): The path to the file to read.
    Returns:
        str: The content of the file or an error message if the file cannot be read.
    """
    try:
        with open(file_path, "r") as f:
            print(file_path)
            content = f.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"Error reading file: {str(e)}"