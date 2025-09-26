"""
AI Assistant CLI - Main assistant class
"""
import os
import json
from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import ollama

from ai_cli.config import Config
from ai_cli.models import ModelManager
from ai_cli.files import EnhancedFileHandler
from ai_cli.errors import ErrorHandler, handle_errors, OllamaConnectionError, ModelNotFoundError, FileOperationError
from ai_cli.animations import show_thinking_animation

console = Console()


class AIAssistant:
    """Main AI Assistant class for handling all AI interactions"""

    def __init__(self, model: Optional[str] = None):
        """Initialize the AI Assistant"""
        self.config = Config()
        self.model = model or self.config.DEFAULT_MODEL
        self.conversation_history = []

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

    @handle_errors()
    def analyze_file(self, file_path: str, custom_prompt: Optional[str] = None):
        """Analyze a file and provide insights"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Create analysis prompt
            prompt = custom_prompt or "Analyze this code and provide insights about its structure, functionality, and potential improvements."

            full_prompt = f"""File: {file_path}
Content:
```{Path(file_path).suffix[1:] if Path(file_path).suffix else 'text'}
{content}
```

{prompt}"""

            console.print(f"[bold blue]🔍 Analyzing {file_path}...[/bold blue]")

            # Show thinking animation
            with show_thinking_animation():
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": full_prompt}]
                )

            # Display results
            analysis = response['message']['content']
            console.print(Panel(
                Markdown(analysis),
                title=f"📄 Analysis of {Path(file_path).name}",
                border_style="blue"
            ))

        except FileNotFoundError:
            ErrorHandler.handle_file_error(file_path, "read")
        except Exception as e:
            console.print(f"[red]Error analyzing file: {e}[/red]")

    @handle_errors()
    def edit_file(self, file_path: str, instruction: str):
        """Edit a file using AI assistance"""
        try:
            # Read current file content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            # Create edit prompt using the enhanced file handler
            edit_prompt = EnhancedFileHandler.create_edit_prompt(file_path, original_content, instruction)

            console.print(f"[bold yellow]✏️  Editing {file_path}...[/bold yellow]")
            console.print(f"[dim]Instruction: {instruction}[/dim]")

            # Show thinking animation
            with show_thinking_animation():
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": edit_prompt}]
                )

            # Clean the AI response
            cleaned_content = EnhancedFileHandler.clean_ai_response(response['message']['content'])

            # Validate the cleaned content
            is_valid, validation_msg = EnhancedFileHandler.validate_cleaned_content(
                original_content, cleaned_content, Path(file_path).suffix
            )

            if not is_valid:
                console.print(f"[red]⚠️  {validation_msg}[/red]")
                console.print("[yellow]Raw response for manual review:[/yellow]")
                console.print(Panel(
                    response['message']['content'],
                    title="Raw AI Response",
                    border_style="yellow"
                ))
                return

            # Create backup if enabled
            if self.config.CREATE_BACKUPS:
                backup_path = f"{file_path}.backup"
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                console.print(f"[dim]Backup created: {backup_path}[/dim]")

            # Write the edited content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)

            console.print(f"[green]✅ Successfully edited {file_path}[/green]")

        except FileNotFoundError:
            ErrorHandler.handle_file_error(file_path, "read")
        except Exception as e:
            console.print(f"[red]Error editing file: {e}[/red]")

    @handle_errors()
    def system_assistant(self, question: str):
        """Handle system/Ubuntu related questions"""
        system_prompt = """You are a helpful Ubuntu/Linux system assistant.
        Provide clear, practical answers about system administration, troubleshooting, and best practices.
        Focus on actionable solutions and explain commands clearly."""

        full_prompt = f"{system_prompt}\n\nQuestion: {question}"

        console.print("[bold green]🖥️  System Assistant[/bold green]")

        # Show thinking animation
        with show_thinking_animation():
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}]
            )

        # Display results
        answer = response['message']['content']
        console.print(Panel(
            Markdown(answer),
            title="🖥️  System Assistant Response",
            border_style="green"
        ))

    @handle_errors()
    def chat_mode(self):
        """Start interactive chat mode"""
        console.print(Panel(
            "[bold blue]🤖 Kuzco AI Assistant[/bold blue]\n"
            f"Model: {self.model}\n"
            "Type your questions or commands. Use 'exit', 'quit', or 'bye' to end the chat.",
            title="Welcome",
            border_style="blue"
        ))

        while True:
            try:
                user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()

                # Check for exit commands
                if user_input.lower() in self.config.EXIT_COMMANDS:
                    console.print("[bold magenta]Goodbye![/bold magenta]")
                    break

                if not user_input:
                    continue

                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": user_input})

                # Show thinking animation
                with show_thinking_animation():
                    response = ollama.chat(
                        model=self.model,
                        messages=self.conversation_history
                    )

                # Get AI response
                ai_response = response['message']['content']

                # Add to conversation history
                self.conversation_history.append({"role": "assistant", "content": ai_response})

                # Display response
                console.print(Panel(
                    Markdown(ai_response),
                    title="🤖 Assistant",
                    border_style="green"
                ))

            except KeyboardInterrupt:
                console.print("\n[bold magenta]Goodbye![/bold magenta]")
                break
            except Exception as e:
                console.print(f"[red]Error in chat: {e}[/red]")

    def save_conversation(self, filepath: Optional[str] = None):
        """Save conversation history to file"""
        if not filepath:
            from datetime import datetime
            filepath = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, indent=2)
            console.print(f"[green]💾 Conversation saved to {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving conversation: {e}[/red]")

    def load_conversation(self, filepath: str):
        """Load previous conversation"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.conversation_history = json.load(f)
            console.print(f"[green]📂 Conversation loaded from {filepath}[/green]")
        except Exception as e:
            console.print(f"[red]Error loading conversation: {e}[/red]")