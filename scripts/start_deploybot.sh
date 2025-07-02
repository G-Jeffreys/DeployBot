#!/bin/bash

# DeployBot Comprehensive Startup Script
# Handles cleanup, validation, and coordinated startup

set -e  # Exit on any error

echo "🚀 DeployBot Comprehensive Startup Script"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WEBSOCKET_PORT=8765
PYTHON_ENV_PATH="deploybot-env"
BACKEND_PATH="backend"
LOG_DIR="logs"
MAX_RETRIES=3
RETRY_DELAY=5

# Log function
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we're in the correct directory
check_directory() {
    log "🔍 Checking project directory..."
    
    if [[ ! -f "package.json" ]] || [[ ! -d "backend" ]] || [[ ! -d "main" ]]; then
        error "❌ Not in DeployBot project directory!"
        error "Please run this script from the DeployBot root directory."
        exit 1
    fi
    
    success "✅ In correct project directory"
}

# Comprehensive cleanup of existing processes
cleanup_existing_processes() {
    log "🧹 Performing comprehensive process cleanup..."
    
    # Kill any Python processes related to DeployBot
    log "🐍 Cleaning up Python processes..."
    if pgrep -f "python.*deploybot" > /dev/null 2>&1; then
        pkill -f "python.*deploybot" && success "✅ Python processes killed" || warning "⚠️ Some Python processes might still be running"
    else
        log "ℹ️ No Python processes found"
    fi
    
    # Kill any processes on WebSocket port
    log "🔌 Cleaning up WebSocket port ${WEBSOCKET_PORT}..."
    if lsof -ti:${WEBSOCKET_PORT} > /dev/null 2>&1; then
        lsof -ti:${WEBSOCKET_PORT} | xargs kill -9 2>/dev/null && success "✅ Port ${WEBSOCKET_PORT} processes killed" || warning "⚠️ Some port processes might still be running"
    else
        log "ℹ️ Port ${WEBSOCKET_PORT} is clear"
    fi
    
    # Kill any Electron processes related to DeployBot
    log "⚡ Cleaning up Electron processes..."
    if pgrep -f "electron.*deploybot" > /dev/null 2>&1; then
        pkill -f "electron.*deploybot" && success "✅ Electron processes killed" || warning "⚠️ Some Electron processes might still be running"
    else
        log "ℹ️ No Electron processes found"
    fi
    
    # Wait for processes to fully terminate
    log "⏳ Waiting for processes to terminate..."
    sleep 2
    
    # Verify cleanup
    remaining_processes=$(ps aux | grep -i deploybot | grep -v grep | wc -l)
    if [[ $remaining_processes -eq 0 ]]; then
        success "✅ All DeployBot processes cleaned up"
    else
        warning "⚠️ ${remaining_processes} processes may still be running"
        ps aux | grep -i deploybot | grep -v grep | head -5
    fi
}

# Validate Python environment
validate_python_environment() {
    log "🐍 Validating Python environment..."
    
    if [[ ! -d "$PYTHON_ENV_PATH" ]]; then
        error "❌ Python environment not found at: $PYTHON_ENV_PATH"
        error "Please run the Python setup script first"
        exit 1
    fi
    
    local python_executable="$PYTHON_ENV_PATH/bin/python3"
    if [[ ! -f "$python_executable" ]]; then
        error "❌ Python executable not found: $python_executable"
        exit 1
    fi
    
    # Test Python environment
    if ! "$python_executable" --version > /dev/null 2>&1; then
        error "❌ Python environment is not working"
        exit 1
    fi
    
    # Check required Python packages
    log "📦 Checking Python dependencies..."
    local required_packages=("websockets" "asyncio" "structlog")
    for package in "${required_packages[@]}"; do
        if ! "$python_executable" -c "import $package" > /dev/null 2>&1; then
            error "❌ Required Python package '$package' not found"
            error "Please reinstall Python dependencies: pip install -r requirements.txt"
            exit 1
        fi
    done
    
    success "✅ Python environment validated"
}

# Validate backend files
validate_backend_files() {
    log "📄 Validating backend files..."
    
    local required_files=("graph.py" "logger.py" "monitor.py" "notification.py" "project_manager.py" "redirect.py" "tasks.py" "timer.py")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$BACKEND_PATH/$file" ]]; then
            error "❌ Required backend file not found: $BACKEND_PATH/$file"
            exit 1
        fi
    done
    
    success "✅ Backend files validated"
}

# Validate Node.js environment
validate_node_environment() {
    log "📦 Validating Node.js environment..."
    
    if ! command -v node > /dev/null 2>&1; then
        error "❌ Node.js not found"
        exit 1
    fi
    
    if ! command -v npm > /dev/null 2>&1; then
        error "❌ npm not found"
        exit 1
    fi
    
    if [[ ! -f "package.json" ]]; then
        error "❌ package.json not found"
        exit 1
    fi
    
    if [[ ! -d "node_modules" ]]; then
        warning "⚠️ node_modules not found, installing dependencies..."
        npm install
    fi
    
    success "✅ Node.js environment validated"
}

