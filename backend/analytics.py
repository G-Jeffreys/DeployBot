"""
DeployBot Analytics System
Tracks task suggestions, user interactions, and productivity metrics
Uses JSON-based storage with smart monthly indexing for minimal overhead

Phase 1: Task Selection Analytics & Learning ✅
Phase 2: Comprehensive Productivity Analytics (Deploy Sessions, Time Saved, Patterns) 🚧
"""

import json
import asyncio
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import hashlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class TaskSuggestion:
    """Data class for task suggestion events"""
    id: str
    task_id: str
    task_text: str
    task_tags: List[str]
    suggested_app: str
    suggestion_timestamp: str
    deploy_command: str
    timer_duration: int
    context_data: Dict[str, Any]
    project_name: str

@dataclass
class UserInteraction:
    """Data class for user interaction events"""
    suggestion_id: str
    interaction_type: str  # accepted, ignored, snoozed, dismissed
    interaction_timestamp: str
    response_time_seconds: float
    completion_detected: bool = False
    completion_method: Optional[str] = None  # manual, time_heuristic, app_integration
    time_in_app_seconds: Optional[int] = None
    productivity_score: Optional[float] = None

@dataclass
class DeploySession:
    """
    📊 PHASE 2: Data class for deployment session tracking
    Tracks complete deploy sessions from timer start to completion
    """
    session_id: str
    project_name: str
    deploy_command: str
    session_start: str
    session_end: Optional[str] = None
    timer_duration_seconds: int = 1800  # Default 30 minutes
    cloud_propagation_time_seconds: int = 1800  # Always equals timer_duration (30 min)
    tasks_suggested: int = 0
    tasks_accepted: int = 0
    switch_button_pressed: bool = False  # 📊 PHASE 2: Track first Switch press only
    switch_timestamp: Optional[str] = None  # When Switch was first pressed
    estimated_time_saved_seconds: int = 0  # 📊 PHASE 2: = cloud_propagation_time IF switch_button_pressed
    session_status: str = "active"  # active, completed, cancelled
    productivity_score: Optional[float] = None

@dataclass  
class DeployPattern:
    """
    📊 PHASE 2: Data class for deploy pattern analytics
    Tracks deployment frequency and command patterns
    """
    project_name: str
    deploy_command: str
    deploy_timestamp: str
    time_of_day: str  # morning, afternoon, evening, night
    day_of_week: str
    deploy_frequency_score: float = 0.0  # Calculated based on recent deploys

