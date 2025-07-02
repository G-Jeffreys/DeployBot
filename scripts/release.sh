#!/bin/bash
# DeployBot Release Script
# Usage: ./scripts/release.sh v1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if version is provided
VERSION=$1
if [ -z "$VERSION" ]; then
    log_error "Version is required"
    echo "Usage: ./scripts/release.sh v1.0.0"
    exit 1
fi

# Validate version format
if [[ ! $VERSION =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    log_error "Invalid version format. Use vX.Y.Z (e.g., v1.0.0)"
    exit 1
fi

# Extract version number without 'v' prefix
VERSION_NUMBER=${VERSION#v}

log_info "Starting DeployBot release process for $VERSION"

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    log_warning "You're on branch '$CURRENT_BRANCH', not 'main'"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Release cancelled"
        exit 0
    fi
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    log_error "You have uncommitted changes. Please commit or stash them first."
    git status --short
    exit 1
fi

# Check if tag already exists
if git tag -l | grep -q "^$VERSION$"; then
    log_error "Tag $VERSION already exists"
    exit 1
fi

# Update version in package.json
log_info "Updating version in package.json to $VERSION_NUMBER"
npm version $VERSION_NUMBER --no-git-tag-version

# Install dependencies if needed
log_info "Installing/updating dependencies"
npm install
pip install -r requirements.txt

# Run any pre-release checks
log_info "Running pre-release checks"

# Check if Python backend can start
log_info "Testing Python backend startup"
python3 -c "
import sys
sys.path.append('langgraph')
try:
    from graph import DeployBotState
    print('✅ Python backend imports successful')
except Exception as e:
    print(f'❌ Python backend import failed: {e}')
    sys.exit(1)
"

# Build frontend
log_info "Building frontend with Vite"
npm run build

# Package Electron app
log_info "Packaging Electron application"
log_warning "This may take several minutes..."
npm run build:electron

# Verify build outputs exist
DIST_DIR="dist"
DMG_FILE="$DIST_DIR/DeployBot-$VERSION_NUMBER-arm64.dmg"
ZIP_FILE="$DIST_DIR/DeployBot-$VERSION_NUMBER-arm64-mac.zip"
APP_BUNDLE="$DIST_DIR/mac-arm64/DeployBot.app"

if [ ! -f "$DMG_FILE" ]; then
    log_error "DMG file not found: $DMG_FILE"
    exit 1
fi

if [ ! -f "$ZIP_FILE" ]; then
    log_error "ZIP file not found: $ZIP_FILE"
    exit 1
fi

if [ ! -d "$APP_BUNDLE" ]; then
    log_error "App bundle not found: $APP_BUNDLE"
    exit 1
fi

# Test that the built app can launch
log_info "Testing built application launch"
timeout 10 open "$APP_BUNDLE" || {
    log_warning "App launch test timed out (this is normal)"
}

# Show build information
log_success "Build completed successfully!"
echo ""
echo "📦 Build artifacts:"
echo "   DMG: $(ls -lh "$DMG_FILE" | awk '{print $5}') - $DMG_FILE"
echo "   ZIP: $(ls -lh "$ZIP_FILE" | awk '{print $5}') - $ZIP_FILE"
echo "   APP: $APP_BUNDLE"
echo ""

# Commit version change
log_info "Committing version bump"
git add package.json package-lock.json
git commit -m "Release $VERSION

- Bump version to $VERSION_NUMBER
- Update dependencies
- Build artifacts generated"

# Create git tag
log_info "Creating git tag $VERSION"
git tag -a $VERSION -m "Release $VERSION

## Features
- [Add release features here]

## Bug Fixes
- [Add bug fixes here]

## Dependencies
- Node.js $(node --version)
- npm $(npm --version)
- Electron $(npm list electron --depth=0 2>/dev/null | grep electron | cut -d'@' -f2)

## Build Info
- Built on: $(date)
- Platform: $(uname -s) $(uname -m)
- DMG Size: $(ls -lh "$DMG_FILE" | awk '{print $5}')
- ZIP Size: $(ls -lh "$ZIP_FILE" | awk '{print $5}')"

# Ask about pushing
echo ""
log_success "Release $VERSION prepared successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Review the changes: git show $VERSION"
echo "   2. Push to repository: git push origin main && git push origin $VERSION"
echo "   3. Create GitHub Release with build artifacts"
echo "   4. Update release notes"
echo "   5. Notify users of new version"
echo ""

read -p "Push to origin now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Pushing to origin..."
    git push origin main
    git push origin $VERSION
    
    log_success "Successfully pushed $VERSION to origin!"
    echo ""
    echo "🌐 GitHub Release URL:"
    echo "   https://github.com/$(git config remote.origin.url | sed 's/.*github.com[:/]\([^.]*\)\.git/\1/')/releases/new?tag=$VERSION"
    echo ""
    echo "📎 Upload these files to the GitHub Release:"
    echo "   - $DMG_FILE"
    echo "   - $ZIP_FILE"
    echo "   - $DIST_DIR/latest-mac.yml"
else
    log_info "Skipped pushing to origin"
    echo ""
    echo "🔄 To push later, run:"
    echo "   git push origin main"
    echo "   git push origin $VERSION"
fi

echo ""
log_success "Release process completed for $VERSION! 🎉" 