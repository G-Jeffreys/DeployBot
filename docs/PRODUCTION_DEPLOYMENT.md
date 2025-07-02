# 🚀 DeployBot Production Deployment Guide

This document provides comprehensive instructions for building, packaging, and distributing DeployBot for production use.

---

## 📋 Prerequisites

### Development Environment
- **Node.js**: v18+ with npm
- **Python**: 3.9+ with pip
- **macOS**: Required for building macOS distributions
- **Git**: For version control and release management

### Build Tools
- **Vite**: v5.2.0+ (frontend build)
- **Electron Builder**: v24.13.3+ (app packaging)
- **Electron**: v29.1.4+ (runtime)

---

## 🔧 Build Configuration

### Current Setup
```json
{
  "build": {
    "appId": "com.deploybot.app",
    "productName": "DeployBot",
    "directories": {
      "output": "dist"
    },
    "files": [
      "main/**/*",
      "dist/**/*"
    ]
  }
}
```

### Supported Platforms
- **macOS**: ARM64 (Apple Silicon) and Intel x64
- **Future**: Windows and Linux support can be added

---

## 🏗️ Build Process

### 1. Development Build
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start development environment
npm run dev
```

### 2. Production Build
```bash
# Step 1: Build frontend (React + Vite)
npm run build
# Output: dist/index.html, dist/assets/

# Step 2: Package Electron app
npm run build:electron
# Output: dist/DeployBot-1.0.0-arm64.dmg (installer)
#         dist/DeployBot-1.0.0-arm64-mac.zip (portable)
#         dist/mac-arm64/DeployBot.app (app bundle)
```

### 3. Build Output Structure
```
dist/
├── index.html                          # Frontend build
├── assets/                             # CSS, JS bundles
├── DeployBot-1.0.0-arm64.dmg          # DMG installer (182MB)
├── DeployBot-1.0.0-arm64-mac.zip      # Portable ZIP (176MB)
├── DeployBot-1.0.0-arm64.dmg.blockmap # Update metadata
├── DeployBot-1.0.0-arm64-mac.zip.blockmap
├── latest-mac.yml                      # Auto-updater metadata
└── mac-arm64/
    └── DeployBot.app/                  # Runnable app bundle
```

---

## 🔐 Code Signing (macOS)

### Current Status
- **❌ Code signing disabled**: "cannot find valid Developer ID Application identity"
- **⚠️ Impact**: May cause macOS security warnings, slower launch times

### Setup Code Signing
```bash
# 1. Obtain Apple Developer ID certificate
# Visit: https://developer.apple.com/account/resources/certificates/

# 2. Install certificate in Keychain Access

# 3. Update package.json with signing configuration
{
  "build": {
    "mac": {
      "identity": "Developer ID Application: Your Name (TEAM_ID)",
      "hardenedRuntime": true,
      "entitlements": "build/entitlements.mac.plist"
    }
  }
}

# 4. Create entitlements file
mkdir -p build
# Add build/entitlements.mac.plist with required permissions
```

### Entitlements Template
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.allow-dyld-environment-variables</key>
    <true/>
</dict>
</plist>
```

---

## 📦 Distribution Methods

### Method 1: Direct Download
```bash
# 1. Build production version
npm run build:electron

# 2. Upload DMG to hosting service
# - GitHub Releases (recommended)
# - AWS S3 + CloudFront
# - Your own web server

# 3. Provide download links
# DMG: https://releases.yoursite.com/DeployBot-1.0.0-arm64.dmg
# ZIP: https://releases.yoursite.com/DeployBot-1.0.0-arm64-mac.zip
```

### Method 2: GitHub Releases
```bash
# 1. Create release tag
git tag v1.0.0
git push origin v1.0.0

# 2. Upload build artifacts to GitHub Releases
# - DeployBot-1.0.0-arm64.dmg
# - DeployBot-1.0.0-arm64-mac.zip
# - latest-mac.yml (for auto-updater)

# 3. Generate release notes
```

### Method 3: App Store (Future)
```bash
# Requires additional configuration:
# - App Store entitlements
# - Sandboxing compliance
# - Review process submission
```

---

## 🔄 Auto-Update System

### Current Setup
- **Metadata**: `latest-mac.yml` generated automatically
- **Update server**: Not configured
- **Client**: Electron auto-updater ready

