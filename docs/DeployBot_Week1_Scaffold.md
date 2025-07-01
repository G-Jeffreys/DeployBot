# 📅 Week 1 Scaffold Plan – DeployBot

## 🎯 Goals for Week 1
- Set up the project structure
- Make the Electron app run with a simple UI
- Set up the Python backend with LangGraph stub
- Establish communication between Electron and Python
- Scaffold core project folders and config file handling

---

## 🧱 1. Project Folder Structure

```
DeployBot/
├── main/                      # Electron app
│   ├── main.js
│   ├── preload.js
│   └── renderer/
│       ├── index.html
│       ├── App.jsx
│       └── components/
├── langgraph/                 # Python backend
│   ├── graph.py
│   ├── tasks.py
│   └── monitor.py
├── bridge/                    # IPC bridge
│   ├── electronToPython.js
│   └── python_server.py
├── projects/                  # Project storage
├── docs/                      # User docs
│   └── DEPLOY_WRAPPER.md
├── package.json               # Electron config
├── requirements.txt           # Python deps
└── README.md
```

---

## ⚙️ 2. Initialize Electron App

### Setup Steps:
```bash
npm init -y
npm install electron
npm install electron-reload --save-dev
npm install electron-global-shortcut
```

### `main.js`
```js
const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
  const win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile('renderer/index.html');
}

app.whenReady().then(createWindow);
```

---

## 💻 3. Add UI Placeholder

`renderer/index.html`:
```html
<!DOCTYPE html>
<html>
  <head><title>DeployBot</title></head>
  <body>
    <div id="app">Loading...</div>
    <script src="bundle.js"></script>
  </body>
</html>
```

`renderer/App.jsx`:
```jsx
import React from "react";
export default function App() {
  return (
    <div>
      <h1>DeployBot</h1>
      <p>Select a project or create one to get started.</p>
    </div>
  );
}
```

---

## 🧪 4. Python Backend + LangGraph Stub

`langgraph/graph.py`:
```python
def run_langgraph():
    print("LangGraph initialized and waiting...")
```

`bridge/python_server.py`:
```python
import subprocess

def start_graph():
    subprocess.run(["python3", "langgraph/graph.py"])
```

---

## 🔄 5. IPC Test (Electron → Python)

`bridge/electronToPython.js`:
```js
const { exec } = require("child_process");
exec("python3 langgraph/graph.py", (error, stdout, stderr) => {
  if (error) console.error(error);
  else console.log(stdout);
});
```

Hook this up to a UI button in your Electron app.

---

## 📁 6. Create Initial Project Folders

Example folder:
```
projects/DemoProject/
├── TODO.md
├── config.json
└── logs/activity.log
```

`TODO.md`:
```markdown
- [ ] Write script for product video #short #creative
- [ ] Review Firebase rules #research #backend
```

`config.json`:
```json
{
  "projectName": "DemoProject",
  "backendServices": ["firebase"]
}
```

---

## 📓 7. Document Deploy Wrapper

File: `docs/DEPLOY_WRAPPER.md`

Include:
- Explanation of alias setup
- Correct usage examples
- Cursor-friendly notes

---

## ✅ Week 1 Deliverables

- [ ] A running Electron app with a visible window and placeholder UI
- [ ] A Python backend that prints a test message when called
- [ ] Simple IPC from Electron → Python
- [ ] Project folder structure with example `TODO.md` and `config.json`
- [ ] Initial docs for deploy wrapper alias