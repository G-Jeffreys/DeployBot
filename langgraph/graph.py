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
from datetime import datetime
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
        self.monitoring_active = False
        self.current_project = None
        self.deploy_detected = False
        self.selected_task = None
        self.timer_active = False
        self.websocket_clients = set()
        self.last_deploy_time = None
        
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
        """Initialize and configure Week 2 modules"""
        logger.info("🔧 [INIT] Initializing Week 2 modules...")
        
        # Set up deploy event callbacks
        deploy_monitor.set_deploy_detected_callback(self.on_deploy_detected)
        deploy_monitor.set_deploy_completed_callback(self.on_deploy_completed)
        
        # Connect timer to WebSocket for real-time updates  
        deploy_timer.set_websocket_server(self)
        
        logger.info("✅ [INIT] Week 2 modules initialized")
    
    async def on_deploy_detected(self, project_name: str, deploy_command: str, project_path: str):
        """Called when a deploy is detected"""
        logger.info("🚀 [DEPLOY] Deploy detected", project=project_name, command=deploy_command)
        
        # Update state
        deploybot_state.deploy_detected = True
        deploybot_state.current_project = project_name
        
        # Log the event
        await activity_logger.log_deploy_detected(project_name, deploy_command, project_path)
        
        # Start timer (default 30 minutes)
        timer_duration = 1800  # 30 minutes
        await deploy_timer.start_timer(project_name, timer_duration, deploy_command)
        
        # Notify frontend
        await self.broadcast({
            "type": "deploy",
            "event": "deploy_detected",
            "data": {
                "project": project_name,
                "command": deploy_command,
                "timer_duration": timer_duration,
                "timestamp": datetime.now().isoformat()
            }
        })
    
    async def on_deploy_completed(self, project_name: str, deploy_command: str, exit_code: int, project_path: str):
        """Called when a deploy completes"""
        logger.info("✅ [DEPLOY] Deploy completed", project=project_name, exit_code=exit_code)
        
        # Update state
        deploybot_state.deploy_detected = False
        
        # Log the event
        await activity_logger.log_deploy_completed(project_name, deploy_command, exit_code, project_path)
        
        # Stop the timer
        await deploy_timer.stop_timer(project_name, "deploy_completed")
        
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
        logger.info("🔌 [WEBSOCKET] WebSocket server initialized", host=host, port=port)

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
                
            # Deploy Simulation for Testing
            elif command == "simulate-deploy":
                project_name = data.get("project_name", deploybot_state.current_project)
                command_str = data.get("command", "firebase deploy --test")
                
                if project_name:
                    success = await deploy_monitor.simulate_deploy_event(project_name, command_str)
                    return {"success": success, "project": project_name, "command": command_str}
                else:
                    return {"success": False, "message": "No project specified"}
                    
            else:
                logger.warning("❓ [COMMAND] Unknown command received", command=command)
                return {"success": False, "message": f"Unknown command: {command}"}
                
        except Exception as e:
            logger.error("❌ [COMMAND] Error processing command", command=command, error=str(e))
            return {"success": False, "message": f"Error processing command: {str(e)}"}

    async def start_server(self):
        """Start the WebSocket server"""
        logger.info("🚀 [WEBSOCKET] Starting WebSocket server", host=self.host, port=self.port)
        
        async def handle_client(websocket, path):
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
    """LangGraph node: Select alternative task based on context"""
    logger.info("🎯 [LANGGRAPH] Selecting alternative task...")
    
    # Mock task selection - in Week 3 we'll implement real TODO.md parsing
    mock_tasks = [
        {"text": "Write product video script", "tags": ["#short", "#creative"], "app": "Notion"},
        {"text": "Review Firebase rules", "tags": ["#backend", "#research"], "app": "VSCode"},
        {"text": "Update documentation", "tags": ["#writing", "#long"], "app": "Bear"},
    ]
    
    # Filter out backend tasks during deploy (simple heuristic)
    suitable_tasks = [task for task in mock_tasks if "#backend" not in task.get("tags", [])]
    
    if suitable_tasks:
        selected = suitable_tasks[0]  # Simple selection for now
        state["selected_task"] = selected
        deploybot_state.selected_task = selected
        logger.info("✅ [LANGGRAPH] Task selected", task=selected["text"], app=selected["app"])
    else:
        logger.warning("⚠️ [LANGGRAPH] No suitable tasks found")
        state["selected_task"] = None
    
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
async def run_task_selection_test(project_name: str) -> Dict[str, Any]:
    """Test the task selection logic"""
    logger.info("🧪 [TEST] Running task selection test", project=project_name)
    
    mock_state = {"project": project_name}
    result_state = await select_task(mock_state)
    
    return result_state.get("selected_task")

async def open_application(app_name: str, task_text: str = None) -> bool:
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