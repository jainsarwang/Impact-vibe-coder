import json
import logging
import os
from typing import Dict, List, Optional
from pymongo import MongoClient
from ..utils.session_manager import SessionManager

client = MongoClient("mongodb://localhost:27017")
db = client["impact_vibe_coder"]
session_db = db["session"]

class ChecklistManager:
    """Manages the checklist for tracking file generation progress."""
    def __init__(self, checklist_file: str = "checklist.json", project_prefix: str = None):
        self.session_id = ""
        self.checklist_file = checklist_file
        self.checklist: List[Dict] = []
        self._normalize_paths = True
        # Store the project prefix to handle paths consistently
        self.project_prefix = project_prefix
        
    def _normalize_path(self, path: str) -> str:
        """
        Normalize path for consistent comparison.
        Handles both path separators and project directory prefixes.
        """
        if not self._normalize_paths:
            return path
        # First normalize slashes
        normalized = os.path.normpath(path.replace("\\", "/")).replace("\\", "/")
        
        # Handle project prefix variation
        if self.project_prefix:
            # If path starts with the project prefix, keep it
            if normalized.startswith(f"{self.project_prefix}/"):
                return normalized
                
            # If path doesn't have the prefix but should, add it
            project_name = normalized.split("/")[0]
            if project_name and not normalized.startswith("projects/"):
                # Check if this appears to be a project path without the prefix
                return normalized
        
        # Strip any "projects/" prefix to ensure consistency
        if normalized.startswith("projects/"):
            parts = normalized.split("/", 1)
            if len(parts) > 1:
                project_part = parts[1]
                if self.project_prefix and not project_part.startswith(f"{self.project_prefix}/"):
                    return f"{self.project_prefix}/{project_part}"
                return project_part
        
        return normalized
    
    def _find_checklist_entry(self, file_path: str) -> Optional[Dict]:
        """Find a checklist entry by file path (normalized comparison)."""
        normalized_path = self._normalize_path(file_path)
        for entry in self.checklist:
            if self._normalize_path(entry["file_path"]) == normalized_path:
                return entry
        return None
    
    def initialize_from_directory(self, directory_structure: Dict) -> List[Dict]:
        """Initialize checklist from directory structure."""
        try:
            self.session_id = SessionManager.get()
            if isinstance(directory_structure, str):
                directory_structure = json.loads(directory_structure)
            self.checklist = []
            
            # Extract project name if present
            if "project_name" in directory_structure:
                self.project_prefix = directory_structure["project_name"]
            
            def process_structure(structure: Dict, current_path: str = ""):
                for key, value in structure.items():
                    if key == "files":
                        for file in value:
                            file_path = self._normalize_path(os.path.join(current_path, file))
                            self.checklist.append({
                                "file_path": file_path,
                                "plan_created": False,
                                "file_created": False,
                                "coder": None,
                                "description": ""
                            })
                            logging.debug(f"Added directory file to checklist: {file_path}")
                    elif isinstance(value, dict):
                        new_path = os.path.join(current_path, key)
                        process_structure(value, new_path)
            
            process_structure(directory_structure.get("directory_structure", {}))
            self._save_checklist()
            logging.info(f"Initialized checklist with {len(self.checklist)} items from directory structure")
            return self.checklist
        except Exception as e:
            logging.error(f"Error initializing checklist from directory: {str(e)}")
            return []
    
    def update_from_plan(self, plan: List[Dict]) -> List[Dict]:
        """Update checklist based on the development plan."""
        try:
            if isinstance(plan, str):
                plan = json.loads(plan)
            if not isinstance(plan, list):
                plan = plan.get("plan", [])
            
            logging.info(f"Updating checklist from plan with {len(plan)} items")
            
            for item in plan:
                if "file" in item:
                    file_path = self._normalize_path(item["file"])
                    entry = self._find_checklist_entry(file_path)
                    
                    if entry:
                        # Update existing entry
                        entry["plan_created"] = True
                        entry["coder"] = item.get("coder")
                        if "description" in item:
                            entry["description"] = item.get("description")
                        logging.debug(f"Updated existing file in checklist: {file_path}")
                    else:
                        # Add new entry
                        self.checklist.append({
                            "file_path": file_path,
                            "plan_created": True,
                            "file_created": False,
                            "coder": item.get("coder"),
                            "description": item.get("description", "")
                        })
                        logging.debug(f"Added new planned file to checklist: {file_path}")
            
            self._save_checklist()
            logging.info(f"Checklist updated with plan, now contains {len(self.checklist)} items")
            return self.checklist
        except Exception as e:
            logging.error(f"Error updating checklist from plan: {str(e)}")
            return self.checklist
    
    def mark_file_created(self, file_path: str) -> None:
        """Mark a file as created in the checklist."""
        entry = self._find_checklist_entry(file_path)
        
        if entry:
            entry["file_created"] = True
            self._save_checklist()
            logging.debug(f"Marked file as created in checklist: {file_path}")
        else:
            # If file wasn't in checklist but was created, add it
            normalized_path = self._normalize_path(file_path)
            self.checklist.append({
                "file_path": normalized_path,
                "plan_created": False,  # Wasn't planned but exists
                "file_created": True,
                "coder": None,
                "description": ""
            })
            self._save_checklist()
            logging.warning(f"File {normalized_path} was created but wasn't in checklist. Added to checklist.")

    def update_file_description(self, file_path: str, description: str) -> None:
        """Update the description of a file in the checklist."""
        entry = self._find_checklist_entry(file_path)
        
        if entry:
            entry["description"] = description
            self._save_checklist()
            logging.debug(f"Updated description for file in checklist: {file_path}")
        else:
            logging.warning(f"Attempted to update description for file not in checklist: {file_path}")
    
    def get_next_file_to_process(self) -> Optional[Dict]:
        """Get the next file that needs to be processed."""
        for entry in self.checklist:
            if entry["plan_created"] and not entry["file_created"]:
                logging.debug(f"Found next file to process: {entry['file_path']}")
                return {
                    "file_path": entry["file_path"],
                    "coder": entry["coder"],
                    "description": entry.get("description", "")
                }
        logging.debug("No files left to process in checklist")
        return None
    
    def get_unplanned_files(self) -> List[str]:
        """Get files that exist in directory but have no plan."""
        unplanned = [
            entry["file_path"] for entry in self.checklist
            if not entry["plan_created"] and entry["file_created"]
        ]
        logging.debug(f"Found {len(unplanned)} unplanned files")
        return unplanned
    
    def get_missing_files(self) -> List[str]:
        """Get files that are planned but not created."""
        missing = [
            entry["file_path"] for entry in self.checklist
            if entry["plan_created"] and not entry["file_created"]
        ]
        logging.debug(f"Found {len(missing)} missing files")
        return missing
    
    def is_complete(self) -> bool:
        """Check if all planned files have been created."""
        complete = all(
            not entry["plan_created"] or entry["file_created"]
            for entry in self.checklist
        )
        logging.debug(f"Checklist completion status: {complete}")
        return complete
    
    def _save_checklist(self) -> None:
        """Save checklist to file."""
        try:
            session_db.update_one(
                {"session_id": self.session_id},
                {"$set": {"checklist": self.checklist}},
                upsert=False
            )
            logging.debug(f"Checklist saved to session database")
        except Exception as e:
            logging.error(f"Error saving checklist: {str(e)}")
    
    def load_checklist(self) -> List[Dict]:
        """Load checklist from file."""
        try:
            session_data = session_db.find_one({"session_id": self.session_id})
            if session_data and "checklist" in session_data:
                self.checklist = session_data["checklist"]
                logging.info(f"Loaded checklist with {len(self.checklist)} items from session")
            else:
                self.checklist = []
                logging.info("No existing checklist found in session, starting fresh")
            return self.checklist
        except Exception as e:
            logging.error(f"Error loading checklist: {str(e)}")
            return []
    
    def cleanup_duplicated_paths(self) -> List[Dict]:
        """
        Clean up any duplicate paths in the checklist by merging information.
        This helps fix the issue when the same file is tracked multiple times with different paths.
        """
        # Build a map of normalized paths to their entries
        path_map = {}
        to_remove = set()
        
        for i, entry in enumerate(self.checklist):
            norm_path = self._normalize_path(entry["file_path"])
            if norm_path not in path_map:
                path_map[norm_path] = entry
            else:
                # Merge with existing entry
                existing = path_map[norm_path]
                existing["plan_created"] |= entry["plan_created"]
                existing["file_created"] |= entry["file_created"]
                if entry["coder"] is not None:
                    existing["coder"] = entry["coder"]
                if entry.get("description"):
                    existing["description"] = entry["description"]
                to_remove.add(i)
        
        # Remove duplicates (working backwards to preserve indices)
        if to_remove:
            self.checklist = [entry for i, entry in enumerate(self.checklist) if i not in to_remove]
            logging.info(f"Removed {len(to_remove)} duplicate path entries from checklist")
            self._save_checklist()
            
        return self.checklist