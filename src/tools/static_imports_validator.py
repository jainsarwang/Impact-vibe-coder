# src/utils/static_validator.py
import ast
import os
import sys
import logging
from typing import List, Tuple, Set, Optional

logger = logging.getLogger(__name__)

# A simplified list of standard library modules.
# For Python 3.10+, you can use:
# from importlib.resources import read_text
# STANDARD_LIBRARY_MODULES = set(sys.stdlib_module_names)
# For older versions, a pre-compiled list or this manual one is needed.
STANDARD_LIBRARY_MODULES = set(sys.builtin_module_names) | {
    'os', 'sys', 'json', 're', 'datetime', 'logging', 'collections', 'math',
    'itertools', 'functools', 'random', 'time', 'pathlib', 'subprocess', 'threading',
    'multiprocessing', 'argparse', 'csv', 'pickle', 'socket', 'http', 'urllib',
    'copy', 'typing', 'abc', 'enum', 'textwrap', 'io', 'glob', 'shutil',
    'tempfile', 'unittest', 'doctest', 'inspect', 'concurrent', 'asyncio',
    'decimal', 'fractions', 'statistics', 'hashlib', 'hmac', 'secrets',
    'base64', 'binascii', 'struct', 'tarfile', 'zipfile', 'gzip', 'bz2',
    'lzma', 'xml', 'email', 'calendar', 'getopt', 'optparse', 'uuid',
    # Add more common ones as needed
}
# Add common submodules often imported directly
STANDARD_LIBRARY_MODULES.update([
    'collections.abc', 'urllib.parse', 'urllib.request', 'urllib.error',
    'http.client', 'http.server', 'json.decoder', 'json.encoder',
    'os.path'
])


def _is_project_module_available(
    module_parts: List[str],
    base_dir: str, # This would be the effective directory to start looking from (e.g. project_root or a directory for relative imports)
    project_root: str # The absolute root of the project for resolving modules if base_dir isn't project_root
) -> bool:
    """
    Checks if a module (file or package) exists relative to base_dir.
    module_parts: e.g., ['app', 'models', 'user'] for 'app.models.user'
    """
    current_path = base_dir
    for part_idx, part in enumerate(module_parts):
        potential_path = os.path.join(current_path, part)
        if os.path.exists(potential_path + ".py"): # It's a .py file
            # Ensure we are at the last part of the module path
            return part_idx == len(module_parts) - 1
        elif os.path.isdir(potential_path) and \
             os.path.exists(os.path.join(potential_path, "__init__.py")): # It's a package
            current_path = potential_path # Descend into package
            if part_idx == len(module_parts) - 1: # Last part is a package itself
                return True
        else:
            return False # Path component not found
    return False # Should have returned True earlier if valid


def verify_imports_in_file(
    file_path: str,
    project_root: str,
    project_modules: Set[str],
    third_party_libs: Optional[Set[str]] = None
) -> List[str]:
    """
    Verifies imports in a single Python file.
    Returns a list of error messages.
    """
    if third_party_libs is None:
        third_party_libs = set()

    errors: List[str] = []
    if not os.path.exists(file_path):
        errors.append(f"File not found for validation: {file_path}")
        return errors

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content, filename=file_path)
    except Exception as e:
        errors.append(f"Could not parse {os.path.basename(file_path)}: {e}")
        return errors

    current_file_dir_abs = os.path.abspath(os.path.dirname(file_path))
    project_root_abs = os.path.abspath(project_root)

    for node in ast.walk(tree):
        module_to_check: Optional[str] = None
        is_relative_import = False

        if isinstance(node, ast.Import):
            for alias in node.names:
                module_to_check = alias.name
                top_level_module = module_to_check.split('.')[0]

                if top_level_module in STANDARD_LIBRARY_MODULES:
                    continue
                if top_level_module in third_party_libs:
                    continue
                if module_to_check in project_modules:
                    continue
                
                # Fallback file system check for absolute import from project root
                if _is_project_module_available(module_to_check.split('.'), project_root_abs, project_root_abs):
                    continue

                errors.append(
                    f"{os.path.basename(file_path)}:{node.lineno}: Cannot resolve absolute import '{module_to_check}'. "
                    f"Not standard, known third-party, or found in project structure."
                )

        elif isinstance(node, ast.ImportFrom):
            level = node.level  # For relative imports: 0=absolute, 1=., 2=.., etc.
            
            if level > 0: # Relative import
                is_relative_import = True
                # Calculate the base directory for the relative import
                effective_base_dir = current_file_dir_abs
                for _ in range(level - 1): # For each '..'
                    effective_base_dir = os.path.dirname(effective_base_dir)
                    if effective_base_dir == project_root_abs and _ < level - 2: # Went too far up
                         errors.append(
                            f"{os.path.basename(file_path)}:{node.lineno}: Relative import level {level} attempts to go above project root from {current_file_dir_abs}."
                        )
                         continue # Skip this import

                relative_module_name = node.module if node.module else "" # Handle "from . import foo" vs "from .foo import bar"
                module_parts_from_relative = relative_module_name.split('.') if relative_module_name else []
                
                # Check module from this effective base
                if _is_project_module_available(module_parts_from_relative, effective_base_dir, project_root_abs):
                    # We could also try to convert this to an absolute project module name and check project_modules
                    # e.g., if effective_base_dir is project_root/app and module is 'models', it's 'app.models'
                    # For simplicity, file system check is done here.
                    continue
                else:
                    errors.append(
                        f"{os.path.basename(file_path)}:{node.lineno}: Cannot resolve relative import "
                        f"'{"." * level}{relative_module_name}'. "
                        f"Module not found from base '{os.path.relpath(effective_base_dir, project_root_abs)}'."
                    )

            else: # Absolute import (level == 0)
                module_to_check = node.module
                if not module_to_check: # Should not happen for level 0
                    errors.append(f"{os.path.basename(file_path)}:{node.lineno}: Invalid 'from import' statement (no module name).")
                    continue

                top_level_module = module_to_check.split('.')[0]

                if top_level_module in STANDARD_LIBRARY_MODULES:
                    continue
                if top_level_module in third_party_libs:
                    continue
                if module_to_check in project_modules:
                    continue
                
                if _is_project_module_available(module_to_check.split('.'), project_root_abs, project_root_abs):
                    continue
                
                errors.append(
                    f"{os.path.basename(file_path)}:{node.lineno}: Cannot resolve absolute import from '{module_to_check}'. "
                    f"Not standard, known third-party, or found in project structure."
                )
    return errors


