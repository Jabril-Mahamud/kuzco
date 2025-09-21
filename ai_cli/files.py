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
    def find_file_case_insensitive(file_path: Path) -> Optional[Path]:
        """Find file with case-insensitive matching and suggest alternatives"""
        if file_path.exists():
            return file_path

        # Try case-insensitive search in the same directory
        parent_dir = file_path.parent
        target_name = file_path.name.lower()

        try:
            for item in parent_dir.iterdir():
                if item.is_file() and item.name.lower() == target_name:
                    console.print(f"[bold yellow]💡 Found similar file:[/bold yellow] {item.name}")
                    return item
        except Exception:
            pass

        # Suggest files with similar names
        try:
            similar_files = []
            for item in parent_dir.iterdir():
                if item.is_file() and target_name in item.name.lower():
                    similar_files.append(item.name)

            if similar_files:
                console.print(f"[bold yellow]💡 Did you mean one of these?[/bold yellow]")
                for file in similar_files[:5]:  # Show max 5 suggestions
                    console.print(f"  • {file}")
        except Exception:
            pass

        return None

    @staticmethod
    def read_file_content(file_path: Path) -> Optional[str]:
        """Read file content with error handling and case-insensitive matching"""
        try:
            # First try exact match
            if file_path.exists():
                return file_path.read_text(encoding='utf-8')

            # Try case-insensitive search
            found_file = FileHandler.find_file_case_insensitive(file_path)
            if found_file:
                return found_file.read_text(encoding='utf-8')

            console.print(f"[bold red]File not found:[/bold red] {file_path}")
            return None

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