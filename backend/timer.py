#!/usr/bin/env python3
"""
Timer Module for DeployBot

This module handles deploy wait timers with real-time WebSocket updates
and integrates with the LangGraph workflow for productivity redirections.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
import structlog

logger = structlog.get_logger()

class DeployTimer:
    """Manages deploy wait timers with WebSocket integration"""
    
    def __init__(self):
        self.active_timers = {}  # project_name -> timer_info
        self.timer_callbacks = []  # Callbacks for timer events
        self.websocket_clients = set()  # WebSocket clients for real-time updates
        self.websocket_server = None
        self.update_interval = 2.0  # Update every 2 seconds instead of 1
        self.timer_update_task = None
        
        logger.info("⏰ [TIMER] DeployTimer initialized")

    def add_timer_callback(self, callback: Callable):
        """Add a callback function for timer events"""
        self.timer_callbacks.append(callback)
        logger.info("📡 [TIMER] Timer callback registered")

    def remove_timer_callback(self, callback: Callable):
        """Remove a timer callback"""
        if callback in self.timer_callbacks:
            self.timer_callbacks.remove(callback)
            logger.info("📡 [TIMER] Timer callback removed")

    def add_websocket_client(self, websocket):
        """Add a WebSocket client for real-time timer updates"""
        self.websocket_clients.add(websocket)
        logger.info("🔌 [TIMER] WebSocket client added for timer updates")

    def remove_websocket_client(self, websocket):
        """Remove a WebSocket client"""
        self.websocket_clients.discard(websocket)
        logger.info("🔌 [TIMER] WebSocket client removed from timer updates")
    
    def set_websocket_server(self, websocket_server):
        """Set the WebSocket server for broadcasting timer updates"""
        self.websocket_server = websocket_server
        logger.info("🔌 [TIMER] WebSocket server configured for timer updates")

    async def start_timer(self, project_name: str, duration_seconds: int = 1800, 
                         deploy_command: Optional[str] = None, custom_config: Optional[Dict[str, Any]] = None) -> bool:
        """Start a deploy wait timer for a project"""
        logger.info("🚀 [TIMER] Starting deploy timer", 
                   project_name=project_name, 
                   duration_seconds=duration_seconds,
                   deploy_command=deploy_command)
        
        try:
            # Stop any existing timer for this project
            if project_name in self.active_timers:
                await self.stop_timer(project_name)
            
            start_time = time.time()
            end_time = start_time + duration_seconds
            
            # Create timer info
            timer_info = {
                "project_name": project_name,
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": duration_seconds,
                "remaining_seconds": duration_seconds,
                "deploy_command": deploy_command,
                "custom_config": custom_config or {},
                "status": "running",
                "created_at": datetime.now().isoformat(),
                "grace_period_used": False,
                "paused": False,
                "pause_time": None,
                "pause_duration": 0
            }
            
            self.active_timers[project_name] = timer_info
            
            # Start the update loop if not already running
            if not self.timer_update_task:
                self.timer_update_task = asyncio.create_task(self._timer_update_loop())
            
            # Notify callbacks
            await self._notify_timer_event("timer_started", timer_info)
            
            # Send WebSocket update
            await self._send_websocket_update(timer_info)
            
            logger.info("✅ [TIMER] Timer started successfully", 
                       project_name=project_name,
                       end_time=datetime.fromtimestamp(end_time).isoformat())
            return True
            
        except Exception as e:
            logger.error("❌ [TIMER] Failed to start timer", 
                        project_name=project_name, error=str(e))
            return False

    async def stop_timer(self, project_name: str, reason: str = "manual") -> bool:
        """Stop a running timer"""
        logger.info("🛑 [TIMER] Stopping timer", 
                   project_name=project_name, reason=reason)
        
        if project_name not in self.active_timers:
            logger.warning("⚠️ [TIMER] No active timer found", 
                          project_name=project_name)
            return False
        
        try:
            timer_info = self.active_timers[project_name]
            timer_info["status"] = "stopped"
            timer_info["stop_reason"] = reason
            timer_info["stopped_at"] = datetime.now().isoformat()
            
            # Calculate final remaining time
            if not timer_info["paused"]:
                current_time = time.time()
                timer_info["remaining_seconds"] = max(0, timer_info["end_time"] - current_time)
            
            # Notify callbacks
            await self._notify_timer_event("timer_stopped", timer_info)
            
            # Send WebSocket update
            await self._send_websocket_update(timer_info)
            
            # Remove from active timers
            del self.active_timers[project_name]
            
            # Stop update loop if no active timers
            if not self.active_timers and self.timer_update_task:
                self.timer_update_task.cancel()
                self.timer_update_task = None
            
            logger.info("✅ [TIMER] Timer stopped successfully", 
                       project_name=project_name)
            return True
            
        except Exception as e:
            logger.error("❌ [TIMER] Failed to stop timer", 
                        project_name=project_name, error=str(e))
            return False

    async def pause_timer(self, project_name: str) -> bool:
        """Pause a running timer"""
        logger.info("⏸️ [TIMER] Pausing timer", project_name=project_name)
        
        if project_name not in self.active_timers:
            logger.warning("⚠️ [TIMER] No active timer found", 
                          project_name=project_name)
            return False
        
        timer_info = self.active_timers[project_name]
        
        if timer_info["paused"]:
            logger.warning("⚠️ [TIMER] Timer already paused", 
                          project_name=project_name)
            return False
        
        try:
            timer_info["paused"] = True
            timer_info["pause_time"] = time.time()
            timer_info["status"] = "paused"
            
            # Notify callbacks
            await self._notify_timer_event("timer_paused", timer_info)
            
            # Send WebSocket update
            await self._send_websocket_update(timer_info)
            
            logger.info("✅ [TIMER] Timer paused successfully", 
                       project_name=project_name)
            return True
            
        except Exception as e:
            logger.error("❌ [TIMER] Failed to pause timer", 
                        project_name=project_name, error=str(e))
            return False

    async def resume_timer(self, project_name: str) -> bool:
        """Resume a paused timer"""
        logger.info("▶️ [TIMER] Resuming timer", project_name=project_name)
        
        if project_name not in self.active_timers:
            logger.warning("⚠️ [TIMER] No active timer found", 
                          project_name=project_name)
            return False
        
        timer_info = self.active_timers[project_name]
        
        if not timer_info["paused"]:
            logger.warning("⚠️ [TIMER] Timer not paused", 
                          project_name=project_name)
            return False
        
        try:
            # Calculate pause duration
            pause_duration = time.time() - timer_info["pause_time"]
            timer_info["pause_duration"] += pause_duration
            
            # Extend end time by pause duration
            timer_info["end_time"] += pause_duration
            
            # Resume timer
            timer_info["paused"] = False
            timer_info["pause_time"] = None
            timer_info["status"] = "running"
            
            # Notify callbacks
            await self._notify_timer_event("timer_resumed", timer_info)
            
            # Send WebSocket update
            await self._send_websocket_update(timer_info)
            
            logger.info("✅ [TIMER] Timer resumed successfully", 
                       project_name=project_name, 
                       pause_duration=pause_duration)
            return True
            
        except Exception as e:
            logger.error("❌ [TIMER] Failed to resume timer", 
                        project_name=project_name, error=str(e))
            return False

    async def extend_timer(self, project_name: str, additional_seconds: int) -> bool:
        """Extend a running timer by additional seconds"""
        logger.info("🔄 [TIMER] Extending timer", 
                   project_name=project_name, 
                   additional_seconds=additional_seconds)
        
        if project_name not in self.active_timers:
            logger.warning("⚠️ [TIMER] No active timer found", 
                          project_name=project_name)
            return False
        
        try:
            timer_info = self.active_timers[project_name]
            timer_info["end_time"] += additional_seconds
            timer_info["duration_seconds"] += additional_seconds
            
            # Notify callbacks
            await self._notify_timer_event("timer_extended", timer_info)
            
            # Send WebSocket update
            await self._send_websocket_update(timer_info)
            
            logger.info("✅ [TIMER] Timer extended successfully", 
                       project_name=project_name)
            return True
            
        except Exception as e:
            logger.error("❌ [TIMER] Failed to extend timer", 
                        project_name=project_name, error=str(e))
            return False

    async def _timer_update_loop(self):
        """Background loop that updates timer states and sends WebSocket updates"""
        logger.info("🔄 [TIMER] Starting timer update loop...")
        
        while True:
            try:
                current_time = time.time()
                expired_timers = []
                
                # Update all active timers
                for project_name, timer_info in self.active_timers.items():
                    if timer_info["paused"]:
                        # Don't update paused timers
                        continue
                    
                    # Calculate remaining time
                    remaining = timer_info["end_time"] - current_time
                    timer_info["remaining_seconds"] = max(0, remaining)
                    
                    # Check if timer expired
                    if remaining <= 0 and timer_info["status"] == "running":
                        timer_info["status"] = "expired"
                        expired_timers.append(project_name)
                    
                    # Send WebSocket update
                    await self._send_websocket_update(timer_info)
                
                # Handle expired timers
                for project_name in expired_timers:
                    await self._handle_timer_expiry(project_name)
                
                # Wait before next update
                await asyncio.sleep(self.update_interval)
                
            except asyncio.CancelledError:
                logger.info("🔄 [TIMER] Timer update loop cancelled")
                break
            except Exception as e:
                logger.error("❌ [TIMER] Error in timer update loop", error=str(e))
                await asyncio.sleep(self.update_interval * 2)

    async def _handle_timer_expiry(self, project_name: str):
        """Handle timer expiry"""
        logger.info("⏰ [TIMER] Timer expired", project_name=project_name)
        
        timer_info = self.active_timers[project_name]
        timer_info["expired_at"] = datetime.now().isoformat()
        
        # Notify callbacks
        await self._notify_timer_event("timer_expired", timer_info)
        
        # Send final WebSocket update
        await self._send_websocket_update(timer_info)
        
        # Remove from active timers after a brief delay
        await asyncio.sleep(5)  # Keep for 5 seconds for UI transition
        if project_name in self.active_timers:
            del self.active_timers[project_name]

    async def _notify_timer_event(self, event_type: str, timer_info: Dict[str, Any]):
        """Notify all registered callbacks of timer events"""
        for callback in self.timer_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event_type, timer_info)
                else:
                    callback(event_type, timer_info)
            except Exception as e:
                logger.error("❌ [TIMER] Error in timer callback", 
                           event_type=event_type, error=str(e))

    async def _send_websocket_update(self, timer_info: Dict[str, Any]):
        """Send timer update to all WebSocket clients"""
        message = {
            "type": "timer_update",
            "data": {
                "project_name": timer_info["project_name"],
                "status": timer_info["status"],
                "remaining_seconds": timer_info["remaining_seconds"],
                "total_duration": timer_info["duration_seconds"],
                "progress_percentage": self._calculate_progress(timer_info),
                "time_remaining_formatted": self._format_time_remaining(timer_info["remaining_seconds"]),
                "paused": timer_info.get("paused", False),
                "deploy_command": timer_info.get("deploy_command"),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Use WebSocket server broadcast if available, otherwise send to individual clients
        if hasattr(self, 'websocket_server') and self.websocket_server:
            try:
                await self.websocket_server.broadcast(message)
                return
            except Exception as e:
                logger.warning("⚠️ [TIMER] Failed to broadcast timer update via server", error=str(e))
        
        # Fallback to individual client updates
        if not self.websocket_clients:
            return
        
        disconnected_clients = []
        for websocket in self.websocket_clients:
            try:
                import json
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.warning("⚠️ [TIMER] Failed to send WebSocket update", error=str(e))
                disconnected_clients.append(websocket)
        
        # Remove disconnected clients
        for websocket in disconnected_clients:
            self.websocket_clients.discard(websocket)

    def _calculate_progress(self, timer_info: Dict[str, Any]) -> float:
        """Calculate timer progress percentage"""
        total_duration = timer_info["duration_seconds"]
        remaining = timer_info["remaining_seconds"]
        
        if total_duration <= 0:
            return 100.0
        
        elapsed = total_duration - remaining
        progress = (elapsed / total_duration) * 100
        return min(100.0, max(0.0, progress))

    def _format_time_remaining(self, seconds: float) -> str:
        """Format remaining time in human-readable format"""
        if seconds <= 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"

    def get_timer_status(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a timer"""
        if project_name not in self.active_timers:
            return None
        
        timer_info = self.active_timers[project_name]
        
        return {
            "project_name": project_name,
            "status": timer_info["status"],
            "remaining_seconds": timer_info["remaining_seconds"],
            "duration_seconds": timer_info["duration_seconds"],
            "progress_percentage": self._calculate_progress(timer_info),
            "time_remaining_formatted": self._format_time_remaining(timer_info["remaining_seconds"]),
            "deploy_command": timer_info.get("deploy_command"),
            "paused": timer_info.get("paused", False),
            "created_at": timer_info["created_at"]
        }

    def get_all_timers_status(self) -> Dict[str, Any]:
        """Get status of all active timers"""
        return {
            "active_timer_count": len(self.active_timers),
            "active_projects": list(self.active_timers.keys()),
            "timers": {
                project_name: self.get_timer_status(project_name)
                for project_name in self.active_timers.keys()
            }
        }

    async def cleanup(self):
        """Clean up timer resources"""
        logger.info("🧹 [TIMER] Cleaning up timer resources...")
        
        # Stop all active timers
        active_projects = list(self.active_timers.keys())
        for project_name in active_projects:
            await self.stop_timer(project_name, reason="cleanup")
        
        # Cancel update task
        if self.timer_update_task:
            self.timer_update_task.cancel()
            try:
                await self.timer_update_task
            except asyncio.CancelledError:
                pass
            self.timer_update_task = None
        
        # Clear WebSocket clients
        self.websocket_clients.clear()
        
        logger.info("✅ [TIMER] Timer cleanup completed")

# Global instance
deploy_timer = DeployTimer() 