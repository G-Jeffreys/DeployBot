# 🚀 DeployBot Deploy Wrapper

This document explains how to set up and use the DeployBot deploy wrapper for detecting backend deployment events.

## Overview

The deploy wrapper is a Python script that acts as a proxy for your deployment commands. It logs deployment events while passing through commands unchanged, enabling DeployBot to detect when deployments occur.

## Installation

### 1. Create the Wrapper Script

Copy the deploy wrapper script to your home directory:

```bash
mkdir -p ~/.deploybot
```

Create `~/.deploybot/deploybot-wrapper.py` with the following content:

```python
#!/usr/bin/env python3
import sys
import subprocess
import time
from pathlib import Path

DEPLOY_LOG = Path.home() / ".deploybot" / "deploy_log.txt"
DEPLOY_LOG.parent.mkdir(exist_ok=True)

def main():
    args = sys.argv[1:]
    timestamp = time.time()
    command_string = " ".join(args)

    # Log the deployment command
    with open(DEPLOY_LOG, "a") as f:
        f.write(f"{timestamp} DEPLOY: {command_string}\n")

    # Execute the original command unchanged
    subprocess.run(args)

if __name__ == "__main__":
    main()
```

### 2. Make the Script Executable

```bash
chmod +x ~/.deploybot/deploybot-wrapper.py
```

### 3. Add Shell Alias

Add this alias to your shell configuration file (`~/.zshrc` for zsh or `~/.bashrc` for bash):

```bash
alias deploybot="python3 ~/.deploybot/deploybot-wrapper.py"
```

Reload your shell configuration:

```bash
source ~/.zshrc  # or source ~/.bashrc
```

## Usage

Replace your normal deployment commands with `deploybot` prefix:

### Firebase
```bash
# Instead of: firebase deploy
deploybot firebase deploy

# Instead of: firebase deploy --only functions
deploybot firebase deploy --only functions
```

### Vercel
```bash
# Instead of: vercel --prod
deploybot vercel --prod
```

### Netlify
```bash
# Instead of: netlify deploy --prod
deploybot netlify deploy --prod
```

### Custom Commands
```bash
# Any deployment command works
deploybot npm run deploy
deploybot ./deploy.sh
deploybot docker deploy
```

## How It Works

1. **Command Logging**: The wrapper logs each deployment command with a timestamp to `~/.deploybot/deploy_log.txt`
2. **Passthrough Execution**: Your original command runs exactly as it would without the wrapper
3. **DeployBot Detection**: DeployBot monitors the log file for new entries to detect deployments
4. **Timer Activation**: When a deployment is detected, DeployBot starts its productivity timer

## Log File Format

The deploy log file (`~/.deploybot/deploy_log.txt`) contains entries in this format:

```
1705315200.123 DEPLOY: firebase deploy --only functions
1705315800.456 DEPLOY: vercel --prod
1705316400.789 DEPLOY: netlify deploy --prod
```

Each line contains:
- Unix timestamp (seconds since epoch)
- "DEPLOY:" prefix
- Complete command that was executed

## Troubleshooting

### Command Not Found
If you get "deploybot: command not found":
1. Verify the script is executable: `ls -la ~/.deploybot/deploybot-wrapper.py`
2. Check the alias is loaded: `alias | grep deploybot`
3. Reload your shell: `source ~/.zshrc`

### Python Not Found
If you get "python3: command not found":
1. Install Python 3: `brew install python3` (macOS)
2. Verify installation: `python3 --version`

### Permission Denied
If you get "Permission denied":
1. Make script executable: `chmod +x ~/.deploybot/deploybot-wrapper.py`
2. Check file permissions: `ls -la ~/.deploybot/`

### DeployBot Not Detecting
If DeployBot doesn't detect your deployments:
1. Check log file exists: `ls -la ~/.deploybot/deploy_log.txt`
2. Verify commands are logged: `tail ~/.deploybot/deploy_log.txt`
3. Ensure DeployBot is running and monitoring is enabled

## Advanced Configuration

### Custom Log Location
Set a custom log file location by modifying the `DEPLOY_LOG` variable in the wrapper script:

```python
DEPLOY_LOG = Path("/custom/path/deploy_log.txt")
```

### Multiple Projects
Use different aliases for different projects:

```bash
alias deploybot-project1="python3 ~/.deploybot/project1-wrapper.py"
alias deploybot-project2="python3 ~/.deploybot/project2-wrapper.py"
```

### Integration with CI/CD
The wrapper can be used in CI/CD pipelines by calling it directly:

```yaml
# GitHub Actions example
- name: Deploy with DeployBot
  run: python3 ~/.deploybot/deploybot-wrapper.py firebase deploy
```

## Security Notes

- The wrapper only logs command names and arguments, not sensitive output
- Log files are stored locally in your home directory
- No network requests are made by the wrapper itself
- Original command security is unchanged

## Next Steps

Once the wrapper is set up:
1. Start DeployBot application
2. Enable deploy monitoring in the UI
3. Run a test deployment: `deploybot echo "test"`
4. Verify detection in DeployBot's activity log

For more information, see the main DeployBot documentation. 