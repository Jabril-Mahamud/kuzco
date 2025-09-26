"""Comprehensive error handling and validation system"""
import sys
import subprocess
from typing import Optional, Callable, Any, TypeVar, Dict
from functools import wraps
from rich.console import Console
from rich.panel import Panel
import ollama

console = Console()

T = TypeVar('T')


class KuzcoError(Exception):
    """Base exception for Kuzco errors"""
    pass


class OllamaConnectionError(KuzcoError):
    """Raised when Ollama is not accessible"""
    pass


class ModelNotFoundError(KuzcoError):
    """Raised when specified model is not found"""
    pass


class FileOperationError(KuzcoError):
    """Raised for file operation failures"""
    pass


class ErrorHandler:
    """Centralized error handling and recovery"""

    @staticmethod
    def check_ollama_status() -> bool:
        """Check if Ollama is running and accessible"""
        try:
            # Try to list models as a connectivity check
            models = ollama.list()
            return True
        except Exception as e:
            return False

    @staticmethod
    def check_ollama_installed() -> bool:
        """Check if Ollama is installed on the system"""
        try:
            result = subprocess.run(
                ['which', 'ollama'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False

    @staticmethod
    def start_ollama() -> bool:
        """Attempt to start Ollama service"""
        try:
            console.print("[yellow]🚀 Attempting to start Ollama service...[/yellow]")

            # Try systemctl first (for systemd systems)
            result = subprocess.run(
                ['systemctl', 'start', 'ollama'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                console.print("[green]✅ Ollama service started successfully[/green]")
                return True

            # Try direct ollama serve command
            subprocess.Popen(
                ['ollama', 'serve'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait a moment for it to start
            import time
            time.sleep(3)

            if ErrorHandler.check_ollama_status():
                console.print("[green]✅ Ollama started successfully[/green]")
                return True

        except Exception as e:
            console.print(f"[red]Failed to start Ollama: {e}[/red]")

        return False

    @staticmethod
    def validate_model(model_name: str) -> bool:
        """Validate that a model exists"""
        try:
            models = ollama.list()
            available = [m.model for m in models.models]
            return model_name in available
        except:
            return False

    @staticmethod
    def suggest_model_pull(model_name: str) -> bool:
        """Offer to pull a model if it's not installed"""
        console.print(Panel(
            f"[yellow]Model '{model_name}' is not installed.[/yellow]\n"
            f"Would you like to download it now?",
            title="🤖 Model Not Found",
            border_style="yellow"
        ))

        choice = console.input("[bold]Download model? (y/n):[/bold] ").strip().lower()

        if choice == 'y':
            try:
                console.print(f"[cyan]📥 Downloading {model_name}...[/cyan]")
                console.print("[dim]This may take a few minutes depending on the model size.[/dim]")

                # Pull the model
                subprocess.run(['ollama', 'pull', model_name], check=True)

                console.print(f"[green]✅ Model {model_name} downloaded successfully![/green]")
                return True

            except subprocess.CalledProcessError as e:
                console.print(f"[red]❌ Failed to download model: {e}[/red]")
                return False

        return False

    @staticmethod
    def handle_file_error(file_path: str, operation: str = "read") -> None:
        """Provide helpful feedback for file errors"""
        from pathlib import Path

        path = Path(file_path)
        parent = path.parent

        error_panel = Panel(
            f"[red]Cannot {operation} file:[/red] {file_path}\n\n",
            title=f"❌ File {operation.title()} Error",
            border_style="red"
        )
        console.print(error_panel)

        # Provide suggestions
        suggestions = []

        # Check if parent directory exists
        if not parent.exists():
            suggestions.append(f"• Directory '{parent}' does not exist")

        # Check permissions
        elif parent.exists() and not os.access(parent, os.R_OK):
            suggestions.append(f"• No read permission for directory '{parent}'")

        # Find similar files
        if parent.exists():
            try:
                similar = []
                for file in parent.iterdir():
                    if file.is_file() and file_path.lower() in str(file).lower():
                        similar.append(str(file.name))

                if similar:
                    suggestions.append("• Did you mean one of these?")
                    for s in similar[:5]:
                        suggestions.append(f"  - {s}")
            except:
                pass

        if suggestions:
            console.print("[yellow]💡 Suggestions:[/yellow]")
            for suggestion in suggestions:
                console.print(suggestion)

    @staticmethod
    def safe_execute(func: Callable[..., T],
                     error_message: str = "Operation failed",
                     fallback: Optional[T] = None,
                     retry_count: int = 0) -> Optional[T]:
        """Safely execute a function with error handling and optional retry"""

        attempts = 0
        last_error = None

        while attempts <= retry_count:
            try:
                return func()
            except Exception as e:
                last_error = e
                attempts += 1

                if attempts <= retry_count:
                    console.print(f"[yellow]Retry {attempts}/{retry_count}...[/yellow]")
                    import time
                    time.sleep(1)

        # All attempts failed
        console.print(f"[red]{error_message}: {last_error}[/red]")
        return fallback


def handle_errors(fallback: Any = None):
    """Decorator for automatic error handling"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OllamaConnectionError as e:
                console.print(Panel(
                    "[red]Cannot connect to Ollama service[/red]\n"
                    "Please ensure Ollama is running:\n"
                    "[cyan]ollama serve[/cyan]",
                    title="🔌 Connection Error",
                    border_style="red"
                ))
                return fallback
            except ModelNotFoundError as e:
                console.print(Panel(
                    f"[red]{str(e)}[/red]\n"
                    "Available models can be listed with:\n"
                    "[cyan]ollama list[/cyan]",
                    title="🤖 Model Error",
                    border_style="red"
                ))
                return fallback
            except FileOperationError as e:
                ErrorHandler.handle_file_error(str(e))
                return fallback
            except KeyboardInterrupt:
                console.print("\n[magenta]Operation cancelled by user[/magenta]")
                return fallback
            except Exception as e:
                console.print(Panel(
                    f"[red]Unexpected error:[/red] {str(e)}\n"
                    "[yellow]Please report this issue if it persists[/yellow]",
                    title="❌ Error",
                    border_style="red"
                ))
                return fallback
        return wrapper
    return decorator


class Validator:
    """Input validation utilities"""

    @staticmethod
    def validate_file_path(path: str, must_exist: bool = True) -> Dict[str, Any]:
        """Validate file path and return validation result"""
        from pathlib import Path

        result = {
            "valid": False,
            "path": None,
            "error": None,
            "suggestions": []
        }

        try:
            file_path = Path(path).expanduser().resolve()

            if must_exist and not file_path.exists():
                result["error"] = f"File does not exist: {path}"

                # Find similar files
                parent = file_path.parent
                if parent.exists():
                    similar = [f.name for f in parent.glob(f"*{file_path.name}*") if f.is_file()]
                    result["suggestions"] = similar[:5]
            else:
                result["valid"] = True
                result["path"] = file_path

        except Exception as e:
            result["error"] = str(e)

        return result

    @staticmethod
    def validate_command(command: str, safe_mode: bool = True) -> Dict[str, Any]:
        """Validate a system command for safety"""

        result = {
            "valid": True,
            "safe": True,
            "warnings": [],
            "requires_sudo": False
        }

        # Dangerous commands that should be warned about
        dangerous_patterns = [
            ('rm -rf', '⚠️  Recursive deletion - will delete entire directory trees'),
            ('dd if=', '⚠️  Disk operation - can overwrite entire disks'),
            ('mkfs', '⚠️  Format operation - will erase filesystem'),
            ('> /dev/', '⚠️  Device write - can damage system'),
            ('fork()', '⚠️  Fork bomb risk'),
            (':(){ :|:& }', '⚠️  Fork bomb detected!'),
        ]

        command_lower = command.lower()

        for pattern, warning in dangerous_patterns:
            if pattern.lower() in command_lower:
                result["warnings"].append(warning)
                result["safe"] = False

        # Check for sudo
        if command.strip().startswith(('sudo ', 'su ')):
            result["requires_sudo"] = True
            result["warnings"].append("🔒 Requires administrator privileges")

        # Check for output redirection that might overwrite files
        if '>' in command and '>>' not in command:
            result["warnings"].append("📝 Will overwrite existing file if it exists")

        return result


# Initialize error handler on import
import os
error_handler = ErrorHandler()