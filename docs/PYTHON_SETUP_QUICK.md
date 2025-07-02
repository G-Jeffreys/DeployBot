# 🚀 Quick Python Setup for DeployBot

**DeployBot needs Python to work.** Here are the easiest ways to get it set up:

---

## 🎯 **Option 1: One-Command Install (Easiest)**

Copy and paste this into Terminal:

```bash
curl -sSL https://raw.githubusercontent.com/your-username/DeployBot/main/scripts/install_python.sh | bash
```

**That's it!** This installs everything automatically.

---

## 🎯 **Option 2: Manual Install**

If you prefer to do it step by step:

```bash
# 1. Install Python
brew install python@3.11

# 2. Install DeployBot requirements
pip3 install --user "langgraph>=0.0.55" "websockets>=12.0" "structlog>=24.1.0" "langchain-openai>=0.1.0"

# 3. Test it works
python3 -c "import langgraph; print('✅ Ready!')"
```

---

## 🎯 **Option 3: Already Have Python?**

Check if Python is ready:

```bash
python3 --version
```

If you see `Python 3.9` or higher, just install the packages:

```bash
pip3 install --user -r requirements.txt
```

---

## 🆘 **Having Problems?**

- **"Command not found"** → [Install Python first](PYTHON_INSTALLATION.md#step-2-install-python)
- **"Permission denied"** → Add `--user` flag: `pip3 install --user package_name`
- **"externally-managed-environment"** → Add `--break-system-packages`: `pip3 install --break-system-packages package_name`

📖 **Need more help?** See the [Full Python Installation Guide](PYTHON_INSTALLATION.md)

---

## ✅ **You're Done!**

Once Python is set up:
1. **Launch DeployBot** from your Applications folder
2. **Create a project** and start being productive!

🎉 **Welcome to DeployBot!** 