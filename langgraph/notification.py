#!/usr/bin/env python3
"""
Hybrid Notification System for DeployBot

This module handles:
- macOS system notifications for deploy detection and task suggestions
- In-app modal coordination through WebSocket communication
- Notification preferences and user response handling
- Cross-platform notification support (macOS focus)
"""

import asyncio
import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union
import structlog

logger = structlog.get_logger()

# macOS notification support
try:
    import pync
    PYNC_AVAILABLE = True
    logger.info("✅ [NOTIFY] pync library available for macOS notifications")
except ImportError:
    PYNC_AVAILABLE = False
    logger.warning("⚠️ [NOTIFY] pync library not available - using fallback notifications")

class NotificationManager:
    """Comprehensive notification system for DeployBot"""
    
    def __init__(self):
        self.websocket_server = None  # Will be set externally
        self.notification_callbacks = []
        self.notification_history = []
        self.max_history = 50
        
        # Notification preferences
        self.preferences = {
            "system_notifications_enabled": True,
            "in_app_modals_enabled": True,
            "sound_enabled": True,
            "auto_dismiss_timeout": 30,  # seconds
            "grace_period": 180,  # 3 minutes before task suggestion
            "notification_persistence": True
        }
        
        # Notification templates
        self.templates = {
            "deploy_detected": {
                "title": "🚀 Deploy Detected",
                "message": "Deployment started: {command}",
                "actions": ["View Timer", "Dismiss"],
                "category": "deploy",
                "sound": "default"
            },
            "task_suggestion": {
                "title": "🎯 Task Suggestion",
                "message": "Switch to: {task_text}",
                "actions": ["Switch Now", "Snooze 5min", "Dismiss"],
                "category": "task",
                "sound": "default"
            },
            "timer_expiry": {
                "title": "⏰ Timer Expired",
                "message": "Deploy timer finished for {project}",
                "actions": ["View Project", "Dismiss"],
                "category": "timer",
                "sound": "default"
            },
            "deploy_completed": {
                "title": "✅ Deploy Complete",
                "message": "Deployment finished: {status}",
                "actions": ["View Logs", "Dismiss"],
                "category": "deploy",
                "sound": "success"
            }
        }
        
        # Active notification tracking
        self.active_notifications = {}  # notification_id -> notification_data
        self.notification_responses = {}  # notification_id -> user_response
        
        logger.info("🔔 [NOTIFY] NotificationManager initialized", 
                   system_notifications=PYNC_AVAILABLE,
                   templates=len(self.templates))

    def set_websocket_server(self, websocket_server):
        """Set the WebSocket server for communication with frontend"""
        self.websocket_server = websocket_server
        logger.info("🔌 [NOTIFY] WebSocket server attached to notification manager")

    def add_notification_callback(self, callback: Callable):
        """Add a callback to be notified of notification events"""
        self.notification_callbacks.append(callback)
        logger.debug("📡 [NOTIFY] Notification callback registered")

    async def notify_deploy_detected(self, project_name: str, deploy_command: str, 
                                   timer_duration: int = 1800) -> str:
        """Send notification when a deploy is detected"""
        logger.info("🚀 [NOTIFY] Sending deploy detected notification", 
                   project=project_name, command=deploy_command)
        
        notification_data = {
            "type": "deploy_detected",
            "project_name": project_name,
            "deploy_command": deploy_command,
            "timer_duration": timer_duration,
            "timestamp": datetime.now().isoformat(),
            "grace_period": self.preferences["grace_period"]
        }
        
        return await self._send_notification("deploy_detected", notification_data)

    async def notify_task_suggestion(self, project_name: str, task: Dict[str, Any], 
                                   context: Dict[str, Any] = None) -> str:
        """Send notification suggesting an alternative task"""
        logger.info("🎯 [NOTIFY] Sending task suggestion notification", 
                   project=project_name, task=task.get('text', ''))
        
        notification_data = {
            "type": "task_suggestion",
            "project_name": project_name,
            "task": task,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "estimated_duration": task.get('estimated_duration', 45),
            "task_app": task.get('app', 'Unknown')
        }
        
        return await self._send_notification("task_suggestion", notification_data)

    async def notify_timer_expiry(self, project_name: str, timer_info: Dict[str, Any]) -> str:
        """Send notification when a deploy timer expires"""
        logger.info("⏰ [NOTIFY] Sending timer expiry notification", project=project_name)
        
        notification_data = {
            "type": "timer_expiry",
            "project_name": project_name,
            "timer_info": timer_info,
            "timestamp": datetime.now().isoformat(),
            "duration": timer_info.get('duration_seconds', 0)
        }
        
        return await self._send_notification("timer_expiry", notification_data)

    async def notify_deploy_completed(self, project_name: str, deploy_command: str, 
                                    success: bool, exit_code: int = 0) -> str:
        """Send notification when a deploy completes"""
        logger.info("✅ [NOTIFY] Sending deploy completed notification", 
                   project=project_name, success=success)
        
        status = "successfully" if success else f"with error (exit code: {exit_code})"
        
        notification_data = {
            "type": "deploy_completed",
            "project_name": project_name,
            "deploy_command": deploy_command,
            "success": success,
            "exit_code": exit_code,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        return await self._send_notification("deploy_completed", notification_data)

    async def _send_notification(self, template_name: str, data: Dict[str, Any]) -> str:
        """Send a notification using the specified template"""
        
        notification_id = f"{template_name}_{int(time.time() * 1000)}"
        template = self.templates.get(template_name, {})
        
        # Prepare notification content
        notification = {
            "id": notification_id,
            "template": template_name,
            "title": self._format_template_string(template.get("title", "DeployBot"), data),
            "message": self._format_template_string(template.get("message", "Notification"), data),
            "actions": template.get("actions", ["Dismiss"]),
            "category": template.get("category", "general"),
            "sound": template.get("sound", "default"),
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "auto_dismiss_timeout": self.preferences["auto_dismiss_timeout"]
        }
        
        # Store in active notifications
        self.active_notifications[notification_id] = notification
        
        # Add to history
        self._add_to_history(notification)
        
        # Send system notification if enabled
        if self.preferences["system_notifications_enabled"]:
            await self._send_system_notification(notification)
        
        # Send in-app notification if enabled
        if self.preferences["in_app_modals_enabled"]:
            await self._send_in_app_notification(notification)
        
        # Notify callbacks
        await self._notify_callbacks("notification_sent", notification)
        
        # Schedule auto-dismiss if configured
        if self.preferences["auto_dismiss_timeout"] > 0:
            asyncio.create_task(self._auto_dismiss_notification(notification_id))
        
        logger.info("✅ [NOTIFY] Notification sent successfully", 
                   notification_id=notification_id, 
                   template=template_name)
        
        return notification_id

    async def _send_system_notification(self, notification: Dict[str, Any]):
        """Send macOS system notification"""
        
        try:
            title = notification["title"]
            message = notification["message"]
            sound = notification["sound"] if self.preferences["sound_enabled"] else None
            
            if PYNC_AVAILABLE:
                # Use pync for advanced macOS notifications
                pync.notify(
                    message=message,
                    title=title,
                    subtitle="DeployBot",
                    sound=sound,
                    group="deploybot",
                    activate="com.apple.Terminal",  # Bring Terminal to front when clicked
                    timeout=self.preferences["auto_dismiss_timeout"]
                )
                logger.debug("📱 [NOTIFY] macOS notification sent via pync")
                
            else:
                # Fallback to osascript
                script = f'''
                display notification "{message}" ¬
                with title "{title}" ¬
                subtitle "DeployBot"
                '''
                
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: subprocess.run(
                        ['osascript', '-e', script],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                )
                
                if result.returncode == 0:
                    logger.debug("📱 [NOTIFY] macOS notification sent via osascript")
                else:
                    logger.warning("⚠️ [NOTIFY] osascript notification failed", 
                                 error=result.stderr)
                    
        except Exception as e:
            logger.error("❌ [NOTIFY] Failed to send system notification", error=str(e))

    async def _send_in_app_notification(self, notification: Dict[str, Any]):
        """Send in-app notification via WebSocket"""
        
        if not self.websocket_server:
            logger.warning("⚠️ [NOTIFY] WebSocket server not available for in-app notification")
            return
        
        try:
            message = {
                "type": "notification",
                "event": "show_modal",
                "data": {
                    "notification": notification,
                    "show_modal": True,
                    "modal_type": "notification",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await self.websocket_server.broadcast(message)
            logger.debug("📱 [NOTIFY] In-app notification sent via WebSocket")
            
        except Exception as e:
            logger.error("❌ [NOTIFY] Failed to send in-app notification", error=str(e))

    async def handle_notification_response(self, notification_id: str, action: str, 
                                         additional_data: Dict[str, Any] = None) -> bool:
        """Handle user response to a notification"""
        logger.info("👆 [NOTIFY] Handling notification response", 
                   notification_id=notification_id, action=action)
        
        if notification_id not in self.active_notifications:
            logger.warning("⚠️ [NOTIFY] Notification not found", 
                          notification_id=notification_id)
            return False
        
        notification = self.active_notifications[notification_id]
        response_data = {
            "notification_id": notification_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "additional_data": additional_data or {}
        }
        
        # Store response
        self.notification_responses[notification_id] = response_data
        
        # Process the response based on action
        await self._process_notification_action(notification, action, additional_data or {})
        
        # Remove from active notifications unless it's a snooze
        if action not in ["snooze", "snooze_5min", "snooze_10min"]:
            self.active_notifications.pop(notification_id, None)
        
        # Notify callbacks
        await self._notify_callbacks("notification_response", response_data)
        
        logger.info("✅ [NOTIFY] Notification response processed", 
                   notification_id=notification_id, action=action)
        
        return True

    async def _process_notification_action(self, notification: Dict[str, Any], 
                                         action: str, additional_data: Dict[str, Any]):
        """Process specific notification actions"""
        
        notification_type = notification["data"]["type"]
        
        try:
            if action == "switch_now" and notification_type == "task_suggestion":
                # Handle task switching
                await self._handle_task_switch(notification, additional_data)
                
            elif action.startswith("snooze"):
                # Handle snoozing
                await self._handle_snooze(notification, action, additional_data)
                
            elif action == "view_timer" and notification_type == "deploy_detected":
                # Send timer status to frontend
                await self._send_timer_status(notification)
                
            elif action == "view_logs" and notification_type == "deploy_completed":
                # Send log information to frontend
                await self._send_deploy_logs(notification)
                
            elif action == "dismiss":
                # Simple dismissal - already handled by removing from active notifications
                logger.debug("📱 [NOTIFY] Notification dismissed", 
                           notification_id=notification["id"])
                
        except Exception as e:
            logger.error("❌ [NOTIFY] Error processing notification action", 
                        action=action, error=str(e))

    async def _handle_task_switch(self, notification: Dict[str, Any], additional_data: Dict[str, Any]):
        """Handle task switching action"""
        
        task_data = notification["data"]["task"]
        project_name = notification["data"]["project_name"]
        context = notification["data"].get("context", {})
        
        logger.info("🔀 [NOTIFY] Processing task switch request", 
                   task=task_data.get('text', ''), 
                   app=task_data.get('app', ''))
        
        # Import redirect module to handle app opening
        from . import redirect
        
        # Perform the redirection
        redirect_result = await redirect.app_redirector.redirect_to_task(task_data, context)
        
        # Notify frontend of redirection result
        if self.websocket_server:
            await self.websocket_server.broadcast({
                "type": "task",
                "event": "redirection_result",
                "data": {
                    "task": task_data,
                    "redirect_result": redirect_result,
                    "project_name": project_name,
                    "timestamp": datetime.now().isoformat()
                }
            })

    async def _handle_snooze(self, notification: Dict[str, Any], action: str, 
                           additional_data: Dict[str, Any]):
        """Handle notification snoozing"""
        
        # Parse snooze duration
        if action == "snooze_5min":
            snooze_minutes = 5
        elif action == "snooze_10min":
            snooze_minutes = 10
        else:
            snooze_minutes = int(additional_data.get("snooze_minutes", 5))
        
        logger.info("😴 [NOTIFY] Snoozing notification", 
                   notification_id=notification["id"], 
                   minutes=snooze_minutes)
        
        # Schedule re-notification
        snooze_task = asyncio.create_task(
            self._reschedule_notification(notification, snooze_minutes * 60)
        )
        
        # Store snooze task for potential cancellation
        notification["snooze_task"] = snooze_task

    async def _reschedule_notification(self, notification: Dict[str, Any], delay_seconds: int):
        """Reschedule a notification after snooze period"""
        
        await asyncio.sleep(delay_seconds)
        
        # Re-send the notification
        notification["id"] = f"{notification['template']}_resend_{int(time.time() * 1000)}"
        notification["timestamp"] = datetime.now().isoformat()
        notification["message"] += " (Reminder)"
        
        self.active_notifications[notification["id"]] = notification
        
        # Send notifications again
        if self.preferences["system_notifications_enabled"]:
            await self._send_system_notification(notification)
        
        if self.preferences["in_app_modals_enabled"]:
            await self._send_in_app_notification(notification)
        
        logger.info("🔔 [NOTIFY] Snoozed notification re-sent", 
                   notification_id=notification["id"])

    async def _auto_dismiss_notification(self, notification_id: str):
        """Auto-dismiss notification after timeout"""
        
        await asyncio.sleep(self.preferences["auto_dismiss_timeout"])
        
        if notification_id in self.active_notifications:
            logger.debug("⏰ [NOTIFY] Auto-dismissing notification", 
                        notification_id=notification_id)
            
            await self.handle_notification_response(notification_id, "auto_dismiss")

    async def _send_timer_status(self, notification: Dict[str, Any]):
        """Send timer status to frontend"""
        
        if self.websocket_server:
            project_name = notification["data"]["project_name"]
            
            await self.websocket_server.broadcast({
                "type": "timer",
                "event": "status_request",
                "data": {
                    "project_name": project_name,
                    "timestamp": datetime.now().isoformat()
                }
            })

    async def _send_deploy_logs(self, notification: Dict[str, Any]):
        """Send deploy logs to frontend"""
        
        if self.websocket_server:
            project_name = notification["data"]["project_name"]
            
            await self.websocket_server.broadcast({
                "type": "logs",
                "event": "deploy_logs_request",
                "data": {
                    "project_name": project_name,
                    "timestamp": datetime.now().isoformat()
                }
            })

    def _format_template_string(self, template: str, data: Dict[str, Any]) -> str:
        """Format template string with data"""
        
        try:
            # Flatten nested data for template formatting
            flat_data = {}
            
            for key, value in data.items():
                if isinstance(value, dict):
                    # Handle nested dictionaries
                    for nested_key, nested_value in value.items():
                        flat_data[f"{key}_{nested_key}"] = nested_value
                else:
                    flat_data[key] = value
            
            # Add commonly used formatters
            if "task" in data and isinstance(data["task"], dict):
                flat_data["task_text"] = data["task"].get("text", "Unknown task")
                flat_data["task_app"] = data["task"].get("app", "Unknown app")
            
            if "project_name" in data:
                flat_data["project"] = data["project_name"]
            
            if "deploy_command" in data:
                flat_data["command"] = data["deploy_command"]
                
            return template.format(**flat_data)
            
        except (KeyError, ValueError) as e:
            logger.warning("⚠️ [NOTIFY] Template formatting failed", 
                          template=template, error=str(e))
            return template

    def _add_to_history(self, notification: Dict[str, Any]):
        """Add notification to history"""
        
        self.notification_history.append({
            "id": notification["id"],
            "title": notification["title"],
            "message": notification["message"],
            "category": notification["category"],
            "timestamp": notification["timestamp"]
        })
        
        # Trim history if it exceeds max size
        if len(self.notification_history) > self.max_history:
            self.notification_history = self.notification_history[-self.max_history:]

    async def _notify_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Notify all registered callbacks"""
        
        for callback in self.notification_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, data)
                else:
                    callback(event_type, data)
            except Exception as e:
                logger.error("❌ [NOTIFY] Error in notification callback", 
                           event_type=event_type, error=str(e))

    async def get_notification_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent notification history"""
        
        return self.notification_history[-limit:] if self.notification_history else []

    async def get_active_notifications(self) -> Dict[str, Dict[str, Any]]:
        """Get currently active notifications"""
        
        return self.active_notifications.copy()

    async def dismiss_all_notifications(self) -> int:
        """Dismiss all active notifications"""
        
        count = len(self.active_notifications)
        
        for notification_id in list(self.active_notifications.keys()):
            await self.handle_notification_response(notification_id, "dismiss_all")
        
        logger.info("🗑️ [NOTIFY] All notifications dismissed", count=count)
        return count

    def update_preferences(self, new_preferences: Dict[str, Any]):
        """Update notification preferences"""
        
        self.preferences.update(new_preferences)
        logger.info("⚙️ [NOTIFY] Notification preferences updated", 
                   preferences=self.preferences)

    async def test_notification(self, notification_type: str = "task_suggestion") -> str:
        """Send a test notification for debugging"""
        
        test_data = {
            "project_name": "TestProject",
            "deploy_command": "test deploy command",
            "task": {
                "text": "Test task for notification",
                "app": "Bear",
                "tags": ["#test", "#short"]
            },
            "timer_duration": 1800
        }
        
        logger.info("🧪 [NOTIFY] Sending test notification", type=notification_type)
        return await self._send_notification(notification_type, test_data)

# Global instance
notification_manager = NotificationManager() 