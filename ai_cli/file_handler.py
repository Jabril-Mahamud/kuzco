"""
AI Assistant CLI - File Handler Module
Handles both file content processing and AI-powered file operations
"""
import re
from pathlib import Path
from typing import Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import ollama

from ai_cli.config import Config
from ai_cli.errors import ErrorHandler, handle_errors
from ai_cli.animations import show_thinking_animation

console = Console()


class FileHandler:
    """Handles file operations and content processing"""

    def __init__(self, model: str, config: Config):
        """Initialize file handler"""
        self.model = model
        self.config = config

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

            # Create edit prompt
            edit_prompt = self.create_edit_prompt(file_path, original_content, instruction)

            console.print(f"[bold yellow]✏️  Editing {file_path}...[/bold yellow]")
            console.print(f"[dim]Instruction: {instruction}[/dim]")

            # Show thinking animation
            with show_thinking_animation():
                response = ollama.chat(
                    model=self.model,
                    messages=[{"role": "user", "content": edit_prompt}]
                )

            # Clean the AI response
            cleaned_content = self.clean_ai_response(response['message']['content'])

            # Validate the cleaned content
            is_valid, validation_msg = self.validate_cleaned_content(
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

    @staticmethod
    def clean_ai_response(content: str) -> str:
        """Remove all AI artifacts from response - thoughts, markdown, explanations"""

        # Remove thinking tags and their content
        # Handles various formats: <thinking>, <thoughts>, <reasoning>, etc.
        thinking_patterns = [
            r'<thinking>.*?</thinking>',
            r'<thoughts>.*?</thoughts>',
            r'<reasoning>.*?</reasoning>',
            r'<reflection>.*?</reflection>',
            r'<planning>.*?</planning>',
            r'<analysis>.*?</analysis>',
        ]

        for pattern in thinking_patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove markdown code blocks with language specifiers
        # Matches ```python, ```javascript, etc.
        content = re.sub(r'```[\w]*\n(.*?)```', r'\1', content, flags=re.DOTALL)

        # Remove standalone code blocks
        content = re.sub(r'```\n?(.*?)```', r'\1', content, flags=re.DOTALL)

        # Remove common AI explanation prefixes/suffixes
        explanation_patterns = [
            r'^Here\'s the .*?:\n+',  # "Here's the modified file:"
            r'^Here is the .*?:\n+',
            r'^Modified content:\n+',
            r'^Updated file:\n+',
            r'^Fixed version:\n+',
            r'^Edited content:\n+',
            r'^\s*---+\s*\n',  # Separator lines
            r'\n\s*---+\s*$',
            r'^The following.*?:\n+',
            r'^Below is.*?:\n+',
        ]

        for pattern in explanation_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)

        # Remove trailing explanations (often after the actual content)
        # Look for patterns like "This code..." or "The above..."
        trailing_explanation = re.search(
            r'\n\n(This\s|The\s+above|I\'ve\s|Note\s|Notice|Explanation:|Changes:)',
            content,
            re.IGNORECASE
        )
        if trailing_explanation:
            content = content[:trailing_explanation.start()]

        # Clean up excessive whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)  # Max 2 newlines
        content = content.strip()

        return content

    @staticmethod
    def validate_cleaned_content(original: str, cleaned: str, file_type: str) -> Tuple[bool, str]:
        """Validate that cleaned content is reasonable"""

        # Check if content was overly stripped
        if not cleaned or len(cleaned) < 10:
            return False, "Content appears to be empty after cleaning"

        # Check if we accidentally removed too much (> 90% reduction is suspicious)
        if len(cleaned) < len(original) * 0.1:
            return False, "Content reduced by more than 90% - may be over-cleaned"

        # Basic syntax validation for code files
        code_extensions = {'.py', '.js', '.java', '.cpp', '.c', '.go', '.rs'}
        if file_type in code_extensions:
            # Check for basic code structure
            if file_type == '.py' and 'def ' not in cleaned and 'class ' not in cleaned and 'import ' not in cleaned:
                if len(cleaned) > 50:  # Only warn for non-trivial files
                    console.print("[yellow]⚠️  Warning: No Python keywords found in cleaned content[/yellow]")

        return True, "Content validated successfully"

    @staticmethod
    def extract_code_from_response(response: str, file_type: str) -> str:
        """Extract only the code/content from AI response, handling various formats"""

        # First, try to find content between specific markers
        content_markers = [
            (r'Modified content:\s*\n(.*)', r'\1'),
            (r'```[\w]*\n(.*?)```', r'\1'),  # Code blocks
            (r'<content>(.*?)</content>', r'\1'),  # XML-style tags
            (r'<file>(.*?)</file>', r'\1'),
        ]

        for pattern, replacement in content_markers:
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # If no markers found, clean the entire response
        return FileHandler.clean_ai_response(response)

    @staticmethod
    def create_edit_prompt(file_path: str, content: str, instruction: str) -> str:
        """Create a more explicit edit prompt that minimizes artifacts"""

        return f"""You are a code editor. Your task is to modify the file according to the instruction.

CRITICAL RULES:
1. Return ONLY the complete modified file content
2. Do NOT include any explanations, thoughts, or markdown formatting
3. Do NOT wrap the code in backticks or code blocks
4. Do NOT add prefixes like "Here's the modified file:"
5. Start directly with the actual file content

File: {file_path}
Current content:
---START FILE---
{content}
---END FILE---

Instruction: {instruction}

Return the complete modified file content below (no formatting, no explanations):
"""
