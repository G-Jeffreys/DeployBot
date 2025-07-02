#!/usr/bin/env python3
"""
Project Management Backend for DeployBot

This module handles real project management operations including creating,
deleting, listing, and loading project data from the filesystem.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger()

class ProjectManager:
    """Manages DeployBot projects on the filesystem"""
    
    def __init__(self, projects_root: Optional[str] = None):
        if projects_root:
            self.projects_root = Path(projects_root).resolve()
        else:
            # Default to projects/ directory relative to the langgraph folder
            self.projects_root = Path(__file__).parent.parent / "projects"
        
        # Ensure projects directory exists
        self.projects_root.mkdir(exist_ok=True)
        
        logger.info("📁 [PROJECT_MANAGER] ProjectManager initialized", 
                   projects_root=str(self.projects_root))

    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new DeployBot project with directory structure"""
        project_name = project_data.get("name", "").strip()
        
        if not project_name:
            return {
                "success": False,
                "error": "Project name is required",
                "message": "Please provide a valid project name"
            }
        
        logger.info("📁 [PROJECT_MANAGER] Creating new project", project_name=project_name)
        
        try:
            # Sanitize project name for filesystem
            safe_project_name = self._sanitize_project_name(project_name)
            project_path = self.projects_root / safe_project_name
            
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
            
            logger.info("✅ [PROJECT_MANAGER] Project created successfully", 
                       project_name=project_name, project_path=str(project_path))
            
            return {
                "success": True,
                "message": f"Project '{project_name}' created successfully",
                "project": {
                    "name": project_name,
                    "path": str(project_path),
                    "config": config,
                    "created_at": config["createdAt"]
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
        """Delete a project and all its data"""
        logger.info("🗑️ [PROJECT_MANAGER] Deleting project", project_path=project_path)
        
        try:
            path_obj = Path(project_path).resolve()
            
            # Verify it's under our projects root for safety
            if not str(path_obj).startswith(str(self.projects_root)):
                return {
                    "success": False,
                    "error": "Invalid project path",
                    "message": "Project path is not under the projects directory"
                }
            
            if not path_obj.exists():
                return {
                    "success": False,
                    "error": "Project not found",
                    "message": f"Project at path '{project_path}' does not exist"
                }
            
            # Load project name from config for logging
            project_name = path_obj.name
            config_file = path_obj / "config.json"
            if config_file.exists():
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                        project_name = config.get("projectName", project_name)
                except:
                    pass  # Use directory name as fallback
            
            # Remove the entire project directory
            shutil.rmtree(path_obj)
            
            logger.info("✅ [PROJECT_MANAGER] Project deleted successfully", 
                       project_name=project_name, project_path=project_path)
            
            return {
                "success": True,
                "message": f"Project '{project_name}' deleted successfully",
                "deleted_path": project_path
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
        """List all available projects"""
        logger.info("📋 [PROJECT_MANAGER] Listing all projects...")
        
        try:
            projects = []
            
            # Scan projects directory
            for project_dir in self.projects_root.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # Check if it's a valid DeployBot project
                config_file = project_dir / "config.json"
                todo_file = project_dir / "TODO.md"
                
                if not config_file.exists() or not todo_file.exists():
                    logger.warning("⚠️ [PROJECT_MANAGER] Skipping invalid project directory", 
                                 directory=str(project_dir))
                    continue
                
                try:
                    # Load project metadata
                    project_info = await self._load_project_info(project_dir)
                    if project_info:
                        projects.append(project_info)
                except Exception as e:
                    logger.warning("⚠️ [PROJECT_MANAGER] Error loading project info", 
                                 project_dir=str(project_dir), error=str(e))
                    continue
            
            # Sort projects by last modified time (most recent first)
            projects.sort(key=lambda x: x.get("lastModified", ""), reverse=True)
            
            logger.info("✅ [PROJECT_MANAGER] Projects listed successfully", 
                       project_count=len(projects))
            
            return {
                "success": True,
                "projects": projects,
                "total_count": len(projects),
                "projects_root": str(self.projects_root)
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
        """Load complete project data including config, tasks, and logs"""
        logger.info("📖 [PROJECT_MANAGER] Loading project data", project_path=project_path)
        
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

# Global instance
project_manager = ProjectManager() 