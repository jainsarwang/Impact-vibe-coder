#Importing Libraries
import os
import zipfile
from pathlib import Path


def create_zip_from_folder(folder_path_to_zip: str, output_zip_path_with_filename: str) -> bool:
    """
    Creates a zip archive of a specified folder.

    Args:
        folder_path_to_zip (str): The path to the folder that needs to be zipped.
        output_zip_path_with_filename (str): The full path (including the desired .zip filename)
                                             where the zip file will be saved.
                                             Example: '/path/to/destination/archive_name.zip'

    Returns:
        bool: True if zipping was successful, False otherwise.
    """
    try:
        # Convert to Path objects for easier handling
        folder_path = Path(folder_path_to_zip)
        output_path = Path(output_zip_path_with_filename)
        
        # Check if the source folder exists
        if not folder_path.exists() or not folder_path.is_dir():
            print(f"Error: Source folder '{folder_path_to_zip}' does not exist or is not a directory.")
            return False
        
        # Create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create the zip file
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Walk through the directory and add all files
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = Path(root) / file
                    # Calculate the relative path to preserve folder structure
                    relative_path = file_path.relative_to(folder_path)
                    zipf.write(file_path, relative_path)
        
        print(f"Successfully created zip archive: {output_zip_path_with_filename}")
        return True
        
    except PermissionError as e:
        print(f"Permission error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"File not found error: {e}")
        return False
    except zipfile.BadZipFile as e:
        print(f"Zip file error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        return False
    

if __name__ == "__main__":

    SOURCE_FOLDER = 'D:/A MAY/TEXT IMAGE MULTI MODAL/samples'
    DESTINATION_ZIPPED_FILE = 'D:/A MAY/TEXT IMAGE MULTI MODAL MODULES/UTILS/fold/archive.zip'

    create_zip_from_folder(folder_path_to_zip=SOURCE_FOLDER,output_zip_path_with_filename=DESTINATION_ZIPPED_FILE)
    print('Succesfully Zipped')