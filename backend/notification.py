#!/usr/bin/env python3
"""
Hybrid Notification System for DeployBot

This module handles:
- macOS system notifications for deploy detection and task suggestions
- In-app modal coordination through WebSocket communication
- Notification preferences and user response handling
- Cross-platform notification support (macOS focus)

📊 PHASE 2: Enhanced with Switch button analytics tracking for time saved calculation
"""

import asyncio
import copy
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
    PYNC_AVAILABLE = False  # FORCE osascript fallback due to Apple Silicon architecture issues
    logger.info("🔧 [NOTIFY] Forcing osascript fallback for Apple Silicon compatibility")
except ImportError:
    PYNC_AVAILABLE = False
    logger.warning("⚠️ [NOTIFY] pync library not available - using fallback notifications")

# 📊 PHASE 2: Analytics integration for Switch tracking
from analytics import analytics_manager

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
            "auto_dismiss_timeout": 0,  # DISABLED - notifications should persist until manually dismissed
            "grace_period": 0,  # NO GRACE PERIOD - immediate task suggestions when deploy completes
            "notification_persistence": True
        }
        
        # Notification templates
        self.templates = {
            "deploy_detected": {
                "title": "🚀 Deploy Started",
                "message": "Cloud deployment initiated: {command}",
                "actions": ["View Timer", "Dismiss"],
                "category": "deploy",
                "sound": "default"
            },
            "task_suggestion": {
                "title": "🎯 Task Suggestion",
                "message": "While waiting for propagation: {task_text}",
                "actions": ["Switch Now", "Snooze 5min", "Dismiss"],
                "category": "task",
                "sound": "default"
            },
            "timer_expiry": {
                "title": "⏰ Propagation Complete",
                "message": "Cloud deployment ready for {project}",
                "actions": ["View Project", "Dismiss"],
                "category": "timer",
                "sound": "default"
            },
            "deploy_completed": {
                "title": "✅ Local Deploy Complete",
                "message": "Starting cloud propagation: {status}",
                "actions": ["View Logs", "Dismiss"],
                "category": "deploy",
                "sound": "success"
            },
            "unified_suggestion": {
                "title": "🎯⏰ Task & Timer Update",
                "message": "Timer update with task suggestion available", 
                "actions": ["Switch to Task", "Start New Timer", "View Timer", "Snooze", "Dismiss"],
                "category": "unified",
                "sound": "default"
            }
        }
        
        # Active notification tracking
        self.active_notifications = {}  # notification_id -> notification_data
        self.notification_responses = {}  # notification_id -> user_response
        
        # 📊 ANALYTICS INTEGRATION: Track notification display times for response time calculation
        self.notification_display_times = {}  # notification_id -> display_timestamp
        
        # Initialize analytics integration (already imported above)
        self.analytics = analytics_manager
        
        # 📊 PHASE 2: Switch tracking for time saved analytics
        self.switch_tracking_enabled = True
        
        logger.info("🔔 [NOTIFY] NotificationManager initialized with Phase 2 Switch tracking", 
                   system_notifications=PYNC_AVAILABLE,
                   templates=len(self.templates),
                   analytics_enabled=True)

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
                                   context: Optional[Dict[str, Any]] = None) -> str:
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

    async def notify_unified_suggestion(self, project_name: str, 
                                      timer_info: Optional[Dict[str, Any]] = None,
                                      task: Optional[Dict[str, Any]] = None,
                                      context: Optional[Dict[str, Any]] = None) -> str:
        """Send unified notification combining timer updates and task suggestions"""
        logger.info("🎯⏰ [NOTIFY] Sending unified suggestion notification", 
                   project=project_name, 
                   has_timer=timer_info is not None,
                   has_task=task is not None)
        
        # Build contextual message based on what information we have
        message_parts = []
        
        if timer_info:
            timer_status = timer_info.get('status', 'unknown')
            if timer_status == 'expired':
                message_parts.append(f"⏰ Timer expired for {project_name}")
            elif timer_status == 'running':
                remaining = timer_info.get('time_remaining_formatted', 'unknown')
                message_parts.append(f"⏰ Timer running: {remaining} left")
            else:
                message_parts.append(f"⏰ Timer {timer_status}")
        
        if task:
            message_parts.append(f"🎯 Suggested: {task.get('text', 'Unknown task')}")
        
        # Fallback message if neither timer nor task info provided
        if not message_parts:
            message_parts.append("📋 Workflow update available")
        
        notification_data = {
            "type": "unified_suggestion",
            "project_name": project_name,
            "timer_info": timer_info,
            "task": task,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "has_timer": timer_info is not None,
            "has_task": task is not None,
            "estimated_duration": task.get('estimated_duration', 45) if task else None,
            "task_app": task.get('app', 'Unknown') if task else None
        }
        
        return await self._send_notification("unified_suggestion", notification_data)

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
        
        # 📊 ANALYTICS: Record notification display time for response time tracking
        self.notification_display_times[notification_id] = time.time()
        
        # Add to history
        self._add_to_history(notification)
        
        # Send custom notification via WebSocket to main process
        # This replaces system notifications with our custom implementation
        await self._send_custom_notification(notification)
        
        # Send system notification if enabled (as fallback)
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

    async def _send_custom_notification(self, notification: Dict[str, Any]):
        """Send custom notification via WebSocket to Electron main process"""
        
        logger.info("🔔 [NOTIFY] Sending custom notification via WebSocket", 
                   notification_id=notification["id"],
                   title=notification["title"])
        
        if not self.websocket_server:
            logger.warning("⚠️ [NOTIFY] WebSocket server not available for custom notification")
            return
        
        try:
            # Send custom notification message to main process
            message = {
                "type": "notification",
                "event": "show_custom",
                "data": {
                    "notification": notification,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            await self.websocket_server.broadcast(message)
            logger.info("✅ [NOTIFY] Custom notification sent successfully via WebSocket", 
                       notification_id=notification["id"])
            
        except Exception as e:
            logger.error("❌ [NOTIFY] Failed to send custom notification", 
                        notification_id=notification["id"], error=str(e))

    async def _send_system_notification(self, notification: Dict[str, Any]):
        """Send macOS system notification with multiple fallback methods"""
        
        title = notification["title"]
        message = notification["message"]
        sound = notification["sound"] if self.preferences["sound_enabled"] else None
        
        logger.info("🔔 [NOTIFY] Attempting system notification", 
                   title=title, message=message)
        
        # Method 1: Try pync if available (won't be used due to forced fallback)
        if PYNC_AVAILABLE:
            try:
                pync.notify(
                    message=message,
                    title=title,
                    subtitle="DeployBot",
                    sound=sound,
                    group="deploybot",
                    activate="com.apple.Terminal"
                )
                logger.debug("📱 [NOTIFY] macOS notification sent via pync")
                return
            except Exception as e:
                logger.warning("⚠️ [NOTIFY] pync notification failed, trying fallback", error=str(e))
        
        # Method 2: Standard osascript notification
        try:
            script = f'''
            display notification "{message}" ¬
            with title "{title}" ¬
            subtitle "DeployBot"
            '''
            
            logger.debug("🔧 [NOTIFY] Executing osascript", script=script.strip())
            
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
                # Test if notification actually appeared
                await self._verify_notification_display(title, message)
                return
            else:
                logger.warning("⚠️ [NOTIFY] osascript notification failed", 
                             error=result.stderr, returncode=result.returncode)
        except Exception as e:
            logger.error("❌ [NOTIFY] osascript notification failed", error=str(e))
        
        # Method 3: Alternative AppleScript approach
        try:
            alt_script = f'''
            tell application "System Events"
                display notification "{message}" with title "{title}" subtitle "DeployBot"
            end tell
            '''
            
            logger.debug("🔧 [NOTIFY] Trying alternative AppleScript approach")
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ['osascript', '-e', alt_script],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
            )
            
            if result.returncode == 0:
                logger.debug("📱 [NOTIFY] macOS notification sent via System Events")
                return
            else:
                logger.warning("⚠️ [NOTIFY] System Events notification failed", 
                             error=result.stderr)
        except Exception as e:
            logger.error("❌ [NOTIFY] System Events notification failed", error=str(e))
        
        # Method 4: Terminal bell + echo (audible fallback)
        try:
            logger.info("🔔 [NOTIFY] Using terminal bell fallback")
            
            bell_command = f'echo -e "\\a🚀 DeployBot: {title} - {message}"'
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ['bash', '-c', bell_command],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            )
            
            if result.returncode == 0:
                logger.info("🔔 [NOTIFY] Terminal bell notification sent")
            else:
                logger.warning("⚠️ [NOTIFY] Terminal bell failed", error=result.stderr)
                
        except Exception as e:
            logger.error("❌ [NOTIFY] All notification methods failed", error=str(e))
        
        # Method 5: Create visible file for manual checking
        try:
            desktop_path = os.path.expanduser("~/Desktop/DeployBot_Notification.txt")
            notification_text = f"""
🚀 DeployBot Notification
=========================
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Title: {title}
Message: {message}

This file was created because system notifications may not be working.
You can delete this file after reading the notification.
"""
            with open(desktop_path, 'w') as f:
                f.write(notification_text)
            
            logger.info("📄 [NOTIFY] Created desktop notification file", path=desktop_path)
            
        except Exception as e:
            logger.error("❌ [NOTIFY] Failed to create desktop notification file", error=str(e))

    async def _verify_notification_display(self, title: str, message: str):
        """Attempt to verify if notification was actually displayed"""
        try:
            # Check if we can detect the notification in the system
            check_script = '''
            tell application "System Events"
                if exists process "NotificationCenter" then
                    return "NotificationCenter running"
                else
                    return "NotificationCenter not found"
                end if
            end tell
            '''
            
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: subprocess.run(
                    ['osascript', '-e', check_script],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
            )
            
            if result.returncode == 0:
                logger.debug("🔍 [NOTIFY] Notification verification", result=result.stdout.strip())
            else:
                logger.debug("⚠️ [NOTIFY] Could not verify notification display")
                
        except Exception as e:
            logger.debug("❓ [NOTIFY] Notification verification failed", error=str(e))

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
                                         additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """Handle user response to a notification"""
        logger.info("👆 [NOTIFY] Handling notification response", 
                   notification_id=notification_id, action=action)
        
        if notification_id not in self.active_notifications:
            logger.warning("⚠️ [NOTIFY] Notification not found", 
                          notification_id=notification_id)
            return False
        
        notification = self.active_notifications[notification_id]
        response_timestamp = time.time()
        
        # 📊 ANALYTICS: Calculate response time
        display_time = self.notification_display_times.get(notification_id, response_timestamp)
        response_time_seconds = response_timestamp - display_time
        
        response_data = {
            "notification_id": notification_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "response_time_seconds": response_time_seconds,
            "additional_data": additional_data or {}
        }
        
        # Store response
        self.notification_responses[notification_id] = response_data
        
        # 📊 ANALYTICS: Record user interaction if this is a task suggestion
        await self._record_interaction_analytics(notification, action, response_time_seconds, additional_data or {})
        
        # Process the response based on action
        await self._process_notification_action(notification, action, additional_data or {})
        
        # Remove from active notifications unless it's a snooze
        if action not in ["snooze", "snooze_5min", "snooze_10min"]:
            self.active_notifications.pop(notification_id, None)
            # Clean up display time tracking
            self.notification_display_times.pop(notification_id, None)
        
        # Notify callbacks
        await self._notify_callbacks("notification_response", response_data)
        
        logger.info("✅ [NOTIFY] Notification response processed", 
                   notification_id=notification_id, action=action,
                   response_time=f"{response_time_seconds:.1f}s")
        
        return True

    async def _process_notification_action(self, notification: Dict[str, Any], 
                                         action: str, additional_data: Dict[str, Any]):
        """Process specific notification actions"""
        
        notification_type = notification["data"]["type"]
        
        try:
            if action == "switch_now" and notification_type == "task_suggestion":
                # Handle task switching
                await self._handle_task_switch(notification, additional_data)
                
            elif action == "switch_to_task" and notification_type == "unified_suggestion":
                # Handle task switching from unified notification
                await self._handle_task_switch(notification, additional_data)
                
            elif action.startswith("snooze"):
                # Handle snoozing
                await self._handle_snooze(notification, action, additional_data)
                
            elif action == "view_timer" and notification_type in ["deploy_detected", "unified_suggestion"]:
                # Send timer status to frontend
                await self._send_timer_status(notification)
                
            elif action == "start_new_timer" and notification_type == "unified_suggestion":
                # Handle starting a new timer
                await self._handle_start_new_timer(notification, additional_data)
                
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
        """
        Handle task switching action
        📊 PHASE 2: Enhanced with Switch button analytics tracking
        """
        
        task_data = notification["data"]["task"]
        project_name = notification["data"]["project_name"]
        original_context = notification["data"].get("context", {})
        
        # 📊 PHASE 2: Record Switch button press for time saved calculation
        logger.info("🔀 [NOTIFY] Recording Switch button press for analytics", 
                   project=project_name, task=task_data.get('text', ''))
        
        # Get active session for this project
        session_id = await analytics_manager.get_active_session_for_project(project_name)
        if session_id:
            await analytics_manager.record_switch_button_press(session_id, project_name)
        else:
            logger.warning("⚠️ [NOTIFY] No active session found for Switch tracking", project=project_name)
        
        # Build enhanced context with required fields for redirection
        context = {
            "project_name": project_name,
            "project_path": original_context.get("project_path"),
            "deploy_active": original_context.get("deploy_active", True),
            "timer_duration": original_context.get("timer_duration", 1800),
            "redirect_reason": "notification_task_switch"
        }
        
        logger.info("🔀 [NOTIFY] Processing task switch request with analytics tracking", 
                   task=task_data.get('text', ''), 
                   app=task_data.get('app', ''),
                   context_project_path=context.get("project_path"),
                   has_project_path=bool(context.get("project_path")),
                   session_id=session_id)
        
        # Import redirect module to handle app opening
        from . import redirect
        
        # Perform the redirection
        redirect_result = await redirect.app_redirector.redirect_to_task(task_data, context)
        
        # 📊 PHASE 2: Record task acceptance for session analytics
        if redirect_result.get("success", False):
            # Import timer module to record task acceptance
            from . import timer
            await timer.deploy_timer.record_task_acceptance_for_timer(project_name, 1)
            
            logger.info("✅ [NOTIFY] Switch button press and task acceptance recorded in analytics", 
                       project=project_name, session_id=session_id)
        
        # Notify frontend of redirection result
        if self.websocket_server:
            await self.websocket_server.broadcast({
                "type": "task",
                "event": "redirection_result",
                "data": {
                    "task": task_data,
                    "redirect_result": redirect_result,
                    "project_name": project_name,
                    "session_id": session_id,  # 📊 PHASE 2: Include session info
                    "switch_recorded": True,   # 📊 PHASE 2: Indicate Switch was recorded
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
        
        # IMPORTANT: Make a deep copy of the notification before removing it
        # Use deepcopy to ensure nested dicts (like 'data') are properly copied
        notification_copy = copy.deepcopy(notification)
        
        # Remove the current notification from active notifications
        # This allows the frontend window to close properly
        if notification["id"] in self.active_notifications:
            del self.active_notifications[notification["id"]]
            logger.debug("🗑️ [NOTIFY] Current notification removed for snoozing", 
                        notification_id=notification["id"])
        
        # Schedule re-notification using the copy
        snooze_task = asyncio.create_task(
            self._reschedule_notification(notification_copy, snooze_minutes * 60)
        )
        
        # Store snooze task for potential cancellation (store on copy)
        notification_copy["snooze_task"] = snooze_task

    async def _handle_start_new_timer(self, notification: Dict[str, Any], additional_data: Dict[str, Any]):
        """Handle starting a new timer from unified notification"""
        
        project_name = notification["data"]["project_name"]
        
        logger.info("⏰ [NOTIFY] Processing start new timer request", project=project_name)
        
        # Import timer module to start new timer
        from . import timer
        
        # Start a new timer (default 30 minutes)
        timer_duration = additional_data.get('duration', 1800)  # Default 30 minutes
        deploy_command = f"Manual timer for {project_name}"
        
        # Start the timer
        await timer.deploy_timer.start_timer(project_name, timer_duration, deploy_command)
        
        # Notify frontend of new timer
        if self.websocket_server:
            await self.websocket_server.broadcast({
                "type": "timer",
                "event": "timer_started",
                "data": {
                    "project_name": project_name,
                    "timer_duration": timer_duration,
                    "deploy_command": deploy_command,
                    "timestamp": datetime.now().isoformat()
                }
            })
        
        logger.info("✅ [NOTIFY] New timer started", project=project_name, duration=timer_duration)

    async def _reschedule_notification(self, notification: Dict[str, Any], delay_seconds: int):
        """Reschedule a notification after snooze period"""
        
        original_id = notification.get("id", "unknown")
        logger.info("⏱️ [NOTIFY] Starting snooze timer", 
                   original_notification_id=original_id, 
                   delay_seconds=delay_seconds,
                   notification_data_keys=list(notification.keys()))
        
        try:
            # Sleep for the snooze period
            await asyncio.sleep(delay_seconds)
            
            logger.info("⏰ [NOTIFY] Snooze period completed, preparing to resend", 
                       original_notification_id=original_id)
            
            # Re-send the notification with new ID and reminder text
            new_id = f"{notification['template']}_resend_{int(time.time() * 1000)}"
            notification["id"] = new_id
            notification["timestamp"] = datetime.now().isoformat()
            
            # Add reminder text if not already present
            if "(Reminder)" not in notification["message"]:
                notification["message"] += " (Reminder)"
            
            logger.info("🔄 [NOTIFY] Prepared rescheduled notification", 
                       new_notification_id=new_id,
                       original_id=original_id,
                       message=notification["message"][:100])
            
            # Store in active notifications
            self.active_notifications[notification["id"]] = notification
            logger.debug("💾 [NOTIFY] Stored rescheduled notification in active notifications")
            
            # Add to history
            self._add_to_history(notification)
            logger.debug("📚 [NOTIFY] Added rescheduled notification to history")
            
            # Check if websocket server is available
            if not self.websocket_server:
                logger.error("❌ [NOTIFY] WebSocket server not available for rescheduled notification!")
                return
            
            logger.info("📡 [NOTIFY] WebSocket server available, sending custom notification")
            
            # Send custom notification first (this is what creates the notification windows)
            await self._send_custom_notification(notification)
            logger.info("✅ [NOTIFY] Custom notification sent for rescheduled notification")
            
            # Send system notification if enabled (as fallback)
            if self.preferences["system_notifications_enabled"]:
                await self._send_system_notification(notification)
                logger.debug("📱 [NOTIFY] System notification sent for rescheduled notification")
            
            # Send in-app notification if enabled
            if self.preferences["in_app_modals_enabled"]:
                await self._send_in_app_notification(notification)
                logger.debug("🖥️ [NOTIFY] In-app notification sent for rescheduled notification")
            
            # Notify callbacks
            await self._notify_callbacks("notification_snoozed_resent", notification)
            logger.debug("🔔 [NOTIFY] Callbacks notified for rescheduled notification")
            
            logger.info("🎉 [NOTIFY] Snoozed notification re-sent successfully", 
                       notification_id=notification["id"],
                       original_id=original_id)
                       
        except asyncio.CancelledError:
            logger.warning("⚠️ [NOTIFY] Snooze task was cancelled", 
                          original_notification_id=original_id)
            raise
        except Exception as e:
            logger.error("❌ [NOTIFY] Error in reschedule notification", 
                        original_notification_id=original_id,
                        error=str(e),
                        error_type=type(e).__name__)
            # Re-raise the exception to see it in logs
            raise

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

    async def _record_interaction_analytics(self, notification: Dict[str, Any], action: str, 
                                           response_time_seconds: float, additional_data: Dict[str, Any]):
        """
        📊 ANALYTICS: Record user interaction with task suggestion notifications
        """
        try:
            # Only record analytics for task suggestion notifications
            notification_type = notification["data"].get("type")
            if notification_type not in ["task_suggestion", "unified_suggestion"]:
                return
            
            # Extract suggestion ID and project info
            suggestion_id = None
            project_name = notification["data"].get("project_name", "Unknown")
            
            # Check if task has suggestion_id from TaskSelector
            task_data = notification["data"].get("task", {})
            if task_data and "suggestion_id" in task_data:
                suggestion_id = task_data["suggestion_id"]
            else:
                # Fallback: try to extract from notification data
                suggestion_id = notification["data"].get("suggestion_id")
            
            if not suggestion_id:
                logger.warning("⚠️ [ANALYTICS] No suggestion_id found for interaction tracking")
                return
            
            # Map notification actions to analytics interaction types
            interaction_type_mapping = {
                "switch_now": "accepted",
                "switch_to_task": "accepted", 
                "snooze": "snoozed",
                "snooze_5min": "snoozed",
                "snooze_10min": "snoozed",
                "dismiss": "dismissed"
            }
            
            interaction_type = interaction_type_mapping.get(action, "ignored")
            
            # Record the interaction
            await self.analytics.record_user_interaction(
                suggestion_id=suggestion_id,
                interaction_type=interaction_type,
                response_time_seconds=response_time_seconds,
                project_name=project_name,
                additional_data=additional_data
            )
            
            logger.info("📊 [ANALYTICS] User interaction recorded", 
                       suggestion_id=suggestion_id,
                       interaction_type=interaction_type,
                       project=project_name,
                       response_time=f"{response_time_seconds:.1f}s")
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to record interaction", 
                        error=str(e), action=action)

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

    async def test_unified_notification(self) -> str:
        """Send a test unified notification combining timer and task info"""
        
        # Create test timer info
        test_timer_info = {
            "status": "running",
            "time_remaining_formatted": "22:15",
            "duration_seconds": 1800,
            "project_name": "TestProject"
        }
        
        # Create test task info
        test_task = {
            "text": "Write documentation for unified notifications",
            "app": "Bear",
            "tags": ["#writing", "#docs"],
            "estimated_duration": 25
        }
        
        test_context = {
            "deploy_active": True,
            "timer_duration": 1800
        }
        
        logger.info("🧪 [NOTIFY] Sending test unified notification")
        return await self.notify_unified_suggestion(
            "TestProject",
            timer_info=test_timer_info,
            task=test_task,
            context=test_context
        )

# Global instance
notification_manager = NotificationManager() 