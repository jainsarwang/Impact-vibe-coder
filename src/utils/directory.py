from typing import Union
from pathlib import Path

def ensure_directory_exists(file_path: Union[str, Path]) -> None:
    """
    Ensure that the directory for the given file path exists.
    If it does not exist, create all necessary directories.

    Args:
        file_path: The file path for which to ensure the directory exists
    """
    try:
        directory = Path(file_path).parent
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise NameError(f"Failed to create directory: {str(e)}")