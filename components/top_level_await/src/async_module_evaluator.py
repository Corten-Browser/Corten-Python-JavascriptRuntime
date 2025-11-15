"""
AsyncModuleEvaluator - Evaluates modules with async dependencies
Implements FR-ES24-067: Async module evaluation order
"""
from dataclasses import dataclass
from typing import Dict, List, Set, Any
from .top_level_await_manager import Promise


@dataclass
class DependencyGraph:
    """Module dependency graph"""
    nodes: Dict[str, Any]  # Module ID -> Module
    edges: Dict[str, List[str]]  # Module ID -> List of dependency IDs
    evaluation_order: List[str]  # Topologically sorted module IDs


class AsyncModuleEvaluator:
    """
    Evaluates modules with async dependencies
    Implements FR-ES24-067: Async module evaluation order
    """

    def __init__(self):
        """Initialize async module evaluator"""
        self.evaluated_modules: Set[str] = set()

    def evaluate(self, module) -> Promise:
        """
        Evaluate module with async dependency resolution

        Args:
            module: Module to evaluate

        Returns:
            Promise that resolves when evaluation complete
        """
        # Build dependency graph
        graph = self.resolve_dependency_graph(module)

        # Evaluate in topological order
        def executor(resolve, reject):
            try:
                # Evaluate dependencies first
                for module_id in graph.evaluation_order:
                    if module_id not in self.evaluated_modules:
                        mod = graph.nodes[module_id]
                        if hasattr(mod, 'evaluate') and callable(mod.evaluate):
                            mod.evaluate()
                        self.evaluated_modules.add(module_id)

                resolve(None)
            except Exception as e:
                reject(e)

        return Promise(executor)

    def resolve_dependency_graph(self, module) -> DependencyGraph:
        """
        Build dependency graph for async evaluation order

        Args:
            module: Root module

        Returns:
            Module dependency graph with topological ordering
        """
        nodes = {}
        edges = {}
        visited = set()

        def visit(mod):
            """Visit module and its dependencies"""
            if mod.id in visited:
                return
            visited.add(mod.id)

            nodes[mod.id] = mod
            edges[mod.id] = []

            # Get dependencies
            deps = getattr(mod, 'dependencies', [])
            for dep in deps:
                edges[mod.id].append(dep.id)
                visit(dep)

        # Build graph
        visit(module)

        # Topological sort
        evaluation_order = self._topological_sort(nodes, edges)

        return DependencyGraph(
            nodes=nodes,
            edges=edges,
            evaluation_order=evaluation_order
        )

    def _topological_sort(self, nodes: Dict[str, Any], edges: Dict[str, List[str]]) -> List[str]:
        """
        Perform topological sort on dependency graph

        Args:
            nodes: Module nodes
            edges: Dependency edges

        Returns:
            Topologically sorted list of module IDs
        """
        # Calculate in-degrees
        in_degree = {node_id: 0 for node_id in nodes}
        for node_id in edges:
            for dep_id in edges[node_id]:
                if dep_id in in_degree:
                    in_degree[dep_id] = in_degree.get(dep_id, 0)

        # Update in-degrees based on edges
        for node_id in edges:
            for dep_id in edges[node_id]:
                in_degree[node_id] += 1

        # Find nodes with no incoming edges
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort to ensure deterministic order
            queue.sort()
            node_id = queue.pop(0)
            result.append(node_id)

            # Reduce in-degree for nodes that depend on this node
            for other_id in nodes:
                if other_id != node_id and node_id in edges.get(other_id, []):
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        # If not all nodes processed, there's a cycle
        # Add remaining nodes in arbitrary order
        for node_id in nodes:
            if node_id not in result:
                result.append(node_id)

        return result
