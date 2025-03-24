"""
Command-line interface for the Git simulation system.
"""
from typing import Dict, Optional
from .repository_manager import RepositoryManager
from .commands import (
    Command, InitCommand, AddCommand, CommitCommand,
    CheckoutCommand, StatusCommand, LogCommand,
    PRCreateCommand, PRStatusCommand, PRReviewCommand,
    PRApproveCommand, PRRejectCommand, PRCancelCommand,
    PRListCommand, PRNextCommand, PRTagCommand, PRClearCommand
)
from .config import Config

class GitSimCLI:
    def __init__(self):
        self.config = Config()
        self.repo_manager = RepositoryManager()
        self.commands: Dict[str, Command] = {
            'init': InitCommand(self.repo_manager),
            'add': AddCommand(self.repo_manager),
            'commit': CommitCommand(self.repo_manager),
            'checkout': CheckoutCommand(self.repo_manager),
            'status': StatusCommand(self.repo_manager),
            'log': LogCommand(self.repo_manager),
            'pr': {
                'create': PRCreateCommand(self.repo_manager),
                'status': PRStatusCommand(self.repo_manager),
                'review': PRReviewCommand(self.repo_manager),
                'approve': PRApproveCommand(self.repo_manager),
                'reject': PRRejectCommand(self.repo_manager),
                'cancel': PRCancelCommand(self.repo_manager),
                'list': PRListCommand(self.repo_manager),
                'next': PRNextCommand(self.repo_manager),
                'tag': PRTagCommand(self.repo_manager),
                'clear': PRClearCommand(self.repo_manager)
            }
        }
    
    def execute(self, command: str, *args: str) -> str:
        """Execute a git command."""
        if command not in self.commands:
            return f"Error: Unknown command '{command}'"
        
        if not self.config.is_command_enabled(command):
            return f"Error: Command '{command}' is disabled"
        
        # Handle PR subcommands
        if command == 'pr':
            if not args:
                return "Error: PR subcommand required"
            subcommand = args[0]
            if subcommand not in self.commands['pr']:
                return f"Error: Unknown PR subcommand '{subcommand}'"
            return self.commands['pr'][subcommand].execute(*args[1:])
        
        try:
            return self.commands[command].execute(*args)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        """Menu de ayuda para los comandos."""
        help_text = ["Comandos permitidos:"]
        for name, cmd in self.commands.items():
            if self.config.is_command_enabled(name):
                if isinstance(cmd, dict):  # PR subcommands
                    help_text.append(f"\n{name} subcommands:")
                    for subname, subcmd in cmd.items():
                        help_text.append(f"  {subcmd.get_help()}")
                else:
                    help_text.append(cmd.get_help())
        return "\n".join(help_text)