### Configure Auto-Updates
```javascript
// main/main.js - Add auto-updater
const { autoUpdater } = require('electron-updater');

// Set update server URL
autoUpdater.setFeedURL({
  provider: 'github',
  owner: 'your-username',
  repo: 'DeployBot'
});

// Check for updates on startup
app.whenReady().then(() => {
  autoUpdater.checkForUpdatesAndNotify();
});
```

---

## 🧪 Testing Production Builds

### Local Testing
```bash
# 1. Build and test locally
npm run build:electron

# 2. Install DMG on test machine
open dist/DeployBot-1.0.0-arm64.dmg

# 3. Test app functionality
# - Deploy detection
# - Task selection
# - WebSocket communication
# - Python backend integration

# 4. Test uninstall process
```

### Integration Testing Checklist
- [ ] App launches without errors
- [ ] Python backend starts correctly
- [ ] WebSocket communication works
- [ ] Deploy wrapper functions
- [ ] Project management operations
- [ ] File monitoring active
- [ ] Task selection working
- [ ] Notifications display
- [ ] Global shortcuts work
- [ ] App can be cleanly uninstalled

---

## 📝 Release Workflow

### Version Management
```bash
# 1. Update version in package.json
npm version patch|minor|major

# 2. Update CHANGELOG.md with changes

# 3. Commit version bump
git add .
git commit -m "Release v1.0.1"

# 4. Create tagged release
git tag v1.0.1
git push origin v1.0.1
```

### Automated Release Script
```bash
#!/bin/bash
# scripts/release.sh

set -e

VERSION=$1
if [ -z "$VERSION" ]; then
  echo "Usage: ./release.sh v1.0.0"
  exit 1
fi

echo "🚀 Starting release process for $VERSION"

# Update version
npm version $VERSION --no-git-tag-version

# Build production
echo "📦 Building production..."
npm run build
npm run build:electron

# Create git tag
git add .
git commit -m "Release $VERSION"
git tag $VERSION

# Push to repository
git push origin main
git push origin $VERSION

echo "✅ Release $VERSION complete!"
echo "📋 Next steps:"
echo "  1. Upload dist/*.dmg and dist/*.zip to GitHub Releases"
echo "  2. Update release notes"
echo "  3. Notify users of new version"
```

---

## 🔍 Troubleshooting

### Common Build Issues

**Issue**: "Cannot find valid Developer ID Application identity"
```bash
# Solution: Set up code signing or disable
export CSC_IDENTITY_AUTO_DISCOVERY=false
npm run build:electron
```

**Issue**: "Python backend not starting"
```bash
# Check Python dependencies
pip install -r requirements.txt

# Verify Python path in main.js
which python3
```

**Issue**: "WebSocket connection failed"
```bash
# Check port conflicts
lsof -i :8765

# Verify backend startup sequence
```

### Production Issues

**Issue**: "App won't open on other Macs"
- **Cause**: Code signing required for distribution
- **Solution**: Set up Apple Developer ID certificate

**Issue**: "Python not found error"
- **Cause**: Python not in system PATH
- **Solution**: Bundle Python or provide installation instructions

**Issue**: "Deploy wrapper not working"
- **Cause**: Shell alias not configured
- **Solution**: Provide setup instructions in app

---

## 📊 Build Metrics

### Current Build Sizes
- **DMG Installer**: 182MB
- **ZIP Portable**: 176MB
- **App Bundle**: ~180MB

### Performance Targets
- **Startup Time**: < 3 seconds
- **Memory Usage**: < 200MB idle
- **CPU Usage**: < 5% idle

---

## 🔮 Future Enhancements

### Multi-Platform Support
```bash
# Windows build configuration
"win": {
  "target": "nsis",
  "icon": "build/icon.ico"
}

# Linux build configuration  
"linux": {
  "target": "AppImage",
  "icon": "build/icon.png"
}
```

### CI/CD Integration
```yaml
# .github/workflows/release.yml
name: Release
on:
  push:
    tags: ['v*']
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build:electron
      - uses: actions/upload-artifact@v3
```

---

## 📞 Support

### Build Support
- **Documentation**: This guide + Electron Builder docs
- **Issues**: Check GitHub Issues for build problems
- **Community**: Electron Discord for packaging help

### Distribution Support
- **Code Signing**: Apple Developer Documentation
- **App Store**: Apple Review Guidelines
- **Enterprise**: Custom deployment solutions

---

*This document should be updated with each major release to reflect new build requirements and distribution methods.* 