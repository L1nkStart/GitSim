"""
Command pattern implementation for Git operations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from .repository_manager import RepositoryManager

class Command(ABC):
    @abstractmethod
    def execute(self, *args) -> str:
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        pass

class InitCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Required arguments: <name> <path>"
        name, path = args[0], args[1]
        self.repo_manager.create_repository(name, path)
        return f"Initialized empty Git repository '{name}' at '{path}'"
    
    def get_help(self) -> str:
        return "git init <name> <path> - Create a new repository"

class AddCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <file>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        filename = args[0]
        try:
            with open(filename, 'r') as f:
                content = f.read()
            repo.add(filename, content)
            return f"Added {filename} to staging area"
        except FileNotFoundError:
            return f"Error: File '{filename}' not found"
    
    def get_help(self) -> str:
        return "git add <file> - Add file to staging area"

class CommitCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2 or args[0] != '-m':
            return 'Error: Required format: commit -m "<message>"'
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        message = args[1]
        try:
            commit_id = repo.commit(message, "user@example.com")  # In a real system, this would come from config
            return f"Created commit {commit_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return 'git commit -m "<message>" - Create a new commit'

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
            return "Error: No repository selected"
        
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

class StatusCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
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
        return "git status - Show working tree status"

class LogCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        history = repo.get_commit_history()
        if not history:
            return "No commits yet"
        
        output = []
        for commit in history:
            output.extend([
                f"Commit: {commit.id}",
                f"Author: {commit.author_email}",
                f"Date: {commit.timestamp}",
                f"Branch: {commit.branch}",
                f"\n    {commit.message}\n",
                "-" * 40
            ])
        return "\n".join(output)
    
    def get_help(self) -> str:
        return "git log - Show commit history"

class PRCreateCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 4:
            return "Error: Required arguments: <title> <source_branch> <target_branch> <description>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        title, source_branch, target_branch, *desc_parts = args
        description = " ".join(desc_parts)
        
        try:
            pr_id = repo.create_pull_request(
                title=title,
                description=description,
                source_branch=source_branch,
                target_branch=target_branch,
                author="user@example.com"  # In a real system, this would come from config
            )
            return f"Created pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr create <title> <source_branch> <target_branch> <description> - Create a new pull request"

class PRStatusCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id = args[0]
        pr = repo.get_pull_request(pr_id)
        if not pr:
            return f"Error: Pull request '{pr_id}' not found"
        
        return (
            f"Pull Request: {pr.id}\n"
            f"Title: {pr.title}\n"
            f"Status: {pr.status}\n"
            f"Author: {pr.author}\n"
            f"Created: {pr.created_at}\n"
            f"Source: {pr.source_branch}\n"
            f"Target: {pr.target_branch}\n"
            f"Reviewers: {', '.join(pr.reviewers) if pr.reviewers else 'None'}\n"
            f"Tags: {', '.join(pr.tags) if pr.tags else 'None'}\n"
            f"Modified Files: {', '.join(pr.modified_files)}\n"
            f"Description:\n{pr.description}"
        )
    
    def get_help(self) -> str:
        return "git pr status <pr_id> - Show pull request status"

class PRReviewCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Required arguments: <pr_id> <reviewer_email>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id, reviewer = args
        try:
            repo.review_pull_request(pr_id, reviewer)
            return f"Added reviewer {reviewer} to pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr review <pr_id> <reviewer_email> - Add a reviewer to a pull request"

class PRApproveCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id = args[0]
        try:
            repo.approve_pull_request(pr_id)
            return f"Approved pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr approve <pr_id> - Approve a pull request"

class PRRejectCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id = args[0]
        try:
            repo.reject_pull_request(pr_id)
            return f"Rejected pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr reject <pr_id> - Reject a pull request"

class PRCancelCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if not args:
            return "Error: Required argument: <pr_id>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id = args[0]
        try:
            repo.cancel_pull_request(pr_id)
            return f"Cancelled pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr cancel <pr_id> - Cancel a pull request"

class PRListCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        prs = repo.list_pull_requests()
        if not prs:
            return "No pull requests found"
        
        output = ["Pull Requests:"]
        for pr in prs:
            output.append(
                f"  {pr.id}: {pr.title} ({pr.status})\n"
                f"    Source: {pr.source_branch} → Target: {pr.target_branch}"
            )
        return "\n".join(output)
    
    def get_help(self) -> str:
        return "git pr list - List all pull requests"

class PRNextCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr = repo.get_next_pull_request()
        if not pr:
            return "No pull requests in queue"
        
        return (
            f"Next Pull Request:\n"
            f"  ID: {pr.id}\n"
            f"  Title: {pr.title}\n"
            f"  Status: {pr.status}\n"
            f"  Source: {pr.source_branch} → Target: {pr.target_branch}"
        )
    
    def get_help(self) -> str:
        return "git pr next - Show the next pull request in the queue"

class PRTagCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        if len(args) < 2:
            return "Error: Required arguments: <pr_id> <tag>"
        
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        pr_id, tag = args
        try:
            repo.tag_pull_request(pr_id, tag)
            return f"Added tag '{tag}' to pull request {pr_id}"
        except ValueError as e:
            return f"Error: {str(e)}"
    
    def get_help(self) -> str:
        return "git pr tag <pr_id> <tag> - Add a tag to a pull request"

class PRClearCommand(Command):
    def __init__(self, repo_manager: RepositoryManager):
        self.repo_manager = repo_manager
    
    def execute(self, *args) -> str:
        repo = self.repo_manager.current_repository
        if not repo:
            return "Error: No repository selected"
        
        repo.clear_pull_requests()
        return "Cleared all pull requests"
    
    def get_help(self) -> str:
        return "git pr clear - Clear all pull requests"