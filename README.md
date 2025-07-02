# 🤖 DeployBot

**Personal desktop productivity assistant** that detects backend deployment events and intelligently suggests productive tasks from your TODO list during deployment wait times. Built with LangGraph for intelligent task selection and WebSocket communication between frontend and backend.

![DeployBot Demo](docs/images/deploybot-demo.gif)

---

## 🎯 What DeployBot Does

1. **Detects Deployments**: Monitors when you run deployment commands (`firebase deploy`, `vercel --prod`, etc.)
2. **Starts Timer**: Begins tracking your deployment wait time (default 30 minutes)
3. **Suggests Tasks**: After a grace period, intelligently suggests alternative tasks from your TODO.md
4. **Redirects Focus**: Opens the appropriate app (Bear, Figma, VSCode) for the suggested task
5. **Logs Activity**: Tracks all deployments, task selections, and productivity sessions

---

## ✨ Features

### 🚀 Current Features (v1.0.0)
- **Deploy Detection**: Wrapper script integration with all major deployment tools
- **Smart Task Selection**: Tag-based filtering with optional LLM enhancement
- **Project Management**: Multi-project support with individual configurations
- **Real-time Communication**: WebSocket bridge between Electron frontend and Python backend
- **Activity Logging**: Comprehensive tracking of deployments and task redirections
- **Native Integration**: macOS notifications and global shortcuts
- **TODO.md file parsing**: Automated task extraction with hashtag support
- **Timer Management**: Deploy wait period tracking with customizable durations

### 🎨 UI Components
- **Project Selector**: Create, open, and manage multiple projects
- **Task List**: View tagged tasks from your TODO.md file with app associations
- **Deploy Status**: Real-time deployment monitoring and timer display
- **Activity Log**: Live feed of deployments, task selections, and app redirections
- **Python Testing**: Backend connectivity verification and debugging tools

---

## 🚀 Quick Start

### Installation

#### 1. Download DeployBot
```bash
# Download the latest release
# macOS Apple Silicon:
curl -L -o DeployBot.dmg https://github.com/your-username/DeployBot/releases/latest/download/DeployBot-arm64.dmg

# Install by opening the DMG and dragging to Applications
open DeployBot.dmg
```

#### 2. Install Python (Required)
DeployBot requires Python 3.9+ to run its intelligent backend.

**🚀 Automated Setup (Recommended):**
```bash
curl -sSL https://raw.githubusercontent.com/your-username/DeployBot/main/scripts/install_python.sh | bash
```

**⚙️ Manual Setup:**
```bash
# Install Python via Homebrew
brew install python@3.11

# Install DeployBot dependencies
pip3 install --user "langgraph>=0.0.55" "websockets>=12.0" "structlog>=24.1.0" "langchain-openai>=0.1.0"

# Verify installation
python3 -c "import langgraph; print('✅ Python setup complete!')"
```

**📖 Need help?** See: [Quick Python Setup](docs/PYTHON_SETUP_QUICK.md) or [Detailed Guide](docs/PYTHON_INSTALLATION.md)

### First-Time Setup

1. **Launch DeployBot** from Applications
2. **Create a project** using the sidebar
3. **Install deploy wrapper**:
   ```bash
   # The app will guide you through this setup
   mkdir -p ~/.deploybot
   # ... (detailed setup in app)
   ```
4. **Add tasks to TODO.md** in your project with tags like `#short`, `#writing`, `#solo`
5. **Test detection**: Run `deploybot echo "test"` in terminal

---

## 🏗️ Development & Building

### Development Setup
```bash
# Clone the repository
git clone https://github.com/your-username/DeployBot.git
cd DeployBot

# Install dependencies
npm install
pip install -r requirements.txt

# Start development environment
npm run dev
```

### Production Build
```bash
# Quick build
npm run build:electron

# Or use the automated release script
./scripts/release.sh v1.0.1
```

**Build Outputs**:
- `dist/DeployBot-1.0.0-arm64.dmg` - macOS Installer (182MB)
- `dist/DeployBot-1.0.0-arm64-mac.zip` - Portable App (176MB)
- `dist/mac-arm64/DeployBot.app` - App Bundle for testing

### Deployment
See [Quick Deployment Guide](docs/QUICK_DEPLOYMENT_GUIDE.md) for fast builds or [Production Deployment Guide](docs/PRODUCTION_DEPLOYMENT.md) for comprehensive release management.

---

## 🗂️ Project Structure

