#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.text import Text
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import ollama

console = Console()


class AIAssistant:
    def __init__(self, model_name=None):
        self.model_name = model_name or self.select_model()
        self.conversation = []

    def list_models(self):
        """Return a list of installed Ollama models."""
        try:
            models = ollama.list()
            return [m.model for m in models.models]
        except Exception as e:
            console.print(f"[bold red]Error fetching models:[/bold red] {e}")
            return []

    def select_model(self):
        """Interactive model selection."""
        models = self.list_models()
        if not models:
            console.print("[bold red]No models found![/bold red]")
            sys.exit(1)

        if len(models) == 1:
            console.print(f"[bold green]Using model:[/bold green] {models[0]}")
            return models[0]

        console.print("[bold yellow]Available models:[/bold yellow]")
        for i, m in enumerate(models, 1):
            console.print(f"[bold blue]{i}[/bold blue]: {m}")

        while True:
            choice = console.input("\nChoose a model by number: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(models):
                model_name = models[int(choice) - 1]
                console.print(f"[bold green]Using model:[/bold green] {model_name}")
                return model_name
            console.print("[bold red]Invalid choice, try again.[/bold red]")

    def stream_response(self, messages):
        """Stream response from the model."""
        try:
            response_text = ""
            stream = ollama.chat(model=self.model_name, messages=messages, stream=True)

            for chunk in stream:
                token = chunk["message"]["content"]
                # Use regular print for streaming to support flush
                print(token, end="", flush=True)
                response_text += token

            console.print()  # newline after response
            return response_text

        except Exception as e:
            console.print(f"[bold red]Error during chat:[/bold red] {e}")
            return ""

    def chat_mode(self):
        """Interactive chat mode."""
        console.print("[bold green]🤖 AI Assistant Chat Mode[/bold green]")
        console.print(f"[bold yellow]Model:[/bold yellow] {self.model_name}")
        console.print(
            "[bold magenta]Type 'exit', 'quit', or Ctrl+C to quit[/bold magenta]\n"
        )

        try:
            while True:
                user_input = console.input("[bold green]You:[/bold green] ").strip()
                if user_input.lower() in ["exit", "quit"]:
                    console.print("[bold magenta]Goodbye![/bold magenta]")
                    break

                if not user_input:
                    continue

                self.conversation.append({"role": "user", "content": user_input})

                console.print()  # Add space before assistant response
                console.print("[bold blue]Assistant:[/bold blue] ", end="")
                response = self.stream_response(self.conversation)

                if response:
                    self.conversation.append({"role": "assistant", "content": response})
                console.print()

        except KeyboardInterrupt:
            console.print("\n[bold magenta]Goodbye![/bold magenta]")

    def read_file(self, file_path, prompt=None):
        """Read and analyze a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                console.print(f"[bold red]File not found:[/bold red] {file_path}")
                return

            content = path.read_text(encoding="utf-8")

            # Display file info
            console.print(
                Panel(
                    f"[bold]File:[/bold] {path.name}\n"
                    f"[bold]Size:[/bold] {len(content)} characters\n"
                    f"[bold]Lines:[/bold] {len(content.splitlines())}",
                    title="📁 File Info",
                    border_style="blue",
                )
            )

            # Show file preview if it's reasonable size
            if len(content) < 2000:
                syntax = Syntax(
                    content,
                    path.suffix[1:] if path.suffix else "text",
                    theme="monokai",
                    line_numbers=True,
                )
                console.print(
                    Panel(syntax, title="📄 File Preview", border_style="green")
                )

            # Default prompt if none provided
            if not prompt:
                prompt = f"Please analyze this {path.suffix[1:] if path.suffix else 'text'} file and provide a summary of its contents, structure, and any notable patterns or issues you notice."

            # Create message with file content
            full_prompt = (
                f"{prompt}\n\nFile: {path.name}\nContent:\n```\n{content}\n```"
            )

            messages = [{"role": "user", "content": full_prompt}]

            console.print(f"\n[bold blue]🔍 Analyzing {path.name}...[/bold blue]")
            console.print("[bold blue]Assistant:[/bold blue] ", end="")
            self.stream_response(messages)
            console.print()

        except UnicodeDecodeError:
            console.print(
                f"[bold red]Error:[/bold red] Cannot read {file_path} as text file"
            )
        except Exception as e:
            console.print(f"[bold red]Error reading file:[/bold red] {e}")

    def edit_file(self, file_path, instruction):
        """Edit a file based on instructions."""
        try:
            path = Path(file_path)
            if not path.exists():
                console.print(f"[bold red]File not found:[/bold red] {file_path}")
                return

            original_content = path.read_text(encoding="utf-8")

            console.print(
                Panel(
                    f"[bold]File:[/bold] {path.name}\n"
                    f"[bold]Instruction:[/bold] {instruction}",
                    title="✏️ Edit Request",
                    border_style="yellow",
                )
            )

            # Create edit prompt
            edit_prompt = f"""Please edit the following file according to the instruction.
Return ONLY the complete modified file content, with no explanations or markdown formatting.

Instruction: {instruction}

File: {path.name}
Original content:
```
{original_content}
```

Modified content:"""

            messages = [{"role": "user", "content": edit_prompt}]

            console.print(f"\n[bold blue]✏️ Editing {path.name}...[/bold blue]\n")

            with Progress(
                SpinnerColumn(), TextColumn("[progress.description]{task.description}")
            ) as progress:
                task = progress.add_task("Processing edit...", total=None)

                # Get the edit without streaming for cleaner output
                response = ollama.chat(model=self.model_name, messages=messages)
                new_content = response["message"]["content"].strip()

                # Remove any markdown code blocks if present
                if new_content.startswith("```"):
                    lines = new_content.split("\n")
                    if len(lines) > 2:
                        new_content = "\n".join(lines[1:-1])

                progress.update(task, completed=True)

            # Create backup with prefix
            backup_path = path.parent / f"backup_{path.name}"
            backup_path.write_text(original_content)
            console.print(f"[bold green]✓ Backup created:[/bold green] {backup_path}")

            # Write new content
            path.write_text(new_content)
            console.print(f"[bold green]✓ File updated:[/bold green] {path}")

            # Show diff-like summary
            orig_lines = len(original_content.splitlines())
            new_lines = len(new_content.splitlines())
            console.print(
                f"[bold blue]Changes:[/bold blue] {orig_lines} → {new_lines} lines"
            )

        except Exception as e:
            console.print(f"[bold red]Error editing file:[/bold red] {e}")

    def ask_about_system(self, question):
        """Ask questions about the system."""
        # Get system info
        import platform
        import subprocess

        system_info = {
            "OS": platform.system(),
            "Distribution": platform.platform(),
            "Python": platform.python_version(),
            "Architecture": platform.machine(),
            "Hostname": platform.node(),
        }

        # Get current directory and file listing
        cwd = os.getcwd()
        try:
            files = subprocess.run(["ls", "-la"], capture_output=True, text=True).stdout
        except:
            files = "Could not list files"

        system_prompt = f"""You are an AI assistant helping with system administration and development on Ubuntu (Omakub).

System Information:
{system_info}

Current Directory: {cwd}
Directory Contents:
{files}

User Question: {question}

Please provide helpful, specific advice for Ubuntu/Linux systems."""

        messages = [{"role": "user", "content": system_prompt}]

        console.print("[bold blue]🖥️ System Assistant:[/bold blue] ", end="")
        self.stream_response(messages)
        console.print()


def main():
    parser = argparse.ArgumentParser(
        description="AI Assistant CLI - Like Google Gemini for your terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
    Examples:
    %(prog)s                                    # Start interactive chat
    %(prog)s --read file.py                     # Analyze a file
    %(prog)s --read file.py --prompt "explain"  # Analyze with custom prompt
    %(prog)s --edit file.py "add comments"      # Edit a file
    %(prog)s --system "how to install docker"   # Ask about system
        """,
    )

    parser.add_argument("--model", "-m", help="Specify model to use")
    parser.add_argument("--read", "-r", metavar="FILE", help="Read and analyze a file")
    parser.add_argument(
        "--edit", "-e", metavar="FILE", help="Edit a file with AI assistance"
    )
    parser.add_argument("--prompt", "-p", help="Custom prompt for file analysis")
    parser.add_argument("--instruction", "-i", help="Instruction for file editing")
    parser.add_argument("--system", "-s", help="Ask about system/Ubuntu")
    parser.add_argument(
        "--chat", "-c", action="store_true", help="Start interactive chat (default)"
    )

    args = parser.parse_args()

    # Create assistant
    assistant = AIAssistant(args.model)

    try:
        if args.read:
            assistant.read_file(args.read, args.prompt)
        elif args.edit:
            if not args.instruction:
                instruction = console.input(
                    "[bold yellow]Enter editing instruction:[/bold yellow] "
                )
            else:
                instruction = args.instruction
            assistant.edit_file(args.edit, instruction)
        elif args.system:
            assistant.ask_about_system(args.system)
        else:
            # Default to chat mode
            assistant.chat_mode()

    except KeyboardInterrupt:
        console.print("\n[bold magenta]Goodbye![/bold magenta]")


if __name__ == "__main__":
    main()
