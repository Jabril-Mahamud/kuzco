"""
AI Assistant CLI - Main assistant class
"""
from typing import Optional
from rich.console import Console
from rich.panel import Panel

from ai_cli.config import Config
from ai_cli.models import ModelManager
from ai_cli.errors import ErrorHandler, OllamaConnectionError
from ai_cli.file_handler import FileHandler
from ai_cli.chat import ChatOperations
from ai_cli.system import SystemOperations

console = Console()


class AIAssistant:
    """Main AI Assistant class for handling all AI interactions"""

    def __init__(self, model: Optional[str] = None):
        """Initialize the AI Assistant"""
        self.config = Config()
        self.model = model or self.config.DEFAULT_MODEL

        # Initialize operation modules
        self.file_handler = FileHandler(self.model, self.config)
        self.chat_ops = ChatOperations(self.model, self.config)
        self.system_ops = SystemOperations(self.model, self.config)

        # Validate and setup model
        self._setup_model()

    def _setup_model(self):
        """Setup and validate the model"""
        # Check if Ollama is running
        if not ErrorHandler.check_ollama_status():
            if not ErrorHandler.check_ollama_installed():
                console.print(Panel(
                    "[red]Ollama is not installed![/red]\n"
                    "Please install Ollama first:\n"
                    "[cyan]curl -fsSL https://ollama.ai/install.sh | sh[/cyan]",
                    title="❌ Ollama Not Found",
                    border_style="red"
                ))
                raise OllamaConnectionError("Ollama is not installed")

            # Try to start Ollama
            if not ErrorHandler.start_ollama():
                console.print(Panel(
                    "[red]Cannot start Ollama service[/red]\n"
                    "Please start it manually:\n"
                    "[cyan]ollama serve[/cyan]",
                    title="🔌 Service Error",
                    border_style="red"
                ))
                raise OllamaConnectionError("Cannot start Ollama service")

        # Select model if not specified
        if not self.model:
            self.model = ModelManager.select_model()
        elif not ErrorHandler.validate_model(self.model):
            console.print(f"[yellow]Model '{self.model}' not found[/yellow]")
            if ErrorHandler.suggest_model_pull(self.model):
                self.model = self.model  # Model was pulled successfully
            else:
                self.model = ModelManager.select_model()

    def analyze_file(self, file_path: str, custom_prompt: Optional[str] = None):
        """Analyze a file and provide insights"""
        return self.file_handler.analyze_file(file_path, custom_prompt)

    def edit_file(self, file_path: str, instruction: str):
        """Edit a file using AI assistance"""
        return self.file_handler.edit_file(file_path, instruction)

    def system_assistant(self, question: str):
        """Handle system/Ubuntu related questions"""
        return self.system_ops.system_assistant(question)

    def chat_mode(self):
        """Start interactive chat mode"""
        return self.chat_ops.chat_mode()

    def save_conversation(self, filepath: Optional[str] = None):
        """Save conversation history to file"""
        return self.chat_ops.save_conversation(filepath)

    def load_conversation(self, filepath: str):
        """Load previous conversation"""
        return self.chat_ops.load_conversation(filepath)