class AnalyticsManager:
    """
    Manages analytics data collection and storage for DeployBot
    Uses JSON-based storage with monthly files for efficient access
    
    📊 PHASE 2: Enhanced with comprehensive productivity analytics
    """
    
    def __init__(self, projects_root: Optional[Path] = None):
        """Initialize analytics manager with projects directory"""
        self.projects_root = projects_root or Path(__file__).parent.parent / "projects"
        
        # 📊 PHASE 2: Enhanced session management
        self.active_sessions: Dict[str, DeploySession] = {}
        self.app_focus_monitoring: Dict[str, Dict[str, Any]] = {}
        
        # Cache for analytics data (last 30 days)
        self.analytics_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_expiry: Dict[str, datetime] = {}
        
        logger.info("📊 [ANALYTICS] AnalyticsManager initialized with Phase 2 enhancements", 
                   projects_root=str(self.projects_root))
    
    def _get_current_month_key(self) -> str:
        """Get current month key for file indexing (YYYY-MM format)"""
        return datetime.now().strftime("%Y-%m")
    
    def _get_analytics_dir(self, project_name: str) -> Path:
        """Get analytics directory for a project, create if doesn't exist"""
        project_dir = self.projects_root / project_name.replace(" ", "_")
        analytics_dir = project_dir / "analytics"
        analytics_dir.mkdir(parents=True, exist_ok=True)
        return analytics_dir
    
    def _generate_suggestion_id(self, task_text: str, timestamp: str) -> str:
        """Generate unique suggestion ID based on task and timestamp"""
        content = f"{task_text}_{timestamp}"
        return f"suggestion_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _generate_session_id(self, project_name: str, deploy_command: str) -> str:
        """Generate unique session ID for deploy sessions"""
        content = f"{project_name}_{deploy_command}_{time.time()}"
        return f"session_{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    async def record_task_suggestion(self, task: Dict[str, Any], 
                                   project_name: str,
                                   context: Dict[str, Any]) -> str:
        """
        Record a task suggestion event
        Returns suggestion ID for tracking interactions
        """
        logger.info("📝 [ANALYTICS] Recording task suggestion", 
                   task=task.get('text', ''), 
                   project=project_name)
        
        # Generate suggestion ID
        timestamp = datetime.now().isoformat()
        suggestion_id = self._generate_suggestion_id(task.get('text', ''), timestamp)
        
        # Create suggestion record
        suggestion = TaskSuggestion(
            id=suggestion_id,
            task_id=task.get('id', ''),
            task_text=task.get('text', ''),
            task_tags=task.get('tags', []),
            suggested_app=task.get('app', ''),
            suggestion_timestamp=timestamp,
            deploy_command=context.get('deploy_command', ''),
            timer_duration=context.get('timer_duration', 1800),
            context_data={
                'time_of_day': datetime.now().strftime('%p').lower(),
                'project_type': context.get('project_type', 'unknown'),
                'recent_deploys': context.get('recent_deploys', 0),
                'deploy_active': context.get('deploy_active', False),
                'priority': task.get('priority', 5),
                'estimated_duration': task.get('estimated_duration', 45)
            },
            project_name=project_name
        )
        
        # Save to monthly suggestions file
        await self._save_suggestion(suggestion)
        
        logger.info("✅ [ANALYTICS] Task suggestion recorded", 
                   suggestion_id=suggestion_id,
                   project=project_name)
        
        return suggestion_id
    
    async def record_user_interaction(self, suggestion_id: str, 
                                    interaction_type: str,
                                    response_time_seconds: float,
                                    project_name: str,
                                    additional_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record user interaction with a task suggestion
        Returns True if successfully recorded
        """
        logger.info("👆 [ANALYTICS] Recording user interaction", 
                   suggestion_id=suggestion_id,
                   interaction_type=interaction_type,
                   response_time=response_time_seconds)
        
        # Create interaction record
        interaction = UserInteraction(
            suggestion_id=suggestion_id,
            interaction_type=interaction_type,
            interaction_timestamp=datetime.now().isoformat(),
            response_time_seconds=response_time_seconds,
            completion_detected=False,  # Will be updated later if task completed
            completion_method=None,
            time_in_app_seconds=None,
            productivity_score=None
        )
        
        # Save to monthly interactions file
        await self._save_interaction(interaction, project_name)
        
        # Start app focus monitoring if user accepted the task
        if interaction_type == "accepted":
            await self._start_app_focus_monitoring(suggestion_id, project_name, additional_data or {})
        
        logger.info("✅ [ANALYTICS] User interaction recorded", 
                   suggestion_id=suggestion_id,
                   interaction_type=interaction_type)
        
        return True
    
    async def _save_suggestion(self, suggestion: TaskSuggestion):
        """Save task suggestion to monthly JSON file"""
        try:
            analytics_dir = self._get_analytics_dir(suggestion.project_name)
            month_key = self._get_current_month_key()
            suggestions_file = analytics_dir / f"suggestions_{month_key}.json"
            
            # Load existing data or create new
            if suggestions_file.exists():
                with open(suggestions_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"month": month_key, "suggestions": []}
            
            # Add new suggestion
            data["suggestions"].append({
                "id": suggestion.id,
                "task_id": suggestion.task_id,
                "task_text": suggestion.task_text,
                "task_tags": suggestion.task_tags,
                "suggested_app": suggestion.suggested_app,
                "suggestion_timestamp": suggestion.suggestion_timestamp,
                "deploy_command": suggestion.deploy_command,
                "timer_duration": suggestion.timer_duration,
                "context_data": suggestion.context_data
            })
            
            # Save back to file
            with open(suggestions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("💾 [ANALYTICS] Suggestion saved to file", 
                        file=str(suggestions_file),
                        suggestion_id=suggestion.id)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to save suggestion", 
                        error=str(e),
                        suggestion_id=suggestion.id)
    
    async def _save_interaction(self, interaction: UserInteraction, project_name: str):
        """Save user interaction to monthly JSON file"""
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            month_key = self._get_current_month_key()
            interactions_file = analytics_dir / f"interactions_{month_key}.json"
            
            # Load existing data or create new
            if interactions_file.exists():
                with open(interactions_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"month": month_key, "interactions": []}
            
            # Add new interaction
            data["interactions"].append({
                "suggestion_id": interaction.suggestion_id,
                "interaction_type": interaction.interaction_type,
                "interaction_timestamp": interaction.interaction_timestamp,
                "response_time_seconds": interaction.response_time_seconds,
                "completion_detected": interaction.completion_detected,
                "completion_method": interaction.completion_method,
                "time_in_app_seconds": interaction.time_in_app_seconds,
                "productivity_score": interaction.productivity_score
            })
            
            # Save back to file
            with open(interactions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("💾 [ANALYTICS] Interaction saved to file", 
                        file=str(interactions_file),
                        suggestion_id=interaction.suggestion_id)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to save interaction", 
                        error=str(e),
                        suggestion_id=interaction.suggestion_id)
    
    async def _start_app_focus_monitoring(self, suggestion_id: str, 
                                        project_name: str, 
                                        additional_data: Dict[str, Any]):
        """Start monitoring app focus for task completion detection"""
        task_data = additional_data.get('task', {})
        target_app = task_data.get('app', '')
        
        if not target_app:
            logger.warning("⚠️ [ANALYTICS] No target app specified for focus monitoring")
            return
        
        # Store monitoring data
        self.app_focus_monitoring[suggestion_id] = {
            'target_app': target_app,
            'project_name': project_name,
            'start_time': time.time(),
            'task_data': task_data,
            'focus_detected': False,
            'total_focus_time': 0
        }
        
        logger.info("👁️ [ANALYTICS] Started app focus monitoring", 
                   suggestion_id=suggestion_id,
                   target_app=target_app)
        
        # Start the monitoring task
        asyncio.create_task(self._monitor_app_focus(suggestion_id))
    
    async def _monitor_app_focus(self, suggestion_id: str):
        """Monitor app focus for task completion (time-based heuristic)"""
        monitor_data = self.app_focus_monitoring.get(suggestion_id)
        if not monitor_data:
            return
        
        target_app = monitor_data['target_app']
        project_name = monitor_data['project_name']
        start_time = monitor_data['start_time']
        
        # Simple time-based heuristic: check if 10+ minutes have passed
        # In a real implementation, this would integrate with macOS focus detection
        completion_threshold = 600  # 10 minutes in seconds
        
        logger.info("⏱️ [ANALYTICS] Starting app focus monitoring timer", 
                   suggestion_id=suggestion_id,
                   target_app=target_app,
                   threshold_minutes=completion_threshold/60)
        
        # Wait for completion threshold
        await asyncio.sleep(completion_threshold)
        
        # Check if monitoring is still active
        if suggestion_id in self.app_focus_monitoring:
            elapsed_time = time.time() - start_time
            
            # Mark as completed (heuristic)
            await self._mark_task_completed(
                suggestion_id, 
                project_name,
                completion_method="time_heuristic",
                time_in_app_seconds=int(elapsed_time),
                productivity_score=0.75  # Moderate confidence for heuristic
            )
            
            # Clean up monitoring
            del self.app_focus_monitoring[suggestion_id]
            
            logger.info("✅ [ANALYTICS] Task marked as completed (heuristic)", 
                       suggestion_id=suggestion_id,
                       elapsed_time_minutes=elapsed_time/60)
    
    async def _mark_task_completed(self, suggestion_id: str, 
                                 project_name: str,
                                 completion_method: str,
                                 time_in_app_seconds: int,
                                 productivity_score: float):
        """Mark a task as completed and update interaction record"""
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            month_key = self._get_current_month_key()
            interactions_file = analytics_dir / f"interactions_{month_key}.json"
            
            if not interactions_file.exists():
                logger.warning("⚠️ [ANALYTICS] No interactions file found for completion update")
                return
            
            # Load and update interactions data
            with open(interactions_file, 'r') as f:
                data = json.load(f)
            
            # Find and update the interaction
            for interaction in data["interactions"]:
                if interaction["suggestion_id"] == suggestion_id:
                    interaction["completion_detected"] = True
                    interaction["completion_method"] = completion_method
                    interaction["time_in_app_seconds"] = time_in_app_seconds
                    interaction["productivity_score"] = productivity_score
                    break
            
            # Save updated data
            with open(interactions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info("✅ [ANALYTICS] Task completion recorded", 
                       suggestion_id=suggestion_id,
                       completion_method=completion_method,
                       time_in_app_minutes=time_in_app_seconds/60)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to mark task as completed", 
                        error=str(e),
                        suggestion_id=suggestion_id)
    
    async def get_task_analytics(self, project_name: str, 
                               task_text: Optional[str] = None,
                               last_n_days: int = 30) -> Dict[str, Any]:
        """
        Get analytics data for task suggestions
        Used by TaskSelector for learning
        """
        logger.debug("📊 [ANALYTICS] Getting task analytics", 
                    project=project_name,
                    task=task_text,
                    days=last_n_days)
        
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            
            # Load recent months' data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=last_n_days)
            
            suggestions_data = []
            interactions_data = []
            
            # Load data from multiple months if needed
            current_month = end_date.replace(day=1)
            while current_month >= start_date.replace(day=1):
                month_key = current_month.strftime("%Y-%m")
                
                # Load suggestions
                suggestions_file = analytics_dir / f"suggestions_{month_key}.json"
                if suggestions_file.exists():
                    with open(suggestions_file, 'r') as f:
                        month_suggestions = json.load(f)
                        suggestions_data.extend(month_suggestions.get("suggestions", []))
                
                # Load interactions
                interactions_file = analytics_dir / f"interactions_{month_key}.json"
                if interactions_file.exists():
                    with open(interactions_file, 'r') as f:
                        month_interactions = json.load(f)
                        interactions_data.extend(month_interactions.get("interactions", []))
                
                # Move to previous month
                if current_month.month == 1:
                    current_month = current_month.replace(year=current_month.year - 1, month=12)
                else:
                    current_month = current_month.replace(month=current_month.month - 1)
            
            # Build analytics summary
            analytics = self._build_analytics_summary(
                suggestions_data, 
                interactions_data, 
                task_text,
                last_n_days
            )
            
            logger.debug("✅ [ANALYTICS] Task analytics retrieved", 
                        project=project_name,
                        suggestions_count=len(suggestions_data),
                        interactions_count=len(interactions_data))
            
            return analytics
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to get task analytics", 
                        error=str(e),
                        project=project_name)
            return {
                "suggestions_count": 0,
                "accepted": 0,
                "ignored": 0,
                "snoozed": 0,
                "recent_ignores_30d": 0,
                "acceptance_rate": 0.0,
                "completion_rate": 0.0,
                "avg_response_time": 0.0,
                "task_patterns": {}
            }
    
    def _build_analytics_summary(self, suggestions: List[Dict], 
                               interactions: List[Dict],
                               task_text: str = None,
                               last_n_days: int = 30) -> Dict[str, Any]:
        """Build analytics summary from raw data"""
        
        # Filter by task text if specified
        if task_text:
            suggestions = [s for s in suggestions if s["task_text"] == task_text]
        
        # Create suggestion ID mapping
        suggestion_ids = {s["id"] for s in suggestions}
        
        # Filter interactions for our suggestions
        relevant_interactions = [
            i for i in interactions 
            if i["suggestion_id"] in suggestion_ids
        ]
        
        # Calculate metrics
        total_suggestions = len(suggestions)
        accepted = len([i for i in relevant_interactions if i["interaction_type"] == "accepted"])
        ignored = len([i for i in relevant_interactions if i["interaction_type"] == "ignored"])
        snoozed = len([i for i in relevant_interactions if i["interaction_type"] == "snoozed"])
        
        # Recent ignores (last 30 days)
        cutoff_date = datetime.now() - timedelta(days=last_n_days)
        recent_ignores = len([
            i for i in relevant_interactions 
            if i["interaction_type"] == "ignored" and 
            datetime.fromisoformat(i["interaction_timestamp"].replace('Z', '+00:00')) >= cutoff_date
        ])
        
        # Completion metrics
        completed_tasks = len([i for i in relevant_interactions if i["completion_detected"]])
        
        # Response time metrics
        response_times = [i["response_time_seconds"] for i in relevant_interactions if i["response_time_seconds"]]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        # Calculate rates
        acceptance_rate = accepted / total_suggestions if total_suggestions > 0 else 0.0
        completion_rate = completed_tasks / accepted if accepted > 0 else 0.0
        
        return {
            "suggestions_count": total_suggestions,
            "accepted": accepted,
            "ignored": ignored,
            "snoozed": snoozed,
            "recent_ignores_30d": recent_ignores,
            "acceptance_rate": acceptance_rate,
            "completion_rate": completion_rate,
            "avg_response_time": avg_response_time,
            "task_patterns": {
                "total_completed": completed_tasks,
                "avg_completion_time": sum([
                    i["time_in_app_seconds"] for i in relevant_interactions 
                    if i["time_in_app_seconds"]
                ]) / max(1, completed_tasks),
                "avg_productivity_score": sum([
                    i["productivity_score"] for i in relevant_interactions 
                    if i["productivity_score"]
                ]) / max(1, completed_tasks)
            }
        }
    
    async def get_project_analytics_summary(self, project_name: str) -> Dict[str, Any]:
        """Get high-level analytics summary for a project"""
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            
            # Get current month data
            month_key = self._get_current_month_key()
            
            # Load suggestions
            suggestions_file = analytics_dir / f"suggestions_{month_key}.json"
            suggestions_count = 0
            if suggestions_file.exists():
                with open(suggestions_file, 'r') as f:
                    data = json.load(f)
                    suggestions_count = len(data.get("suggestions", []))
            
            # Load interactions
            interactions_file = analytics_dir / f"interactions_{month_key}.json"
            interactions_count = 0
            acceptance_rate = 0.0
            if interactions_file.exists():
                with open(interactions_file, 'r') as f:
                    data = json.load(f)
                    interactions = data.get("interactions", [])
                    interactions_count = len(interactions)
                    
                    accepted = len([i for i in interactions if i["interaction_type"] == "accepted"])
                    acceptance_rate = accepted / suggestions_count if suggestions_count > 0 else 0.0
            
            return {
                "project_name": project_name,
                "month": month_key,
                "suggestions_count": suggestions_count,
                "interactions_count": interactions_count,
                "acceptance_rate": acceptance_rate,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to get project analytics summary", 
                        error=str(e),
                        project=project_name)
            return {
                "project_name": project_name,
                "month": self._get_current_month_key(),
                "suggestions_count": 0,
                "interactions_count": 0,
                "acceptance_rate": 0.0,
                "last_updated": datetime.now().isoformat()
            }

    # 📊 PHASE 2: SESSION MANAGEMENT METHODS
    
    async def start_deploy_session(self, project_name: str, deploy_command: str, 
                                 timer_duration_seconds: int = 1800) -> str:
        """
        📊 PHASE 2: Start a new deploy session when timer starts
        Returns session_id for tracking
        """
        logger.info("🚀 [ANALYTICS] Starting deploy session", 
                   project=project_name, 
                   command=deploy_command,
                   timer_duration_minutes=timer_duration_seconds/60)
        
        # Generate session ID
        session_id = self._generate_session_id(project_name, deploy_command)
        
        # Create session record
        session = DeploySession(
            session_id=session_id,
            project_name=project_name,
            deploy_command=deploy_command,
            session_start=datetime.now().isoformat(),
            timer_duration_seconds=timer_duration_seconds,
            cloud_propagation_time_seconds=timer_duration_seconds,  # 📊 PHASE 2: Always equals timer duration
            session_status="active"
        )
        
        # Store in active sessions
        self.active_sessions[session_id] = session
        
        # Record deploy pattern
        await self._record_deploy_pattern(project_name, deploy_command)
        
        logger.info("✅ [ANALYTICS] Deploy session started", 
                   session_id=session_id,
                   project=project_name,
                   cloud_propagation_minutes=timer_duration_seconds/60)
        
        return session_id
    
    async def end_deploy_session(self, session_id: str, status: str = "completed") -> bool:
        """
        📊 PHASE 2: End a deploy session and save to storage
        """
        logger.info("🏁 [ANALYTICS] Ending deploy session", 
                   session_id=session_id, status=status)
        
        if session_id not in self.active_sessions:
            logger.warning("⚠️ [ANALYTICS] Session not found", session_id=session_id)
            return False
        
        try:
            session = self.active_sessions[session_id]
            session.session_end = datetime.now().isoformat()
            session.session_status = status
            
            # 📊 PHASE 2: Calculate time saved based on Switch button press
            if session.switch_button_pressed:
                session.estimated_time_saved_seconds = session.cloud_propagation_time_seconds
                logger.info("💰 [ANALYTICS] Time saved calculated - user switched to task", 
                           session_id=session_id,
                           time_saved_minutes=session.estimated_time_saved_seconds/60)
            else:
                session.estimated_time_saved_seconds = 0
                logger.info("📊 [ANALYTICS] No time saved - user didn't switch to task", 
                           session_id=session_id)
            
            # Calculate productivity score
            session.productivity_score = self._calculate_session_productivity_score(session)
            
            # Save to monthly sessions file
            await self._save_session(session)
            
            # Remove from active sessions
            del self.active_sessions[session_id]
            
            logger.info("✅ [ANALYTICS] Deploy session ended and saved", 
                       session_id=session_id,
                       status=status,
                       time_saved_minutes=session.estimated_time_saved_seconds/60)
            
            return True
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to end deploy session", 
                        session_id=session_id, error=str(e))
            return False
    
    async def record_switch_button_press(self, session_id: str, project_name: str = None) -> bool:
        """
        📊 PHASE 2: Record when user presses Switch button (first time only per session)
        """
        logger.info("🔀 [ANALYTICS] Recording Switch button press", 
                   session_id=session_id, project=project_name)
        
        # Find session by ID or by project name
        session = None
        if session_id and session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        elif project_name:
            # Find active session for project
            for sid, sess in self.active_sessions.items():
                if sess.project_name == project_name and sess.session_status == "active":
                    session = sess
                    session_id = sid
                    break
        
        if not session:
            logger.warning("⚠️ [ANALYTICS] No active session found for Switch tracking", 
                          session_id=session_id, project=project_name)
            return False
        
        # 📊 PHASE 2: Only record the FIRST Switch press per session
        if session.switch_button_pressed:
            logger.info("📊 [ANALYTICS] Switch already pressed in this session - ignoring", 
                       session_id=session_id)
            return True  # Return success since it was already recorded
        
        try:
            # Record the Switch press
            session.switch_button_pressed = True
            session.switch_timestamp = datetime.now().isoformat()
            
            logger.info("✅ [ANALYTICS] First Switch button press recorded", 
                       session_id=session_id,
                       project=session.project_name)
            
            return True
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to record Switch button press", 
                        session_id=session_id, error=str(e))
            return False
    
    async def _record_deploy_pattern(self, project_name: str, deploy_command: str):
        """
        📊 PHASE 2: Record deploy pattern for frequency analysis
        """
        try:
            now = datetime.now()
            
            # Create deploy pattern record
            pattern = DeployPattern(
                project_name=project_name,
                deploy_command=deploy_command,
                deploy_timestamp=now.isoformat(),
                time_of_day=self._get_time_of_day(now.hour),
                day_of_week=now.strftime("%A"),
                deploy_frequency_score=await self._calculate_deploy_frequency_score(project_name)
            )
            
            # Save to monthly patterns file
            await self._save_deploy_pattern(pattern)
            
            logger.debug("📊 [ANALYTICS] Deploy pattern recorded", 
                        project=project_name, 
                        command=deploy_command,
                        time_of_day=pattern.time_of_day)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to record deploy pattern", 
                        project=project_name, error=str(e))
    
    def _get_time_of_day(self, hour: int) -> str:
        """Convert hour to time of day category"""
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"  
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    async def _calculate_deploy_frequency_score(self, project_name: str) -> float:
        """
        📊 PHASE 2: Calculate deploy frequency score based on recent activity
        """
        try:
            # Get recent deploy patterns (last 7 days)
            patterns = await self._get_recent_deploy_patterns(project_name, days=7)
            
            if not patterns:
                return 0.0
            
            # Calculate deploys per day
            deploy_count = len(patterns)
            frequency_score = min(10.0, deploy_count / 7.0)  # Max score of 10
            
            return frequency_score
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to calculate deploy frequency", 
                        project=project_name, error=str(e))
            return 0.0
    
    def _calculate_session_productivity_score(self, session: DeploySession) -> float:
        """
        📊 PHASE 2: Calculate productivity score for a completed session
        """
        score = 0.0
        
        # Base score for completing the session
        score += 0.3
        
        # Bonus for accepting task suggestions
        if session.tasks_suggested > 0:
            acceptance_rate = session.tasks_accepted / session.tasks_suggested
            score += acceptance_rate * 0.3
        
        # Major bonus for pressing Switch button (actually engaging with suggested task)
        if session.switch_button_pressed:
            score += 0.4
        
        # Bonus for longer sessions (user stayed engaged)
        if session.session_end and session.session_start:
            try:
                start_time = datetime.fromisoformat(session.session_start.replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(session.session_end.replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds()
                
                # Bonus for sessions lasting at least 50% of timer duration
                if duration >= (session.timer_duration_seconds * 0.5):
                    score += 0.1
                    
            except Exception as e:
                logger.warning("⚠️ [ANALYTICS] Failed to calculate session duration", error=str(e))
        
        return min(1.0, score)  # Cap at 1.0
    
    # 📊 PHASE 2: SESSION STORAGE METHODS
    
    async def _save_session(self, session: DeploySession):
        """Save deploy session to monthly JSON file"""
        try:
            analytics_dir = self._get_analytics_dir(session.project_name)
            month_key = self._get_current_month_key()
            sessions_file = analytics_dir / f"sessions_{month_key}.json"
            
            # Load existing data or create new
            if sessions_file.exists():
                with open(sessions_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"month": month_key, "deploy_sessions": []}
            
            # Add new session
            data["deploy_sessions"].append({
                "session_id": session.session_id,
                "project_name": session.project_name,
                "deploy_command": session.deploy_command,
                "session_start": session.session_start,
                "session_end": session.session_end,
                "timer_duration_seconds": session.timer_duration_seconds,
                "cloud_propagation_time_seconds": session.cloud_propagation_time_seconds,
                "tasks_suggested": session.tasks_suggested,
                "tasks_accepted": session.tasks_accepted,
                "switch_button_pressed": session.switch_button_pressed,
                "switch_timestamp": session.switch_timestamp,
                "estimated_time_saved_seconds": session.estimated_time_saved_seconds,
                "session_status": session.session_status,
                "productivity_score": session.productivity_score
            })
            
            # Save back to file
            with open(sessions_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("💾 [ANALYTICS] Session saved to file", 
                        file=str(sessions_file),
                        session_id=session.session_id)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to save session", 
                        error=str(e),
                        session_id=session.session_id)
    
    async def _save_deploy_pattern(self, pattern: DeployPattern):
        """Save deploy pattern to monthly JSON file"""
        try:
            analytics_dir = self._get_analytics_dir(pattern.project_name)
            month_key = self._get_current_month_key()
            patterns_file = analytics_dir / f"deploy_patterns_{month_key}.json"
            
            # Load existing data or create new
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {"month": month_key, "deploy_patterns": []}
            
            # Add new pattern
            data["deploy_patterns"].append({
                "project_name": pattern.project_name,
                "deploy_command": pattern.deploy_command,
                "deploy_timestamp": pattern.deploy_timestamp,
                "time_of_day": pattern.time_of_day,
                "day_of_week": pattern.day_of_week,
                "deploy_frequency_score": pattern.deploy_frequency_score
            })
            
            # Save back to file
            with open(patterns_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("💾 [ANALYTICS] Deploy pattern saved to file", 
                        file=str(patterns_file),
                        project=pattern.project_name)
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to save deploy pattern", 
                        error=str(e),
                        project=pattern.project_name)

    # 📊 PHASE 2: HELPER METHODS FOR DEPLOY PATTERNS AND SESSION ANALYTICS
    
    async def _get_recent_deploy_patterns(self, project_name: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        📊 PHASE 2: Get recent deploy patterns for frequency calculation
        """
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            patterns = []
            
            # Load data from multiple months if needed
            current_month = end_date.replace(day=1)
            while current_month >= start_date.replace(day=1):
                month_key = current_month.strftime("%Y-%m")
                patterns_file = analytics_dir / f"deploy_patterns_{month_key}.json"
                
                if patterns_file.exists():
                    with open(patterns_file, 'r') as f:
                        month_data = json.load(f)
                        month_patterns = month_data.get("deploy_patterns", [])
                        
                        # Filter by date range
                        for pattern in month_patterns:
                            pattern_date = datetime.fromisoformat(pattern["deploy_timestamp"].replace('Z', '+00:00'))
                            if start_date <= pattern_date <= end_date:
                                patterns.append(pattern)
                
                # Move to previous month
                if current_month.month == 1:
                    current_month = current_month.replace(year=current_month.year - 1, month=12)
                else:
                    current_month = current_month.replace(month=current_month.month - 1)
            
            logger.debug("📊 [ANALYTICS] Retrieved recent deploy patterns", 
                        project=project_name, 
                        patterns_count=len(patterns),
                        days=days)
            
            return patterns
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to get recent deploy patterns", 
                        project=project_name, error=str(e))
            return []
    
    async def get_deploy_analytics_summary(self, project_name: str, last_n_days: int = 30) -> Dict[str, Any]:
        """
        📊 PHASE 2: Get comprehensive deploy analytics for a project
        """
        logger.debug("📊 [ANALYTICS] Getting deploy analytics summary", 
                    project=project_name, days=last_n_days)
        
        try:
            # Get recent sessions
            sessions = await self._get_recent_deploy_sessions(project_name, last_n_days)
            
            # Get recent deploy patterns
            patterns = await self._get_recent_deploy_patterns(project_name, last_n_days)
            
            # Calculate metrics
            total_sessions = len(sessions)
            total_deploys = len(patterns)
            
            # Time saved metrics
            total_time_saved = sum(s.get("estimated_time_saved_seconds", 0) for s in sessions)
            sessions_with_switch = len([s for s in sessions if s.get("switch_button_pressed", False)])
            switch_rate = (sessions_with_switch / total_sessions) if total_sessions > 0 else 0.0
            
            # Deploy frequency metrics
            if patterns:
                # Most common deploy commands
                command_counts = {}
                for pattern in patterns:
                    cmd = pattern["deploy_command"]
                    command_counts[cmd] = command_counts.get(cmd, 0) + 1
                
                most_common_commands = sorted(command_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                
                # Time of day analysis
                time_of_day_counts = {}
                for pattern in patterns:
                    tod = pattern["time_of_day"]
                    time_of_day_counts[tod] = time_of_day_counts.get(tod, 0) + 1
                
                # Calculate average frequency
                avg_deploys_per_day = total_deploys / last_n_days
            else:
                most_common_commands = []
                time_of_day_counts = {}
                avg_deploys_per_day = 0.0
            
            # Productivity scores
            productivity_scores = [s.get("productivity_score", 0) for s in sessions if s.get("productivity_score")]
            avg_productivity_score = sum(productivity_scores) / len(productivity_scores) if productivity_scores else 0.0
            
            summary = {
                "project_name": project_name,
                "analysis_period_days": last_n_days,
                "timestamp": datetime.now().isoformat(),
                
                # Session metrics
                "total_sessions": total_sessions,
                "total_time_saved_minutes": total_time_saved / 60,
                "switch_button_usage_rate": switch_rate,
                "avg_productivity_score": avg_productivity_score,
                
                # Deploy pattern metrics
                "total_deploys": total_deploys,
                "avg_deploys_per_day": avg_deploys_per_day,
                "most_common_commands": most_common_commands,
                "deploy_time_patterns": time_of_day_counts,
                
                # Efficiency metrics
                "avg_time_saved_per_session_minutes": (total_time_saved / total_sessions / 60) if total_sessions > 0 else 0.0,
                "productivity_improvement_rate": switch_rate * 100  # Percentage of sessions where user engaged
            }
            
            logger.info("✅ [ANALYTICS] Deploy analytics summary generated", 
                       project=project_name,
                       total_sessions=total_sessions,
                       total_deploys=total_deploys,
                       switch_rate=f"{switch_rate:.1%}")
            
            return summary
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to generate deploy analytics summary", 
                        project=project_name, error=str(e))
            return {
                "project_name": project_name,
                "analysis_period_days": last_n_days,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_recent_deploy_sessions(self, project_name: str, days: int = 30) -> List[Dict[str, Any]]:
        """
        📊 PHASE 2: Get recent deploy sessions for analytics
        """
        try:
            analytics_dir = self._get_analytics_dir(project_name)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            sessions = []
            
            # Load data from multiple months if needed
            current_month = end_date.replace(day=1)
            while current_month >= start_date.replace(day=1):
                month_key = current_month.strftime("%Y-%m")
                sessions_file = analytics_dir / f"sessions_{month_key}.json"
                
                if sessions_file.exists():
                    with open(sessions_file, 'r') as f:
                        month_data = json.load(f)
                        month_sessions = month_data.get("deploy_sessions", [])
                        
                        # Filter by date range
                        for session in month_sessions:
                            session_date = datetime.fromisoformat(session["session_start"].replace('Z', '+00:00'))
                            if start_date <= session_date <= end_date:
                                sessions.append(session)
                
                # Move to previous month
                if current_month.month == 1:
                    current_month = current_month.replace(year=current_month.year - 1, month=12)
                else:
                    current_month = current_month.replace(month=current_month.month - 1)
            
            logger.debug("📊 [ANALYTICS] Retrieved recent deploy sessions", 
                        project=project_name, 
                        sessions_count=len(sessions),
                        days=days)
            
            return sessions
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to get recent deploy sessions", 
                        project=project_name, error=str(e))
            return []
    
    async def get_active_session_for_project(self, project_name: str) -> Optional[str]:
        """
        📊 PHASE 2: Get active session ID for a project (used for Switch tracking)
        """
        for session_id, session in self.active_sessions.items():
            if session.project_name == project_name and session.session_status == "active":
                return session_id
        return None
    
    async def update_session_task_counts(self, session_id: str, tasks_suggested: int = 0, tasks_accepted: int = 0) -> bool:
        """
        📊 PHASE 2: Update task suggestion and acceptance counts for a session
        """
        if session_id not in self.active_sessions:
            logger.warning("⚠️ [ANALYTICS] Session not found for task count update", session_id=session_id)
            return False
        
        try:
            session = self.active_sessions[session_id]
            if tasks_suggested > 0:
                session.tasks_suggested += tasks_suggested
            if tasks_accepted > 0:
                session.tasks_accepted += tasks_accepted
            
            logger.debug("📊 [ANALYTICS] Session task counts updated", 
                        session_id=session_id,
                        suggested=session.tasks_suggested,
                        accepted=session.tasks_accepted)
            
            return True
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to update session task counts", 
                        session_id=session_id, error=str(e))
            return False

    # 📊 PHASE 2: FRONTEND API METHODS
    # These methods provide the interface that the frontend analytics dashboard expects
    
    async def get_productivity_overview(self, last_n_days: int = 30) -> Dict[str, Any]:
        """
        📊 PHASE 2: Get cross-project productivity overview
        Called by frontend analytics dashboard
        """
        logger.info("📊 [ANALYTICS] Getting productivity overview", days=last_n_days)
        
        try:
            # Get all project directories
            projects = []
            if self.projects_root.exists():
                for project_dir in self.projects_root.iterdir():
                    if project_dir.is_dir() and not project_dir.name.startswith('.'):
                        projects.append(project_dir.name.replace("_", " "))
            
            # Aggregate metrics across all projects
            total_time_saved_minutes = 0
            total_sessions = 0
            total_deploys = 0
            switch_presses = 0
            
            project_summaries = []
            
            for project_name in projects:
                try:
                    # Get deploy analytics for this project
                    deploy_data = await self.get_deploy_analytics_summary(project_name, last_n_days)
                    
                    if deploy_data.get("total_sessions", 0) > 0:
                        project_summaries.append({
                            "project_name": project_name,
                            "sessions": deploy_data.get("total_sessions", 0),
                            "time_saved_minutes": deploy_data.get("total_time_saved_minutes", 0),
                            "switch_rate": deploy_data.get("switch_button_usage_rate", 0.0)
                        })
                        
                        # Add to totals
                        total_time_saved_minutes += deploy_data.get("total_time_saved_minutes", 0)
                        total_sessions += deploy_data.get("total_sessions", 0)
                        total_deploys += deploy_data.get("total_deploys", 0)
                        switch_presses += deploy_data.get("sessions_with_switch", 0)
                
                except Exception as project_error:
                    logger.warning("⚠️ [ANALYTICS] Failed to get data for project", 
                                 project=project_name, error=str(project_error))
                    continue
            
            # Calculate overall metrics
            overall_switch_rate = (switch_presses / total_sessions) if total_sessions > 0 else 0.0
            avg_time_saved_per_session = (total_time_saved_minutes / total_sessions) if total_sessions > 0 else 0.0
            productivity_improvement_rate = overall_switch_rate * 100  # Simple metric
            
            overview = {
                "period_days": last_n_days,
                "generated_at": datetime.now().isoformat(),
                "total_time_saved_minutes": total_time_saved_minutes,
                "total_sessions": total_sessions,
                "total_deploys": total_deploys,
                "total_projects": len(project_summaries),
                "overall_switch_rate": overall_switch_rate,
                "avg_time_saved_per_session_minutes": avg_time_saved_per_session,
                "productivity_improvement_rate": productivity_improvement_rate,
                "project_summaries": project_summaries[:10],  # Top 10 projects
                "key_insights": self._generate_productivity_insights(
                    total_time_saved_minutes, total_sessions, overall_switch_rate
                )
            }
            
            logger.info("✅ [ANALYTICS] Productivity overview generated", 
                       projects_count=len(project_summaries),
                       total_sessions=total_sessions,
                       time_saved_hours=total_time_saved_minutes/60)
            
            return overview
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to generate productivity overview", error=str(e))
            return {
                "period_days": last_n_days,
                "generated_at": datetime.now().isoformat(),
                "total_time_saved_minutes": 0,
                "total_sessions": 0,
                "total_deploys": 0,
                "total_projects": 0,
                "overall_switch_rate": 0.0,
                "avg_time_saved_per_session_minutes": 0.0,
                "productivity_improvement_rate": 0.0,
                "project_summaries": [],
                "key_insights": ["No data available for the selected period"]
            }
    
    def _generate_productivity_insights(self, time_saved_minutes: float, 
                                      total_sessions: int, switch_rate: float) -> List[str]:
        """Generate key insights for productivity overview"""
        insights = []
        
        if time_saved_minutes > 0:
            hours_saved = time_saved_minutes / 60
            if hours_saved >= 1:
                insights.append(f"You've saved {hours_saved:.1f} hours through productive task switching")
            else:
                insights.append(f"You've saved {time_saved_minutes:.0f} minutes through productive task switching")
        
        if switch_rate > 0.7:
            insights.append("Excellent productivity! You're switching to tasks in over 70% of deploy sessions")
        elif switch_rate > 0.4:
            insights.append("Good productivity habits! Consider switching to tasks more often during deployments")
        elif switch_rate > 0.1:
            insights.append("There's opportunity to boost productivity by switching to tasks during deploys")
        else:
            insights.append("Try using the Switch button during deployments to maximize your productivity")
        
        if total_sessions > 20:
            insights.append(f"You're actively deploying with {total_sessions} sessions - great development activity!")
        elif total_sessions > 5:
            insights.append("Good development momentum with regular deployment activity")
        
        if not insights:
            insights.append("Start using DeployBot during deployments to track your productivity gains")
        
        return insights
    
    async def get_deploy_analytics(self, project_name: str, last_n_days: int = 30) -> Dict[str, Any]:
        """
        📊 PHASE 2: Get deploy analytics for a specific project
        Called by frontend analytics dashboard (wrapper for get_deploy_analytics_summary)
        """
        logger.info("📊 [ANALYTICS] Getting deploy analytics", 
                   project=project_name, days=last_n_days)
        
        return await self.get_deploy_analytics_summary(project_name, last_n_days)
    
    async def get_session_status(self, project_name: str) -> Dict[str, Any]:
        """
        📊 PHASE 2: Get current session status for a project
        Called by frontend analytics dashboard
        """
        logger.info("📊 [ANALYTICS] Getting session status", project=project_name)
        
        try:
            # Find active session for the project
            active_session = None
            for session_id, session in self.active_sessions.items():
                if session.project_name == project_name and session.session_status == "active":
                    active_session = {
                        "session_id": session_id,
                        "project_name": session.project_name,
                        "deploy_command": session.deploy_command,
                        "session_start": session.session_start,
                        "timer_duration_seconds": session.timer_duration_seconds,
                        "cloud_propagation_time_seconds": session.cloud_propagation_time_seconds,
                        "tasks_suggested": session.tasks_suggested,
                        "tasks_accepted": session.tasks_accepted,
                        "switch_button_pressed": session.switch_button_pressed,
                        "switch_timestamp": session.switch_timestamp,
                        "session_status": session.session_status
                    }
                    break
            
            # Get recent completed sessions for context
            recent_sessions = await self._get_recent_deploy_sessions(project_name, days=7)
            
            result = {
                "project_name": project_name,
                "current_session": active_session,
                "has_active_session": active_session is not None,
                "recent_sessions_count": len(recent_sessions),
                "last_session_time": recent_sessions[0]["session_start"] if recent_sessions else None,
                "checked_at": datetime.now().isoformat()
            }
            
            logger.info("✅ [ANALYTICS] Session status retrieved", 
                       project=project_name,
                       has_active=active_session is not None,
                       recent_count=len(recent_sessions))
            
            return result
            
        except Exception as e:
            logger.error("❌ [ANALYTICS] Failed to get session status", 
                        project=project_name, error=str(e))
            return {
                "project_name": project_name,
                "current_session": None,
                "has_active_session": False,
                "recent_sessions_count": 0,
                "last_session_time": None,
                "checked_at": datetime.now().isoformat(),
                "error": str(e)
            }

# Global analytics manager instance
analytics_manager = AnalyticsManager() 