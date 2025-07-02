#!/bin/bash

# 🔄 Clean DeployBot Restart Script
# Ensures complete shutdown and clean startup

set -e  # Exit on any error

printf "\n🔄 DEPLOYBOT CLEAN RESTART\n"
printf "==========================\n\n"

# Step 1: Complete shutdown
printf "1️⃣ Shutting down all DeployBot processes...\n"
if [ -f "./scripts/shutdown_deploybot.sh" ]; then
    ./scripts/shutdown_deploybot.sh
else
    printf "   ⚠️ Shutdown script not found, doing manual cleanup...\n"
    pkill -f "Electron.*DeployBot" 2>/dev/null || true
    pkill -f "backend/graph.py" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    lsof -ti:8765 | xargs kill -9 2>/dev/null || true
fi

# Step 2: Wait for complete shutdown
printf "\n2️⃣ Waiting for processes to fully terminate...\n"
sleep 3

# Step 3: Force kill any remaining processes
printf "3️⃣ Force cleaning any remaining processes...\n"
REMAINING_PIDS=$(ps aux | grep -E "(electron.*[Dd]eploybot|[Dd]eployBot|backend/graph\.py)" | grep -v grep | awk '{print $2}' || true)
if [ ! -z "$REMAINING_PIDS" ]; then
    printf "   🔨 Force killing remaining PIDs: %s\n" "$REMAINING_PIDS"
    printf "%s\n" "$REMAINING_PIDS" | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Step 4: Clean ports
printf "4️⃣ Cleaning up ports...\n"
lsof -ti:8765 | xargs kill -9 2>/dev/null && printf "   ✅ Port 8765 cleaned\n" || printf "   ✅ Port 8765 was already clean\n"
lsof -ti:3000 | xargs kill -9 2>/dev/null && printf "   ✅ Port 3000 cleaned\n" || printf "   ✅ Port 3000 was already clean\n"

# Step 5: Build frontend if needed
printf "\n5️⃣ Building frontend for production...\n"
npm run build

# Step 6: Start backend
printf "\n6️⃣ Starting Python backend...\n"
python3 backend/graph.py > logs/activity.log 2>&1 &
BACKEND_PID=$!
printf "   🐍 Backend started with PID: %d\n" $BACKEND_PID

# Step 7: Wait for backend to be ready
printf "7️⃣ Waiting for backend to initialize...\n"
sleep 3

# Check if backend is responding
BACKEND_READY=false
for i in {1..10}; do
    if lsof -i :8765 >/dev/null 2>&1; then
        printf "   ✅ Backend responding on port 8765\n"
        BACKEND_READY=true
        break
    fi
    printf "   ⏳ Waiting for backend... (%d/10)\n" $i
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    printf "   ❌ Backend failed to start properly\n"
    printf "   📋 Check logs/activity.log for details\n"
    exit 1
fi

# Step 8: Start frontend
printf "\n8️⃣ Starting Electron frontend...\n"
NODE_ENV=production npm start &
FRONTEND_PID=$!
printf "   📱 Frontend started with PID: %d\n" $FRONTEND_PID

# Step 9: Verification
printf "\n9️⃣ Final verification...\n"
sleep 3

# Check processes
PYTHON_RUNNING=$(ps aux | grep "backend/graph.py" | grep -v grep | wc -l | xargs)
ELECTRON_RUNNING=$(ps aux | grep -E "electron.*DeployBot" | grep -v grep | grep -v "UE" | wc -l | xargs)

printf "   📊 Status Report:\n"
printf "      🐍 Python Backend: %s\n" "$([ $PYTHON_RUNNING -gt 0 ] && printf "✅ Running" || printf "❌ Not Running")"
printf "      📱 Electron Frontend: %s\n" "$([ $ELECTRON_RUNNING -gt 0 ] && printf "✅ Running" || printf "❌ Not Running")"
printf "      🔗 WebSocket Port: %s\n" "$(lsof -i :8765 >/dev/null 2>&1 && printf "✅ Active" || printf "❌ Inactive")"

if [ $PYTHON_RUNNING -gt 0 ] && [ $ELECTRON_RUNNING -gt 0 ]; then
    printf "\n🎉 SUCCESS! DeployBot is running cleanly\n"
    printf "   📱 App should be visible and responsive\n"
    printf "   🔗 Backend and frontend are connected\n"
    printf "\n📝 To stop: ./scripts/shutdown_deploybot.sh\n"
    printf "📝 To restart: ./scripts/clean_restart.sh\n"
else
    printf "\n❌ FAILED! Some components did not start properly\n"
    printf "   📋 Check logs/activity.log for backend issues\n"
    printf "   🔍 Check console for frontend issues\n"
    exit 1
fi

printf "\n==========================\n"
printf "🔄 CLEAN RESTART COMPLETE\n\n" 