```
DeployBot/
├── main/                      # Electron app (frontend)
│   ├── main.js               # Main process
│   ├── preload.js            # Security bridge
│   └── renderer/             # React UI components
├── bridge/                   # WebSocket IPC communication
│   └── websocket_bridge.js   # Electron ↔ Python bridge
├── langgraph/               # Python backend (LangGraph)
│   ├── graph.py             # Main workflow orchestration
│   ├── monitor.py           # Deploy detection
│   ├── timer.py             # Timer management
│   ├── tasks.py             # Task selection (LLM + heuristic)
│   ├── project_manager.py   # Project CRUD operations
│   └── logger.py            # Activity logging
├── projects/                # User project data
│   └── MyProject/
│       ├── TODO.md          # Task list with tags
│       ├── config.json      # Project configuration
│       └── logs/            # Activity and deploy logs
├── scripts/                 # Build and deployment tools
│   └── release.sh          # Automated release workflow
└── docs/                   # Documentation
```

---

## 🏷️ Task Tagging System

DeployBot uses hashtag-based task classification in your TODO.md files:

```markdown
# My Project Tasks

- [ ] Write blog post about deployment automation #writing #short #solo
- [ ] Review security settings in Firebase #research #backend #long
- [ ] Design new dashboard mockups #creative #short #design
- [ ] Optimize database queries #code #backend #long
```

### Tag Categories

**Duration**: `#short` (15-30 min), `#long` (1+ hours)  
**Type**: `#writing`, `#code`, `#research`, `#creative`, `#design`, `#business`  
**Collaboration**: `#solo`, `#collab`  
**Context**: `#backend` (deprioritized during deploys)

---

## 🔧 Technical Architecture

### Frontend Stack
- **Electron 29.1.4**: Desktop application framework
- **React 18**: UI components and state management
- **Vite 5**: Fast build tool and development server
- **Tailwind CSS 3.4**: Utility-first styling
- **WebSocket Client**: Real-time communication with backend

### Backend Stack
- **Python 3.9+**: Core backend language
- **LangGraph**: AI workflow orchestration
- **WebSockets**: Real-time bidirectional communication
- **structlog**: Structured logging throughout
- **OpenAI GPT**: Optional LLM-enhanced task selection

### Communication
- **WebSocket Bridge**: Electron ↔ Python with reconnection and message queuing
- **IPC Security**: Context isolation with secure preload script
- **File Monitoring**: Real-time deploy log detection with position tracking

---

## 📊 Performance & Metrics

### Resource Usage
- **Memory**: <200MB idle, <400MB active
- **CPU**: <5% idle, 10-15% during processing
- **Storage**: ~180MB installed, minimal project data overhead

### Build Metrics
- **DMG Installer**: 182MB
- **ZIP Portable**: 176MB  
- **Startup Time**: <3 seconds
- **Deploy Detection**: <2 second latency

---

## 🧪 Testing

### Manual Testing
```bash
# Test Python backend
npm run test:python

# Test build process
npm run build:electron

# Test release workflow
./scripts/release.sh v1.0.1-test
```

### Integration Testing
The app includes comprehensive manual testing via the built-in Python connection tester. Automated testing infrastructure is planned for v1.1.0.

---

## 📚 Documentation

- **[Quick Deployment Guide](docs/QUICK_DEPLOYMENT_GUIDE.md)** - Fast build and release
- **[Production Deployment](docs/PRODUCTION_DEPLOYMENT.md)** - Comprehensive release management
- **[Deploy Wrapper Setup](docs/DEPLOY_WRAPPER.md)** - User installation guide
- **[Architecture Overview](docs/DeployBot_Full_Project_Overview.md)** - System design and components
- **[PRD](docs/DeployBot_PRD.md)** - Product requirements and specifications
- **[Architectural Decisions](docs/ARCHITECTURAL_DECISIONS.md)** - Design choices and trade-offs
- **[Development Scaffolds](docs/)** - Week-by-week implementation guides

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with comprehensive logging
4. **Test thoroughly** using the built-in testing tools
5. **Update documentation** if needed
6. **Submit a pull request** with detailed description

### Development Guidelines
- **No monolithic files** - Keep modules focused and modular
- **Comment everything** - Extensive logging and debugging output
- **Real functionality only** - No mock data or placeholder code
- **LLM-first approach** - Leverage AI over hardcoded logic
- **Production-ready** - All code should be deployable immediately

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for detailed release notes and version history.

---

## 📞 Support

- **Documentation**: Comprehensive guides in `/docs`
- **Issues**: [GitHub Issues](https://github.com/your-username/DeployBot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/DeployBot/discussions)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🎉 Acknowledgments

- **LangGraph** for AI workflow orchestration
- **Electron** for cross-platform desktop development
- **OpenAI** for intelligent task selection capabilities
- **Tailwind CSS** for beautiful, responsive UI design

---

*Built with ❤️ for developers who want to stay productive during deployment wait times.* 