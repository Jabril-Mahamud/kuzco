"""
Tests for configuration module
"""
import pytest
import os
from unittest.mock import patch
from ai_cli.config import Config


class TestConfig:
    """Test configuration loading and environment variables"""

    def test_default_values(self):
        """Test that default values are loaded correctly"""
        assert Config.MAX_PREVIEW_SIZE == 2000
        assert Config.COMMAND_TIMEOUT == 30
        assert Config.DEFAULT_THEME == "monokai"
        assert Config.SAFE_MODE is True
        assert Config.CREATE_BACKUPS is True

    def test_environment_variables(self):
        """Test that environment variables override defaults"""
        with patch.dict(os.environ, {
            'MAX_PREVIEW_SIZE': '5000',
            'SAFE_MODE': 'false',
            'CREATE_BACKUPS': 'false'
        }):
            # Reload config to pick up environment variables
            from importlib import reload
            import ai_cli.config
            reload(ai_cli.config)

            assert ai_cli.config.Config.MAX_PREVIEW_SIZE == 5000
            assert ai_cli.config.Config.SAFE_MODE is False
            assert ai_cli.config.Config.CREATE_BACKUPS is False

    def test_exit_commands_property(self):
        """Test that exit commands are loaded from environment"""
        with patch.dict(os.environ, {'EXIT_COMMANDS': 'quit,bye,exit'}):
            from importlib import reload
            import ai_cli.config
            reload(ai_cli.config)

            assert 'quit' in ai_cli.config.Config.EXIT_COMMANDS
            assert 'bye' in ai_cli.config.Config.EXIT_COMMANDS
            assert 'exit' in ai_cli.config.Config.EXIT_COMMANDS

    def test_sudo_prefixes_property(self):
        """Test that sudo prefixes are loaded from environment"""
        with patch.dict(os.environ, {'SUDO_PREFIXES': 'sudo,su,doas'}):
            from importlib import reload
            import ai_cli.config
            reload(ai_cli.config)

            assert 'sudo' in ai_cli.config.Config.SUDO_PREFIXES
            assert 'su' in ai_cli.config.Config.SUDO_PREFIXES
            assert 'doas' in ai_cli.config.Config.SUDO_PREFIXES
