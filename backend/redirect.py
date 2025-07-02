#!/usr/bin/env python3
"""
Enhanced App Redirection for DeployBot

This module handles:
- Intelligent app opening with context preservation
- Deep linking support for compatible applications
- URL-based redirection for web services
- Task-specific content creation in target apps
- Cross-platform compatibility (macOS focus)
"""

import asyncio
import json
import os
import subprocess
import urllib.parse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import structlog

# Check if debug mode is enabled
DEBUG_MODE = os.getenv('DEPLOYBOT_DEBUG', '0') == '1'

logger = structlog.get_logger()

class AppRedirector:
    """Enhanced application redirection system for DeployBot"""
    
    def __init__(self):
        # App-specific redirection configurations
        self.app_configs = {
            "Bear": {
                "bundle_id": "net.shinyfrog.bear",
                "supports_deep_linking": True,
                "url_scheme": "bear://",
                "task_actions": {
                    "create_note": "bear://x-callback-url/create?title={title}&text={content}",
                    "search": "bear://x-callback-url/search?term={term}",
                    "open_tag": "bear://x-callback-url/open-tag?name={tag}"
                }
            },
            "Notion": {
                "bundle_id": "notion.id",
                "supports_deep_linking": True,
                "url_scheme": "notion://",
                "task_actions": {
                    "open_workspace": "notion://notion.so/",
                    "search": "notion://notion.so/search?query={query}",
                    "new_page": "notion://notion.so/new"
                }
            },
            "VSCode": {
                "bundle_id": "com.microsoft.VSCode",
                "supports_deep_linking": True,
                "command_line": "code",
                "task_actions": {
                    "open_project": "code {project_path}",
                    "open_file": "code {file_path}:{line}",
                    "search": "code --goto {project_path} --search {term}"
                }
            },
            "Figma": {
                "bundle_id": "com.figma.Desktop",
                "supports_deep_linking": False,
                "url_scheme": "figma://",
                "web_fallback": "https://figma.com"
            },
            "Safari": {
                "bundle_id": "com.apple.Safari",
                "supports_deep_linking": True,
                "task_actions": {
                    "search": "https://www.google.com/search?q={query}",
                    "open_url": "{url}"
                }
            },
            "Terminal": {
                "bundle_id": "com.apple.Terminal",
                "supports_deep_linking": False,
                "task_actions": {
                    "open_project": "cd {project_path}",
                    "run_command": "{command}"
                }
            },
            "Mail": {
                "bundle_id": "com.apple.mail",
                "supports_deep_linking": True,
                "url_scheme": "mailto:",
                "task_actions": {
                    "compose": "mailto:?subject={subject}&body={body}",
                    "search": "message://search?query={query}"
                }
            },
            "Things": {
                "bundle_id": "com.culturedcode.ThingsMac",
                "supports_deep_linking": True,
                "url_scheme": "things://",
                "task_actions": {
                    "add_todo": "things:///add?title={title}&notes={notes}&tags={tags}",
                    "show_today": "things:///show?id=today",
                    "search": "things:///search?query={query}"
                }
            },
            "Zoom": {
                "bundle_id": "us.zoom.xos",
                "supports_deep_linking": True,
                "url_scheme": "zoommtg://",
                "task_actions": {
                    "join_meeting": "zoommtg://zoom.us/join?confno={meeting_id}",
                    "schedule_meeting": "zoomus://meeting/schedule"
                }
            }
        }
        
        # Default fallback applications
        self.fallback_apps = {
            "text_editor": "TextEdit",
            "web_browser": "Safari",
            "terminal": "Terminal",
            "notes": "Notes"
        }
        
        logger.info("🔀 [REDIRECT] AppRedirector initialized", 
                   supported_apps=len(self.app_configs),
                   debug_mode=DEBUG_MODE)

    async def redirect_to_task(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Redirect user to the appropriate app for the given task with full context
        
        Args:
            task: Task object with text, tags, app, etc.
            context: Additional context (project_path, deploy_info, etc.)
            
        Returns:
            Dict with success status, app opened, and any relevant info
        """
        logger.info("🔀 [REDIRECT] Starting task redirection", 
                   task_text=task.get('text', ''),
                   target_app=task.get('app', 'Unknown'))
        
        try:
            app_name = task.get('app', 'Notion')
            task_text = task.get('text', '')
            tags = task.get('tags', [])
            
            # Prepare task context for redirection
            task_context = self._prepare_task_context(task, context or {})
            
            # Check if app supports enhanced redirection
            if app_name in self.app_configs:
                result = await self._redirect_with_context(app_name, task, task_context)
            else:
                # Fallback to simple app opening
                result = await self._simple_app_redirect(app_name, task_text)
            
            # Log the redirection result
            if result.get('success'):
                logger.info("✅ [REDIRECT] Task redirection successful", 
                           app=app_name, 
                           method=result.get('method', 'unknown'),
                           task=task_text)
            else:
                logger.error("❌ [REDIRECT] Task redirection failed", 
                           app=app_name, 
                           error=result.get('error', 'Unknown error'),
                           task=task_text)
            
            return result
            
        except Exception as e:
            logger.error("❌ [REDIRECT] Unexpected error during redirection", 
                        error=str(e), task=task.get('text', ''))
            return {
                "success": False,
                "error": str(e),
                "method": "error"
            }

    def _prepare_task_context(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare comprehensive context for task redirection"""
        
        task_context = {
            "task_title": task.get('text', ''),
            "original_text": task.get('original_text', ''),
            "tags": task.get('tags', []),
            "estimated_duration": task.get('estimated_duration', 45),
            "priority": task.get('priority', 5),
            "project_name": context.get('project_name', ''),
            "project_path": context.get('project_path', ''),
            "deploy_command": context.get('deploy_command', ''),
            "timer_duration": context.get('timer_duration', 1800),
            "timestamp": datetime.now().isoformat(),
            "redirect_reason": "deploy_detected"
        }
        
        # Add specific context based on task tags
        if '#writing' in task_context['tags']:
            task_context['content_type'] = 'writing'
            task_context['suggested_content'] = self._generate_writing_starter(task)
        elif '#code' in task_context['tags']:
            task_context['content_type'] = 'development'
            task_context['file_suggestions'] = self._suggest_code_files(task, context)
        elif '#research' in task_context['tags']:
            task_context['content_type'] = 'research'
            task_context['search_queries'] = self._generate_search_queries(task)
        elif '#creative' in task_context['tags']:
            task_context['content_type'] = 'creative'
            task_context['creative_prompts'] = self._generate_creative_prompts(task)
        
        return task_context

    async def _redirect_with_context(self, app_name: str, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced redirection with app-specific context and deep linking"""
        
        app_config = self.app_configs[app_name]
        logger.debug("🔀 [REDIRECT] Using enhanced redirection", 
                    app=app_name, 
                    supports_deep_linking=app_config.get('supports_deep_linking', False))
        
        # Try deep linking first if supported
        if app_config.get('supports_deep_linking', False):
            deep_link_result = await self._try_deep_linking(app_name, task, context, app_config)
            if deep_link_result.get('success'):
                return deep_link_result
        
        # Try command line integration
        if app_config.get('command_line'):
            cli_result = await self._try_command_line(app_name, task, context, app_config)
            if cli_result.get('success'):
                return cli_result
        
        # Fallback to simple app opening
        logger.debug("🔀 [REDIRECT] Falling back to simple app opening", app=app_name)
        return await self._simple_app_redirect(app_name, task.get('text', ''))

    async def _try_deep_linking(self, app_name: str, task: Dict[str, Any], context: Dict[str, Any], 
                               app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to use deep linking for enhanced app integration"""
        
        try:
            task_actions = app_config.get('task_actions', {})
            task_text = task.get('text', '')
            tags = task.get('tags', [])
            
            # Determine the best action based on task type
            action_url = None
            action_type = None
            
            if app_name == "Bear":
                # Create a new note in Bear (works for any Bear task, not just writing)
                # Create a new note in Bear with task context
                note_content = self._generate_bear_note_content(task, context)
                logger.debug("🐻 [REDIRECT] Generated Bear note content", 
                           content_length=len(note_content), 
                           content_preview=note_content[:100])
                
                # Try full content first
                action_url = task_actions['create_note'].format(
                    title=urllib.parse.quote(task_text),
                    content=urllib.parse.quote(note_content)
                )
                
                # If URL is too long, use simplified content
                if len(action_url) > 2000:
                    logger.warning("🐻 [REDIRECT] URL too long, using simplified content", 
                                 original_length=len(action_url))
                    simplified_content = self._generate_simplified_bear_content(task, context)
                    action_url = task_actions['create_note'].format(
                        title=urllib.parse.quote(task_text),
                        content=urllib.parse.quote(simplified_content)
                    )
                    logger.debug("🐻 [REDIRECT] Simplified Bear URL created", 
                               url_length=len(action_url))
                
                action_type = "create_note"
                
                logger.debug("🐻 [REDIRECT] Final Bear URL created", 
                           url_length=len(action_url),
                           url_preview=action_url[:150])
                
            elif app_name == "VSCode" and context.get('project_path'):
                # Open VSCode with project context
                project_path = context['project_path']
                action_url = f"code {project_path}"
                action_type = "open_project"
                
            elif app_name == "Safari" and '#research' in tags:
                # Open Safari with relevant search
                search_query = self._extract_search_query(task_text)
                action_url = task_actions['search'].format(query=urllib.parse.quote(search_query))
                action_type = "search"
                
            elif app_name == "Things":
                # Add task to Things with proper formatting
                tags_str = ','.join([tag.replace('#', '') for tag in tags])
                action_url = task_actions['add_todo'].format(
                    title=urllib.parse.quote(task_text),
                    notes=urllib.parse.quote(f"Created by DeployBot during deploy"),
                    tags=urllib.parse.quote(tags_str)
                )
                action_type = "add_todo"
                
            elif app_name == "Notion":
                # Open Notion workspace
                action_url = task_actions['open_workspace']
                action_type = "open_workspace"
            
            if action_url:
                logger.info("🔗 [REDIRECT] Attempting deep link", 
                           app=app_name, action=action_type, url_length=len(action_url))
                logger.debug("🔗 [REDIRECT] Full URL for debugging", url=action_url)
                
                # Execute the deep link
                if action_url.startswith('http'):
                    # Web URL
                    logger.debug("🌐 [REDIRECT] Opening web URL")
                    result = await self._open_url(action_url)
                elif action_url.startswith(('code ', 'open ')):
                    # Command line
                    logger.debug("🖥️ [REDIRECT] Executing command line")
                    result = await self._execute_command(action_url)
                else:
                    # App URL scheme
                    logger.debug("📱 [REDIRECT] Opening app URL scheme")
                    result = await self._open_url_scheme(action_url)
                
                logger.info("🔗 [REDIRECT] Deep link execution result", 
                           app=app_name, action=action_type, success=result)
                
                if result:
                    return {
                        "success": True,
                        "method": "deep_linking",
                        "action": action_type,
                        "app": app_name,
                        "url": action_url[:100] + "..." if len(action_url) > 100 else action_url
                    }
            else:
                logger.warning("🔗 [REDIRECT] No action URL generated", 
                             app=app_name, tags=tags, task_text=task_text[:50])
            
        except Exception as e:
            logger.error("❌ [REDIRECT] Deep linking failed with exception", 
                        app=app_name, error=str(e), error_type=type(e).__name__)
        
        return {"success": False, "method": "deep_linking"}

    async def _try_command_line(self, app_name: str, task: Dict[str, Any], context: Dict[str, Any], 
                               app_config: Dict[str, Any]) -> Dict[str, Any]:
        """Try command line integration for supported apps"""
        
        try:
            command_line = app_config.get('command_line')
            if not command_line:
                return {"success": False, "method": "command_line"}
            
            # Build command based on app and context
            if app_name == "VSCode" and context.get('project_path'):
                command = f"{command_line} {context['project_path']}"
                
                # If it's a code task, try to open specific files
                if '#code' in task.get('tags', []):
                    # Look for relevant files in project
                    relevant_files = self._find_relevant_files(task, context)
                    if relevant_files:
                        command += f" {relevant_files[0]}"
                
                logger.debug("🖥️ [REDIRECT] Executing command", command=command)
                result = await self._execute_command(command)
                
                if result:
                    return {
                        "success": True,
                        "method": "command_line",
                        "command": command,
                        "app": app_name
                    }
                    
        except Exception as e:
            logger.warning("⚠️ [REDIRECT] Command line execution failed", 
                          app=app_name, error=str(e))
        
        return {"success": False, "method": "command_line"}

    async def _simple_app_redirect(self, app_name: str, task_text: str) -> Dict[str, Any]:
        """Simple app opening fallback using macOS open command"""
        
        try:
            logger.debug("📱 [REDIRECT] Using simple app redirect", app=app_name)
            
            # Use macOS open command
            command = ['open', '-a', app_name]
            result = await self._execute_subprocess(command)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "method": "simple_open",
                    "app": app_name,
                    "command": ' '.join(command)
                }
            else:
                return {
                    "success": False,
                    "method": "simple_open",
                    "error": result.stderr,
                    "app": app_name
                }
                
        except Exception as e:
            logger.error("❌ [REDIRECT] Simple app redirect failed", 
                        app=app_name, error=str(e))
            return {
                "success": False,
                "method": "simple_open",
                "error": str(e),
                "app": app_name
            }

    async def _execute_subprocess(self, command: List[str], timeout: int = 10) -> subprocess.CompletedProcess:
        """Execute subprocess command with timeout and enhanced debugging"""
        
        if DEBUG_MODE:
            logger.debug("🖥️ [REDIRECT] Executing subprocess command", 
                       command=command, timeout=timeout, cwd=os.getcwd())
        
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=None,  # Use current working directory
                    env=None   # Inherit environment
                )
            )
            
            if DEBUG_MODE:
                logger.debug("🖥️ [REDIRECT] Subprocess result", 
                           return_code=result.returncode,
                           stdout_length=len(result.stdout) if result.stdout else 0,
                           stderr_length=len(result.stderr) if result.stderr else 0,
                           stdout_preview=result.stdout[:100] if result.stdout else None,
                           stderr_preview=result.stderr[:100] if result.stderr else None)
            
            return result
            
        except subprocess.TimeoutExpired as e:
            logger.error("⏰ [REDIRECT] Subprocess timeout", 
                       command=command, timeout=timeout)
            raise
        except Exception as e:
            logger.error("❌ [REDIRECT] Subprocess execution error", 
                       command=command, error=str(e), error_type=type(e).__name__)
            raise

    async def _execute_command(self, command: str, timeout: int = 10) -> bool:
        """Execute shell command"""
        
        try:
            result = await self._execute_subprocess(command.split(), timeout)
            return result.returncode == 0
        except Exception as e:
            logger.error("❌ [REDIRECT] Command execution failed", command=command, error=str(e))
            return False

    async def _open_url(self, url: str) -> bool:
        """Open URL in default browser"""
        
        try:
            command = ['open', url]
            result = await self._execute_subprocess(command)
            return result.returncode == 0
        except Exception as e:
            logger.error("❌ [REDIRECT] URL opening failed", url=url, error=str(e))
            return False

    async def _open_url_scheme(self, url_scheme: str) -> bool:
        """Open app using URL scheme"""
        
        try:
            logger.debug("📱 [REDIRECT] Executing URL scheme", 
                        url_length=len(url_scheme), 
                        scheme=url_scheme.split('://')[0] if '://' in url_scheme else 'unknown')
            
            command = ['open', url_scheme]
            result = await self._execute_subprocess(command)
            
            logger.debug("📱 [REDIRECT] URL scheme execution result", 
                        return_code=result.returncode,
                        stdout=result.stdout.strip() if result.stdout else None,
                        stderr=result.stderr.strip() if result.stderr else None)
            
            success = result.returncode == 0
            
            if not success:
                logger.error("❌ [REDIRECT] URL scheme failed", 
                           return_code=result.returncode,
                           stderr=result.stderr,
                           command=' '.join(command))
                           
            return success
            
        except Exception as e:
            logger.error("❌ [REDIRECT] URL scheme opening failed with exception", 
                        url_scheme=url_scheme[:100], error=str(e), error_type=type(e).__name__)
            return False

    def _generate_bear_note_content(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate formatted content for Bear note"""
        
        content_lines = [
            f"# {task.get('text', 'Task from DeployBot')}",
            "",
            f"**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Source:** DeployBot (during deployment)",
            ""
        ]
        
        if context.get('project_name'):
            content_lines.append(f"**Project:** {context['project_name']}")
        
        if context.get('deploy_command'):
            content_lines.append(f"**Deploy Command:** `{context['deploy_command']}`")
        
        if task.get('tags'):
            tags_str = ' '.join(task['tags'])
            content_lines.append(f"**Tags:** {tags_str}")
        
        content_lines.extend([
            "",
            "## Notes",
            "",
            "Start working on this task...",
            "",
            "## Progress",
            "",
            "- [ ] Task started",
            "- [ ] In progress",
            "- [ ] Completed"
        ])
        
        return '\n'.join(content_lines)

    def _generate_simplified_bear_content(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate simplified Bear note content for URL scheme limits"""
        
        content_lines = [
            f"# {task.get('text', 'Task from DeployBot')}",
            "",
            f"Created by DeployBot on {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            ""
        ]
        
        if context.get('project_name'):
            content_lines.append(f"Project: {context['project_name']}")
        
        if task.get('tags'):
            content_lines.append(f"Tags: {' '.join(task['tags'])}")
        
        content_lines.extend([
            "",
            "## Notes",
            "",
            "Start working on this task..."
        ])
        
        return '\n'.join(content_lines)

    def _generate_writing_starter(self, task: Dict[str, Any]) -> str:
        """Generate writing starter content based on task"""
        
        task_text = task.get('text', '')
        
        # Common writing starters based on task content
        if 'blog' in task_text.lower():
            return "# Blog Post: [Title]\n\n## Introduction\n\n## Main Content\n\n## Conclusion\n"
        elif 'email' in task_text.lower():
            return "Subject: \n\nHi [Name],\n\n\n\nBest regards,\n[Your name]"
        elif 'documentation' in task_text.lower() or 'docs' in task_text.lower():
            return "# Documentation\n\n## Overview\n\n## Prerequisites\n\n## Instructions\n\n"
        else:
            return f"# {task_text}\n\n## Outline\n\n- \n- \n- \n\n## Content\n\n"

    def _suggest_code_files(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Suggest relevant code files based on task and project context"""
        
        suggestions = []
        project_path = context.get('project_path', '')
        
        if project_path:
            project_dir = Path(project_path)
            task_lower = task.get('text', '').lower()
            
            # Common file patterns based on task content
            patterns = []
            if 'component' in task_lower or 'ui' in task_lower:
                patterns.extend(['*.jsx', '*.tsx', '*.vue', '*.svelte'])
            elif 'api' in task_lower or 'backend' in task_lower:
                patterns.extend(['*.py', '*.js', '*.ts', '*.go', '*.rs'])
            elif 'style' in task_lower or 'css' in task_lower:
                patterns.extend(['*.css', '*.scss', '*.sass', '*.less'])
            elif 'test' in task_lower:
                patterns.extend(['*test*', '*spec*'])
            
            # Find matching files
            for pattern in patterns:
                try:
                    matches = list(project_dir.glob(f"**/{pattern}"))
                    suggestions.extend([str(f) for f in matches[:3]])  # Limit to 3 files
                except:
                    pass
        
        return suggestions

    def _generate_search_queries(self, task: Dict[str, Any]) -> List[str]:
        """Generate relevant search queries for research tasks"""
        
        task_text = task.get('text', '')
        queries = []
        
        # Extract key terms from task text
        words = task_text.lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why'}
        key_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        if key_words:
            # Primary search with all key terms
            queries.append(' '.join(key_words[:4]))  # Limit to 4 words
            
            # Secondary searches with combinations
            if len(key_words) > 2:
                queries.append(' '.join(key_words[:2]) + ' tutorial')
                queries.append(' '.join(key_words[:2]) + ' best practices')
        
        return queries[:3]  # Return max 3 queries

    def _generate_creative_prompts(self, task: Dict[str, Any]) -> List[str]:
        """Generate creative prompts based on the task"""
        
        task_text = task.get('text', '')
        prompts = []
        
        if 'design' in task_text.lower():
            prompts.extend([
                "What's the primary user goal?",
                "What emotions should this evoke?",
                "What are 3 different approaches?"
            ])
        elif 'write' in task_text.lower():
            prompts.extend([
                "Who is the target audience?",
                "What's the key message?",
                "What tone should you use?"
            ])
        else:
            prompts.extend([
                "What's the creative challenge here?",
                "How can you approach this differently?",
                "What would make this stand out?"
            ])
        
        return prompts

    def _extract_search_query(self, task_text: str) -> str:
        """Extract a good search query from task text"""
        
        # Remove task-specific words
        clean_text = task_text.lower()
        remove_words = ['research', 'investigate', 'look up', 'find out', 'study']
        
        for word in remove_words:
            clean_text = clean_text.replace(word, '')
        
        # Clean up and return
        return clean_text.strip()

    def _find_relevant_files(self, task: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """Find relevant files in project for code tasks"""
        
        project_path = context.get('project_path', '')
        if not project_path:
            return []
        
        # This is a simplified version - in practice, you'd use more sophisticated matching
        relevant_files = []
        task_lower = task.get('text', '').lower()
        
        try:
            project_dir = Path(project_path)
            
            # Look for files mentioned in task or related patterns
            if 'readme' in task_lower:
                readme_files = list(project_dir.glob('**/README*'))
                relevant_files.extend([str(f) for f in readme_files])
            
            if 'package' in task_lower:
                package_files = list(project_dir.glob('**/package.json'))
                relevant_files.extend([str(f) for f in package_files])
                
        except Exception as e:
            logger.debug("🔍 [REDIRECT] Error finding relevant files", error=str(e))
        
        return relevant_files[:5]  # Limit to 5 files

    async def get_app_availability(self) -> Dict[str, bool]:
        """Check which configured apps are available on the system"""
        
        availability = {}
        
        for app_name, config in self.app_configs.items():
            try:
                # Try to check if app is installed
                command = ['open', '-a', app_name]
                result = await self._execute_subprocess(command + ['--args', '--version'], timeout=5)
                availability[app_name] = result.returncode == 0
            except:
                availability[app_name] = False
        
        logger.info("📱 [REDIRECT] App availability check completed", 
                   available_apps=[app for app, available in availability.items() if available])
        
        return availability

    async def test_redirection(self, app_name: str, task_text: str = "Test task") -> Dict[str, Any]:
        """Test redirection for a specific app (useful for debugging)"""
        
        test_task = {
            "text": task_text,
            "app": app_name,
            "tags": ["#test"],
            "priority": 5
        }
        
        test_context = {
            "project_name": "TestProject",
            "deploy_command": "test deploy",
            "timer_duration": 1800
        }
        
        logger.info("🧪 [REDIRECT] Testing redirection", app=app_name, task=task_text)
        result = await self.redirect_to_task(test_task, test_context)
        
        return result

# Global instance
app_redirector = AppRedirector() 