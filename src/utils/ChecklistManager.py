import json
import logging
import os
from typing import Dict, List, Optional


class ChecklistManager:
    """Manages the checklist for tracking file generation progress."""

    def __init__(self, checklist_file: str = "checklist.json"):
        self.checklist_file = checklist_file
        self.checklist: Dict[str, Dict] = {}
        
    def initialize_from_directory(self, directory_structure: Dict) -> Dict:
        """Initialize checklist from directory structure."""
        try:
            if isinstance(directory_structure, str):
                directory_structure = json.loads(directory_structure)
                
            self.checklist = {}
            
            def process_structure(structure: Dict, current_path: str = ""):
                for key, value in structure.items():
                    if key == "files":
                        for file in value:
                            file_path = os.path.join(current_path, file)
                            self.checklist[file_path] = {
                                "plan_created": False,
                                "file_created": False,
                                "coder": None
                            }
                    elif isinstance(value, dict):
                        new_path = os.path.join(current_path, key)
                        process_structure(value, new_path)
            
            process_structure(directory_structure.get("directory_structure", {}))
            self._save_checklist()
            return self.checklist
            
        except Exception as e:
            logging.error(f"Error initializing checklist from directory: {str(e)}")
            return {}

    def update_from_plan(self, plan: List[Dict]) -> Dict:
        """Update checklist based on the development plan."""
        try:
            if isinstance(plan, str):
                plan = json.loads(plan)
                
            if not isinstance(plan, list):
                plan = plan.get("plan", [])
                
            for item in plan:
                if "file" in item:
                    file_path = item["file"]
                    if file_path not in self.checklist:
                        self.checklist[file_path] = {
                            "plan_created": True,
                            "file_created": False,
                            "coder": item.get("coder")
                        }
                    else:
                        self.checklist[file_path]["plan_created"] = True
                        self.checklist[file_path]["coder"] = item.get("coder")
            
            self._save_checklist()
            return self.checklist
            
        except Exception as e:
            logging.error(f"Error updating checklist from plan: {str(e)}")
            return self.checklist

    def mark_file_created(self, file_path: str) -> None:
        """Mark a file as created in the checklist."""
        if file_path in self.checklist:
            self.checklist[file_path]["file_created"] = True
            self._save_checklist()

    def get_next_file_to_process(self) -> Optional[Dict]:
        """Get the next file that needs to be processed."""
        for file_path, status in self.checklist.items():
            if status["plan_created"] and not status["file_created"]:
                return {
                    "file_path": file_path,
                    "coder": status["coder"]
                }
        return None

    def get_unplanned_files(self) -> List[str]:
        """Get files that exist in directory but have no plan."""
        return [
            file_path for file_path, status in self.checklist.items()
            if not status["plan_created"]
        ]

    def get_missing_files(self) -> List[str]:
        """Get files that are planned but not created."""
        return [
            file_path for file_path, status in self.checklist.items()
            if status["plan_created"] and not status["file_created"]
        ]

    def is_complete(self) -> bool:
        """Check if all planned files have been created."""
        return all(
            not status["plan_created"] or status["file_created"]
            for status in self.checklist.values()
        )

    def _save_checklist(self) -> None:
        """Save checklist to file."""
        try:
            with open(self.checklist_file, "w") as f:
                json.dump(self.checklist, f, indent=2)
        except Exception as e:
            logging.error(f"Error saving checklist: {str(e)}")

    def load_checklist(self) -> Dict:
        """Load checklist from file."""
        try:
            with open(self.checklist_file) as f:
                self.checklist = json.load(f)
                return self.checklist
        except (FileNotFoundError, json.JSONDecodeError):
            return {}