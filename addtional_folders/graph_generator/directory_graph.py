import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
try:
    import plotly.graph_objects as go
except ImportError:
    print("Warning: plotly not found. Visualization will not be available.")
    print("To install: pip install plotly")
    go = None

VERSION = 'v3.0'
NODE_TYPE_DIRECTORY = 'directory'
NODE_TYPE_FILE = 'file'
NODE_TYPE_CLASS = 'class'
NODE_TYPE_FUNCTION = 'function'
EDGE_TYPE_CONTAINS = 'contains'
EDGE_TYPE_INHERITS = 'inherits'
EDGE_TYPE_INVOKES = 'invokes'
EDGE_TYPE_IMPORTS = 'imports'

VALID_NODE_TYPES = [NODE_TYPE_DIRECTORY, NODE_TYPE_FILE, NODE_TYPE_CLASS, NODE_TYPE_FUNCTION]
VALID_EDGE_TYPES = [EDGE_TYPE_CONTAINS, EDGE_TYPE_INHERITS, EDGE_TYPE_INVOKES, EDGE_TYPE_IMPORTS]


def build_graph_from_json(json_path: str) -> nx.MultiDiGraph:
    """
    Build a dependency graph from a JSON file describing the project structure.
    
    Args:
        json_path: Path to the JSON file containing project structure
        
    Returns:
        A MultiDiGraph representing the project structure and dependencies
    """
    # Create a new multigraph
    graph = nx.MultiDiGraph()
    
    # Load the JSON data
    with open(json_path, 'r') as f:
        project_data = json.load(f)
    
    # Extract project overview
    project_name = project_data.get('project_overview', {}).get('name', 'Project')
    print(f"Analyzing project: {project_name}")
    
    # Add root directory node
    root_dir = "/"
    graph.add_node(root_dir, type=NODE_TYPE_DIRECTORY)
    
    # Process directory structure
    directories = project_data.get('directory_structure', {})
    for dir_path, dir_info in directories.items():
        # Add directory node
        graph.add_node(dir_path, type=NODE_TYPE_DIRECTORY, purpose=dir_info.get('purpose', ''))
        
        # Connect to parent directory
        parent_dir = os.path.dirname(dir_path.rstrip('/')) + '/'
        if parent_dir == '/':
            parent_dir = root_dir
        
        # Handle the case when parent_dir is not present yet
        if not graph.has_node(parent_dir) and parent_dir != root_dir:
            graph.add_node(parent_dir, type=NODE_TYPE_DIRECTORY)
            # Connect to its parent
            parent_parent = os.path.dirname(parent_dir.rstrip('/')) + '/'
            if parent_parent == '/':
                parent_parent = root_dir
            graph.add_edge(parent_parent, parent_dir, type=EDGE_TYPE_CONTAINS)
        
        graph.add_edge(parent_dir, dir_path, type=EDGE_TYPE_CONTAINS)
        
        # Add files in this directory
        for file_name in dir_info.get('files', []):
            file_path = os.path.join(dir_path, file_name)
            # Add file node
            graph.add_node(file_path, type=NODE_TYPE_FILE)
            # Connect to parent directory
            graph.add_edge(dir_path, file_path, type=EDGE_TYPE_CONTAINS)
    
    # Process file documentation to add function nodes and imports
    file_docs = project_data.get('file_documentation', {})
    for file_path, file_info in file_docs.items():
        # Add file if not already added
        if not graph.has_node(file_path):
            graph.add_node(file_path, type=NODE_TYPE_FILE, purpose=file_info.get('purpose', ''))
            parent_dir = os.path.dirname(file_path) + '/'
            # Add parent directory if needed
            if not graph.has_node(parent_dir):
                graph.add_node(parent_dir, type=NODE_TYPE_DIRECTORY)
                parent_parent = os.path.dirname(parent_dir.rstrip('/')) + '/'
                if parent_parent == '/':
                    parent_parent = root_dir
                graph.add_edge(parent_parent, parent_dir, type=EDGE_TYPE_CONTAINS)
            graph.add_edge(parent_dir, file_path, type=EDGE_TYPE_CONTAINS)
        
        # Add function nodes
        for func_name, func_info in file_info.get('functions', {}).items():
            full_func_name = f"{file_path}:{func_name}"
            graph.add_node(full_func_name, type=NODE_TYPE_FUNCTION, 
                          params=func_info.get('params', ''),
                          returns=func_info.get('returns', ''),
                          description=func_info.get('description', ''))
            graph.add_edge(file_path, full_func_name, type=EDGE_TYPE_CONTAINS)
        
        # Add imports as edges between files/functions
        for import_name, import_info in file_info.get('imports', {}).items():
            import_path = import_info.get('importfilepath', '')
            if not import_path:
                continue
                
            # Try to resolve the import path to an actual file path
            resolved_path = resolve_import_path(import_path, project_data)
            if resolved_path:
                # Check if it's a function or module
                if import_info.get('type') == 'function':
                    # Find the function in the target file
                    target_file_info = file_docs.get(resolved_path, {})
                    if import_name in target_file_info.get('functions', {}):
                        target_node = f"{resolved_path}:{import_name}"
                        if graph.has_node(target_node):
                            graph.add_edge(file_path, target_node, type=EDGE_TYPE_IMPORTS, alias=import_name)
                    else:
                        # Function not found, just link to the file
                        graph.add_edge(file_path, resolved_path, type=EDGE_TYPE_IMPORTS, alias=import_name)
                else:
                    # Module import
                    if graph.has_node(resolved_path):
                        graph.add_edge(file_path, resolved_path, type=EDGE_TYPE_IMPORTS, alias=import_name)
    
    # Process function calls (invocations)
    for file_path, file_info in file_docs.items():
        # For each function in the file
        for func_name, func_info in file_info.get('functions', {}).items():
            caller_node = f"{file_path}:{func_name}"
            
            # The actual invocations are not in the JSON, but we could infer from descriptions
            # or add a "calls" field to the JSON if needed
            # For this implementation, we'll use import relationships as a proxy

            # For each imported function, add an INVOKES edge
            for import_name, import_info in file_info.get('imports', {}).items():
                if import_info.get('type') == 'function':
                    import_path = import_info.get('importfilepath', '')
                    if import_path:
                        resolved_path = resolve_import_path(import_path, project_data)
                        if resolved_path:
                            target_file_info = file_docs.get(resolved_path, {})
                            if import_name in target_file_info.get('functions', {}):
                                target_node = f"{resolved_path}:{import_name}"
                                if graph.has_node(target_node) and graph.has_node(caller_node):
                                    graph.add_edge(caller_node, target_node, type=EDGE_TYPE_INVOKES)
    
    return graph


