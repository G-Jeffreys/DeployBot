#!/bin/bash

# 🛑 DeployBot Complete Shutdown Script
# This script ensures clean shutdown of all DeployBot processes

echo "🛑 DEPLOYBOT SHUTDOWN INITIATED..."
echo "================================"

# Step 1: Graceful app quit attempt
echo "1️⃣ Attempting graceful shutdown..."
osascript -e 'tell application "DeployBot" to quit' 2>/dev/null && echo "   ✅ App quit gracefully" || echo "   ⚠️ App quit failed or not running"

# Step 2: Wait for graceful shutdown
echo "2️⃣ Waiting for graceful shutdown..."
sleep 3

# Step 3: Kill Electron processes
echo "3️⃣ Killing Electron DeployBot processes..."
pkill -f "Electron.*DeployBot" && echo "   ✅ Electron processes killed" || echo "   ⚠️ No Electron processes found"

# Step 4: Kill Python backend
echo "4️⃣ Stopping Python backend..."
pkill -f "backend/graph.py" && echo "   ✅ Python backend stopped" || echo "   ⚠️ No Python backend found"

# Step 5: Kill development server
echo "5️⃣ Stopping development servers..."
pkill -f "vite" && echo "   ✅ Vite dev server stopped" || echo "   ⚠️ No Vite dev server found"
pkill -f "esbuild" && echo "   ✅ Esbuild processes stopped" || echo "   ⚠️ No esbuild processes found"

# Step 6: Kill installed app
echo "6️⃣ Killing installed DeployBot app..."
killall "DeployBot" 2>/dev/null && echo "   ✅ Installed app killed" || echo "   ⚠️ No installed app found"

# Step 7: Clean up ports
echo "7️⃣ Cleaning up ports..."
lsof -ti:8765 | xargs kill -9 2>/dev/null && echo "   ✅ Port 8765 cleaned" || echo "   ✅ Port 8765 was already clean"

# Step 8: Force kill any remaining processes
echo "8️⃣ Force killing any remaining processes..."
REMAINING_PIDS=$(ps aux | grep -E "(electron.*deploybot|DeployBot|backend/graph\.py)" | grep -v grep | awk '{print $2}')
if [ ! -z "$REMAINING_PIDS" ]; then
    echo "   🔨 Force killing PIDs: $REMAINING_PIDS"
    echo $REMAINING_PIDS | xargs kill -9 2>/dev/null
    echo "   ✅ Remaining processes force killed"
else
    echo "   ✅ No remaining processes found"
fi

# Step 9: Final verification
echo "9️⃣ Final verification..."
sleep 2
FINAL_COUNT=$(ps aux | grep -E "(electron.*deploybot|DeployBot|backend/graph\.py)" | grep -v grep | wc -l | xargs)
if [ "$FINAL_COUNT" -eq 0 ]; then
    echo "   ✅ All DeployBot processes successfully terminated"
    echo ""
    echo "🎉 SHUTDOWN COMPLETE - No zombie processes remaining!"
    echo "   You can now safely restart DeployBot or work on other projects."
else
    echo "   ⚠️ Warning: $FINAL_COUNT processes still running"
    echo "   Remaining processes:"
    ps aux | grep -E "(electron.*deploybot|DeployBot|backend/graph\.py)" | grep -v grep
fi

echo "================================"
echo "🔄 To restart DeployBot, run: npm start" 