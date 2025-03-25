"""
Implementación principal del repositorio para el sistema de simulación Git.
"""
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Set
from .data_structures import (
    Commit, FileStatus, Stack, StagedFile,
    Queue, PullRequest
)

class Repository:
    def __init__(self, name: str, path: str):
        # Propiedades básicas del repositorio
        self.name = name
        self.path = path
        
        # Estructuras de datos para manejo de archivos y commits
        self.staging_stack = Stack()  # Pila para archivos en staging
        self.commits: Dict[str, Commit] = {}  # Diccionario de commits
        self.current_branch = "main"  # Rama actual
        self.branches: Dict[str, str] = {"main": None}  # Ramas y sus últimos commits
        self.head: Optional[str] = None  # Commit actual (HEAD)
        self.working_directory: Dict[str, str] = {}  # Directorio de trabajo
        
        # Estado especial para HEAD desvinculado
        self.detached_head = False
        
        # Estructuras para manejo de Pull Requests
        self.pull_requests = Queue()  # Cola de PRs
        self.pr_counter = 0  # Contador de PRs
        self.pr_map: Dict[str, PullRequest] = {}  # Mapa de PRs por ID
    
    def calculate_file_hash(self, content: str) -> str:
        """Calcula el hash SHA-1 del contenido de un archivo."""
        return hashlib.sha1(content.encode()).hexdigest()
    
    def create_pull_request(self, title: str, description: str, source_branch: str, target_branch: str, author: str) -> str:
        """Crea un nuevo pull request."""
        # Validación de ramas
        if source_branch not in self.branches:
            raise ValueError(f"Rama origen '{source_branch}' no existe")
        if target_branch not in self.branches:
            raise ValueError(f"Rama destino '{target_branch}' no existe")
        
        # Obtiene commits únicos entre las ramas
        source_commits = self._get_branch_commits(source_branch)
        target_commits = self._get_branch_commits(target_branch)
        unique_commits = [c for c in source_commits if c not in target_commits]
        
        if not unique_commits:
            raise ValueError("No hay cambios para fusionar")
        
        # Obtiene archivos modificados
        modified_files = set()
        for commit_id in unique_commits:
            modified_files.update(self.commits[commit_id].changes.keys())
        
        # Crea el PR
        self.pr_counter += 1
        pr_id = f"PR-{self.pr_counter}"
        
        pr = PullRequest(
            id=pr_id,
            title=title,
            description=description,
            author=author,
            created_at=datetime.now(),
            source_branch=source_branch,
            target_branch=target_branch,
            commit_ids=unique_commits,
            modified_files=modified_files,
            reviewers=set()
        )
        
        # Añade el PR a las estructuras de datos
        self.pull_requests.enqueue(pr)
        self.pr_map[pr_id] = pr
        
        return pr_id
    
    def _get_branch_commits(self, branch_name: str) -> List[str]:
        """Obtiene todos los IDs de commit en una rama."""
        commits = []
        current = self.branches[branch_name]
        while current:
            commits.append(current)
            current = self.commits[current].parent_id
        return commits
    
    def get_pull_request(self, pr_id: str) -> Optional[PullRequest]:
        """Obtiene un pull request por ID."""
        return self.pr_map.get(pr_id)
    
    def review_pull_request(self, pr_id: str, reviewer: str) -> None:
        """Añade un revisor a un pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' no encontrado")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' no está abierto")
        pr.reviewers.add(reviewer)
    
    def approve_pull_request(self, pr_id: str) -> None:
        """Aprueba un pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' no encontrado")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' no está abierto")
        pr.status = "approved"
        pr.closed_at = datetime.now()
    
    def reject_pull_request(self, pr_id: str) -> None:
        """Rechaza un pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' no encontrado")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' no está abierto")
        pr.status = "rejected"
        pr.closed_at = datetime.now()
    
    def cancel_pull_request(self, pr_id: str) -> None:
        """Cancela un pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' no encontrado")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' no está abierto")
        pr.status = "cancelled"
        pr.closed_at = datetime.now()
    
    def list_pull_requests(self) -> List[PullRequest]:
        """Lista todos los pull requests."""
        result = []
        temp_queue = Queue()
        
        # Vacía la cola principal temporalmente
        while not self.pull_requests.is_empty():
            pr = self.pull_requests.dequeue()
            result.append(pr)
            temp_queue.enqueue(pr)
        
        # Restaura la cola original
        while not temp_queue.is_empty():
            self.pull_requests.enqueue(temp_queue.dequeue())
        
        return result
    
    def get_next_pull_request(self) -> Optional[PullRequest]:
        """Obtiene el siguiente pull request en la cola."""
        return self.pull_requests.peek()
    
    def tag_pull_request(self, pr_id: str, tag: str) -> None:
        """Añade una etiqueta a un pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' no encontrado")
        pr.tags.add(tag)
    
    def clear_pull_requests(self) -> None:
        """Limpia todos los pull requests."""
        self.pull_requests.clear()
        self.pr_map.clear()
    
    def add(self, filename: str, content: str) -> None:
        """Añade un archivo al área de staging usando una pila."""
        self.working_directory[filename] = content
        file_hash = self.calculate_file_hash(content)
        
        # Determina el estado del archivo
        status = 'A'  # Añadido por defecto
        last_commit_id = None
        
        if self.head:
            current_commit = self.commits[self.head]
            if filename in current_commit.changes:
                old_content = current_commit.changes[filename]
                if old_content != content:
                    status = 'M'  # Modificado
                last_commit_id = self.head
        
        staged_file = StagedFile(
            path=filename,
            content=content,
            status=status,
            checksum=file_hash,
            last_commit_id=last_commit_id
        )
        
        # Manejo de la pila para evitar duplicados
        temp_stack = Stack()
        while not self.staging_stack.is_empty():
            item = self.staging_stack.pop()
            if item.path != filename:
                temp_stack.push(item)
        
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        self.staging_stack.push(staged_file)
    
    def commit(self, message: str, author_email: str) -> str:
        """Crea un nuevo commit con los contenidos del área de staging."""
        if self.staging_stack.is_empty():
            raise ValueError("Nada para commitear")
        
        # Recoge los cambios del staging
        changes: Dict[str, str] = {}
        temp_stack = Stack()
        while not self.staging_stack.is_empty():
            staged_file = self.staging_stack.pop()
            changes[staged_file.path] = staged_file.content
            temp_stack.push(staged_file)
        
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        
        # Genera un ID único para el commit
        timestamp = datetime.now()
        content_str = f"{message}{timestamp}{self.head}{author_email}"
        for filename, content in sorted(changes.items()):
            content_str += f"{filename}{content}"
        commit_id = hashlib.sha1(content_str.encode()).hexdigest()
        
        # Crea el nuevo commit
        new_commit = Commit(
            id=commit_id,
            message=message,
            timestamp=timestamp,
            author_email=author_email,
            parent_id=self.head,
            changes=changes,
            branch=self.current_branch
        )
        
        # Actualiza las estructuras de datos
        self.commits[commit_id] = new_commit
        self.head = commit_id
        if not self.detached_head:
            self.branches[self.current_branch] = commit_id
        self.staging_stack.clear()
        
        return commit_id
    
    def checkout_commit(self, commit_id: str) -> None:
        """Cambia a un commit específico."""
        if commit_id not in self.commits:
            raise ValueError(f"Commit '{commit_id}' no encontrado")
        
        self.head = commit_id
        self.detached_head = True
        self.working_directory = dict(self.commits[commit_id].changes)
        self.staging_stack.clear()
    
    def status(self) -> List[FileStatus]:
        """Obtiene el estado de los archivos en el directorio de trabajo y área de staging."""
        status_list = []
        staged_files = set()
        
        # Revisa archivos en staging
        temp_stack = Stack()
        while not self.staging_stack.is_empty():
            staged_file = self.staging_stack.pop()
            staged_files.add(staged_file.path)
            status_list.append(FileStatus(
                path=staged_file.path,
                status=staged_file.status,
                content=staged_file.content
            ))
            temp_stack.push(staged_file)
        
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        
        # Revisa archivos en working directory no en staging
        for filename, content in self.working_directory.items():
            if filename not in staged_files:
                status_list.append(FileStatus(filename, "new", content))
        
        return status_list
    
    def branch(self, name: str) -> None:
        """Crea una nueva rama apuntando al commit actual."""
        if name in self.branches:
            raise ValueError(f"Rama '{name}' ya existe")
        self.branches[name] = self.head
    
    def checkout(self, branch_name: str) -> None:
        """Cambia a una rama diferente."""
        if branch_name not in self.branches:
            raise ValueError(f"Rama '{branch_name}' no existe")
        self.current_branch = branch_name
        self.head = self.branches[branch_name]
        self.detached_head = False
        
        if self.head and self.head in self.commits:
            self.working_directory = dict(self.commits[self.head].changes)
        else:
            self.working_directory.clear()
        self.staging_stack.clear()
    
    def get_commit_history(self) -> List[Commit]:
        """Devuelve el historial de commits para la rama actual."""
        history = []
        current = self.head
        while current:
            commit = self.commits[current]
            history.append(commit)
            current = commit.parent_id
        return history