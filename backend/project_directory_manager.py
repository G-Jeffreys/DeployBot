#!/usr/bin/env python3
"""
Project Directory Management System for DeployBot

This module handles the mapping between project names and their custom directory locations,
providing a centralized system for storing and retrieving project paths.

This enables users to store projects anywhere on their filesystem rather than being
restricted to the default DeployBot/projects directory.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import structlog

logger = structlog.get_logger()

class ProjectDirectoryManager:
    """
    Manages project name → directory path mappings for custom project locations.
    
    This class provides:
    - Storage of project directory mappings in a JSON file
    - Validation of project directories
    - Path resolution for projects
    - Migration support for existing projects
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize the ProjectDirectoryManager
        
        Args:
            config_dir: Optional custom config directory path
        """
        # Set up configuration directory
        if config_dir:
            self.config_dir = Path(config_dir).resolve()
        else:
            # Default to ~/.deploybot for cross-platform compatibility
            self.config_dir = Path.home() / ".deploybot"
        
        # Ensure config directory exists
        self.config_dir.mkdir(exist_ok=True)
        
        # Configuration file for project mappings
        self.mappings_file = self.config_dir / "project_mappings.json"
        
        # Default projects directory (for backward compatibility)
        self.default_projects_root = Path(__file__).parent.parent / "projects"
        
        # In-memory cache of mappings
        self._mappings_cache: Dict[str, str] = {}
        self._cache_loaded = False
        
        logger.info("📂 [PROJECT_DIR_MANAGER] ProjectDirectoryManager initialized", 
                   config_dir=str(self.config_dir),
                   mappings_file=str(self.mappings_file),
                   default_root=str(self.default_projects_root))

    async def load_mappings(self) -> Dict[str, str]:
        """
        Load project directory mappings from storage
        
        Returns:
            Dictionary mapping project names to directory paths
        """
        logger.info("📖 [PROJECT_DIR_MANAGER] Loading project directory mappings...")
        
        try:
            if not self.mappings_file.exists():
                logger.info("📄 [PROJECT_DIR_MANAGER] No mappings file found, creating empty mappings")
                await self._save_mappings({})
                return {}
            
            with open(self.mappings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract just the mappings from the stored data
            mappings = data.get("project_mappings", {})
            
            # Update cache
            self._mappings_cache = mappings.copy()
            self._cache_loaded = True
            
            logger.info("✅ [PROJECT_DIR_MANAGER] Project mappings loaded successfully", 
                       project_count=len(mappings),
                       projects=list(mappings.keys()))
            
            return mappings
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Failed to load project mappings", 
                        error=str(e))
            # Return empty mappings on error
            return {}

    async def _save_mappings(self, mappings: Dict[str, str]) -> bool:
        """
        Save project directory mappings to storage
        
        Args:
            mappings: Dictionary mapping project names to directory paths
            
        Returns:
            True if saved successfully, False otherwise
        """
        logger.info("💾 [PROJECT_DIR_MANAGER] Saving project directory mappings...", 
                   project_count=len(mappings))
        
        try:
            # Create comprehensive storage data
            storage_data = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "default_projects_root": str(self.default_projects_root),
                "total_projects": len(mappings),
                "project_mappings": mappings,
                "metadata": {
                    "created_by": "DeployBot ProjectDirectoryManager",
                    "format_description": "Project name to directory path mappings"
                }
            }
            
            # Ensure directory exists
            self.config_dir.mkdir(exist_ok=True)
            
            # Write to temporary file first, then atomic rename
            temp_file = self.mappings_file.with_suffix('.json.tmp')
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(storage_data, f, indent=2, ensure_ascii=False)
            
            # Atomic rename for safety
            temp_file.replace(self.mappings_file)
            
            # Update cache
            self._mappings_cache = mappings.copy()
            self._cache_loaded = True
            
            logger.info("✅ [PROJECT_DIR_MANAGER] Project mappings saved successfully")
            return True
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Failed to save project mappings", 
                        error=str(e))
            return False

    async def add_project_mapping(self, project_name: str, project_path: str) -> bool:
        """
        Add or update a project directory mapping
        
        Args:
            project_name: Name of the project
            project_path: Full path to the project directory
            
        Returns:
            True if added successfully, False otherwise
        """
        logger.info("➕ [PROJECT_DIR_MANAGER] Adding project mapping", 
                   project_name=project_name, project_path=project_path)
        
        try:
            # Validate the project path
            path_obj = Path(project_path).resolve()
            
            if not path_obj.exists():
                logger.error("❌ [PROJECT_DIR_MANAGER] Project path does not exist", 
                           project_path=str(path_obj))
                return False
            
            if not path_obj.is_dir():
                logger.error("❌ [PROJECT_DIR_MANAGER] Project path is not a directory", 
                           project_path=str(path_obj))
                return False
            
            # Load current mappings
            mappings = await self.load_mappings()
            
            # Add the new mapping
            mappings[project_name] = str(path_obj)
            
            # Save updated mappings
            success = await self._save_mappings(mappings)
            
            if success:
                logger.info("✅ [PROJECT_DIR_MANAGER] Project mapping added successfully", 
                           project_name=project_name, resolved_path=str(path_obj))
            
            return success
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Failed to add project mapping", 
                        project_name=project_name, error=str(e))
            return False

    async def remove_project_mapping(self, project_name: str) -> bool:
        """
        Remove a project directory mapping
        
        Args:
            project_name: Name of the project to remove
            
        Returns:
            True if removed successfully, False otherwise
        """
        logger.info("🗑️ [PROJECT_DIR_MANAGER] Removing project mapping", 
                   project_name=project_name)
        
        try:
            # Load current mappings
            mappings = await self.load_mappings()
            
            if project_name not in mappings:
                logger.warning("⚠️ [PROJECT_DIR_MANAGER] Project mapping not found", 
                             project_name=project_name)
                return False
            
            # Remove the mapping
            removed_path = mappings.pop(project_name)
            
            # Save updated mappings
            success = await self._save_mappings(mappings)
            
            if success:
                logger.info("✅ [PROJECT_DIR_MANAGER] Project mapping removed successfully", 
                           project_name=project_name, removed_path=removed_path)
            
            return success
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Failed to remove project mapping", 
                        project_name=project_name, error=str(e))
            return False

    async def get_project_path(self, project_name: str) -> Optional[str]:
        """
        Get the directory path for a project
        
        Args:
            project_name: Name of the project
            
        Returns:
            Full path to the project directory, or None if not found
        """
        logger.debug("🔍 [PROJECT_DIR_MANAGER] Looking up project path", 
                    project_name=project_name)
        
        try:
            # Load mappings if not cached
            if not self._cache_loaded:
                await self.load_mappings()
            
            # Check custom mappings first
            if project_name in self._mappings_cache:
                custom_path = self._mappings_cache[project_name]
                logger.debug("📍 [PROJECT_DIR_MANAGER] Found custom mapping", 
                           project_name=project_name, path=custom_path)
                return custom_path
            
            # Fallback to default directory
            default_path = self.default_projects_root / project_name
            if default_path.exists():
                logger.debug("📍 [PROJECT_DIR_MANAGER] Found in default directory", 
                           project_name=project_name, path=str(default_path))
                return str(default_path)
            
            logger.debug("❓ [PROJECT_DIR_MANAGER] Project not found", 
                        project_name=project_name)
            return None
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Error looking up project path", 
                        project_name=project_name, error=str(e))
            return None

    async def list_all_projects(self) -> List[Tuple[str, str]]:
        """
        List all projects and their directory paths
        
        Returns:
            List of tuples (project_name, project_path)
        """
        logger.info("📋 [PROJECT_DIR_MANAGER] Listing all projects...")
        
        try:
            projects = []
            
            # Load custom mappings
            mappings = await self.load_mappings()
            
            # Add custom mapped projects
            for project_name, project_path in mappings.items():
                if Path(project_path).exists():
                    projects.append((project_name, project_path))
                else:
                    logger.warning("⚠️ [PROJECT_DIR_MANAGER] Custom project path no longer exists", 
                                 project_name=project_name, path=project_path)
            
            # Add projects from default directory that aren't already mapped
            if self.default_projects_root.exists():
                for project_dir in self.default_projects_root.iterdir():
                    if not project_dir.is_dir():
                        continue
                    
                    project_name = project_dir.name
                    
                    # Skip if already in custom mappings
                    if project_name in mappings:
                        continue
                    
                    # Check if it's a valid DeployBot project
                    config_file = project_dir / "config.json"
                    todo_file = project_dir / "TODO.md"
                    
                    if config_file.exists() and todo_file.exists():
                        projects.append((project_name, str(project_dir)))
            
            logger.info("✅ [PROJECT_DIR_MANAGER] Project listing completed", 
                       total_projects=len(projects),
                       custom_mapped=len(mappings),
                       default_directory=len(projects) - len(mappings))
            
            return projects
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Failed to list projects", error=str(e))
            return []

    async def validate_project_directory(self, project_path: str) -> Dict[str, Any]:
        """
        Validate that a directory is suitable for a DeployBot project
        
        Args:
            project_path: Path to validate
            
        Returns:
            Validation result with details
        """
        logger.info("🔍 [PROJECT_DIR_MANAGER] Validating project directory", 
                   project_path=project_path)
        
        try:
            path_obj = Path(project_path).resolve()
            
            result = {
                "valid": False,
                "path": str(path_obj),
                "exists": False,
                "is_directory": False,
                "writable": False,
                "has_config": False,
                "has_todo": False,
                "has_logs_dir": False,
                "issues": []
            }
            
            # Check existence
            if not path_obj.exists():
                result["issues"].append("Directory does not exist")
                return result
            
            result["exists"] = True
            
            # Check if it's a directory
            if not path_obj.is_dir():
                result["issues"].append("Path is not a directory")
                return result
            
            result["is_directory"] = True
            
            # Check writability
            try:
                test_file = path_obj / ".deploybot_write_test"
                test_file.touch()
                test_file.unlink()
                result["writable"] = True
            except Exception:
                result["issues"].append("Directory is not writable")
            
            # Check for DeployBot project files
            config_file = path_obj / "config.json"
            todo_file = path_obj / "TODO.md"
            logs_dir = path_obj / "logs"
            
            result["has_config"] = config_file.exists()
            result["has_todo"] = todo_file.exists()
            result["has_logs_dir"] = logs_dir.exists() and logs_dir.is_dir()
            
            # Determine if valid
            result["valid"] = (
                result["exists"] and 
                result["is_directory"] and 
                result["writable"]
            )
            
            # Add recommendations for new projects
            if result["valid"] and not (result["has_config"] or result["has_todo"]):
                result["recommendation"] = "Directory is suitable for a new DeployBot project"
            elif result["valid"] and result["has_config"] and result["has_todo"]:
                result["recommendation"] = "Existing DeployBot project detected"
            elif result["valid"]:
                result["recommendation"] = "Directory exists but missing some DeployBot files"
            
            logger.info("✅ [PROJECT_DIR_MANAGER] Directory validation completed", 
                       path=str(path_obj), valid=result["valid"], 
                       issues=len(result["issues"]))
            
            return result
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Error validating directory", 
                        project_path=project_path, error=str(e))
            return {
                "valid": False,
                "error": str(e),
                "issues": [f"Validation error: {str(e)}"]
            }

    async def migrate_existing_projects(self) -> Dict[str, Any]:
        """
        Migrate existing projects from the default directory to the mapping system
        
        Returns:
            Migration report with details
        """
        logger.info("🔄 [PROJECT_DIR_MANAGER] Starting migration of existing projects...")
        
        try:
            migration_report = {
                "success": True,
                "projects_found": 0,
                "projects_migrated": 0,
                "projects_skipped": 0,
                "errors": []
            }
            
            # Load current mappings
            current_mappings = await self.load_mappings()
            
            # Scan default projects directory
            if not self.default_projects_root.exists():
                logger.info("📂 [PROJECT_DIR_MANAGER] No default projects directory found")
                return migration_report
            
            for project_dir in self.default_projects_root.iterdir():
                if not project_dir.is_dir():
                    continue
                
                project_name = project_dir.name
                migration_report["projects_found"] += 1
                
                # Skip if already mapped
                if project_name in current_mappings:
                    logger.info("⏭️ [PROJECT_DIR_MANAGER] Project already mapped, skipping", 
                              project_name=project_name)
                    migration_report["projects_skipped"] += 1
                    continue
                
                # Check if it's a valid DeployBot project
                config_file = project_dir / "config.json"
                todo_file = project_dir / "TODO.md"
                
                if not (config_file.exists() and todo_file.exists()):
                    logger.warning("⚠️ [PROJECT_DIR_MANAGER] Invalid project structure, skipping", 
                                 project_name=project_name)
                    migration_report["projects_skipped"] += 1
                    continue
                
                # Add to mappings (pointing to current location)
                success = await self.add_project_mapping(project_name, str(project_dir))
                
                if success:
                    migration_report["projects_migrated"] += 1
                    logger.info("✅ [PROJECT_DIR_MANAGER] Project migrated successfully", 
                               project_name=project_name)
                else:
                    migration_report["errors"].append(f"Failed to migrate {project_name}")
                    logger.error("❌ [PROJECT_DIR_MANAGER] Failed to migrate project", 
                               project_name=project_name)
            
            logger.info("🎉 [PROJECT_DIR_MANAGER] Migration completed", 
                       found=migration_report["projects_found"],
                       migrated=migration_report["projects_migrated"],
                       skipped=migration_report["projects_skipped"],
                       errors=len(migration_report["errors"]))
            
            return migration_report
            
        except Exception as e:
            logger.error("❌ [PROJECT_DIR_MANAGER] Migration failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "projects_found": 0,
                "projects_migrated": 0,
                "projects_skipped": 0,
                "errors": [str(e)]
            }

# Global instance for use throughout the application
project_directory_manager = ProjectDirectoryManager() 