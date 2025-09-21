"""System command execution with safety checks"""
import subprocess
from typing import List
from rich.console import Console
from ai_cli.config import Config

console = Console()


class CommandExecutor:
    """Handles system command execution with safety checks"""

    def __init__(self, timeout: int = Config.COMMAND_TIMEOUT):
        self.timeout = timeout

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
            if any(cmd.strip().startswith(prefix) for prefix in Config.SUDO_PREFIXES):
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