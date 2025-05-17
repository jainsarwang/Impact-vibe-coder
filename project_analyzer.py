# import os
# import re
# import networkx as nx
# import numpy as np
# import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import javalang
# import ast
# import logging
# from dataclasses import dataclass, field
# from typing import Dict, List, Any, Optional, Tuple

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# @dataclass
# class CodeFile:
#     path: str
#     content: str
#     ast_representation: Any = None
#     dependencies: List[str] = field(default_factory=list)
#     imports: List[str] = field(default_factory=list)
#     functions: List[str] = field(default_factory=list)
#     classes: List[str] = field(default_factory=list)

# @dataclass
# class ProjectStructure:
#     root_path: str
#     files: Dict[str, CodeFile] = field(default_factory=dict)
#     dependency_graph: Any = None
#     language: str = "java"

# class CodeAnalyzer:
#     """Base class for code analyzers"""
    
#     def analyze_file(self, file_path: str, content: str) -> CodeFile:
#         raise NotImplementedError

# class JavaCodeAnalyzer(CodeAnalyzer):
#     """Analyzes Java code files and extracts dependencies."""
    
#     def analyze_file(self, file_path: str, content: str) -> CodeFile:
#         """Analyze a Java file and create a CodeFile object with dependencies."""
#         try:
#             tree = javalang.parse.parse(content)
#             imports = []
#             for path, node in tree.filter(javalang.tree.Import):
#                 imports.append(node.path)
            
#             classes = []
#             for path, node in tree.filter(javalang.tree.ClassDeclaration):
#                 classes.append(node.name)
            
#             functions = []
#             for path, node in tree.filter(javalang.tree.MethodDeclaration):
#                 functions.append(node.name)
            
#             return CodeFile(
#                 path=file_path,
#                 content=content,
#                 ast_representation=tree,
#                 dependencies=imports,
#                 imports=imports,
#                 functions=functions,
#                 classes=classes
#             )
        
#         except Exception as e:
#             logger.error(f"Error analyzing Java file {file_path}: {e}")
#             return CodeFile(path=file_path, content=content)

# class PythonCodeAnalyzer(CodeAnalyzer):
#     """Analyzes Python code files and extracts dependencies."""
    
#     def analyze_file(self, file_path: str, content: str) -> CodeFile:
#         """Analyze a Python file and create a CodeFile object with dependencies."""
#         try:
#             tree = ast.parse(content)
#             imports = []
#             dependencies = []
#             functions = []
#             classes = []
            
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.Import):
#                     for alias in node.names:
#                         imports.append(alias.name)
#                         dependencies.append(alias.name.split('.')[0])
#                 elif isinstance(node, ast.ImportFrom):
#                     module = node.module if node.module else ""
#                     for alias in node.names:
#                         imports.append(f"{module}.{alias.name}" if module else alias.name)
#                         dependencies.append(module.split('.')[0] if module else alias.name)
#                 elif isinstance(node, ast.FunctionDef):
#                     functions.append(node.name)
#                 elif isinstance(node, ast.ClassDef):
#                     classes.append(node.name)
            
#             return CodeFile(
#                 path=file_path,
#                 content=content,
#                 ast_representation=tree,
#                 dependencies=dependencies,
#                 imports=imports,
#                 functions=functions,
#                 classes=classes
#             )
        
#         except Exception as e:
#             logger.error(f"Error analyzing Python file {file_path}: {e}")
#             return CodeFile(path=file_path, content=content)

# class ProjectStructureAnalyzer:
#     """Analyzes the structure of a software project."""
    
#     def __init__(self):
#         self.analyzers = {
#             'java': JavaCodeAnalyzer(),
#             'python': PythonCodeAnalyzer()
#         }
    
#     def detect_language(self, project_path: str) -> str:
#         """Detect the primary language of the project."""
#         file_extensions = {}
#         for root, _, files in os.walk(project_path):
#             for file in files:
#                 ext = os.path.splitext(file)[1]
#                 file_extensions[ext] = file_extensions.get(ext, 0) + 1
        
#         if '.java' in file_extensions:
#             return 'java'
#         elif '.py' in file_extensions:
#             return 'python'
#         return 'java'  # default to Java
    
#     def analyze_project(self, project_path: str) -> ProjectStructure:
#         """Analyze a project directory and create a ProjectStructure object."""
#         language = self.detect_language(project_path)
#         analyzer = self.analyzers[language]
        
#         project = ProjectStructure(root_path=project_path, language=language)
        
#         for root, _, files in os.walk(project_path):
#             for file in files:
#                 if (language == 'java' and file.endswith('.java')) or \
#                    (language == 'python' and file.endswith('.py')):
#                     file_path = os.path.join(root, file)
#                     rel_path = os.path.relpath(file_path, project_path)
#                     try:
#                         with open(file_path, 'r', encoding='utf-8') as f:
#                             content = f.read()
                        
