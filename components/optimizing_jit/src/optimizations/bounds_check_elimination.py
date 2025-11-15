"""
Bounds Check Elimination

Eliminates redundant array bounds checks when range analysis proves they are safe.

Example:
    for (i = 0; i < arr.length; i++) {
        x = arr[i]  // Bounds check can be eliminated
    }
"""

from typing import Dict
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, CallNode, ConstantNode
from .range_analysis import ValueRange


class BoundsCheckEliminator:
    """
    Bounds Check Eliminator

    Uses range analysis to eliminate provably safe bounds checks.
    A bounds check is safe if:
        0 <= index < array.length
    """

    def __init__(self):
        """Create bounds check eliminator"""
        pass

    def eliminate_checks(
        self,
        ir_graph: SSAGraph,
        range_info: Dict[IRNode, ValueRange]
    ) -> SSAGraph:
        """
        Eliminate redundant bounds checks

        Args:
            ir_graph: SSA IR graph
            range_info: Range information from range analysis

        Returns:
            Optimized IR with eliminated bounds checks
        """
        # Find all bounds check nodes
        # In our simplified IR, bounds checks are represented as special CallNodes
        checks_to_remove = []

        for node in ir_graph.nodes:
            if self._is_bounds_check(node):
                # Check if this bounds check is provably safe
                if self._can_eliminate_check(node, range_info):
                    checks_to_remove.append(node)

        # Remove eliminated checks
        for check in checks_to_remove:
            ir_graph.nodes.remove(check)

            # Remove from basic blocks
            for block in ir_graph.basic_blocks:
                if check in block.nodes:
                    block.nodes.remove(check)

        return ir_graph

    def _is_bounds_check(self, node: IRNode) -> bool:
        """
        Check if node is a bounds check

        Args:
            node: Node to check

        Returns:
            True if node is a bounds check
        """
        # Bounds checks are represented as CallNode with "bounds_check" function
        if isinstance(node, CallNode) and len(node.inputs) >= 1:
            func = node.inputs[0]
            if isinstance(func, ConstantNode) and func.value == "bounds_check":
                return True
        return False

    def _can_eliminate_check(
        self,
        check_node: CallNode,
        range_info: Dict[IRNode, ValueRange]
    ) -> bool:
        """
        Determine if bounds check can be eliminated

        Args:
            check_node: Bounds check node
            range_info: Range information

        Returns:
            True if check is provably safe
        """
        # Extract index and length from bounds check
        # bounds_check(index, length)
        # Format: CallNode(func="bounds_check", args=[index, length])
        if len(check_node.inputs) < 2:
            return False

        # inputs[0] is the function name, inputs[1] is index, inputs[2] is length
        if len(check_node.inputs) == 2:
            # Only one argument - not enough info
            return False

        index_node = check_node.inputs[1]
        length_node = check_node.inputs[2] if len(check_node.inputs) > 2 else None

        if length_node is None:
            return False

        # Get range of index
        index_range = range_info.get(index_node, None)
        if index_range is None:
            return False

        # Get array length (if it's a constant)
        if isinstance(length_node, ConstantNode):
            array_length = length_node.value
        else:
            # Length is not a constant - conservative
            return False

        # Check if index range is provably safe
        return self._is_check_safe(index_range, array_length)

    def _is_check_safe(self, index_range: ValueRange, array_length: int) -> bool:
        """
        Check if index range is provably safe for array access

        Args:
            index_range: Range of index values
            array_length: Array length

        Returns:
            True if access is provably safe (0 <= index < length)
        """
        # Check lower bound: min_value >= 0
        if index_range.min_value < 0:
            return False

        # Check upper bound: max_value < array_length
        if index_range.max_value >= array_length:
            return False

        return True
