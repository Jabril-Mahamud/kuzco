# AI CLI Installation & Setup Guide

This guide will help you install the AI CLI tool, add it to your system PATH, and configure it to run on startup.

## 📋 Prerequisites

Before installing, ensure you have:

- **Python 3.8+** installed
- **Ollama** installed and running locally
- **Git** (for cloning the repository)

### Install Ollama (if not already installed)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (e.g., llama3.2)
ollama pull llama3.2

# Start Ollama service (if not already running)
ollama serve
```

## 🚀 Installation Methods

### Method 1: Development Installation (Recommended)

This method allows you to edit the code and have changes reflected immediately.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install in development mode
pip install -e .

# 4. Copy configuration
cp .env.example .env
```

### Method 2: System-wide Installation

This method installs the tool system-wide and makes it available from anywhere.

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# 2. Install system-wide
pip install .

# 3. Copy configuration to user directory
cp .env.example ~/.ai-cli.env
```

## 🔧 Adding to PATH

### Option 1: Using pip install (Automatic)

If you used `pip install .` or `pip install -e .`, the `ai-cli` command should already be available in your PATH through the console script entry point defined in `setup.py`.

Test it:
```bash
ai-cli --help
```

### Option 2: Manual PATH Addition

If the automatic method doesn't work, you can manually add the tool to your PATH.

#### For Linux/macOS:

1. **Find your Python scripts directory:**
```bash
python -c "import site; print(site.USER_BASE + '/bin')"
```

2. **Add to your shell profile:**
```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

3. **Create a symbolic link (alternative):**
```bash
# Create symlink in a directory that's already in PATH
sudo ln -s /path/to/your/ai-cli/main.py /usr/local/bin/ai-cli
```

#### For Windows:

1. **Find your Python scripts directory:**
```cmd
python -c "import site; print(site.USER_BASE + '/Scripts')"
```

2. **Add to PATH through System Properties:**
   - Open "System Properties" → "Environment Variables"
   - Add the Python Scripts directory to your PATH
   - Or add to your PowerShell profile:
```powershell
$env:PATH += ";C:\Users\YourUsername\AppData\Roaming\Python\Python3x\Scripts"
```

### Option 3: Create a Wrapper Script

Create a simple wrapper script that activates your virtual environment and runs the tool:

```bash
# Create wrapper script
cat > ~/bin/ai-cli << 'EOF'
#!/bin/bash
cd /home/dev/Documents/GitHub/python/ai-cli
source venv/bin/activate
python main.py "$@"
EOF

# Make it executable
chmod +x ~/bin/ai-cli

# Add ~/bin to PATH (if not already there)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## ⚙️ Configuration

### Environment Setup

1. **Copy the example configuration:**
```bash
cp .env.example .env
```

2. **Edit the configuration:**
```bash
nano .env
```

### Key Configuration Options

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEFAULT_MODEL` | Set default model | `""` | `llama3.2` |
| `SAFE_MODE` | Enable safe mode | `true` | `true`/`false` |
| `CREATE_BACKUPS` | Create backups when editing | `true` | `true`/`false` |
| `MAX_PREVIEW_SIZE` | Max file size for preview | `2000` | `5000` |
| `COMMAND_TIMEOUT` | Command execution timeout | `30` | `60` |

## 🚀 Startup Configuration

### Option 1: Shell Alias (Recommended for Development)

Add to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# Add to ~/.bashrc or ~/.zshrc
alias ai-cli='cd /home/dev/Documents/GitHub/python/ai-cli && source venv/bin/activate && python main.py'
```

Then reload your shell:
```bash
source ~/.bashrc  # or source ~/.zshrc
```

### Option 2: System Service (Advanced)

Create a systemd service to run Ollama automatically:

```bash
# Create service file
sudo nano /etc/systemd/system/ollama.service
```

Add this content:
```ini
[Unit]
Description=Ollama Service
After=network.target

[Service]
Type=simple
User=ollama
Group=ollama
ExecStart=/usr/local/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl enable ollama
sudo systemctl start ollama
```

### Option 3: Desktop Entry (GUI)

Create a desktop entry for easy access:

```bash
# Create desktop entry
cat > ~/.local/share/applications/ai-cli.desktop << 'EOF'
[Desktop Entry]
Name=AI CLI Assistant
Comment=AI Assistant CLI - Like Google Gemini for your terminal
Exec=gnome-terminal -- bash -c "cd /home/dev/Documents/GitHub/python/ai-cli && source venv/bin/activate && python main.py; exec bash"
Icon=terminal
Type=Application
Categories=Development;Utility;
Terminal=true
EOF
```

## 🧪 Testing Your Installation

### 1. Test Basic Functionality

```bash
# Test if the command is available
ai-cli --help

# Test interactive mode
ai-cli

# Test file analysis
ai-cli --read README.md

# Test system assistance
ai-cli --system "list running processes"
```

### 2. Test Model Connection

```bash
# Check if Ollama is running
ollama list

# Test with a specific model
ai-cli --model llama3.2 --system "hello"
```

### 3. Test File Operations

```bash
# Create a test file
echo "print('Hello, World!')" > test.py

# Analyze the file
ai-cli --read test.py

# Edit the file
ai-cli --edit test.py --instruction "add a comment"
```

## 🔧 Troubleshooting

### Common Issues

**Issue: `ai-cli: command not found`**
```bash
# Check if the command is in PATH
which ai-cli
echo $PATH

# Reinstall with pip
pip install -e .
```

**Issue: `ModuleNotFoundError`**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**Issue: `Connection refused` (Ollama)**
```bash
# Check if Ollama is running
ollama serve

# Check if models are available
ollama list
```

**Issue: Permission denied**
```bash
# Check file permissions
ls -la main.py
chmod +x main.py
```

### Debug Mode

Run with verbose output to debug issues:

```bash
# Run with Python debug
python -u main.py --help

# Check Python path
python -c "import sys; print(sys.path)"
```

## 📝 Usage Examples

Once installed, you can use the AI CLI from anywhere:

```bash
# Interactive chat
ai-cli

# Analyze a file
ai-cli --read /path/to/file.py

# Edit a file
ai-cli --edit /path/to/file.py --instruction "add error handling"

# System help
ai-cli --system "how to install docker"

# Use specific model
ai-cli --model llama3.2 --system "explain quantum computing"
```

## 🔄 Updating

To update your installation:

```bash
# Navigate to the project directory
cd /home/dev/Documents/GitHub/python/ai-cli

# Pull latest changes
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Reinstall if needed
pip install -e .
```

## 🗑️ Uninstalling

To remove the AI CLI:

```bash
# Remove from pip
pip uninstall ai-cli-assistant

# Remove virtual environment
rm -rf venv

# Remove project directory
rm -rf /home/dev/Documents/GitHub/python/ai-cli

# Remove from PATH (if manually added)
# Edit ~/.bashrc and remove the export PATH line
```

## 📚 Additional Resources

- [Main README](../README.md) - Complete feature documentation
- [API Documentation](API.md) - Technical API reference
- [Examples](../examples/) - Usage examples and tutorials
- [Changelog](../CHANGELOG.md) - Version history and updates

## 🆘 Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#-troubleshooting) above
2. Review your configuration in `.env`
3. Ensure Ollama is running: `ollama serve`
4. Check model availability: `ollama list`
5. Open an issue on GitHub with your error details

---

**Happy coding with AI CLI! 🤖✨**