def resolve_import_path(import_path: str, project_data: Dict[str, Any]) -> Optional[str]:
    """
    Resolve an import path to an actual file path in the project.
    
    Args:
        import_path: The import path to resolve
        project_data: The full project data dictionary
        
    Returns:
        The resolved file path, or None if it couldn't be resolved
    """
    # List of all file paths in the project
    all_file_paths = project_data.get('file_documentation', {}).keys()
    
    # Direct match
    if import_path in all_file_paths:
        return import_path
    
    # Try different extensions for Python modules
    for ext in ['', '.py', '/__init__.py']:
        potential_path = import_path + ext
        if potential_path in all_file_paths:
            return potential_path
    
    # Try to match by module name
    module_name = import_path.split('.')[-1]
    for file_path in all_file_paths:
        if file_path.endswith(f"/{module_name}.py") or file_path.endswith(f"/{module_name}/__init__.py"):
            return file_path
    
    # If it's a standard library, we won't have it in our project
    if '.' not in import_path and import_path.islower():
        return None
    
    # For Flask-specific imports, map to flask
    flask_imports = ['Blueprint', 'render_template', 'request', 'redirect', 'url_for', 'g', 'Flask']
    if import_path in flask_imports:
        return None  # External
    
    return None


def visualize_graph(G, output_file=None):
    """
    Create an interactive visualization of the graph.
    
    Args:
        G: The NetworkX graph to visualize
        output_file: The output file path for the visualization
        
    Returns:
        The plotly figure object if successful, None otherwise
    """
    try:
        import plotly.graph_objects as go
        import numpy as np
        import networkx as nx  # Import networkx inside the function
        
        # Get node positions using networkx layout algorithms
        pos = nx.spring_layout(G, k=2, iterations=50)
    
        # Get node types and prepare node styling
        node_types = set(nx.get_node_attributes(G, 'type').values())
        node_colors = {
            NODE_TYPE_CLASS: 'lightgreen', 
            NODE_TYPE_FUNCTION: 'lightblue',
            NODE_TYPE_FILE: 'lightgrey', 
            NODE_TYPE_DIRECTORY: 'orange'
        }
        node_symbols = {
            NODE_TYPE_CLASS: 'circle', 
            NODE_TYPE_FUNCTION: 'square', 
            NODE_TYPE_FILE: 'diamond',
            NODE_TYPE_DIRECTORY: 'triangle-up'
        }
        
        # Edge styling
        edge_types = set(nx.get_edge_attributes(G, 'type').values())
        edge_colors = {
            EDGE_TYPE_IMPORTS: 'forestgreen', 
            EDGE_TYPE_CONTAINS: 'skyblue',
            EDGE_TYPE_INVOKES: 'magenta', 
            EDGE_TYPE_INHERITS: 'brown'
        }
        edge_dash_patterns = {
            EDGE_TYPE_IMPORTS: 'solid', 
            EDGE_TYPE_CONTAINS: 'dash', 
            EDGE_TYPE_INVOKES: 'dot',
            EDGE_TYPE_INHERITS: 'dashdot'
        }
        
        # Create figure
        fig = go.Figure()
        
        # Add nodes by type
        for node_type in node_types:
            nodes_of_type = [n for n, d in G.nodes(data=True) if d['type'] == node_type]
            
            # Skip if no nodes of this type
            if not nodes_of_type:
                continue
                
            x_pos = [pos[node][0] for node in nodes_of_type]
            y_pos = [pos[node][1] for node in nodes_of_type]
            
            # Node labels for hover text
            node_labels = []
            for node in nodes_of_type:
                node_data = G.nodes[node]
                hover_text = f"Node: {node}<br>Type: {node_type}"
                
                # Add additional attributes to hover text
                for attr in ['purpose', 'description', 'params', 'returns']:
                    if attr in node_data and node_data[attr]:
                        hover_text += f"<br>{attr.capitalize()}: {node_data[attr]}"
                
                node_labels.append(hover_text)
            
            # Create shortened display names
            display_names = []
            for node in nodes_of_type:
                if node_type == NODE_TYPE_FILE or node_type == NODE_TYPE_DIRECTORY:
                    # Just show filename/dirname
                    display_names.append(os.path.basename(node.rstrip('/')))
                elif node_type == NODE_TYPE_FUNCTION or node_type == NODE_TYPE_CLASS:
                    # Just show function/class name
                    display_names.append(node.split(':')[-1])
                else:
                    display_names.append(str(node))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=x_pos,
                y=y_pos,
                mode='markers+text',
                marker=dict(
                    symbol=node_symbols[node_type],
                    size=25,
                    color=node_colors[node_type],
                    line=dict(width=1, color='black')
                ),
                text=display_names,
                textposition="top center",
                hoverinfo='text',
                hovertext=node_labels,
                name=node_type
            ))
        
        # Group edges between the same pair of nodes
        edge_groups = {}
        for u, v, key, data in G.edges(keys=True, data=True):
            if (u, v) not in edge_groups:
                edge_groups[(u, v)] = []
            edge_groups[(u, v)].append((key, data))
        
        # Add edges with different styles based on their type
        for edge_type in edge_types:
            edge_x = []
            edge_y = []
            edge_hover_text = []
            
            for (u, v), edges in edge_groups.items():
                # Process only edges of current type
                type_edges = [(key, data) for key, data in edges if data['type'] == edge_type]
                
                if not type_edges:
                    continue
                    
                # For multiple edges between same nodes, add slight curvature
                num_edges = len(type_edges)
                
                for i, (key, data) in enumerate(type_edges):
                    # Calculate control points for curved edges
                    x0, y0 = pos[u]
                    x1, y1 = pos[v]
                    
                    # Calculate perpendicular vector for curve control point
                    if num_edges > 1:
                        dx = x1 - x0
                        dy = y1 - y0
                        dist = np.sqrt(dx*dx + dy*dy)
                        # Normalize and rotate 90 degrees
                        nx = -dy/dist
                        ny = dx/dist
                        # Scale curvature based on edge position
                        curvature = 0.2 * (i - (num_edges - 1) / 2)
                        # Control point
                        cx = (x0 + x1) / 2 + curvature * nx
                        cy = (y0 + y1) / 2 + curvature * ny
                        
                        # Create points for curved line
                        t = np.linspace(0, 1, 50)
                        # Quadratic Bezier curve
                        bez_x = (1-t)**2 * x0 + 2*(1-t)*t * cx + t**2 * x1
                        bez_y = (1-t)**2 * y0 + 2*(1-t)*t * cy + t**2 * y1
                        
                        edge_x.extend(bez_x.tolist() + [None])
                        edge_y.extend(bez_y.tolist() + [None])
                    else:
                        # Straight line for single edge
                        edge_x.extend([x0, x1, None])
                        edge_y.extend([y0, y1, None])
                    
                    # Create edge hover text
                    hover_text = f"From: {u}<br>To: {v}<br>Type: {edge_type}"
                    if 'alias' in data and data['alias']:
                        hover_text += f"<br>Alias: {data['alias']}"
                    edge_hover_text.append(hover_text)
            
            # Add edge trace
            if edge_x:
                fig.add_trace(go.Scatter(
                    x=edge_x,
                    y=edge_y,
                    mode='lines',
                    line=dict(
                        width=2,
                        color=edge_colors[edge_type],
                        dash=edge_dash_patterns[edge_type]
                    ),
                    hoverinfo='text',
                    hovertext=edge_hover_text,
                    name=edge_type
                ))
        
        # Add arrow annotations for edge directions
        annotations = []
        for (u, v), edges in edge_groups.items():
            x0, y0 = pos[u]
            x1, y1 = pos[v]
            
            # Use the first edge's type for the arrow style
            edge_type = edges[0][1]['type']
            
            dx = x1 - x0
            dy = y1 - y0
            dist = np.sqrt(dx*dx + dy*dy)
            
            # Normalize direction vector
            dx = dx / dist
            dy = dy / dist
            
            # Position the arrow slightly before the target node
            ax = x1 - dx * 0.15
            ay = y1 - dy * 0.15
            
            annotations.append(dict(
                x=ax,
                y=ay,
                ax=x1,
                ay=y1,
                xref='x',
                yref='y',
                axref='x',
                ayref='y',
                showarrow=True,
                arrowhead=2,
                arrowsize=1.5,
                arrowwidth=2,
                arrowcolor=edge_colors[edge_type]
            ))
        
        # Update layout
        fig.update_layout(
            title='Project Structure Graph',
            showlegend=True,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            annotations=annotations,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=800,
            width=1000,
            legend=dict(
                x=0,
                y=1,
                traceorder='normal',
                font=dict(size=12),
                bordercolor='Black',
                borderwidth=1
            ),
            template='plotly_white'
        )
        
        # Update hover behavior
        fig.update_traces(
            hovertemplate='%{hovertext}<extra></extra>'
        )
        
        # Save as PNG file
        if output_file:
            fig.write_image(output_file.replace('.html', '.png'), format='png')
        else:
            fig.write_image('project_structure.png', format='png')
        
        print(f"Visualization saved to {output_file or 'project_structure.png'}")
        
        return fig
        
    except Exception as e:
        print(f"Error creating visualization: {e}")
        print("Make sure you have plotly installed: pip install plotly")
        import traceback
        traceback.print_exc()
        return None


