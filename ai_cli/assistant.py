"""Main AI Assistant implementation"""
import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import ollama

from ai_cli.animations import LoadingAnimations
from ai_cli.config import Config
from ai_cli.models import ModelManager
from ai_cli.files import FileHandler
from ai_cli.commands import CommandExecutor

console = Console()


class AIAssistant:
    """Main AI Assistant with chat and task capabilities"""

    def __init__(self, model_name: Optional[str] = None):
        # Create config instance
        self.config = Config()

        # Use environment default model if available, otherwise use provided or select
        if not model_name and self.config.DEFAULT_MODEL:
            model_name = self.config.DEFAULT_MODEL

        self.model_name: str = model_name or ModelManager.select_model()
        self.conversation: List[Dict[str, str]] = []
        self.file_handler = FileHandler()
        self.command_executor = CommandExecutor()

        if not self.model_name:
            console.print("[bold red]Error: No valid model available![/bold red]")
            sys.exit(1)

        # Show safe mode status
        if not self.config.SAFE_MODE:
            console.print("[bold yellow]⚠️  Safe mode is DISABLED - backups will not be created[/bold yellow]")
        elif not self.config.CREATE_BACKUPS:
            console.print("[bold yellow]⚠️  Backup creation is DISABLED[/bold yellow]")

    def stream_response(self, messages: List[Dict[str, str]], show_spinner: bool = True, context: str = "chat") -> str:
        """Stream response from the model with optional loading animation"""
        try:
            response_text = ""
            in_thoughts = False
            thought_content = ""

            # Show thinking animation before response starts
            if show_spinner:
                # Use contextual loading message
                message = LoadingAnimations.get_contextual_message(context)

                with LoadingAnimations.simple_spinner(message) as status:
                    # Get the stream started
                    stream = ollama.chat(
                        model=self.model_name,
                        messages=messages,
                        stream=True
                    )

                    # Get first chunk to stop the spinner
                    first_chunk = next(stream)
                    token = first_chunk['message']['content']

                    # Stop spinner and start showing response
                    status.stop()

                    # Process the first token
                    if token.startswith('<') and '>' in token:
                        in_thoughts = True
                        thought_content += token
                        console.print("[bold blue]💭 Thoughts:[/bold blue]")
                        console.print("[dim blue]" + token + "[/dim blue]", end="", )
                    else:
                        console.print("[bold green]🤖 Assistant:[/bold green]")
                        console.print(token, end="", )

                    response_text += token

                    # Continue with rest of stream
                    for chunk in stream:
                        token = chunk['message']['content']

                        if in_thoughts:
                            if token.startswith('</') and '>' in token:
                                # End of thoughts
                                thought_content += token
                                console.print("[dim blue]" + token + "[/dim blue]", end="", )
                                console.print()  # Newline after thoughts
                                console.print("[bold cyan]─────────────────────────────────────────────────────────[/bold cyan]")
                                console.print("[bold green]🤖 Response:[/bold green]")
                                in_thoughts = False
                            else:
                                thought_content += token
                                console.print("[dim blue]" + token + "[/dim blue]", end="", )
                        else:
                            console.print(token, end="", )

                        response_text += token
            else:
                # No spinner mode (for system commands, etc.)
                stream = ollama.chat(
                    model=self.model_name,
                    messages=messages,
                    stream=True
                )

                for chunk in stream:
                    token = chunk['message']['content']
                    console.print(token, end="", )
                    response_text += token

            console.print()  # newline after response
            return response_text

        except StopIteration:
            # Handle case where stream is empty
            console.print()
            return ""
        except Exception as e:
            console.print(f"[bold red]Error during chat:[/bold red] {e}")
            return ""

    def get_response(self, messages: List[Dict[str, str]]) -> str:
        """Get response without streaming"""
        try:
            response = ollama.chat(model=self.model_name, messages=messages)
            return response['message']['content']
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return ""

    # ========================================================================
    # Main Features
    # ========================================================================

    def chat_mode(self) -> None:
        """Interactive chat mode with loading animations"""
        console.print("[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]")
        console.print("[bold cyan]│[/bold cyan] [bold green]🤖 AI Assistant Chat Mode[/bold green] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]│[/bold cyan] [bold yellow]Model:[/bold yellow] [bold white]{self.model_name}[/bold white] [bold cyan]│[/bold cyan]")

        # Show safe mode status
        if self.config.SAFE_MODE and self.config.CREATE_BACKUPS:
            console.print("[bold cyan]│[/bold cyan] [bold green]🛡️  Safe mode: ENABLED (backups will be created)[/bold green] [bold cyan]│[/bold cyan]")
        elif self.config.SAFE_MODE and not self.config.CREATE_BACKUPS:
            console.print("[bold cyan]│[/bold cyan] [bold yellow]🛡️  Safe mode: ENABLED (backups disabled)[/bold yellow] [bold cyan]│[/bold cyan]")
        else:
            console.print("[bold cyan]│[/bold cyan] [bold red]🛡️  Safe mode: DISABLED[/bold red] [bold cyan]│[/bold cyan]")

        console.print("[bold cyan]│[/bold cyan] [bold magenta]Type 'exit', 'quit', or Ctrl+C to quit[/bold magenta] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]│[/bold cyan] [bold yellow]Use /help for special commands[/bold yellow] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]\n")

        try:
            while True:
                user_input = console.input("[bold green]👤 You:[/bold green] ").strip()

                if user_input.lower() in self.config.EXIT_COMMANDS:
                    console.print("\n[bold magenta]👋 Goodbye![/bold magenta]")
                    break

                if not user_input:
                    continue

                # Check for special commands
                if self._handle_special_commands(user_input):
                    continue

                # Add user message to conversation
                self.conversation.append({"role": "user", "content": user_input})

                # Show that we're processing with animation
                console.print()  # Add space before assistant response

                # Stream response with contextual thinking animation
                response = self.stream_response(self.conversation, show_spinner=True, context="chat")

                if response:
                    self.conversation.append({"role": "assistant", "content": response})
                console.print()

        except KeyboardInterrupt:
            console.print("\n[bold magenta]Goodbye![/bold magenta]")

    def _handle_special_commands(self, user_input: str) -> bool:
        """Handle special commands within chat mode. Returns True if command was handled."""
        input_lower = user_input.lower().strip()

        # /read command: /read <file> [prompt]
        if input_lower.startswith('/read '):
            parts = user_input[6:].strip().split(' ', 1)
            file_path = parts[0]
            custom_prompt = parts[1] if len(parts) > 1 else None

            console.print(f"[bold cyan]📖 Reading file:[/bold cyan] {file_path}")
            self.analyze_file(file_path, custom_prompt)
            return True

        # /edit command: /edit <file> <instruction>
        elif input_lower.startswith('/edit '):
            parts = user_input[6:].strip().split(' ', 1)
            if len(parts) < 2:
                console.print("[bold red]Usage: /edit <file> <instruction>[/bold red]")
                return True
            file_path = parts[0]
            instruction = parts[1]

            console.print(f"[bold cyan]✏️  Editing file:[/bold cyan] {file_path}")
            self.edit_file(file_path, instruction)
            return True

        # /system command: /system <question>
        elif input_lower.startswith('/system '):
            question = user_input[8:].strip()
            console.print(f"[bold cyan]🖥️  System question:[/bold cyan] {question}")
            self.system_assistant(question)
            return True

        # /help command
        elif input_lower == '/help':
            self._show_chat_help()
            return True

        # /clear command
        elif input_lower == '/clear':
            self.conversation.clear()
            console.print("[bold green]🧹 Conversation history cleared![/bold green]")
            return True

        return False

    def _show_chat_help(self):
        """Show help for special chat commands"""
        console.print("\n[bold cyan]📋 Special Chat Commands:[/bold cyan]")
        console.print("[bold yellow]/read <file> [prompt][/bold yellow] - Analyze a file")
        console.print("[bold yellow]/edit <file> <instruction>[/bold yellow] - Edit a file with AI")
        console.print("[bold yellow]/system <question>[/bold yellow] - Ask system/Ubuntu questions")
        console.print("[bold yellow]/help[/bold yellow] - Show this help")
        console.print("[bold yellow]/clear[/bold yellow] - Clear conversation history")
        console.print("[bold yellow]exit, quit, bye, goodbye[/bold yellow] - Exit chat")
        console.print()

    def analyze_file(self, file_path: str, custom_prompt: Optional[str] = None) -> None:
        """Read and analyze a file with loading animation"""
        path = Path(file_path)
        content = self.file_handler.read_file_content(path)

        if not content:
            return

        # Display file information
        self.file_handler.display_file_info(path, content)
        self.file_handler.display_file_preview(path, content)

        # Prepare prompt
        if not custom_prompt:
            file_type = path.suffix[1:] if path.suffix else 'text'
            custom_prompt = (
                f"Please analyze this {file_type} file and provide a summary of its contents, "
                "structure, and any notable patterns or issues you notice."
            )

        full_prompt = f"{custom_prompt}\n\nFile: {path.name}\nContent:\n```\n{content}\n```"
        messages = [{"role": "user", "content": full_prompt}]

        console.print(f"\n[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]")
        console.print(f"[bold cyan]│[/bold cyan] [bold blue]🔍 Analyzing {path.name}...[/bold blue] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]")

        # Use file context for animation
        self.stream_response(messages, show_spinner=True, context="file")
        console.print()

    def edit_file(self, file_path: str, instruction: str) -> None:
        """Edit a file based on instructions with enhanced animation"""
        path = Path(file_path)
        original_content = self.file_handler.read_file_content(path)

        if not original_content:
            return

        # Display edit request
        console.print(Panel(
            f"[bold]File:[/bold] {path.name}\n"
            f"[bold]Instruction:[/bold] {instruction}",
            title="✏️ Edit Request",
            border_style="yellow"
        ))

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

        console.print(f"\n[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]")
        console.print(f"[bold cyan]│[/bold cyan] [bold yellow]✏️ Editing {path.name}...[/bold yellow] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]\n")

        # Use enhanced progress bar for editing
        with LoadingAnimations.progress_bar("Processing edits") as progress:
            task = progress.add_task("Processing edits...", total=None)

            # Get contextual loading message
            with LoadingAnimations.simple_spinner(
                LoadingAnimations.get_contextual_message("edit")
            ) as spinner:
                # Get the edit without streaming
                new_content = self.get_response(messages).strip()
                new_content = self.file_handler.clean_ai_response(new_content)
                spinner.stop()

            progress.update(task, completed=True)

        # Create backup and save
        self.file_handler.create_backup(path, original_content)
        path.write_text(new_content)
        console.print(f"[bold green]✅ File updated:[/bold green] [bold white]{path}[/bold white]")

        # Show changes summary
        orig_lines = len(original_content.splitlines())
        new_lines = len(new_content.splitlines())
        console.print(f"[bold cyan]📊 Changes:[/bold cyan] [bold yellow]{orig_lines}[/bold yellow] → [bold green]{new_lines}[/bold green] lines")

    def system_assistant(self, question: str) -> None:
        """Enhanced system assistant with command execution"""
        system_info = self._get_system_info()
        system_prompt = self._build_system_prompt(question, system_info)

        messages = [{"role": "user", "content": system_prompt}]

        console.print(f"\n[bold cyan]╭─────────────────────────────────────────────────────────╮[/bold cyan]")
        console.print(f"[bold cyan]│[/bold cyan] [bold blue]🖥️ System Assistant[/bold blue] [bold cyan]│[/bold cyan]")
        console.print("[bold cyan]╰─────────────────────────────────────────────────────────╯[/bold cyan]")
        response = self._process_system_response(messages)

        # Parse and optionally execute commands
        commands = self.command_executor.parse_commands(response)
        self.command_executor.execute_with_confirmation(commands)
        console.print()

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _get_system_info(self) -> Dict[str, Any]:
        """Gather system information"""
        cwd = os.getcwd()
        try:
            files = subprocess.run(['ls', '-la'], capture_output=True, text=True).stdout
        except:
            files = "Could not list files"

        return {
            "info": {
                "OS": platform.system(),
                "Distribution": platform.platform(),
                "Python": platform.python_version(),
                "Architecture": platform.machine(),
                "Hostname": platform.node()
            },
            "cwd": cwd,
            "files": files
        }

    def _build_system_prompt(self, question: str, system_info: Dict[str, Any]) -> str:
        """Build the system assistant prompt"""
        return f"""You are an advanced AI system administrator for Ubuntu (Omakub). You can analyze questions and suggest both explanations AND executable commands.

System Information:
{system_info['info']}

Current Directory: {system_info['cwd']}
Directory Contents:
{system_info['files']}

CAPABILITIES:
1. **Service Management**: systemctl commands (start, stop, restart, status, enable, disable)
2. **Package Management**: apt commands (install, remove, update, upgrade, search)
3. **File Operations**: file/directory operations (ls, find, rm, cp, mv, chmod, chown)
4. **Execute Commands**: any safe Ubuntu command

USER QUESTION: {question}

RESPONSE FORMAT:
1. First, provide a brief explanation
2. If commands are needed, list them with this EXACT format:
    EXECUTE_COMMAND: command_here
    EXECUTE_COMMAND: another_command_here

SAFETY RULES:
- Always explain what commands do before suggesting them
- For destructive operations (rm, rmdir, etc.), include safety warnings
- For sudo commands, explain why sudo is needed
- For package installs, mention disk space if relevant

Provide helpful, specific advice for Ubuntu systems with actionable commands when appropriate."""

    def _process_system_response(self, messages: List[Dict[str, str]]) -> str:
        """Process system response and display it"""
        response_text = self.get_response(messages)

        # Print response, filtering out EXECUTE_COMMAND lines
        lines = response_text.split('\n')
        for line in lines:
            if not line.strip().startswith('EXECUTE_COMMAND:'):
                print(line)

        return response_text