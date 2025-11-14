"""Module linker - links modules together, resolving dependencies."""

from typing import List, Dict, Optional
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.module_system.src.module import Module
from components.module_system.src.module_status import ModuleStatus
from components.module_system.src.module_loader import ModuleLoader
from components.module_system.src.module_registry import ModuleRegistry
from components.parser.src.ast_nodes import (
    ImportDeclaration, ExportNamedDeclaration,
    ExportDefaultDeclaration, ExportAllDeclaration
)


class ModuleLinkError(Exception):
    """Raised when module linking fails."""
    pass


class CircularDependencyError(ModuleLinkError):
    """Raised when circular dependency is detected."""
    pass


class ModuleLinker:
    """
    Links modules together, resolving import/export dependencies.

    Responsibilities:
    - Parse module AST
    - Extract import/export declarations
    - Load dependencies recursively
    - Build dependency graph
    - Detect circular dependencies
    - Compile modules to bytecode
    - Manage module lifecycle
    """

    def __init__(self, loader: ModuleLoader, registry: Optional[ModuleRegistry] = None):
        """
        Initialize module linker.

        Args:
            loader: ModuleLoader instance for loading modules
            registry: ModuleRegistry for caching (default: global singleton)
        """
        self.loader = loader
        self.registry = registry or ModuleRegistry()
        self.linking_stack: List[str] = []  # For cycle detection

    def link(self, module: Module) -> None:
        """
        Link module and all dependencies.

        This is the main entry point for linking a module.

        Args:
            module: Module to link

        Raises:
            ModuleLinkError: If linking fails

        Process:
        1. Parse module AST
        2. Extract imports/exports
        3. Load dependencies recursively
        4. Compile to bytecode
        5. Update status to LINKED

        Note:
            Circular dependencies are allowed and detected.
            They will be handled by TDZ (Temporal Dead Zone) during evaluation.
        """
        if module.status == ModuleStatus.LINKED:
            # Already linked - skip
            return

        if module.status == ModuleStatus.LINKING:
            # Currently being linked - circular dependency detected
            # This is allowed in ES Modules (TDZ handles it during evaluation)
            return

        # Mark as linking
        module.status = ModuleStatus.LINKING

        # Add to linking stack for cycle tracking
        self.linking_stack.append(module.url)

        try:
            # Step 1: Parse AST
            self._parse_module(module)

            # Step 2: Extract imports/exports
            self._extract_imports_exports(module)

            # Step 3: Load dependencies recursively
            self._load_dependencies(module)

            # Step 4: Compile to bytecode
            self._compile_module(module)

            # Step 5: Update status
            module.status = ModuleStatus.LINKED

        except Exception as e:
            module.status = ModuleStatus.ERROR
            module.error = e
            raise ModuleLinkError(f"Failed to link module {module.url}: {e}") from e

        finally:
            # Remove from linking stack
            self.linking_stack.pop()

    def _parse_module(self, module: Module):
        """
        Parse module source to AST.

        Args:
            module: Module to parse
        """
        try:
            module.ast = Parse(module.source)
        except Exception as e:
            raise ModuleLinkError(f"Parse error in {module.url}: {e}") from e

    def _extract_imports_exports(self, module: Module):
        """
        Extract import/export declarations from AST.

        Args:
            module: Module with parsed AST

        Populates:
            module.imports - List of ImportDeclaration nodes
            module.exports - List of Export* nodes
        """
        module.imports = []
        module.exports = []

        for statement in module.ast.body:
            if isinstance(statement, ImportDeclaration):
                module.imports.append(statement)
            elif isinstance(statement, (ExportNamedDeclaration, ExportDefaultDeclaration, ExportAllDeclaration)):
                module.exports.append(statement)

    def _load_dependencies(self, module: Module):
        """
        Load all dependencies (imported modules) recursively.

        Args:
            module: Module with imports extracted

        Populates:
            module.dependencies - List of dependency Module objects
        """
        for import_decl in module.imports:
            # Get module specifier (source URL)
            specifier = import_decl.source.value

            # Resolve specifier to absolute URL
            dep_url = self.loader.resolve_url(specifier, referrer=module.url)
            dep_url = self.loader.normalize_url(dep_url)

            # Check if already loaded (cache)
            dep_module = self.registry.get(dep_url)

            if dep_module is None:
                # Load dependency
                dep_module = self.loader.load(specifier, referrer=module.url)

                # Register in cache
                self.registry.register(dep_module)

                # Link dependency recursively
                # Note: link() will detect and handle circular dependencies
                self.link(dep_module)
            elif dep_module.status == ModuleStatus.LINKED:
                # Already linked - good to use
                pass
            elif dep_module.status == ModuleStatus.LINKING:
                # Circular dependency detected
                # This is allowed in ES Modules
                # The module is being linked higher up in the call stack
                # We still add it to dependencies, but don't try to link it
                pass
            elif dep_module.status == ModuleStatus.UNLINKED:
                # Found in cache but not yet linked - link it now
                self.link(dep_module)

            # Add to dependencies (even for circular dependencies)
            module.dependencies.append(dep_module)

    def _compile_module(self, module: Module):
        """
        Compile module AST to bytecode.

        Args:
            module: Module with parsed AST

        Note:
            Currently skipped as bytecode compiler doesn't support
            ES Modules (import/export) yet. Will be implemented in
            Phase 2.7.4: Module Bytecode Compilation.
        """
        # TODO(Phase 2.7.4): Implement module bytecode compilation
        # For now, we skip compilation as the bytecode compiler
        # doesn't support import/export statements yet
        module.bytecode = None

    def get_dependency_graph(self, module: Module) -> Dict[str, List[str]]:
        """
        Get dependency graph for module.

        Args:
            module: Root module

        Returns:
            Dict mapping module URL to list of dependency URLs

        Example:
            {
                '/app/main.js': ['/app/math.js', '/app/utils.js'],
                '/app/math.js': [],
                '/app/utils.js': ['/app/helpers.js'],
                '/app/helpers.js': []
            }
        """
        graph = {}
        visited = set()

        def visit(mod: Module):
            if mod.url in visited:
                return
            visited.add(mod.url)

            graph[mod.url] = [dep.url for dep in mod.dependencies]

            for dep in mod.dependencies:
                visit(dep)

        visit(module)
        return graph

    def topological_sort(self, module: Module) -> List[Module]:
        """
        Get topological order of modules for evaluation.

        Args:
            module: Root module

        Returns:
            List of modules in evaluation order (dependencies first)

        Raises:
            CircularDependencyError: If strongly connected cycles exist

        Note: This uses DFS post-order traversal to get topological order.
        Circular dependencies are handled with TDZ during evaluation.
        """
        order = []
        visited = set()
        visiting = set()

        def visit(mod: Module):
            if mod.url in visited:
                return

            if mod.url in visiting:
                # Circular dependency - for now, skip (TDZ will handle)
                return

            visiting.add(mod.url)

            for dep in mod.dependencies:
                visit(dep)

            visiting.remove(mod.url)
            visited.add(mod.url)
            order.append(mod)

        visit(module)
        return order
