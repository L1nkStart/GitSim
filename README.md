# Simulador de git en python hecho por:
-Daniel Laviera
-Eduardo Tovar
-Luis Leon

# Sistema de Simulación Git

Un sistema de simulación de Git basado en Python que implementa funcionalidades básicas de control de versiones utilizando diversas estructuras de datos.

## Características

### 1. Gestión de Repositorios
- Crear y gestionar múltiples repositorios
- Seguimiento de cambios en archivos e historial de commits
- Gestión y navegación de ramas
- Utiliza listas enlazadas para la organización de repositorios

### 2. Área de Staging (Basada en Pila)
- Agregar y rastrear archivos modificados
- Seguimiento del estado de archivos (Agregado, Modificado, Eliminado)
- Validación de checksum usando SHA-1
- Implementación basada en pila para operaciones LIFO

### 3. Historial de Commits (Lista Enlazada)
- Crear y rastrear commits
- Almacenar metadatos de commits:
  - Identificador hash SHA-1
  - Mensaje del commit
  - Información del autor
  - Marca de tiempo
  - Referencia al commit padre
  - Información de la rama
  - Archivos modificados

### 4. Sistema de Pull Requests (Basado en Cola)
- Crear y gestionar pull requests
- Implementación de cola FIFO
- Rastrear estado y metadatos de PR:
  - Identificador único
  - Título y descripción
  - Ramas de origen y destino
  - Autor y revisores
  - Archivos modificados
  - Etiquetas
  - Marcas de tiempo de creación y cierre

## Comandos

### Operaciones Básicas de Git

```bash
# Inicializar un nuevo repositorio
init <nombre> <ruta>

# Agregar archivo al área de staging
add <archivo>

# Crear un nuevo commit
commit -m "<mensaje>"

# Cambiar a un commit específico
checkout <id_commit>

# Mostrar estado del árbol de trabajo
status

# Mostrar historial de commits
log
```

### Gestión de Pull Requests

```bash
# Crear un nuevo pull request
pr create <título> <rama_origen> <rama_destino> <descripción>

# Mostrar estado del pull request
pr status <id_pr>

# Agregar un revisor
pr review <id_pr> <email_revisor>

# Aprobar un pull request
pr approve <id_pr>

# Rechazar un pull request
pr reject <id_pr>

# Cancelar un pull request
pr cancel <id_pr>

# Listar todos los pull requests
pr list

# Mostrar siguiente pull request en la cola
pr next

# Agregar etiqueta al pull request
pr tag <id_pr> <etiqueta>

# Limpiar todos los pull requests
pr clear
```

## Estructuras de Datos

### 1. Lista Enlazada
- Usada para gestionar repositorios
- Permite acceso y modificación secuencial
- Operaciones: agregar, eliminar, buscar

### 2. Pila
- Implementa el área de staging
- Operaciones LIFO (Último en Entrar, Primero en Salir)
- Operaciones: push, pop, peek, limpiar

### 3. Cola
- Gestiona pull requests
- Operaciones FIFO (Primero en Entrar, Primero en Salir)
- Operaciones: encolar, desencolar, peek, limpiar

### 4. Nodo
- Bloque básico de construcción para estructuras de datos
- Contiene datos y puntero al siguiente
- Usado en Lista Enlazada, Pila y Cola

## Configuración

El sistema utiliza un archivo de configuración JSON (`git_sim_config.json`) para gestionar la disponibilidad de comandos:

```json
{
  "enabled_commands": [
    "init",
    "add",
    "commit",
    "checkout",
    "status",
    "log",
    "pr"
  ]
}
```

Los comandos pueden ser habilitados o deshabilitados a través del sistema de configuración.

## Clases

### 1. Repository
- Clase principal para operaciones de repositorio
- Gestiona directorio de trabajo, área de staging y commits
- Maneja operaciones de ramas y pull requests

### 2. RepositoryManager
- Gestiona múltiples repositorios
- Proporciona cambio y listado de repositorios
- Usa Lista Enlazada para almacenamiento de repositorios

### 3. GitSimCLI
- Interfaz de línea de comandos
- Implementa el patrón Command para operaciones
- Maneja análisis y ejecución de comandos

### 4. Config
- Gestiona configuración de comandos
- Carga y guarda configuraciones
- Controla disponibilidad de comandos

## Ejemplo de Uso

```python
# Inicializar el CLI
py main.py

# Crear un nuevo repositorio
init mi-repo '/ruta/al/repo'

# Agregar un archivo
add 'ejemplo.txt'

# Crear un commit
commit -m 'Commit inicial'

# Crear una nueva rama y agregar cambios
checkout -b 'rama-caracteristica'
add nueva-caracteristica.txt'
commit -m 'Agregar nueva característica'

# Crear un pull request
pr create 'Nueva Característica' 'rama-caracteristica' main 'Agregando una nueva característica'

# Revisar y aprobar el pull request
pr review 'PR-1' 'revisor@ejemplo.com'
pr approve 'PR-1'
```

## Manejo de Errores

El sistema incluye manejo de errores completo:

- Validación de comandos inválidos
- Verificación de existencia de archivos
- Validación del estado del repositorio
- Validación del estado de pull requests
- Validación de existencia de ramas

## Detalles de Implementación

### 1. Patrón Command
- Cada operación está implementada como una clase Command
- Los comandos están registrados en el CLI
- Permite fácil adición de nuevos comandos
- Soporta habilitación/deshabilitación de comandos

### 2. Operaciones de Estructuras de Datos
- Lista Enlazada: recorrido O(n), agregar O(1)
- Pila: operaciones push/pop O(1)
- Cola: operaciones encolar/desencolar O(1)

### 3. Operaciones de Archivos
- Seguimiento de contenido de archivos
- Cálculo de checksum SHA-1
- Simulación de directorio de trabajo

### 4. Flujo de Pull Request
1. Crear PR con ramas de origen y destino
2. Agregar revisores
3. Proceso de revisión (aprobar/rechazar)
4. Seguimiento de estado
5. Etiquetado opcional

## Mejores Prácticas

1. Siempre crear mensajes de commit significativos
2. Revisar cambios antes de hacer commit
3. Usar títulos y descripciones descriptivos para PRs
4. Agregar revisores apropiados a los PRs
5. Usar etiquetas para categorización de PRs
6. Mantener PRs enfocados y manejables

