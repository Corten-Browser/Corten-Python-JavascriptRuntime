"""
Code Motion and Instruction Scheduling

Optimizes code placement and instruction order for better performance:
- Code motion: Move operations to reduce register pressure
- Instruction scheduling: Reorder for optimal execution
"""

from typing import List, Set, Dict
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, IRNodeType


class DependencyGraph:
    """
    Dependency graph for instruction scheduling

    Tracks data and control dependencies between instructions.
    """

    def __init__(self):
        """Create empty dependency graph"""
        self.dependencies: Dict[IRNode, Set[IRNode]] = {}

    def add_dependency(self, node: IRNode, depends_on: IRNode):
        """
        Add dependency edge (node depends on depends_on)

        Args:
            node: Dependent node
            depends_on: Node that must execute first
        """
        if node not in self.dependencies:
            self.dependencies[node] = set()
        self.dependencies[node].add(depends_on)

    def get_dependencies(self, node: IRNode) -> Set[IRNode]:
        """
        Get all dependencies of a node

        Args:
            node: Node to query

        Returns:
            Set of nodes that this node depends on
        """
        return self.dependencies.get(node, set())

    def has_dependency(self, node: IRNode, depends_on: IRNode) -> bool:
        """
        Check if node depends on another node

        Args:
            node: Dependent node
            depends_on: Potential dependency

        Returns:
            True if dependency exists
        """
        return depends_on in self.get_dependencies(node)


class CodeMotionOptimizer:
    """
    Code Motion Optimizer

    Moves code to better locations:
    - Sink operations closer to their use (reduce live ranges)
    - Move independent operations for better scheduling
    - Respect data and control dependencies
    """

    def __init__(self):
        """Create code motion optimizer"""
        pass

    def optimize(self, ir_graph: SSAGraph) -> SSAGraph:
        """
        Optimize code placement

        Args:
            ir_graph: SSA IR graph

        Returns:
            IR with optimized code placement
        """
        # Analyze dependencies
        dep_graph = self._build_dependency_graph(ir_graph)

        # Sink operations closer to their uses
        self._sink_operations(ir_graph, dep_graph)

        # Move independent operations
        self._move_independent_operations(ir_graph, dep_graph)

        return ir_graph

    def _build_dependency_graph(self, ir_graph: SSAGraph) -> DependencyGraph:
        """
        Build dependency graph from IR

        Args:
            ir_graph: IR graph

        Returns:
            Dependency graph
        """
        dep_graph = DependencyGraph()

        # Add data dependencies (from IR edges)
        for node in ir_graph.nodes:
            for input_node in node.inputs:
                dep_graph.add_dependency(node, input_node)

        return dep_graph

    def _sink_operations(self, ir_graph: SSAGraph, dep_graph: DependencyGraph):
        """
        Sink operations closer to their uses

        Reduces live ranges and register pressure.

        Args:
            ir_graph: IR graph
            dep_graph: Dependency graph
        """
        # For each node, try to move it closer to its uses
        for node in ir_graph.nodes:
            if self._can_sink(node):
                # Find the best location (closest to uses)
                # In a full implementation, we'd move the node in the CFG
                # For now, we just mark it as sinkable
                if not hasattr(node, 'code_motion'):
                    node.code_motion = 'sinkable'

    def _can_sink(self, node: IRNode) -> bool:
        """
        Check if node can be sunk (moved later)

        Args:
            node: IR node

        Returns:
            True if node can be sunk
        """
        # Can't sink nodes with side effects
        if self._has_side_effects(node):
            return False

        # Can sink pure computations
        return node.node_type in {
            IRNodeType.BINARY_OP,
            IRNodeType.UNARY_OP,
            IRNodeType.CONSTANT,
        }

    def _move_independent_operations(
        self,
        ir_graph: SSAGraph,
        dep_graph: DependencyGraph
    ):
        """
        Move independent operations for better scheduling

        Args:
            ir_graph: IR graph
            dep_graph: Dependency graph
        """
        # Find operations that are independent (no dependencies between them)
        for node in ir_graph.nodes:
            # Check if this node has independent siblings
            if not self._has_side_effects(node):
                # Mark as movable
                if not hasattr(node, 'code_motion'):
                    node.code_motion = 'movable'

    def _has_side_effects(self, node: IRNode) -> bool:
        """
        Check if node has side effects

        Args:
            node: IR node

        Returns:
            True if node has side effects
        """
        side_effect_types = {
            IRNodeType.STORE_PROPERTY,
            IRNodeType.CALL,
            IRNodeType.RETURN,
            IRNodeType.BRANCH,
        }
        return node.node_type in side_effect_types


