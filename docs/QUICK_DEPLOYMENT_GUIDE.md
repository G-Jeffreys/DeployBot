# 🚀 Quick Deployment Guide

This is a simplified guide for quickly building and deploying DeployBot. For comprehensive details, see [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md).

---

## ⚡ Quick Start

### 1. One-Command Release
```bash
# Create and deploy a new release
./scripts/release.sh v1.0.1
```

### 2. Manual Build Process
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Build for production
npm run build:electron

# Find your built files in dist/
open dist/
```

---

## 📦 Build Outputs

After running `npm run build:electron`, you'll get:

- **`dist/DeployBot-1.0.0-arm64.dmg`** - Installer for macOS (182MB)
- **`dist/DeployBot-1.0.0-arm64-mac.zip`** - Portable app (176MB)  
- **`dist/mac-arm64/DeployBot.app`** - App bundle for testing

---

## 🧪 Quick Testing

```bash
# Test the built app
open dist/mac-arm64/DeployBot.app

# Or install the DMG
open dist/DeployBot-1.0.0-arm64.dmg
```

---

## 🔄 Release Workflow

1. **Make changes** to your code
2. **Commit changes** to git
3. **Run release script**: `./scripts/release.sh v1.0.1`
4. **Upload to GitHub Releases** (script will provide URL)
5. **Share the download links** with users

---

## 🐛 Common Issues

### Build Fails
```bash
# Clean and rebuild
npm run clean
npm install
npm run build:electron
```

### "Python not found" 
```bash
# Verify Python installation
which python3
pip install -r requirements.txt
```

### App won't open on other Macs
- This is normal without code signing
- Users need to right-click → Open → Open anyway
- Or set up proper code signing (see full deployment guide)

---

## 📋 Distribution Checklist

- [ ] Build works locally
- [ ] App launches without errors  
- [ ] Python backend starts correctly
- [ ] WebSocket communication works
- [ ] Deploy detection functions
- [ ] Task selection working
- [ ] Created GitHub release with DMG/ZIP files
- [ ] Updated changelog
- [ ] Notified users

---

## 🔗 Quick Links

- **Full Deployment Guide**: [PRODUCTION_DEPLOYMENT.md](./PRODUCTION_DEPLOYMENT.md)
- **Architecture Overview**: [DeployBot_Full_Project_Overview.md](./DeployBot_Full_Project_Overview.md)
- **User Setup Guide**: [DEPLOY_WRAPPER.md](./DEPLOY_WRAPPER.md)

---

*For detailed configuration, code signing, auto-updates, and multi-platform builds, see the complete production deployment guide.* 