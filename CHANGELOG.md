# Changelog

All notable changes to DeployBot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production deployment documentation and scripts
- Automated release workflow with `scripts/release.sh`
- Enhanced package.json configuration for multi-platform builds
- Auto-updater support with GitHub releases
- Comprehensive build testing and validation

### Changed
- Improved error handling throughout the application
- Enhanced WebSocket communication reliability
- Better logging and debugging capabilities

### Fixed
- WebSocket connection stability issues
- Python backend startup race conditions
- Build process optimization and artifact generation

## [1.0.0] - 2024-01-15

### Added
- Initial release of DeployBot MVP
- Electron desktop application with React frontend
- Python LangGraph backend with WebSocket communication
- Deploy detection system with wrapper script
- Project management system with TODO.md parsing
- Task selection with tag-based filtering
- Real-time activity logging and monitoring
- Timer system for deploy wait periods
- Notification system (macOS native + in-app)
- Global shortcuts for app activation
- Theme support (light/dark mode ready)

### Core Features
- **Deploy Detection**: Monitors deployment commands via wrapper script
- **Task Selection**: Intelligent task picking from TODO.md with tag support
- **Project Management**: Full CRUD operations for projects
- **Real-time Communication**: WebSocket bridge between Electron and Python
- **Activity Logging**: Comprehensive event tracking and history
- **Timer Management**: Deploy wait period tracking with notifications
- **App Redirection**: Opens appropriate apps for selected tasks

### Technical Stack
- **Frontend**: Electron 29.1.4 + React 18 + Vite 5 + Tailwind CSS 3.4
- **Backend**: Python 3.9+ + LangGraph + WebSockets
- **Communication**: WebSocket IPC bridge with reconnection and queuing
- **Build**: electron-builder with macOS DMG/ZIP distribution
- **Architecture**: Modular design with clean separation of concerns

### Supported Platforms
- macOS (ARM64 Apple Silicon)
- Future: Intel x64, Windows, Linux

### Documentation
- Complete API documentation for all modules
- Deployment wrapper setup guide
- Week-by-week development scaffolding
- Architectural decision records (ADRs)
- Production deployment guide

---

## Release Notes Format

Each release should include:

### Added
- New features and capabilities

### Changed
- Changes to existing functionality

### Deprecated
- Features that will be removed in future versions

### Removed
- Features that have been removed

### Fixed
- Bug fixes and issue resolutions

### Security
- Security-related changes and fixes

---

## Version Numbering

DeployBot follows [Semantic Versioning](https://semver.org/):

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner
- **PATCH** version when you make backwards compatible bug fixes

### Examples:
- `1.0.0` - Initial release
- `1.0.1` - Bug fix release
- `1.1.0` - New feature release
- `2.0.0` - Breaking changes release 