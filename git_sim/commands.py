"""
Implementación del patrón Command para operaciones Git.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from .repository_manager import RepositoryManager

# Clase abstracta base para todos los comandos
class Command(ABC):
    @abstractmethod
    def execute(self, *args) -> str:
        """Método abstracto para ejecutar el comando."""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Método abstracto para obtener texto de ayuda."""
        pass

# Comando para inicializar un repositorio
class InitCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Argumentos requeridos: <nombre> <ruta>"
        nombre, ruta = args[0], args[1]
        self.repo_manager.create_repository(nombre, ruta)
        return f"Repositorio Git vacío inicializado '{nombre}' en '{ruta}'"
    
    def get_help(self) -> str:
        return "git init <nombre> <ruta> - Crea un nuevo repositorio"

# Comando para añadir archivos al área de staging
class AddCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Argumento requerido: <archivo>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        nombre_archivo = args[0]
        try:
            with open(nombre_archivo, 'r') as f:
                contenido = f.read()
            repo.add(nombre_archivo, contenido)
            return f"Añadido {nombre_archivo} al área de staging"
        except FileNotFoundError:
            return f"Error: Archivo '{nombre_archivo}' no encontrado"
    
    def get_help(self) -> str:
        return "git add <archivo> - Añade archivo al área de staging"

# Comando para crear un nuevo commit
class CommitCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2 or args[0] != '-m':
            return 'Error: Formato requerido: commit -m "<mensaje>"'
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        mensaje = args[1]
        try:
            commit_id = repo.commit(mensaje, "user@example.com")
            return f"Commit creado {commit_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return 'git commit -m "<mensaje>" - Crea un nuevo commit'

class BranchCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        # Si no hay argumentos, listar las ramas
        if not args:
            branches = repo.list_branches()
            current = repo.current_branch
            output = []
            for branch in branches:
                prefix = "* " if branch == current else "  "
                output.append(f"{prefix}{branch}")
            return "\n".join(output) if output else "No branches exist yet"
        
        # Crear nueva rama
        branch_name = args[0]
        try:
            repo.branch(branch_name)
            return f"Created branch '{branch_name}'"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git branch [<branch-name>] - List or create branches"

class CheckoutCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <branch-name> or <commit-id> or -b <new-branch>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        # Crear y cambiar a nueva rama
        if args[0] == '-b':
            if len(args) < 2:
                return "Error: Branch name required"
            branch_name = args[1]
            try:
                repo.branch(branch_name)
                repo.checkout(branch_name)
                return f"Switched to a new branch '{branch_name}'"
            except ValueError as e:
                return f"Error: {str(e)}"
        
        # Cambiar a rama o commit existente
        target = args[0]
        try:
            # Intentar cambiar a una rama primero
            if target in repo.branches:
                repo.checkout(target)
                return f"Switched to branch '{target}'"
            # Si no es una rama, intentar cambiar a un commit
            repo.checkout_commit(target)
            return f"HEAD is now at {target}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git checkout [-b] <branch-name> | <commit-id> - Switch branches or restore working tree files"

# Comando para ver el estado del repositorio
class StatusCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        status_list = repo.status()
        output = [f"On branch {repo.current_branch}"]
        
        if not status_list:
            output.append("Nothing to commit, working tree clean")
        else:
            output.append("\nChanges not staged for commit:")
            for status in status_list:
                output.append(f"  {status.status}: {status.path}")
        
        return "\n".join(output)
    
    def get_help(self) -> str:
        return "git status - Muestra el estado del árbol de trabajo"

# Comando para ver el historial de commits
class LogCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        historial = repo.get_commit_history()
        if not historial:
            return "Aún no hay commits"
        
        salida = []
        for commit in historial:
            salida.extend([
                f"Commit: {commit.id}",
                f"Autor: {commit.author_email}",
                f"Fecha: {commit.timestamp}",
                f"Rama: {commit.branch}",
                f"\n    {commit.message}\n",
                "-" * 40
            ])
        return "\n".join(salida)
    
    def get_help(self) -> str:
        return "git log - Muestra el historial de commits"

# Comandos para Pull Requests (PRs):

