#Importing Libraries
import os
from pathlib import Path

def save_html_to_file(html_content, file_path, create_dirs=True, encoding='utf-8'):
    """
    Save HTML content string to a specified file path.
    
    Args:
        html_content (str): The HTML content to save
        file_path (str): The path where the HTML file should be saved
        create_dirs (bool): Whether to create directories if they don't exist (default: True)
        encoding (str): File encoding (default: 'utf-8')
    
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ValueError: If html_content is not a string or file_path is empty
        OSError: If there are file system related errors
    """
    
    # Validate inputs
    if not isinstance(html_content, str):
        raise ValueError("html_content must be a string")
    
    if not file_path or not isinstance(file_path, str):
        raise ValueError("file_path must be a non-empty string")
    
    # Ensure the file has .html extension
    if not file_path.lower().endswith('.html'):
        file_path += '.html'
    
    try:
        # Convert to Path object for easier manipulation
        path = Path(file_path)
        
        # Create directories if they don't exist and create_dirs is True
        if create_dirs and path.parent != Path('.'):
            path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the HTML content to file
        with open(path, 'w', encoding=encoding) as file:
            file.write(html_content)
        
        print(f"HTML file successfully saved to: {path.absolute()}")
        return True
        
    except OSError as e:
        print(f"Error saving file: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
