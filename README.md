# AI CLI Assistant

An AI-powered command-line assistant that brings LLM capabilities to your terminal, similar to Google Gemini. Features enhanced visual display, environment-based configuration, and safe mode protection.

## ✨ Features

- 🤖 **Interactive Chat Mode** - Beautiful conversational interface with thought/response separation
- 📁 **File Analysis** - Analyze and understand code/text files with syntax highlighting
- ✏️ **File Editing** - AI-assisted file modifications with automatic backups
- 🖥️ **System Assistant** - Get Ubuntu/Linux system help with executable commands
- 🔧 **Command Execution** - Safely execute suggested system commands with confirmation
- 🛡️ **Safe Mode** - Configurable backup system to protect your files
- 🎨 **Enhanced Display** - Rich terminal interface with colors, borders, and visual separators
- ⚙️ **Environment Configuration** - Flexible configuration via `.env` files

## 🏗️ Project Structure

```
ai-cli/
├── main.py                 # Entry point
├── setup.py               # Package setup
├── requirements.txt        # Dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore rules
├── README.md              # This file
└── ai_cli/                # Main package
    ├── __init__.py        # Package initialization
    ├── config.py          # Environment-based configuration
    ├── models.py          # Ollama model management
    ├── files.py           # File handling operations
    ├── commands.py        # System command execution
    ├── assistant.py       # Main AI assistant logic
    └── animations.py      # Loading animations and progress indicators
```

## Installation

> 📖 **For detailed installation instructions, PATH setup, and startup configuration, see [INSTALLATION.md](docs/INSTALLATION.md)**

### Quick Start

For a quick automated installation:

```bash
# Run the installation script
./install.sh
```

### Virtual Environment Setup (Recommended)

It's recommended to use a virtual environment to avoid conflicts with system packages:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### Configuration

The application uses environment variables for configuration. Copy `.env.example` to `.env` and modify as needed:

```bash
# Copy the example configuration
cp .env.example .env

# Edit the configuration
nano .env
```

#### Key Configuration Options:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DEFAULT_MODEL` | Set default model (empty for interactive) | `""` | `llama3.2` |
| `SAFE_MODE` | Enable/disable safe mode | `true` | `true`/`false` |
| `CREATE_BACKUPS` | Create backups when editing files | `true` | `true`/`false` |
| `MAX_PREVIEW_SIZE` | Maximum file size for preview | `2000` | `5000` |
| `COMMAND_TIMEOUT` | Timeout for command execution (seconds) | `30` | `60` |
| `DEFAULT_THEME` | Syntax highlighting theme | `monokai` | `github` |
| `SPINNER_STYLE` | Loading animation style | `dots` | `bounce` |
| `ANIMATION_SPEED` | Animation speed (seconds) | `0.1` | `0.2` |

#### 🛡️ Safe Mode

The application includes a comprehensive safe mode system:

- **`SAFE_MODE=true`**: Enables safe mode (recommended)
- **`CREATE_BACKUPS=true`**: Creates backup files before editing (recommended)
- **`SAFE_MODE=false`**: Disables safe mode (use with caution)

When safe mode is disabled, the application will not create backup files before editing, which means changes are permanent and cannot be easily undone.

#### 🎨 Enhanced Display

The application features a rich terminal interface with:

- **Visual separators** between AI thoughts and responses
- **Color-coded status indicators** for different operations
- **Bordered headers** for major sections
- **Enhanced emojis** and icons throughout
- **Automatic thought detection** for models like DeepSeek

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/ai-cli.git
cd ai-cli

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Deactivating Virtual Environment

When you're done working with the project:

```bash
# Deactivate the virtual environment
deactivate
```

### Dependencies

- Python 3.8+
- Ollama (running locally)
- Required Python packages:
  - `rich` - Beautiful terminal formatting
  - `ollama` - Ollama Python client

## 🚀 Usage

### Basic Commands

```bash
# Start interactive chat (default)
python main.py

# Or after installation
ai-cli

# Specify a model
ai-cli --model llama3.2

# Analyze a file
ai-cli --read script.py

# Edit a file with AI assistance
ai-cli --edit config.json --instruction "add debug settings"

# Get system help
ai-cli --system "how to install docker"
```

### Command Line Options

