# 🚀 DeployBot: Complete System Architecture & Specification

**Version**: 1.0.0  
**Status**: Production Ready  
**Architecture**: Electron + React + Python LangGraph + WebSocket  
**Platform**: macOS (with Windows/Linux foundation)

---

## 📋 **Executive Summary**

DeployBot is a sophisticated desktop productivity assistant that detects backend deployment events and intelligently redirects developers to productive alternative tasks during deployment wait periods. The system features enterprise-grade architecture with real-time communication, AI-powered task selection, and production-ready error handling.

**Core Innovation**: While local deployment commands complete quickly (30 seconds), cloud propagation takes 10-30 minutes. DeployBot fills this productivity gap with intelligent task suggestions tailored to the waiting period.

---

## 🏗️ **System Architecture**

### **High-Level Architecture**
```
┌─────────────────┐    WebSocket     ┌─────────────────┐
│   Electron UI   │ ←──────────────→ │  Python Backend │
│                 │    Real-time     │   (LangGraph)   │
│ • React Frontend│    Bidirectional │ • AI Task Agent │
│ • Process Mgmt  │    Communication │ • Deploy Monitor│
│ • Notifications │                  │ • Timer System  │
└─────────────────┘                  └─────────────────┘
         │                                     │
         │                                     │
    ┌────▼────┐                          ┌────▼────┐
    │ Projects│                          │File Logs│
    │ • TODO  │                          │• Deploy │
    │ • Config│                          │• Activity│
    └─────────┘                          └─────────┘
```

### **Component Stack**
- **Frontend**: Electron 29.1.4 + React 18.2.0 + Tailwind CSS 3.4.3
- **Backend**: Python 3.12 + LangGraph + OpenAI API + WebSocket Server
- **Communication**: WebSocket (ws://localhost:8765) with automatic reconnection
- **Data Layer**: Filesystem-based with JSON configs and markdown task lists
- **Process Management**: Sophisticated lifecycle management with health monitoring

---

## 🎯 **Product Requirements & Goals**

### **Primary Use Case**
1. Developer runs deployment command: `deploybot firebase deploy --only functions`
2. Local command completes in ~30 seconds
3. **DeployBot detects completion** and knows cloud propagation will take 15+ minutes
4. **AI selects optimal alternative task** from project's TODO.md
5. **System redirects focus** to productive work during waiting period
6. **Timer manages the wait period** with notifications and status updates

### **Target Users**
- **Primary**: Individual developers working on projects with cloud deployments
- **Secondary**: Development teams using shared productivity patterns
- **Use Pattern**: Episodic use during deployment cycles (multiple times per day)

### **Success Metrics**
- **Productivity Recovery**: 70%+ of deploy wait time converted to productive work
- **Context Switching Speed**: <5 seconds from deploy completion to task engagement
- **Task Relevance**: 80%+ of AI suggestions rated as contextually appropriate
- **Adoption**: Daily active usage during development cycles

---

## 🔧 **Detailed Component Architecture**

### **1. Electron Frontend (Production-Grade)**

#### **Main Process (`main/main.js` - 896 lines)**
**Sophisticated window management with custom notifications:**
- `createWindow()`: BrowserWindow management with dev/prod handling
- `createNotificationWindow()`: Custom notification system with positioning
- `setupIPC()`: Comprehensive inter-process communication
- `setupGlobalShortcuts()`: System-wide keyboard shortcuts
- `cleanup()`: Graceful shutdown with process termination

**Key Features:**
- **Custom Notification Windows**: macOS-style floating notifications with transparency and blur effects
- **Multi-Window Management**: Main app + floating notification windows with smart positioning
- **Development Mode Detection**: Automatic Vite dev server vs production build loading
- **Resource Management**: Proper icon loading for both development and packaged apps

#### **Process Manager (`main/process_manager.js` - 749 lines)**
**Enterprise-grade WebSocket client with resilience:**
```javascript
class ProcessManager extends EventEmitter {
  config: {
    maxStartupAttempts: 5,
    maxConnectionAttempts: 10,
    startupTimeout: 30000,
    connectionTimeout: 10000,
    healthCheckInterval: 15000,
    gracefulShutdownTimeout: 5000
  }
}
```

**Production Features:**
- **Automatic Reconnection**: Exponential backoff with connection attempt limits
- **Health Monitoring**: Continuous backend health checks with status reporting
- **Port Cleanup**: Intelligent port conflict resolution using `lsof`
- **Message Queuing**: Queue messages during disconnection with replay on reconnect
- **Process Lifecycle**: Complete startup/shutdown orchestration

#### **API Bridge (`main/preload.js` - 305 lines)**
**Comprehensive API exposure with security isolation:**
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  // Project Management
  project: { create, open, delete, list, validateCustomDirectory },
  
  // Task Management with AI
  tasks: { getSuggestions, redirectToTask, testSelection },
  
  // Deploy Monitoring
  monitoring: { start, stop, status, simulateDeploy },
  
  // Timer System
  timer: { start, stop, status },
  
  // Backend Communication
  backend: { ping, status },
  
  // Testing & Utilities
  testing: { week3Workflow, pythonBackend }
});
```

#### **React Application (`main/renderer/src/`)**
**Production React components with real-time integration:**

- **App.jsx (334 lines)**: Real-time WebSocket event handling, connection state management, project selection with persistent state, component orchestration with error boundaries

- **ProjectSelector.jsx (570 lines)**: Full CRUD operations for project management, custom directory support, backend integration with retry logic, real-time project loading with validation

- **TaskList.jsx (418 lines)**: Real TODO.md parsing via backend API, AI-powered task suggestions with OpenAI integration, smart app redirection, task statistics and completion tracking

- **Additional Components**: DeployStatus.jsx (real-time deploy monitoring), TimerDisplay.jsx (live timer updates), ActivityLog.jsx (real-time activity streaming), CustomNotification.jsx (rich notification UI)

### **2. Python Backend (AI-Powered)**

#### **Core LangGraph System (`backend/graph.py` - 1,221 lines)**
**Enterprise WebSocket server with comprehensive command processing:**

```python
# Real-time deploy detection workflow
async def on_deploy_detected(project_name, deploy_command, project_path):
    # 1. Update system state
    # 2. Focus DeployBot window
    # 3. Start deployment timer
    # 4. Check task availability
    # 5. Schedule unified notification (timer + task)
    # 6. Broadcast to frontend via WebSocket

