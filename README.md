# Kuzco - AI CLI Assistant

A simple AI-powered command-line assistant that brings LLM capabilities to your terminal using Ollama. Set it up once and you have your own Gemini-like assistant based on Ollama.

## Features

- 🤖 **Interactive Chat** - Beautiful conversational interface with special commands
- 📁 **File Analysis** - Analyze and understand code/text files
- ✏️ **File Editing** - AI-assisted file modifications with backups
- 🖥️ **System Assistant** - Get Ubuntu/Linux system help
- 🛡️ **Safe Mode** - Automatic backups to protect your files
- 🔍 **Smart File Matching** - Case-insensitive file discovery

## Quick Setup

1. **Install Ollama** (if not already installed):
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure** (optional):
   ```bash
   cp .env.example .env
   # Edit .env to customize settings
   ```

4. **Run**:
   ```bash
   kuzco
   ```

## Usage

### Command Line
```bash
# Interactive chat
kuzco

# Analyze a file
kuzco --read script.py

# Edit a file
kuzco --edit config.json --instruction "add debug settings"

# System help
kuzco --system "how to install docker"
```

### Special Chat Commands
Once in chat mode, use these commands:
- `/read <file> [prompt]` - Analyze a file
- `/edit <file> <instruction>` - Edit a file
- `/system <question>` - Ask system questions
- `/help` - Show all commands
- `/clear` - Clear conversation history

## Configuration

Copy `.env.example` to `.env` and customize:

- `DEFAULT_MODEL` - Set default model (empty for interactive selection)
- `SAFE_MODE` - Enable safe mode (recommended: true)
- `CREATE_BACKUPS` - Create backups when editing (recommended: true)

## Requirements

- Python 3.8+
- Ollama (running locally)
- Dependencies in `requirements.txt`

## Global Installation

The app is set up as `kuzco` command globally. Use `kuzco` from anywhere in your terminal.

That's it! Simple setup, powerful AI assistant.