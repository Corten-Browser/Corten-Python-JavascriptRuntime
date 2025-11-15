"""
IR Node Definitions for Optimizing JIT

Defines the high-level intermediate representation (IR) nodes used in the optimizing compiler.
Uses a "sea of nodes" representation where nodes are connected by data flow edges.
"""

from enum import Enum
from typing import List, Optional, Any
from dataclasses import dataclass, field


class IRNodeType(Enum):
    """
    Types of IR nodes in the sea-of-nodes representation

    Data nodes:
        - CONSTANT: Constant value
        - PARAMETER: Function parameter
        - BINARY_OP: Binary operation (ADD, SUB, MUL, DIV, etc.)
        - UNARY_OP: Unary operation (NEG, NOT, etc.)
        - PHI: Phi node for SSA merge points
        - LOAD_PROPERTY: Property access (obj.prop)
        - STORE_PROPERTY: Property assignment (obj.prop = value)
        - CALL: Function call

    Control nodes:
        - RETURN: Function return
        - BRANCH: Conditional branch
        - MERGE: Control flow merge point
    """
    CONSTANT = "CONSTANT"
    PARAMETER = "PARAMETER"
    BINARY_OP = "BINARY_OP"
    UNARY_OP = "UNARY_OP"
    PHI = "PHI"
    LOAD_PROPERTY = "LOAD_PROPERTY"
    STORE_PROPERTY = "STORE_PROPERTY"
    CALL = "CALL"
    RETURN = "RETURN"
    BRANCH = "BRANCH"
    MERGE = "MERGE"


# Global counter for node IDs
_node_id_counter = 0


def _next_node_id() -> int:
    """Generate next unique node ID"""
    global _node_id_counter
    _node_id_counter += 1
    return _node_id_counter


class IRNode:
    """
    Base class for all IR nodes in the sea-of-nodes representation

    Each node has:
    - node_type: Type of the node
    - inputs: List of nodes that this node depends on (data flow edges)
    - uses: List of nodes that depend on this node (reverse edges)
    - id: Unique identifier

    The sea-of-nodes representation allows flexible scheduling and optimization.
    """

    def __init__(self, node_type: IRNodeType):
        """
        Create a new IR node

        Args:
            node_type: Type of this node
        """
        self.node_type = node_type
        self.inputs: List[IRNode] = []
        self.uses: List[IRNode] = []
        self.id = _next_node_id()

    def add_input(self, input_node: "IRNode"):
        """
        Add an input (data dependency)

        Args:
            input_node: Node that this node depends on
        """
        if input_node not in self.inputs:
            self.inputs.append(input_node)
            input_node.uses.append(self)

    def remove_input(self, input_node: "IRNode"):
        """
        Remove an input

        Args:
            input_node: Node to remove from inputs
        """
        if input_node in self.inputs:
            self.inputs.remove(input_node)
            input_node.uses.remove(self)

    def __repr__(self) -> str:
        """String representation"""
        return f"{self.__class__.__name__}(id={self.id}, type={self.node_type.value})"


class ConstantNode(IRNode):
    """
    Constant value node

    Represents a constant value in the IR (integer, float, string, boolean, etc.)
    """

    def __init__(self, value: Any):
        """
        Create a constant node

        Args:
            value: The constant value
        """
        super().__init__(IRNodeType.CONSTANT)
        self.value = value

    def __repr__(self) -> str:
        return f"ConstantNode(id={self.id}, value={self.value})"


class ParameterNode(IRNode):
    """
    Function parameter node

    Represents a function parameter in the IR.
    """

    def __init__(self, index: int):
        """
        Create a parameter node

        Args:
            index: Parameter index (0-based)
        """
        super().__init__(IRNodeType.PARAMETER)
        self.index = index

    def __repr__(self) -> str:
        return f"ParameterNode(id={self.id}, index={self.index})"


class BinaryOpNode(IRNode):
    """
    Binary operation node

    Represents a binary operation (ADD, SUB, MUL, DIV, etc.)
    """

    def __init__(self, op: str, left: IRNode, right: IRNode):
        """
        Create a binary operation node

        Args:
            op: Operation (ADD, SUB, MUL, DIV, etc.)
            left: Left operand
            right: Right operand
        """
        super().__init__(IRNodeType.BINARY_OP)
        self.op = op
        self.add_input(left)
        self.add_input(right)

    def __repr__(self) -> str:
        return f"BinaryOpNode(id={self.id}, op={self.op})"


