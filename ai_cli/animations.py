"""Loading animations and progress indicators"""
import random
import time
from typing import List, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text

console = Console()


class LoadingAnimations:
    """Collection of loading animations for different contexts"""

    # Thinking messages that rotate
    THINKING_MESSAGES = [
        "🤔 Thinking...",
        "🧠 Processing...",
        "💭 Contemplating...",
        "📚 Analyzing...",
        "🔍 Examining...",
        "⚡ Computing...",
        "🎯 Focusing...",
        "✨ Generating response...",
    ]

    # Spinners available in rich
    SPINNERS = [
        "dots",
        "dots2",
        "dots3",
        "dots8",
        "line",
        "growVertical",
        "growHorizontal",
        "noise",
        "bounce",
        "boxing",
        "arc",
        "circle",
        "squareCorners",
        "circleQuarters",
        "circleHalves",
        "star",
        "moon",
    ]

    @classmethod
    def get_random_thinking_message(cls) -> str:
        """Get a random thinking message"""
        return random.choice(cls.THINKING_MESSAGES)

    @classmethod
    def get_contextual_message(cls, context: str) -> str:
        """Get a contextual loading message based on the operation"""
        messages = {
            "chat": ["💬 Crafting response...", "🤖 Processing your message...", "💡 Generating ideas...", "🧠 Thinking deeply..."],
            "file": ["📄 Analyzing file structure...", "🔍 Examining code patterns...", "📊 Processing content...", "🔬 Deep analysis..."],
            "edit": ["✏️ Applying changes...", "🔧 Modifying code...", "⚙️ Refactoring...", "🎨 Crafting edits..."],
            "system": ["🖥️ Checking system...", "⚡ Preparing commands...", "🔧 Analyzing configuration...", "🛠️ System analysis..."],
        }

        context_messages = messages.get(context, cls.THINKING_MESSAGES)
        return random.choice(context_messages)

    @classmethod
    def simple_spinner(cls, message: Optional[str] = None, spinner_type: str = "dots") -> Console.status: # type: ignore
        """Create a simple spinner animation"""
        if message is None:
            message = cls.get_random_thinking_message()

        return console.status(f"[bold cyan]{message}[/bold cyan]", spinner=spinner_type)

    @classmethod
    def cycling_spinner(cls, messages: Optional[List[str]] = None, cycle_time: float = 2.0):
        """Create a spinner that cycles through different messages"""
        if messages is None:
            messages = cls.THINKING_MESSAGES

        class CyclingStatus:
            def __init__(self, messages, cycle_time):
                self.messages = messages
                self.cycle_time = cycle_time
                self.current_index = 0

            def __enter__(self):
                self.status = console.status(
                    f"[bold cyan]{self.messages[0]}[/bold cyan]",
                    spinner="dots"
                )
                self.status.__enter__()
                return self

            def __exit__(self, exc_type, exc_val, exc_tb):
                self.status.__exit__(exc_type, exc_val, exc_tb)

            def update_message(self):
                """Cycle to next message"""
                self.current_index = (self.current_index + 1) % len(self.messages)
                self.status.update(f"[bold cyan]{self.messages[self.current_index]}[/bold cyan]")

            def stop(self):
                """Stop the spinner"""
                self.status.stop()

        return CyclingStatus(messages, cycle_time)

    @classmethod
    def progress_bar(cls, task_description: str = "Processing", total: Optional[int] = None):
        """Create a progress bar for longer operations"""
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn() if total else "",
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%") if total else "",
            console=console,
            transient=True,
        )

    @classmethod
    def multi_step_progress(cls, steps: List[str]):
        """Create a multi-step progress indicator"""
        table = Table(show_header=False, show_edge=False, box=None)

        for i, step in enumerate(steps, 1):
            status = "✓" if i < len(steps) else "⏳" if i == len(steps) else "⏸"
            color = "green" if status == "✓" else "yellow" if status == "⏳" else "dim"
            table.add_row(
                f"[{color}]{status}[/{color}]",
                f"[{color}]{step}[/{color}]"
            )

        return Panel(table, title="Progress", border_style="cyan")

    @classmethod
    def fun_animation(cls, duration: float = 3.0):
        """A fun loading animation for special occasions"""
        frames = [
            "⠋ Loading magic",
            "⠙ Loading magic.",
            "⠹ Loading magic..",
            "⠸ Loading magic...",
            "⠼ Loading magic... ✨",
            "⠴ Loading magic.. ✨",
            "⠦ Loading magic. ✨",
            "⠧ Loading magic ✨",
            "⠇ Loading magic ✨",
            "⠏ Loading magic ✨",
        ]

        with Live(frames[0], refresh_per_second=4, console=console) as live:
            start_time = time.time()
            frame_index = 0

            while time.time() - start_time < duration:
                live.update(f"[bold cyan]{frames[frame_index]}[/bold cyan]")
                frame_index = (frame_index + 1) % len(frames)
                time.sleep(0.25)


def show_thinking_animation():
    """Context manager for showing thinking animation during AI operations"""
    return LoadingAnimations.simple_spinner()