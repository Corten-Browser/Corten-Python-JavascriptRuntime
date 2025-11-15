"""
Strength Reduction Optimization

Replaces expensive operations with cheaper equivalents:
- x * 2 -> x << 1 (multiply by power of 2 -> shift left)
- x / 2 -> x >> 1 (divide by power of 2 -> shift right)
- x % 2 -> x & 1 (modulo by power of 2 -> bitwise AND)
"""

import math
from typing import Optional
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, BinaryOpNode, ConstantNode, IRNodeType


class StrengthReducer:
    """
    Strength Reduction Optimizer

    Replaces expensive arithmetic operations with cheaper equivalents
    when operands are constants with special properties (powers of 2, etc.)
    """

    def __init__(self):
        """Create strength reducer"""
        pass

    def reduce(self, ir_graph: SSAGraph) -> SSAGraph:
        """
        Apply strength reduction to IR graph

        Args:
            ir_graph: SSA IR graph

        Returns:
            Optimized IR graph with reduced operations
        """
        # Find all binary operations that can be reduced
        for node in list(ir_graph.nodes):
            if isinstance(node, BinaryOpNode):
                reduced_node = self._try_reduce_operation(node)
                if reduced_node and reduced_node != node:
                    # Replace node with reduced version
                    self._replace_node(ir_graph, node, reduced_node)

        return ir_graph

    def _try_reduce_operation(self, node: BinaryOpNode) -> Optional[IRNode]:
        """
        Try to reduce a binary operation

        Args:
            node: Binary operation node

        Returns:
            Reduced node if reduction possible, None otherwise
        """
        if node.op == "MUL":
            return self._try_reduce_multiply(node)
        elif node.op == "DIV":
            return self._try_reduce_divide(node)
        elif node.op == "MOD":
            return self._try_reduce_modulo(node)

        return None

    def _try_reduce_multiply(self, node: BinaryOpNode) -> Optional[IRNode]:
        """
        Try to reduce multiplication: x * 2^n -> x << n

        Args:
            node: Multiplication node

        Returns:
            Shift left node if reduction possible, None otherwise
        """
        # Check if right operand is a constant power of 2
        if len(node.inputs) >= 2:
            left, right = node.inputs[0], node.inputs[1]

            # Try both operands (multiplication is commutative)
            constant, value = self._extract_constant_and_value(left, right)

            if constant and isinstance(constant.value, int) and self._is_power_of_2(constant.value):
                # Replace with shift left
                shift_amount = self._log2(constant.value)
                shift_constant = ConstantNode(shift_amount)
                return BinaryOpNode("SHL", value, shift_constant)

        return None

    def _try_reduce_divide(self, node: BinaryOpNode) -> Optional[IRNode]:
        """
        Try to reduce division: x / 2^n -> x >> n

        Args:
            node: Division node

        Returns:
            Shift right node if reduction possible, None otherwise
        """
        # Check if right operand is a constant power of 2
        if len(node.inputs) >= 2:
            left, right = node.inputs[0], node.inputs[1]

            if isinstance(right, ConstantNode) and isinstance(right.value, int) and self._is_power_of_2(right.value):
                # Replace with shift right
                shift_amount = self._log2(right.value)
                shift_constant = ConstantNode(shift_amount)
                return BinaryOpNode("SHR", left, shift_constant)

        return None

    def _try_reduce_modulo(self, node: BinaryOpNode) -> Optional[IRNode]:
        """
        Try to reduce modulo: x % 2^n -> x & (2^n - 1)

        Args:
            node: Modulo node

        Returns:
            Bitwise AND node if reduction possible, None otherwise
        """
        # Check if right operand is a constant power of 2
        if len(node.inputs) >= 2:
            left, right = node.inputs[0], node.inputs[1]

            if isinstance(right, ConstantNode) and isinstance(right.value, int) and self._is_power_of_2(right.value):
                # Replace with bitwise AND: x & (n - 1)
                mask = right.value - 1
                mask_constant = ConstantNode(mask)
                return BinaryOpNode("AND", left, mask_constant)

        return None

    def _extract_constant_and_value(self, left: IRNode, right: IRNode):
        """
        Extract constant and value node from operands

        Args:
            left: Left operand
            right: Right operand

        Returns:
            Tuple of (constant_node, value_node) or (None, None)
        """
        if isinstance(right, ConstantNode):
            return (right, left)
        elif isinstance(left, ConstantNode):
            return (left, right)
        return (None, None)

    def _is_power_of_2(self, n: int) -> bool:
        """
        Check if number is a power of 2

        Args:
            n: Number to check

        Returns:
            True if n is a power of 2
        """
        if not isinstance(n, int) or n <= 0:
            return False
        return (n & (n - 1)) == 0

    def _log2(self, n: int) -> int:
        """
        Compute log base 2 of a power of 2

        Args:
            n: Power of 2

        Returns:
            Exponent
        """
        return int(math.log2(n))

    def _replace_node(self, ir_graph: SSAGraph, old_node: IRNode, new_node: IRNode):
        """
        Replace a node in the graph

        Args:
            ir_graph: IR graph
            old_node: Node to replace
            new_node: Replacement node
        """
        # Add new node and its inputs to graph
        if new_node not in ir_graph.nodes:
            ir_graph.add_node(new_node)

        # Add constant nodes used by new_node to graph
        for inp in new_node.inputs:
            if inp not in ir_graph.nodes:
                ir_graph.add_node(inp)

        # Update all uses of old_node to use new_node
        for user in list(old_node.uses):
            # Replace in user's inputs
            for i, inp in enumerate(user.inputs):
                if inp == old_node:
                    user.inputs[i] = new_node
                    new_node.uses.append(user)

        # Optionally remove old node (or let DCE handle it)
        # For now, we leave it (dead code elimination will remove it later)
