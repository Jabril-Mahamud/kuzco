# AI CLI Assistant

A simple AI-powered command-line assistant that brings LLM capabilities to your terminal using Ollama. Set it up once and you have your own Gemini-like assistant based on Ollama.

## Features

- 🤖 **Interactive Chat** - Beautiful conversational interface
- 📁 **File Analysis** - Analyze and understand code/text files
- ✏️ **File Editing** - AI-assisted file modifications with backups
- 🖥️ **System Assistant** - Get Ubuntu/Linux system help
- 🛡️ **Safe Mode** - Automatic backups to protect your files

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
   python main.py
   ```

## Usage

```bash
# Interactive chat
python main.py

# Analyze a file
python main.py --read script.py

# Edit a file
python main.py --edit config.json --instruction "add debug settings"

# System help
python main.py --system "how to install docker"
```

## Configuration

Copy `.env.example` to `.env` and customize:

- `DEFAULT_MODEL` - Set default model (empty for interactive selection)
- `SAFE_MODE` - Enable safe mode (recommended: true)
- `CREATE_BACKUPS` - Create backups when editing (recommended: true)

## Requirements

- Python 3.8+
- Ollama (running locally)
- Dependencies in `requirements.txt`

That's it! Simple setup, powerful AI assistant.