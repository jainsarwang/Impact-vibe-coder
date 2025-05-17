import os
import ast
import re
import argparse


def extract_imports(tree):
    """Extract all import statements from an AST tree."""
    imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(f"import {name.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(name.name for name in node.names)
            imports.append(f"from {module} import {names}")
    
    return imports


def extract_function_info(node, include_comments=False, source_lines=None):
    """Extract detailed information about a function from its AST node."""
    function_info = {
        "name": node.name,
        "args": [],
        "docstring": ast.get_docstring(node),
        "returns": [],
        "comments": []
    }
    
    # Extract arguments
    args = node.args
    
    # Positional arguments
    for arg in args.args:
        arg_name = arg.arg
        # Check if argument has a type annotation
        if arg.annotation:
            try:
                annotation = ast.unparse(arg.annotation)
                arg_name += f": {annotation}"
            except (AttributeError, ValueError):
                # For older Python versions or complex annotations
                pass
        function_info["args"].append(arg_name)
    
    # *args
    if args.vararg:
        function_info["args"].append(f"*{args.vararg.arg}")
    
    # Keyword-only arguments
    for arg in args.kwonlyargs:
        function_info["args"].append(arg.arg)
    
    # **kwargs
    if args.kwarg:
        function_info["args"].append(f"**{args.kwarg.arg}")
    
    # Extract return statements
    for child_node in ast.walk(node):
        if isinstance(child_node, ast.Return) and child_node.value:
            try:
                return_value = ast.unparse(child_node.value)
                function_info["returns"].append(return_value)
            except (AttributeError, ValueError):
                function_info["returns"].append("Unknown return value")
    
    # Extract comments if requested and source_lines is provided
    if include_comments and source_lines:
        # Get line numbers for this function
        start_line = node.lineno
        end_line = 0
        for child in ast.walk(node):
            if hasattr(child, 'lineno'):
                end_line = max(end_line, child.lineno)
        
        # Look for comments within the function's lines
        for i in range(start_line - 1, min(end_line, len(source_lines))):
            line = source_lines[i]
            comment_match = re.search(r'#(.+)$', line)
            if comment_match:
                comment = comment_match.group(1).strip()
                if comment:  # Only add non-empty comments
                    function_info["comments"].append(f"Line {i+1}: {comment}")
    
    return function_info


def extract_python_file_info(file_path, include_comments=False):
    """Extract information from a Python file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        source_lines = content.splitlines()
    
    try:
        tree = ast.parse(content)
        
        file_info = {
            "imports": extract_imports(tree),
            "functions": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_info = extract_function_info(node, include_comments, source_lines)
                file_info["functions"].append(function_info)
        
        return file_info
    except SyntaxError:
        return {"imports": [], "functions": [], "error": "Syntax error in file"}


def extract_folder_hierarchy(folder_path, output_file, ignore_list=None, include_comments=False):
    """
    Extract the file-folder hierarchy of a given folder path and export it to a text file.
    Also extracts detailed information from Python files.
    
    Args:
        folder_path (str): Path to the folder whose hierarchy needs to be extracted
        output_file (str): Path to the output text file
        ignore_list (list): List of file/folder names to ignore
        include_comments (bool): Whether to include comments from Python files
    """
    if ignore_list is None:
        ignore_list = []
    
    # Ensure the folder path exists
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The specified folder path '{folder_path}' does not exist.")
    
    # Create or open the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"Folder Hierarchy and Python Analysis for: {os.path.abspath(folder_path)}\n")
        f.write("=" * 70 + "\n\n")
        
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
                    last_item = (i == len(files) - 1 and len(dirs) == 0)
                    prefix = "└── " if last_item else "├── "
                    
                    f.write(f"{subindent[:-4]}{prefix}{file}\n")
                    
                    # If this is a Python file, extract and write its information
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            py_info = extract_python_file_info(file_path, include_comments)
                            code_indent = '│   ' * (level + 2)
                            
                            # Write imports
                            if py_info["imports"]:
                                f.write(f"{code_indent}Imports:\n")
                                for imp in py_info["imports"]:
                                    f.write(f"{code_indent}  {imp}\n")
                            
                            # Write functions
                            if py_info["functions"]:
                                f.write(f"{code_indent}Functions:\n")
                                for func in py_info["functions"]:
                                    f.write(f"{code_indent}  def {func['name']}({', '.join(func['args'])}):\n")
                                    
                                    # Write docstring if it exists
                                    if func["docstring"]:
                                        docstring_lines = func["docstring"].strip().split('\n')
                                        f.write(f"{code_indent}    \"\"\"{docstring_lines[0]}\n")
                                        for line in docstring_lines[1:]:
                                            f.write(f"{code_indent}    {line}\n")
                                        f.write(f"{code_indent}    \"\"\"\n")
                                    
                                    # Write returns if they exist
                                    if func["returns"]:
                                        f.write(f"{code_indent}    Returns:\n")
                                        for ret in func["returns"]:
                                            f.write(f"{code_indent}      return {ret}\n")
                                    
                                    # Write comments if requested and they exist
                                    if include_comments and func["comments"]:
                                        f.write(f"{code_indent}    Comments:\n")
                                        for comment in func["comments"]:
                                            f.write(f"{code_indent}      {comment}\n")
                                    
                                    f.write("\n")
                            
                            # Write errors if they exist
                            if "error" in py_info:
                                f.write(f"{code_indent}ERROR: {py_info['error']}\n")
                        
                        except Exception as e:
                            f.write(f"{code_indent}ERROR: Failed to analyze Python file: {str(e)}\n")


def main():
    parser = argparse.ArgumentParser(description='Extract folder hierarchy and Python file information to a text file.')
    parser.add_argument('folder_path', help='Path to the folder whose hierarchy needs to be extracted')
    parser.add_argument('output_file', help='Path to the output text file')
    parser.add_argument('--ignore', nargs='+', default=[], 
                        help='List of files/folders to ignore (space-separated)')
    parser.add_argument('--include-comments', action='store_true', default=False,
                        help='Include comments from Python files (default: False)')
    
    args = parser.parse_args()
    
    try:
        extract_folder_hierarchy(args.folder_path, args.output_file, args.ignore, args.include_comments)
        print(f"Folder hierarchy and Python analysis successfully exported to {args.output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    extract_folder_hierarchy(folder_path = 'D:/A APRIL/LANGMANUS FRAMEWORK VIBE CODER/Impact-vibe-coder/src',
                             output_file = 'D:/A APRIL/LANGMANUS FRAMEWORK VIBE CODER/Impact-vibe-coder/addtional_folders/documentation_work/hierarchy/advanced_hierarchy.txt',
                             ignore_list=['__init__.py','__pycache__'],
                             include_comments=True)