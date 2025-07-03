#!/usr/bin/env python3
"""
Activity Logger for DeployBot

This module handles logging significant events to per-project activity logs
and provides centralized logging functionality for the DeployBot system.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import structlog

logger = structlog.get_logger()

class ActivityLogger:
    """Manages activity logging for DeployBot projects"""
    
    def __init__(self):
        self.log_queue = asyncio.Queue(maxsize=100)
        self.queue_processor_task = None
        self.processing_active = False
        
        logger.info("📝 [ACTIVITY_LOGGER] ActivityLogger initialized with queue size limit")

    async def start_processing(self):
        """Start the log queue processing task"""
        if self.processing_active:
            logger.warning("⚠️ [ACTIVITY_LOGGER] Processing already active")
            return
        
        logger.info("🚀 [ACTIVITY_LOGGER] Starting activity log processing...")
        self.processing_active = True
        self.queue_processor_task = asyncio.create_task(self._process_log_queue())

    async def stop_processing(self):
        """Stop the log queue processing task"""
        if not self.processing_active:
            logger.warning("⚠️ [ACTIVITY_LOGGER] Processing not active")
            return
        
        logger.info("🛑 [ACTIVITY_LOGGER] Stopping activity log processing...")
        self.processing_active = False
        
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
            try:
                await self.queue_processor_task
            except asyncio.CancelledError:
                pass
            self.queue_processor_task = None

    async def log_deploy_detected(self, project_name: str, deploy_command: str, project_path: Optional[str] = None):
        """Log a deploy detection event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="DEPLOY_DETECTED",
            message=f"Deploy detected: {deploy_command}",
            details={
                "deploy_command": deploy_command,
                "event_category": "deployment"
            }
        )

    async def log_deploy_completed(self, project_name: str, deploy_command: str, 
                                 exit_code: int, project_path: Optional[str] = None):
        """Log a deploy completion event"""
        status = "SUCCESS" if exit_code == 0 else "FAILED"
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="DEPLOY_COMPLETED",
            message=f"Deploy {status.lower()}: {deploy_command} (exit code: {exit_code})",
            details={
                "deploy_command": deploy_command,
                "exit_code": exit_code,
                "status": status,
                "event_category": "deployment"
            }
        )

    async def log_timer_started(self, project_name: str, duration_seconds: int, 
                              deploy_command: Optional[str] = None, project_path: Optional[str] = None):
        """Log a timer start event"""
        duration_minutes = duration_seconds // 60
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="TIMER_STARTED",
            message=f"Deploy timer started: {duration_minutes} minutes",
            details={
                "duration_seconds": duration_seconds,
                "duration_minutes": duration_minutes,
                "deploy_command": deploy_command,
                "event_category": "timer"
            }
        )

    async def log_timer_expired(self, project_name: str, project_path: Optional[str] = None):
        """Log a timer expiration event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="TIMER_EXPIRED",
            message="Deploy timer expired - productivity period ended",
            details={
                "event_category": "timer"
            }
        )

    async def log_timer_stopped(self, project_name: str, reason: str = "manual", project_path: Optional[str] = None):
        """Log a timer stop event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="TIMER_STOPPED",
            message=f"Deploy timer stopped: {reason}",
            details={
                "stop_reason": reason,
                "event_category": "timer"
            }
        )

    async def log_task_selected(self, project_name: str, task_text: str, tags: Optional[List[str]] = None, 
                              app: Optional[str] = None, project_path: Optional[str] = None):
        """Log a task selection event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="TASK_SELECTED",
            message=f"Task selected: {task_text}",
            details={
                "task_text": task_text,
                "tags": tags or [],
                "target_app": app,
                "event_category": "task_management"
            }
        )

    async def log_app_opened(self, project_name: str, app_name: str, task_text: Optional[str] = None, 
                           project_path: Optional[str] = None):
        """Log an app opening event"""
        message = f"App opened: {app_name}"
        if task_text:
            message += f" for task: {task_text}"
        
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="APP_OPENED",
            message=message,
            details={
                "app_name": app_name,
                "task_text": task_text,
                "event_category": "redirection"
            }
        )

    async def log_project_created(self, project_name: str, project_path: str):
        """Log a project creation event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="PROJECT_CREATED",
            message=f"Project created: {project_name}",
            details={
                "project_path": project_path,
                "event_category": "project_management"
            }
        )

    async def log_project_deleted(self, project_name: str, project_path: Optional[str] = None):
        """Log a project deletion event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type="PROJECT_DELETED",
            message=f"Project deleted: {project_name}",
            details={
                "event_category": "project_management"
            }
        )

    async def log_wrapper_installed(self, success: bool, wrapper_path: Optional[str] = None):
        """Log deploy wrapper installation"""
        event_type = "WRAPPER_INSTALLED" if success else "WRAPPER_INSTALL_FAILED"
        message = "Deploy wrapper installed successfully" if success else "Deploy wrapper installation failed"
        
        await self._queue_log_entry(
            project_name="system",
            event_type=event_type,
            message=message,
            details={
                "wrapper_path": wrapper_path,
                "success": success,
                "event_category": "system"
            }
        )

    async def log_monitoring_started(self, project_name: Optional[str] = None):
        """Log monitoring start event"""
        await self._queue_log_entry(
            project_name=project_name or "system",
            event_type="MONITORING_STARTED",
            message="Deploy monitoring started",
            details={
                "event_category": "system"
            }
        )

    async def log_monitoring_stopped(self, project_name: Optional[str] = None):
        """Log monitoring stop event"""
        await self._queue_log_entry(
            project_name=project_name or "system",
            event_type="MONITORING_STOPPED",
            message="Deploy monitoring stopped",
            details={
                "event_category": "system"
            }
        )

    async def log_custom_event(self, project_name: str, event_type: str, message: str, 
                             details: Optional[Dict[str, Any]] = None, project_path: Optional[str] = None):
        """Log a custom event"""
        await self._queue_log_entry(
            project_name=project_name,
            project_path=project_path,
            event_type=event_type,
            message=message,
            details=details or {}
        )

    async def _queue_log_entry(self, project_name: str, event_type: str, message: str, 
                             details: Optional[Dict[str, Any]] = None, project_path: Optional[str] = None):
        """Queue a log entry for processing"""
        log_entry = {
            "timestamp": datetime.now(),
            "project_name": project_name,
            "project_path": project_path,
            "event_type": event_type,
            "message": message,
            "details": details or {}
        }
        
        try:
            await self.log_queue.put(log_entry)
            logger.debug("📝 [ACTIVITY_LOGGER] Log entry queued", 
                        project_name=project_name, event_type=event_type)
        except Exception as e:
            logger.error("❌ [ACTIVITY_LOGGER] Failed to queue log entry", 
                        project_name=project_name, error=str(e))

    async def _process_log_queue(self):
        """Process queued log entries"""
        logger.info("🔄 [ACTIVITY_LOGGER] Starting log queue processing...")
        
        while self.processing_active:
            try:
                # MEMORY LEAK FIX: Increased timeout to reduce CPU pressure
                log_entry = await asyncio.wait_for(self.log_queue.get(), timeout=2.0)
                await self._write_log_entry(log_entry)
                self.log_queue.task_done()
                
            except asyncio.TimeoutError:
                # No new log entries, continue
                continue
            except asyncio.CancelledError:
                logger.info("🔄 [ACTIVITY_LOGGER] Log queue processing cancelled")
                break
            except Exception as e:
                logger.error("❌ [ACTIVITY_LOGGER] Error processing log queue", error=str(e))
                # MEMORY LEAK FIX: Increased wait time on errors
                await asyncio.sleep(2)  # Wait 2 seconds before retrying instead of 1

    async def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write a log entry to the appropriate file"""
        try:
            project_name = log_entry["project_name"]
            timestamp = log_entry["timestamp"]
            event_type = log_entry["event_type"]
            message = log_entry["message"]
            project_path = log_entry.get("project_path")
            
            # Format timestamp
            timestamp_str = timestamp.strftime("[%Y-%m-%d %H:%M:%S]")
            
            # Create log line
            log_line = f"{timestamp_str} {event_type}: {message}\n"
            
            # Determine log file path
            log_file = self._get_log_file_path(project_name, project_path)
            
            if log_file:
                # Ensure log directory exists
                log_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write log entry
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_line)
                
                logger.debug("✅ [ACTIVITY_LOGGER] Log entry written", 
                           project_name=project_name, 
                           event_type=event_type,
                           log_file=str(log_file))
            else:
                logger.warning("⚠️ [ACTIVITY_LOGGER] Could not determine log file path", 
                             project_name=project_name)
        
        except Exception as e:
            logger.error("❌ [ACTIVITY_LOGGER] Failed to write log entry", 
                        project_name=log_entry.get("project_name"), error=str(e))

    def _get_log_file_path(self, project_name: str, project_path: Optional[str] = None) -> Optional[Path]:
        """
        Determine the appropriate log file path for a project
        
        PHASE 1 ENHANCED: Now uses ProjectDirectoryManager for path resolution
        """
        try:
            if project_name == "system":
                # System-wide events go to a global log
                projects_root = Path(__file__).parent.parent / "projects"
                projects_root.mkdir(exist_ok=True)
                return projects_root / "system_activity.log"
            
            if project_path:
                # Use provided project path directly
                project_dir = Path(project_path)
                logger.debug("🔍 [ACTIVITY_LOGGER] Using provided project path", 
                           project_name=project_name, path=str(project_dir))
            else:
                # PHASE 1: Use ProjectDirectoryManager to resolve project path
                try:
                    from project_directory_manager import project_directory_manager
                    import asyncio
                    
                    # Get the current event loop or create a new one
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # If we're already in an async context, we can't use await
                            # Fall back to the old method for now
                            logger.debug("🔄 [ACTIVITY_LOGGER] In async context, using fallback method")
                            projects_root = Path(__file__).parent.parent / "projects"
                            project_dir = projects_root / project_name
                        else:
                            # We can run the async method
                            resolved_path = loop.run_until_complete(
                                project_directory_manager.get_project_path(project_name)
                            )
                            if resolved_path:
                                project_dir = Path(resolved_path)
                                logger.debug("✅ [ACTIVITY_LOGGER] Resolved project path using directory manager", 
                                           project_name=project_name, path=str(project_dir))
                            else:
                                logger.debug("❓ [ACTIVITY_LOGGER] Project not found in directory manager", 
                                           project_name=project_name)
                                return None
                    except RuntimeError:
                        # No event loop, create one
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            resolved_path = loop.run_until_complete(
                                project_directory_manager.get_project_path(project_name)
                            )
                            if resolved_path:
                                project_dir = Path(resolved_path)
                                logger.debug("✅ [ACTIVITY_LOGGER] Resolved project path with new event loop", 
                                           project_name=project_name, path=str(project_dir))
                            else:
                                logger.debug("❓ [ACTIVITY_LOGGER] Project not found in directory manager", 
                                           project_name=project_name)
                                return None
                        finally:
                            loop.close()
                            
                except Exception as e:
                    logger.debug("🔄 [ACTIVITY_LOGGER] Could not use directory manager, falling back", 
                               error=str(e))
                    # Fallback to old method
                    projects_root = Path(__file__).parent.parent / "projects"
                    project_dir = projects_root / project_name
            
            if project_dir.exists():
                logs_dir = project_dir / "logs"
                logs_dir.mkdir(exist_ok=True)
                return logs_dir / "activity.log"
            else:
                logger.warning("⚠️ [ACTIVITY_LOGGER] Project directory not found", 
                             project_name=project_name, 
                             project_path=project_path,
                             resolved_path=str(project_dir))
                return None
        
        except Exception as e:
            logger.error("❌ [ACTIVITY_LOGGER] Error determining log file path", 
                        project_name=project_name, error=str(e))
            return None

    async def get_recent_logs(self, project_name: str, limit: int = 20, 
                            project_path: Optional[str] = None) -> List[str]:
        """Get recent log entries for a project"""
        try:
            log_file = self._get_log_file_path(project_name, project_path)
            
            if not log_file or not log_file.exists():
                return []
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Get the most recent entries
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            return [line.strip() for line in recent_lines if line.strip()]
        
        except Exception as e:
            logger.error("❌ [ACTIVITY_LOGGER] Failed to get recent logs", 
                        project_name=project_name, error=str(e))
            return []

    async def clear_project_logs(self, project_name: str, project_path: Optional[str] = None) -> bool:
        """Clear all logs for a project"""
        try:
            log_file = self._get_log_file_path(project_name, project_path)
            
            if log_file and log_file.exists():
                log_file.unlink()
                logger.info("🗑️ [ACTIVITY_LOGGER] Project logs cleared", 
                           project_name=project_name)
                return True
            
            return True  # No logs to clear
        
        except Exception as e:
            logger.error("❌ [ACTIVITY_LOGGER] Failed to clear project logs", 
                        project_name=project_name, error=str(e))
            return False

    async def cleanup(self):
        """Clean up activity logger resources"""
        logger.info("🧹 [ACTIVITY_LOGGER] Cleaning up activity logger...")
        
        await self.stop_processing()
        
        # Process any remaining queued entries
        while not self.log_queue.empty():
            try:
                log_entry = self.log_queue.get_nowait()
                await self._write_log_entry(log_entry)
                self.log_queue.task_done()
            except asyncio.QueueEmpty:
                break
            except Exception as e:
                logger.warning("⚠️ [ACTIVITY_LOGGER] Error processing final log entries", 
                             error=str(e))
        
        logger.info("✅ [ACTIVITY_LOGGER] Activity logger cleanup completed")

# Global instance
activity_logger = ActivityLogger() 