# Check port availability
check_port_availability() {
    log "🔌 Checking port availability..."
    
    if lsof -i:${WEBSOCKET_PORT} > /dev/null 2>&1; then
        warning "⚠️ Port ${WEBSOCKET_PORT} is in use. Attempting cleanup..."
        lsof -ti:${WEBSOCKET_PORT} | xargs kill -9 2>/dev/null || true
        sleep 2
        
        if lsof -i:${WEBSOCKET_PORT} > /dev/null 2>&1; then
            error "❌ Port ${WEBSOCKET_PORT} is still in use after cleanup"
            lsof -i:${WEBSOCKET_PORT}
            exit 1
        fi
    fi
    
    success "✅ Port ${WEBSOCKET_PORT} is available"
}

# Prepare log directory
prepare_logs() {
    log "📋 Preparing log directory..."
    
    mkdir -p "$LOG_DIR"
    
    # Clean old logs (keep last 10 files)
    find "$LOG_DIR" -name "*.log" -type f | sort | head -n -10 | xargs rm -f 2>/dev/null || true
    
    success "✅ Log directory prepared"
}

# Test backend startup (quick validation)
test_backend_startup() {
    log "🧪 Testing backend startup..."
    
    local python_executable="$PYTHON_ENV_PATH/bin/python3"
    local test_timeout=10
    
    # Start backend in background with timeout
    timeout $test_timeout "$python_executable" "$BACKEND_PATH/graph.py" > /dev/null 2>&1 &
    local backend_pid=$!
    
    # Wait a moment for startup
    sleep 3
    
    # Check if process is still running
    if kill -0 $backend_pid 2>/dev/null; then
        # Try to connect to WebSocket
        if command -v curl > /dev/null 2>&1; then
            if curl -s --max-time 5 http://localhost:${WEBSOCKET_PORT} > /dev/null 2>&1; then
                success "✅ Backend startup test successful"
            else
                warning "⚠️ Backend started but WebSocket not responding"
            fi
        else
            success "✅ Backend process started successfully"
        fi
        
        # Clean up test process
        kill $backend_pid 2>/dev/null || true
        wait $backend_pid 2>/dev/null || true
    else
        error "❌ Backend failed to start"
        exit 1
    fi
    
    # Clean up any remaining processes
    sleep 1
    lsof -ti:${WEBSOCKET_PORT} | xargs kill -9 2>/dev/null || true
}

# Main startup function
start_deploybot() {
    log "🚀 Starting DeployBot..."
    
    # Determine startup mode
    local start_mode="${1:-dev}"
    
    case $start_mode in
        "dev"|"development")
            log "🔧 Starting in development mode..."
            npm run dev
            ;;
        "prod"|"production")
            log "📦 Starting in production mode..."
            npm start
            ;;
        "build")
            log "🏗️ Building and starting..."
            npm run build
            npm start
            ;;
        *)
            error "❌ Invalid start mode: $start_mode"
            error "Available modes: dev, prod, build"
            exit 1
            ;;
    esac
}

# Handle script interruption
cleanup_on_exit() {
    log "🛑 Startup script interrupted, cleaning up..."
    cleanup_existing_processes
    exit 1
}

# Set up signal handlers
trap cleanup_on_exit SIGINT SIGTERM

# Main execution flow
main() {
    local start_mode="${1:-dev}"
    
    log "🎯 Starting DeployBot in '$start_mode' mode..."
    
    # Pre-flight checks
    check_directory
    cleanup_existing_processes
    validate_python_environment
    validate_backend_files
    validate_node_environment
    check_port_availability
    prepare_logs
    
    # Optional: Test backend startup
    if [[ "${2:-}" == "--test-backend" ]]; then
        test_backend_startup
    fi
    
    # Start DeployBot
    success "✅ All pre-flight checks passed!"
    log "🚀 Launching DeployBot..."
    
    start_deploybot "$start_mode"
}

# Show usage if requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [mode] [options]"
    echo ""
    echo "Modes:"
    echo "  dev         Start in development mode (default)"
    echo "  prod        Start in production mode"
    echo "  build       Build and start in production mode"
    echo ""
    echo "Options:"
    echo "  --test-backend    Test backend startup before launching"
    echo "  --help, -h       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Start in development mode"
    echo "  $0 dev --test-backend # Start in dev mode with backend test"
    echo "  $0 prod              # Start in production mode"
    echo ""
    exit 0
fi

# Run main function with all arguments
main "$@" 