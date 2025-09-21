"""Configuration and constants for AI CLI Assistant"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List
import random
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Config:
    """Configuration and constants"""
    # Load from environment with defaults
    MAX_PREVIEW_SIZE: int = int(os.getenv('MAX_PREVIEW_SIZE', '2000'))
    COMMAND_TIMEOUT: int = int(os.getenv('COMMAND_TIMEOUT', '30'))
    DEFAULT_THEME: str = os.getenv('DEFAULT_THEME', 'monokai')
    DEFAULT_MODEL: str = os.getenv('DEFAULT_MODEL', '')

    # Safe mode settings
    SAFE_MODE: bool = os.getenv('SAFE_MODE', 'true').lower() == 'true'
    CREATE_BACKUPS: bool = os.getenv('CREATE_BACKUPS', 'true').lower() == 'true'

    # Animation settings
    SPINNER_STYLE: str = os.getenv('SPINNER_STYLE', 'dots')
    ANIMATION_SPEED: float = float(os.getenv('ANIMATION_SPEED', '0.1'))

    # Exit commands for chat mode (from env or default)
    @property
    def EXIT_COMMANDS(self) -> List[str]:
        exit_commands = os.getenv('EXIT_COMMANDS', 'exit,quit,bye,goodbye')
        return [cmd.strip() for cmd in exit_commands.split(',')]

    # Safety prefixes that require warnings (from env or default)
    @property
    def SUDO_PREFIXES(self) -> List[str]:
        sudo_prefixes = os.getenv('SUDO_PREFIXES', 'sudo,su')
        return [prefix.strip() for prefix in sudo_prefixes.split(',')]

    # Fun loading messages for animations
    THINKING_MESSAGES = [
        "🤔 Thinking...",
        "🧠 Processing...",
        "💭 Contemplating...",
        "🎯 Analyzing...",
        "🔍 Examining...",
        "📊 Computing...",
        "⚡ Working on it...",
        "🎨 Crafting response...",
        "🚀 Generating answer...",
        "✨ Creating magic...",
    ]

    @staticmethod
    def get_random_thinking_message() -> str:
        """Get a random thinking message for loading animations"""
        return random.choice(Config.THINKING_MESSAGES)