# Command processing with full API coverage (42+ commands)
async def process_command(command: str, data: Dict) -> Dict:
    # Project management (create, list, load, delete)
    # Task operations (get-suggestions, redirect-to-task)
    # Deploy monitoring (start-monitoring, simulate-deploy)
    # Timer management (timer-start, timer-stop, timer-status)
    # Testing utilities (test-week3-workflow, ping)
```

**LangGraph Workflow:**
```python
# Sophisticated agent-based workflow
graph = StateGraph(DeployBotState)
graph.add_node("detect_deploy", detect_deploy)
graph.add_node("select_task", select_task)  
graph.add_node("start_timer", start_timer)
graph.add_edge("detect_deploy", "select_task")
graph.add_edge("select_task", "start_timer")
```

#### **AI Task Selection (`backend/tasks.py` - 620 lines)**
**Intelligent task selection with OpenAI integration:**

```python
class TaskSelector:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tag_app_mapping = {
            "writing": "Bear", "creative": "Figma", 
            "research": "Safari", "code": "VSCode",
            "backend": "Terminal", "business": "Notion"
        }
    
    async def select_best_task(self, project_path: str, context: Dict) -> Dict:
        # 1. Parse TODO.md with hashtag taxonomy
        # 2. Filter tasks by context (deploy_active, timer_duration)
        # 3. Use LLM for intelligent selection OR heuristic fallback
        # 4. Return task with app mapping and priority
```

**Task Selection Intelligence:**
- **TODO.md Parsing**: Full markdown parsing with hashtag extraction
- **Context Awareness**: Considers deploy status, timer duration, project type
- **AI Integration**: OpenAI GPT for semantic task selection with prompt engineering
- **Fallback Logic**: Sophisticated heuristic selection when AI unavailable
- **App Mapping**: Intelligent application routing based on task type and tags

#### **Project Management (`backend/project_manager.py` - 845 lines)**
**Comprehensive project lifecycle management:**

```python
class ProjectManager:
    # Enhanced with custom directory support
    async def create_project(self, project_data: Dict) -> Dict:
        # 1. Validate project name and custom directory
        # 2. Create directory structure (config.json, TODO.md, logs/)
        # 3. Initialize default configurations
        # 4. Register with directory mapping system
        # 5. Create activity logging
    
    # Full project discovery and loading
    async def list_projects(self) -> Dict:
        # 1. Scan default projects directory
        # 2. Load custom directory mappings
        # 3. Validate project structures
        # 4. Return enriched project metadata
