"""
Main repository implementation for the Git simulation system.
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
        """Calculate SHA-1 hash of file content."""
        return hashlib.sha1(content.encode()).hexdigest()
    
    def create_pull_request(self, title: str, description: str, source_branch: str, target_branch: str, author: str) -> str:
        """Create a new pull request."""
        if source_branch not in self.branches:
            raise ValueError(f"Source branch '{source_branch}' does not exist")
        if target_branch not in self.branches:
            raise ValueError(f"Target branch '{target_branch}' does not exist")
        
        # Get commits that are in source branch but not in target branch
        source_commits = self._get_branch_commits(source_branch)
        target_commits = self._get_branch_commits(target_branch)
        unique_commits = [c for c in source_commits if c not in target_commits]
        
        if not unique_commits:
            raise ValueError("No changes to merge")
        
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
        """Get all commit IDs in a branch."""
        commits = []
        current = self.branches[branch_name]
        while current:
            commits.append(current)
            current = self.commits[current].parent_id
        return commits
    
    def get_pull_request(self, pr_id: str) -> Optional[PullRequest]:
        """Get a pull request by ID."""
        return self.pr_map.get(pr_id)
    
    def review_pull_request(self, pr_id: str, reviewer: str) -> None:
        """Add a reviewer to a pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' not found")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' is not open")
        pr.reviewers.add(reviewer)
    
    def approve_pull_request(self, pr_id: str) -> None:
        """Approve a pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' not found")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' is not open")
        pr.status = "approved"
        pr.closed_at = datetime.now()
    
    def reject_pull_request(self, pr_id: str) -> None:
        """Reject a pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' not found")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' is not open")
        pr.status = "rejected"
        pr.closed_at = datetime.now()
    
    def cancel_pull_request(self, pr_id: str) -> None:
        """Cancel a pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' not found")
        if pr.status != "open":
            raise ValueError(f"Pull request '{pr_id}' is not open")
        pr.status = "cancelled"
        pr.closed_at = datetime.now()
    
    def list_pull_requests(self) -> List[PullRequest]:
        """List all pull requests."""
        result = []
        temp_queue = Queue()
        
        while not self.pull_requests.is_empty():
            pr = self.pull_requests.dequeue()
            result.append(pr)
            temp_queue.enqueue(pr)
        
        # Restore queue
        while not temp_queue.is_empty():
            self.pull_requests.enqueue(temp_queue.dequeue())
        
        return result
    
    def get_next_pull_request(self) -> Optional[PullRequest]:
        """Get the next pull request in the queue."""
        return self.pull_requests.peek()
    
    def tag_pull_request(self, pr_id: str, tag: str) -> None:
        """Add a tag to a pull request."""
        pr = self.get_pull_request(pr_id)
        if not pr:
            raise ValueError(f"Pull request '{pr_id}' not found")
        pr.tags.add(tag)
    
    def clear_pull_requests(self) -> None:
        """Clear all pull requests."""
        self.pull_requests.clear()
        self.pr_map.clear()
    
    def add(self, filename: str, content: str) -> None:
        """Add a file to the staging area using a stack."""
        self.working_directory[filename] = content
        file_hash = self.calculate_file_hash(content)
        
        # Determine file status
        status = 'A'  # Added by default
        last_commit_id = None
        
        if self.head:
            current_commit = self.commits[self.head]
            if filename in current_commit.changes:
                old_content = current_commit.changes[filename]
                if old_content != content:
                    status = 'M'  # Modified
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
        """Create a new commit with the current staging area contents."""
        if self.staging_stack.is_empty():
            raise ValueError("Nothing to commit")
        
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
    
    def checkout_commit(self, commit_id: str) -> None:
        """Checkout a specific commit."""
        if commit_id not in self.commits:
            raise ValueError(f"Commit '{commit_id}' not found")
        
        self.head = commit_id
        self.detached_head = True
        self.working_directory = dict(self.commits[commit_id].changes)
        self.staging_stack.clear()
    
    def status(self) -> List[FileStatus]:
        """Get the status of files in the working directory and staging area."""
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
    
    def branch(self, name: str) -> None:
        """Create a new branch pointing to the current commit."""
        if name in self.branches:
            raise ValueError(f"Branch '{name}' already exists")
        self.branches[name] = self.head
    
    def checkout(self, branch_name: str) -> None:
        """Switch to a different branch."""
        if branch_name not in self.branches:
            raise ValueError(f"Branch '{branch_name}' does not exist")
        self.current_branch = branch_name
        self.head = self.branches[branch_name]
        self.detached_head = False
        
        # Update working directory to match the branch's state
        if self.head and self.head in self.commits:
            self.working_directory = dict(self.commits[self.head].changes)
        else:
            self.working_directory.clear()
        self.staging_stack.clear()
    
    def get_commit_history(self) -> List[Commit]:
        """Return the commit history for the current branch."""
        history = []
        current = self.head
        while current:
            commit = self.commits[current]
            history.append(commit)
            current = commit.parent_id
        return history