def traverse_directory_structure(graph, root='/'):
    """Print the directory structure as a tree."""
    def traverse(node, prefix, is_last):
        if node == root:
            print(f"{node}")
            new_prefix = ''
        else:
            connector = '└── ' if is_last else '├── '
            print(f"{prefix}{connector}{os.path.basename(node.rstrip('/'))}")
            new_prefix = prefix + ('    ' if is_last else '│   ')

        # Traverse neighbors with edge type 'contains'
        children = []
        for neighbor in graph.neighbors(node):
            for key in graph[node][neighbor]:
                if graph[node][neighbor][key].get('type') == 'contains':
                    children.append(neighbor)
        
        # Sort children (directories first, then files, then others)
        def sort_key(child):
            if graph.nodes[child].get('type') == 'directory':
                return (0, child)
            elif graph.nodes[child].get('type') == 'file':
                return (1, child)
            else:
                return (2, child)
        
        children.sort(key=sort_key)
        
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            traverse(child, new_prefix, is_last_child)

    traverse(root, '', False)


def print_project_summary(graph):
    """Print a summary of the project structure."""
    node_types = Counter([data['type'] for _, data in graph.nodes(data=True)])
    edge_types = Counter([data['type'] for _, _, data in graph.edges(data=True)])
    
    print("\nProject Summary:")
    print("----------------")
    print("Nodes:")
    for node_type, count in node_types.items():
        print(f"  {node_type}: {count}")
    print("\nEdges:")
    for edge_type, count in edge_types.items():
        print(f"  {edge_type}: {count}")
    print()


def main():
    parser = argparse.ArgumentParser(description='Analyze and visualize project structure from JSON')
    parser.add_argument('--json_path', type=str, required=True, help='Path to the JSON file with project structure')
    parser.add_argument('--visualize', action='store_true', help='Generate interactive visualization')
    parser.add_argument('--output', type=str, help='Output HTML file for visualization')
    args = parser.parse_args()
    
    try:
        # Check if the JSON file exists
        if not os.path.exists(args.json_path):
            print(f"Error: JSON file not found at {args.json_path}")
            return 1
            
        # Build graph from JSON
        graph = build_graph_from_json(args.json_path)
        
        # Print directory structure
        print("\nDirectory Structure:")
        print("-------------------")
        traverse_directory_structure(graph)
        
        # Print project summary
        print_project_summary(graph)
        
        # Visualize the graph if requested
        if args.visualize:
            visualize_graph(graph, args.output)
            
        return 0
        
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file at {args.json_path}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())