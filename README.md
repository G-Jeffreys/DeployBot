# 🤖 DeployBot - Week 1 MVP

**Personal desktop productivity assistant that detects backend deployment events and redirects to productive alternative tasks.**

## 🎯 Overview

DeployBot is an Electron + Python desktop application that monitors your backend deployments and automatically suggests productive tasks from your TODO list during deployment wait times. Built with LangGraph for intelligent task selection and WebSocket communication between frontend and backend.

## 🏗️ Architecture

- **Frontend**: Electron + React + Vite + Tailwind CSS v3.4
- **Backend**: Python + LangGraph + WebSockets
- **Communication**: WebSocket bridge (ws://localhost:8765)
- **Deploy Detection**: Deploy wrapper script + log monitoring

## 📋 Week 1 Features

✅ **Core Components**
- Electron desktop app with React frontend
- Python LangGraph backend with WebSocket server
- Project management (create, open, delete projects)
- Task list display with tag-based filtering
- Deploy status monitoring and timer
- Real-time activity logging
- Python backend testing interface

✅ **Deploy Detection Framework**
- Deploy wrapper script for command logging
- WebSocket communication infrastructure
- Timer simulation and progress tracking

✅ **Task Management**
- TODO.md file parsing (mocked for Week 1)
- Tag-based task categorization (#short, #long, #creative, etc.)
- App mapping (tasks → applications)
- Task completion tracking

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **macOS** (primary target platform)

### 1. Install Dependencies

```bash
# Install Node.js dependencies
npm install

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Start the Development Environment

**Terminal 1 - Python Backend:**
```bash
python3 langgraph/graph.py
```

**Terminal 2 - Electron Frontend:**
```bash
npm run dev
```

### 3. Set Up Deploy Detection (Optional)

Follow the [deploy wrapper guide](docs/DEPLOY_WRAPPER.md) to enable deployment detection:

```bash
# Create wrapper script
mkdir -p ~/.deploybot

# Add alias to shell config
echo 'alias deploybot="python3 ~/.deploybot/deploybot-wrapper.py"' >> ~/.zshrc
source ~/.zshrc

# Test deployment detection
deploybot echo "test deployment"
```

## 🖥️ Usage

### Main Interface

1. **Project Management**: Create or select a project from the sidebar
2. **Task List**: View tagged tasks from your TODO.md file
3. **Deploy Status**: Monitor deployment status and timer
4. **Activity Log**: Track system events and actions
5. **Python Testing**: Verify backend connectivity

### Testing the System

1. **Select DemoProject** from the sidebar (or create a new project)
2. **Click "Test Deploy"** to simulate a deployment event
3. **Watch the timer** and task suggestions update
4. **Test Python connection** using the testing panel
5. **View activity logs** in the right panel

### Key Shortcuts

- **Cmd+Shift+D**: Show/hide DeployBot window (global shortcut)

## 📁 Project Structure

```
DeployBot/
├── main/                          # Electron app
│   ├── main.js                    # Main process
│   ├── preload.js                 # Preload script
│   └── renderer/                  # React frontend
│       ├── src/
│       │   ├── App.jsx            # Main app component
│       │   ├── components/        # React components
│       │   └── index.css          # Tailwind styles
│       └── index.html
├── langgraph/
│   └── graph.py                   # Python LangGraph backend
├── bridge/
│   └── websocket_bridge.js        # WebSocket communication
├── projects/
│   └── DemoProject/               # Example project
│       ├── TODO.md                # Task list with tags
│       ├── config.json            # Project configuration
│       └── logs/activity.log      # Activity history
├── docs/                          # Documentation
├── package.json                   # Node.js config
├── requirements.txt               # Python dependencies
├── vite.config.js                 # Vite bundler config
└── tailwind.config.js             # Tailwind CSS config
```

## 🔧 Development

### Available Scripts

```bash
# Development (runs both frontend and backend)
npm run dev

# Frontend only
npm run dev:vite

# Backend only (in separate terminal)
python3 langgraph/graph.py

# Build for production
npm run build

# Run tests
npm test
```

### Environment Variables

```bash
# Development mode (automatically set by npm run dev)
NODE_ENV=development

# WebSocket server URL (default)
WS_URL=ws://localhost:8765
```

## 🐛 Troubleshooting

### Common Issues

**Backend Connection Failed**
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify WebSocket server
python3 langgraph/graph.py
# Should show: WebSocket server starting on ws://localhost:8765
```

**Frontend Build Errors**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check Node.js version
node --version  # Should be 18+
```

**Electron App Won't Start**
```bash
# Verify Vite dev server is running
npm run dev:vite
# Should show: Local: http://localhost:3000

# Then start Electron
npm run dev:electron
```

### Log Files

- **Frontend logs**: Chrome DevTools console
- **Backend logs**: Terminal output + structured logging
- **Deploy logs**: `~/.deploybot/deploy_log.txt`
- **Activity logs**: `projects/{ProjectName}/logs/activity.log`

## 📋 Week 1 Limitations

The current MVP includes mock data and simplified logic:

- **Deploy Detection**: Simulated (wrapper framework ready for Week 2)
- **Task Selection**: Mock data (TODO.md parsing comes in Week 3)
- **LangGraph**: Basic structure (full workflow in Week 4)
- **App Integration**: macOS 'open' command only

## 🗺️ Roadmap

### Week 2: Deploy Detection
- File monitoring for deploy logs
- Real-time deployment event detection
- Deploy timer integration
- Multi-service support (Firebase, Vercel, Netlify)

### Week 3: Task Intelligence
- TODO.md parsing and analysis
- LLM-powered task selection
- Context-aware recommendations
- Dynamic task filtering

### Week 4: Full Integration
- Complete LangGraph workflow
- Advanced app integrations
- User preferences and learning
- Production optimizations

## 🤝 Contributing

This is an educational project focused on learning Electron, LangGraph, and desktop app development.

### Development Guidelines

1. **Extensive Logging**: Every function should log its operations
2. **Modular Design**: Keep components small and focused
3. **No Hardcoding**: Use variables and configuration
4. **Test-Driven**: Write tests for all major functionality

## 📞 Support

For issues and questions:

1. Check the **troubleshooting section** above
2. Review the **activity logs** for error details
3. Test **Python backend connectivity** in the UI
4. Verify **WebSocket connection** status

## 📜 License

MIT License - Educational use and learning purposes.

---

**🎉 Week 1 MVP Complete!** The foundation is set for intelligent deployment detection and task redirection. Next week we'll implement real deploy monitoring and begin building the LangGraph intelligence layer. 