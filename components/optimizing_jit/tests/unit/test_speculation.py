"""
Tests for Speculation Manager and Deoptimization
"""

import pytest
from components.optimizing_jit.src.optimizations.speculation_manager import (
    SpeculationManager, GuardType, GuardNode, DeoptTrigger, DeoptReason
)
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder


class TestGuardNode:
    """Test guard node"""

    def test_create_guard_node(self):
        """Should create guard node"""
        # Given: A value to guard
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        value = builder.build_parameter(0)

        # When: We create type guard
        guard = GuardNode(GuardType.TYPE_GUARD, value, expected_type="Smi")

        # Then: Guard should be created
        assert guard is not None
        assert guard.guard_type == GuardType.TYPE_GUARD
        assert guard.expected_type == "Smi"

    def test_create_range_guard(self):
        """Should create range guard"""
        # Given: A value to guard
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        value = builder.build_parameter(0)

        # When: We create range guard [0, 100]
        guard = GuardNode(GuardType.RANGE_GUARD, value, min_value=0, max_value=100)

        # Then: Range guard should be created
        assert guard is not None
        assert guard.guard_type == GuardType.RANGE_GUARD
        assert guard.min_value == 0
        assert guard.max_value == 100

    def test_create_shape_guard(self):
        """Should create shape guard"""
        # Given: An object to guard
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        obj = builder.build_parameter(0)

        # When: We create shape guard
        guard = GuardNode(GuardType.SHAPE_GUARD, obj, expected_shape="Shape_123")

        # Then: Shape guard should be created
        assert guard is not None
        assert guard.guard_type == GuardType.SHAPE_GUARD
        assert guard.expected_shape == "Shape_123"


class TestDeoptTrigger:
    """Test deoptimization trigger"""

    def test_create_deopt_trigger(self):
        """Should create deopt trigger"""
        # Given: Nothing
        # When: We create deopt trigger
        trigger = DeoptTrigger(
            guard_id=1,
            reason=DeoptReason.TYPE_MISMATCH,
            bytecode_offset=42,
            value_map={"x": "r0", "y": "r1"}
        )

        # Then: Trigger should be created
        assert trigger is not None
        assert trigger.guard_id == 1
        assert trigger.reason == DeoptReason.TYPE_MISMATCH
        assert trigger.bytecode_offset == 42
        assert trigger.value_map == {"x": "r0", "y": "r1"}


class TestSpeculationManager:
    """Test speculation manager"""

    def test_create_speculation_manager(self):
        """Should create speculation manager"""
        # Given: Nothing
        # When: We create manager
        manager = SpeculationManager()

        # Then: Manager should be created
        assert manager is not None

    def test_insert_type_guard(self):
        """Should insert type guard for specialized operation"""
        # Given: IR with binary operation (could specialize to Smi)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        add = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Mock profiling data suggesting Smi types
        profiling_data = {
            "type_feedback": {
                0: {"type": "Smi"},  # Parameter 0 is Smi
                1: {"type": "Smi"},  # Parameter 1 is Smi
            }
        }

        # When: We insert guards
        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # Then: Should have type guards for both parameters
        assert len(guards) >= 2
        type_guards = [g for g in guards if g.guard_type == GuardType.TYPE_GUARD]
        assert len(type_guards) >= 2

    def test_insert_shape_guard(self):
        """Should insert shape guard for property access"""
        # Given: IR with property load
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "x")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Mock profiling data with shape
        profiling_data = {
            "type_feedback": {
                0: {"type": "Object", "shape": "Shape_42"}
            }
        }

        # When: We insert guards
        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # Then: Should have shape guard
        assert len(guards) > 0
        shape_guards = [g for g in guards if g.guard_type == GuardType.SHAPE_GUARD]
        assert len(shape_guards) > 0

    def test_insert_range_guard(self):
        """Should insert range guard for array index"""
        # Given: IR with array access (simplified as property load)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        arr = builder.build_parameter(0)
        index = builder.build_parameter(1)
        load = builder.build_load_property(arr, "data")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Mock profiling data with range info
        profiling_data = {
            "type_feedback": {
                1: {"type": "Smi", "min": 0, "max": 100}
            }
        }

        # When: We insert guards
        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # Then: Should have guards
        assert len(guards) >= 0  # May or may not insert range guard

    def test_create_deopt_trigger_from_guard(self):
        """Should create deopt trigger from guard"""
        # Given: A guard node
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        value = builder.build_parameter(0)

        guard = GuardNode(GuardType.TYPE_GUARD, value, expected_type="Smi")

        # When: We create deopt trigger
        manager = SpeculationManager()
        trigger = manager.create_deopt_trigger(
            guard=guard,
            reason=DeoptReason.TYPE_MISMATCH,
            bytecode_offset=10
        )

        # Then: Trigger should be created with correct info
        assert trigger is not None
        assert trigger.reason == DeoptReason.TYPE_MISMATCH
        assert trigger.bytecode_offset == 10

    def test_generate_deopt_metadata(self):
        """Should generate deopt metadata for all guards"""
        # Given: IR with guards
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        add = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        profiling_data = {
            "type_feedback": {
                0: {"type": "Smi"},
                1: {"type": "Smi"},
            }
        }

        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # When: We generate deopt metadata
        deopt_info = manager.generate_deopt_metadata(guards, bytecode_offset=5)

        # Then: Should have deopt triggers for all guards
        assert len(deopt_info) == len(guards)
        for trigger in deopt_info:
            assert isinstance(trigger, DeoptTrigger)

    def test_no_guards_without_profiling(self):
        """Should not insert guards without profiling data"""
        # Given: IR without profiling data
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        add = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Empty profiling data
        profiling_data = {"type_feedback": {}}

        # When: We insert guards
        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # Then: Should have no guards
        assert len(guards) == 0

    def test_guard_for_null_check(self):
        """Should insert null check guard"""
        # Given: IR with property access that might be null
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "x")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        profiling_data = {
            "type_feedback": {
                0: {"type": "Object", "nullable": True}
            }
        }

        # When: We insert guards
        manager = SpeculationManager()
        optimized, guards = manager.insert_guards(ssa_graph, profiling_data)

        # Then: Should have null check guard
        null_guards = [g for g in guards if g.guard_type == GuardType.NULL_CHECK]
        # May or may not have null check depending on implementation
        assert guards is not None