#                         code_file = analyzer.analyze_file(rel_path, content)
#                         project.files[rel_path] = code_file
#                         logger.info(f"Analyzed file: {rel_path}")
#                     except Exception as e:
#                         logger.error(f"Error reading file {file_path}: {e}")
        
#         project.dependency_graph = self._build_dependency_graph(project)
#         logger.info(f"Project contains {len(project.files)} files and {len(project.dependency_graph.edges())} dependencies")
        
#         return project
    
#     def _build_dependency_graph(self, project: ProjectStructure) -> nx.DiGraph:
#         """Build a dependency graph for the project."""
#         G = nx.DiGraph()
        
#         for file_path, code_file in project.files.items():
#             if code_file.classes:
#                 label = code_file.classes[0]
#             else:
#                 label = os.path.basename(file_path).replace('.py', '').replace('.java', '')
#                 if code_file.functions:
#                     label += f" ({code_file.functions[0]})"
            
#             G.add_node(file_path, label=label, type='file')
        
#         for file_path, code_file in project.files.items():
#             for dep in code_file.dependencies:
#                 for dep_path, dep_file in project.files.items():
#                     if project.language == 'java':
#                         if dep.split('.')[-1] in dep_file.classes:
#                             G.add_edge(file_path, dep_path, type='import')
#                             break
#                     elif project.language == 'python':
#                         if dep == os.path.basename(dep_path).replace('.py', ''):
#                             G.add_edge(file_path, dep_path, type='import')
#                             break
#                         if dep in dep_file.classes:
#                             G.add_edge(file_path, dep_path, type='import')
#                             break
        
#         return G
    
#     def find_relationships(self, project: ProjectStructure, start_node: str, end_node: str) -> List[List[str]]:
#         if project.dependency_graph is None:
#             logger.error("Dependency graph not available")
#             return []
        
#         G = project.dependency_graph
        
#         try:
#             paths = list(nx.all_simple_paths(G, source=start_node, target=end_node))
#             logger.info(f"Found {len(paths)} paths between {start_node} and {end_node}")
#             return paths
#         except nx.NetworkXNoPath:
#             logger.info(f"No path exists between {start_node} and {end_node}")
#             return []
#         except nx.NodeNotFound as e:
#             logger.error(f"Node not found in graph: {e}")
#             return []
    
#     def detect_packages(self, project: ProjectStructure) -> Dict[str, List[str]]:
#         packages = {}
        
#         for file_path in project.files:
#             if project.language == 'java':
#                 parts = os.path.dirname(file_path).split(os.sep)
#                 package = ".".join(parts) if parts[0] else "default"
#             else:
#                 code_file = project.files[file_path]
#                 package = "default"
#                 if code_file.ast_representation and isinstance(code_file.ast_representation, ast.Module):
#                     for node in code_file.ast_representation.body:
#                         if isinstance(node, ast.ImportFrom) and node.level > 0:
#                             dir_parts = os.path.dirname(file_path).split(os.sep)
#                             package = ".".join(dir_parts[-node.level:] + ([node.module] if node.module else []))
#                             break
                
#                 if package == "default":
#                     parts = os.path.dirname(file_path).split(os.sep)
#                     package = ".".join(parts) if parts[0] else "default"
            
#             if package not in packages:
#                 packages[package] = []
#             packages[package].append(file_path)
        
#         return packages
    
#     def visualize_project_structure_3d(
#         self,
#         project: ProjectStructure,
#         highlight_paths: List[List[str]] = None,
#         output_path: str = "project_structure_3d.png",
#     ):
#         if project.dependency_graph is None:
#             logger.error("Dependency graph not available")
#             return
        
#         fig = plt.figure(figsize=(16, 14))
#         ax = fig.add_subplot(111, projection='3d')
        
#         G = project.dependency_graph
#         packages = self.detect_packages(project)
#         package_colors = {}
#         colors = plt.cm.tab20(np.linspace(0, 1, len(packages)))
        
#         for i, package in enumerate(packages.keys()):
#             package_colors[package] = colors[i]
        
#         pos = nx.spring_layout(G, dim=3, seed=42)
        
#         node_xyz = []
#         node_colors = []
#         node_sizes = []
#         labels = {}
        
#         for node in G.nodes():
#             node_xyz.append(pos[node])
            
#             package = "default"
#             for pkg, files in packages.items():
#                 if node in files:
#                     package = pkg
#                     break
            
#             node_colors.append(package_colors.get(package, "gray"))
            
