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

## [2025-01-02] - DIAGNOSTIC: Notification System Investigation

### 🔍 **Issues Identified During Investigation**

#### **1. Custom Notification Windows Not Displaying**
- **DISCOVERY**: Backend processes notification commands successfully but visual notification windows don't appear
- **ROOT CAUSE**: Disconnect between Python backend WebSocket messages and Electron notification window creation
- **EVIDENCE**: `test-snooze-quick` command returns success but no notification window appears
- **STATUS**: ❌ **UNRESOLVED** - Requires backend WebSocket message format fix

#### **2. Task Selection System Failure**
- **DISCOVERY**: Task selection returns "No tasks found" despite projects having populated TODO.md files
- **TESTED PROJECTS**: 
  - `My_Awesome_Project` (40 lines TODO.md with 6 pending tasks)
  - `DemoProject` (45 lines TODO.md with 10 pending tasks)
- **EVIDENCE**: `test-week3-workflow` shows `task_selection.success: false` for all projects
- **STATUS**: ❌ **UNRESOLVED** - Task parsing/selection logic broken

#### **3. Snooze Functionality Broken**
- **DISCOVERY**: Snooze commands process but notifications don't reappear after delay
- **EVIDENCE**: `test-snooze-quick` (10-second test) shows success but no notification reappears
- **PREVIOUS CONTEXT**: Snooze fixes were implemented but require DeployBot restart to load
- **STATUS**: ❌ **PARTIALLY FIXED** - Requires restart and further testing

### 🧪 **Testing Results**

#### **Working Systems ✅**
- WebSocket communication (backend ↔ frontend)
- Bear app redirection system
- Backend command processing
- Timer system functionality
- Process monitoring and logging

#### **Broken Systems ❌**
- Custom notification window creation
- Task selection from TODO.md files  
- Snooze notification rescheduling
- Visual notification display

### 📊 **Commands Tested**
```bash
# WebSocket Commands Tested
test-snooze-quick        # ✅ Backend Success / ❌ No Visual
test-week3-workflow      # ❌ Task Selection Failed  
test-bear-redirection    # ✅ Full Success
```

### 🎯 **Critical Discovery: Backend-Frontend Disconnect**
- **Python Backend**: Successfully processes all notification-related commands
- **Electron Frontend**: Has complete custom notification window system implemented
- **Missing Link**: Backend doesn't send proper WebSocket message format to trigger notification windows
- **Expected Message**: `{type: 'notification', event: 'show_custom', data: {notification: {...}}}`
- **Current Issue**: Backend processes but doesn't broadcast notification creation messages

### 🔧 **Required Fixes (Not Yet Implemented)**
1. **Fix Backend Notification Broadcasting**: Update Python backend to send proper WebSocket messages for notification window creation
2. **Debug Task Selection**: Investigate why TODO.md parsing fails to find tasks
3. **Verify Snooze System**: Test snooze functionality after proper notification display
4. **Integration Testing**: End-to-end testing of notification → snooze → reappear cycle

### 📝 **Investigation Methodology**
- WebSocket command testing via Python scripts
- Project structure analysis (TODO.md content verification)
- Backend response analysis (JSON command responses)
- Process status verification (DeployBot running since 7:01PM)
- Code path analysis (Electron notification system review)

### 🚨 **Impact Assessment**
- **HIGH SEVERITY**: Core notification system non-functional
- **USER IMPACT**: No visual feedback during deploy wait periods
- **WORKAROUND**: None currently available
- **PRIORITY**: Critical - affects primary DeployBot value proposition

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

## [2025-01-02] - CRITICAL FIX: Notification System Architecture

### 🎯 **Core Insight Discovered**
- **FIXED**: Fundamental misunderstanding of DeployBot's purpose
- **DISCOVERY**: System was cancelling notifications when deploys completed quickly
- **CORRECTION**: Notifications should appear AFTER deploy completion for cloud propagation periods

### 🔧 **Changes Made**
- **backend/graph.py**: Removed backwards cancellation logic in `_schedule_unified_notification`
- **backend/notification.py**: Updated templates to reflect cloud propagation focus
- **backend/notification.py**: Set grace period to 0 for immediate notifications

### ✅ **Result**
- Notifications now appear correctly after deployment completion
- Task suggestions show during cloud propagation periods (10-30 minutes)
- End-to-end flow verified working: deploy → notification → task suggestions → timer

### 📖 **Documentation**
- Updated `docs/NOTIFICATION_SYSTEM_FIX.md` with complete architectural analysis
- Documented correct workflow: Local deploy (30s) → Notification → Cloud propagation (15-30min)

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