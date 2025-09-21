# 🤖 AI CLI Assistant

A powerful command-line AI assistant that brings Google Gemini-like capabilities to your terminal using Ollama. Built for developers who want to integrate AI seamlessly into their workflow.

## 🐧 Born from Ubuntu Learning

This project was created by someone new to Ubuntu who wanted an AI assistant to help navigate file paths, understand system commands, and learn Linux workflows. If you're also transitioning to Ubuntu or learning Linux, this tool can be your friendly guide for:

- 📁 Understanding file system navigation
- 🛠️ Learning Ubuntu commands and best practices
- 📂 Managing files and directories with AI assistance
- 🚀 Getting comfortable with terminal workflows

*Perfect for Ubuntu newcomers who want AI help while they learn!*

## ✨ Features

- 🗣️ **Interactive Chat Mode** - Natural conversation with your local AI models
- 📁 **File Analysis** - Read and analyze any text file with AI insights
- ✏️ **AI-Powered Editing** - Modify files using natural language instructions
- 🖥️ **System Help** - Get Ubuntu/Linux system administration assistance
- 🎨 **Rich Terminal UI** - Beautiful syntax highlighting and formatting
- 🔄 **Model Selection** - Choose from your installed Ollama models
- 💾 **Automatic Backups** - Never lose your original files during edits

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai) installed and running
- At least one Ollama model downloaded

### Installation

1. **Clone or download the project**
   ```bash
   git clone <your-repo-url>
   cd ai-cli
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install ollama rich
   ```

4. **Make executable**
   ```bash
   chmod +x ai_cli.py
   ```

5. **Test installation**
   ```bash
   ./ai_cli.py --help
   ```

### Optional: Global Installation

Make the tool available system-wide:

```bash
sudo ln -s $(pwd)/ai_cli.py /usr/local/bin/ai-cli
# Now use: ai-cli instead of ./ai_cli.py
```

## 📖 Usage

### Interactive Chat Mode (Default)

Start a conversation with your AI assistant:

```bash
./ai_cli.py
# or specify a model
./ai_cli.py --model deepseek-r1:latest
```

### File Analysis

Analyze any text file:

```bash
# Basic analysis
./ai_cli.py --read config.py

# Custom analysis prompt
./ai_cli.py --read script.js --prompt "find potential security vulnerabilities"

# Analyze configuration files
./ai_cli.py --read nginx.conf --prompt "optimize this configuration"
```

### AI-Powered File Editing

Edit files using natural language:

```bash
# Interactive mode (prompts for instruction)
./ai_cli.py --edit main.py

# Direct instruction
./ai_cli.py --edit README.md --instruction "add installation section"

# Code improvements
./ai_cli.py --edit script.py --instruction "add error handling and type hints"
```

**⚠️ Safety Note:** Original files are automatically backed up with `backup_` before editing.

### System Administration Help

Get Ubuntu/Linux assistance:

```bash
./ai_cli.py --system "how to set up nginx with SSL"
./ai_cli.py --system "optimize Ubuntu for development"
./ai_cli.py --system "troubleshoot high memory usage"
```

## 🔧 Command Reference

```bash
./ai_cli.py [options]

Options:
  -h, --help              Show help message
  -m, --model MODEL       Specify Ollama model to use
  -r, --read FILE         Read and analyze a file
  -p, --prompt PROMPT     Custom prompt for file analysis
  -e, --edit FILE         Edit a file with AI assistance
  -i, --instruction TEXT  Instruction for file editing
  -s, --system QUESTION   Ask about system/Ubuntu topics
  -c, --chat              Start interactive chat (default)
```

## 💡 Examples

### Development Workflow

```bash
# Code review
./ai_cli.py --read src/main.py --prompt "review for bugs and improvements"

# Refactor legacy code
./ai_cli.py --edit old_script.py --instruction "modernize using Python 3.11 features"

# Generate documentation
./ai_cli.py --read api.py --prompt "create API documentation"
```

### System Administration

```bash
# Log analysis
./ai_cli.py --read /var/log/nginx/error.log --prompt "summarize recent errors"

# Configuration help
./ai_cli.py --system "secure SSH configuration best practices"

# Performance tuning
./ai_cli.py --system "optimize PostgreSQL for high traffic"
```

### Content Creation

```bash
# Improve documentation
./ai_cli.py --edit README.md --instruction "make more professional and comprehensive"

# Code comments
./ai_cli.py --edit functions.py --instruction "add detailed docstrings"
```

## 🛠️ Supported Models

The tool works with any Ollama model you have installed:

```bash
# Popular options
ollama pull llama3.2
ollama pull deepseek-r1
ollama pull codellama
ollama pull mistral
```

Check available models:
```bash
ollama list
```

## 🎨 Features in Detail

### Rich Terminal Interface
- Syntax highlighting for code files
- Progress indicators for long operations
- Colored output for better readability
- File previews for small files

### Smart File Handling
- Automatic file type detection
- Support for most text formats (Python, JavaScript, JSON, YAML, etc.)
- Intelligent content analysis
- Backup creation before edits

### Model Management
- Automatic model detection
- Interactive model selection
- Per-session model persistence
- Support for all Ollama models

## 🐛 Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve
```

### Python Dependencies
```bash
# Reinstall dependencies
pip install --upgrade ollama rich
```

### File Permissions
```bash
# Make script executable
chmod +x ai_cli.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for the amazing local AI platform
- [Rich](https://github.com/Textualize/rich) for beautiful terminal formatting
- The open-source AI community

---

**Made with ❤️ for developers who love AI and terminal workflows**

*For more advanced features and integrations, check out the examples directory.*