# 📝 Product Requirements Document: **DeployBot**

## 📌 Overview

**DeployBot** is a desktop productivity assistant that detects backend deployment events and redirects the developer to alternative productive tasks while waiting. It’s built for personal use with educational goals in mind (learning Electron, LangGraph, and desktop app development).

---

## 🎯 Goals

- Detect when a backend deployment command is run.
- Redirect focus to a relevant task from a per-project to-do list.
- Use LangGraph agents to manage state, choose tasks, and handle notifications.
- Help developers remain productive during backend-related bottlenecks.

---

## 👤 Target Audience

- Primarily the developer themselves (for self-use and learning).
- Secondarily: mentor/teacher evaluating the tool.

---

## 🧩 Core Features

### 1. **Project & Task Management**
- Create, rename, delete, and switch between projects.
- Each project has:
  - A `TODO.md` task list (optional in-app editor later).
  - A `config.json` containing backend service info.
  - A `taskmap.json` storing agent-determined task → tool/app associations.

### 2. **Backend Service Doc Parsing**
- User enters backend services used in the project.
- Agent fetches official documentation (if possible) to extract deploy commands.
- Populates a list of trigger phrases (e.g. `firebase deploy`, `gcloud app deploy`).

### 3. **LangGraph Agent Workflow**
- Agent monitors terminal activity for deployment commands.
- On detection:
  - Starts a timer (default 30 minutes).
  - Waits a grace period (2–3 mins).
  - Picks a relevant task based on context/tags.
  - Switches user’s focus to the appropriate app/tool.
  - Notifies user of task redirection.
- Clears or resets timer if another deployment happens during the wait window.
- Graph contains a loop so detection resumes after each cycle.

### 4. **Agent Debug Logs**
- Log every agent decision: deploy detected, task selected, app opened, etc.
- Logs saved per project in `logs/activity.log`.

---

## ✨ Stretch Goals

| Feature | Description |
|--------|-------------|
| **VSCode/Cursor Integration** | Auto-detect opened folders, launch corresponding project |
| **Terminal Integration** | Deeper CLI wrapping or shell hooks for reliability |
| **Smart Task Parsing** | LLM-based task + app inference from loosely structured tasks |
| **Switch Mode Options** | Let user choose between soft, medium, and hard focus switching |
| **In-App TODO.md Editor** | Edit task list in the app itself |
| **Advanced Notifications** | Persistent overlays, history, snooze/dismiss controls |
| **Privacy/Security Toggles** | Allow user to pause terminal monitoring and hide sensitive data |
| **Cloud Sync** | Sync projects and logs across devices |

---

## 🖼️ UI Sketch (MVP)

- Sidebar: project selector
- Main panel:
  - Project name
  - To-do list view (checkbox + task + app)
  - Backend services list (editable)
  - "Deploy Detected!" banner with timer
- Log viewer (optional panel or toggle)

---

## 📁 File Structure

```
DeployBot/
├── main/                      ← Electron app
│   └── renderer/              ← React or simple HTML/JS UI
├── backend/                 ← Python agents (LangGraph)
│   ├── graph.py, tasks.py, timer.py, state.py
├── bridge/                    ← IPC or socket communication
├── projects/
│   ├── MyProject/
│   │   ├── TODO.md
│   │   ├── config.json
│   │   ├── taskmap.json
│   │   └── logs/
```

---

## 🔧 Tech Stack

| Layer | Tools |
|-------|-------|
| Desktop App | Electron |
| Frontend UI | React (or minimal HTML/JS) |
| Agent Framework | LangGraph (Python) |
| Communication | IPC or WebSockets |
| OS | macOS-only (initially) |

---

## 🧪 Testing & Debugging

- Manual testing across several deployment tools (Firebase, GCP, Vercel).
- Agent log viewer to inspect behavior and trace logic flow.
- Terminal simulation scripts for triggering fake deployments.

---

## 💰 Cost Considerations

- **Deploy Detection Agent**: runs locally; no API cost.
- **Pick Alt Task Agent**: OpenAI API used **only if** needed for semantic task parsing.
  - Cache results per project (`taskmap.json`).
  - Parse only on task list change.
- **Other agents**: All local logic or simple functions.

---

## 📅 Timeline (Tentative Phases)

| Phase | Milestone |
|-------|-----------|
| **Week 1** | Scaffold Electron + LangGraph, build simple UI |
| **Week 2** | Add project/task management, terminal watcher |
| **Week 3** | Complete agent loop (detect → timer → redirect) |
| **Week 4** | Backend doc parsing, agent logs, cleanup |
| **Future** | Stretch goals, performance, polish, Cursor extension |