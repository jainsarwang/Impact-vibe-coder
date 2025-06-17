import json
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from ..utils.session_manager import SessionManager
from ..models.session_schema import session_schema 
from ..service.database import db

# Create collection with strict schema validation
try:
    db.create_collection("session", validator=session_schema)
    db.command({
        'collMod': 'session',
        'validator': session_schema,
        'validationLevel': 'strict',
        'validationAction': 'error'  # This makes it fail hard on invalid data
    })
except Exception as e:
    logging.debug(f"Collection setup note: {str(e)}")
    # For existing collections, ensure the schema is applied strictly
    db.command({
        'collMod': 'session',
        'validator': session_schema,
        'validationLevel': 'strict',
        'validationAction': 'error'
    })
    
session_db = db["session"]

class ChecklistManager:
    """Manages the checklist for tracking file generation and validation progress."""
    def __init__(self, state, checklist_file: str = "checklist.json", project_prefix: str = None):
        self.session_id = ""
        self.checklist_file = checklist_file
        self.checklist: List[Dict] = []
        self._normalize_paths = True
        # Store the project prefix to handle paths consistently
        self.project_prefix = project_prefix
        self.state = state
        
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
    
    def _create_checklist_entry(self, file_path: str, **kwargs) -> Dict:
        """Create a new checklist entry with default validation fields."""
        entry = {
            "file_path": self._normalize_path(file_path),
            "plan_created": kwargs.get("plan_created", False),
            "file_created": kwargs.get("file_created", False),
            "coder": kwargs.get("coder", None),
            "description": kwargs.get("description", ""),
            # Validation fields
            "validated": kwargs.get("validated", False),
            "validation_passed": kwargs.get("validation_passed", False),
            "validation_in_progress": kwargs.get("validation_in_progress", False),
            "validation_date": kwargs.get("validation_date", None),
            "validation_failed_count": kwargs.get("validation_failed_count", 0),
            "reason": kwargs.get("reason","")
        }
        return entry
    
    def initialize_from_directory(self, directory_structure: Dict) -> List[Dict]:
        """Initialize checklist from directory structure with validation fields."""
        try:
            self.session_id = self.state.get("session_id")
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
                            entry = self._create_checklist_entry(file_path)
                            self.checklist.append(entry)
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
                        # Add new entry with validation fields
                        new_entry = self._create_checklist_entry(
                            file_path,
                            plan_created=True,
                            coder=item.get("coder"),
                            description=item.get("description", "")
                        )
                        self.checklist.append(new_entry)
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
            # Reset validation status when file is recreated
            entry["validated"] = False
            entry["validation_passed"] = False
            entry["validation_in_progress"] = False
            entry["validation_date"] = None
            entry["validation_failed_count"] = 0
            self._save_checklist()
            logging.debug(f"Marked file as created in checklist: {file_path}")
        else:
            # If file wasn't in checklist but was created, add it with validation fields
            new_entry = self._create_checklist_entry(
                file_path,
                plan_created=False,  # Wasn't planned but exists
                file_created=True
            )
            self.checklist.append(new_entry)
            self._save_checklist()
            logging.warning(f"File {file_path} was created but wasn't in checklist. Added to checklist.")

    def update_file_description(self, file_path: str, description: str) -> None:
        """Update the description of a file in the checklist."""
        entry = self._find_checklist_entry(file_path)
        
        if entry:
            entry["description"] = description
            logging.info(f"description: {description}")
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
    
    def next_file_to_validate(self) -> Optional[Dict]:
        """Get the next file that needs to be validated."""
        for entry in self.checklist:
            # Only validate files that have been created but not yet validated
            if (entry["file_created"] and 
                not entry.get("validated", False) and 
                not entry.get("validation_passed", False) and
                not entry.get("validation_in_progress", False)):
                
                # Mark as validation in progress to avoid duplicate processing
                entry["validation_in_progress"] = True
                self._save_checklist()
                
                logging.debug(f"Found next file to validate: {entry['file_path']}")
                return {
                    "file_path": entry["file_path"],
                    "coder": entry.get("coder"),
                    "description": entry.get("description", ""),
                    "plan_created": entry.get("plan_created", False)
                }
        
        logging.debug("No files left to validate in checklist")
        return None
    
    def mark_file_validated(self, file_path: str, reason: str ,validation_passed: bool = True) -> None:
        """Mark a file as validated in the checklist."""
        entry = self._find_checklist_entry(file_path)
        
        if entry:
            entry["validated"] = True
            entry["validation_passed"] = validation_passed
            entry["validation_in_progress"] = False  # Clear the in-progress flag
            entry["validation_date"] = datetime.now().isoformat()
            
            if not validation_passed:
                entry["validation_failed_count"] = entry.get("validation_failed_count", 0) + 1
                entry["reason"] = reason
                entry["validated"] = False
                logging.warning(f"File {file_path} failed validation (attempt #{entry['validation_failed_count']})")
            else:
                entry["validation_failed_count"] = 0  # Reset failed count on success
                entry["reason"] = reason
                logging.info(f"File {file_path} passed validation")
            
            self._save_checklist()
            logging.debug(f"Marked file validation status in checklist: {file_path} - {'Passed' if validation_passed else 'Failed'}")
        else:
            logging.warning(f"Attempted to mark validation for file not in checklist: {file_path}")
    
    def get_validation_summary(self) -> Dict:
        """Get a summary of validation status for all files."""
        total_files = len([entry for entry in self.checklist if entry["file_created"]])
        validated_files = len([entry for entry in self.checklist 
                              if entry.get("validated", False) and entry.get("validation_passed", False)])
        failed_files = len([entry for entry in self.checklist 
                           if entry.get("validated", False) and not entry.get("validation_passed", False)])
        pending_files = len([entry for entry in self.checklist 
                            if entry["file_created"] and not entry.get("validated", False)])
        
        summary = {
            "total_files": total_files,
            "validated_files": validated_files,
            "failed_files": failed_files,
            "pending_files": pending_files,
            "validation_complete": pending_files == 0
        }
        
        logging.debug(f"Validation summary: {summary}")
        return summary
    
    def get_file_description(self, file_path: str) -> Optional[str]:
        """Get the description of a file from the checklist."""
        entry = self._find_checklist_entry(file_path)
        if entry:
            return entry.get("description", "")
        return None
    
    def get_failed_validation_files(self) -> List[Dict]:
        """Get all files that failed validation."""
        failed_files = []
        for entry in self.checklist:
            if (entry.get("validated", False) and 
                not entry.get("validation_passed", False)):
                failed_files.append({
                    "file_path": entry["file_path"],
                    "description": entry.get("description", ""),
                    "failed_count": entry.get("validation_failed_count", 0),
                    "validation_date": entry.get("validation_date")
                })
        
        logging.debug(f"Found {len(failed_files)} files that failed validation")
        return failed_files
    
    def reset_validation_status(self, file_path: str = None) -> None:
        """Reset validation status for a specific file or all files."""
        if file_path:
            # Reset specific file
            entry = self._find_checklist_entry(file_path)
            if entry:
                entry["validated"] = False
                entry["validation_passed"] = False
                entry["validation_in_progress"] = False
                entry["validation_date"] = None
                entry["validation_failed_count"] = 0
                logging.info(f"Reset validation status for file: {file_path}")
        else:
            # Reset all files
            for entry in self.checklist:
                entry["validated"] = False
                entry["validation_passed"] = False
                entry["validation_in_progress"] = False
                entry["validation_date"] = None
                entry["validation_failed_count"] = 0
            logging.info("Reset validation status for all files")
        
        self._save_checklist()
    
    def is_validation_complete(self) -> bool:
        """Check if all created files have been validated successfully."""
        for entry in self.checklist:
            if entry["file_created"]:
                if not entry.get("validated", False):
                    return False
                if not entry.get("validation_passed", False):
                    return False
        
        validation_complete = True
        logging.debug(f"Validation completion status: {validation_complete}")
        return validation_complete
    
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
    
    def get_checklist_status(self) -> Dict:
        """Get comprehensive status of the entire checklist including validation."""
        total_planned = len([e for e in self.checklist if e["plan_created"]])
        total_created = len([e for e in self.checklist if e["file_created"]])
        total_validated = len([e for e in self.checklist if e.get("validated", False)])
        total_validation_passed = len([e for e in self.checklist 
                                     if e.get("validated", False) and e.get("validation_passed", False)])
        
        status = {
            "total_entries": len(self.checklist),
            "planned_files": total_planned,
            "created_files": total_created,
            "validated_files": total_validated,
            "validation_passed": total_validation_passed,
            "coding_complete": self.is_complete(),
            "validation_complete": self.is_validation_complete(),
            "overall_complete": self.is_complete() and self.is_validation_complete()
        }
        
        return status
    
    def _migrate_existing_entries(self) -> None:
        """Migrate existing checklist entries to include validation fields."""
        migrated_count = 0
        for entry in self.checklist:
            if "validated" not in entry:
                entry["validated"] = False
                entry["validation_passed"] = False
                entry["validation_in_progress"] = False
                entry["validation_date"] = None
                entry["validation_failed_count"] = 0
                migrated_count += 1
        
        if migrated_count > 0:
            logging.info(f"Migrated {migrated_count} checklist entries to include validation fields")
            self._save_checklist()
    
    def _save_checklist(self) -> None:
        """Save checklist to database with schema validation."""
        try:            
            update_data = {
                '$set': {
                    'checklist': self.checklist,
                    'updated_at': datetime.now(),
                },
                '$setOnInsert': {
                    'created_at': datetime.now(),
                    'session_id': self.session_id
                }
            }
            
            session_db.update_one(
                {"session_id": self.session_id},
                update_data,
                upsert=True
            )
            logging.debug(f"Checklist saved to session database")
        except Exception as e:
            logging.error(f"Error saving checklist: {str(e)}")
            if "Document failed validation" in str(e):
                logging.error("Data validation failed. Checklist data doesn't match schema.")
        
    
    def load_checklist(self) -> List[Dict]:
        """Load checklist from database and migrate if necessary."""
        try:
            session_data = session_db.find_one({"session_id": self.session_id})
            if session_data and "checklist" in session_data:
                self.checklist = session_data["checklist"]
                # Migrate existing entries to include validation fields
                self._migrate_existing_entries()
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
                
                # Merge validation fields (keep the most advanced state)
                existing["validated"] = existing.get("validated", False) or entry.get("validated", False)
                existing["validation_passed"] = (existing.get("validation_passed", False) or 
                                               entry.get("validation_passed", False))
                existing["validation_in_progress"] = (existing.get("validation_in_progress", False) or 
                                                    entry.get("validation_in_progress", False))
                
                # Keep the latest validation date
                if entry.get("validation_date") and existing.get("validation_date"):
                    existing["validation_date"] = max(existing["validation_date"], entry["validation_date"])
                elif entry.get("validation_date"):
                    existing["validation_date"] = entry["validation_date"]
                
                # Sum failed counts
                existing["validation_failed_count"] = (existing.get("validation_failed_count", 0) + entry.get("validation_failed_count", 0))
                
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
    
    def update_tokens(self, tokens) -> None:
        logging.info(f"tokens: {tokens}")
        if tokens >=0: 
            session_db.update_one({"session_id": self.session_id}, {"$set": {"tokens": tokens}})
        else:
            raise Exception("tokens are invalid")
        