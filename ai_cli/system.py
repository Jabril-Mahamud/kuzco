"""
AI Assistant CLI - System Operations Module
Handles both AI-powered system assistance and command execution
"""
import subprocess
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import ollama

from ai_cli.config import Config
from ai_cli.errors import handle_errors
from ai_cli.animations import show_thinking_animation

console = Console()


class SystemOperations:
    """Handles system/Ubuntu related questions and command execution"""

    def __init__(self, model: str, config: Config):
        """Initialize system operations"""
        self.model = model
        self.config = config
        self.timeout = config.COMMAND_TIMEOUT

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

    def parse_commands(self, response: str) -> List[str]:
        """Extract executable commands from AI response"""
        if 'EXECUTE_COMMAND:' not in response:
            return []

        commands = []
        for line in response.split('\n'):
            if line.strip().startswith('EXECUTE_COMMAND:'):
                cmd = line.replace('EXECUTE_COMMAND:', '').strip()
                commands.append(cmd)
        return commands

    def execute_single(self, cmd: str) -> bool:
        """Execute a single command with error handling"""
        try:
            console.print(f"\n[bold cyan]⚡ Executing:[/bold cyan] [bold white]{cmd}[/bold white]")

            # Check for commands that need sudo
            if any(cmd.strip().startswith(prefix) for prefix in self.config.SUDO_PREFIXES):
                console.print("[bold yellow]⚠️  This command requires administrator privileges![/bold yellow]")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            if result.returncode == 0:
                console.print(f"[bold green]✅ Success![/bold green]")
                if result.stdout.strip():
                    console.print("[bold blue]📤 Output:[/bold blue]")
                    console.print(result.stdout.strip())
                return True
            else:
                console.print(f"[bold red]❌ Failed (exit code: {result.returncode})[/bold red]")
                if result.stderr.strip():
                    console.print("[bold red]🚨 Error:[/bold red]")
                    console.print(result.stderr.strip())
                return False

        except subprocess.TimeoutExpired:
            console.print(f"[bold red]⏰ Command timed out ({self.timeout}s limit)[/bold red]")
            return False
        except Exception as e:
            console.print(f"[bold red]💥 Error executing command:[/bold red] {e}")
            return False

    def execute_with_confirmation(self, commands: List[str]) -> None:
        """Execute commands with user confirmation"""
        if not commands:
            return

        console.print(f"\n[bold yellow]🔧 Suggested Commands:[/bold yellow]")
        for i, cmd in enumerate(commands, 1):
            console.print(f"  [bold cyan]{i}.[/bold cyan] [bold white]{cmd}[/bold white]")

        console.print(f"\n[bold yellow]⚡ Execute these commands?[/bold yellow]")
        choice = console.input(
            "[bold green]Enter 'yes' to execute all, 'selective' to choose, or anything else to skip:[/bold green] "
        ).strip().lower()

        if choice == 'yes':
            for cmd in commands:
                self.execute_single(cmd)
        elif choice == 'selective':
            self._execute_selective(commands)
        else:
            console.print("[bold magenta]⏭️  Commands skipped.[/bold magenta]")

    def _execute_selective(self, commands: List[str]) -> None:
        """Let user choose which commands to execute"""
        for i, cmd in enumerate(commands, 1):
            choice = console.input(
                f"[bold yellow]Execute command {i}:[/bold yellow] '{cmd}' ? (y/n): "
            ).strip().lower()
            if choice in ['y', 'yes']:
                self.execute_single(cmd)
            else:
                console.print(f"[bold magenta]⏭️  Skipped:[/bold magenta] [bold white]{cmd}[/bold white]")
