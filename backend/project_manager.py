#!/usr/bin/env python3
"""
Project Management Backend for DeployBot

This module handles real project management operations including creating,
deleting, listing, and loading project data from the filesystem.

ENHANCED FOR PHASE 1: Now supports custom project directories through the
ProjectDirectoryManager system, allowing projects to be stored anywhere
on the filesystem rather than being restricted to DeployBot/projects.
"""

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

# Import the new project directory management system
from project_directory_manager import project_directory_manager

logger = structlog.get_logger()

class ProjectManager:
    """
    Manages DeployBot projects on the filesystem
    
    PHASE 1 ENHANCED: Now supports custom project directories through the
    ProjectDirectoryManager system for flexible project location management.
    """
    
    def __init__(self, projects_root: Optional[str] = None):
        """
        Initialize the ProjectManager with enhanced custom directory support
        
        Args:
            projects_root: Optional default projects root (for backward compatibility)
        """
        if projects_root:
            self.projects_root = Path(projects_root).resolve()
        else:
            # Default to projects/ directory relative to the langgraph folder
            self.projects_root = Path(__file__).parent.parent / "projects"
        
        # Ensure default projects directory exists for backward compatibility
        self.projects_root.mkdir(exist_ok=True)
        
        # Store reference to the project directory manager
        self.directory_manager = project_directory_manager
        
        logger.info("📁 [PROJECT_MANAGER] ProjectManager initialized with custom directory support", 
                   default_projects_root=str(self.projects_root),
                   uses_custom_directories=True,
                   directory_manager_available=self.directory_manager is not None)

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new DeployBot project with directory structure
        
        PHASE 1 ENHANCED: Now supports custom project directories
        
        Args:
            project_data: Project configuration including:
                - name: Project name (required)
                - custom_directory: Optional custom directory path
                - All other standard project settings
        
        Returns:
            Result dictionary with success status and project details
        """
        project_name = project_data.get("name", "").strip()
        custom_directory = project_data.get("custom_directory", "").strip()
        
        if not project_name:
            return {
                "success": False,
                "error": "Project name is required",
                "message": "Please provide a valid project name"
            }
        
        logger.info("📁 [PROJECT_MANAGER] Creating new project with custom directory support", 
                   project_name=project_name, 
                   has_custom_directory=bool(custom_directory),
                   custom_directory=custom_directory or "default")
        
        try:
            # Sanitize project name for filesystem
            safe_project_name = self._sanitize_project_name(project_name)
            
            # Determine project path based on custom directory preference
            if custom_directory:
                # Validate and use custom directory
                validation_result = await self.directory_manager.validate_project_directory(custom_directory)
                
                if not validation_result["valid"]:
                    logger.error("❌ [PROJECT_MANAGER] Custom directory validation failed", 
                               custom_directory=custom_directory, 
                               issues=validation_result.get("issues", []))
                    return {
                        "success": False,
                        "error": "Invalid custom directory",
                        "message": f"Custom directory validation failed: {'; '.join(validation_result.get('issues', ['Unknown error']))}",
                        "validation_details": validation_result
                    }
                
                # Use custom directory with project name as subdirectory
                custom_path = Path(custom_directory).resolve()
                project_path = custom_path / safe_project_name
                
                logger.info("📂 [PROJECT_MANAGER] Using custom directory", 
                           custom_directory=str(custom_path),
                           project_path=str(project_path))
            else:
                # Use default projects directory
                project_path = self.projects_root / safe_project_name
                
                logger.info("📂 [PROJECT_MANAGER] Using default directory", 
                           project_path=str(project_path))
            
            # Check if project already exists
            if project_path.exists():
                return {
                    "success": False,
                    "error": "Project already exists",
                    "message": f"A project named '{project_name}' already exists"
                }
            
            # Create project directory structure
            project_path.mkdir(parents=True)
            (project_path / "logs").mkdir()
            
            # Create default config.json
            config = self._create_default_config(project_name, project_data)
            config_file = project_path / "config.json"
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create default TODO.md
            todo_content = self._create_default_todo(project_name)
            todo_file = project_path / "TODO.md"
            todo_file.write_text(todo_content)
            
            # Create initial activity log
            activity_log = project_path / "logs" / "activity.log"
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            with open(activity_log, 'w') as f:
                f.write(f"{timestamp} PROJECT CREATED: {project_name} initialized\n")
                f.write(f"{timestamp} CONFIG CREATED: Default configuration generated\n")
                f.write(f"{timestamp} TODO CREATED: Default task list created\n")
            
            # Create empty deploy log
            deploy_log = project_path / "logs" / "deploy_log.txt"
            deploy_log.touch()
            
            # Register the project in the directory mapping system
            mapping_success = await self.directory_manager.add_project_mapping(project_name, str(project_path))
            
            if not mapping_success:
                logger.warning("⚠️ [PROJECT_MANAGER] Failed to register project mapping", 
                             project_name=project_name, project_path=str(project_path))
            
            logger.info("✅ [PROJECT_MANAGER] Project created successfully", 
                       project_name=project_name, 
                       project_path=str(project_path),
                       uses_custom_directory=bool(custom_directory),
                       mapping_registered=mapping_success)
            
            return {
                "success": True,
                "message": f"Project '{project_name}' created successfully",
                "project": {
                    "name": project_name,
                    "path": str(project_path),
                    "config": config,
                    "created_at": config["createdAt"],
                    "uses_custom_directory": bool(custom_directory),
                    "custom_directory": custom_directory if custom_directory else None
                }
            }
            
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to create project", 
                        project_name=project_name, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to create project: {str(e)}"
            }

    async def delete_project(self, project_path: str) -> Dict[str, Any]:
        """
        Delete a project and all its data
        
        PHASE 1 ENHANCED: Now handles projects in custom directories and
        cleans up project directory mappings
        """
        logger.info("🗑️ [PROJECT_MANAGER] Deleting project with custom directory support", 
                   project_path=project_path)
        
        try:
            path_obj = Path(project_path).resolve()
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": "Project not found",
                    "message": f"Project at path '{project_path}' does not exist"
                }
            
            # Load project name from config for logging and mapping cleanup
            project_name = path_obj.name
            config_file = path_obj / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        project_name = config.get("projectName", project_name)
                except:
                    pass  # Use directory name as fallback
            
            # Enhanced safety check: Allow deletion of projects in custom directories
            # Check if this is in the default projects directory OR a known custom mapping
            is_in_default_dir = str(path_obj).startswith(str(self.projects_root))
            is_custom_mapped = False
            
            # Check if this project is in our custom mappings
            try:
                mapped_path = await self.directory_manager.get_project_path(project_name)
                is_custom_mapped = mapped_path and Path(mapped_path).resolve() == path_obj
            except Exception as e:
                logger.debug("🔍 [PROJECT_MANAGER] Could not check custom mapping", error=str(e))
            
            if not is_in_default_dir and not is_custom_mapped:
                logger.warning("⚠️ [PROJECT_MANAGER] Project path is not in known locations", 
                             project_path=str(path_obj),
                             project_name=project_name,
                             in_default=is_in_default_dir,
                             in_custom_mapping=is_custom_mapped)
                # Allow deletion but warn
            
            logger.info("🗂️ [PROJECT_MANAGER] Project location analysis", 
                       project_name=project_name,
                       in_default_directory=is_in_default_dir,
                       in_custom_mapping=is_custom_mapped,
                       will_proceed=True)
            
            # Remove the entire project directory
            shutil.rmtree(path_obj)
            
            # Clean up the project mapping if it exists
            mapping_removed = await self.directory_manager.remove_project_mapping(project_name)
            
            logger.info("✅ [PROJECT_MANAGER] Project deleted successfully", 
                       project_name=project_name, 
                       project_path=project_path,
                       mapping_cleaned_up=mapping_removed)
            
            return {
                "success": True,
                "message": f"Project '{project_name}' deleted successfully",
                "deleted_path": project_path,
                "mapping_cleaned_up": mapping_removed
            }
            
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to delete project", 
                        project_path=project_path, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to delete project: {str(e)}"
            }

    async def list_projects(self) -> Dict[str, Any]:
        """
        List all available projects from both default and custom directories
        
        PHASE 1 ENHANCED: Now uses ProjectDirectoryManager to find projects
        in both default and custom locations
        """
        logger.info("📋 [PROJECT_MANAGER] Listing all projects from all locations...")
        
        try:
            projects = []
            default_count = 0
            custom_count = 0
            
            # Get all projects using the directory manager
            all_project_locations = await self.directory_manager.list_all_projects()
            
            logger.info("🔍 [PROJECT_MANAGER] Found project locations", 
                       total_locations=len(all_project_locations))
            
            # Process each project location
            for project_name, project_path in all_project_locations:
                project_dir = Path(project_path)
                
                # Check if it's a valid DeployBot project
                config_file = project_dir / "config.json"
                todo_file = project_dir / "TODO.md"
                
                if not config_file.exists() or not todo_file.exists():
                    logger.warning("⚠️ [PROJECT_MANAGER] Skipping invalid project directory", 
                                 project_name=project_name,
                                 directory=str(project_dir),
                                 has_config=config_file.exists(),
                                 has_todo=todo_file.exists())
                    continue
                
                try:
                    # Load project metadata
                    project_info = await self._load_project_info(project_dir)
                    if project_info:
                        # Add location metadata
                        is_in_default = str(project_dir).startswith(str(self.projects_root))
                        project_info["is_custom_directory"] = not is_in_default
                        project_info["location_type"] = "default" if is_in_default else "custom"
                        
                        if is_in_default:
                            default_count += 1
                        else:
                            custom_count += 1
                        
                        projects.append(project_info)
                        
                        logger.debug("📂 [PROJECT_MANAGER] Loaded project info", 
                                   project_name=project_name,
                                   location_type=project_info["location_type"],
                                   path=str(project_dir))
                        
                except Exception as e:
                    logger.warning("⚠️ [PROJECT_MANAGER] Error loading project info", 
                                 project_name=project_name,
                                 project_dir=str(project_dir), 
                                 error=str(e))
                    continue
            
            # Sort projects by last modified time (most recent first)
            projects.sort(key=lambda x: x.get("lastModified", ""), reverse=True)
            
            logger.info("✅ [PROJECT_MANAGER] Projects listed successfully", 
                       total_projects=len(projects),
                       from_default_directory=default_count,
                       from_custom_directories=custom_count)
            
            return {
                "success": True,
                "projects": projects,
                "total_count": len(projects),
                "default_projects_count": default_count,
                "custom_projects_count": custom_count,
                "default_projects_root": str(self.projects_root),
                "supports_custom_directories": True
            }
            
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to list projects", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to list projects: {str(e)}",
                "projects": []
            }

    async def load_project(self, project_path: str) -> Dict[str, Any]:
        """
        Load complete project data including config, tasks, and logs
        
        PHASE 1 ENHANCED: Supports loading projects from custom directories
        """
        logger.info("📖 [PROJECT_MANAGER] Loading project data with custom directory support", 
                   project_path=project_path)
        
        try:
            path_obj = Path(project_path).resolve()
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": "Project not found",
                    "message": f"Project at path '{project_path}' does not exist"
                }
            
            # Load configuration
            config_file = path_obj / "config.json"
            if not config_file.exists():
                return {
                    "success": False,
                    "error": "Invalid project",
                    "message": "Project config.json not found"
                }
            
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Load TODO.md tasks
            todo_file = path_obj / "TODO.md"
            tasks = []
            if todo_file.exists():
                tasks = await self._parse_todo_file(todo_file)
            
            # Load recent activity logs
            activity_log = path_obj / "logs" / "activity.log"
            recent_activities = []
            if activity_log.exists():
                recent_activities = await self._load_recent_activities(activity_log, limit=20)
            
            # Check deploy log status
            deploy_log = path_obj / "logs" / "deploy_log.txt"
            deploy_log_info = {
                "exists": deploy_log.exists(),
                "size": deploy_log.stat().st_size if deploy_log.exists() else 0,
                "last_modified": deploy_log.stat().st_mtime if deploy_log.exists() else None
            }
            
            project_data = {
                "name": config.get("projectName", path_obj.name),
                "path": str(path_obj),
                "config": config,
                "tasks": tasks,
                "recent_activities": recent_activities,
                "deploy_log_info": deploy_log_info,
                "loaded_at": datetime.now().isoformat()
            }
            
            logger.info("✅ [PROJECT_MANAGER] Project loaded successfully", 
                       project_name=project_data["name"],
                       task_count=len(tasks),
                       activity_count=len(recent_activities))
            
            return {
                "success": True,
                "project": project_data
            }
            
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to load project", 
                        project_path=project_path, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to load project: {str(e)}"
            }

    async def update_project_config(self, project_path: str, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update project configuration"""
        logger.info("🔧 [PROJECT_MANAGER] Updating project config", 
                   project_path=project_path)
        
        try:
            path_obj = Path(project_path).resolve()
            config_file = path_obj / "config.json"
            
            if not config_file.exists():
                return {
                    "success": False,
                    "error": "Project not found",
                    "message": "Project config.json not found"
                }
            
            # Load current config
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Update config with new values
            config.update(config_updates)
            config["lastModified"] = datetime.now().isoformat()
            
            # Save updated config
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Log the update
            await self._log_activity(path_obj, f"CONFIG UPDATED: Configuration modified")
            
            logger.info("✅ [PROJECT_MANAGER] Project config updated successfully")
            
            return {
                "success": True,
                "message": "Project configuration updated successfully",
                "config": config
            }
            
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to update project config", 
                        project_path=project_path, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to update project config: {str(e)}"
            }

    async def resolve_project_path(self, project_name: str) -> Optional[str]:
        """
        Resolve a project name to its directory path
        
        PHASE 1 NEW METHOD: Uses ProjectDirectoryManager to find projects
        in both default and custom locations
        
        Args:
            project_name: Name of the project to resolve
            
        Returns:
            Full path to the project directory, or None if not found
        """
        logger.debug("🔍 [PROJECT_MANAGER] Resolving project path", project_name=project_name)
        
        try:
            # Use the directory manager to find the project
            project_path = await self.directory_manager.get_project_path(project_name)
            
            if project_path:
                logger.debug("✅ [PROJECT_MANAGER] Project path resolved", 
                           project_name=project_name, path=project_path)
                return project_path
            else:
                logger.debug("❓ [PROJECT_MANAGER] Project not found", project_name=project_name)
                return None
                
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Error resolving project path", 
                        project_name=project_name, error=str(e))
            return None

    async def validate_custom_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Validate a custom directory for project creation
        
        PHASE 1 NEW METHOD: Provides validation for custom project directories
        
        Args:
            directory_path: Path to validate
            
        Returns:
            Validation result with details
        """
        logger.info("🔍 [PROJECT_MANAGER] Validating custom directory", 
                   directory_path=directory_path)
        
        return await self.directory_manager.validate_project_directory(directory_path)

    async def migrate_existing_projects(self) -> Dict[str, Any]:
        """
        Migrate existing projects to the new directory mapping system
        
        PHASE 1 NEW METHOD: Helps transition existing projects to the new system
        
        Returns:
            Migration report with details
        """
        logger.info("🔄 [PROJECT_MANAGER] Starting project migration...")
        
        return await self.directory_manager.migrate_existing_projects()

    async def _load_project_info(self, project_dir: Path) -> Optional[Dict[str, Any]]:
        """Load basic project information for listing"""
        try:
            config_file = project_dir / "config.json"
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Count tasks from TODO.md
            todo_file = project_dir / "TODO.md"
            task_count = 0
            completed_count = 0
            if todo_file.exists():
                content = todo_file.read_text()
                lines = content.split('\n')
                for line in lines:
                    if line.strip().startswith('- ['):
                        task_count += 1
                        if line.strip().startswith('- [x]'):
                            completed_count += 1
            
            # Get last activity
            activity_log = project_dir / "logs" / "activity.log"
            last_activity = None
            if activity_log.exists():
                try:
                    with open(activity_log, 'r') as f:
                        lines = f.readlines()
                        if lines:
                            last_activity = lines[-1].strip()
                except:
                    pass
            
            return {
                "name": config.get("projectName", project_dir.name),
                "path": str(project_dir),
                "description": config.get("description", ""),
                "createdAt": config.get("createdAt"),
                "lastModified": config.get("lastModified"),
                "backendServices": config.get("backendServices", []),
                "taskCount": task_count,
                "completedTasks": completed_count,
                "lastActivity": last_activity
            }
            
        except Exception as e:
            logger.warning("⚠️ [PROJECT_MANAGER] Error loading project info", 
                         project_dir=str(project_dir), error=str(e))
            return None

    async def _parse_todo_file(self, todo_file: Path) -> List[Dict[str, Any]]:
        """Parse TODO.md file and extract tasks with tags"""
        tasks = []
        
        try:
            content = todo_file.read_text()
            lines = content.split('\n')
            
            task_id = 1
            for line in lines:
                line = line.strip()
                
                # Look for task lines (- [ ] or - [x])
                if line.startswith('- ['):
                    completed = line.startswith('- [x]')
                    
                    # Extract task text (remove checkbox part)
                    if completed:
                        task_text = line[5:].strip()  # Remove "- [x] "
                    else:
                        task_text = line[5:].strip()  # Remove "- [ ] "
                    
                    # Extract hashtags
                    import re
                    tags = re.findall(r'#\w+', task_text)
                    
                    # Remove tags from task text for clean display
                    clean_text = re.sub(r'\s*#\w+', '', task_text).strip()
                    
                    # Determine app based on tags or use default mapping
                    app = self._determine_app_for_task(tags)
                    
                    tasks.append({
                        "id": task_id,
                        "text": clean_text,
                        "original_text": task_text,
                        "tags": tags,
                        "completed": completed,
                        "app": app
                    })
                    
                    task_id += 1
        
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to parse TODO file", 
                        todo_file=str(todo_file), error=str(e))
        
        return tasks

    def _determine_app_for_task(self, tags: List[str]) -> str:
        """Determine the appropriate app for a task based on its tags"""
        # Default tag-to-app mapping
        tag_app_mapping = {
            "writing": "Bear",
            "creative": "Figma", 
            "design": "Figma",
            "research": "Safari",
            "code": "VSCode",
            "backend": "Terminal",
            "business": "Notion"
        }
        
        # Check tags for app mapping
        for tag in tags:
            clean_tag = tag.replace('#', '').lower()
            if clean_tag in tag_app_mapping:
                return tag_app_mapping[clean_tag]
        
        # Default app
        return "Notion"

    async def _load_recent_activities(self, activity_log: Path, limit: int = 20) -> List[str]:
        """Load recent activity log entries"""
        activities = []
        
        try:
            with open(activity_log, 'r') as f:
                lines = f.readlines()
                # Get the last N lines
                recent_lines = lines[-limit:] if len(lines) > limit else lines
                activities = [line.strip() for line in recent_lines if line.strip()]
        
        except Exception as e:
            logger.error("❌ [PROJECT_MANAGER] Failed to load activity log", 
                        activity_log=str(activity_log), error=str(e))
        
        return activities

    async def _log_activity(self, project_path: Path, message: str):
        """Log an activity to the project's activity log"""
        try:
            activity_log = project_path / "logs" / "activity.log"
            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
            
            with open(activity_log, 'a') as f:
                f.write(f"{timestamp} {message}\n")
        
        except Exception as e:
            logger.warning("⚠️ [PROJECT_MANAGER] Failed to log activity", 
                         project_path=str(project_path), error=str(e))

    def _sanitize_project_name(self, name: str) -> str:
        """Sanitize project name for filesystem usage"""
        import re
        # Remove or replace invalid characters
        sanitized = re.sub(r'[^\w\-_\.]', '_', name)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized or "UnnamedProject"

    def _create_default_config(self, project_name: str, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create default project configuration"""
        now = datetime.now().isoformat()
        
        return {
            "projectName": project_name,
            "description": project_data.get("description", f"DeployBot project: {project_name}"),
            "version": "1.0.0",
            "createdAt": now,
            "lastModified": now,
            "backendServices": project_data.get("backendServices", []),
            "deployCommands": project_data.get("deployCommands", [
                "npm run deploy",
                "firebase deploy",
                "vercel --prod"
            ]),
            "settings": {
                "defaultTimer": project_data.get("defaultTimer", 1800),
                "graceperiod": 30,
                "autoRedirect": True,
                "excludeTags": ["#backend"],
                "preferredTags": ["#short", "#solo"]
            },
            "taskMappings": {
                "writing": "Bear",
                "creative": "Figma",
                "research": "Safari",
                "code": "VSCode",
                "design": "Figma",
                "business": "Notion"
            },
            "metadata": {
                "totalTasks": 0,
                "completedTasks": 0,
                "lastDeployDetected": None,
                "lastTaskSelected": None
            }
        }

    def _create_default_todo(self, project_name: str) -> str:
        """Create default TODO.md content"""
        return f"""# {project_name} Tasks

This is the task list for {project_name}. Tasks are tagged with hashtags to help DeployBot understand context and priority.

## Pending Tasks

- [ ] Set up project structure and initial configuration #code #short
- [ ] Write project documentation #writing #long #solo
- [ ] Design initial UI wireframes #creative #design #short
- [ ] Research competitor analysis #research #long #business
- [ ] Create deployment pipeline #code #backend #long
- [ ] Write user stories and requirements #writing #business #solo

## Completed Tasks

- [x] Initialize DeployBot project

## Task Tags Reference

### Duration Tags
- `#short` - Tasks that take 15-30 minutes
- `#long` - Tasks that take 1+ hours

### Type Tags
- `#writing` - Content creation, documentation
- `#code` - Programming, development tasks
- `#research` - Investigation, analysis
- `#creative` - Design, creative work
- `#backend` - Server-side, infrastructure (deprioritized during deploys)
- `#design` - UI/UX design work
- `#business` - Business strategy, planning

### Collaboration Tags
- `#solo` - Can be done independently
- `#collab` - Requires collaboration with others

## Notes

DeployBot will automatically suggest tasks from this list when backend deployments are detected. Tasks tagged with `#backend` will be deprioritized during deploy periods to avoid conflicts.
"""

# Global instance with enhanced custom directory support
# PHASE 1 ENHANCED: Uses intelligent project discovery with environment variable support
def _get_default_projects_directory():
    """
    Get the default projects directory with smart fallback logic
    
    This maintains backward compatibility while supporting the new custom directory system
    """
    # Check for environment variable first (highest priority)
    projects_root = os.environ.get('DEPLOYBOT_PROJECTS_ROOT')
    if projects_root and Path(projects_root).exists():
        logger.info("🌍 [PROJECT_MANAGER] Using environment variable DEPLOYBOT_PROJECTS_ROOT", 
                   path=projects_root)
        return projects_root
    
    current_dir = Path(__file__).parent
    
    # If we're in a temp directory, we need to find the real DeployBot directory
    if 'tmp' in str(current_dir) or 'temp' in str(current_dir):
        logger.info("🔍 [PROJECT_MANAGER] Detected temp directory, searching for real projects path")
        
        # Look for the projects directory in common locations
        possible_paths = [
            Path.home() / "Documents" / "DeployBot" / "projects",
            Path("/Users") / os.environ.get('USER', 'default') / "Documents" / "DeployBot" / "projects",
            Path.cwd() / "projects"  # If running from DeployBot directory
        ]
        
        for path in possible_paths:
            if path.exists():
                logger.info("✅ [PROJECT_MANAGER] Found real projects directory", path=str(path))
                return str(path)
        
        logger.warning("⚠️ [PROJECT_MANAGER] Could not find real projects directory, using fallback")
    
    # Final fallback to original logic
    fallback_path = str(current_dir.parent / "projects")
    logger.info("📂 [PROJECT_MANAGER] Using fallback projects directory", path=fallback_path)
    return fallback_path

# Initialize the global project manager with custom directory support
project_manager = ProjectManager(_get_default_projects_directory())

logger.info("🎉 [PROJECT_MANAGER] Global ProjectManager initialized with Phase 1 enhancements", 
           supports_custom_directories=True,
           directory_manager_available=hasattr(project_manager, 'directory_manager')) 