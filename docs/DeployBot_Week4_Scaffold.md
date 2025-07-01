# 📅 Week 4 Scaffold Plan – DeployBot

## 🎯 Goals for Week 4
- Finalize the UI with basic styling and structure
- Add Recent Activity Panel (log viewer)
- Implement tag parsing and display in UI
- Add theme toggle (light/dark mode)
- Final integration testing and bug fixing

---

## 🎨 1. Finalize UI Layout

In `App.jsx` (or equivalent), implement:
- Sidebar: project selector
- Main panel: task list, current task, timer status
- Footer: activity log preview (scrollable)

Use basic styling (Tailwind v3.4 or CSS-in-JS) to make it clean and minimal.

---

## 🗂️ 2. Recent Activity Panel

**File:** `renderer/components/ActivityLog.jsx`

- Read `logs/activity.log`
- Display last 10 events with timestamp + description
- Example:
  ```text
  [3:20 PM] Detected deploy: firebase deploy
  [3:22 PM] Suggested task: Write script in Bear
  [3:24 PM] Timer started (30 min)
  ```

Use file watcher or manual refresh.

---

## 🏷️ 3. Tag Parsing Display

- For each task in `TODO.md`, show detected tags visually
- Tags can be styled pills (e.g., `#short`, `#code`)
- Add tooltip or filter-by-tag option (if trivial)

**Use existing tag parser** from Week 3

---

## 🌗 4. Theme Toggle (Light/Dark)

- Add a toggle in the settings or header
- Use a state hook or CSS class to control theme
- Store preference in local storage

**Electron Tip:** Forward theme preference to main window via `preload.js`

---

## 🧪 5. Integration Testing + Cleanup

- Simulate deploy → check that:
  - Timer starts
  - Task is picked
  - Redirect occurs (with log)
- Ensure no redundant LangGraph calls
- Validate fallback behavior (no task available, cancel, etc.)

---

## ✅ Week 4 Deliverables

- [ ] Final UI structure in place and styled
- [ ] Recent Activity Panel shows logs
- [ ] Tags parsed and shown in task list
- [ ] Theme toggle working and stored persistently
- [ ] End-to-end deploy-to-task flow tested and functional
- [ ] MVP complete 🎉