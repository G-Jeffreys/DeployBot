# 📦 DeployBot: Full Project Overview (MVP + Architecture)

DeployBot is a personal desktop productivity assistant built to detect backend deployment events and redirect developer focus to productive alternative tasks during deploy wait periods. It uses LangGraph for agent orchestration and is built with Electron + Python, running on macOS.

---

## 🧱 Core Architecture

**Main Components:**
- **Electron App (JS/React):** Desktop UI, task display, notifications, config management.
- **LangGraph Backend (Python):** Manages deploy detection, task selection via WebSocket server.
- **ProcessManager:** Handles communication between Electron and LangGraph backend.
- **Filesystem-based Project State:** Project folders with task lists, configs, logs.

```
DeployBot/
├── main/                      ← Electron app (UI)
│   └── renderer/              ← Task list, logs, backend services
├── backend/                   ← Python AI logic (LangGraph)
│   ├── graph.py               ← LangGraph workflow & WebSocket server
│   ├── tasks.py               ← Task selection logic
│   ├── monitor.py             ← Deploy detection
│   ├── notify.py, timer.py    ← Supporting modules
├── main/process_manager.js    ← WebSocket communication with Python backend
├── projects/
│   └── MyProject/
│       ├── TODO.md
│       ├── config.json
│       ├── taskmap.json
│       └── logs/activity.log
```

---

## 🧠 Agent Design (LangGraph)

### Only two real agents:
- **Deploy Detection Agent:** Watches for deploys via wrapper log file.
- **Pick Alt Task Agent:** Selects best task from `TODO.md` using tags or LLM.

### Utility Functions (Not agents):
- Timer (start/cancel)
- Notification dispatch
- Task switcher (opens associated app)
- Logger (writes to activity log)

---

## 🧩 MVP Feature Set

### ✅ Included in MVP:
- Project system (create, open, delete projects)
- Load and parse `TODO.md`
- Deploy wrapper + alias (logged for detection)
- LangGraph: detect deploy, pick alt task
- Redirect to task with notification + context switch
- Log actions (deploys, redirects, etc.)
- Light theme toggle
- Click task → open associated app
- Hotkey (e.g., Ctrl+Shift+D) to summon DeployBot
- Manual tagging in `TODO.md` (#short, #writing, etc.)

### ❌ Stretch Goals (Not MVP):
- In-app markdown editor
- VSCode/Cursor integration
- Smart LLM-based task parsing
- Snooze redirection / confirmation modal
- Deep terminal monitoring (e.g. shell injection)
- Cloud sync
- Switch mode preferences (soft/medium/hard)
- Privacy toggles

---

## 🚀 Deploy Wrapper

**Purpose:** Detect when deploys happen.

- Wrapper logs deploy event with timestamp + command
- Actual CLI command runs unaltered
- Works with `alias deploybot="python3 ~/.deploybot/deploybot-wrapper.py"`

### Example:
```bash
deploybot firebase deploy --only functions
```

Creates log entry for detection and passes through command.

### Required Doc: `docs/DEPLOY_WRAPPER.md`
To be fed to Cursor so the agent understands how to deploy.

---

## 🏷️ Task Tagging

**Users manually tag tasks** with hashtags in `TODO.md`. Example:

```markdown
- [ ] Write tweet thread for launch #short #writing #solo
```

Core tags:
- `#short`, `#long`
- `#writing`, `#code`, `#research`
- `#solo`, `#collab`
- `#backend` (to be deprioritized during deploy)

---

## 🔔 Notification Strategy

**Hybrid model:**
- macOS notification: deploy detected → suggest redirection
- In-app modal (if open): offer confirmation/snooze

---

## 📅 MVP Development Timeline

| Week | Milestone |
|------|-----------|
| 1 | Scaffold Electron + LangGraph, build project manager |
| 2 | Add deploy wrapper, log detection, timer logic |
| 3 | Implement task selection agent, redirection, notifications |
| 4 | UI polish, logging, tag parser, final cleanup |

---

## 💸 Cost Consideration

- **OpenAI API use is minimal** and cached:
  - Only used for task inference if needed.
  - Deploy detection is fully local (no API cost).

---

## 🚨 **CURRENT STATUS - January 2, 2025**

### **CRITICAL ISSUES DISCOVERED**

#### **🔴 Core Notification System Non-Functional**
- **Issue**: Backend processes notification commands but no visual windows appear
- **Root Cause**: Backend doesn't send proper WebSocket message format to trigger Electron notification windows
- **Impact**: CRITICAL - No user feedback during deploy wait periods
- **Status**: ❌ **BROKEN** - Requires immediate fix

#### **🔴 Task Selection System Failure** 
- **Issue**: Returns "No tasks found" despite projects having populated TODO.md files
- **Evidence**: 
  - `My_Awesome_Project`: 6 pending tasks → "No tasks found"
  - `DemoProject`: 10 pending tasks → "No tasks found"
- **Impact**: HIGH - Zero task suggestions generated
- **Status**: ❌ **BROKEN** - Task parsing logic failure

#### **🔴 Snooze Functionality Broken**
- **Issue**: Commands process but notifications don't reappear after delay
- **Context**: Previous fixes implemented but may require restart
- **Impact**: MEDIUM - Feature completely unusable  
- **Status**: ❌ **NON-FUNCTIONAL**

### **✅ Working Systems**
- Electron ↔ Python WebSocket communication
- App redirection (Bear, Figma, VSCode, etc.)
- Timer system functionality
- Process monitoring and logging
- Deploy command processing

### **🎯 Immediate Action Required**
1. Fix backend WebSocket notification broadcasting
2. Debug task selection TODO.md parsing
3. Verify snooze system functionality
4. End-to-end integration testing

**Current Priority**: CRITICAL SYSTEM REPAIR before any new feature development.