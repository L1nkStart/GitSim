"""
Configuration management for Git simulation system.
"""
import json
from typing import Dict, Set

class Config:
    def __init__(self, config_file: str = "git_sim_config.json"):
        self.config_file = config_file
        self.enabled_commands: Set[str] = set()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.enabled_commands = set(config.get('enabled_commands', []))
        except FileNotFoundError:
            # Default configuration with all commands enabled
            self.enabled_commands = {
                'init', 'add', 'commit', 'checkout', 'status', 'log',
                'pr'  # PR commands are handled as subcommands
            }
            self.save_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        config = {
            'enabled_commands': list(self.enabled_commands)
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def is_command_enabled(self, command: str) -> bool:
        """Check if a command is enabled."""
        return command in self.enabled_commands
    
    def enable_command(self, command: str) -> None:
        """Enable a command."""
        self.enabled_commands.add(command)
        self.save_config()
    
    def disable_command(self, command: str) -> None:
        """Disable a command."""
        self.enabled_commands.discard(command)
        self.save_config()