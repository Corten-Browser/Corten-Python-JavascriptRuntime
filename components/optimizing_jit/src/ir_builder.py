"""
IR Builder - Builds high-level IR from bytecode

Constructs a sea-of-nodes intermediate representation with control flow graph.
"""

from typing import List, Optional
from .ir_nodes import (
    IRNode,
    ConstantNode,
    ParameterNode,
    BinaryOpNode,
    UnaryOpNode,
    LoadPropertyNode,
    StorePropertyNode,
    CallNode,
    ReturnNode,
    BranchNode,
    PhiNode,
)


class BasicBlock:
    """
    Basic block in control flow graph

    A basic block is a straight-line sequence of instructions with:
    - One entry point (at the beginning)
    - One exit point (at the end)
    - No branches except at the end

    Basic blocks form the control flow graph (CFG).
    """

    def __init__(self, block_id: int):
        """
        Create a basic block

        Args:
            block_id: Unique identifier for this block
        """
        self.id = block_id
        self.nodes: List[IRNode] = []
        self.predecessors: List["BasicBlock"] = []
        self.successors: List["BasicBlock"] = []

    def add_node(self, node: IRNode):
        """
        Add an IR node to this block

        Args:
            node: IR node to add
        """
        self.nodes.append(node)

    def add_successor(self, successor: "BasicBlock"):
        """
        Add a successor block (control flow edge)

        Args:
            successor: Successor basic block
        """
        if successor not in self.successors:
            self.successors.append(successor)
            successor.predecessors.append(self)

    def __repr__(self) -> str:
        return f"BB{self.id}(nodes={len(self.nodes)}, preds={len(self.predecessors)}, succs={len(self.successors)})"


class IRGraph:
    """
    IR Graph (sea of nodes)

    Contains:
    - All IR nodes
    - Basic blocks forming the control flow graph
    - Entry and exit blocks
    """

    def __init__(self):
        """Create an empty IR graph"""
        self.nodes: List[IRNode] = []
        self.basic_blocks: List[BasicBlock] = []
        self.entry: Optional[BasicBlock] = None
        self.exit: Optional[BasicBlock] = None

    def add_node(self, node: IRNode):
        """
        Add a node to the graph

        Args:
            node: IR node to add
        """
        if node not in self.nodes:
            self.nodes.append(node)

    def add_basic_block(self, block: BasicBlock):
        """
        Add a basic block to the graph

        Args:
            block: Basic block to add
        """
        if block not in self.basic_blocks:
            self.basic_blocks.append(block)

    def set_entry(self, block: BasicBlock):
        """
        Set entry block

        Args:
            block: Entry basic block
        """
        self.entry = block

    def set_exit(self, block: BasicBlock):
        """
        Set exit block

        Args:
            block: Exit basic block
        """
        self.exit = block

    def __repr__(self) -> str:
        return f"IRGraph(nodes={len(self.nodes)}, blocks={len(self.basic_blocks)})"


class IRBuilder:
    """
    IR Builder - Constructs IR graphs from bytecode

    Provides a fluent API for building IR nodes and basic blocks.
    Automatically tracks nodes and blocks for graph construction.
    """

    def __init__(self):
        """Create a new IR builder"""
        self.current_block: Optional[BasicBlock] = None
        self._block_counter = 0
        self._all_blocks: List[BasicBlock] = []
        self._all_nodes: List[IRNode] = []

    def create_basic_block(self) -> BasicBlock:
        """
        Create a new basic block

        Returns:
            New basic block with unique ID
        """
        block = BasicBlock(self._block_counter)
        self._block_counter += 1
        self._all_blocks.append(block)
        return block

    def set_current_block(self, block: BasicBlock):
        """
        Set the current insertion point

        Args:
            block: Block to insert into
        """
        self.current_block = block

    def _insert_node(self, node: IRNode) -> IRNode:
        """
        Insert a node into the current block

        Args:
            node: Node to insert

        Returns:
            The node (for chaining)
        """
        self._all_nodes.append(node)
        if self.current_block is not None:
            self.current_block.add_node(node)
        return node

    def build_constant(self, value) -> ConstantNode:
        """
        Build a constant node

        Args:
            value: Constant value

        Returns:
            Constant node
        """
        node = ConstantNode(value)
        return self._insert_node(node)

    def build_parameter(self, index: int) -> ParameterNode:
        """
        Build a parameter node

        Args:
            index: Parameter index

        Returns:
            Parameter node
        """
        node = ParameterNode(index)
        return self._insert_node(node)

    def build_binary_op(self, op: str, left: IRNode, right: IRNode) -> BinaryOpNode:
        """
        Build a binary operation node

        Args:
            op: Operation (ADD, SUB, MUL, DIV, GT, LT, etc.)
            left: Left operand
            right: Right operand

        Returns:
            Binary operation node
        """
        node = BinaryOpNode(op, left, right)
        return self._insert_node(node)

    def build_unary_op(self, op: str, operand: IRNode) -> UnaryOpNode:
        """
        Build a unary operation node

        Args:
            op: Operation (NEG, NOT, etc.)
            operand: Operand

        Returns:
            Unary operation node
        """
        node = UnaryOpNode(op, operand)
        return self._insert_node(node)

    def build_load_property(self, obj: IRNode, property_name: str) -> LoadPropertyNode:
        """
        Build a property load node

        Args:
            obj: Object to load from
            property_name: Property name

        Returns:
            Property load node
        """
        node = LoadPropertyNode(obj, property_name)
        return self._insert_node(node)

    def build_store_property(
        self, obj: IRNode, property_name: str, value: IRNode
    ) -> StorePropertyNode:
        """
        Build a property store node

        Args:
            obj: Object to store to
            property_name: Property name
            value: Value to store

        Returns:
            Property store node
        """
        node = StorePropertyNode(obj, property_name, value)
        return self._insert_node(node)

    def build_call(self, func: IRNode, args: List[IRNode]) -> CallNode:
        """
        Build a call node

        Args:
            func: Function to call
            args: Argument list

        Returns:
            Call node
        """
        node = CallNode(func, args)
        return self._insert_node(node)

    def build_return(self, value: Optional[IRNode]) -> ReturnNode:
        """
        Build a return node

        Args:
            value: Return value (None for void)

        Returns:
            Return node
        """
        node = ReturnNode(value)
        return self._insert_node(node)

    def build_branch(self, condition: IRNode) -> BranchNode:
        """
        Build a conditional branch node

        Args:
            condition: Branch condition

        Returns:
            Branch node
        """
        node = BranchNode(condition)
        return self._insert_node(node)

    def build_phi(self, inputs: List[IRNode]) -> PhiNode:
        """
        Build a phi node

        Args:
            inputs: Values from different control flow paths

        Returns:
            Phi node
        """
        node = PhiNode(inputs)
        return self._insert_node(node)

    def finalize(self, entry: BasicBlock, exit: BasicBlock) -> IRGraph:
        """
        Finalize IR graph construction

        Args:
            entry: Entry basic block
            exit: Exit basic block

        Returns:
            Completed IR graph
        """
        graph = IRGraph()

        # Add all blocks
        for block in self._all_blocks:
            graph.add_basic_block(block)

        # Add all nodes
        for node in self._all_nodes:
            graph.add_node(node)

        # Set entry and exit
        graph.set_entry(entry)
        graph.set_exit(exit)

        return graph
