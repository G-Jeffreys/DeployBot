#!/usr/bin/env python3
"""
DeployBot LangGraph Backend with WebSocket Server

This module implements the core LangGraph workflow for DeployBot,
including deploy detection, task selection, and WebSocket communication
with the Electron frontend.
"""

import asyncio
import json
import logging
import os
import sys
import time
import websockets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableLambda
import structlog

# Import Week 2 modules
from deploy_wrapper_setup import deploy_wrapper_manager
from monitor import deploy_monitor
from timer import deploy_timer
from project_manager import project_manager
from logger import activity_logger

# Import Week 3 modules
from tasks import task_selector
from redirect import app_redirector
from notification import notification_manager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="ISO"),
        structlog.dev.ConsoleRenderer(colors=True)
    ],
    wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO level
    logger_factory=structlog.WriteLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Global state for the DeployBot system
class DeployBotState:
    """Shared state for the DeployBot LangGraph system"""
    
    def __init__(self):
        self.monitoring_active: bool = False
        self.current_project: Optional[str] = None
        self.deploy_detected: bool = False
        self.selected_task: Optional[Dict[str, Any]] = None
        self.timer_active: bool = False
        self.websocket_clients: set = set()
        self.last_deploy_time: Optional[datetime] = None
        
        logger.info("🤖 [STATE] DeployBot state initialized")

# Global state instance
deploybot_state = DeployBotState()

