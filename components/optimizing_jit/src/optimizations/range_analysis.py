"""
Range Analysis

Tracks possible value ranges for each SSA value to enable optimizations like:
- Bounds check elimination
- Overflow detection
- Type specialization
"""

from dataclasses import dataclass
from typing import Dict, Optional
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, ConstantNode, BinaryOpNode, UnaryOpNode, PhiNode, ParameterNode, IRNodeType


# Constants for unknown ranges
UNKNOWN_MIN = -2**31  # -2 billion (effectively -infinity for 32-bit int)
UNKNOWN_MAX = 2**31 - 1  # +2 billion (effectively +infinity for 32-bit int)


@dataclass
class ValueRange:
    """
    Represents the possible range of values for an SSA value

    Attributes:
        min_value: Minimum possible value
        max_value: Maximum possible value
    """
    min_value: int
    max_value: int

    def is_always_positive(self) -> bool:
        """Check if value is always positive"""
        return self.min_value >= 0

    def is_in_range(self, low: int, high: int) -> bool:
        """Check if entire range is within [low, high]"""
        return self.min_value >= low and self.max_value <= high


class RangeAnalyzer:
    """
    Range Analyzer

    Computes value ranges for all SSA values using dataflow analysis.
    Supports:
    - Constant propagation (range [c, c])
    - Binary operations (range arithmetic)
    - Phi nodes (range union)
    """

    def __init__(self):
        """Create range analyzer"""
        pass

    def analyze(self, ir_graph: SSAGraph) -> Dict[IRNode, ValueRange]:
        """
        Analyze value ranges for all nodes

        Args:
            ir_graph: SSA IR graph

        Returns:
            Dictionary mapping nodes to their value ranges
        """
        ranges: Dict[IRNode, ValueRange] = {}

        # Iterate through nodes in topological order
        # (simplified: just iterate through all nodes)
        # In a real implementation, would use worklist algorithm for fixed-point

        # Also analyze phi nodes from SSA graph
        all_nodes = list(ir_graph.nodes)
        if hasattr(ir_graph, 'phi_nodes'):
            all_nodes.extend(ir_graph.phi_nodes)

        for node in all_nodes:
            ranges[node] = self._compute_range(node, ranges)

        return ranges

    def _compute_range(self, node: IRNode, ranges: Dict[IRNode, ValueRange]) -> ValueRange:
        """
        Compute range for a single node

        Args:
            node: Node to analyze
            ranges: Current range information

        Returns:
            Computed range for node
        """
        if isinstance(node, ConstantNode):
            # Constant has exact range [value, value]
            return ValueRange(node.value, node.value)

        elif isinstance(node, ParameterNode):
            # Parameters have unknown range
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

        elif isinstance(node, BinaryOpNode):
            return self._compute_binary_op_range(node, ranges)

        elif isinstance(node, UnaryOpNode):
            return self._compute_unary_op_range(node, ranges)

        elif isinstance(node, PhiNode):
            return self._compute_phi_range(node, ranges)

        else:
            # Unknown node type: conservative range
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

    def _compute_binary_op_range(self, node: BinaryOpNode, ranges: Dict[IRNode, ValueRange]) -> ValueRange:
        """
        Compute range for binary operation

        Args:
            node: Binary operation node
            ranges: Current ranges

        Returns:
            Computed range
        """
        if len(node.inputs) < 2:
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

        left_range = ranges.get(node.inputs[0], ValueRange(UNKNOWN_MIN, UNKNOWN_MAX))
        right_range = ranges.get(node.inputs[1], ValueRange(UNKNOWN_MIN, UNKNOWN_MAX))

        if node.op == "ADD":
            # [a, b] + [c, d] = [a+c, b+d]
            return ValueRange(
                self._safe_add(left_range.min_value, right_range.min_value),
                self._safe_add(left_range.max_value, right_range.max_value)
            )

        elif node.op == "SUB":
            # [a, b] - [c, d] = [a-d, b-c]
            return ValueRange(
                self._safe_sub(left_range.min_value, right_range.max_value),
                self._safe_sub(left_range.max_value, right_range.min_value)
            )

        elif node.op == "MUL":
            # Multiplication: consider all combinations
            products = [
                left_range.min_value * right_range.min_value,
                left_range.min_value * right_range.max_value,
                left_range.max_value * right_range.min_value,
                left_range.max_value * right_range.max_value
            ]
            return ValueRange(min(products), max(products))

        elif node.op == "DIV":
            # Division: avoid divide by zero
            if right_range.min_value <= 0 <= right_range.max_value:
                # Might divide by zero - conservative range
                return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

            quotients = []
            if right_range.min_value != 0:
                quotients.append(left_range.min_value // right_range.min_value)
                quotients.append(left_range.max_value // right_range.min_value)
            if right_range.max_value != 0:
                quotients.append(left_range.min_value // right_range.max_value)
                quotients.append(left_range.max_value // right_range.max_value)

            if quotients:
                return ValueRange(min(quotients), max(quotients))
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

        elif node.op in ["LT", "GT", "LE", "GE", "EQ", "NE"]:
            # Comparison operators return boolean (0 or 1)
            return ValueRange(0, 1)

        else:
            # Unknown operation
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

    def _compute_unary_op_range(self, node: UnaryOpNode, ranges: Dict[IRNode, ValueRange]) -> ValueRange:
        """
        Compute range for unary operation

        Args:
            node: Unary operation node
            ranges: Current ranges

        Returns:
            Computed range
        """
        if len(node.inputs) < 1:
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

        operand_range = ranges.get(node.inputs[0], ValueRange(UNKNOWN_MIN, UNKNOWN_MAX))

        if node.op == "NEG":
            # -[a, b] = [-b, -a]
            return ValueRange(-operand_range.max_value, -operand_range.min_value)

        elif node.op == "NOT":
            # NOT returns boolean
            return ValueRange(0, 1)

        else:
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

    def _compute_phi_range(self, node: PhiNode, ranges: Dict[IRNode, ValueRange]) -> ValueRange:
        """
        Compute range for phi node (union of input ranges)

        Args:
            node: Phi node
            ranges: Current ranges

        Returns:
            Union of all input ranges
        """
        if not node.inputs:
            return ValueRange(UNKNOWN_MIN, UNKNOWN_MAX)

        # Phi range is union of all input ranges
        min_val = UNKNOWN_MAX
        max_val = UNKNOWN_MIN

        for input_node in node.inputs:
            input_range = ranges.get(input_node, ValueRange(UNKNOWN_MIN, UNKNOWN_MAX))
            min_val = min(min_val, input_range.min_value)
            max_val = max(max_val, input_range.max_value)

        return ValueRange(min_val, max_val)

    def _safe_add(self, a: int, b: int) -> int:
        """Safe addition with overflow handling"""
        result = a + b
        # Clamp to range
        if result < UNKNOWN_MIN:
            return UNKNOWN_MIN
        if result > UNKNOWN_MAX:
            return UNKNOWN_MAX
        return result

    def _safe_sub(self, a: int, b: int) -> int:
        """Safe subtraction with overflow handling"""
        result = a - b
        # Clamp to range
        if result < UNKNOWN_MIN:
            return UNKNOWN_MIN
        if result > UNKNOWN_MAX:
            return UNKNOWN_MAX
        return result

    def get_range(self, node: IRNode, ranges: Dict[IRNode, ValueRange]) -> ValueRange:
        """
        Get range for a specific node

        Args:
            node: Node to query
            ranges: Range information from analysis

        Returns:
            Range for node, or unknown range if not found
        """
        return ranges.get(node, ValueRange(UNKNOWN_MIN, UNKNOWN_MAX))
