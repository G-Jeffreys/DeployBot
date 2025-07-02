# 🐍 Python Installation Guide for DeployBot

DeployBot requires Python 3.9+ to run its intelligent backend. This guide will help you install Python and get DeployBot working on your system.

---

## 🔍 **Step 1: Check if Python is Already Installed**

Open Terminal and run:
```bash
python3 --version
```

**If you see something like `Python 3.9.0` or higher:** ✅ You're good to go! Skip to [Step 3](#step-3-install-dependencies).

**If you see `command not found`:** Continue to Step 2.

---

## 🏗️ **Step 2: Install Python**

### **Option A: Automated Installation (Easiest)**

Run our automated installer that handles everything:
```bash
curl -sSL https://raw.githubusercontent.com/your-username/DeployBot/main/scripts/install_python.sh | bash
```

This script will:
- ✅ Check if Python is already installed
- ✅ Install Homebrew (if needed)
- ✅ Install Python 3.11
- ✅ Install all DeployBot dependencies
- ✅ Verify everything works

**If the automated script works, skip to [Step 5](#step-5-launch-deploybot)!**

### **Option B: Using Homebrew (Manual)**

1. **Install Homebrew** (if you don't have it):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**:
   ```bash
   brew install python@3.11
   ```

3. **Verify installation**:
   ```bash
   python3 --version
   pip3 --version
   ```



### **Option C: Official Python Installer**

1. **Download Python** from [python.org](https://www.python.org/downloads/)
2. **Run the installer** and check "Add Python to PATH"
3. **Verify in Terminal**:
   ```bash
   python3 --version
   ```

### **Option D: Using pyenv (Advanced Users)**

```bash
# Install pyenv
brew install pyenv

# Install Python 3.11
pyenv install 3.11.0
pyenv global 3.11.0

# Add to your shell profile
echo 'export PATH="$HOME/.pyenv/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc
```

---

## 📦 **Step 3: Install Dependencies**

DeployBot needs specific Python packages to function. Here's how to install them:

### **Quick Installation**

```bash
# If you have the source code (developers):
cd /path/to/DeployBot
pip3 install -r requirements.txt

# If you installed DeployBot from DMG:
# Download requirements.txt from: https://github.com/your-username/DeployBot/raw/main/requirements.txt
# Then run: pip3 install -r requirements.txt
```

### **Manual Installation (if you don't have requirements.txt)**

```bash
pip3 install \
    "langgraph>=0.0.55" \
    "langchain>=0.1.0" \
    "langchain-openai>=0.1.0" \
    "websockets>=12.0" \
    "structlog>=24.1.0" \
    "python-dotenv>=1.0.1" \
    "watchdog>=4.0.0" \
    "asyncio-mqtt>=0.16.1" \
    "colorama>=0.4.6"
```

### **Using Virtual Environment (Recommended)**

```bash
# Create a virtual environment for DeployBot
python3 -m venv deploybot-env

# Activate it
source deploybot-env/bin/activate

# Install packages
pip install -r requirements.txt

# To deactivate later
deactivate
```

---

## ✅ **Step 4: Verify Installation**

Test that everything works:

```bash
# Test Python import
python3 -c "
import langgraph
import websockets
import structlog
print('✅ All DeployBot dependencies installed successfully!')
"
```

**Expected output:** `✅ All DeployBot dependencies installed successfully!`

---

## 🚀 **Step 5: Launch DeployBot**

Now you can run DeployBot:

1. **Open the DeployBot app** (from Applications or the DMG)
2. **Check the app logs** to see if Python backend starts successfully
3. **Look for messages like:**
   ```
   🐍 [MAIN] Starting Python backend...
   🐍 [MAIN] Python process started with PID: 12345
   ✅ [MAIN] WebSocket connection established
   ```

---

## 🐛 **Troubleshooting**

### **"Command not found: python3"**
- Make sure Python is in your PATH
- Try `python` instead of `python3`
- Restart Terminal after installation

### **"No module named 'langgraph'"**
```bash
# Make sure you're using the right pip
which pip3
pip3 install langgraph

# Or try
python3 -m pip install langgraph
```

### **"Permission denied" or "externally-managed-environment" errors**
Modern Python installations protect system packages. Use these solutions:

```bash
# Option 1: Install for current user only (recommended)
pip3 install --user -r requirements.txt

# Option 2: Override system protection (use carefully)
pip3 install --break-system-packages -r requirements.txt

# Option 3: Use virtual environment (safest)
python3 -m venv deploybot-venv
source deploybot-venv/bin/activate
pip install -r requirements.txt
```

### **Multiple Python versions causing issues**
```bash
# See all Python installations
ls -la /usr/bin/python*
ls -la /usr/local/bin/python*

# Use specific version
/usr/local/bin/python3.11 -m pip install langgraph
```

### **DeployBot can't find Python**
The app looks for Python in these locations:
1. `/usr/local/bin/python3`
2. `/usr/bin/python3` 
3. `python3` in PATH

You can create a symlink if needed:
```bash
# Find your Python
which python3

# Create symlink (replace with your Python path)
sudo ln -sf /opt/homebrew/bin/python3 /usr/local/bin/python3
```

---

## 📋 **Quick Reference**

### **Minimum Requirements**
- **Python:** 3.9 or higher
- **pip:** Latest version
- **macOS:** 10.15+ (Catalina)

### **Required Packages**
- `langgraph` - AI workflow engine
- `websockets` - Real-time communication
- `structlog` - Structured logging
- `openai` - AI model integration
- `watchdog` - File monitoring

### **Installation Commands**
```bash
# Check Python
python3 --version

# Install Homebrew + Python
brew install python@3.11

# Install dependencies (using --user to avoid conflicts)
pip3 install --user "langgraph>=0.0.55" "websockets>=12.0" "structlog>=24.1.0" "langchain-openai>=0.1.0"

# Test installation
python3 -c "import langgraph; print('✅ Ready!')"
```

---

## 🆘 **Still Having Issues?**

1. **Check Python Path:**
   ```bash
   echo $PATH
   which python3
   ```

2. **Reinstall Python:**
   ```bash
   brew uninstall python@3.11
   brew install python@3.11
   ```

3. **Clear pip cache:**
   ```bash
   pip3 cache purge
   ```

4. **Use Python directly:**
   ```bash
   /usr/local/bin/python3 -m pip install langgraph
   ```

5. **Contact Support:**
   - Include output of `python3 --version`
   - Include output of `pip3 list`
   - Include any error messages from DeployBot

---

## 🎯 **Next Steps**

Once Python is installed:
1. ✅ **Launch DeployBot**
2. ✅ **Create your first project**
3. ✅ **Set up deploy wrapper**: [Deploy Wrapper Guide](DEPLOY_WRAPPER.md)
4. ✅ **Add tasks to TODO.md**
5. ✅ **Test deploy detection**

**Welcome to DeployBot! 🚀** 