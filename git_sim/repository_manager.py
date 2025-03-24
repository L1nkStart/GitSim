"""
Repository manager for handling multiple Git repositories.
"""
from typing import Dict, Optional
from .data_structures import LinkedList
from .repository import Repository

class RepositoryManager:
    def __init__(self):
        self.repositories = LinkedList()
        self.current_repository: Optional[Repository] = None
    
    def create_repository(self, name: str, path: str) -> Repository:
        """Create a new repository."""
        repo = Repository(name, path)
        self.repositories.append(repo)
        self.current_repository = repo
        return repo
    
    def switch_repository(self, name: str) -> None:
        """Switch to a different repository."""
        node = self.repositories.find(lambda r: r.name == name)
        if not node:
            raise ValueError(f"Repository '{name}' not found")
        self.current_repository = node.data
    
    def list_repositories(self) -> list[str]:
        """List all repositories."""
        return [repo.name for repo in self.repositories.to_list()]
    
    def delete_repository(self, name: str) -> None:
        """Delete a repository."""
        repo = next((r for r in self.repositories.to_list() if r.name == name), None)
        if not repo:
            raise ValueError(f"Repository '{name}' not found")
        
        self.repositories.remove(repo)
        if self.current_repository and self.current_repository.name == name:
            self.current_repository = None