class InstructionScheduler:
    """
    Instruction Scheduler

    Schedules instructions within basic blocks for optimal execution:
    - Respects dependencies
    - Prioritizes critical path
    - Groups similar operations
    - Hides memory latency
    """

    def __init__(self):
        """Create instruction scheduler"""
        pass

    def schedule(self, ir_graph: SSAGraph) -> SSAGraph:
        """
        Schedule instructions in IR

        Args:
            ir_graph: SSA IR graph

        Returns:
            IR with optimized instruction order
        """
        # Build dependency graph
        dep_graph = self.build_dependency_graph(ir_graph)

        # Schedule each basic block
        for block in ir_graph.basic_blocks:
            self._schedule_block(block, dep_graph)

        return ir_graph

    def build_dependency_graph(self, ir_graph: SSAGraph) -> DependencyGraph:
        """
        Build dependency graph for scheduling

        Args:
            ir_graph: IR graph

        Returns:
            Dependency graph with data and control dependencies
        """
        dep_graph = DependencyGraph()

        # Add data dependencies
        for node in ir_graph.nodes:
            for input_node in node.inputs:
                dep_graph.add_dependency(node, input_node)

        # Add control dependencies
        # (branches, stores must maintain order)
        self._add_control_dependencies(ir_graph, dep_graph)

        return dep_graph

    def _add_control_dependencies(
        self,
        ir_graph: SSAGraph,
        dep_graph: DependencyGraph
    ):
        """
        Add control dependencies to graph

        Args:
            ir_graph: IR graph
            dep_graph: Dependency graph to update
        """
        # Stores and calls must maintain their relative order
        side_effect_nodes = [
            node for node in ir_graph.nodes
            if node.node_type in {
                IRNodeType.STORE_PROPERTY,
                IRNodeType.CALL,
                IRNodeType.BRANCH,
            }
        ]

        # Add sequential dependencies between side-effect nodes
        for i in range(len(side_effect_nodes) - 1):
            dep_graph.add_dependency(
                side_effect_nodes[i + 1],
                side_effect_nodes[i]
            )

    def _schedule_block(self, block, dep_graph: DependencyGraph):
        """
        Schedule instructions in a basic block

        Args:
            block: Basic block
            dep_graph: Dependency graph
        """
        if not block.nodes:
            return

        # Perform topological sort with heuristics
        scheduled = self._topological_sort_with_heuristics(
            block.nodes,
            dep_graph
        )

        # Update block with scheduled order
        block.nodes = scheduled

    def _topological_sort_with_heuristics(
        self,
        nodes: List[IRNode],
        dep_graph: DependencyGraph
    ) -> List[IRNode]:
        """
        Topological sort with scheduling heuristics

        Heuristics:
        1. Prioritize critical path (longest dependency chain)
        2. Group similar operations
        3. Schedule memory loads early (hide latency)

        Args:
            nodes: Nodes to schedule
            dep_graph: Dependency graph

        Returns:
            Scheduled node list
        """
        # Compute in-degree for each node (number of dependencies)
        in_degree = {}
        for node in nodes:
            in_degree[node] = len([
                dep for dep in dep_graph.get_dependencies(node)
                if dep in nodes
            ])

        # Ready queue: nodes with no unscheduled dependencies
        ready = [node for node in nodes if in_degree[node] == 0]
        scheduled = []

        while ready:
            # Choose best node from ready queue using heuristics
            node = self._choose_best_node(ready, dep_graph)
            ready.remove(node)
            scheduled.append(node)

            # Update in-degrees of dependent nodes
            for other in nodes:
                if node in dep_graph.get_dependencies(other):
                    in_degree[other] -= 1
                    if in_degree[other] == 0 and other not in scheduled:
                        ready.append(other)

        return scheduled

    def _choose_best_node(
        self,
        ready: List[IRNode],
        dep_graph: DependencyGraph
    ) -> IRNode:
        """
        Choose best node from ready queue using heuristics

        Heuristics:
        1. Prioritize loads (hide memory latency)
        2. Prioritize critical path
        3. Group similar operations

        Args:
            ready: Ready queue
            dep_graph: Dependency graph

        Returns:
            Best node to schedule next
        """
        if len(ready) == 1:
            return ready[0]

        # Prioritize loads (hide latency)
        loads = [n for n in ready if n.node_type == IRNodeType.LOAD_PROPERTY]
        if loads:
            return loads[0]

        # Prioritize by critical path length
        # (simplified: choose node with most uses)
        best = ready[0]
        max_uses = len(best.uses)

        for node in ready[1:]:
            uses = len(node.uses)
            if uses > max_uses:
                best = node
                max_uses = uses

        return best
