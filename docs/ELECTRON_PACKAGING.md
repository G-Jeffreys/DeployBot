# DeployBot Electron Packaging Guide

## Overview

DeployBot is packaged as a native desktop application using Electron with an embedded Python runtime. This allows the app to run on any machine without requiring Python to be pre-installed.

## Architecture

The packaged app consists of:

1. **Electron Frontend**: React-based UI built with Vite
2. **Node.js Process Manager**: Handles Python backend lifecycle
3. **Embedded Python Runtime**: Self-contained Python 3.12 with all dependencies
4. **Python Backend**: LangGraph-based backend for AI processing

## Build Process

### Prerequisites

- Node.js 18+ 
- npm
- Internet connection (for downloading Python runtime)

### Building the App

```bash
# Install dependencies
npm install

# Build the packaged app (includes Python runtime setup)
npm run build:electron

# Build for all platforms
npm run build:all
```

### Build Steps Explained

1. **Python Runtime Setup** (`npm run setup:python`)
   - Downloads portable Python 3.12 distribution (~60MB)
   - Copies to `python_runtime/` directory
   - Installs all backend dependencies (LangChain, OpenAI, etc.)
   - Verifies installation works correctly

2. **Frontend Build** (`npm run build`)
   - Compiles React app with Vite
   - Outputs to `dist/` directory

3. **Electron Packaging** (`electron-builder`)
   - Packages frontend, backend, and Python runtime
   - Creates platform-specific installers (DMG, ZIP, etc.)
   - Handles code signing (if configured)

## Runtime Behavior

### Python Executable Detection

The app uses a priority system for finding Python:

1. **Embedded Python** (production): `process.resourcesPath/python/bin/python3`
2. **Virtual Environment** (development): `../deploybot-env/bin/python3`  
3. **System Python** (fallback): `python3`

### Backend File Extraction

In production, Python backend files are extracted from the app bundle to a temporary directory:

```
/tmp/deploybot-backend/
├── graph.py
├── logger.py
├── monitor.py
├── notification.py
├── project_manager.py
├── project_directory_manager.py
├── redirect.py
├── tasks.py
├── timer.py
└── deploy_wrapper_setup.py
```

## Package Contents

### Included Files

- `main/**/*` - Electron main process
- `dist/**/*` - Built React frontend  
- `backend/**/*` - Python backend source
- `python_runtime/**/*` → `python/` - Embedded Python runtime
- `assets/icon.png` → `icon.png` - App icon
- `requirements.txt` - Python dependencies list

### Excluded Files

- `python_bundle/**` - PyInstaller artifacts
- `deploybot-env/**` - Development virtual environment
- `logs/**` - Runtime logs
- `docs/**` - Documentation
- `node_modules/**` - Node.js dependencies (except required ones)

## File Sizes

- **Embedded Python Runtime**: ~198MB (includes all dependencies)
- **ARM64 DMG**: ~235MB
- **x64 DMG**: ~468MB  
- **ARM64 ZIP**: ~231MB
- **x64 ZIP**: ~456MB

## Platform Support

### macOS
- **ARM64**: Native Apple Silicon support
- **x64**: Intel Mac support
- **Minimum Version**: macOS 10.13 (High Sierra)
- **Formats**: DMG installer, ZIP archive

### Windows (Planned)
- **x64**: 64-bit Windows support
- **Minimum Version**: Windows 10
- **Format**: NSIS installer

### Linux (Planned)
- **x64**: 64-bit Linux support
- **Format**: AppImage

## Code Signing & Distribution

### macOS Code Signing

Currently unsigned. For distribution, you'll need:

1. **Apple Developer Account**
2. **Developer ID Application Certificate**
3. **Notarization** (for Gatekeeper compatibility)

Add to `package.json`:

```json
{
  "build": {
    "mac": {
      "notarize": {
        "appleId": "your-apple-id@example.com",
        "appleIdPassword": "@keychain:AC_PASSWORD"
      }
    }
  }
}
```

### Auto-Updates

Configured for GitHub Releases:

1. Set `GITHUB_TOKEN` environment variable
2. Push git tag: `git tag v1.0.1 && git push --tags`
3. Run `npm run release` to build and upload

## Troubleshooting

### Build Issues

**Python runtime download fails:**
```bash
# Manual setup
npm run setup:python
```

**Missing dependencies:**
```bash
# Clean rebuild
npm run clean
npm install
npm run build:electron
```

### Runtime Issues

**Backend won't start:**
- Check that embedded Python has all dependencies
- Verify `python_runtime/bin/python3` exists and is executable
- Check logs in `logs/` directory

**WebSocket connection fails:**
- Ensure port 8765 is available
- Check firewall settings
- Verify backend process is running

### Testing Packaged App

To test without system Python:

1. Temporarily rename system Python: `sudo mv /usr/bin/python3 /usr/bin/python3.bak`
2. Launch packaged app
3. Verify backend starts and WebSocket connects
4. Restore system Python: `sudo mv /usr/bin/python3.bak /usr/bin/python3`

## Development vs Production

| Aspect | Development | Production |
|--------|-------------|------------|
| Python Source | `../deploybot-env/bin/python3` | `process.resourcesPath/python/bin/python3` |
| Backend Files | `../backend/*.py` | Extracted to temp directory |
| Frontend | Vite dev server (port 3000) | Bundled in `app.asar` |
| Icons | Relative paths | Resource paths |
| Logs | Console + file | File only |

## Next Steps

1. **Add Windows/Linux support** - Install portable Python for other platforms
2. **Implement code signing** - Set up certificates and notarization
3. **Add auto-updater** - Configure GitHub releases integration
4. **Optimize bundle size** - Remove unnecessary Python packages
5. **Add crash reporting** - Integrate error tracking service 