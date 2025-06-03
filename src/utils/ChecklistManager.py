import json
import logging
import os
from typing import Dict, List, Optional
from pymongo import MongoClient

# Initialize MongoDB client with error handling
try:
    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
    db = client["impact_vibe_coder"]
    if "    " in db.list_collection_names():
        db.drop_collection("checklist")  # Clear existing checklist if it exists
    db.create_collection("checklist")
    collection = db["checklist"]
except Exception as e:
    logging.error(f"Error connecting to MongoDB: {str(e)}")
    raise


class ChecklistManager:
    """Manages the checklist for tracking file generation progress."""

    def __init__(self, checklist_file: str = "checklist.json", project_prefix: str = None):
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
                if self.project_prefix and not project_part.startswith(
                        f"{self.project_prefix}/"):
                    return f"{self.project_prefix}/{project_part}"
                return project_part

        return normalized

    def get_canonical_path(self, path: str) -> str:
        """
        Get the canonical path used in the checklist for a given path.
        This helps find the proper key when there might be multiple ways to refer to the same file.
        """
        normalized = self._normalize_path(path)

        # First try direct lookup
        for item in self.checklist:
            if item["file_path"] == normalized:
                return normalized

        # Try with/without project prefix
        if normalized.startswith("projects/"):
            alt_path = normalized.split("/", 1)[1]
            for item in self.checklist:
                if item["file_path"] == alt_path:
                    return alt_path
        else:
            alt_path = f"projects/{normalized}"
            for item in self.checklist:
                if item["file_path"] == alt_path:
                    return alt_path

        # Try the path as provided
        for item in self.checklist:
            if item["file_path"] == path:
                return path

        # If all else fails, return the normalized path
        return normalized

    def initialize_from_directory(self, directory_structure: Dict) -> Dict:
        """Initialize checklist from directory structure."""
        try:
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
                                "description": None
                            })
                            logging.debug(f"Added directory file to checklist: {file_path}")
                    elif isinstance(value, dict):
                        new_path = os.path.join(current_path, key)
                        process_structure(value, new_path)

            process_structure(directory_structure.get("directory_structure", {}))
            self._save_checklist()
            logging.info(
                f"Initialized checklist with {len(self.checklist)} items from directory structure")
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

            logging.info(f"Updating checklist from plan with {len(plan)} items")

            for item in plan:
                if "file" in item:
                    file_path = self._normalize_path(item["file"])
                    # Check if this file or a variant already exists in the checklist
                    existing_path = self.get_canonical_path(file_path)

                    if existing_path != file_path:  # and existing_path in self.checklist:
                        # Update the existing entry instead of creating a new one
                        for entry in self.checklist:
                            if entry["file_path"] == existing_path:
                                entry["plan_created"] = True
                                entry["coder"] = item.get("coder")
                                logging.debug(
                                    f"Updated existing file in checklist: {existing_path} (from {file_path})")
                                break

                    else:
                        found = False
                        for entry in self.checklist:
                            if entry["file_path"] == file_path:
                                entry["plan_created"] = True
                                entry["coder"] = item.get("coder")
                                logging.debug(f"Updated existing file in checklist: {file_path}")
                                found = True
                                break
                        if not found:
                            self.checklist.append({
                                "file_path": file_path,
                                "plan_created": True,
                                "file_created": False,
                                "coder": item.get("coder"),
                                "description": None
                            })
                            logging.debug(f"Added new planned file to checklist: {file_path}")

            self._save_checklist()
            logging.info(
                f"Checklist updated with plan, now contains {len(self.checklist)} items")
            return self.checklist
        except Exception as e:
            logging.error(f"Error updating checklist from plan: {str(e)}")
            return self.checklist

    def mark_file_created(self, file_path: str) -> None:
        """Mark a file as created in the checklist."""
        # Try to find the canonical path in the checklist
        canonical_path = self.get_canonical_path(file_path)

        #if canonical_path in self.checklist:
        for entry in self.checklist:
            if entry["file_path"] == canonical_path:
                entry["file_created"] = True
                self._save_checklist()
                logging.debug(f"Marked file as created in checklist: {canonical_path}")
                return # Exit function after updating

        #else:
        # If file wasn't in checklist but was created, add it
        normalized_path = self._normalize_path(file_path)
        self.checklist.append({
            "file_path": normalized_path,
            "plan_created": False,  # Wasn't planned but exists
            "file_created": True,
            "coder": None,
            "description": None
        })
        self._save_checklist()
        logging.warning(
            f"File {normalized_path} was created but wasn't in checklist. Added to checklist.")


    def get_next_file_to_process(self) -> Optional[Dict]:
        """Get the next file that needs to be processed."""
        for items in self.checklist:
            if not items["plan_created"] and items["file_created"]:
                # Found a file that exists but has no plan
                logging.debug(f"Next file to process: {items['file_path']}")
                return items

            if items["plan_created"] and not items["file_created"]:
                # Found a planned file that hasn't been created yet
                logging.debug(f"Next file to create: {items['file_path']}")
                return items
        logging.debug("No files left to process in checklist")
        return None

    def get_unplanned_files(self) -> List[str]:
        """Get files that exist in directory but have no plan."""
        unplanned = [
            item["file_path"] for item in self.checklist
            if not item["plan_created"] and item["file_created"]
        ]
        logging.debug(f"Found {len(unplanned)} unplanned files")
        return unplanned

    def get_missing_files(self) -> List[str]:
        """Get files that are planned but not created."""
        missing = [
            item["file_path"] for item in self.checklist
            if item["plan_created"] and not item["file_created"]
        ]
        logging.debug(f"Found {len(missing)} missing files")
        return missing

    def is_complete(self) -> bool:
        """Check if all planned files have been created."""
        complete = all(
            not item["plan_created"] or item["file_created"]
            for item in self.checklist
        )
        logging.debug(f"Checklist completion status: {complete}")
        return complete

    def _save_checklist(self) -> None:
        """Save checklist to MongoDB."""
        try:
            if self.checklist:  # Only save if there's data
                collection.update_one(
                    {"_id": "checklist"},
                    {"$set": {"data": self.checklist}},
                    upsert=True
                )
                logging.debug("Checklist saved to MongoDB")
        except Exception as e:
            logging.error(f"Error saving checklist to MongoDB: {str(e)}")

    def load_checklist(self) -> Dict:
        """Load checklist from MongoDB."""
        try:
            doc = collection.find_one({"_id": "checklist"})
            if doc and "data" in doc:
                self.checklist = doc["data"]
                logging.info(
                    f"Loaded checklist with {len(self.checklist)} items from MongoDB")
            else:
                self.checklist = []
                logging.info(
                    "No existing checklist found in MongoDB, starting fresh")
            return self.checklist
        except Exception as e:
            logging.error(f"Error loading checklist from MongoDB: {str(e)}")
            return {}

    def cleanup_duplicated_paths(self) -> Dict:
        """
        Clean up any duplicate paths in the checklist by merging information.
        This helps fix the issue when the same file is tracked multiple times with different paths.
        """
        # Build a map of normalized paths to all their variant forms
        path_variants = {}
        for item in list(self.checklist):
            norm_path = self._normalize_path(item["file_path"])
            if norm_path not in path_variants:
                path_variants[norm_path] = []
            path_variants[norm_path].append(item["file_path"])

        # Process duplicates
        merged_count = 0
        for norm_path, variants in path_variants.items():
            if len(variants) > 1:
                # Multiple entries for the same normalized path - merge them
                merged_entry = {
                    "plan_created": False,
                    "file_created": False,
                    "coder": None,
                    "file_path": variants[0] # Keep the first variant's path
                }

                # Combine information from all variants
                for variant in variants:
                    #Find the matching entry
                    for i, entry in enumerate(self.checklist):
                        if entry["file_path"] == variant:
                            merged_entry["plan_created"] |= entry["plan_created"]
                            merged_entry["file_created"] |= entry["file_created"]
                            if entry["coder"] is not None:
                                merged_entry["coder"] = entry["coder"]

                            # Remove all but the first variant
                            if variant != variants[0]:
                                del self.checklist[i]
                            break

                # Update the remaining entry with merged info - find index by file_path
                for i, entry in enumerate(self.checklist):
                    if entry["file_path"] == variants[0]:
                        self.checklist[i] = merged_entry
                        break
                merged_count += 1

        if merged_count > 0:
            logging.info(
                f"Merged {merged_count} duplicate path entries in checklist")
            self._save_checklist()

        return self.checklist