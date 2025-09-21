"""
Ollama model management
"""
import sys
from typing import List
from rich.console import Console
import ollama

console = Console()


class ModelManager:
    """Handles Ollama model selection and listing"""

    @staticmethod
    def list_available_models() -> List[str]:
        """Return a list of installed Ollama models"""
        try:
            models = ollama.list()
            # Filter out None values and ensure all items are strings
            return [str(m.model) for m in models.models if m.model is not None]
        except Exception as e:
            console.print(f"[bold red]Error fetching models:[/bold red] {e}")
            return []

    @staticmethod
    def select_model() -> str:
        """Interactive model selection"""
        models = ModelManager.list_available_models()

        if not models:
            console.print("[bold red]No models found! Please install Ollama models first.[/bold red]")
            console.print("[bold yellow]Example: ollama pull llama3.2[/bold yellow]")
            sys.exit(1)

        if len(models) == 1:
            model_name = models[0]
            console.print(f"[bold green]Using model:[/bold green] {model_name}")
            return model_name

        console.print("[bold yellow]Available models:[/bold yellow]")
        for i, model in enumerate(models, 1):
            console.print(f"[bold blue]{i}[/bold blue]: {model}")

        while True:
            try:
                choice = console.input("\nChoose a model by number: ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(models):
                    model_name = models[int(choice) - 1]
                    console.print(f"[bold green]Using model:[/bold green] {model_name}")
                    return model_name
                console.print("[bold red]Invalid choice, try again.[/bold red]")
            except KeyboardInterrupt:
                console.print("\n[bold magenta]Goodbye![/bold magenta]")
                sys.exit(0)
            except Exception:
                console.print("[bold red]Invalid input, try again.[/bold red]")