def collect_project_modules(project_root: str) -> Set[str]:
    """
    Walks the project_root and collects all possible Python module paths.
    e.g., "app.models", "utils.helpers"
    Assumes project_root is the base for module paths.
    """
    project_modules: Set[str] = set()
    project_root_abs = os.path.abspath(project_root)

    for root, dirs, files in os.walk(project_root_abs, topdown=True):
        # Prune non-relevant directories
        dirs[:] = [d for d in dirs if d not in ['.git', '.venv', '__pycache__', 'node_modules', 'tests', 'docs'] and not d.startswith('.')]

        # Calculate module prefix for current directory
        rel_dir = os.path.relpath(root, project_root_abs)
        if rel_dir == ".":
            current_module_prefix_parts = []
        else:
            current_module_prefix_parts = rel_dir.split(os.sep)

        for file_name in files:
            if file_name.endswith(".py"):
                module_path_parts = list(current_module_prefix_parts) # Make a copy

                if file_name == "__init__.py":
                    # This directory is a package
                    if module_path_parts: # Avoid adding "" for project_root/__init__.py (if it's a module itself)
                        project_modules.add(".".join(module_path_parts))
                else:
                    # This is a module file
                    module_name_stem = file_name[:-3]  # remove .py
                    module_path_parts.append(module_name_stem)
                    project_modules.add(".".join(module_path_parts))
        
        # Also add directories that are packages (contain __init__.py) even if __init__ itself wasn't processed above
        for dir_name in dirs:
            if os.path.exists(os.path.join(root, dir_name, "__init__.py")):
                module_path_parts = list(current_module_prefix_parts)
                module_path_parts.append(dir_name)
                project_modules.add(".".join(module_path_parts))


    logger.debug(f"Collected project modules from '{project_root_abs}': {project_modules}")
    return project_modules


def static_imports_validator(
    project_root: str,
    generated_py_files: List[str],
    third_party_libs: Optional[Set[str]] = None
) -> List[str]:
    """
    Validates imports for a list of generated Python files within a project.
    generated_py_files: List of paths relative to project_root.
    """
    all_errors: List[str] = []
    project_root_abs = os.path.abspath(project_root)

    if not os.path.isdir(project_root_abs):
        msg = f"Project root directory '{project_root_abs}' does not exist."
        logger.error(msg)
        all_errors.append(msg)
        return all_errors

    project_modules = collect_project_modules(project_root_abs)

    for rel_file_path in generated_py_files:
        abs_file_path = os.path.join(project_root_abs, rel_file_path)
        if not os.path.exists(abs_file_path):
            all_errors.append(f"File to validate does not exist: {abs_file_path} (original rel: {rel_file_path})")
            continue
        if not abs_file_path.endswith(".py"):
            logger.debug(f"Skipping non-python file for import validation: {abs_file_path}")
            continue

        logger.info(f"Validating imports in: {rel_file_path}")
        file_errors = verify_imports_in_file(abs_file_path, project_root_abs, project_modules, third_party_libs)
        all_errors.extend(file_errors)
        if file_errors:
            logger.warning(f"Import errors in {rel_file_path}: {file_errors}")

    return all_errors