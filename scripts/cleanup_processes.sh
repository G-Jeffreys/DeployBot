#!/bin/bash

echo "🧹 DeployBot Process Cleanup Script"
echo "=================================="

# Kill any Python processes related to DeployBot
echo "🐍 Killing DeployBot Python processes..."
pkill -f "python.*deploybot" && echo "✅ Python processes killed" || echo "ℹ️  No Python processes found"

# Kill any processes on port 8765
echo "🔌 Killing processes on port 8765..."
lsof -ti:8765 | xargs kill -9 2>/dev/null && echo "✅ Port 8765 processes killed" || echo "ℹ️  No processes on port 8765"

# Kill any Electron processes related to DeployBot
echo "⚡ Killing DeployBot Electron processes..."
pkill -f "electron.*deploybot" && echo "✅ Electron processes killed" || echo "ℹ️  No Electron processes found"

# Show remaining DeployBot-related processes
echo ""
echo "🔍 Remaining DeployBot processes:"
ps aux | grep -i deploybot | grep -v grep || echo "ℹ️  No DeployBot processes running"

echo ""
echo "✅ Cleanup completed!"
echo "You can now safely start DeployBot again." 