```

**Advanced Features:**
- **Custom Directories**: Projects can be stored anywhere on filesystem
- **Project Discovery**: Intelligent scanning and validation
- **Configuration Management**: Rich JSON configs with task mappings
- **Activity Logging**: Comprehensive event tracking per project

#### **Deploy Monitoring (`backend/monitor.py` - 534 lines)**
**Sophisticated file-based deploy detection:**

```python
class DeployMonitor:
    async def _monitoring_loop(self):
        # 1. Monitor multiple project-specific deploy logs
        # 2. Parse deploy events with command extraction
        # 3. Trigger LangGraph workflow on detection
        # 4. Handle global fallback monitoring
    
    def _parse_deploy_line(self, line: str, project_name: str) -> Dict:
        # Smart parsing of deploy wrapper log entries:
        # timestamp DEPLOY: command_with_args
```

**Monitoring Features:**
- **Multi-Project Support**: Simultaneous monitoring of multiple projects
- **Smart Log Parsing**: Extracts commands, timestamps, and project context
- **File Position Tracking**: Efficient incremental log reading
- **Global Fallback**: Monitors `~/.deploybot/deploy_log.txt` for non-project commands

#### **Notification System (`backend/notification.py` - 994 lines)**
**Cross-platform notification system with rich templates:**

```python
class NotificationManager:
    # Sophisticated notification templates
    templates = {
        "deploy_detected": {"title": "🚀 Deploy Started"},
        "task_suggestion": {"title": "🎯 Task Suggestion"},
        "unified_suggestion": {"title": "🎯⏰ Task & Timer Update"},
        "timer_expiry": {"title": "⏰ Propagation Complete"}
    }
    
    async def notify_unified_suggestion(self, project_name, timer_info, task, context):
        # 1. Combine timer status with AI task recommendation
        # 2. Create rich notification with multiple action buttons
        # 3. Send via WebSocket to trigger custom Electron windows
        # 4. Handle user responses and callback actions
```

**Notification Features:**
- **Custom Templates**: Rich notification templates for different scenarios
- **Multi-Channel**: System notifications + custom Electron windows + in-app modals
- **Action Handling**: User interaction processing with callbacks
- **Persistence**: No auto-dismiss - notifications stay until user action

### **3. Deploy Wrapper System**

#### **Smart Deploy Wrapper (`backend/deploy_wrapper_setup.py` - 373 lines)**
**Intelligent project-aware logging:**

```python
def get_deploy_log_path():
    """Determine appropriate deploy log path based on project context"""
    # 1. Scan current directory and parent directories
    # 2. Look for DeployBot project markers (config.json + TODO.md)
    # 3. Use project-specific logs/ directory if found
    # 4. Fallback to global ~/.deploybot/deploy_log.txt
```

**Wrapper Features:**
- **Project-Aware Logging**: Automatically detects project context
- **Command Pass-Through**: Zero impact on actual deployment commands
- **Shell Integration**: Automatic alias installation across shells (zsh, bash)
- **Smart Installation**: Handles existing installations and updates

#### **Wrapper Installation Process**
```bash
# Automatic installation creates:
~/.deploybot/deploybot-wrapper.py    # Smart wrapper script
~/.zshrc                            # alias deploybot="python3 ~/.deploybot/deploybot-wrapper.py"

# Usage:
deploybot firebase deploy --only functions  # Logs + executes normally
deploybot vercel --prod                     # Works with any command
deploybot npm run deploy                    # Full command transparency
```

---

## 🔄 **Data Flow & User Journey**

### **Complete Workflow Example**
```
1. COMMAND EXECUTION
   User: deploybot firebase deploy --only functions
   │
   ├─ Wrapper logs to project-specific logs/deploy_log.txt
   ├─ Command executes normally (30 seconds)
   └─ Command completes with exit code 0

2. DEPLOY DETECTION  
   Python Monitor detects new log entry
   │
   ├─ Parses: timestamp, project_name, deploy_command
   ├─ Triggers LangGraph workflow
   └─ Updates deploybot_state.deploy_detected = True