| Option | Short | Description | Example |
|--------|-------|-------------|---------|
| `--model` | `-m` | Specify which Ollama model to use | `--model llama3.2` |
| `--read` | `-r` | Read and analyze a file | `--read script.py` |
| `--edit` | `-e` | Edit a file with AI assistance | `--edit config.json` |
| `--prompt` | `-p` | Custom prompt for file analysis | `--prompt "find bugs"` |
| `--instruction` | `-i` | Instruction for file editing | `--instruction "add comments"` |
| `--system` | `-s` | Ask about system/Ubuntu | `--system "install docker"` |
| `--chat` | `-c` | Start interactive chat (default) | `--chat` |

## Module Descriptions

### `main.py`
Entry point that handles argument parsing and initializes the assistant.

### `ai_cli/assistant.py`
Core assistant class that orchestrates all functionality:
- Chat mode management
- File operations coordination
- System assistance
- Response streaming

### `ai_cli/models.py`
Manages Ollama model operations:
- Lists available models
- Interactive model selection
- Model validation

### `ai_cli/files.py`
Handles all file-related operations:
- Safe file reading with encoding detection
- Syntax-highlighted previews
- Automatic backup creation
- AI response cleaning

### `ai_cli/commands.py`
System command execution with safety:
- Command parsing from AI responses
- Safe execution with timeout
- User confirmation workflows
- Sudo detection and warnings

### `ai_cli/config.py`
Centralized configuration:
- Display settings
- Timeout values
- File size limits
- Default models

## 🔧 Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/

# Run with coverage
pytest --cov=ai_cli tests/
```

### Adding New Features

1. Create new module in `ai_cli/` if needed
2. Import in `__init__.py` if it's a public API
3. Update `assistant.py` to integrate the feature
4. Add command line option in `main.py`
5. Update configuration in `config.py`
6. Add tests for new functionality

### Code Style

- Use type hints for all functions
- Follow PEP 8 guidelines
- Add docstrings to all classes and methods
- Keep modules focused on single responsibilities
- Use environment variables for configuration
- Add proper error handling and user feedback

## 🐛 Troubleshooting

### Common Issues

**Q: No models found error**
```bash
# Install Ollama and pull a model
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2
```

**Q: Permission denied when editing files**
```bash
# Check file permissions
ls -la filename
# Make sure you have write access
chmod 644 filename
```

**Q: Colors not displaying properly**
```bash
# Check terminal color support
echo $TERM
# Try setting TERM=xterm-256color
export TERM=xterm-256color
```

**Q: Safe mode not working**
```bash
# Check your .env file
cat .env
# Ensure SAFE_MODE=true and CREATE_BACKUPS=true
```

### Getting Help

- Check the [Issues](https://github.com/yourusername/ai-cli/issues) page
- Review the configuration options above
- Ensure Ollama is running: `ollama serve`
- Check model availability: `ollama list`

## 📚 Examples

### 🤖 Interactive Chat

```bash
# Start a conversation
ai-cli

# Example interaction:
👤 You: How do I optimize a Python function?
💭 Thoughts: <thinking>User wants to optimize Python code...</thinking>
─────────────────────────────────────────────────────────
🤖 Response: Here are several optimization techniques...
```

### 📁 File Analysis

```bash
# Analyze a Python script
ai-cli --read app.py --prompt "Find potential bugs and suggest improvements"

# Analyze with custom prompt
ai-cli --read config.json --prompt "Check for security issues"
```

### ✏️ File Editing

```bash
# Edit a configuration file
ai-cli --edit docker-compose.yml --instruction "add redis service on port 6379"

# Edit Python code
ai-cli --edit main.py --instruction "add error handling and logging"
```

### 🖥️ System Administration

```bash
# Get system help
ai-cli --system "set up nginx reverse proxy for port 3000"

# System diagnostics
ai-cli --system "check disk usage and clean up old files"
```

### 🎨 Enhanced Display Features

The application automatically detects and displays:

- **Thought processes** from models like DeepSeek
- **Visual separators** between different response types
- **Color-coded status** for all operations
- **Progress indicators** for long-running tasks

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## Requirements

Ensure Ollama is installed and running:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model
ollama pull llama3.2

# Start Ollama (if not already running)
ollama serve
```