class UnaryOpNode(IRNode):
    """
    Unary operation node

    Represents a unary operation (NEG, NOT, etc.)
    """

    def __init__(self, op: str, operand: IRNode):
        """
        Create a unary operation node

        Args:
            op: Operation (NEG, NOT, etc.)
            operand: Operand
        """
        super().__init__(IRNodeType.UNARY_OP)
        self.op = op
        self.add_input(operand)

    def __repr__(self) -> str:
        return f"UnaryOpNode(id={self.id}, op={self.op})"


class PhiNode(IRNode):
    """
    Phi node for SSA form

    Represents a merge point in SSA where a variable can have different values
    from different control flow paths.

    Example:
        if (condition) {
            x = 10;  // value1
        } else {
            x = 20;  // value2
        }
        // x = phi(value1, value2)
    """

    def __init__(self, inputs: List[IRNode]):
        """
        Create a phi node

        Args:
            inputs: Values from different control flow paths
        """
        super().__init__(IRNodeType.PHI)
        for input_node in inputs:
            self.add_input(input_node)

    def __repr__(self) -> str:
        return f"PhiNode(id={self.id}, num_inputs={len(self.inputs)})"


class LoadPropertyNode(IRNode):
    """
    Property load node (obj.prop)

    Represents reading a property from an object.
    """

    def __init__(self, obj: IRNode, property_name: str):
        """
        Create a property load node

        Args:
            obj: Object to load from
            property_name: Property name
        """
        super().__init__(IRNodeType.LOAD_PROPERTY)
        self.property_name = property_name
        self.add_input(obj)

    def __repr__(self) -> str:
        return f"LoadPropertyNode(id={self.id}, property={self.property_name})"


class StorePropertyNode(IRNode):
    """
    Property store node (obj.prop = value)

    Represents writing a property to an object.
    """

    def __init__(self, obj: IRNode, property_name: str, value: IRNode):
        """
        Create a property store node

        Args:
            obj: Object to store to
            property_name: Property name
            value: Value to store
        """
        super().__init__(IRNodeType.STORE_PROPERTY)
        self.property_name = property_name
        self.add_input(obj)
        self.add_input(value)

    def __repr__(self) -> str:
        return f"StorePropertyNode(id={self.id}, property={self.property_name})"


class CallNode(IRNode):
    """
    Function call node

    Represents a function call with arguments.
    """

    def __init__(self, func: IRNode, args: List[IRNode]):
        """
        Create a call node

        Args:
            func: Function to call
            args: Argument list
        """
        super().__init__(IRNodeType.CALL)
        self.add_input(func)
        for arg in args:
            self.add_input(arg)

    def __repr__(self) -> str:
        return f"CallNode(id={self.id}, num_args={len(self.inputs) - 1})"


class ReturnNode(IRNode):
    """
    Return node

    Represents a function return statement.
    """

    def __init__(self, value: Optional[IRNode]):
        """
        Create a return node

        Args:
            value: Return value (None for undefined/void return)
        """
        super().__init__(IRNodeType.RETURN)
        if value is not None:
            self.add_input(value)

    def __repr__(self) -> str:
        has_value = len(self.inputs) > 0
        return f"ReturnNode(id={self.id}, has_value={has_value})"


class BranchNode(IRNode):
    """
    Conditional branch node

    Represents a conditional branch (if statement, loop condition, etc.)
    """

    def __init__(self, condition: IRNode):
        """
        Create a branch node

        Args:
            condition: Branch condition
        """
        super().__init__(IRNodeType.BRANCH)
        self.add_input(condition)

    def __repr__(self) -> str:
        return f"BranchNode(id={self.id})"


class MergeNode(IRNode):
    """
    Control flow merge node

    Represents a point where multiple control flow paths merge.
    Used in SSA construction.
    """

    def __init__(self, num_predecessors: int):
        """
        Create a merge node

        Args:
            num_predecessors: Number of incoming control flow paths
        """
        super().__init__(IRNodeType.MERGE)
        self.num_predecessors = num_predecessors

    def __repr__(self) -> str:
        return f"MergeNode(id={self.id}, predecessors={self.num_predecessors})"