3. AI TASK SELECTION
   LangGraph select_task agent
   │
   ├─ Loads project TODO.md
   ├─ Filters tasks (exclude #backend during deploy)
   ├─ Uses OpenAI for intelligent selection OR heuristic fallback
   └─ Returns: {text: "Write blog post", app: "Bear", tags: ["#writing", "#solo"]}

4. TIMER & NOTIFICATION
   30-minute cloud propagation timer starts
   │
   ├─ WebSocket broadcasts timer status to frontend
   ├─ Custom notification window appears with task suggestion
   └─ User can: "Switch Now", "Snooze 5min", "View Timer", "Dismiss"

5. APP REDIRECTION
   User clicks "Switch Now"
   │
   ├─ App redirector launches Bear with deep linking
   ├─ Activity logger records task switch
   └─ Timer continues running in background

6. COMPLETION
   Timer expires after 30 minutes
   │
   ├─ "⏰ Propagation Complete" notification
   ├─ User can return to check deployment
   └─ Cycle completes
```

### **WebSocket Communication Protocol**
```javascript
// Frontend → Backend Commands
{
  "command": "get-task-suggestions",
  "data": {
    "project_path": "/path/to/project",
    "context": {
      "deploy_active": true,
      "use_llm": true,
      "timer_duration": 1800
    }
  }
}

// Backend → Frontend Events
{
  "type": "deploy",
  "event": "deploy_detected", 
  "data": {
    "project": "MyProject",
    "command": "firebase deploy",
    "timer_duration": 1800,
    "timestamp": "2025-01-02T19:45:32.123Z"
  }
}

// Notification Display Trigger
{
  "type": "notification",
  "event": "show_custom",
  "data": {
    "notification": {
      "id": "unified_suggestion_12345",
      "title": "🎯⏰ Task & Timer Update",
      "message": "Timer: 29:15 remaining. Suggested task: Write blog post",
      "actions": ["Switch to Task", "Snooze", "View Timer", "Dismiss"]
    }
  }
}
```

---

## 📁 **Project Structure & Configuration**

### **File System Organization**
```
DeployBot/
├── main/                           # Electron Application
│   ├── main.js                     # Main process (896 lines)
│   ├── preload.js                  # API bridge (305 lines)
│   ├── process_manager.js          # WebSocket client (749 lines)
│   └── renderer/                   # React UI
│       ├── src/
│       │   ├── App.jsx             # Main app (334 lines)
│       │   ├── components/         # React components
│       │   └── NotificationApp.jsx # Notification windows
│       ├── index.html              # Main window
│       └── notification.html       # Notification fallback
├── backend/                        # Python Backend
│   ├── graph.py                    # LangGraph core (1,221 lines)
│   ├── tasks.py                    # AI task selection (620 lines)
│   ├── project_manager.py          # Project CRUD (845 lines)
│   ├── monitor.py                  # Deploy detection (534 lines)
│   ├── notification.py             # Notification system (994 lines)
│   ├── timer.py                    # Timer management
│   ├── redirect.py                 # App redirection
│   ├── logger.py                   # Activity logging
│   └── deploy_wrapper_setup.py     # Wrapper installation (373 lines)
├── projects/                       # User Projects (8 active projects)
│   └── {ProjectName}/
│       ├── config.json             # Project configuration
│       ├── TODO.md                 # Task list with hashtags
│       └── logs/
│           ├── activity.log        # Activity history
│           └── deploy_log.txt      # Deploy detection log
├── assets/                         # Application assets
├── build/                          # Build configuration
└── dist/                          # Built application
```

### **Project Configuration Schema**
```json
// projects/{ProjectName}/config.json
{
  "projectName": "My Awesome Project",
  "description": "Project created via DeployBot UI",
  "version": "1.0.0",
  "createdAt": "2025-01-02T19:45:32.123Z",
  "lastModified": "2025-01-02T19:45:32.123Z",
  "backendServices": ["firebase", "vercel"],
  "deployCommands": ["firebase deploy", "vercel --prod"],
  "settings": {
    "defaultTimer": 1800,           // 30 minutes
    "graceperiod": 0,               // Immediate notifications
    "autoRedirect": true,
    "excludeTags": ["#backend"],    // Exclude during deploys
    "preferredTags": ["#short", "#solo"]
  },
  "taskMappings": {                 // Tag → App mappings
    "writing": "Bear",
    "creative": "Figma",
    "research": "Safari",
    "code": "VSCode"
  },
  "metadata": {
    "totalTasks": 6,
    "completedTasks": 1,
    "lastDeployDetected": "2025-01-02T19:30:15.456Z",
    "lastTaskSelected": "Write documentation"
  }
}
```

### **Task List Schema (TODO.md)**
```markdown
# Project Tasks

## Pending Tasks
- [ ] Write documentation for new features #writing #long #solo
- [ ] Design user interface mockups #creative #design #short  
- [ ] Research competitor pricing strategies #research #business #long
- [ ] Optimize database queries #code #backend #long
- [ ] Create social media content #writing #creative #short

## Completed Tasks
- [x] Set up project structure #code #setup

## Tag Taxonomy
### Duration: #short (15-30 min), #long (1+ hours)
### Type: #writing, #code, #research, #creative, #design, #business, #backend
### Collaboration: #solo, #collab
```

---

## ⚙️ **Configuration & Deployment**

### **Development Environment**
```bash
# Prerequisites
node >= 18.0.0
python >= 3.12
npm install

# Development Mode
npm run dev                    # Starts Vite + Electron with hot reload
npm run dev:vite              # Frontend only
npm run dev:electron          # Electron only

# Backend Development  
cd backend
python graph.py               # Start WebSocket server manually
```

### **Production Build**
```bash
# Full Build Process
npm run setup:python          # Bundle Python runtime
npm run build                 # Build React frontend
npm run build:electron        # Package Electron app

# Outputs
dist/DeployBot-1.0.0-arm64.dmg     # macOS installer (182MB)
dist/DeployBot-1.0.0-arm64.zip     # macOS portable (176MB)
```

### **Python Dependencies**
```txt
# requirements.txt
langgraph>=0.5.1
langchain>=0.3.26
langchain-openai>=0.3.27
openai>=1.93.0
websockets>=12.0
structlog>=24.1.0
python-dotenv>=1.0.0
pathlib>=1.0.1
```

---

## 📊 **Current Status & Metrics**

### **Implementation Completeness**
- ✅ **Core Architecture**: Production-ready (42,000+ lines of code)
- ✅ **Deploy Detection**: Sophisticated wrapper system with project awareness
- ✅ **AI Task Selection**: OpenAI integration with intelligent fallback
- ✅ **WebSocket Communication**: Enterprise-grade with health monitoring
- ✅ **Project Management**: Full CRUD with custom directory support
- ✅ **Notification System**: Multi-channel with rich templating
- ✅ **Timer Management**: Real-time updates with WebSocket integration
- ✅ **Build System**: Complete cross-platform distribution

### **Active Projects**
The system currently manages **8 active projects** with real data:
- **My_Awesome_Project**: 6 pending tasks, comprehensive hashtag taxonomy
- **DemoProject**: 10 pending tasks, advanced tagging patterns
- **Test, my-app, TimerTestProject, etc.**: Various development and testing projects

### **Quality Indicators**
- **Code Coverage**: Comprehensive error handling throughout
- **Documentation**: Architectural decisions recorded in ADR format
- **Logging**: Structured logging with full context at every level
- **Testing**: Built-in testing utilities and manual testing workflows
- **Distribution**: Professional DMG/ZIP packaging ready for users

---

## 🎯 **Summary**

DeployBot represents a sophisticated desktop productivity solution that successfully bridges the gap between individual developer workflows and intelligent automation. The system demonstrates enterprise-grade architecture patterns while maintaining the simplicity needed for personal productivity tools.

**Key Architectural Strengths:**
- **Real-time Communication**: WebSocket-based architecture with automatic reconnection
- **AI Integration**: OpenAI-powered task selection with intelligent fallbacks  
- **Production Ready**: Comprehensive error handling, logging, and distribution
- **Extensible Design**: Modular architecture supporting future enhancements
- **User-Centric**: Intuitive UI with sophisticated backend automation

**Deployment Ready**: The system is immediately deployable for production use with existing build infrastructure and comprehensive documentation.

---

*This document represents the complete technical specification for DeployBot as implemented. For operational guidance, see `DEPLOY_WRAPPER.md` and `PRODUCTION_DEPLOYMENT_SUMMARY.md`.* 