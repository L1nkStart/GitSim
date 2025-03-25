"""
Interfaz de línea de comandos para el sistema de simulación Git.
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
        # Configuración del sistema y gestor de repositorios
        self.config = Config()
        self.repo_manager = RepositoryManager()
        
        # Diccionario de comandos disponibles
        self.commands: Dict[str, Command] = {
            'init': InitCommand(self.repo_manager),  # Comando para inicializar repositorio
            'add': AddCommand(self.repo_manager),    # Comando para añadir archivos
            'commit': CommitCommand(self.repo_manager),  # Comando para hacer commit
            'checkout': CheckoutCommand(self.repo_manager),  # Comando para cambiar de commit/branch
            'status': StatusCommand(self.repo_manager),  # Comando para ver estado
            'log': LogCommand(self.repo_manager),    # Comando para ver historial
            # Subcomandos para Pull Requests (PRs)
            'pr': {
                'create': PRCreateCommand(self.repo_manager),  # Crear PR
                'status': PRStatusCommand(self.repo_manager),  # Ver estado de PR
                'review': PRReviewCommand(self.repo_manager),  # Añadir revisor a PR
                'approve': PRApproveCommand(self.repo_manager),  # Aprobar PR
                'reject': PRRejectCommand(self.repo_manager),  # Rechazar PR
                'cancel': PRCancelCommand(self.repo_manager),  # Cancelar PR
                'list': PRListCommand(self.repo_manager),  # Listar PRs
                'next': PRNextCommand(self.repo_manager),  # Ver siguiente PR en cola
                'tag': PRTagCommand(self.repo_manager),  # Añadir etiqueta a PR
                'clear': PRClearCommand(self.repo_manager)  # Limpiar todos los PRs
            }
        }
    
    def execute(self, command: str, *args: str) -> str:
        """Ejecuta un comando git y devuelve el resultado como cadena."""
        # Verifica si el comando existe
        if command not in self.commands:
            return f"Error: Comando desconocido '{command}'"
        
        # Verifica si el comando está habilitado en la configuración
        if not self.config.is_command_enabled(command):
            return f"Error: Comando '{command}' está deshabilitado"
        
        # Manejo especial para subcomandos de PR
        if command == 'pr':
            if not args:
                return "Error: Se requiere subcomando para PR"
            subcommand = args[0]
            if subcommand not in self.commands['pr']:
                return f"Error: Subcomando de PR desconocido '{subcommand}'"
            return self.commands['pr'][subcommand].execute(*args[1:])
        
        # Ejecuta el comando normal
        try:
            return self.commands[command].execute(*args)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        """Muestra el menú de ayuda con todos los comandos disponibles."""
        help_text = ["Comandos permitidos:"]
        for name, cmd in self.commands.items():
            if self.config.is_command_enabled(name):
                if isinstance(cmd, dict):  # Manejo de subcomandos de PR
                    help_text.append(f"\n{name} subcomandos:")
                    for subname, subcmd in cmd.items():
                        help_text.append(f"  {subcmd.get_help()}")
                else:
                    help_text.append(cmd.get_help())
        return "\n".join(help_text)