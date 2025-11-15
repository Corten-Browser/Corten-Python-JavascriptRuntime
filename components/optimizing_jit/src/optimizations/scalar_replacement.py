"""
Scalar Replacement of Aggregates

Replaces non-escaping objects with scalar values.
This eliminates heap allocation for objects that don't escape function scope.
"""

from typing import Dict, Set
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, LoadPropertyNode, StorePropertyNode, ConstantNode
from .escape_analyzer import EscapeInfo, EscapeStatus


class ScalarReplacement:
    """
    Scalar Replacement Optimizer

    Replaces non-escaping objects with scalar values.

    Transformation:
    ---------------
    Before:
        obj = new Object()
        obj.x = 10
        obj.y = 20
        return obj.x + obj.y

    After:
        scalar_x = 10
        scalar_y = 20
        return scalar_x + scalar_y

    Benefits:
    ---------
    - Eliminates heap allocation
    - Reduces GC pressure
    - Enables further optimizations (constant folding, etc.)

    Algorithm:
    ----------
    1. Identify non-escaping objects (from escape analysis)
    2. For each non-escaping object:
       a. Track all property stores (obj.x = v → create scalar_x = v)
       b. Replace property loads (obj.x → scalar_x)
       c. Replace property stores (obj.x = v → scalar_x = v)
       d. Remove object allocation
    3. Update SSA graph
    """

    def __init__(self):
        """Create scalar replacement optimizer"""
        pass

    def replace(self, ir_graph: SSAGraph, escape_info: EscapeInfo) -> SSAGraph:
        """
        Replace non-escaping objects with scalars

        Args:
            ir_graph: SSA IR graph
            escape_info: Escape analysis results

        Returns:
            Optimized IR graph with scalar replacement applied
        """
        # Identify non-escaping objects
        non_escaping = escape_info.non_escaping_objects

        if not non_escaping:
            return ir_graph

        # Track scalar replacements for each object
        # Map: (object, property_name) → scalar_value
        scalar_map: Dict[tuple, IRNode] = {}

        # Track nodes to remove
        nodes_to_remove: Set[IRNode] = set()

        # Process each basic block
        for block in ir_graph.basic_blocks:
            for node in block.nodes[:]:
                # Replace StoreProperty to non-escaping objects
                if isinstance(node, StorePropertyNode):
                    obj = node.inputs[0] if len(node.inputs) > 0 else None
                    value = node.inputs[1] if len(node.inputs) > 1 else None

                    if obj in non_escaping:
                        # This is a store to non-escaping object
                        # Record the scalar value for this property
                        key = (obj, node.property_name)
                        scalar_map[key] = value

                        # Mark store for removal (we'll use scalar directly)
                        nodes_to_remove.add(node)

                # Replace LoadProperty from non-escaping objects
                elif isinstance(node, LoadPropertyNode):
                    obj = node.inputs[0] if len(node.inputs) > 0 else None

                    if obj in non_escaping:
                        # This is a load from non-escaping object
                        # Replace with scalar value
                        key = (obj, node.property_name)

                        if key in scalar_map:
                            scalar_value = scalar_map[key]

                            # Replace all uses of this load with the scalar value
                            for use in node.uses[:]:
                                use.remove_input(node)
                                use.add_input(scalar_value)

                            # Mark load for removal
                            nodes_to_remove.add(node)

        # Remove nodes
        for node in nodes_to_remove:
            if node in ir_graph.nodes:
                ir_graph.nodes.remove(node)

            # Remove from basic blocks
            for block in ir_graph.basic_blocks:
                if node in block.nodes:
                    block.nodes.remove(node)

        return ir_graph
