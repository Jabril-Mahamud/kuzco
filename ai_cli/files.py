"""File reading and editing operations"""
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from ai_cli.config import Config

console = Console()


class FileHandler:
    """Handles file reading and editing operations"""

    @staticmethod
    def read_file_content(file_path: Path) -> Optional[str]:
        """Read file content with error handling"""
        try:
            if not file_path.exists():
                console.print(f"[bold red]File not found:[/bold red] {file_path}")
                return None
            return file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            console.print(f"[bold red]Error:[/bold red] Cannot read {file_path} as text file")
            return None
        except Exception as e:
            console.print(f"[bold red]Error reading file:[/bold red] {e}")
            return None

    @staticmethod
    def display_file_info(path: Path, content: str) -> None:
        """Display file information panel"""
        console.print(Panel(
            f"[bold]File:[/bold] {path.name}\n"
            f"[bold]Size:[/bold] {len(content)} characters\n"
            f"[bold]Lines:[/bold] {len(content.splitlines())}",
            title="📁 File Info",
            border_style="blue"
        ))

    @staticmethod
    def display_file_preview(path: Path, content: str) -> None:
        """Display syntax-highlighted file preview"""
        if len(content) < Config.MAX_PREVIEW_SIZE:
            syntax = Syntax(
                content,
                path.suffix[1:] if path.suffix else "text",
                theme=Config.DEFAULT_THEME,
                line_numbers=True
            )
            console.print(Panel(syntax, title="📄 File Preview", border_style="green"))

    @staticmethod
    def create_backup(path: Path, content: str) -> Path:
        """Create a backup of the file if safe mode is enabled"""
        if not Config.CREATE_BACKUPS:
            console.print("[bold yellow]⚠️  Safe mode disabled - no backup created[/bold yellow]")
            return path

        backup_path = path.parent / f"backup_{path.name}"
        backup_path.write_text(content)
        console.print(f"[bold green]💾 Backup created:[/bold green] [bold white]{backup_path}[/bold white]")
        return backup_path

    @staticmethod
    def clean_ai_response(content: str) -> str:
        """Remove markdown code blocks from AI response if present"""
        if content.startswith('```'):
            lines = content.split('\n')
            if len(lines) > 2:
                return '\n'.join(lines[1:-1])
        return content