#             if highlight_paths and any(node in path for path in highlight_paths):
#                 node_sizes.append(300)
#             else:
#                 node_sizes.append(150)
            
#             labels[node] = G.nodes[node].get('label', os.path.basename(node))
        
#         node_xyz = np.array(node_xyz)
        
#         scatter = ax.scatter(
#             node_xyz[:, 0],
#             node_xyz[:, 1],
#             node_xyz[:, 2],
#             s=node_sizes,
#             c=node_colors,
#             edgecolors='black',
#             alpha=0.8,
#         )
        
#         for i, j in G.edges():
#             x = np.array([pos[i][0], pos[j][0]])
#             y = np.array([pos[i][1], pos[j][1]])
#             z = np.array([pos[i][2], pos[j][2]])
#             ax.plot(x, y, z, c='gray', alpha=0.3, linewidth=0.8)
        
#         if highlight_paths:
#             for path in highlight_paths:
#                 for k in range(len(path)-1):
#                     i, j = path[k], path[k+1]
#                     if G.has_edge(i, j):
#                         x = np.array([pos[i][0], pos[j][0]])
#                         y = np.array([pos[i][1], pos[j][1]])
#                         z = np.array([pos[i][2], pos[j][2]])
#                         ax.plot(x, y, z, c='red', alpha=0.7, linewidth=2)
        
#         for i, node in enumerate(G.nodes()):
#             ax.text(
#                 node_xyz[i, 0],
#                 node_xyz[i, 1],
#                 node_xyz[i, 2],
#                 labels[node],
#                 fontsize=8,
#                 ha='center',
#                 va='center',
#                 bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=0.5)
#             )
        
#         legend_elements = [
#             plt.Line2D(
#                 [0], [0],
#                 marker='o',
#                 color='w',
#                 label=package,
#                 markerfacecolor=color,
#                 markersize=10
#             )
#             for package, color in package_colors.items()
#         ]
        
#         ax.legend(
#             handles=legend_elements,
#             title="Packages",
#             loc='upper right',
#             bbox_to_anchor=(1.15, 1)
#         )
        
#         ax.set_xlabel("X")
#         ax.set_ylabel("Y")
#         ax.set_zlabel("Z")
#         ax.set_title(f"{project.language.capitalize()} Project 3D Dependency Graph")
        
#         ax.xaxis.pane.fill = False
#         ax.yaxis.pane.fill = False
#         ax.zaxis.pane.fill = False
#         ax.xaxis.pane.set_edgecolor('w')
#         ax.yaxis.pane.set_edgecolor('w')
#         ax.zaxis.pane.set_edgecolor('w')
        
#         ax.grid(True)
        
#         plt.savefig(output_path, dpi=300, bbox_inches='tight')
#         plt.show()
#         logger.info(f"3D project structure visualization saved to {output_path}")

# def main():
#     import sys
    
#     if len(sys.argv) < 2:
#         print("Usage: python project_analyzer.py <project_path> [start_node] [end_node] [output_path]")
#         return
    
#     project_path = sys.argv[1]
#     start_node = sys.argv[2] if len(sys.argv) > 2 else None
#     end_node = sys.argv[3] if len(sys.argv) > 3 else None
#     output_path = sys.argv[4] if len(sys.argv) > 4 else "project_structure_3d.png"
    
#     print(f"Analyzing project at: {project_path}")
    
#     analyzer = ProjectStructureAnalyzer()
#     project = analyzer.analyze_project(project_path)
    
#     highlight_paths = []
#     if start_node and end_node:
#         start_full = None
#         end_full = None
        
#         for file_path in project.files:
#             if start_node in file_path:
#                 start_full = file_path
#             if end_node in file_path:
#                 end_full = file_path
        
#         if start_full and end_full:
#             print(f"Finding relationships between: {start_full} and {end_full}")
#             paths = analyzer.find_relationships(project, start_full, end_full)
            
#             if paths:
#                 print(f"Found {len(paths)} relationship paths:")
#                 for i, path in enumerate(paths, 1):
#                     print(f"\nPath {i}:")
#                     for node in path:
#                         print(f"  - {node} ({project.files[node].classes or project.files[node].functions})")
                
#                 highlight_paths = paths
#             else:
#                 print("No relationships found between the specified nodes.")
#         else:
#             print("Could not find one or both of the specified nodes in the project.")
#             if not start_full:
#                 print(f"Start node '{start_node}' not found.")
#             if not end_full:
#                 print(f"End node '{end_node}' not found.")
    
#     analyzer.visualize_project_structure_3d(
#         project,
#         highlight_paths=highlight_paths,
#         output_path=output_path
#     )
    
#     print(f"Visualization saved to: {output_path}")

# if __name__ == "__main__":
#     main()