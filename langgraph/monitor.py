#!/usr/bin/env python3
"""
Deploy Detection Monitor for DeployBot

This module handles monitoring deploy log files for new deployment events
and integrating with the LangGraph workflow to trigger timer and task selection.
"""

import asyncio
import json
import time
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
from datetime import datetime
import structlog

logger = structlog.get_logger()

class DeployMonitor:
    """Monitors deploy log files for new deployment events"""
    
    def __init__(self):
        self.monitored_projects = {}  # project_name -> project_info
        self.last_known_positions = {}  # log_file_path -> last_read_position
        self.monitoring_active = False
        self.monitor_task = None
        self.check_interval = 2.0  # Check every 2 seconds
        self.event_callbacks = []  # Callbacks for deploy detection events
        
        # Specific callbacks for different event types
        self.deploy_detected_callback = None
        self.deploy_completed_callback = None
        
        logger.info("🔍 [DEPLOY_MONITOR] DeployMonitor initialized")
    
    def set_deploy_detected_callback(self, callback):
        """Set callback for deploy detected events"""
        self.deploy_detected_callback = callback
        logger.info("📡 [DEPLOY_MONITOR] Deploy detected callback set")
    
    def set_deploy_completed_callback(self, callback):
        """Set callback for deploy completed events"""
        self.deploy_completed_callback = callback
        logger.info("📡 [DEPLOY_MONITOR] Deploy completed callback set")

    def add_event_callback(self, callback):
        """Add a callback function to be called when deploy events are detected"""
        self.event_callbacks.append(callback)
        logger.info("📡 [DEPLOY_MONITOR] Event callback registered")

    def remove_event_callback(self, callback):
        """Remove an event callback"""
        if callback in self.event_callbacks:
            self.event_callbacks.remove(callback)
            logger.info("📡 [DEPLOY_MONITOR] Event callback removed")

    async def add_project(self, project_name: str, project_path: str) -> bool:
        """Add a project to monitor for deploy events"""
        logger.info("📁 [DEPLOY_MONITOR] Adding project to monitoring", 
                   project_name=project_name, project_path=project_path)
        
        try:
            project_path_obj = Path(project_path).resolve()
            
            # Verify project structure
            config_file = project_path_obj / "config.json"
            todo_file = project_path_obj / "TODO.md"
            logs_dir = project_path_obj / "logs"
            
            if not config_file.exists():
                logger.warning("⚠️ [DEPLOY_MONITOR] Project config.json not found", 
                             project_name=project_name)
                return False
            
            if not todo_file.exists():
                logger.warning("⚠️ [DEPLOY_MONITOR] Project TODO.md not found", 
                             project_name=project_name)
                return False
            
            # Ensure logs directory exists
            logs_dir.mkdir(exist_ok=True)
            deploy_log = logs_dir / "deploy_log.txt"
            
            # Load project configuration
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.error("❌ [DEPLOY_MONITOR] Failed to load project config", 
                           project_name=project_name, error=str(e))
                return False
            
            # Store project info
            project_info = {
                "name": project_name,
                "path": str(project_path_obj),
                "config": config,
                "deploy_log": str(deploy_log),
                "last_deploy_time": None,
                "deploy_count": 0
            }
            
            self.monitored_projects[project_name] = project_info
            
            # Initialize log position tracking
            if deploy_log.exists():
                # Start monitoring from the end of existing log
                self.last_known_positions[str(deploy_log)] = deploy_log.stat().st_size
                logger.info("📏 [DEPLOY_MONITOR] Starting from end of existing log", 
                           position=deploy_log.stat().st_size)
            else:
                # Create empty log file and start from position 0
                deploy_log.touch()
                self.last_known_positions[str(deploy_log)] = 0
                logger.info("📄 [DEPLOY_MONITOR] Created new deploy log file")
            
            logger.info("✅ [DEPLOY_MONITOR] Project added successfully", 
                       project_name=project_name, deploy_log=str(deploy_log))
            return True
            
        except Exception as e:
            logger.error("❌ [DEPLOY_MONITOR] Failed to add project", 
                        project_name=project_name, error=str(e))
            return False

    async def remove_project(self, project_name: str) -> bool:
        """Remove a project from monitoring"""
        logger.info("🗑️ [DEPLOY_MONITOR] Removing project from monitoring", 
                   project_name=project_name)
        
        if project_name in self.monitored_projects:
            project_info = self.monitored_projects[project_name]
            deploy_log = project_info["deploy_log"]
            
            # Clean up position tracking
            if deploy_log in self.last_known_positions:
                del self.last_known_positions[deploy_log]
            
            # Remove project
            del self.monitored_projects[project_name]
            
            logger.info("✅ [DEPLOY_MONITOR] Project removed successfully", 
                       project_name=project_name)
            return True
        else:
            logger.warning("⚠️ [DEPLOY_MONITOR] Project not found in monitoring list", 
                          project_name=project_name)
            return False

    async def start_monitoring(self) -> bool:
        """Start the deploy monitoring loop"""
        if self.monitoring_active:
            logger.warning("⚠️ [DEPLOY_MONITOR] Monitoring already active")
            return True
        
        logger.info("🚀 [DEPLOY_MONITOR] Starting deploy monitoring...")
        
        # Add global deploy log monitoring as fallback
        await self._add_global_log_monitoring()
        
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("✅ [DEPLOY_MONITOR] Deploy monitoring started successfully")
        return True

    async def _add_global_log_monitoring(self):
        """Add monitoring for the global deploy log as a fallback"""
        global_log_dir = Path.home() / ".deploybot"
        global_log = global_log_dir / "deploy_log.txt"
        
        # Ensure global log exists
        global_log_dir.mkdir(exist_ok=True)
        if not global_log.exists():
            global_log.touch()
        
        # Add global monitoring entry
        self.monitored_projects["_global"] = {
            "name": "_global",
            "path": str(global_log_dir),
            "config": {"type": "global_fallback"},
            "deploy_log": str(global_log),
            "last_deploy_time": None,
            "deploy_count": 0
        }
        
        # Initialize position tracking
        if global_log.exists():
            self.last_known_positions[str(global_log)] = global_log.stat().st_size
        else:
            self.last_known_positions[str(global_log)] = 0
            
        logger.info("🌐 [DEPLOY_MONITOR] Added global log monitoring", 
                   global_log=str(global_log))

    async def stop_monitoring(self) -> bool:
        """Stop the deploy monitoring loop"""
        if not self.monitoring_active:
            logger.warning("⚠️ [DEPLOY_MONITOR] Monitoring not active")
            return True
        
        logger.info("🛑 [DEPLOY_MONITOR] Stopping deploy monitoring...")
        
        self.monitoring_active = False
        
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
            self.monitor_task = None
        
        logger.info("✅ [DEPLOY_MONITOR] Deploy monitoring stopped successfully")
        return True

    async def _monitoring_loop(self):
        """Main monitoring loop that checks for new deploy events"""
        logger.info("🔄 [DEPLOY_MONITOR] Starting monitoring loop...")
        
        while self.monitoring_active:
            try:
                # Check all monitored projects for new deploy events
                for project_name, project_info in self.monitored_projects.items():
                    await self._check_project_for_deploys(project_name, project_info)
                
                # Wait before next check
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                logger.info("🔄 [DEPLOY_MONITOR] Monitoring loop cancelled")
                break
            except Exception as e:
                logger.error("❌ [DEPLOY_MONITOR] Error in monitoring loop", error=str(e))
                # Continue monitoring despite errors
                await asyncio.sleep(self.check_interval * 2)  # Wait longer after errors

    async def _check_project_for_deploys(self, project_name: str, project_info: Dict[str, Any]):
        """Check a specific project's deploy log for new events"""
        deploy_log_path = project_info["deploy_log"]
        
        try:
            deploy_log = Path(deploy_log_path)
            
            if not deploy_log.exists():
                # Log file doesn't exist yet, skip
                return
            
            current_size = deploy_log.stat().st_size
            last_position = self.last_known_positions.get(deploy_log_path, 0)
            
            if current_size <= last_position:
                # No new content
                return
            
            # Read new content
            with open(deploy_log, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_content = f.read()
            
            # Update position
            self.last_known_positions[deploy_log_path] = current_size
            
            # Parse new deploy events
            new_events = self._parse_deploy_events(new_content, project_name)
            
            # Process each new event
            for event in new_events:
                await self._handle_deploy_event(event, project_info)
                
        except Exception as e:
            logger.error("❌ [DEPLOY_MONITOR] Error checking project deploys", 
                        project_name=project_name, error=str(e))

    def _parse_deploy_events(self, content: str, project_name: str) -> List[Dict[str, Any]]:
        """Parse deploy events from log content"""
        events = []
        
        for line in content.strip().split('\n'):
            if not line.strip():
                continue
                
            event = self._parse_deploy_line(line, project_name)
            if event:
                events.append(event)
        
        if events:
            logger.info("📝 [DEPLOY_MONITOR] Parsed deploy events", 
                       project_name=project_name, event_count=len(events))
        
        return events

    def _parse_deploy_line(self, line: str, project_name: str) -> Optional[Dict[str, Any]]:
        """Parse a single deploy log line"""
        try:
            # Expected format: "timestamp DEPLOY: command [CWD: path]"
            # or: "timestamp DEPLOY_COMPLETE: command [EXIT_CODE: code]"
            
            parts = line.strip().split(' ', 2)
            if len(parts) < 3:
                return None
            
            timestamp_str = parts[0]
            event_type = parts[1].rstrip(':')
            remaining = parts[2] if len(parts) > 2 else ""
            
            try:
                timestamp = float(timestamp_str)
            except ValueError:
                logger.warning("⚠️ [DEPLOY_MONITOR] Invalid timestamp in log line", 
                             line=line, project_name=project_name)
                return None
            
            if event_type == "DEPLOY":
                # Parse deploy start event
                command_match = re.match(r'^(.*?)\s*\[CWD:\s*(.*?)\]$', remaining)
                if command_match:
                    command = command_match.group(1).strip()
                    cwd = command_match.group(2).strip()
                else:
                    command = remaining.strip()
                    cwd = None
                
                return {
                    "type": "deploy_start",
                    "timestamp": timestamp,
                    "datetime": datetime.fromtimestamp(timestamp),
                    "command": command,
                    "cwd": cwd,
                    "project_name": project_name
                }
                
            elif event_type == "DEPLOY_COMPLETE":
                # Parse deploy completion event
                command_match = re.match(r'^(.*?)\s*\[EXIT_CODE:\s*(\d+)\]$', remaining)
                if command_match:
                    command = command_match.group(1).strip()
                    exit_code = int(command_match.group(2))
                else:
                    command = remaining.strip()
                    exit_code = None
                
                return {
                    "type": "deploy_complete", 
                    "timestamp": timestamp,
                    "datetime": datetime.fromtimestamp(timestamp),
                    "command": command,
                    "exit_code": exit_code,
                    "project_name": project_name
                }
            
        except Exception as e:
            logger.warning("⚠️ [DEPLOY_MONITOR] Error parsing log line", 
                          line=line, project_name=project_name, error=str(e))
        
        return None

    async def _handle_deploy_event(self, event: Dict[str, Any], project_info: Dict[str, Any]):
        """Handle a detected deploy event"""
        project_name = event["project_name"]
        event_type = event["type"]
        
        logger.info("🚀 [DEPLOY_MONITOR] Deploy event detected", 
                   project_name=project_name, 
                   event_type=event_type,
                   command=event.get("command", "Unknown"),
                   timestamp=event["datetime"].isoformat())
        
        # Update project statistics
        if event_type == "deploy_start":
            project_info["last_deploy_time"] = event["datetime"].isoformat()
            project_info["deploy_count"] += 1
        
        # Call specific callbacks based on event type
        try:
            if event_type == "deploy_start" and self.deploy_detected_callback:
                await self.deploy_detected_callback(
                    project_name,
                    event.get("command", ""),
                    project_info["path"]
                )
            elif event_type == "deploy_complete" and self.deploy_completed_callback:
                await self.deploy_completed_callback(
                    project_name,
                    event.get("command", ""),
                    event.get("exit_code", 0),
                    project_info["path"]
                )
        except Exception as e:
            logger.error("❌ [DEPLOY_MONITOR] Error calling specific callback", 
                        event_type=event_type, error=str(e))
        
        # Notify all registered generic callbacks
        for callback in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event, project_info)
                else:
                    callback(event, project_info)
            except Exception as e:
                logger.error("❌ [DEPLOY_MONITOR] Error in event callback", 
                           project_name=project_name, error=str(e))

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get the current monitoring status"""
        return {
            "monitoring_active": self.monitoring_active,
            "monitored_projects": list(self.monitored_projects.keys()),
            "project_count": len(self.monitored_projects),
            "callback_count": len(self.event_callbacks),
            "check_interval": self.check_interval
        }

    def get_project_status(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get status for a specific project"""
        if project_name not in self.monitored_projects:
            return None
        
        project_info = self.monitored_projects[project_name]
        deploy_log = Path(project_info["deploy_log"])
        
        return {
            "project_name": project_name,
            "project_path": project_info["path"],
            "deploy_log_exists": deploy_log.exists(),
            "deploy_log_size": deploy_log.stat().st_size if deploy_log.exists() else 0,
            "last_deploy_time": project_info["last_deploy_time"],
            "deploy_count": project_info["deploy_count"],
            "last_known_position": self.last_known_positions.get(str(deploy_log), 0)
        }

    async def simulate_deploy_event(self, project_name: str, command: str = "test deploy") -> bool:
        """Simulate a deploy event for testing purposes"""
        logger.info("🧪 [DEPLOY_MONITOR] Simulating deploy event", 
                   project_name=project_name, command=command)
        
        if project_name not in self.monitored_projects:
            logger.warning("⚠️ [DEPLOY_MONITOR] Cannot simulate - project not monitored", 
                          project_name=project_name)
            return False
        
        try:
            project_info = self.monitored_projects[project_name]
            deploy_log = Path(project_info["deploy_log"])
            
            # Write a simulated deploy event
            timestamp = time.time()
            cwd = project_info["path"]
            
            with open(deploy_log, 'a') as f:
                f.write(f"{timestamp} DEPLOY: {command} [CWD: {cwd}]\n")
                f.write(f"{timestamp + 1} DEPLOY_COMPLETE: {command} [EXIT_CODE: 0]\n")
            
            logger.info("✅ [DEPLOY_MONITOR] Deploy event simulated successfully")
            return True
            
        except Exception as e:
            logger.error("❌ [DEPLOY_MONITOR] Failed to simulate deploy event", 
                        project_name=project_name, error=str(e))
            return False

# Global instance
deploy_monitor = DeployMonitor() 