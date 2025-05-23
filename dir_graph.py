import json
import os
from typing import Dict, List, Optional
import networkx as nx
import matplotlib.pyplot as plt
 
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
       
        # Handle both list and dictionary structures
        if isinstance(project_data, list):
            # Find the first dictionary in the list that contains file_documentation
            for item in project_data:
                if isinstance(item, dict) and 'file_documentation' in item:
                    project_data = item
                    break
            else:
                raise ValueError("No valid project structure found in JSON list")
        elif not isinstance(project_data, dict):
            raise ValueError("Invalid JSON structure: Expected dictionary or list")
           
        if 'file_documentation' not in project_data:
            raise ValueError("Missing required 'file_documentation' section")
       
        # Process all files
        files = []
        file_imports = {}  # {filename: [imports]}
        file_exports = {}  # {filename: [exports]}
        path_to_file = {}  # {path: filename}
        module_map = {}  # {module_name: filename}
       
        # First pass: collect all files and create mappings
        for file_path, file_info in project_data['file_documentation'].items():
            filename = os.path.basename(file_path)
            
            # Store path to filename mapping
            path_to_file[file_path] = filename
            path_to_file[f"/{file_path}"] = filename  # Add leading slash version
            
            # Get exports
            exports = file_info.get('exports', [])
            file_exports[filename] = exports
            
            # Map module names to filenames
            module_name = os.path.splitext(filename)[0]  # Remove extension
            module_map[module_name] = filename
            
            # Get imports
            imports = file_info.get('imports', {})
            processed_imports = []
            
            # Process imports
            for imp_name, imp_info in imports.items():
                if isinstance(imp_info, dict):
                    import_path = imp_info.get('importfilepath', '')
                    if import_path:
                        # Handle different import patterns
                        if import_path.startswith('/'):
                            # Absolute path import
                            if import_path in path_to_file:
                                processed_imports.append(path_to_file[import_path])
                            else:
                                # Try to find the file in the project structure
                                for path, file in path_to_file.items():
                                    if path.endswith(import_path.split('/')[-1]):
                                        processed_imports.append(file)
                                        break
                        elif '.' in import_path:
                            # Module-style import
                            parts = import_path.split('.')
                            # Try to find the module in our mappings
                            module_name = parts[-1]
                            if module_name in module_map:
                                processed_imports.append(module_map[module_name])
                            else:
                                # Try to find by filename
                                for path, file in path_to_file.items():
                                    if path.endswith(f"{module_name}.py") or path.endswith(f"{module_name}.js") or path.endswith(f"{module_name}.jsx") or path.endswith(f"{module_name}.ts") or path.endswith(f"{module_name}.tsx"):
                                        processed_imports.append(file)
                                        break
                        else:
                            # Direct file import
                            import_file = os.path.basename(import_path)
                            processed_imports.append(import_file)
            
            file_imports[filename] = processed_imports
            
            # Create file entry
            file_entry = {
                'filename': filename,
                'full_path': file_path,
                'imports': processed_imports,
                'exports': exports,
                'functions': list(file_info.get('functions', {}).keys()),
                'variables': list(file_info.get('variables', {}).keys()),
                'purpose': file_info.get('purpose', '')
            }
            files.append(file_entry)
        
        # Find dependencies and detect cycles
        dependencies = []
        cycles = set()
        
        def find_cycles(current_file, visited, path):
            if current_file in visited:
                if current_file in path:
                    cycle_start = path.index(current_file)
                    cycle = path[cycle_start:] + [current_file]
                    cycles.add(tuple(cycle))
                return
            
            visited.add(current_file)
            path.append(current_file)
            
            for imp in file_imports.get(current_file, []):
                if imp in file_exports:
                    find_cycles(imp, visited, path.copy())
            
            path.pop()
            visited.remove(current_file)
        
        # Find all cycles
        for file in files:
            find_cycles(file['filename'], set(), [])
        
        # Create dependencies
        for file in files:
            for imp in file['imports']:
                if imp in file_exports:
                    # Check if this dependency is part of a cycle
                    is_in_cycle = False
                    for cycle in cycles:
                        if file['filename'] in cycle and imp in cycle:
                            is_in_cycle = True
                            break
                    
                    dependencies.append({
                        'source_file': imp,
                        'target_file': file['filename'],
                        'import_statement': imp,
                        'in_cycle': is_in_cycle
                    })
        
        return {
            'project_info': {
                'name': project_data.get('project_overview', {}).get('name', ''),
                'description': project_data.get('project_overview', {}).get('description', '')
            },
            'files': files,
            'dependencies': dependencies,
            'cycles': list(cycles),
            'stats': {
                'total_files': len(files),
                'files_with_exports': sum(1 for f in files if f['exports']),
                'files_with_imports': sum(1 for f in files if f['imports']),
                'total_dependencies': len(dependencies),
                'total_cycles': len(cycles)
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
 
def create_dependency_graph(analysis: Dict) -> nx.DiGraph:
    """
    Creates a directed graph from the analysis results.
    
    Args:
        analysis (Dict): The analysis results from analyze_project_structure
        
    Returns:
        nx.DiGraph: A directed graph representing file dependencies
    """
    G = nx.DiGraph()
    
    # Add nodes (files)
    for file in analysis['files']:
        G.add_node(file['filename'], 
                  purpose=file['purpose'],
                  functions=len(file['functions']),
                  variables=len(file['variables']))
    
    # Add edges (dependencies)
    for dep in analysis['dependencies']:
        G.add_edge(dep['source_file'], 
                  dep['target_file'],
                  import_statement=dep['import_statement'],
                  in_cycle=dep['in_cycle'])
    
    # Mark nodes involved in cycles
    for cycle in analysis['cycles']:
        for node in cycle:
            G.nodes[node]['in_cycle'] = True
    
    return G

def visualize_graph(G: nx.DiGraph, output_path: str = None) -> None:
    """
    Visualizes the dependency graph and optionally saves it to a file.
    
    Args:
        G (nx.DiGraph): The graph to visualize
        output_path (str, optional): Path to save the visualization
    """
    plt.figure(figsize=(20, 15))
    
    # Use a more basic layout that doesn't require scipy
    pos = nx.spring_layout(G, k=2, iterations=100)
    
    # Calculate node sizes based on number of functions and variables
    node_sizes = [2000 + (G.nodes[node]['functions'] * 200) + (G.nodes[node]['variables'] * 100) 
                for node in G.nodes()]
    
    # Draw nodes with different colors based on their role and cycle status
    node_colors = []
    for node in G.nodes():
        if G.nodes[node].get('in_cycle', False):
            node_colors.append('#FF0000')  # Red for nodes in cycles
        elif any(x in node.lower() for x in ['screen', 'page', 'view']):
            node_colors.append('#FFB6C1')  # Light pink for screens/pages/views
        elif any(x in node.lower() for x in ['list', 'table', 'grid']):
            node_colors.append('#98FB98')  # Light green for list/table components
        elif any(x in node.lower() for x in ['item', 'row', 'cell']):
            node_colors.append('#87CEEB')  # Light blue for item/row components
        elif any(x in node.lower() for x in ['util', 'helper', 'service']):
            node_colors.append('#DDA0DD')  # Light purple for utility files
        elif any(x in node.lower() for x in ['model', 'schema', 'type']):
            node_colors.append('#F0E68C')  # Light yellow for data models
        else:
            node_colors.append('#E6E6FA')  # Lavender for other components
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                        node_color=node_colors,
                        node_size=node_sizes,
                        alpha=0.8,
                        edgecolors='black',
                        linewidths=2)
    
    # Separate edges by type
    direct_imports = []
    cycle_edges = []
    
    for (source, target, data) in G.edges(data=True):
        if data.get('in_cycle', False):
            cycle_edges.append((source, target, data))
        else:
            direct_imports.append((source, target, data))
    
    # Draw direct import edges (solid lines)
    nx.draw_networkx_edges(G, pos,
                        edgelist=[(s, t) for s, t, _ in direct_imports],
                        edge_color='#2E86C1',  # Blue for direct imports
                        arrows=True,
                        arrowsize=20,
                        width=2,
                        alpha=0.8,
                        connectionstyle='arc3,rad=0.1')
    
    # Draw cycle edges (thick red lines)
    nx.draw_networkx_edges(G, pos,
                        edgelist=[(s, t) for s, t, _ in cycle_edges],
                        edge_color='#FF0000',  # Red for cycles
                        arrows=True,
                        arrowsize=20,
                        width=3,
                        alpha=0.8,
                        style='dotted',
                        connectionstyle='arc3,rad=0.3')
    
    # Draw node labels with background
    labels = {node: f"{node}\n({G.nodes[node]['functions']} funcs, {G.nodes[node]['variables']} vars)"
            for node in G.nodes()}
    nx.draw_networkx_labels(G, pos,
                        labels=labels,
                        font_size=8,
                        font_family='sans-serif',
                        bbox=dict(facecolor='white',
                                edgecolor='none',
                                alpha=0.7))
    
    # Add edge labels
    edge_labels = {}
    for (source, target, data) in G.edges(data=True):
        if data.get('in_cycle', False):
            edge_labels[(source, target)] = f"cycle: {data['import_statement']}"
        else:
            edge_labels[(source, target)] = f"imports: {data['import_statement']}"
    
    nx.draw_networkx_edge_labels(G, pos,
                                edge_labels=edge_labels,
                                font_size=6,
                                bbox=dict(facecolor='white',
                                        edgecolor='none',
                                        alpha=0.7))
    
    # Add title and legend
    plt.title("File Dependencies Graph\n" +
            "Pink: Screens/Pages/Views, Green: List/Table Components, Blue: Item/Row Components\n" +
            "Purple: Utilities, Yellow: Data Models, Lavender: Others, Red: Circular Dependencies",
            fontsize=14, pad=20)
    
    # Add a legend for node sizes and edge types
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#E6E6FA',
                markersize=15, label='Small Component'),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#E6E6FA',
                markersize=25, label='Large Component'),
        plt.Line2D([0], [0], color='#2E86C1', label='Direct Import',
                linewidth=2),
        plt.Line2D([0], [0], color='#FF0000', label='Circular Dependency',
                linewidth=3, linestyle=':')
    ]
    plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1))
    
    plt.axis('off')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Graph visualization saved to: {output_path}")
    
    plt.show()

def main():
    # Example usage - can be called with any path
    json_path = input("Enter path to project structure JSON file: ").strip()
    
    analysis = analyze_project_structure(json_path)
    if analysis:
        print(f"Analyzed {analysis['stats']['total_files']} files")
        print(f"Found {analysis['stats']['total_dependencies']} dependencies")
        
        # Save analysis results
        output_path = os.path.join(os.path.dirname(json_path), 'project_analysis.json')
        if save_analysis_results(analysis, output_path):
            print(f"Results saved to: {output_path}")
        
        # Create and visualize graph
        G = create_dependency_graph(analysis)
        graph_output_path = os.path.join(os.path.dirname(json_path), 'dependency_graph.png')
        visualize_graph(G, graph_output_path)
        
        # Sample output
        print("\nSample dependencies:")
        for dep in analysis['dependencies'][:3]:  # Show first 3
            print(f"{dep['source_file']} -> {dep['target_file']} (via '{dep['import_statement']}')")

if __name__ == "__main__":
    main()