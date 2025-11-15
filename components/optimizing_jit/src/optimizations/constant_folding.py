"""
Constant Folding

Evaluates constant expressions at compile time instead of runtime.
"""

from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, BinaryOpNode, UnaryOpNode, ConstantNode, IRNodeType


class ConstantFolder:
    """
    Constant Folder

    Evaluates constant expressions at compile time:
    - Binary operations on constants (2 + 3 → 5)
    - Unary operations on constants (-42 → -42)
    - Constant propagation (if x = 5, then x + 1 → 6)
    """

    def __init__(self):
        """Create constant folder"""
        pass

    def fold(self, ir_graph: SSAGraph) -> SSAGraph:
        """
        Fold constant expressions in IR

        Args:
            ir_graph: SSA IR graph

        Returns:
            IR with constants folded
        """
        changed = True
        while changed:
            changed = False

            for node in ir_graph.nodes[:]:  # Copy to avoid modification during iteration
                if isinstance(node, BinaryOpNode):
                    if self._can_fold_binary(node):
                        folded = self._fold_binary(node)
                        self._replace_node(ir_graph, node, folded)
                        changed = True

                elif isinstance(node, UnaryOpNode):
                    if self._can_fold_unary(node):
                        folded = self._fold_unary(node)
                        self._replace_node(ir_graph, node, folded)
                        changed = True

        return ir_graph

    def _can_fold_binary(self, node: BinaryOpNode) -> bool:
        """Check if binary op can be folded"""
        return (
            len(node.inputs) == 2
            and isinstance(node.inputs[0], ConstantNode)
            and isinstance(node.inputs[1], ConstantNode)
        )

    def _fold_binary(self, node: BinaryOpNode) -> ConstantNode:
        """Fold binary operation on constants"""
        left_val = node.inputs[0].value
        right_val = node.inputs[1].value

        # Perform operation
        op_map = {
            "ADD": lambda l, r: l + r,
            "SUB": lambda l, r: l - r,
            "MUL": lambda l, r: l * r,
            "DIV": lambda l, r: l / r if r != 0 else float("inf"),
            "MOD": lambda l, r: l % r if r != 0 else 0,
            "GT": lambda l, r: l > r,
            "LT": lambda l, r: l < r,
            "EQ": lambda l, r: l == r,
            "NE": lambda l, r: l != r,
            "GE": lambda l, r: l >= r,
            "LE": lambda l, r: l <= r,
        }

        if node.op in op_map:
            result = op_map[node.op](left_val, right_val)
            return ConstantNode(result)

        # Unknown operation - don't fold
        return node

    def _can_fold_unary(self, node: UnaryOpNode) -> bool:
        """Check if unary op can be folded"""
        return len(node.inputs) == 1 and isinstance(node.inputs[0], ConstantNode)

    def _fold_unary(self, node: UnaryOpNode) -> ConstantNode:
        """Fold unary operation on constant"""
        val = node.inputs[0].value

        op_map = {
            "NEG": lambda v: -v,
            "NOT": lambda v: not v,
        }

        if node.op in op_map:
            result = op_map[node.op](val)
            return ConstantNode(result)

        return node

    def _replace_node(self, ir_graph: SSAGraph, old_node: IRNode, new_node: IRNode):
        """Replace old node with new node in graph"""
        # Update all uses of old node to use new node
        for use in old_node.uses[:]:
            use.remove_input(old_node)
            use.add_input(new_node)

        # Replace in graph nodes list
        if old_node in ir_graph.nodes:
            idx = ir_graph.nodes.index(old_node)
            ir_graph.nodes[idx] = new_node

        # Replace in basic blocks
        for block in ir_graph.basic_blocks:
            if old_node in block.nodes:
                idx = block.nodes.index(old_node)
                block.nodes[idx] = new_node
