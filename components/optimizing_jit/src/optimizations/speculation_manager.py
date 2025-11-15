"""
Speculation Manager

Manages speculative optimizations with guards and deoptimization triggers.

Speculative optimization assumes certain conditions (type, shape, range) and inserts
guard instructions. If guards fail at runtime, execution deoptimizes back to interpreter.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from ..ssa_builder import SSAGraph
from ..ir_nodes import IRNode, IRNodeType, ParameterNode, BinaryOpNode, LoadPropertyNode


class GuardType(Enum):
    """Types of guard instructions"""
    TYPE_GUARD = "TYPE_GUARD"  # Guard: value is expected type
    SHAPE_GUARD = "SHAPE_GUARD"  # Guard: object has expected shape
    RANGE_GUARD = "RANGE_GUARD"  # Guard: value in expected range
    NULL_CHECK = "NULL_CHECK"  # Guard: value is not null


class DeoptReason(Enum):
    """Reasons for deoptimization"""
    TYPE_MISMATCH = "TYPE_MISMATCH"  # Type guard failed
    SHAPE_MISMATCH = "SHAPE_MISMATCH"  # Shape guard failed
    RANGE_OVERFLOW = "RANGE_OVERFLOW"  # Range guard failed
    NULL_POINTER = "NULL_POINTER"  # Null check failed


class GuardNode(IRNode):
    """
    Guard instruction node

    Inserted before speculative optimizations to check assumptions.
    If guard fails at runtime, execution deoptimizes to interpreter.
    """

    def __init__(
        self,
        guard_type: GuardType,
        value: IRNode,
        expected_type: Optional[str] = None,
        expected_shape: Optional[str] = None,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None
    ):
        """
        Create guard node

        Args:
            guard_type: Type of guard
            value: Value to guard
            expected_type: Expected type (for TYPE_GUARD)
            expected_shape: Expected shape (for SHAPE_GUARD)
            min_value: Minimum value (for RANGE_GUARD)
            max_value: Maximum value (for RANGE_GUARD)
        """
        super().__init__(IRNodeType.CALL)  # Guards are represented as special calls
        self.guard_type = guard_type
        self.expected_type = expected_type
        self.expected_shape = expected_shape
        self.min_value = min_value
        self.max_value = max_value
        self.add_input(value)

    def __repr__(self) -> str:
        return f"GuardNode(id={self.id}, type={self.guard_type.value})"


@dataclass
class DeoptTrigger:
    """
    Deoptimization trigger metadata

    Contains information needed to deoptimize when a guard fails.
    """
    guard_id: int
    reason: DeoptReason
    bytecode_offset: int
    value_map: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"DeoptTrigger(guard={self.guard_id}, reason={self.reason.value}, offset={self.bytecode_offset})"


class SpeculationManager:
    """
    Speculation Manager

    Inserts guard instructions for speculative optimizations and generates
    deoptimization metadata.
    """

    def __init__(self):
        """Create speculation manager"""
        self._guard_counter = 0

    def insert_guards(
        self,
        ir_graph: SSAGraph,
        profiling_data: Dict[str, Any]
    ) -> Tuple[SSAGraph, List[GuardNode]]:
        """
        Insert guard instructions for speculative optimizations

        Args:
            ir_graph: SSA IR graph
            profiling_data: Profiling data with type feedback

        Returns:
            Tuple of (optimized IR graph, list of inserted guards)
        """
        guards: List[GuardNode] = []

        # Extract type feedback
        type_feedback = profiling_data.get("type_feedback", {})

        # Iterate through nodes and insert guards based on profiling
        for node in list(ir_graph.nodes):
            # Insert type guards for parameters based on profiling
            if isinstance(node, ParameterNode):
                guard = self._insert_parameter_guard(node, type_feedback)
                if guard:
                    guards.append(guard)
                    ir_graph.add_node(guard)

            # Insert shape guards for property loads
            elif isinstance(node, LoadPropertyNode):
                guard = self._insert_property_guard(node, type_feedback)
                if guard:
                    guards.append(guard)
                    ir_graph.add_node(guard)

        return ir_graph, guards

    def _insert_parameter_guard(
        self,
        param: ParameterNode,
        type_feedback: Dict[int, Dict[str, Any]]
    ) -> Optional[GuardNode]:
        """
        Insert guard for parameter based on type feedback

        Args:
            param: Parameter node
            type_feedback: Type feedback data

        Returns:
            Guard node if guard needed, None otherwise
        """
        feedback = type_feedback.get(param.index, None)
        if not feedback:
            return None

        # Get expected type from profiling
        expected_type = feedback.get("type", None)
        if expected_type:
            # Insert type guard
            guard = GuardNode(GuardType.TYPE_GUARD, param, expected_type=expected_type)
            return guard

        return None

    def _insert_property_guard(
        self,
        load: LoadPropertyNode,
        type_feedback: Dict[int, Dict[str, Any]]
    ) -> Optional[GuardNode]:
        """
        Insert guard for property load based on shape feedback

        Args:
            load: Load property node
            type_feedback: Type feedback data

        Returns:
            Guard node if guard needed, None otherwise
        """
        if not load.inputs:
            return None

        obj = load.inputs[0]

        # If object is a parameter, check for shape feedback
        if isinstance(obj, ParameterNode):
            feedback = type_feedback.get(obj.index, None)
            if feedback and "shape" in feedback:
                # Insert shape guard
                expected_shape = feedback["shape"]
                guard = GuardNode(GuardType.SHAPE_GUARD, obj, expected_shape=expected_shape)
                return guard

        return None

    def create_deopt_trigger(
        self,
        guard: GuardNode,
        reason: DeoptReason,
        bytecode_offset: int = 0
    ) -> DeoptTrigger:
        """
        Create deoptimization trigger for guard

        Args:
            guard: Guard node
            reason: Deoptimization reason
            bytecode_offset: Bytecode offset to resume at

        Returns:
            Deoptimization trigger
        """
        return DeoptTrigger(
            guard_id=guard.id,
            reason=reason,
            bytecode_offset=bytecode_offset,
            value_map={}  # Simplified: would map SSA values to interpreter state
        )

    def generate_deopt_metadata(
        self,
        guards: List[GuardNode],
        bytecode_offset: int = 0
    ) -> List[DeoptTrigger]:
        """
        Generate deoptimization metadata for all guards

        Args:
            guards: List of guard nodes
            bytecode_offset: Bytecode offset for recovery

        Returns:
            List of deoptimization triggers
        """
        triggers = []

        for guard in guards:
            # Determine deopt reason based on guard type
            if guard.guard_type == GuardType.TYPE_GUARD:
                reason = DeoptReason.TYPE_MISMATCH
            elif guard.guard_type == GuardType.SHAPE_GUARD:
                reason = DeoptReason.SHAPE_MISMATCH
            elif guard.guard_type == GuardType.RANGE_GUARD:
                reason = DeoptReason.RANGE_OVERFLOW
            elif guard.guard_type == GuardType.NULL_CHECK:
                reason = DeoptReason.NULL_POINTER
            else:
                reason = DeoptReason.TYPE_MISMATCH

            trigger = self.create_deopt_trigger(guard, reason, bytecode_offset)
            triggers.append(trigger)

        return triggers
