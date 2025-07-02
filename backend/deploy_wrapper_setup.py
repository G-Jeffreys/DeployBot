#!/usr/bin/env python3
"""
Deploy Wrapper Setup Automation for DeployBot

This module handles the automated installation and configuration of the 
deploy wrapper script, including per-project logging capabilities.
"""

import os
import stat
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import structlog

logger = structlog.get_logger()

class DeployWrapperManager:
    """Manages deploy wrapper installation and configuration"""
    
    def __init__(self):
        self.wrapper_dir = Path.home() / ".deploybot"
        self.wrapper_script = self.wrapper_dir / "deploybot-wrapper.py"
        self.shell_config_files = [
            Path.home() / ".zshrc",
            Path.home() / ".bashrc", 
            Path.home() / ".bash_profile"
        ]
        
        logger.info("🔧 [DEPLOY_WRAPPER] DeployWrapperManager initialized", 
                   wrapper_dir=str(self.wrapper_dir))

    async def check_installation_status(self) -> Dict[str, Any]:
        """Check the current installation status of deploy wrapper"""
        logger.info("🔍 [DEPLOY_WRAPPER] Checking installation status...")
        
        status = {
            "wrapper_script_exists": self.wrapper_script.exists(),
            "wrapper_script_executable": False,
            "alias_configured": False,
            "shell_detected": self.detect_shell(),
            "python_available": self.check_python_available(),
            "can_auto_install": True,
            "issues": []
        }
        
        # Check if script is executable
        if status["wrapper_script_exists"]:
            status["wrapper_script_executable"] = os.access(self.wrapper_script, os.X_OK)
            logger.info("✅ [DEPLOY_WRAPPER] Wrapper script exists and is executable")
        
        # Check for existing alias
        status["alias_configured"] = await self.check_alias_exists()
        
        # Check for any blocking issues
        if not status["python_available"]:
            status["issues"].append("Python 3 not found in PATH")
            status["can_auto_install"] = False
        
        logger.info("📊 [DEPLOY_WRAPPER] Installation status checked", 
                   status=status)
        return status

    def detect_shell(self) -> str:
        """Detect the user's current shell"""
        shell = os.environ.get('SHELL', '/bin/bash')
        shell_name = Path(shell).name
        logger.info("🐚 [DEPLOY_WRAPPER] Detected shell", shell=shell_name)
        return shell_name

    def check_python_available(self) -> bool:
        """Check if Python 3 is available"""
        try:
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            available = result.returncode == 0
            logger.info("🐍 [DEPLOY_WRAPPER] Python availability checked", 
                       available=available, version=result.stdout.strip() if available else None)
            return available
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            logger.warning("⚠️ [DEPLOY_WRAPPER] Python check failed", error=str(e))
            return False

    async def check_alias_exists(self) -> bool:
        """Check if deploybot alias exists in shell config"""
        logger.info("🔍 [DEPLOY_WRAPPER] Checking for existing alias...")
        
        for config_file in self.shell_config_files:
            if config_file.exists():
                try:
                    content = config_file.read_text()
                    if 'alias deploybot=' in content:
                        logger.info("✅ [DEPLOY_WRAPPER] Found existing alias", 
                                   config_file=str(config_file))
                        return True
                except Exception as e:
                    logger.warning("⚠️ [DEPLOY_WRAPPER] Error reading config file", 
                                 config_file=str(config_file), error=str(e))
        
        logger.info("❌ [DEPLOY_WRAPPER] No existing alias found")
        return False

    async def install_wrapper(self, project_name: Optional[str] = None) -> Dict[str, Any]:
        """Install the deploy wrapper script and configure shell alias"""
        logger.info("🚀 [DEPLOY_WRAPPER] Starting wrapper installation...", 
                   project_name=project_name)
        
        try:
            # Create wrapper directory
            self.wrapper_dir.mkdir(exist_ok=True)
            logger.info("📁 [DEPLOY_WRAPPER] Created wrapper directory")
            
            # Create the wrapper script with per-project logging
            await self.create_wrapper_script()
            
            # Make script executable
            self.wrapper_script.chmod(self.wrapper_script.stat().st_mode | stat.S_IEXEC)
            logger.info("🔧 [DEPLOY_WRAPPER] Made wrapper script executable")
            
            # Add shell alias
            await self.add_shell_alias()
            
            # Test the installation
            test_result = await self.test_installation()
            
            result = {
                "success": True,
                "message": "Deploy wrapper installed successfully",
                "wrapper_path": str(self.wrapper_script),
                "alias_added": True,
                "test_result": test_result,
                "next_steps": [
                    "Restart your terminal or run 'source ~/.zshrc'",
                    "Test with: deploybot echo 'test deployment'",
                    "Use 'deploybot' prefix for all deployment commands"
                ]
            }
            
            logger.info("✅ [DEPLOY_WRAPPER] Installation completed successfully")
            return result
            
        except Exception as e:
            logger.error("❌ [DEPLOY_WRAPPER] Installation failed", error=str(e))
            return {
                "success": False,
                "message": f"Installation failed: {str(e)}",
                "error": str(e)
            }

    async def create_wrapper_script(self):
        """Create the deploy wrapper script with per-project logging"""
        logger.info("📝 [DEPLOY_WRAPPER] Creating wrapper script...")
        
        wrapper_content = '''#!/usr/bin/env python3
"""
DeployBot Deploy Wrapper Script

This script acts as a proxy for deployment commands, logging them for
DeployBot to detect while passing commands through unchanged.
"""

import sys
import subprocess
import time
import os
from pathlib import Path

def get_deploy_log_path():
    """Determine the appropriate deploy log path based on project context"""
    cwd = Path.cwd()
    
    # Look for DeployBot project structure in current directory and parent directories
    potential_project_dirs = [
        cwd,
        cwd.parent,
        cwd.parent.parent
    ]
    
    for proj_dir in potential_project_dirs:
        config_file = proj_dir / "config.json"
        todo_file = proj_dir / "TODO.md"
        
        # Check if this looks like a DeployBot project
        if config_file.exists() and todo_file.exists():
            # Ensure logs directory exists
            logs_dir = proj_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            deploy_log = logs_dir / "deploy_log.txt"
            print(f"📁 [DEPLOY_WRAPPER] Using project-specific log: {deploy_log}", file=sys.stderr)
            return deploy_log
    
    # Fallback to global log if no project detected
    global_log_dir = Path.home() / ".deploybot"
    global_log_dir.mkdir(exist_ok=True)
    global_log = global_log_dir / "deploy_log.txt"
    
    print(f"🌐 [DEPLOY_WRAPPER] Using global log: {global_log}", file=sys.stderr)
    return global_log

def main():
    """Main wrapper function that logs and executes deployment commands"""
    args = sys.argv[1:]
    
    if not args:
        print("❌ [DEPLOY_WRAPPER] No command provided", file=sys.stderr)
        sys.exit(1)
    
    timestamp = time.time()
    command_string = " ".join(args)
    cwd = os.getcwd()
    
    # Get the appropriate log file
    deploy_log = get_deploy_log_path()
    
    try:
        # Log the deployment command
        with open(deploy_log, "a") as f:
            f.write(f"{timestamp} DEPLOY: {command_string} [CWD: {cwd}]\\n")
        
        print(f"📝 [DEPLOY_WRAPPER] Logged deployment: {command_string}", file=sys.stderr)
        
    except Exception as e:
        print(f"⚠️ [DEPLOY_WRAPPER] Failed to log deployment: {e}", file=sys.stderr)
        # Continue with execution even if logging fails
    
    try:
        # Execute the original command unchanged
        print(f"🚀 [DEPLOY_WRAPPER] Executing: {command_string}", file=sys.stderr)
        result = subprocess.run(args)
        
        # Log completion
        try:
            with open(deploy_log, "a") as f:
                f.write(f"{time.time()} DEPLOY_COMPLETE: {command_string} [EXIT_CODE: {result.returncode}]\\n")
        except Exception as e:
            print(f"⚠️ [DEPLOY_WRAPPER] Failed to log completion: {e}", file=sys.stderr)
        
        sys.exit(result.returncode)
        
    except KeyboardInterrupt:
        print("\\n🛑 [DEPLOY_WRAPPER] Deployment interrupted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ [DEPLOY_WRAPPER] Error executing command: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        # Write the wrapper script
        self.wrapper_script.write_text(wrapper_content)
        logger.info("✅ [DEPLOY_WRAPPER] Wrapper script created", 
                   path=str(self.wrapper_script))

    async def add_shell_alias(self):
        """Add the deploybot alias to the appropriate shell config file"""
        logger.info("🔗 [DEPLOY_WRAPPER] Adding shell alias...")
        
        shell = self.detect_shell()
        
        # Determine the correct config file
        if shell == "zsh":
            config_file = Path.home() / ".zshrc"
        elif shell in ["bash", "sh"]:
            # Try .bashrc first, then .bash_profile
            config_file = Path.home() / ".bashrc"
            if not config_file.exists():
                config_file = Path.home() / ".bash_profile"
        else:
            # Default to .bashrc
            config_file = Path.home() / ".bashrc"
        
        alias_line = f'alias deploybot="python3 {self.wrapper_script}"'
        
        # Check if alias already exists
        if config_file.exists():
            content = config_file.read_text()
            if 'alias deploybot=' in content:
                logger.info("✅ [DEPLOY_WRAPPER] Alias already exists")
                return
        
        # Add the alias
        with open(config_file, "a") as f:
            f.write(f"\n# DeployBot deployment wrapper alias\n")
            f.write(f"{alias_line}\n")
        
        logger.info("✅ [DEPLOY_WRAPPER] Alias added to config file", 
                   config_file=str(config_file))

    async def test_installation(self) -> Dict[str, Any]:
        """Test the deploy wrapper installation"""
        logger.info("🧪 [DEPLOY_WRAPPER] Testing installation...")
        
        try:
            # Test that the script is executable
            result = subprocess.run([
                'python3', str(self.wrapper_script), 'echo', 'test'
            ], capture_output=True, text=True, timeout=10)
            
            success = result.returncode == 0
            
            test_result = {
                "success": success,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if success:
                logger.info("✅ [DEPLOY_WRAPPER] Installation test passed")
            else:
                logger.warning("⚠️ [DEPLOY_WRAPPER] Installation test failed", 
                             result=test_result)
            
            return test_result
            
        except Exception as e:
            logger.error("❌ [DEPLOY_WRAPPER] Test execution failed", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }

    async def uninstall_wrapper(self) -> Dict[str, Any]:
        """Uninstall the deploy wrapper and clean up"""
        logger.info("🗑️ [DEPLOY_WRAPPER] Starting uninstallation...")
        
        try:
            removed_items = []
            
            # Remove wrapper script
            if self.wrapper_script.exists():
                self.wrapper_script.unlink()
                removed_items.append(str(self.wrapper_script))
                logger.info("🗑️ [DEPLOY_WRAPPER] Removed wrapper script")
            
            # Remove alias from shell configs (leaving comments)
            for config_file in self.shell_config_files:
                if config_file.exists():
                    try:
                        content = config_file.read_text()
                        if 'alias deploybot=' in content:
                            # Remove the alias line but keep comments
                            lines = content.split('\n')
                            filtered_lines = [line for line in lines 
                                           if not line.strip().startswith('alias deploybot=')]
                            config_file.write_text('\n'.join(filtered_lines))
                            removed_items.append(f"alias from {config_file}")
                            logger.info("🗑️ [DEPLOY_WRAPPER] Removed alias", 
                                       config_file=str(config_file))
                    except Exception as e:
                        logger.warning("⚠️ [DEPLOY_WRAPPER] Error cleaning config", 
                                     config_file=str(config_file), error=str(e))
            
            return {
                "success": True,
                "message": "Deploy wrapper uninstalled successfully",
                "removed_items": removed_items
            }
            
        except Exception as e:
            logger.error("❌ [DEPLOY_WRAPPER] Uninstallation failed", error=str(e))
            return {
                "success": False,
                "message": f"Uninstallation failed: {str(e)}",
                "error": str(e)
            }

# Global instance
deploy_wrapper_manager = DeployWrapperManager() 