# AI CLI Assistant API Documentation

## Overview

The AI CLI Assistant provides a comprehensive API for interacting with AI models through a command-line interface. This document describes the main components and their APIs.

## Core Components

### AIAssistant Class

The main class that orchestrates all AI CLI functionality.

```python
from ai_cli.assistant import AIAssistant

# Initialize with default model
assistant = AIAssistant()

# Initialize with specific model
assistant = AIAssistant("llama3.2")
```

#### Methods

##### `chat_mode()`
Start an interactive chat session.

```python
assistant.chat_mode()
```

##### `analyze_file(file_path: str, custom_prompt: Optional[str] = None)`
Analyze a file with optional custom prompt.

```python
assistant.analyze_file("script.py", "Find potential bugs")
```

##### `edit_file(file_path: str, instruction: str)`
Edit a file based on AI instructions.

```python
assistant.edit_file("config.json", "add debug settings")
```

##### `system_assistant(question: str)`
Get system administration help.

```python
assistant.system_assistant("how to install docker")
```

### Configuration

The `Config` class provides environment-based configuration.

```python
from ai_cli.config import Config

# Access configuration values
print(Config.SAFE_MODE)
print(Config.CREATE_BACKUPS)
print(Config.MAX_PREVIEW_SIZE)
```

#### Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SAFE_MODE` | bool | True | Enable safe mode |
| `CREATE_BACKUPS` | bool | True | Create backups when editing |
| `MAX_PREVIEW_SIZE` | int | 2000 | Max file size for preview |
| `COMMAND_TIMEOUT` | int | 30 | Command execution timeout |
| `DEFAULT_THEME` | str | "monokai" | Syntax highlighting theme |
| `DEFAULT_MODEL` | str | "" | Default model name |

### File Operations

The `FileHandler` class manages file operations.

```python
from ai_cli.files import FileHandler
from pathlib import Path

# Read file content
content = FileHandler.read_file_content(Path("file.py"))

# Create backup
backup_path = FileHandler.create_backup(Path("file.py"), content)

# Display file info
FileHandler.display_file_info(Path("file.py"), content)
```

### Command Execution

The `CommandExecutor` class handles system command execution.

```python
from ai_cli.commands import CommandExecutor

executor = CommandExecutor()

# Execute single command
success = executor.execute_single("ls -la")

# Execute with confirmation
executor.execute_with_confirmation(["ls -la", "pwd"])
```

### Model Management

The `ModelManager` class handles Ollama model operations.

```python
from ai_cli.models import ModelManager

# List available models
models = ModelManager.list_available_models()

# Select model interactively
model = ModelManager.select_model()
```

### Animations

The `LoadingAnimations` class provides loading indicators.

```python
from ai_cli.animations import LoadingAnimations

# Simple spinner
with LoadingAnimations.simple_spinner("Processing..."):
    # Do work
    pass

# Progress bar
with LoadingAnimations.progress_bar("Task"):
    # Do work
    pass
```

## Error Handling

All components include comprehensive error handling:

```python
try:
    assistant.analyze_file("nonexistent.py")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Error: {e}")
```

## Environment Variables

The application supports configuration via environment variables:

```bash
# Set default model
export DEFAULT_MODEL="llama3.2"

# Disable safe mode
export SAFE_MODE="false"

# Set custom timeout
export COMMAND_TIMEOUT="60"
```

## Examples

### Basic Usage

```python
from ai_cli.assistant import AIAssistant

# Create assistant
assistant = AIAssistant("llama3.2")

# Start chat
assistant.chat_mode()
```

### File Analysis

```python
# Analyze a Python file
assistant.analyze_file("script.py", "Find security vulnerabilities")
```

### System Administration

```python
# Get system help
assistant.system_assistant("check disk usage and clean up")
```

## Best Practices

1. **Always use safe mode** for file editing
2. **Check file permissions** before editing
3. **Use appropriate timeouts** for long-running operations
4. **Handle errors gracefully** in your code
5. **Test with different models** for best results

## Troubleshooting

### Common Issues

1. **No models available**: Ensure Ollama is running and models are installed
2. **Permission errors**: Check file permissions and safe mode settings
3. **Timeout errors**: Increase `COMMAND_TIMEOUT` for long operations
4. **Display issues**: Check terminal color support and `TERM` variable
