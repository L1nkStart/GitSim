"""
Estructuras de datos centrales para el sistema de simulación Git.
"""
from typing import Any, Optional, List, Dict, Set
from dataclasses import dataclass
from datetime import datetime

# Nodo básico para estructuras enlazadas
class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional[Node] = None

# Implementación de cola (FIFO)
class Queue:
    def __init__(self):
        self.front: Optional[Node] = None  # Frente de la cola
        self.rear: Optional[Node] = None   # Final de la cola
        self.size = 0
    
    def enqueue(self, data: Any) -> None:
        """Añade un elemento al final de la cola."""
        new_node = Node(data)
        if self.rear is None:
            self.front = new_node
            self.rear = new_node
        else:
            self.rear.next = new_node
            self.rear = new_node
        self.size += 1
    
    def dequeue(self) -> Optional[Any]:
        """Elimina y devuelve el elemento del frente de la cola."""
        if self.front is None:
            return None
        
        data = self.front.data
        self.front = self.front.next
        self.size -= 1
        
        if self.front is None:
            self.rear = None
        
        return data
    
    def peek(self) -> Optional[Any]:
        """Mira el elemento del frente sin eliminarlo."""
        return self.front.data if self.front else None
    
    def is_empty(self) -> bool:
        """Verifica si la cola está vacía."""
        return self.size == 0
    
    def clear(self) -> None:
        """Limpia todos los elementos de la cola."""
        self.front = None
        self.rear = None
        self.size = 0

# Implementación de pila (LIFO)
class Stack:
    def __init__(self):
        self.top: Optional[Node] = None  # Tope de la pila
        self.size = 0
    
    def push(self, data: Any) -> None:
        """Apila un elemento."""
        new_node = Node(data)
        new_node.next = self.top
        self.top = new_node
        self.size += 1
    
    def pop(self) -> Optional[Any]:
        """Desapila un elemento."""
        if not self.top:
            return None
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data
    
    def peek(self) -> Optional[Any]:
        """Mira el elemento del tope sin eliminarlo."""
        return self.top.data if self.top else None
    
    def is_empty(self) -> bool:
        """Verifica si la pila está vacía."""
        return self.size == 0
    
    def clear(self) -> None:
        """Limpia todos los elementos de la pila."""
        self.top = None
        self.size = 0

# Implementación de lista enlazada
class LinkedList:
    def __init__(self):
        self.head: Optional[Node] = None
    
    def append(self, data: Any) -> None:
        """Añade un elemento al final de la lista."""
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
    
    def remove(self, data: Any) -> bool:
        """Elimina un elemento de la lista."""
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
        """Busca un elemento en la lista."""
        current = self.head
        while current:
            if current.data == data:
                return current
            current = current.next
        return None
    
    def to_list(self) -> List[Any]:
        """Convierte la lista enlazada a una lista Python."""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

# Clases de datos para el sistema Git:

@dataclass
class PullRequest:
    """Representa un pull request."""
    id: str  # Identificador único
    title: str  # Título del PR
    description: str  # Descripción
    author: str  # Autor
    created_at: datetime  # Fecha creación
    source_branch: str  # Rama origen
    target_branch: str  # Rama destino
    commit_ids: List[str]  # IDs de commits asociados
    modified_files: Set[str]  # Archivos modificados
    reviewers: Set[str]  # Revisores
    closed_at: Optional[datetime] = None  # Fecha cierre
    merged_at: Optional[datetime] = None  # Fecha fusión
    status: str = "open"  # Estados: open, approved, rejected, cancelled, merged
    tags: Set[str] = None  # Etiquetas
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = set()

@dataclass
class StagedFile:
    """Representa un archivo en el área de staging."""
    path: str  # Ruta del archivo
    content: str  # Contenido
    status: str  # 'A' para añadido, 'M' para modificado, 'D' para eliminado
    checksum: str  # Hash SHA-1 del contenido
    last_commit_id: Optional[str]  # Referencia al último commit donde se modificó

@dataclass
class Commit:
    """Representa un commit en el historial."""
    id: str  # Hash SHA-1
    message: str  # Mensaje del commit
    timestamp: datetime  # Fecha y hora
    author_email: str  # Email del autor
    parent_id: Optional[str]  # ID del commit padre
    changes: Dict[str, str]  # Diccionario de cambios: nombre_archivo -> contenido
    branch: str  # Rama a la que pertenece

@dataclass
class FileStatus:
    """Representa el estado de un archivo."""
    path: str  # Ruta del archivo
    status: str  # 'modified', 'new', 'deleted'
    content: str  # Contenido