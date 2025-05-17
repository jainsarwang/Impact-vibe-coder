import os
import argparse


def extract_folder_hierarchy(folder_path, output_file, ignore_list=None):
    """
    Extract the file-folder hierarchy of a given folder path and export it to a text file.
    
    Args:
        folder_path (str): Path to the folder whose hierarchy needs to be extracted
        output_file (str): Path to the output text file
        ignore_list (list): List of file/folder names to ignore
    """
    if ignore_list is None:
        ignore_list = []
    
    # Ensure the folder path exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The specified folder path '{folder_path}' does not exist.")
    
    # Create or open the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Folder Hierarchy for: {os.path.abspath(folder_path)}\n")
        f.write("=" * 50 + "\n\n")
        
        for root, dirs, files in os.walk(folder_path):
            # Remove directories in ignore_list to prevent traversal
            dirs[:] = [d for d in dirs if d not in ignore_list]
            
            # Calculate the current level for indentation
            level = root.replace(folder_path, '').count(os.sep)
            indent = '│   ' * level
            
            # Write the current directory name
            dir_name = os.path.basename(root)
            if level > 0:  # Don't print the root folder itself as a subfolder
                f.write(f"{indent}├── {dir_name}/\n")
            
            # Write all files in the current directory
            subindent = '│   ' * (level + 1)
            for i, file in enumerate(sorted(files)):
                if file not in ignore_list:
                    # If it's the last file and there are no subdirectories
                    if i == len(files) - 1 and len(dirs) == 0:
                        f.write(f"{subindent[:-4]}└── {file}\n")
                    else:
                        f.write(f"{subindent}├── {file}\n")


def main():
    parser = argparse.ArgumentParser(description='Extract folder hierarchy to a text file.')
    parser.add_argument('folder_path', help='Path to the folder whose hierarchy needs to be extracted')
    parser.add_argument('output_file', help='Path to the output text file')
    parser.add_argument('--ignore', nargs='+', default=[], 
                        help='List of files/folders to ignore (space-separated)')
    
    args = parser.parse_args()
    
    try:
        extract_folder_hierarchy(args.folder_path, args.output_file, args.ignore)
        print(f"Folder hierarchy successfully exported to {args.output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    extract_folder_hierarchy('D:/A APRIL/LANGMANUS FRAMEWORK VIBE CODER/Impact-vibe-coder/src',
                             'D:/A APRIL/LANGMANUS FRAMEWORK VIBE CODER/Impact-vibe-coder/addtional_folders/documentation_work/hierarchy/hierarchy.txt',
                             ['__init__.py','__pycache__']
                             )