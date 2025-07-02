#!/usr/bin/env python3
"""
DeployBot Notification Troubleshooting Script
============================================

This script helps diagnose and fix notification issues on macOS.
Run this script to identify why notifications aren't appearing.
"""

import asyncio
import subprocess
import sys
import os
from datetime import datetime

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def print_test(test_name, description):
    print(f"\n📋 {test_name}")
    print(f"   {description}")

async def run_command(command, description="Running command"):
    """Run a shell command and return the result"""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        )
        return result
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return None

async def test_basic_notifications():
    print_header("BASIC NOTIFICATION TESTS")
    
    # Test 1: Basic osascript
    print_test("Test 1", "Basic osascript notification")
    result = await run_command(
        'osascript -e \'display notification "Test 1: Basic notification" with title "DeployBot Test" subtitle "Method 1"\'',
        "Basic osascript"
    )
    if result and result.returncode == 0:
        print("✅ Basic osascript: SUCCESS")
    else:
        print(f"❌ Basic osascript: FAILED - {result.stderr if result else 'Unknown error'}")
    
    # Test 2: System Events approach
    print_test("Test 2", "System Events notification")
    result = await run_command(
        'osascript -e \'tell application "System Events" to display notification "Test 2: System Events" with title "DeployBot Test" subtitle "Method 2"\'',
        "System Events"
    )
    if result and result.returncode == 0:
        print("✅ System Events: SUCCESS")
    else:
        print(f"❌ System Events: FAILED - {result.stderr if result else 'Unknown error'}")
    
    # Test 3: Terminal bell
    print_test("Test 3", "Terminal bell (audible)")
    result = await run_command('echo -e "\\a🔔 DeployBot: Terminal bell test"', "Terminal bell")
    if result and result.returncode == 0:
        print("✅ Terminal bell: SUCCESS (listen for sound)")
    else:
        print("❌ Terminal bell: FAILED")

async def check_system_settings():
    print_header("SYSTEM SETTINGS ANALYSIS")
    
    # Check 1: Do Not Disturb status
    print_test("Check 1", "Do Not Disturb status")
    result = await run_command(
        'defaults read ~/Library/Preferences/com.apple.ncprefs.plist dnd_prefs 2>/dev/null',
        "DND check"
    )
    if result and result.returncode == 0 and result.stdout.strip():
        print("⚠️  Do Not Disturb preferences found - this may be blocking notifications")
        print("   💡 Solution: Check menu bar for Focus/Do Not Disturb icon and disable it")
    else:
        print("✅ Do Not Disturb: Not detected")
    
    # Check 2: NotificationCenter process
    print_test("Check 2", "NotificationCenter process")
    result = await run_command('pgrep -f NotificationCenter', "NotificationCenter check")
    if result and result.returncode == 0:
        print("✅ NotificationCenter: Running")
    else:
        print("❌ NotificationCenter: Not running")
    
    # Check 3: Terminal app permissions
    print_test("Check 3", "Terminal notification permissions")
    result = await run_command(
        'defaults read com.apple.ncprefs 2>/dev/null | grep -A10 -B10 Terminal || echo "No Terminal settings found"',
        "Terminal permissions"
    )
    if result and "No Terminal settings found" in result.stdout:
        print("⚠️  Terminal not found in notification preferences")
        print("   💡 Solution: Run a notification to trigger permission prompt")
    else:
        print("✅ Terminal: Found in notification settings")

def create_desktop_notification(message):
    """Create a visible notification file on desktop"""
    try:
        desktop_path = os.path.expanduser("~/Desktop/DeployBot_Notification_Test.txt")
        notification_text = f"""
🚀 DeployBot Notification Test
==============================
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Message: {message}

This file proves the notification system is working.
If you see this file but no system notifications, 
the issue is with macOS notification settings.

SOLUTIONS TO TRY:
================
1. Check System Preferences > Notifications & Focus
2. Look for "Terminal" and enable notifications
3. Disable Do Not Disturb mode
4. Check Focus settings
5. Restart Notification Center: 
   sudo killall NotificationCenter

You can delete this file after reading.
"""
        with open(desktop_path, 'w') as f:
            f.write(notification_text)
        print(f"📄 Created test file: {desktop_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create desktop file: {e}")
        return False

async def comprehensive_solutions():
    print_header("COMPREHENSIVE SOLUTIONS")
    
    print("🔧 Step-by-step fixes to try:")
    print("\n1️⃣ CHECK FOCUS/DO NOT DISTURB:")
    print("   • Look at the menu bar (top-right)")
    print("   • If you see a moon 🌙 or focus icon, click it and disable")
    print("   • System Preferences > Focus > Do Not Disturb > Turn Off")
    
    print("\n2️⃣ TERMINAL NOTIFICATION PERMISSIONS:")
    print("   • System Preferences > Notifications & Focus")
    print("   • Find 'Terminal' in the left sidebar")
    print("   • Set 'Alert Style' to 'Alerts' or 'Banners'")
    print("   • Enable 'Show in Notification Center'")
    print("   • Enable 'Show on Lock Screen'")
    
    print("\n3️⃣ RESET NOTIFICATION CENTER:")
    print("   Run this command: sudo killall NotificationCenter")
    print("   (NotificationCenter will restart automatically)")
    
    print("\n4️⃣ CHECK SCREEN TIME RESTRICTIONS:")
    print("   • System Preferences > Screen Time > App Limits")
    print("   • Ensure no restrictions on notifications")
    
    print("\n5️⃣ ALTERNATIVE: ENHANCED DEPLOYBOT NOTIFICATIONS:")
    print("   • DeployBot now creates desktop files as backup")
    print("   • Terminal bell sounds for audible alerts")
    print("   • In-app notifications via the DeployBot UI")
    
    # Create a test desktop notification
    create_desktop_notification("Comprehensive test completed")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Try the fixes above")
    print("   2. Run this script again to test")
    print("   3. Look for the test file on your Desktop")
    print("   4. Restart DeployBot and test with a real deployment")

async def main():
    print_header("DEPLOYBOT NOTIFICATION TROUBLESHOOTER")
    print("This script will help identify why notifications aren't working.\n")
    
    await test_basic_notifications()
    await asyncio.sleep(2)  # Give time for notifications to appear
    
    await check_system_settings()
    await comprehensive_solutions()
    
    print(f"\n{'='*50}")
    print("🏁 TROUBLESHOOTING COMPLETE")
    print("Check your screen and Desktop for test notifications!")
    print(f"{'='*50}\n")

if __name__ == "__main__":
    asyncio.run(main()) 