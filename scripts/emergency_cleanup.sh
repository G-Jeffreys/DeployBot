#!/bin/bash

# DeployBot Emergency Cleanup Script
# Use this when things go wrong and normal cleanup isn't working

set -e  # Exit on any error

echo "🚨 DeployBot Emergency Cleanup Script"
echo "====================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WEBSOCKET_PORT=8765
ALTERNATIVE_PORTS=(8766 8767 8768)  # Common alternative ports
MAX_WAIT_TIME=10

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

# Force kill all DeployBot related processes
force_kill_all_deploybot_processes() {
    log "💀 Force killing ALL DeployBot processes..."
    
    # Kill by process name patterns
    local patterns=("python.*deploybot" "electron.*deploybot" "deploybot" "node.*deploybot")
    
    for pattern in "${patterns[@]}"; do
        log "🔍 Searching for processes matching: $pattern"
        if pgrep -f "$pattern" > /dev/null 2>&1; then
            local pids=$(pgrep -f "$pattern")
            log "🔪 Found PIDs: $pids"
            
            # First try SIGTERM
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            
            # Then force kill any remaining
            for pid in $pids; do
                if kill -0 "$pid" 2>/dev/null; then
                    log "💥 Force killing stubborn process: $pid"
                    kill -KILL "$pid" 2>/dev/null || true
                fi
            done
        else
            log "ℹ️ No processes found for pattern: $pattern"
        fi
    done
    
    success "✅ Process cleanup completed"
}

# Aggressive port cleanup
aggressive_port_cleanup() {
    log "🧹 Aggressive port cleanup..."
    
    # Clean primary port
    cleanup_single_port $WEBSOCKET_PORT
    
    # Clean alternative ports that might be in use
    for port in "${ALTERNATIVE_PORTS[@]}"; do
        cleanup_single_port $port
    done
    
    success "✅ Port cleanup completed"
}

cleanup_single_port() {
    local port=$1
    log "🔌 Cleaning port $port..."
    
    if lsof -ti:$port > /dev/null 2>&1; then
        local pids=$(lsof -ti:$port)
        log "🔪 Found processes on port $port: $pids"
        
        # Kill processes using the port
        echo "$pids" | xargs kill -KILL 2>/dev/null || true
        
        # Wait and verify
        sleep 1
        if lsof -ti:$port > /dev/null 2>&1; then
            warning "⚠️ Port $port still has processes after cleanup"
            lsof -i:$port
        else
            success "✅ Port $port cleaned successfully"
        fi
    else
        log "ℹ️ Port $port is clean"
    fi
}

# Clean up temp directories
cleanup_temp_directories() {
    log "🗂️ Cleaning up temporary directories..."
    
    local temp_dirs=(
        "/tmp/deploybot-backend"
        "/tmp/deploybot-*"
        "$HOME/.cache/deploybot"
        "$HOME/.local/share/deploybot"
    )
    
    for dir_pattern in "${temp_dirs[@]}"; do
        # Use find to handle wildcards safely
        if [[ "$dir_pattern" == *"*"* ]]; then
            find /tmp -maxdepth 1 -name "$(basename "$dir_pattern")" -type d 2>/dev/null | while read -r dir; do
                if [[ -d "$dir" ]]; then
                    log "🗑️ Removing temp directory: $dir"
                    rm -rf "$dir" 2>/dev/null || warning "⚠️ Could not remove: $dir"
                fi
            done
        else
            if [[ -d "$dir_pattern" ]]; then
                log "🗑️ Removing temp directory: $dir_pattern"
                rm -rf "$dir_pattern" 2>/dev/null || warning "⚠️ Could not remove: $dir_pattern"
            fi
        fi
    done
    
    success "✅ Temp directory cleanup completed"
}

# Clean up log files
cleanup_logs() {
    log "📋 Cleaning up old log files..."
    
    local log_dirs=(
        "logs"
        "/tmp/deploybot-logs"
        "$HOME/.local/share/deploybot/logs"
    )
    
    for log_dir in "${log_dirs[@]}"; do
        if [[ -d "$log_dir" ]]; then
            log "🧹 Cleaning logs in: $log_dir"
            
            # Keep only the latest 5 log files
            find "$log_dir" -name "*.log" -type f | sort | head -n -5 | xargs rm -f 2>/dev/null || true
            
            # Remove empty log directory if it exists
            if [[ -d "$log_dir" ]] && [[ -z "$(ls -A "$log_dir")" ]]; then
                rmdir "$log_dir" 2>/dev/null || true
            fi
        fi
    done
    
    success "✅ Log cleanup completed"
}

