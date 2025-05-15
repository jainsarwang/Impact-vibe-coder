import json
import os
from typing import Dict, List, Optional

def analyze_project_structure(json_path: str) -> Optional[Dict]:
    """
    Analyzes a project structure JSON file and extracts file dependencies.
    
    Args:
        json_path (str): Path to the JSON file containing project structure
        
    Returns:
        Optional[Dict]: Analysis result with files and dependencies, or None if error
    """
    try:
        # Validate file exists
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found at: {json_path}")
            
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            project_data = json.load(f)
        
        # Validate basic structure
        if not isinstance(project_data, dict):
            raise ValueError("Invalid JSON structure: Expected dictionary")
            
        if 'file_documentation' not in project_data:
            raise ValueError("Missing required 'file_documentation' section")
        
        # Process all files
        files = []
        export_map = {}  # {export_name: source_file}
        
        for file_path, file_info in project_data['file_documentation'].items():
            # Extract filename from path (works with both Windows and Unix paths)
            filename = os.path.basename(file_path)
            
            # Get exports and imports
            exports = file_info.get('exports', [])
            imports = file_info.get('imports', [])
            
            # Create file entry
            file_entry = {
                'filename': filename,
                'full_path': file_path,
                'imports': imports,
                'exports': exports,
                'functions': list(file_info.get('functions', {}).keys()),
                'variables': list(file_info.get('variables', {}).keys()),
                'purpose': file_info.get('purpose', '')
            }
            files.append(file_entry)
            
            # Update export map
            for export in exports:
                export_map[export] = filename
        
        # Find dependencies
        dependencies = []
        
        for file in files:
            for imp in file['imports']:
                # Parse import statement
                import_base = imp.split(' as ')[0].strip()
                possible_matches = set()
                
                # Add different possible interpretations
                possible_matches.add(import_base)  # Full import path
                
                if '.' in import_base:
                    # Add first part (package)
                    possible_matches.add(import_base.split('.')[0])
                    # Add last part (module)
                    possible_matches.add(import_base.split('.')[-1])
                
                # Find matching exports
                for match in possible_matches:
                    if match in export_map:
                        dependencies.append({
                            'source_file': export_map[match],
                            'target_file': file['filename'],
                            'import_statement': imp,
                            'matched_export': match
                        })
        
        return {
            'project_info': {
                'name': project_data.get('project_overview', {}).get('name', ''),
                'description': project_data.get('project_overview', {}).get('description', '')
            },
            'files': files,
            'dependencies': dependencies,
            'export_map': export_map,
            'stats': {
                'total_files': len(files),
                'files_with_exports': sum(1 for f in files if f['exports']),
                'files_with_imports': sum(1 for f in files if f['imports']),
                'total_dependencies': len(dependencies)
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON format: {str(e)}")
        return None
    except Exception as e:
        print(f"Error analyzing project structure: {str(e)}")
        return None

def save_analysis_results(analysis: Dict, output_path: str) -> bool:
    """Saves analysis results to a JSON file"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return False

def main():
    # Example usage - can be called with any path
    json_path = input("Enter path to project structure JSON file: ").strip()
    
    analysis = analyze_project_structure(json_path)
    if analysis:
        print(f"Analyzed {analysis['stats']['total_files']} files")
        print(f"Found {analysis['stats']['total_dependencies']} dependencies")
        
        # Save results
        output_path = os.path.join(os.path.dirname(json_path), 'project_analysis.json')
        if save_analysis_results(analysis, output_path):
            print(f"Results saved to: {output_path}")
        
        # Sample output
        print("\nSample dependencies:")
        for dep in analysis['dependencies'][:3]:  # Show first 3
            print(f"{dep['source_file']} -> {dep['target_file']} (via '{dep['import_statement']}')")

if __name__ == "__main__":
    main()