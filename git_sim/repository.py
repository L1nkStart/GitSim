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
        self.staging_stack = Stack()  # Stack of StagedFile objects
        self.commits: Dict[str, Commit] = {}
        self.current_branch = "main"
        self.branches: Dict[str, str] = {"main": None}  # branch_name -> commit_id
        self.head: Optional[str] = None  # current commit id
        self.working_directory: Dict[str, str] = {}  # filename -> content
        self.detached_head = False
        self.pull_requests = Queue()  # Queue of PullRequest objects
        self.pr_counter = 0  # Counter for generating PR IDs
        self.pr_map: Dict[str, PullRequest] = {}  # ID -> PullRequest mapping
    
    def calculate_file_hash(self, content: str) -> str:
        """Calcula el hash SHA-1 del contenido de un archivo."""
        return hashlib.sha1(content.encode()).hexdigest()
    
    def list_branches(self) -> List[str]:
        """List all branches in the repository."""
        return list(self.branches.keys())
    
    def create_pull_request(self, title: str, description: str, source_branch: str, target_branch: str, author: str) -> str:
        """Crea un nuevo pull request."""
        # Validación de ramas
        if source_branch not in self.branches:
            raise ValueError(f"Rama origen '{source_branch}' no existe")
        if target_branch not in self.branches:
            raise ValueError(f"Rama destino '{target_branch}' no existe")
        
        # Get commits that are in source branch but not in target branch
        source_commits = self._get_branch_commits(source_branch)
        target_commits = self._get_branch_commits(target_branch)
        unique_commits = [c for c in source_commits if c not in target_commits]
        
        if not unique_commits:
            raise ValueError("No hay cambios para fusionar")
        
        # Get modified files from these commits
        modified_files = set()
        for commit_id in unique_commits:
            modified_files.update(self.commits[commit_id].changes.keys())
        
        # Generate PR ID
        self.pr_counter += 1
        pr_id = f"PR-{self.pr_counter}"
        
        # Create pull request
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
        
        # Add to queue and mapping
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
        
        # Clear any previous version of this file from the stack
        temp_stack = Stack()
        while not self.staging_stack.is_empty():
            item = self.staging_stack.pop()
            if item.path != filename:
                temp_stack.push(item)
        
        # Restore other files and add the new one
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        self.staging_stack.push(staged_file)
    
    def commit(self, message: str, author_email: str) -> str:
        """Crea un nuevo commit con los contenidos del área de staging."""
        if self.staging_stack.is_empty():
            raise ValueError("Nada para commitear")
        
        # Collect all staged files
        changes: Dict[str, str] = {}
        temp_stack = Stack()
        while not self.staging_stack.is_empty():
            staged_file = self.staging_stack.pop()
            changes[staged_file.path] = staged_file.content
            temp_stack.push(staged_file)
        
        # Restore the staging stack (though we'll clear it after commit)
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        
        # Create commit ID from content and metadata
        timestamp = datetime.now()
        content_str = f"{message}{timestamp}{self.head}{author_email}"
        for filename, content in sorted(changes.items()):
            content_str += f"{filename}{content}"
        commit_id = hashlib.sha1(content_str.encode()).hexdigest()
        
        # Create new commit
        new_commit = Commit(
            id=commit_id,
            message=message,
            timestamp=timestamp,
            author_email=author_email,
            parent_id=self.head,
            changes=changes,
            branch=self.current_branch
        )
        
        # Update repository state
        self.commits[commit_id] = new_commit
        self.head = commit_id
        if not self.detached_head:
            self.branches[self.current_branch] = commit_id
        self.staging_stack.clear()
        
        return commit_id
    
    def branch(self, name: str) -> None:
        """Create a new branch pointing to the current commit."""
        if name in self.branches:
            raise ValueError(f"Branch '{name}' already exists")
        self.branches[name] = self.head
    
    def checkout(self, branch_name: str) -> None:
        """Switch to a different branch."""
        if branch_name not in self.branches:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        
        # Limpiar el área de staging antes de cambiar de rama
        if not self.staging_stack.is_empty():
            raise ValueError("Cannot switch branches with uncommitted changes")
        
        self.current_branch = branch_name
        self.head = self.branches[branch_name]
        self.detached_head = False
        
        # Update working directory to match the branch's state
        if self.head and self.head in self.commits:
            self.working_directory = dict(self.commits[self.head].changes)
        else:
            self.working_directory.clear()
        self.staging_stack.clear()
    
    def checkout_commit(self, commit_id: str) -> None:
        """Cambia a un commit específico."""
        if commit_id not in self.commits:
            raise ValueError(f"Commit '{commit_id}' not found")
        
        # Limpiar el área de staging antes de cambiar a un commit específico
        if not self.staging_stack.is_empty():
            raise ValueError("Cannot checkout commit with uncommitted changes")
        
        self.head = commit_id
        self.detached_head = True
        self.working_directory = dict(self.commits[commit_id].changes)
        self.staging_stack.clear()
    
    def status(self) -> List[FileStatus]:
        """Obtiene el estado de los archivos en el directorio de trabajo y área de staging."""
        status_list = []
        staged_files = set()
        
        # Process staged files
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
        
        # Restore staging stack
        while not temp_stack.is_empty():
            self.staging_stack.push(temp_stack.pop())
        
        # Check working directory for unstaged changes
        for filename, content in self.working_directory.items():
            if filename not in staged_files:
                status_list.append(FileStatus(filename, "new", content))
        
        return status_list
    
    def get_commit_history(self) -> List[Commit]:
        """Devuelve el historial de commits para la rama actual."""
        history = []
        current = self.head
        while current:
            commit = self.commits[current]
            history.append(commit)
            current = commit.parent_id
        return history