# Comando para crear un PR
class PRCreateCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 4:
            return "Error: Argumentos requeridos: <título> <rama_origen> <rama_destino> <descripción>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        titulo, rama_origen, rama_destino, *partes_desc = args
        descripcion = " ".join(partes_desc)
        
        try:
            pr_id = repo.create_pull_request(
                title=titulo,
                description=descripcion,
                source_branch=rama_origen,
                target_branch=rama_destino,
                author="user@example.com"
            )
            return f"Pull request creado {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr create <título> <rama_origen> <rama_destino> <descripción> - Crea un nuevo pull request"

# Comando para ver estado de un PR
class PRStatusCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Argumento requerido: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id = args[0]
        pr = repo.get_pull_request(pr_id)
        if not pr:
            return f"Error: Pull request '{pr_id}' no encontrado"
        
        return (
            f"Pull Request: {pr.id}\n"
            f"Título: {pr.title}\n"
            f"Estado: {pr.status}\n"
            f"Autor: {pr.author}\n"
            f"Creado: {pr.created_at}\n"
            f"Origen: {pr.source_branch}\n"
            f"Destino: {pr.target_branch}\n"
            f"Revisores: {', '.join(pr.reviewers) if pr.reviewers else 'Ninguno'}\n"
            f"Etiquetas: {', '.join(pr.tags) if pr.tags else 'Ninguna'}\n"
            f"Archivos modificados: {', '.join(pr.modified_files)}\n"
            f"Descripción:\n{pr.description}"
        )
    
    def get_help(self) -> str:
        return "git pr status <pr_id> - Muestra el estado de un pull request"

# Comando para añadir revisor a un PR
class PRReviewCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Argumentos requeridos: <pr_id> <email_revisor>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id, revisor = args
        try:
            repo.review_pull_request(pr_id, revisor)
            return f"Revisor {revisor} añadido al pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr review <pr_id> <email_revisor> - Añade un revisor a un pull request"

# Comando para aprobar un PR
class PRApproveCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Argumento requerido: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id = args[0]
        try:
            repo.approve_pull_request(pr_id)
            return f"Pull request {pr_id} aprobado"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr approve <pr_id> - Aprueba un pull request"

# Comando para rechazar un PR
class PRRejectCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Argumento requerido: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id = args[0]
        try:
            repo.reject_pull_request(pr_id)
            return f"Pull request {pr_id} rechazado"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr reject <pr_id> - Rechaza un pull request"

# Comando para cancelar un PR
class PRCancelCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Argumento requerido: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id = args[0]
        try:
            repo.cancel_pull_request(pr_id)
            return f"Pull request {pr_id} cancelado"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr cancel <pr_id> - Cancela un pull request"

# Comando para listar todos los PRs
class PRListCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        prs = repo.list_pull_requests()
        if not prs:
            return "No se encontraron pull requests"
        
        salida = ["Pull Requests:"]
        for pr in prs:
            salida.append(
                f"  {pr.id}: {pr.title} ({pr.status})\n"
                f"    Origen: {pr.source_branch} → Destino: {pr.target_branch}"
            )
        return "\n".join(salida)
    
    def get_help(self) -> str:
        return "git pr list - Lista todos los pull requests"

# Comando para ver el siguiente PR en cola
class PRNextCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr = repo.get_next_pull_request()
        if not pr:
            return "No hay pull requests en cola"
        
        return (
            f"Siguiente Pull Request:\n"
            f"  ID: {pr.id}\n"
            f"  Título: {pr.title}\n"
            f"  Estado: {pr.status}\n"
            f"  Origen: {pr.source_branch} → Destino: {pr.target_branch}"
        )
    
    def get_help(self) -> str:
        return "git pr next - Muestra el siguiente pull request en cola"

# Comando para etiquetar un PR
class PRTagCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Argumentos requeridos: <pr_id> <etiqueta>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        pr_id, etiqueta = args
        try:
            repo.tag_pull_request(pr_id, etiqueta)
            return f"Etiqueta '{etiqueta}' añadida al pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr tag <pr_id> <etiqueta> - Añade una etiqueta a un pull request"

# Comando para limpiar todos los PRs
class PRClearCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No hay repositorio seleccionado"
        
        repo.clear_pull_requests()
        return "Todos los pull requests han sido eliminados"
    
    def get_help(self) -> str:
        return "git pr clear - Elimina todos los pull requests"