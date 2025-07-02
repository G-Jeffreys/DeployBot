#!/usr/bin/env python3
"""
Monitor deploy detection workflow in real-time
"""

import asyncio
import json
import websockets
import time

async def monitor_deploy_realtime():
    """Monitor what happens when a deploy is detected in real-time"""
    try:
        uri = "ws://localhost:8765"
        print(f"🔌 [MONITOR] Connecting to WebSocket at {uri}")
        
        async with websockets.connect(uri) as websocket:
            print("✅ [MONITOR] Connected to WebSocket")
            print("📡 [MONITOR] Listening for deploy events in real-time...")
            print("🚀 [MONITOR] Now run: deploybot echo 'real-time monitoring test'")
            print("=" * 60)
            
            # Listen for all messages and look for deploy-related activity
            message_count = 0
            deploy_detected = False
            task_activity = False
            notification_activity = False
            
            while message_count < 50:  # Monitor for 50 messages or timeout
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    message_count += 1
                    
                    try:
                        msg_data = json.loads(message)
                        msg_type = msg_data.get('type', 'unknown')
                        
                        # Print all messages to see the full flow
                        print(f"📨 [{message_count:02d}] {msg_type}: {json.dumps(msg_data, indent=2)}")
                        
                        # Look for specific deploy-related events
                        if msg_type == 'deploy':
                            deploy_detected = True
                            print(f"🚀 [DEPLOY EVENT DETECTED] {msg_data}")
                            
                        elif msg_type == 'task':
                            task_activity = True
                            print(f"📋 [TASK EVENT DETECTED] {msg_data}")
                            
                        elif msg_type == 'notification':
                            notification_activity = True
                            print(f"🔔 [NOTIFICATION EVENT DETECTED] {msg_data}")
                            
                        elif 'deploy' in str(msg_data).lower():
                            print(f"🔍 [DEPLOY-RELATED] {msg_data}")
                            
                        elif 'task' in str(msg_data).lower():
                            print(f"🔍 [TASK-RELATED] {msg_data}")
                            
                        elif 'notification' in str(msg_data).lower():
                            print(f"🔍 [NOTIFICATION-RELATED] {msg_data}")
                        
                        print("-" * 40)
                        
                    except json.JSONDecodeError:
                        print(f"📨 [{message_count:02d}] RAW: {message}")
                        print("-" * 40)
                        
                except asyncio.TimeoutError:
                    print("⏰ [MONITOR] No messages for 2 seconds...")
                    
            print("\n" + "=" * 60)
            print("📊 [SUMMARY] Real-time monitoring results:")
            print(f"   Deploy events detected: {deploy_detected}")
            print(f"   Task events detected: {task_activity}")
            print(f"   Notification events detected: {notification_activity}")
            print(f"   Total messages: {message_count}")
            
            if not deploy_detected:
                print("❌ [ISSUE] No deploy events detected - Deploy Monitor may not be working")
            elif not task_activity:
                print("❌ [ISSUE] Deploy detected but no task activity - Task selection failing")
            elif not notification_activity:
                print("❌ [ISSUE] Tasks found but no notifications - Notification system failing")
            else:
                print("✅ [SUCCESS] Full workflow detected!")
            
    except Exception as e:
        print(f"❌ [MONITOR] Error: {e}")
        import traceback
        print(f"❌ [MONITOR] Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(monitor_deploy_realtime()) 