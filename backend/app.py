import os
import zipfile
from flask import Flask, send_file, request, jsonify

app = Flask(__name__)

def create_project_directory(code_snippets):
    """Generate project files from key-value pairs."""
    project_dir = "generated_projects/scientific_calculator_project"
    os.makedirs(project_dir, exist_ok=True)
    
    for file_path, content in code_snippets.items():
        dir_path = os.path.join(project_dir, os.path.dirname(file_path))
        os.makedirs(dir_path, exist_ok=True) if dir_path else None
        with open(os.path.join(project_dir, file_path), "w") as f:
            f.write(content.strip())
    return project_dir

def zip_project(project_dir):
    zip_path = f"{project_dir}.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for root, _, files in os.walk(project_dir):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, project_dir))
    return zip_path

@app.route("/generate_project", methods=["POST"])
def generate_project():
    code_snippets = request.json
    project_dir = create_project_directory(code_snippets)
    zip_path = zip_project(project_dir)
    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    os.makedirs("generated_projects", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)