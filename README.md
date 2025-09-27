# Kuzco - AI CLI Assistant

A simple AI-powered command-line assistant that brings LLM capabilities to your terminal using Ollama. Set it up once and you have your own Gemini-like assistant based on Ollama. In my experience, **gpt-oss** performs best for editing; other models tend to add a lot of junk.

## 🏗️ Architecture

The project is organized into clean, focused modules:

- **`assistant.py`** - Main coordinator class that orchestrates all operations
- **`system.py`** - System assistance and command execution functionality
- **`file_handler.py`** - File operations and content processing
- **`chat.py`** - Interactive chat and conversation management
- **`config.py`** - Configuration and settings management
- **`errors.py`** - Error handling and validation utilities
- **`models.py`** - Model management and selection
- **`animations.py`** - Loading animations and visual feedback
- **`parser.py`** - Response parsing and content extraction utilities

## Features

- 🤖 **Interactive Chat** - Beautiful conversational interface with special commands
- 📁 **File Analysis** - Analyze and understand code/text files with AI insights
- ✏️ **File Editing** - AI-assisted file modifications with intelligent content cleaning
- 🦙 **LLM Models** - Prefer **gpt-oss** for editing; other models may produce excessive noise
- 🖥️ **System Assistant** - Get Ubuntu/Linux system help and execute commands safely
- 🛡️ **Safe Mode** - Automatic backups and command validation to protect your files
- 🔍 **Smart File Matching** - Case-insensitive file discovery
- 🧹 **Content Cleaning** - Advanced AI response cleaning to remove artifacts and thoughts
- ⚡ **Command Execution** - Safe system command execution with user confirmation

## Quick Setup

1. **Install Ollama** (if not already installed):
      curl -fsSL https://ollama.com/install.sh | sh
   ollama pull llama3.2
   # For best editing experience, consider pulling gpt-oss: ollama pull gpt-oss


2. **Install dependencies**:
      pip install -r requirements.txt


3. **Configure** (optional):
      cp .env.example .env
   # Edit .env to customize settings


4. **Run**:
      kuzco


## Usage

### Command Line
# Interactive chat
kuzco

# Analyze a file
kuzco --read script.py

# Edit a file
kuzco --edit config.json --instruction "add debug settings"
# Note: Using gpt-oss improves editing quality

# System help
kuzco --system "how to install docker"

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
- `COMMAND_TIMEOUT` - Timeout for command execution (default: 30s)
- `SUDO_PREFIXES` - Commands that require sudo warnings (default: sudo,su)
- `EXIT_COMMANDS` - Commands to exit chat mode (default: exit,quit,bye,goodbye)

## Requirements

- Python 3.8+
- Ollama (running locally)
- Dependencies in `requirements.txt`

## Global Installation

The app is set up as `kuzco` command globally. Use `kuzco` from anywhere in your terminal.

## Recent Improvements

- 🏗️ **Modular Architecture** - Clean separation of concerns with focused modules
- 🧹 **Advanced Content Cleaning** - Intelligent removal of AI artifacts and thoughts
- ⚡ **Safe Command Execution** - Built-in safety checks and user confirmation for system commands
- 🔧 **Better Error Handling** - Comprehensive error management and validation
- 📦 **Consolidated Codebase** - Eliminated overlapping files and confusing structure

That's it! Simple setup, powerful AI assistant.