# Reset file permissions
reset_permissions() {
    log "🔐 Resetting file permissions..."
    
    # Reset script permissions
    if [[ -f "scripts/start_deploybot.sh" ]]; then
        chmod +x scripts/start_deploybot.sh
        log "✅ Made start_deploybot.sh executable"
    fi
    
    if [[ -f "scripts/cleanup_processes.sh" ]]; then
        chmod +x scripts/cleanup_processes.sh
        log "✅ Made cleanup_processes.sh executable"
    fi
    
    if [[ -f "scripts/emergency_cleanup.sh" ]]; then
        chmod +x scripts/emergency_cleanup.sh
        log "✅ Made emergency_cleanup.sh executable"
    fi
    
    # Reset Python virtual environment permissions
    if [[ -d "deploybot-env" ]]; then
        chmod +x deploybot-env/bin/* 2>/dev/null || true
        log "✅ Reset Python virtual environment permissions"
    fi
    
    success "✅ Permission reset completed"
}

# Verify system state
verify_cleanup() {
    log "🔍 Verifying cleanup results..."
    
    # Check for remaining processes
    local remaining_processes=$(ps aux | grep -i deploybot | grep -v grep | grep -v "emergency_cleanup" | wc -l)
    if [[ $remaining_processes -eq 0 ]]; then
        success "✅ No DeployBot processes running"
    else
        warning "⚠️ $remaining_processes DeployBot processes still running:"
        ps aux | grep -i deploybot | grep -v grep | grep -v "emergency_cleanup" | head -5
    fi
    
    # Check port availability
    if lsof -i:$WEBSOCKET_PORT > /dev/null 2>&1; then
        warning "⚠️ Port $WEBSOCKET_PORT is still in use:"
        lsof -i:$WEBSOCKET_PORT
    else
        success "✅ Port $WEBSOCKET_PORT is available"
    fi
    
    # Check disk space
    local disk_usage=$(df . | tail -1 | awk '{print $5}' | tr -d '%')
    if [[ $disk_usage -gt 90 ]]; then
        warning "⚠️ Disk usage is high: ${disk_usage}%"
    else
        log "ℹ️ Disk usage: ${disk_usage}%"
    fi
}

# Display system information
show_system_info() {
    log "📊 System Information:"
    echo "  🖥️  OS: $(uname -s) $(uname -r)"
    echo "  💾 Memory: $(free -h | grep Mem | awk '{print $3 "/" $2}' 2>/dev/null || echo 'N/A')"
    echo "  💽 Disk: $(df -h . | tail -1 | awk '{print $3 "/" $2 " (" $5 " used)"}')"
    echo "  🕐 Time: $(date)"
    
    if command -v node > /dev/null 2>&1; then
        echo "  📦 Node.js: $(node --version)"
    fi
    
    if command -v python3 > /dev/null 2>&1; then
        echo "  🐍 Python: $(python3 --version)"
    fi
}

# Handle script interruption
cleanup_on_exit() {
    log "🛑 Emergency cleanup interrupted"
    exit 1
}

# Set up signal handlers
trap cleanup_on_exit SIGINT SIGTERM

# Main execution
main() {
    local skip_confirmation="${1:-}"
    
    log "🚨 Starting emergency cleanup procedure..."
    
    # Show system info
    show_system_info
    
    # Ask for confirmation unless skipped
    if [[ "$skip_confirmation" != "--force" ]]; then
        echo ""
        echo -e "${YELLOW}⚠️  WARNING: This will forcefully terminate ALL DeployBot processes!${NC}"
        echo -e "${YELLOW}⚠️  This should only be used when normal cleanup fails.${NC}"
        echo ""
        read -p "Continue with emergency cleanup? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "🛑 Emergency cleanup cancelled by user"
            exit 0
        fi
    fi
    
    log "🚀 Beginning emergency cleanup sequence..."
    
    # Execute cleanup steps
    force_kill_all_deploybot_processes
    aggressive_port_cleanup
    cleanup_temp_directories
    cleanup_logs
    reset_permissions
    
    # Wait for system to stabilize
    log "⏳ Waiting for system to stabilize..."
    sleep 3
    
    # Verify results
    verify_cleanup
    
    success "✅ Emergency cleanup completed!"
    echo ""
    echo -e "${GREEN}🎯 System should now be clean and ready for a fresh start.${NC}"
    echo -e "${BLUE}ℹ️  You can now run: ${NC}./scripts/start_deploybot.sh"
    echo ""
}

# Show usage if requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [--force]"
    echo ""
    echo "Emergency cleanup script for DeployBot system recovery."
    echo ""
    echo "Options:"
    echo "  --force    Skip confirmation prompt"
    echo "  --help     Show this help message"
    echo ""
    echo "This script will:"
    echo "  • Force kill all DeployBot processes"
    echo "  • Clean up all ports used by DeployBot"
    echo "  • Remove temporary directories"
    echo "  • Clean up old log files"
    echo "  • Reset file permissions"
    echo "  • Verify cleanup results"
    echo ""
    echo "⚠️  WARNING: This is a destructive operation!"
    echo "   Only use when normal cleanup methods fail."
    echo ""
    exit 0
fi

# Run main function
main "$@" 