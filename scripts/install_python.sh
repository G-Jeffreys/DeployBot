#!/bin/bash
# DeployBot Python Installation Script
# Usage: curl -sSL https://raw.githubusercontent.com/your-username/DeployBot/main/scripts/install_python.sh | bash

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

log_info "🐍 DeployBot Python Installation Script"
echo ""

# Check if Python is already installed
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        log_success "Python $PYTHON_VERSION is already installed and compatible!"
        PYTHON_INSTALLED=true
    else
        log_warning "Python $PYTHON_VERSION is installed but too old (need 3.9+)"
        PYTHON_INSTALLED=false
    fi
else
    log_info "Python 3 not found, will install it"
    PYTHON_INSTALLED=false
fi

# Install Python if needed
if [ "$PYTHON_INSTALLED" = false ]; then
    log_info "Installing Python 3.11..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        log_info "Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for current session
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -f "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
    
    # Install Python
    brew install python@3.11
    log_success "Python 3.11 installed successfully!"
fi

# Verify Python installation
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    log_success "Python verified: $PYTHON_VERSION"
else
    log_error "Python installation failed!"
    exit 1
fi

# Install DeployBot dependencies
log_info "Installing DeployBot Python dependencies..."

# Define required packages with versions
PACKAGES=(
    "langgraph>=0.0.55"
    "langchain>=0.1.0"
    "langchain-openai>=0.1.0"
    "websockets>=12.0"
    "structlog>=24.1.0"
    "python-dotenv>=1.0.1"
    "watchdog>=4.0.0"
    "asyncio-mqtt>=0.16.1"
    "colorama>=0.4.6"
)

# Install packages (using --user to avoid PEP 668 conflicts)
for package in "${PACKAGES[@]}"; do
    log_info "Installing $package..."
    pip3 install --user "$package" || {
        log_warning "System install failed, trying with --break-system-packages..."
        pip3 install --break-system-packages "$package" || {
            log_error "Failed to install $package"
            exit 1
        }
    }
done

log_success "All dependencies installed successfully!"

# Test installation
log_info "Testing DeployBot dependencies..."
python3 -c "
try:
    import langgraph
    import websockets
    import structlog
    import langchain
    print('✅ All DeployBot dependencies are working!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
" || {
    log_error "Dependency test failed!"
    exit 1
}

log_success "🎉 Python setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Launch DeployBot from your Applications folder"
echo "   2. Create your first project"
echo "   3. Set up the deploy wrapper (DeployBot will guide you)"
echo ""
echo "🚀 Welcome to DeployBot!" 