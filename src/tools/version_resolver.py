from langchain.tools import Tool  # Add this import
import subprocess
import re
from typing import Dict, Any

def resolve_version_conflicts(issue_description: str) -> Dict[str, Any]:
    """
    Handles version conflicts by analyzing package manager errors
    and executing appropriate resolution commands.
    """
    result = {"status": "unresolved", "actions": []}
    
    try:
        # Python package conflicts
        if "pip" in issue_description or "Python" in issue_description:
            py_match = re.search(
                r"ERROR: Cannot install (\w+)==([\d.]+).*requires (\w+)([<>=!]+)([\d.]+)", 
                issue_description
            )
            if py_match:
                pkg1, ver1, pkg2, op, ver2 = py_match.groups()
                cmd = f"pip install {pkg1}>={ver1} {pkg2}{op}{ver2} --dry-run"
                output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                result.update({
                    "status": "resolved",
                    "actions": [f"Would execute: {cmd}"],
                    "resolution": {
                        "packages": {pkg1: ver1, pkg2: f"{op}{ver2}"},
                        "strategy": "version_constraint"
                    }
                })
        
        # Node.js conflicts
        elif "npm" in issue_description or "yarn" in issue_description:
            npm_match = re.search(
                r"peer dependency (\w+)@([\d.]+).*but found (\w+)@([\d.]+)", 
                issue_description
            )
            if npm_match:
                pkg1, ver1, pkg2, ver2 = npm_match.groups()
                result.update({
                    "status": "resolved",
                    "actions": ["npm install --legacy-peer-deps"],
                    "resolution": {
                        "packages": {pkg1: ver1, pkg2: ver2},
                        "strategy": "legacy_peer_deps"
                    }
                })
    
    except Exception as e:
        result["error"] = str(e)
    
    return result

# Define the tool instance after the function is defined
version_resolver_tool = Tool(
    name="version_resolver",
    func=resolve_version_conflicts,
    description="Resolves package version conflicts in Python and Node.js projects"
)

# Explicitly export the tool
__all__ = ["version_resolver_tool"]