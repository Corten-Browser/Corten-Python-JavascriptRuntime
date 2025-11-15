"""
Polymorphic Inline Cache Handler

Handles polymorphic inline caches in optimized code by generating
specialized dispatch code for multiple shapes.
"""

from typing import Dict, Any
from ..ssa_builder import SSAGraph
from ..ir_nodes import (
    IRNode,
    IRNodeType,
    LoadPropertyNode,
    ConstantNode,
    BinaryOpNode,
    BranchNode,
)
from ..ir_builder import BasicBlock


class PolymorphicICHandler:
    """
    Polymorphic Inline Cache Handler

    Generates optimized code for polymorphic property accesses:
    - Monomorphic (1 shape): Direct offset load
    - Polymorphic (2-4 shapes): Shape checks with branches
    - Megamorphic (>4 shapes): Fall back to slow path

    Example polymorphic dispatch for obj.property:
        shape = LoadShape(obj)
        if (shape == shape1):
            value = LoadAtOffset(obj, offset1)
        elif (shape == shape2):
            value = LoadAtOffset(obj, offset2)
        elif (shape == shape3):
            value = LoadAtOffset(obj, offset3)
        else:
            value = SlowPropertyLoad(obj, "property")
    """

    def __init__(self):
        """Create polymorphic IC handler"""
        self.max_polymorphic_shapes = 4

    def handle(self, ir_graph: SSAGraph, ic_data: Dict[str, Any]) -> SSAGraph:
        """
        Handle polymorphic inline caches in IR

        Args:
            ir_graph: SSA IR graph
            ic_data: Inline cache profiling data (property_name -> IC state)

        Returns:
            IR with polymorphic IC handling inserted
        """
        if not ic_data:
            # No IC data, return unchanged
            return ir_graph

        # Find all property load nodes
        property_loads = [
            node for node in ir_graph.nodes
            if isinstance(node, LoadPropertyNode)
        ]

        # Handle each property load with IC data
        for load_node in property_loads:
            property_name = load_node.property_name
            if property_name in ic_data:
                ic_state = ic_data[property_name]
                self._handle_property_load(ir_graph, load_node, ic_state)

        return ir_graph

    def _handle_property_load(
        self,
        ir_graph: SSAGraph,
        load_node: LoadPropertyNode,
        ic_state: Any
    ):
        """
        Handle a single property load with IC data

        Args:
            ir_graph: IR graph
            load_node: Property load node
            ic_state: IC state for this property
        """
        num_shapes = len(ic_state.shapes)

        if num_shapes == 1:
            # Monomorphic: Direct offset load (no branches needed)
            self._handle_monomorphic(ir_graph, load_node, ic_state)
        elif 2 <= num_shapes <= self.max_polymorphic_shapes:
            # Polymorphic: Generate shape checks
            self._handle_polymorphic(ir_graph, load_node, ic_state)
        else:
            # Megamorphic: Use slow path (no optimization)
            self._handle_megamorphic(ir_graph, load_node, ic_state)

    def _handle_monomorphic(
        self,
        ir_graph: SSAGraph,
        load_node: LoadPropertyNode,
        ic_state: Any
    ):
        """
        Handle monomorphic property load (single shape)

        Optimizes to direct offset load without shape checks.

        Args:
            ir_graph: IR graph
            load_node: Property load node
            ic_state: IC state (1 shape)
        """
        # For monomorphic case, we can optimize to direct offset load
        # In a real implementation, we'd replace the LoadProperty with
        # a direct memory load at the known offset.

        # For this implementation, we add a comment node or marker
        # to indicate this is optimized (actual code gen would handle this)

        # The shape and offset are known at compile time
        shape_id = ic_state.shapes[0]
        offset = ic_state.offsets[0]

        # Mark this load as monomorphic (actual optimization happens in code gen)
        # For now, we just track that this is a monomorphic load
        if not hasattr(load_node, 'ic_optimization'):
            load_node.ic_optimization = 'monomorphic'
            load_node.shape_id = shape_id
            load_node.offset = offset

    def _handle_polymorphic(
        self,
        ir_graph: SSAGraph,
        load_node: LoadPropertyNode,
        ic_state: Any
    ):
        """
        Handle polymorphic property load (2-4 shapes)

        Generates shape checks with branches for each shape.

        Args:
            ir_graph: IR graph
            load_node: Property load node
            ic_state: IC state (2-4 shapes)
        """
        # Generate polymorphic dispatch code:
        # if (obj.shape == shape1) -> offset1
        # elif (obj.shape == shape2) -> offset2
        # ...
        # else -> slow path

        obj = load_node.inputs[0] if load_node.inputs else None
        if not obj:
            return

        # Find the basic block containing this load
        containing_block = None
        for block in ir_graph.basic_blocks:
            if load_node in block.nodes:
                containing_block = block
                break

        if not containing_block:
            return

        # Create shape check branches
        # For each shape, create a branch node
        for i, (shape_id, offset) in enumerate(zip(ic_state.shapes, ic_state.offsets)):
            # Create shape constant
            shape_const = ConstantNode(shape_id)
            ir_graph.add_node(shape_const)

            # Create comparison (shape == expected_shape)
            # In a real implementation, we'd load the shape first
            # For now, we create a comparison placeholder
            compare = BinaryOpNode("EQ", obj, shape_const)
            ir_graph.add_node(compare)

            # Create branch based on shape check
            branch = BranchNode(compare)
            ir_graph.add_node(branch)
            containing_block.add_node(branch)

        # Mark this load as polymorphic
        if not hasattr(load_node, 'ic_optimization'):
            load_node.ic_optimization = 'polymorphic'
            load_node.shapes = ic_state.shapes
            load_node.offsets = ic_state.offsets

    def _handle_megamorphic(
        self,
        ir_graph: SSAGraph,
        load_node: LoadPropertyNode,
        ic_state: Any
    ):
        """
        Handle megamorphic property load (>4 shapes)

        Falls back to slow path (no polymorphic dispatch).

        Args:
            ir_graph: IR graph
            load_node: Property load node
            ic_state: IC state (>4 shapes)
        """
        # Megamorphic: Too many shapes, use slow path
        # Mark this load as megamorphic (slow path)
        if not hasattr(load_node, 'ic_optimization'):
            load_node.ic_optimization = 'megamorphic'
            # Keep original LoadProperty node (will use slow path in code gen)
