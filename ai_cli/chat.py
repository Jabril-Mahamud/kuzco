"""
AI Assistant CLI - Chat Module
Handles interactive chat and conversation management
"""
import json
from datetime import datetime
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import ollama

from ai_cli.config import Config
from ai_cli.errors import handle_errors
from ai_cli.animations import show_thinking_animation

console = Console()


class ChatOperations:
    """Handles interactive chat and conversation management"""

    def __init__(self, model: str, config: Config):
        """Initialize chat operations"""
        self.model = model
        self.config = config
        self.conversation_history: List[dict] = []

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

    def get_conversation_history(self) -> List[dict]:
        """Get the current conversation history"""
        return self.conversation_history.copy()

    def clear_conversation(self):
        """Clear the conversation history"""
        self.conversation_history = []
        console.print("[yellow]Conversation history cleared[/yellow]")
