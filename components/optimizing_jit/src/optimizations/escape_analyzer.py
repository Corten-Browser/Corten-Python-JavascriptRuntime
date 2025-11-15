"""
Escape Analyzer

Determines which objects escape the function scope.
Non-escaping objects can be allocated on the stack instead of heap.
"""

from enum import Enum
from typing import Set, Dict
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, ReturnNode, StorePropertyNode, CallNode, PhiNode, IRNodeType


class EscapeStatus(Enum):
    """
    Escape status of an object

    ESCAPES: Object escapes function scope (heap allocation required)
    NO_ESCAPE: Object stays local (can be stack allocated)
    """
    ESCAPES = "ESCAPES"
    NO_ESCAPE = "NO_ESCAPE"


class EscapeInfo:
    """
    Escape analysis results

    Contains:
    - escaping_objects: Set of objects that escape function scope
    - non_escaping_objects: Set of objects that don't escape
    - object_status: Map from object to escape status
    """

    def __init__(self):
        """Create escape info"""
        self.escaping_objects: Set[IRNode] = set()
        self.non_escaping_objects: Set[IRNode] = set()
        self._object_status: Dict[IRNode, EscapeStatus] = {}

    def mark_escapes(self, obj: IRNode):
        """
        Mark object as escaping

        Args:
            obj: Object node
        """
        self.escaping_objects.add(obj)
        self._object_status[obj] = EscapeStatus.ESCAPES

    def mark_no_escape(self, obj: IRNode):
        """
        Mark object as non-escaping

        Args:
            obj: Object node
        """
        self.non_escaping_objects.add(obj)
        self._object_status[obj] = EscapeStatus.NO_ESCAPE

    def get_status(self, obj: IRNode) -> EscapeStatus:
        """
        Get escape status of object

        Args:
            obj: Object node

        Returns:
            Escape status (defaults to ESCAPES if unknown)
        """
        return self._object_status.get(obj, EscapeStatus.ESCAPES)


class EscapeAnalyzer:
    """
    Escape Analyzer

    Determines which objects escape function scope.

    An object ESCAPES if:
    - Returned from function
    - Stored to a global variable or property
    - Passed to a function call (might escape through call)
    - Stored in an escaping object

    An object DOES NOT ESCAPE if:
    - Only used in local computations
    - Only stored to non-escaping objects
    - Never leaves function scope

    Algorithm:
    1. Start with all objects as NO_ESCAPE (optimistic)
    2. Mark objects that escape through returns, stores, calls
    3. Propagate escape status (if A is stored in B and B escapes, A escapes)
    4. Iterate until fixed point
    """

    def __init__(self):
        """Create escape analyzer"""
        pass

    def analyze(self, ir_graph: SSAGraph) -> EscapeInfo:
        """
        Analyze object escape in IR graph

        Args:
            ir_graph: SSA IR graph

        Returns:
            Escape analysis results
        """
        escape_info = EscapeInfo()

        # Collect all potential object nodes
        # (For simplicity, consider parameters and certain operations as objects)
        objects = self._collect_objects(ir_graph)

        # Initially assume all objects don't escape
        for obj in objects:
            escape_info.mark_no_escape(obj)

        # Mark objects that escape
        changed = True
        while changed:
            changed = False

            for node in ir_graph.nodes:
                # Check if node causes objects to escape
                if self._causes_escape(node):
                    # Mark inputs as escaping
                    for input_node in node.inputs:
                        if input_node in objects:
                            if escape_info.get_status(input_node) == EscapeStatus.NO_ESCAPE:
                                escape_info.non_escaping_objects.discard(input_node)
                                escape_info.mark_escapes(input_node)
                                changed = True

            # Propagate escape through phi nodes
            # If a phi node escapes, all its inputs escape
            for node in ir_graph.nodes:
                if isinstance(node, PhiNode):
                    if escape_info.get_status(node) == EscapeStatus.ESCAPES:
                        # Phi escapes, so its inputs escape
                        for input_node in node.inputs:
                            if input_node in objects:
                                if escape_info.get_status(input_node) == EscapeStatus.NO_ESCAPE:
                                    escape_info.non_escaping_objects.discard(input_node)
                                    escape_info.mark_escapes(input_node)
                                    changed = True

        return escape_info

    def _collect_objects(self, ir_graph: SSAGraph) -> Set[IRNode]:
        """
        Collect all potential object nodes

        For simplicity, we consider:
        - Parameters (might be objects)
        - Phi nodes (might merge objects)

        In a full implementation, would track actual allocation sites.

        Args:
            ir_graph: IR graph

        Returns:
            Set of potential object nodes
        """
        objects = set()

        for node in ir_graph.nodes:
            # Parameters might be objects
            if node.node_type == IRNodeType.PARAMETER:
                objects.add(node)

            # Phi nodes might merge objects
            if isinstance(node, PhiNode):
                objects.add(node)

        return objects

    def _causes_escape(self, node: IRNode) -> bool:
        """
        Check if node causes its inputs to escape

        An object escapes if:
        - Returned from function (ReturnNode)
        - Stored to property (StorePropertyNode)
        - Passed to function call (CallNode)

        Args:
            node: IR node

        Returns:
            True if node causes escape
        """
        # Return causes escape
        if isinstance(node, ReturnNode):
            return True

        # Store to property causes escape
        # (Conservatively assume all stores escape)
        if isinstance(node, StorePropertyNode):
            # The value being stored escapes
            # Check if storing an object (not just a value)
            return True

        # Call causes escape (object passed to unknown function)
        if isinstance(node, CallNode):
            # Arguments escape (except function itself)
            # In practice, would check which arguments are objects
            return True

        # Other nodes don't cause escape
        return False
