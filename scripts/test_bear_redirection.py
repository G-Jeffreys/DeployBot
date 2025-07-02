#!/usr/bin/env python3
"""
Bear Redirection Debug Script
Tests the Bear app redirection system step by step to identify issues.
"""

import asyncio
import subprocess
import urllib.parse
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

try:
    from redirect import AppRedirector, logger  # type: ignore
except ImportError:
    print("❌ Could not import redirect module. Make sure you're running this from the DeployBot directory.")
    sys.exit(1)
import structlog

# Configure logging for debugging
structlog.configure(
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

async def test_bear_step_by_step():
    """Test Bear redirection with detailed debugging"""
    
    print("🐻 Bear Redirection Debug Test")
    print("=" * 50)
    
    # Test data
    test_task = {
        "text": "Write documentation for unified notifications",
        "app": "Bear",
        "tags": ["#writing", "#docs"],
        "estimated_duration": 25
    }
    
    test_context = {
        "project_name": "DeployBot",
        "project_path": "/Users/georgejeffreys/Documents/DeployBot",
        "deploy_command": "firebase deploy --hosting",
        "deploy_active": True,
        "timer_duration": 1800
    }
    
    redirector = AppRedirector()
    
    print("📋 Test Configuration:")
    print(f"   Task: {test_task['text']}")
    print(f"   App: {test_task['app']}")
    print(f"   Tags: {test_task['tags']}")
    print(f"   Project: {test_context['project_name']}")
    print()
    
    # Step 1: Test Bear availability
    print("🔍 Step 1: Testing Bear availability")
    try:
        result = subprocess.run(['open', '-a', 'Bear', '--args', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("   ✅ Bear is installed and accessible")
        else:
            print(f"   ❌ Bear availability test failed: {result.stderr}")
            return
    except Exception as e:
        print(f"   ❌ Bear availability test error: {e}")
        return
    
    # Step 2: Test note content generation
    print("\n📝 Step 2: Testing note content generation")
    try:
        note_content = redirector._generate_bear_note_content(test_task, test_context)
        print(f"   ✅ Note content generated ({len(note_content)} characters)")
        print(f"   Preview: {repr(note_content[:100])}")
        
        # Test URL encoding
        encoded_content = urllib.parse.quote(note_content)
        print(f"   ✅ URL encoding successful ({len(encoded_content)} characters)")
        
        if len(encoded_content) > 2000:
            print(f"   ⚠️  Warning: Encoded content is very long ({len(encoded_content)} chars)")
            print("      This might cause issues with URL schemes")
        
    except Exception as e:
        print(f"   ❌ Note content generation failed: {e}")
        return
    
    # Step 3: Test URL scheme construction
    print("\n🔗 Step 3: Testing Bear URL scheme construction")
    try:
        title = urllib.parse.quote(test_task['text'])
        content = urllib.parse.quote(note_content)
        bear_url = f"bear://x-callback-url/create?title={title}&text={content}"
        
        print(f"   ✅ Bear URL constructed ({len(bear_url)} characters)")
        print(f"   URL preview: {bear_url[:150]}...")
        
        if len(bear_url) > 8192:
            print(f"   ❌ URL is too long ({len(bear_url)} chars) - might exceed URL limits")
        
    except Exception as e:
        print(f"   ❌ URL construction failed: {e}")
        return
    
    # Step 4: Test simple Bear opening (without URL scheme)
    print("\n📱 Step 4: Testing simple Bear opening")
    try:
        result = subprocess.run(['open', '-a', 'Bear'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Simple Bear opening successful")
            print("   Check if Bear opened - you should see it in your dock/applications")
        else:
            print(f"   ❌ Simple Bear opening failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Simple Bear opening error: {e}")
    
    # Step 5: Test Bear URL scheme (simplified)
    print("\n🔗 Step 5: Testing simplified Bear URL scheme")
    try:
        simple_url = "bear://x-callback-url/create?title=DeployBot%20Test&text=This%20is%20a%20test%20note"
        print(f"   Trying simplified URL: {simple_url}")
        
        result = subprocess.run(['open', simple_url], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("   ✅ Simplified Bear URL scheme successful")
            print("   Check Bear - you should see a new note called 'DeployBot Test'")
        else:
            print(f"   ❌ Simplified Bear URL scheme failed: {result.stderr}")
    except Exception as e:
        print(f"   ❌ Simplified Bear URL scheme error: {e}")
    
    # Step 6: Test the full redirection system
    print("\n🎯 Step 6: Testing full redirection system")
    try:
        result = await redirector.redirect_to_task(test_task, test_context)
        
        print("   Redirection result:")
        print(f"   - Success: {result.get('success')}")
        print(f"   - Method: {result.get('method')}")
        print(f"   - App: {result.get('app')}")
        if result.get('error'):
            print(f"   - Error: {result.get('error')}")
        if result.get('action'):
            print(f"   - Action: {result.get('action')}")
            
    except Exception as e:
        print(f"   ❌ Full redirection test error: {e}")
    
    print("\n🔍 Debug Complete!")
    print("If Bear didn't open or create a note, check the terminal output above for specific errors.")

async def test_simple_bear_opening():
    """Test just opening Bear without any URL schemes"""
    print("\n🐻 Simple Bear Opening Test")
    print("-" * 30)
    
    try:
        print("Opening Bear...")
        result = subprocess.run(['open', '-a', 'Bear'], 
                              capture_output=True, text=True, timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Bear opening successful!")
        else:
            print("❌ Bear opening failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def test_bear_url_scheme():
    """Test Bear URL scheme with a simple note"""
    print("\n🔗 Bear URL Scheme Test")
    print("-" * 30)
    
    simple_url = "bear://x-callback-url/create?title=Test&text=Hello%20from%20DeployBot"
    
    try:
        print(f"Testing URL: {simple_url}")
        result = subprocess.run(['open', simple_url], 
                              capture_output=True, text=True, timeout=10)
        
        print(f"Return code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode == 0:
            print("✅ Bear URL scheme successful!")
            print("Check Bear for a new note called 'Test'")
        else:
            print("❌ Bear URL scheme failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "simple":
            await test_simple_bear_opening()
        elif sys.argv[1] == "url":
            await test_bear_url_scheme()
        else:
            print("Usage: python test_bear_redirection.py [simple|url]")
    else:
        await test_bear_step_by_step()

if __name__ == "__main__":
    asyncio.run(main()) 