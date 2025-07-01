# 📅 Week 2 Scaffold Plan – DeployBot

## 🎯 Goals for Week 2
- Implement and test the deploy wrapper script and alias
- Enable deploy detection in Python by reading the deploy log
- Create project management UI (create/open/delete projects)
- Set up timer module to track deploy wait windows
- Begin logging significant events (deploys, redirects)

---

## 🛠️ 1. Deploy Wrapper Script

**File:** `~/.deploybot/deploybot-wrapper.py`

```python
#!/usr/bin/env python3
import sys
import subprocess
import time
from pathlib import Path

DEPLOY_LOG = Path.home() / ".deploybot" / "deploy_log.txt"
DEPLOY_LOG.parent.mkdir(exist_ok=True)

def main():
    args = sys.argv[1:]
    timestamp = time.time()
    command_string = " ".join(args)

    with open(DEPLOY_LOG, "a") as f:
        f.write(f"{timestamp} DEPLOY: {command_string}\n")

    subprocess.run(args)

if __name__ == "__main__":
    main()
```

**Shell Alias:**
```bash
alias deploybot="python3 ~/.deploybot/deploybot-wrapper.py"
```

---

## 🧪 2. Deploy Detection Logic (LangGraph)

**File:** `langgraph/monitor.py`

- Watch `deploy_log.txt`
- Detect new entries since last scan
- Send signal to LangGraph flow to initiate timer/task sequence

Example pattern:
```python
def check_for_new_deploy():
    with open(Path.home() / ".deploybot" / "deploy_log.txt", "r") as f:
        lines = f.readlines()
    # Track last known entry in memory or cache file
```

---

## 🗂️ 3. Project Management UI

In `App.jsx` or similar:
- Project list with open/create/delete
- On open: load `TODO.md` and `config.json`
- Store selected project in app state

Basic mock state:
```json
[
  { "name": "DemoProject", "path": "/projects/DemoProject" }
]
```

---

## ⏲️ 4. Timer Module (Python Utility)

**File:** `langgraph/timer.py`

- Start a timer for 30 minutes (or context-aware)
- Provide cancel/reset functions
- Keep track of active timer (can be used for logs or UI)

Example:
```python
import threading

def start_timer(duration=1800, on_expire=None):
    timer = threading.Timer(duration, on_expire)
    timer.start()
    return timer
```

---

## 🧾 5. Logging Utility

**File:** `langgraph/logger.py`

- Log:
  - Deploy detected
  - Task suggested
  - Redirect started
  - Timer started/stopped

**Log file:** `projects/ProjectName/logs/activity.log`

Example:
```text
[2024-07-01 13:21] DEPLOY DETECTED: firebase deploy --only functions
[2024-07-01 13:22] TASK SELECTED: Write tweet thread
```

---

## ✅ Week 2 Deliverables

- [ ] Deploy wrapper script tested and installed
- [ ] Alias added to shell and documented
- [ ] Python code reads and parses deploy log
- [ ] Project picker UI implemented
- [ ] Timer module working (start/reset/cancel)
- [ ] Event logging to per-project logs enabled