class WebSocketServer:
    """WebSocket server for communication with Electron frontend"""
    
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        
        # Initialize Week 2 modules
        self.initialize_modules()
    
    def initialize_modules(self):
        """Initialize and configure Week 2 & 3 modules"""
        logger.info("🔧 [INIT] Initializing Week 2 & 3 modules...")
        
        # Set up deploy event callbacks
        deploy_monitor.set_deploy_detected_callback(self.on_deploy_detected)
        deploy_monitor.set_deploy_completed_callback(self.on_deploy_completed)
        
        # Connect timer to WebSocket for real-time updates  
        deploy_timer.set_websocket_server(self)
        
        # Week 3: Connect notification manager to WebSocket
        notification_manager.set_websocket_server(self)
        
        logger.info("✅ [INIT] Week 2 & 3 modules initialized")
    
    async def on_deploy_detected(self, project_name: str, deploy_command: str, project_path: str):
        """Called when a deploy is detected - Week 3 enhanced workflow"""
        logger.info("🚀 [DEPLOY] Deploy detected", project=project_name, command=deploy_command)
        
        # Update state
        deploybot_state.deploy_detected = True
        deploybot_state.current_project = project_name
        
        # *** BRING DEPLOYBOT TO FOCUS ***
        logger.info("🔍 [DEPLOY] Bringing DeployBot window to focus for deployment")
        await self._focus_window()
        
        # Log the event
        await activity_logger.log_deploy_detected(project_name, deploy_command, project_path)
        
        # Start timer (default 30 minutes)
        timer_duration = 1800  # 30 minutes
        await deploy_timer.start_timer(project_name, timer_duration, deploy_command)
        
        # Week 3: Check if tasks are available to decide notification strategy
        grace_period = notification_manager.preferences["grace_period"]  # 0 seconds now (immediate)
        
        # Quick check for task availability
        tasks_available = await self._check_tasks_available(project_path)
        
        if tasks_available:
            # Tasks available → Only send unified notification after grace period
            logger.info("🎯 [DEPLOY] Tasks available - scheduling unified notification only", 
                       grace_period=grace_period)
            asyncio.create_task(self._schedule_unified_notification(
                project_name, project_path, deploy_command, grace_period, timer_duration
            ))
        else:
            # No tasks → Send immediate timer notification as fallback
            logger.info("⏰ [DEPLOY] No tasks available - sending timer notification immediately")
            await notification_manager.notify_deploy_detected(project_name, deploy_command, timer_duration)
        
        # Notify frontend
        await self.broadcast({
            "type": "deploy",
            "event": "deploy_detected",
            "data": {
                "project": project_name,
                "command": deploy_command,
                "timer_duration": timer_duration,
                "grace_period": grace_period,
                "has_tasks": tasks_available,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def _check_tasks_available(self, project_path: str) -> bool:
        """Quick check if tasks are available for this project"""
        try:
            # Load tasks from TODO.md using the global task_selector
            todo_file = Path(project_path) / "TODO.md"
            if not todo_file.exists():
                logger.info("📋 [DEPLOY] No TODO.md file found", file_path=str(todo_file))
                return False
            
            logger.info("📋 [DEPLOY] Checking tasks in TODO.md", file_path=str(todo_file))
            
            # Use the global task_selector instance (same as unified notification workflow)
            available_tasks = await task_selector.parse_todo_file(todo_file)
            
            # Filter to pending tasks only
            pending_tasks = [task for task in available_tasks if not task['completed']]
            
            logger.info("📋 [DEPLOY] Task availability check", 
                        total_tasks=len(available_tasks),
                        pending_tasks=len(pending_tasks),
                        file_exists=todo_file.exists(),
                        file_size=todo_file.stat().st_size if todo_file.exists() else 0)
            
            return len(pending_tasks) > 0
            
        except Exception as e:
            logger.error("❌ [DEPLOY] Failed to check task availability", error=str(e), file_path=str(project_path))
            import traceback
            logger.error("❌ [DEPLOY] Full traceback", traceback=traceback.format_exc())
            return False

    async def _schedule_unified_notification(self, project_name: str, project_path: str, 
                                          deploy_command: str, grace_period: int, timer_duration: int):
        """Schedule unified notification with timer + task info after grace period"""
        logger.info("🎯⏰ [WORKFLOW] Scheduling unified notification", 
                   project=project_name, grace_period=grace_period)
        
        # Wait for grace period
        await asyncio.sleep(grace_period)
        
        # REMOVED: The backwards cancellation logic that was preventing notifications
        # The deploy command completing is EXACTLY when we want to show notifications
        # for the cloud propagation period (Firebase, Vercel, etc. take 10-30 minutes)
        
        # *** BRING DEPLOYBOT TO FOCUS AGAIN FOR UNIFIED NOTIFICATION ***
        logger.info("🔍 [WORKFLOW] Bringing DeployBot window to focus for unified notification")
        await self._focus_window()
        
        # Get timer status
        timer_status = deploy_timer.get_timer_status(project_name)
        
        # Week 3: Select best alternative task
        context = {
            "project_name": project_name,
            "project_path": project_path,
            "deploy_command": deploy_command,
            "deploy_active": True,  # Deploy may be done locally, but cloud propagation is active
            "timer_duration": timer_duration,
            "use_llm": True
        }
        
        try:
            selected_task = await task_selector.select_best_task(project_path, context)
            
            if selected_task:
                # Store selected task in state
                deploybot_state.selected_task = selected_task
                
                # Log task selection
                await activity_logger.log_task_selected(
                    project_name, 
                    selected_task['text'], 
                    selected_task.get('tags', []),
                    selected_task.get('app', 'Unknown'),
                    project_path
                )
                
                # Send unified notification with both timer and task info
                notification_id = await notification_manager.notify_unified_suggestion(
                    project_name, 
                    timer_info=timer_status,
                    task=selected_task, 
                    context=context
                )
                
                # Notify frontend
                await self.broadcast({
                    "type": "task",
                    "event": "unified_suggested",
                    "data": {
                        "project": project_name,
                        "task": selected_task,
                        "timer_info": timer_status,
                        "context": context,
                        "notification_id": notification_id,
                        "timestamp": datetime.now().isoformat()
                    }
                })
                
                logger.info("✅ [WORKFLOW] Unified notification sent successfully", 
                           task=selected_task['text'], app=selected_task.get('app'))
                
            else:
                # No tasks found - send timer notification as fallback
                logger.warning("⚠️ [WORKFLOW] No suitable tasks found - sending timer notification fallback")
                await notification_manager.notify_deploy_detected(project_name, deploy_command, timer_duration)
                
        except Exception as e:
            logger.error("❌ [WORKFLOW] Error in unified notification workflow", error=str(e))
            # Fallback to timer notification on error
            await notification_manager.notify_deploy_detected(project_name, deploy_command, timer_duration)

    async def _schedule_task_suggestion(self, project_name: str, project_path: str, deploy_command: str, grace_period: int):
        """DEPRECATED: Schedule task suggestion after grace period - replaced by unified notifications"""
        logger.warning("⚠️ [WORKFLOW] Using deprecated task suggestion method - should use unified notifications")
        
        # Forward to unified notification for backward compatibility
        await self._schedule_unified_notification(project_name, project_path, deploy_command, grace_period, 1800)

    async def on_deploy_completed(self, project_name: str, deploy_command: str, exit_code: int, project_path: str):
        """Called when a deploy completes"""
        logger.info("✅ [DEPLOY] Deploy completed", project=project_name, exit_code=exit_code)
        
        # Update state
        deploybot_state.deploy_detected = False
        
        # Log the event
        await activity_logger.log_deploy_completed(project_name, deploy_command, exit_code, project_path)
        
        # DO NOT stop the timer - it should continue running for the full duration
        # to enforce waiting period during cloud propagation
        logger.info("⏰ [DEPLOY] Timer continues running during propagation period", project=project_name)
        
        # Notify frontend
        await self.broadcast({
            "type": "deploy",
            "event": "deploy_completed", 
            "data": {
                "project": project_name,
                "command": deploy_command,
                "exit_code": exit_code,
                "success": exit_code == 0,
                "timestamp": datetime.now().isoformat()
            }
        })

    async def register_client(self, websocket):
        """Register a new WebSocket client"""
        self.clients.add(websocket)
        deploybot_state.websocket_clients.add(websocket)
        logger.info("🔌 [WEBSOCKET] Client connected", total_clients=len(self.clients))
        
        # Send welcome message with current state
        await self.send_to_client(websocket, {
            "type": "system",
            "event": "connected",
            "data": {
                "monitoring_active": deploybot_state.monitoring_active,
                "current_project": deploybot_state.current_project,
                "timestamp": datetime.now().isoformat()
            }
        })

    async def unregister_client(self, websocket):
        """Unregister a WebSocket client"""
        self.clients.discard(websocket)
        deploybot_state.websocket_clients.discard(websocket)
        logger.info("🔌 [WEBSOCKET] Client disconnected", total_clients=len(self.clients))

    async def send_to_client(self, websocket, message):
        """Send message to a specific client"""
        try:
            await websocket.send(json.dumps(message))
            logger.debug("📤 [WEBSOCKET] Message sent to client", message_type=message.get("type"))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("🔌 [WEBSOCKET] Failed to send message - client disconnected")
            await self.unregister_client(websocket)
        except Exception as e:
            logger.error("❌ [WEBSOCKET] Error sending message", error=str(e))

    async def broadcast(self, message):
        """Broadcast message to all connected clients"""
        if not self.clients:
            logger.debug("📡 [WEBSOCKET] No clients connected for broadcast")
            return
            
        logger.info("📡 [WEBSOCKET] Broadcasting message", 
                   message_type=message.get("type"), 
                   client_count=len(self.clients))
        
        # Create a copy of clients to avoid modification during iteration
        clients_copy = self.clients.copy()
        for client in clients_copy:
            await self.send_to_client(client, message)

    async def handle_client_message(self, websocket, message_str):
        """Handle incoming messages from clients"""
        try:
            message = json.loads(message_str)
            command = message.get("command")
            data = message.get("data", {})
            
            logger.info("📥 [WEBSOCKET] Received command", command=command, data=data)
            
            # Route command to appropriate handler
            response = await self.process_command(command, data)
            
            # Send response back to client
            await self.send_to_client(websocket, {
                "type": "response",
                "command": command,
                "data": response,
                "timestamp": datetime.now().isoformat()
            })
            
        except json.JSONDecodeError as e:
            logger.error("❌ [WEBSOCKET] Invalid JSON received", error=str(e))
            await self.send_to_client(websocket, {
                "type": "error",
                "message": "Invalid JSON format",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error("❌ [WEBSOCKET] Error handling message", error=str(e))
            await self.send_to_client(websocket, {
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })

    async def process_command(self, command: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process commands from the frontend"""
        logger.info("⚙️ [COMMAND] Processing command", command=command)
        
        try:
            if command == "ping":
                return {
                    "success": True,
                    "message": "pong",
                    "timestamp": datetime.now().isoformat(),
                    "server_status": "running"
                }
                
            elif command == "status":
                # Get real status from all modules
                monitor_status = deploy_monitor.get_monitoring_status()
                timer_status = deploy_timer.get_all_timers_status()
                
                return {
                    "success": True,
                    "monitoring_active": monitor_status["monitoring_active"],
                    "current_project": deploybot_state.current_project,
                    "deploy_detected": deploybot_state.deploy_detected,
                    "timer_active": timer_status["active_timer_count"] > 0,
                    "client_count": len(self.clients),
                    "monitor_status": monitor_status,
                    "timer_status": timer_status
                }
                
            elif command == "start-monitoring":
                # Use real monitoring module
                success = await deploy_monitor.start_monitoring()
                
                if success:
                    deploybot_state.monitoring_active = True
                    await activity_logger.log_monitoring_started()
                    
                    # Broadcast status change to all clients
                    await self.broadcast({
                        "type": "system",
                        "event": "monitoring_started",
                        "data": {"monitoring_active": True}
                    })
                
                return {"success": success, "message": "Deploy monitoring started" if success else "Failed to start monitoring"}
                
            elif command == "stop-monitoring":
                # Use real monitoring module
                success = await deploy_monitor.stop_monitoring()
                
                if success:
                    deploybot_state.monitoring_active = False
                    await activity_logger.log_monitoring_stopped()
                    
                    await self.broadcast({
                        "type": "system", 
                        "event": "monitoring_stopped",
                        "data": {"monitoring_active": False}
                    })
                
                return {"success": success, "message": "Deploy monitoring stopped" if success else "Failed to stop monitoring"}
                
            elif command == "check-monitor":
                status = deploy_monitor.get_monitoring_status()
                return {
                    "success": True,
                    "monitoring_active": status["monitoring_active"],
                    "monitored_projects": status["monitored_projects"],
                    "last_check": datetime.now().isoformat()
                }
                
            elif command == "direct-add-to-monitoring":
                project_name = data.get("project_name")
                project_path = data.get("project_path")
                
                if project_name and project_path:
                    logger.info("🔧 [DIRECT] Adding project directly to monitoring", 
                               project_name=project_name, project_path=project_path)
                    
                    success = await deploy_monitor.add_project(project_name, project_path)
                    
                    if success:
                        deploybot_state.current_project = project_name
                        logger.info("✅ [DIRECT] Project added to monitoring successfully", 
                                   project_name=project_name)
                        return {
                            "success": True, 
                            "message": f"Project '{project_name}' added to monitoring",
                            "project_name": project_name,
                            "project_path": project_path
                        }
                    else:
                        logger.error("❌ [DIRECT] Failed to add project to monitoring", 
                                    project_name=project_name)
                        return {"success": False, "message": f"Failed to add project '{project_name}' to monitoring"}
                else:
                    return {"success": False, "message": "Project name and path required"}
                
            # Project Management Commands
            elif command == "project-create":
                result = await project_manager.create_project(data)
                if result["success"]:
                    await activity_logger.log_project_created(
                        result["project"]["name"], 
                        result["project"]["path"]
                    )
                return result
                
            elif command == "project-list":
                return await project_manager.list_projects()
                
            elif command == "project-delete":
                project_path = data.get("path")
                if project_path:
                    result = await project_manager.delete_project(project_path)
                    if result["success"]:
                        await activity_logger.log_project_deleted(data.get("name", "Unknown"))
                    return result
                else:
                    return {"success": False, "message": "Project path required"}
                    
            elif command == "project-load":
                project_path = data.get("path")
                if project_path:
                    result = await project_manager.load_project(project_path)
                    
                    # Add project to monitoring if load successful
                    if result["success"]:
                        project_data = result["project"]
                        await deploy_monitor.add_project(project_data["name"], project_data["path"])
                        deploybot_state.current_project = project_data["name"]
                    
                    return result
                else:
                    return {"success": False, "message": "Project path required"}
                
            # Deploy Wrapper Management
            elif command == "wrapper-status":
                return await deploy_wrapper_manager.check_installation_status()
                
            elif command == "wrapper-install":
                result = await deploy_wrapper_manager.install_wrapper()
                await activity_logger.log_wrapper_installed(
                    result["success"], 
                    result.get("wrapper_path")
                )
                return result
                
            elif command == "wrapper-uninstall":
                return await deploy_wrapper_manager.uninstall_wrapper()
                
            # Timer Management
            elif command == "timer-start":
                project_name = data.get("project_name", deploybot_state.current_project)
                duration = data.get("duration_seconds", 1800)
                deploy_command = data.get("deploy_command")
                
                if project_name:
                    success = await deploy_timer.start_timer(project_name, duration, deploy_command)
                    if success:
                        await activity_logger.log_timer_started(project_name, duration, deploy_command)
                    return {"success": success, "project": project_name, "duration": duration}
                else:
                    return {"success": False, "message": "No project specified"}
                    
            elif command == "timer-stop":
                project_name = data.get("project_name", deploybot_state.current_project)
                if project_name:
                    success = await deploy_timer.stop_timer(project_name, "manual")
                    if success:
                        await activity_logger.log_timer_stopped(project_name, "manual")
                    return {"success": success, "project": project_name}
                else:
                    return {"success": False, "message": "No project specified"}
                    
            elif command == "timer-status":
                project_name = data.get("project_name", deploybot_state.current_project)
                if project_name:
                    status = deploy_timer.get_timer_status(project_name)
                    return {"success": True, "timer_status": status}
                else:
                    return {"success": False, "message": "No project specified"}
                
            elif command == "test-task-selection":
                project_name = data.get("projectName", "TestProject")
                selected_task = await run_task_selection_test(project_name)
                
                return {
                    "success": True,
                    "selected_task": selected_task,
                    "project": project_name
                }
            
            # Week 3: Comprehensive workflow test
            elif command == "test-week3-workflow":
                project_name = data.get("project_name", "DemoProject")
                
                try:
                    logger.info("🧪 [TEST] Starting Week 3 comprehensive workflow test")
                    
                    # Test 1: Task selection
                    projects_root = Path(__file__).parent.parent / "projects"
                    project_path = str(projects_root / project_name)
                    
                    context = {
                        "project_name": project_name,
                        "project_path": project_path,
                        "deploy_active": True,
                        "timer_duration": 1800,
                        "use_llm": False  # Use heuristic for testing
                    }
                    
                    selected_task = await task_selector.select_best_task(project_path, context)
                    
                    # Test 2: Notification system
                    notification_id = None
                    if selected_task:
                        notification_id = await notification_manager.notify_task_suggestion(
                            project_name, selected_task, context
                        )
                    
                    # Test 3: App redirection (dry run)
                    redirect_result = None
                    if selected_task:
                        redirect_result = await app_redirector.redirect_to_task(selected_task, context)
                    
                    # Test 4: Get task statistics
                    task_stats = await task_selector.get_task_statistics(project_path)
                    
                    return {
                        "success": True,
                        "tests": {
                            "task_selection": {
                                "success": selected_task is not None,
                                "selected_task": selected_task
                            },
                            "notification": {
                                "success": notification_id is not None,
                                "notification_id": notification_id
                            },
                            "redirection": {
                                "success": redirect_result is not None and redirect_result.get("success", False),
                                "redirect_result": redirect_result
                            },
                            "task_statistics": {
                                "success": "error" not in task_stats,
                                "stats": task_stats
                            }
                        },
                        "project_name": project_name,
                        "message": "Week 3 workflow test completed"
                    }
                    
                except Exception as e:
                    logger.error("❌ [TEST] Week 3 workflow test failed", error=str(e))
                    return {
                        "success": False,
                        "error": str(e),
                        "message": "Week 3 workflow test failed"
                    }
                
            elif command == "open-app":
                app_name = data.get("app")
                task_text = data.get("task")
                project_name = data.get("project", deploybot_state.current_project)
                
                if app_name:
                    success = await open_application(app_name, task_text or "")
                    if success and project_name:
                        await activity_logger.log_app_opened(project_name, app_name, task_text)
                    return {
                        "success": success,
                        "app": app_name,
                        "task": task_text,
                        "message": f"{'Opened' if success else 'Failed to open'} {app_name}"
                    }
                else:
                    return {"success": False, "message": "No app specified"}
            
            # Week 4: Testing and debugging commands
            elif command == "test-snooze-quick":
                # Test snooze functionality with 10 second delay for quick testing
                test_notification = {
                    "id": f"test_snooze_{int(time.time() * 1000)}",
                    "template": "task_suggestion", 
                    "title": "🧪 Test Snooze Notification",
                    "message": "This notification will snooze for 10 seconds",
                    "data": {
                        "type": "task_suggestion",
                        "project_name": "TestProject",
                        "task": {
                            "text": "Test snooze functionality", 
                            "app": "Bear",
                            "tags": ["#test"],
                            "estimated_duration": 5
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info("🧪 [TEST] Creating test notification for snooze testing")
                
                # Add to active notifications
                notification_manager.active_notifications[test_notification["id"]] = test_notification
                
                # Test snooze with 10 second delay
                await notification_manager._handle_snooze(
                    test_notification, 
                    "snooze", 
                    {"snooze_minutes": 0.17}  # 10 seconds = 0.17 minutes
                )
                
                return {
                    "success": True,
                    "message": "Test snooze triggered - should reappear in 10 seconds",
                    "notification_id": test_notification["id"]
                }
            
            elif command == "test-bear-redirection":
                # Test Bear redirection specifically
                test_task = {
                    "text": data.get("task_text", "Write documentation for unified notifications"),
                    "app": "Bear",
                    "tags": ["#writing", "#docs"],
                    "estimated_duration": 25
                }
                
                test_context = {
                    "project_name": data.get("project_name", "DeployBot"),
                    "deploy_active": True,
                    "timer_duration": 1800
                }
                
                logger.info("🧪 [TEST] Testing Bear redirection", task=test_task['text'])
                
                try:
                    redirect_result = await app_redirector.redirect_to_task(test_task, test_context)
                    
                    return {
                        "success": redirect_result.get("success", False),
                        "test_type": "bear_redirection",
                        "redirect_result": redirect_result,
                        "task": test_task,
                        "context": test_context,
                        "message": f"Bear redirection test {'successful' if redirect_result.get('success') else 'failed'}"
                    }
                except Exception as e:
                    logger.error("❌ [TEST] Bear redirection test failed", error=str(e))
                    return {
                        "success": False,
                        "test_type": "bear_redirection",
                        "error": str(e),
                        "message": "Bear redirection test failed with exception"
                    }
            
            # Week 3: Enhanced task redirection
            elif command == "redirect-to-task":
                task_data = data.get("task")
                context = data.get("context", {})
                
                if task_data:
                    try:
                        redirect_result = await app_redirector.redirect_to_task(task_data, context)
                        
                        # Log successful redirection
                        if redirect_result.get("success") and context.get("project_name"):
                            await activity_logger.log_app_opened(
                                context["project_name"],
                                redirect_result.get("app", task_data.get("app", "Unknown")),
                                task_data.get("text", "")
                            )
                        
                        return {
                            "success": redirect_result.get("success", False),
                            "redirect_result": redirect_result,
                            "task": task_data,
                            "message": "Task redirection completed"
                        }
                    except Exception as e:
                        logger.error("❌ [REDIRECT] Task redirection failed", error=str(e))
                        return {"success": False, "error": str(e), "message": "Task redirection failed"}
                else:
                    return {"success": False, "message": "No task data provided"}
            
            # Week 3: Notification response handling
            elif command == "notification-response":
                notification_id = data.get("notification_id")
                action = data.get("action")
                additional_data = data.get("additional_data", {})
                
                if notification_id and action:
                    try:
                        success = await notification_manager.handle_notification_response(
                            notification_id, action, additional_data
                        )
                        return {
                            "success": success,
                            "notification_id": notification_id,
                            "action": action,
                            "message": "Notification response processed"
                        }
                    except Exception as e:
                        logger.error("❌ [NOTIFY] Notification response failed", error=str(e))
                        return {"success": False, "error": str(e), "message": "Notification response failed"}
                else:
                    return {"success": False, "message": "Missing notification_id or action"}
            
            # Week 4: Notification action handling (alias for notification-response)
            elif command == "notification-action":
                notification_id = data.get("notification_id")
                action = data.get("action")
                # Handle nested data structure from frontend
                task_data = data.get("data", {})
                
                logger.info("🔔 [COMMAND] Processing notification action", 
                           notification_id=notification_id, 
                           action=action,
                           has_task_data=bool(task_data))
                
                if notification_id and action:
                    try:
                        success = await notification_manager.handle_notification_response(
                            notification_id, action, task_data
                        )
                        return {
                            "success": success,
                            "notification_id": notification_id,
                            "action": action,
                            "message": "Notification action processed successfully"
                        }
                    except Exception as e:
                        logger.error("❌ [COMMAND] Notification action failed", 
                                   notification_id=notification_id, 
                                   action=action, 
                                   error=str(e))
                        return {
                            "success": False, 
                            "error": str(e), 
                            "message": "Notification action processing failed"
                        }
                else:
                    return {
                        "success": False, 
                        "message": "Missing notification_id or action parameters"
                    }
            
            # Week 3: Get task suggestions
            elif command == "get-task-suggestions":
                project_path = data.get("project_path")
                context = data.get("context", {})
                
                if project_path:
                    try:
                        task = await task_selector.select_best_task(project_path, context)
                        return {
                            "success": True,
                            "task": task,
                            "project_path": project_path,
                            "message": "Task suggestion retrieved"
                        }
                    except Exception as e:
                        logger.error("❌ [TASKS] Task suggestion failed", error=str(e))
                        return {"success": False, "error": str(e), "message": "Task suggestion failed"}
                else:
                    return {"success": False, "message": "No project path provided"}
                
            # Deploy Simulation for Testing
            elif command == "simulate-deploy":
                project_name = data.get("project_name", deploybot_state.current_project)
                command_str = data.get("command", "firebase deploy --test")
                
                if project_name:
                    success = await deploy_monitor.simulate_deploy_event(project_name, command_str)
                    return {"success": success, "project": project_name, "command": command_str}
                else:
                    return {"success": False, "message": "No project specified"}
            
            # Activity Logs Management
            elif command == "get-logs":
                log_type = data.get("type", "activity")
                project_name = data.get("project_name")
                limit = data.get("limit", 100)
                
                try:
                    # For now, return mock activity logs since we don't have a persistent log storage
                    # In a real implementation, you'd query from activity_logger or a database
                    mock_logs = [
                        {
                            "id": 1,
                            "timestamp": datetime.now().isoformat(),
                            "type": "system",
                            "event": "backend_connected",
                            "message": "DeployBot backend connected successfully",
                            "project": deploybot_state.current_project,
                            "data": {"monitoring_active": deploybot_state.monitoring_active}
                        },
                        {
                            "id": 2,
                            "timestamp": (datetime.now() - timedelta(minutes=5)).isoformat(),
                            "type": "project",
                            "event": "project_loaded",
                            "message": f"Project {deploybot_state.current_project or 'DemoProject'} loaded successfully",
                            "project": deploybot_state.current_project or "DemoProject",
                            "data": {"project_name": deploybot_state.current_project or "DemoProject"}
                        }
                    ]
                    
                    # Filter by project if specified
                    if project_name:
                        filtered_logs = [log for log in mock_logs if log.get("project") == project_name]
                    else:
                        filtered_logs = mock_logs
                    
                    # Limit results
                    limited_logs = filtered_logs[:limit]
                    
                    return {
                        "success": True,
                        "logs": limited_logs,
                        "total_count": len(filtered_logs),
                        "log_type": log_type,
                        "project_filter": project_name
                    }
                    
                except Exception as e:
                    logger.error("❌ [LOGS] Failed to retrieve logs", error=str(e))
                    return {"success": False, "error": str(e), "message": "Failed to retrieve logs"}
                    
            else:
                logger.warning("❓ [COMMAND] Unknown command received", command=command)
                return {"success": False, "message": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error("❌ [COMMAND] Error processing command", command=command, error=str(e))
            return {"success": False, "message": f"Error processing command: {str(e)}"}

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info("🚀 [WEBSOCKET] Starting WebSocket server", host=self.host, port=self.port)
        
        async def handle_client(websocket):
            await self.register_client(websocket)
            try:
                async for message in websocket:
                    await self.handle_client_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                logger.info("🔌 [WEBSOCKET] Client connection closed normally")
            except Exception as e:
                logger.error("❌ [WEBSOCKET] Error in client handler", error=str(e))
            finally:
                await self.unregister_client(websocket)

        return await websockets.serve(handle_client, self.host, self.port)

    async def _focus_window(self):
        """Focus the DeployBot window"""
        try:
            # Send window focus command to frontend
            await self.broadcast({
                "type": "system", 
                "event": "focus_window",
                "data": {
                    "action": "focus",
                    "timestamp": datetime.now().isoformat()
                }
            })
            logger.info("✅ [FOCUS] Window focus request sent to frontend")
        except Exception as e:
            logger.error("❌ [FOCUS] Failed to focus window", error=str(e))

# LangGraph implementation functions
async def detect_deploy(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: Detect deployment events"""
    logger.info("🔍 [LANGGRAPH] Checking for deploy events...")
    
    # For now, this is a stub - in Week 2 we'll implement actual log monitoring
    # Simulate deploy detection for testing
    if deploybot_state.monitoring_active:
        logger.info("✅ [LANGGRAPH] Deploy detection active - monitoring for events")
        state["deploy_status"] = "monitoring"
    else:
        logger.info("😴 [LANGGRAPH] Deploy detection inactive")
        state["deploy_status"] = "inactive"
    
    return state

async def select_task(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: Select alternative task based on context - Week 3 Enhanced"""
    logger.info("🎯 [LANGGRAPH] Selecting alternative task using Week 3 logic...")
    
    project_name = state.get("project") or deploybot_state.current_project
    if not project_name:
        logger.warning("⚠️ [LANGGRAPH] No project available for task selection")
        state["selected_task"] = None
        return state
    
    # Get project path
    projects_root = Path(__file__).parent.parent / "projects"
    project_path = str(projects_root / project_name)
    
    # Prepare context for task selection
    context = {
        "project_name": project_name,
        "project_path": project_path,
        "deploy_active": deploybot_state.deploy_detected,
        "timer_duration": 1800,  # 30 minutes
        "use_llm": True
    }
    
    try:
        # Week 3: Use real task selector
        selected_task = await task_selector.select_best_task(project_path, context)
        
        if selected_task:
            state["selected_task"] = selected_task
            deploybot_state.selected_task = selected_task
            logger.info("✅ [LANGGRAPH] Task selected using Week 3 logic", 
                       task=selected_task["text"], 
                       app=selected_task.get("app", "Unknown"),
                       method="real_selection")
        else:
            logger.warning("⚠️ [LANGGRAPH] No suitable tasks found")
            state["selected_task"] = None
            
    except Exception as e:
        logger.error("❌ [LANGGRAPH] Error in task selection", error=str(e))
        # Fallback to simple mock for testing
        fallback_task = {"text": "Work on documentation", "tags": ["#writing"], "app": "Bear"}
        state["selected_task"] = fallback_task
        deploybot_state.selected_task = fallback_task
        logger.info("🔄 [LANGGRAPH] Using fallback task due to error")
    
    return state

async def start_timer(state: Dict[str, Any]) -> Dict[str, Any]:
    """LangGraph node: Start deployment timer"""
    logger.info("⏰ [LANGGRAPH] Starting deployment timer...")
    
    deploybot_state.timer_active = True
    deploybot_state.last_deploy_time = datetime.now()
    state["timer_started"] = True
    
    logger.info("✅ [LANGGRAPH] Timer started successfully")
    return state

# Helper functions
async def run_task_selection_test(project_name: str) -> Optional[Dict[str, Any]]:
    """Test the task selection logic"""
    logger.info("🧪 [TEST] Running task selection test", project=project_name)
    
    mock_state = {"project": project_name}
    result_state = await select_task(mock_state)
    
    return result_state.get("selected_task")

async def open_application(app_name: str, task_text: Optional[str] = None) -> bool:
    """Open the specified application (macOS)"""
    logger.info("📱 [APP] Opening application", app=app_name, task=task_text)
    
    try:
        # Use macOS 'open' command to launch applications
        import subprocess
        result = subprocess.run(['open', '-a', app_name], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info("✅ [APP] Application opened successfully", app=app_name)
            return True
        else:
            logger.error("❌ [APP] Failed to open application", 
                        app=app_name, error=result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ [APP] Timeout opening application", app=app_name)
        return False
    except Exception as e:
        logger.error("❌ [APP] Error opening application", app=app_name, error=str(e))
        return False

async def deploy_monitoring_loop():
    """Background task for monitoring deploy events"""
    logger.info("🔄 [MONITOR] Starting deploy monitoring loop...")
    
    while True:
        try:
            if deploybot_state.monitoring_active:
                # Check for deploy events (stub for Week 1)
                # In Week 2, this will read from the deploy log file
                logger.debug("👀 [MONITOR] Checking for deploy events...")
                
                # Simulate occasional deploy detection for testing
                if deploybot_state.monitoring_active and not deploybot_state.deploy_detected:
                    # This is just for demonstration - real logic comes in Week 2
                    pass
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            logger.error("❌ [MONITOR] Error in monitoring loop", error=str(e))
            await asyncio.sleep(10)  # Wait longer on errors

async def main():
    """Main entry point for the DeployBot backend"""
    logger.info("🎉 [MAIN] DeployBot LangGraph backend starting...")
    
    # Initialize Week 2 modules first
    logger.info("🔧 [MAIN] Starting Week 2 module initialization...")
    
    # Start activity logger
    await activity_logger.start_processing()
    logger.info("✅ [MAIN] Activity logger started")
    
    # Initialize WebSocket server
    ws_server = WebSocketServer()
    
    # Start WebSocket server
    server = await ws_server.start_server()
    logger.info("✅ [MAIN] WebSocket server started successfully")
    
    # 🔧 AUTO-START DEPLOY MONITORING
    logger.info("🚀 [MAIN] Auto-starting deploy monitoring...")
    try:
        monitor_success = await deploy_monitor.start_monitoring()
        if monitor_success:
            deploybot_state.monitoring_active = True
            await activity_logger.log_monitoring_started()
            logger.info("✅ [MAIN] Deploy monitoring auto-started successfully")
        else:
            logger.warning("⚠️ [MAIN] Failed to auto-start deploy monitoring")
    except Exception as e:
        logger.error("❌ [MAIN] Error auto-starting deploy monitoring", error=str(e))
    
    try:
        # Keep the server running
        logger.info("🚀 [MAIN] DeployBot backend is ready and waiting for connections...")
        await server.wait_closed()
    except KeyboardInterrupt:
        logger.info("🛑 [MAIN] Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error("❌ [MAIN] Fatal error in main loop", error=str(e))
    finally:
        # Cleanup
        logger.info("🧹 [MAIN] Cleaning up resources...")
        
        # Stop Week 2 modules
        await deploy_monitor.stop_monitoring()
        await activity_logger.stop_processing()
        
        server.close()
        await server.wait_closed()
        logger.info("✅ [MAIN] DeployBot backend shut down complete")

if __name__ == "__main__":
    print("🤖 DeployBot LangGraph Backend")
    print("=" * 40)
    print("🐍 Python LangGraph backend with WebSocket server")
    print("🔌 Listening for Electron frontend connections...")
    print("📡 WebSocket server starting on ws://localhost:8765")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down DeployBot backend...")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1) 