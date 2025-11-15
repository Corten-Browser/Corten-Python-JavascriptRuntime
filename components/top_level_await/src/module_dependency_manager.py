"""
ModuleDependencyManager - Manages module dependencies with top-level await
Implements FR-ES24-068: Proper module dependency handling with TLA
"""
from typing import List, Dict, Set
from collections import defaultdict, deque


class ModuleDependencyManager:
    """
    Manages module dependencies with top-level await
    Implements FR-ES24-068: Proper module dependency handling with TLA
    """

    def __init__(self):
        """Initialize dependency manager"""
        self.dependencies: Dict[str, List[str]] = defaultdict(list)
        self.reverse_dependencies: Dict[str, List[str]] = defaultdict(list)

    def add_dependency(self, importer: str, importee: str) -> None:
        """
        Add module dependency

        Args:
            importer: Importing module ID (depends on importee)
            importee: Imported module ID (dependency of importer)
        """
        # Add dependency only if not already present (idempotent)
        if importee not in self.dependencies[importer]:
            self.dependencies[importer].append(importee)
            self.reverse_dependencies[importee].append(importer)

    def get_evaluation_order(self, root_module: str) -> List[str]:
        """
        Get topologically sorted evaluation order

        Args:
            root_module: Root module ID

        Returns:
            Module IDs in evaluation order (dependencies before dependents)
        """
        # Build dependency graph for root and all its dependencies
        visited = set()
        graph = {}
        in_degree = defaultdict(int)

        def build_graph(module_id):
            """Build graph starting from module_id"""
            if module_id in visited:
                return
            visited.add(module_id)

            # Get dependencies for this module
            deps = self.dependencies.get(module_id, [])
            graph[module_id] = deps

            # Initialize in-degree
            if module_id not in in_degree:
                in_degree[module_id] = 0

            # Process dependencies
            for dep in deps:
                in_degree[dep] = in_degree.get(dep, 0)
                in_degree[module_id] += 1
                build_graph(dep)

        # Build graph from root
        build_graph(root_module)

        # Topological sort using Kahn's algorithm
        result = []
        queue = deque()

        # Find all nodes with in-degree 0
        for node in graph:
            if in_degree[node] == 0:
                queue.append(node)

        while queue:
            node = queue.popleft()
            result.append(node)

            # Reduce in-degree for dependents
            for dependent in self.reverse_dependencies.get(node, []):
                if dependent in graph:  # Only consider nodes in our subgraph
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # If result doesn't include all nodes, there's a cycle
        # But we still return what we have (cycle detection is separate)
        if len(result) < len(graph):
            # Add remaining nodes
            for node in graph:
                if node not in result:
                    result.append(node)

        return result

    def detect_cycles(self) -> List[List[str]]:
        """
        Detect cyclic dependencies

        Returns:
            List of cycles (each cycle is a list of module IDs)
        """
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node, current_path):
            """DFS to detect cycles"""
            visited.add(node)
            rec_stack.add(node)
            current_path.append(node)

            # Visit all dependencies
            for dep in self.dependencies.get(node, []):
                if dep not in visited:
                    if dfs(dep, current_path):
                        return True
                elif dep in rec_stack:
                    # Found a cycle
                    cycle_start = current_path.index(dep)
                    cycle = current_path[cycle_start:] + [dep]
                    if cycle not in cycles:
                        cycles.append(cycle)
                    return True

            current_path.pop()
            rec_stack.remove(node)
            return False

        # Check all nodes
        for node in list(self.dependencies.keys()):
            if node not in visited:
                dfs(node, [])

        return cycles
