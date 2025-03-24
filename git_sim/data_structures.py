"""
Core data structures for the Git simulation system.
"""
from typing import Any, Optional, List, Dict, Set
from dataclasses import dataclass
from datetime import datetime

class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional[Node] = None

class Queue:
    def __init__(self):
        self.front: Optional[Node] = None
        self.rear: Optional[Node] = None
        self.size = 0
    
    def enqueue(self, data: Any) -> None:
        """Add an item to the queue."""
        new_node = Node(data)
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1
    
    def dequeue(self) -> Optional[Any]:
        """Remove and return the front item from the queue."""
        if self.front is None:
            return None
        
        data = self.front.data
        self.front = self.front.next
        self.size -= 1
        
        if self.front is None:
            self.rear = None
        
        return data
    
    def peek(self) -> Optional[Any]:
        """Look at the front item without removing it."""
        return self.front.data if self.front else None
    
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        return self.size == 0
    
    def clear(self) -> None:
        """Clear all items from the queue."""
        self.front = None
        self.rear = None
        self.size = 0

class Stack:
    def __init__(self):
        self.top: Optional[Node] = None
        self.size = 0
    
    def push(self, data: Any) -> None:
        """Push an item onto the stack."""
        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node
        self.size += 1
    
    def pop(self) -> Optional[Any]:
        """Pop an item from the stack."""
        if not self.top:
            return None
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data
    
    def peek(self) -> Optional[Any]:
        """Look at the top item without removing it."""
        return self.top.data if self.top else None
    
    def is_empty(self) -> bool:
        """Check if the stack is empty."""
        return self.size == 0
    
    def clear(self) -> None:
        """Clear all items from the stack."""
        self.top = None
        self.size = 0

class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
    
    def append(self, data: Any) -> None:
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def remove(self, data: Any) -> bool:
        if not self.head:
            return False
        
        if self.head.data == data:
            self.head = self.head.next
            return True
        
        current = self.head
        while current.next:
            if current.next.data == data:
                current.next = current.next.next
                return True
            current = current.next
        return False
    
    def find(self, data: Any) -> Optional[Node]:
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next
        return None
    
    def to_list(self) -> List[Any]:
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

@dataclass
class PullRequest:
    """Represents a pull request."""
    id: str  # Unique identifier
    title: str
    description: str
    author: str
    created_at: datetime
    source_branch: str
    target_branch: str
    commit_ids: List[str]  # List of associated commit IDs
    modified_files: Set[str]
    reviewers: Set[str]
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    status: str = "open"  # open, approved, rejected, cancelled, merged
    tags: Set[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()

@dataclass
class StagedFile:
    """Represents a file in the staging area."""
    path: str
    content: str
    status: str  # 'A' for added, 'M' for modified, 'D' for deleted
    checksum: str  # SHA-1 hash of the file content
    last_commit_id: Optional[str]  # Reference to the last commit where this file was modified

@dataclass
class Commit:
    id: str  # SHA-1 hash
    message: str
    timestamp: datetime
    author_email: str
    parent_id: Optional[str]
    changes: Dict[str, str]  # filename -> content
    branch: str

@dataclass
class FileStatus:
    path: str
    status: str  # 'modified', 'new', 'deleted'
    content: str