# 📅 Week 3 Scaffold Plan – DeployBot

## 🎯 Goals for Week 3
- Implement the task picking logic (LLM-assisted or tag-based)
- Parse and interpret `TODO.md` with tags
- Implement redirection logic (open associated app or website)
- Set up notification dispatch and hybrid notification flow
- Connect deploy detection to task suggestion flow via LangGraph

---

## 🧠 1. Task Picker Agent (LangGraph)

**File:** `langgraph/tasks.py`

Two possible modes:
1. **Tag-based selection (default for MVP):**
   - Parse `TODO.md`
   - Filter out `#backend` or `#long` if timer is short
   - Randomly or heuristically pick suitable task

2. **LLM-enhanced (stretch goal):**
   - Extract task descriptions and tags
   - Use GPT to score/filter based on context

Example tag-heuristic:
```python
def pick_task(tasks, timer_minutes):
    if timer_minutes <= 30:
        suitable = [t for t in tasks if "#short" in t or "#solo" in t]
    else:
        suitable = tasks
    return suitable[0] if suitable else None
```

---

## 🗒️ 2. TODO.md Parser

**Functionality:**
- Read `TODO.md`
- Split into tasks
- Extract tags (`#short`, `#code`, etc.)
- Store parsed task list in `taskmap.json`

**File:** `langgraph/todo_parser.py`

---

## 🔀 3. Redirection Function

**File:** `langgraph/redirect.py`

- Open app or URL based on mapped app/task
- macOS-only:
  ```bash
  open -a "Notion"
  open bear://note?id=123
  ```

Match task keywords to apps:
```json
{
  "write": "Bear",
  "research": "Safari",
  "code": "VSCode"
}
```

Allow override via `taskmap.json`.

---

## 🔔 4. Notification Strategy

**Hybrid approach:**
- macOS notification for context ("Deploy detected, suggest task switch")
- In-app modal (if app is open): confirm/snooze

**macOS notification (Electron):**
Use `node-notifier` or `electron-notifications`.

**In-app modal:**
- Buttons: [Switch] [Snooze] [Dismiss]
- Show task and timer length

---

## 🔁 5. LangGraph Flow

**Hook up flow:**
- When deploy detected:
  - Start timer
  - After 2–3 min delay, pick task
  - Show notification and/or modal
  - Redirect if confirmed
  - Log everything

---

## ✅ Week 3 Deliverables

- [ ] Task selection logic implemented (tag-based)
- [ ] Parser reads `TODO.md` and extracts tags
- [ ] Redirect module opens correct app/URL
- [ ] Notification system works (system + in-app modal)
- [ ] LangGraph graph connects deploy → timer → task → redirect