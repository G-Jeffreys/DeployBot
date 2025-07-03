#!/usr/bin/env python3
"""
Task Selection and Management for DeployBot

This module handles:
- TODO.md parsing and analysis
- Task selection logic (both heuristic and LLM-assisted)
- Task filtering based on context and tags
- App mapping and redirection logic
"""

import asyncio
import json
import os
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import structlog

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# OpenAI integration - Updated for modern client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    logger = structlog.get_logger()
    logger.info("✅ [TASKS] OpenAI library available for LLM task selection")
except ImportError:
    OPENAI_AVAILABLE = False
    logger = structlog.get_logger()
    logger.warning("⚠️ [TASKS] OpenAI library not available - using heuristic fallback only")

class TaskSelector:
    """Intelligent task selection system for DeployBot"""
    
    def __init__(self):
        self.openai_client = None
        self.task_cache = {}  # Cache for LLM responses
        self.tag_app_mapping = {
            "writing": "Bear",
            "creative": "Figma", 
            "design": "Figma",
            "research": "Safari",
            "code": "VSCode",
            "backend": "Terminal",
            "business": "Notion",
            "todo": "Things",
            "notes": "Bear",
            "email": "Mail"
        }
        
        # Initialize OpenAI if available
        self._initialize_openai()
        
        # Initialize analytics integration
        from analytics import analytics_manager
        self.analytics = analytics_manager
        
        logger.info("🎯 [TASKS] TaskSelector initialized", 
                   openai_enabled=self.openai_client is not None,
                   analytics_enabled=True)
    
    def _initialize_openai(self):
        """Initialize OpenAI client with API key"""
        if not OPENAI_AVAILABLE:
            logger.info("📡 [TASKS] OpenAI library not available - using heuristic fallback only")
            return
        
        # Check for API key in environment
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("⚠️ [TASKS] OPENAI_API_KEY not found in environment - LLM features disabled")
            logger.info("💡 [TASKS] Add OPENAI_API_KEY to your .env file to enable AI task selection")
            return
        
        try:
            # Initialize modern OpenAI client
            self.openai_client = OpenAI(api_key=api_key)
            logger.info("✅ [TASKS] OpenAI client initialized successfully")
            logger.info("🤖 [TASKS] AI-powered task selection enabled")
        except Exception as e:
            logger.error("❌ [TASKS] Failed to initialize OpenAI client", error=str(e))
            self.openai_client = None

    async def parse_todo_file(self, todo_file_path: Path) -> List[Dict[str, Any]]:
        """Parse TODO.md file and extract tasks with tags and metadata"""
        logger.info("📋 [TASKS] Parsing TODO.md file", file_path=str(todo_file_path))
        
        tasks = []
        
        try:
            if not todo_file_path.exists():
                logger.warning("⚠️ [TASKS] TODO.md file not found", file_path=str(todo_file_path))
                return tasks
            
            content = todo_file_path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            task_id = 1
            current_section = "Unknown"
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Track sections (## Pending Tasks, ## Completed Tasks, etc.)
                if line.startswith('##'):
                    current_section = line.replace('##', '').strip()
                    continue
                
                # Look for task lines (- [ ] or - [x])
                if line.startswith('- ['):
                    completed = line.startswith('- [x]')
                    
                    # Extract task text (remove checkbox part)
                    if completed:
                        task_text = line[5:].strip()  # Remove "- [x] "
                    else:
                        task_text = line[5:].strip()  # Remove "- [ ] "
                    
                    # Extract hashtags using regex
                    tags = re.findall(r'#\w+', task_text)
                    
                    # Remove tags from task text for clean display
                    clean_text = re.sub(r'\s*#\w+', '', task_text).strip()
                    
                    # Determine app based on tags
                    app = self._determine_app_for_task(tags, clean_text)
                    
                    # Calculate task priority based on tags
                    priority = self._calculate_task_priority(tags, clean_text)
                    
                    # Estimate duration from tags
                    estimated_duration = self._estimate_task_duration(tags, clean_text)
                    
                    task = {
                        "id": task_id,
                        "text": clean_text,
                        "original_text": task_text,
                        "tags": tags,
                        "completed": completed,
                        "app": app,
                        "section": current_section,
                        "line_number": line_num,
                        "priority": priority,
                        "estimated_duration": estimated_duration,
                        "parsed_at": datetime.now().isoformat()
                    }
                    
                    tasks.append(task)
                    task_id += 1
            
            logger.info("✅ [TASKS] TODO.md parsed successfully", 
                       total_tasks=len(tasks),
                       pending_tasks=len([t for t in tasks if not t['completed']]),
                       completed_tasks=len([t for t in tasks if t['completed']]))
            
        except Exception as e:
            logger.error("❌ [TASKS] Failed to parse TODO.md file", 
                        file_path=str(todo_file_path), error=str(e))
        
        return tasks

    def _determine_app_for_task(self, tags: List[str], task_text: str) -> str:
        """Determine the appropriate app for a task based on tags and content"""
        
        # Check tags first (highest priority)
        for tag in tags:
            clean_tag = tag.replace('#', '').lower()
            if clean_tag in self.tag_app_mapping:
                logger.debug("📱 [TASKS] App determined by tag", tag=clean_tag, app=self.tag_app_mapping[clean_tag])
                return self.tag_app_mapping[clean_tag]
        
        # Fallback: keyword analysis in task text
        task_lower = task_text.lower()
        
        keyword_mappings = {
            "write": "Bear",
            "document": "Bear", 
            "blog": "Bear",
            "note": "Bear",
            "design": "Figma",
            "mockup": "Figma",
            "wireframe": "Figma",
            "code": "VSCode",
            "develop": "VSCode",
            "implement": "VSCode",
            "research": "Safari",
            "google": "Safari",
            "investigate": "Safari",
            "email": "Mail",
            "call": "FaceTime",
            "meeting": "Zoom"
        }
        
        for keyword, app in keyword_mappings.items():
            if keyword in task_lower:
                logger.debug("📱 [TASKS] App determined by keyword", keyword=keyword, app=app)
                return app
        
        # Default app
        logger.debug("📱 [TASKS] Using default app", app="Notion")
        return "Notion"

    def _calculate_task_priority(self, tags: List[str], task_text: str) -> int:
        """Calculate task priority (1-10, higher = more important)"""
        priority = 5  # Base priority
        
        tag_priorities = {
            "#urgent": 3,
            "#important": 2,
            "#high": 2,
            "#low": -2,
            "#someday": -3,
            "#short": 1,  # Short tasks get slight priority boost
            "#solo": 1,   # Solo tasks easier to start during deploys
        }
        
        for tag in tags:
            if tag.lower() in tag_priorities:
                priority += tag_priorities[tag.lower()]
        
        # Keyword-based priority adjustments
        high_priority_keywords = ["urgent", "asap", "deadline", "important"]
        low_priority_keywords = ["someday", "maybe", "nice to have"]
        
        task_lower = task_text.lower()
        for keyword in high_priority_keywords:
            if keyword in task_lower:
                priority += 2
                break
        
        for keyword in low_priority_keywords:
            if keyword in task_lower:
                priority -= 2
                break
        
        # Clamp between 1-10
        return max(1, min(10, priority))

    def _estimate_task_duration(self, tags: List[str], task_text: str) -> int:
        """Estimate task duration in minutes based on tags and content"""
        
        # Tag-based duration estimates
        for tag in tags:
            tag_lower = tag.lower()
            if tag_lower == "#short":
                return 20  # 20 minutes
            elif tag_lower == "#long":
                return 120  # 2 hours
            elif tag_lower == "#quick":
                return 10  # 10 minutes
        
        # Keyword-based estimates
        quick_keywords = ["quick", "simple", "update", "check", "review"]
        long_keywords = ["implement", "design", "research", "write", "create", "build"]
        
        task_lower = task_text.lower()
        
        for keyword in quick_keywords:
            if keyword in task_lower:
                return 15
        
        for keyword in long_keywords:
            if keyword in task_lower:
                return 90
        
        # Default estimate
        return 45  # 45 minutes

    async def select_best_task(self, project_path: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select the best alternative task for the current context
        Uses LLM if available, falls back to heuristic selection
        Now enhanced with analytics-driven learning
        """
        logger.info("🎯 [TASKS] Selecting best task for context", 
                   project_path=project_path, context=context)
        
        # Load tasks from TODO.md
        todo_file = Path(project_path) / "TODO.md"
        tasks = await self.parse_todo_file(todo_file)
        
        if not tasks:
            logger.warning("⚠️ [TASKS] No tasks found in TODO.md", file_path=str(todo_file))
            return None
        
        # Filter to pending tasks only
        pending_tasks = [task for task in tasks if not task['completed']]
        
        if not pending_tasks:
            logger.warning("⚠️ [TASKS] No pending tasks found")
            return None
        
        # Apply context-based filtering
        filtered_tasks = self._filter_tasks_by_context(pending_tasks, context)
        
        if not filtered_tasks:
            logger.warning("⚠️ [TASKS] No suitable tasks after filtering")
            return None
        
        # 📊 ANALYTICS ENHANCEMENT: Load analytics data for intelligent selection
        project_name = context.get('project_name', Path(project_path).name)
        analytics_data = await self.analytics.get_task_analytics(project_name)
        
        # Ensure analytics_data is never None
        if analytics_data is None:
            analytics_data = {}
        
        logger.info("📊 [TASKS] Analytics data loaded for task selection", 
                   project=project_name,
                   suggestions_count=analytics_data.get('suggestions_count', 0),
                   acceptance_rate=analytics_data.get('acceptance_rate', 0.0))
        
        # Try LLM selection first, fallback to heuristic
        if self.openai_client and context.get("use_llm", True):
            try:
                selected_task = await self._select_task_with_llm(filtered_tasks, context, analytics_data)
                if selected_task:
                    logger.info("✅ [TASKS] Task selected using LLM", task=selected_task['text'])
                    
                    # 📊 ANALYTICS: Record task suggestion
                    suggestion_id = await self.analytics.record_task_suggestion(
                        selected_task, project_name, context
                    )
                    
                    # Store suggestion ID for interaction tracking
                    selected_task['suggestion_id'] = suggestion_id
                    
                    return selected_task
            except Exception as e:
                logger.warning("⚠️ [TASKS] LLM selection failed, using heuristic fallback", error=str(e))
        
        # Heuristic fallback selection
        selected_task = self._select_task_heuristic(filtered_tasks, context)
        logger.info("✅ [TASKS] Task selected using heuristic method", task=selected_task['text'])
        
        # 📊 ANALYTICS: Record task suggestion (heuristic)
        suggestion_id = await self.analytics.record_task_suggestion(
            selected_task, project_name, context
        )
        
        # Store suggestion ID for interaction tracking
        selected_task['suggestion_id'] = suggestion_id
        
        return selected_task

    def _filter_tasks_by_context(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter tasks based on deployment context and preferences"""
        logger.debug("🔍 [TASKS] Filtering tasks by context", task_count=len(tasks), context=context)
        
        filtered = []
        
        for task in tasks:
            should_include = True
            tags = [tag.lower() for tag in task.get('tags', [])]
            
            # During deploy: exclude backend tasks
            if context.get('deploy_active', False):
                if '#backend' in tags:
                    logger.debug("🚫 [TASKS] Excluding backend task during deploy", task=task['text'])
                    should_include = False
                    continue
            
            # Time-based filtering
            timer_duration = context.get('timer_duration', 1800)  # 30 minutes default
            estimated_duration = task.get('estimated_duration', 45)
            
            # For short timers, prefer short tasks
            if timer_duration <= 900:  # 15 minutes or less
                if '#long' in tags or estimated_duration > 60:
                    logger.debug("🚫 [TASKS] Excluding long task for short timer", task=task['text'])
                    should_include = False
                    continue
            
            # Time of day considerations
            current_hour = datetime.now().hour
            
            # Creative tasks better in morning/afternoon  
            if '#creative' in tags and (current_hour < 8 or current_hour > 18):
                task['priority'] = max(1, task.get('priority', 5) - 1)
            
            # Research tasks good anytime
            if '#research' in tags:
                task['priority'] = task.get('priority', 5) + 1
            
            # Writing tasks good for focus periods
            if '#writing' in tags and context.get('deploy_active', False):
                task['priority'] = task.get('priority', 5) + 2
            
            if should_include:
                filtered.append(task)
        
        # Sort by priority (highest first)
        filtered.sort(key=lambda t: t.get('priority', 5), reverse=True)
        
        logger.debug("✅ [TASKS] Task filtering complete", 
                    original_count=len(tasks), 
                    filtered_count=len(filtered))
        
        return filtered

    async def _select_task_with_llm(self, tasks: List[Dict[str, Any]], context: Dict[str, Any], analytics_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Use OpenAI to intelligently select the best task"""
        logger.info("🤖 [TASKS] Using LLM for task selection", task_count=len(tasks))
        
        # Create cache key for this selection
        task_texts = [task['text'] for task in tasks]
        cache_key = hash(tuple(task_texts) + tuple(sorted(context.items())))
        
        # Check cache first
        if cache_key in self.task_cache:
            logger.debug("📦 [TASKS] Using cached LLM response")
            cached_result = self.task_cache[cache_key]
            # Find the task that matches the cached selection
            for task in tasks:
                if task['text'] == cached_result['task_text']:
                    return task
        
        # Prepare context for LLM
        context_str = self._format_context_for_llm(context)
        tasks_str = self._format_tasks_for_llm(tasks)
        
        # 📊 ANALYTICS ENHANCEMENT: Build analytics context for LLM
        analytics_context = self._build_analytics_context_for_llm(tasks, analytics_data or {})
        
        prompt = f"""You are DeployBot, an AI assistant that helps developers stay productive during deployment wait times.

CONTEXT:
{context_str}

📊 HISTORICAL ANALYTICS:
{analytics_context}

AVAILABLE TASKS:
{tasks_str}

INSTRUCTIONS:
Select the SINGLE best task for this situation. Consider:
1. Deploy context (avoid backend tasks during deploys)
2. Time available ({context.get('timer_duration', 1800)} seconds)
3. Current time of day
4. Task priority and difficulty
5. Historical acceptance patterns (avoid tasks ignored 3+ times recently)
6. What would be most productive right now

Use the historical analytics to avoid suggesting tasks that have been repeatedly ignored.
If a task type has low acceptance rates, prefer alternatives unless there are no other options.

Respond with ONLY a JSON object:
{{
    "selected_task": "exact task text here",
    "reasoning": "brief explanation why this is the best choice considering historical patterns",
    "confidence": 0.8
}}"""

        try:
            response = await asyncio.wait_for(
                self._call_openai_api(prompt),
                timeout=10.0  # 10 second timeout
            )
            
            # Parse response
            result = self._parse_llm_response(response, tasks)
            
            if result:
                # Cache the result
                self.task_cache[cache_key] = {
                    "task_text": result['text'],
                    "reasoning": response.get('reasoning', ''),
                    "timestamp": datetime.now().isoformat()
                }
                
                logger.info("✅ [TASKS] LLM task selection successful", 
                           task=result['text'],
                           reasoning=response.get('reasoning', ''))
                return result
            
        except asyncio.TimeoutError:
            logger.warning("⏰ [TASKS] LLM selection timed out")
        except Exception as e:
            logger.error("❌ [TASKS] LLM selection failed", error=str(e))
        
        return None

    async def _call_openai_api(self, prompt: str) -> Dict[str, Any]:
        """Make API call to OpenAI with proper error handling - Updated for modern client"""
        
        # Safety check: ensure OpenAI client is available
        if not self.openai_client:
            logger.error("❌ [TASKS] OpenAI client not available for API call")
            raise Exception("OpenAI client not initialized")
        
        # Type assertion - we know client is not None after the check above
        client = self.openai_client
        
        try:
            logger.debug("🤖 [TASKS] Making OpenAI API call...")
            
            # Use the modern OpenAI client API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
            )
            
            # Safely extract content from response
            if not response or not response.choices or not response.choices[0]:
                logger.error("❌ [TASKS] Invalid response structure from OpenAI")
                raise Exception("Invalid OpenAI response structure")
            
            message_content = response.choices[0].message.content
            if message_content is None:
                logger.error("❌ [TASKS] Empty content in OpenAI response")
                raise Exception("Empty content in OpenAI response")
            
            content = message_content.strip()
            logger.debug("✅ [TASKS] OpenAI API response received", content_length=len(content))
            
            # Try to parse as JSON
            try:
                parsed_response = json.loads(content)
                logger.debug("✅ [TASKS] Response parsed as JSON successfully")
                return parsed_response
            except json.JSONDecodeError:
                # If not valid JSON, extract the task name manually
                logger.warning("⚠️ [TASKS] LLM response not valid JSON, attempting manual parsing")
                logger.debug("🔍 [TASKS] Raw response content", content=content)
                return {"selected_task": content, "reasoning": "Manual extraction", "confidence": 0.5}
        
        except Exception as e:
            logger.error("❌ [TASKS] OpenAI API call failed", error=str(e))
            raise

    def _parse_llm_response(self, response: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Parse LLM response and find matching task"""
        
        selected_task_text = response.get('selected_task', '')
        if not selected_task_text:
            return None
        
        # Find exact match first
        for task in tasks:
            if task['text'] == selected_task_text:
                return task
        
        # Fuzzy matching if exact match fails
        selected_lower = selected_task_text.lower()
        for task in tasks:
            if selected_lower in task['text'].lower() or task['text'].lower() in selected_lower:
                logger.debug("🔍 [TASKS] Using fuzzy match for LLM selection", 
                           selected=selected_task_text, matched=task['text'])
                return task
        
        logger.warning("⚠️ [TASKS] Could not match LLM selection to available tasks", 
                      selected=selected_task_text)
        return None

    def _select_task_heuristic(self, tasks: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback heuristic task selection when LLM is not available"""
        logger.info("🎲 [TASKS] Using heuristic task selection", task_count=len(tasks))
        
        # Already filtered and sorted by priority in _filter_tasks_by_context
        # Apply additional heuristic scoring
        
        for task in tasks:
            score = task.get('priority', 5)
            tags = [tag.lower() for tag in task.get('tags', [])]
            
            # Boost solo tasks during deploys (easier to start/stop)
            if context.get('deploy_active', False) and '#solo' in tags:
                score += 2
            
            # Boost short tasks for short timers
            timer_duration = context.get('timer_duration', 1800)
            if timer_duration <= 1800 and '#short' in tags:  # 30 minutes or less
                score += 1
            
            # Boost creative/writing tasks (good for focus)
            if '#creative' in tags or '#writing' in tags:
                score += 1
            
            task['heuristic_score'] = score
        
        # Sort by heuristic score
        tasks.sort(key=lambda t: t.get('heuristic_score', 0), reverse=True)
        
        selected = tasks[0]
        logger.info("✅ [TASKS] Heuristic selection complete", 
                   task=selected['text'],
                   score=selected.get('heuristic_score', 0))
        
        return selected

    def _format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """Format context information for LLM prompt"""
        lines = []
        
        if context.get('deploy_active'):
            lines.append(f"- Deploy in progress: {context.get('deploy_command', 'unknown command')}")
            lines.append(f"- Timer duration: {context.get('timer_duration', 1800)} seconds")
        
        lines.append(f"- Current time: {datetime.now().strftime('%H:%M on %A')}")
        
        if context.get('project_name'):
            lines.append(f"- Project: {context['project_name']}")
        
        return '\n'.join(lines)

    def _format_tasks_for_llm(self, tasks: List[Dict[str, Any]]) -> str:
        """Format task list for LLM prompt"""
        lines = []
        
        for i, task in enumerate(tasks[:10], 1):  # Limit to top 10 tasks
            tags_str = ' '.join(task.get('tags', []))
            duration = task.get('estimated_duration', 45)
            priority = task.get('priority', 5)
            
            lines.append(f"{i}. {task['text']}")
            lines.append(f"   Tags: {tags_str}")
            lines.append(f"   Duration: ~{duration}min, Priority: {priority}/10")
            lines.append("")
        
        return '\n'.join(lines)
    
    def _build_analytics_context_for_llm(self, tasks: List[Dict[str, Any]], analytics_data: Dict[str, Any]) -> str:
        """
        Build analytics context string for LLM prompts
        📊 ANALYTICS ENHANCEMENT: Provides historical data to improve task selection
        """
        context_lines = []
        
        # Overall project analytics
        if analytics_data.get('suggestions_count', 0) > 0:
            acceptance_rate = analytics_data.get('acceptance_rate', 0.0)
            context_lines.append(f"- Overall task acceptance rate: {acceptance_rate:.0%}")
        
        # Recent ignore patterns (key feature from requirements)
        recent_ignores = analytics_data.get('recent_ignores_30d', 0)
        if recent_ignores >= 3:
            context_lines.append(f"- Warning: {recent_ignores} tasks ignored in last 30 days - consider different approach")
        
        # Task completion patterns
        task_patterns = analytics_data.get('task_patterns', {})
        if task_patterns.get('total_completed', 0) > 0:
            avg_completion_time = task_patterns.get('avg_completion_time', 0)
            if avg_completion_time > 0:
                context_lines.append(f"- Average task completion time: {avg_completion_time/60:.1f} minutes")
            
            avg_productivity = task_patterns.get('avg_productivity_score', 0)
            if avg_productivity > 0:
                context_lines.append(f"- Average productivity score: {avg_productivity:.2f}/1.0")
        
        # Response time patterns
        avg_response_time = analytics_data.get('avg_response_time', 0)
        if avg_response_time > 0:
            if avg_response_time < 30:
                context_lines.append("- User typically responds quickly to suggestions")
            elif avg_response_time > 120:
                context_lines.append("- User typically takes time to consider suggestions")
        
        # Provide guidance if no patterns yet
        if not context_lines:
            context_lines.append("- No significant historical patterns yet - focus on task priority and context")
        
        return '\n'.join(context_lines)

    async def get_task_statistics(self, project_path: str) -> Dict[str, Any]:
        """Get statistics about tasks in the project"""
        todo_file = Path(project_path) / "TODO.md"
        tasks = await self.parse_todo_file(todo_file)
        
        if not tasks:
            return {"error": "No tasks found"}
        
        pending_tasks = [t for t in tasks if not t['completed']]
        completed_tasks = [t for t in tasks if t['completed']]
        
        # Tag analysis
        all_tags = []
        for task in tasks:
            all_tags.extend(task.get('tags', []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Duration analysis
        total_estimated_time = sum(task.get('estimated_duration', 45) for task in pending_tasks)
        
        return {
            "total_tasks": len(tasks),
            "pending_tasks": len(pending_tasks),
            "completed_tasks": len(completed_tasks),
            "completion_rate": len(completed_tasks) / len(tasks) if tasks else 0,
            "estimated_remaining_time": total_estimated_time,
            "most_common_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            "avg_priority": sum(task.get('priority', 5) for task in pending_tasks) / len(pending_tasks) if pending_tasks else 0
        }

# Global instance
task_selector = TaskSelector() 