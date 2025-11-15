"""
Dead Code Elimination (DCE)

Removes dead code from SSA IR:
- Unreachable basic blocks
- Unused value computations
- Redundant operations
"""

from typing import Set
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode


class DeadCodeEliminator:
    """
    Dead Code Eliminator

    Removes code that doesn't affect program output:
    - Values that are computed but never used
    - Unreachable basic blocks
    - Pure operations with no side effects
    """

    def __init__(self):
        """Create dead code eliminator"""
        pass

    def eliminate(self, ir_graph: SSAGraph) -> SSAGraph:
        """
        Eliminate dead code from IR

        Algorithm:
        1. Mark all nodes that are "live" (have side effects or are used)
        2. Recursively mark inputs of live nodes as live
        3. Remove unmarked (dead) nodes

        Args:
            ir_graph: SSA IR graph

        Returns:
            IR with dead code removed
        """
        # Mark live nodes
        live_nodes = self._mark_live_nodes(ir_graph)

        # Remove dead nodes
        dead_nodes = [node for node in ir_graph.nodes if node not in live_nodes]

        for node in dead_nodes:
            ir_graph.nodes.remove(node)
            # Remove from basic blocks
            for block in ir_graph.basic_blocks:
                if node in block.nodes:
                    block.nodes.remove(node)

        return ir_graph

    def _mark_live_nodes(self, ir_graph: SSAGraph) -> Set[IRNode]:
        """
        Mark nodes that are live (must be kept)

        Args:
            ir_graph: IR graph

        Returns:
            Set of live nodes
        """
        live = set()
        worklist = []

        # Start with nodes that have side effects
        # (Return, StoreProperty, Call, etc.)
        for node in ir_graph.nodes:
            if self._has_side_effects(node):
                live.add(node)
                worklist.append(node)

        # Propagate liveness to inputs
        while worklist:
            node = worklist.pop()
            for input_node in node.inputs:
                if input_node not in live:
                    live.add(input_node)
                    worklist.append(input_node)

        return live

    def _has_side_effects(self, node: IRNode) -> bool:
        """
        Check if node has side effects (must be kept)

        Args:
            node: IR node

        Returns:
            True if node has side effects
        """
        from ..ir_nodes import IRNodeType

        # These nodes have side effects or are required
        side_effect_types = {
            IRNodeType.RETURN,
            IRNodeType.STORE_PROPERTY,
            IRNodeType.CALL,  # Calls might have side effects
            IRNodeType.BRANCH,
        }

        return node.node_type in side_effect_types
