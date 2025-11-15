"""
Tests for deoptimization data structures (RED phase).
"""
import pytest
from components.deoptimization.src.deopt_types import (
    DeoptReason,
    DeoptMode,
    DeoptInfo,
    ValueLocation,
    JITFrame,
    InterpreterFrame,
    JITState,
    DeoptStats,
    DeoptHotspot,
)


class TestDeoptReason:
    """Test DeoptReason enum."""

    def test_guard_failure_reason(self):
        """Test GUARD_FAILURE reason exists."""
        assert DeoptReason.GUARD_FAILURE is not None

    def test_type_mismatch_reason(self):
        """Test TYPE_MISMATCH reason exists."""
        assert DeoptReason.TYPE_MISMATCH is not None

    def test_overflow_reason(self):
        """Test OVERFLOW reason exists."""
        assert DeoptReason.OVERFLOW is not None

    def test_all_reasons_defined(self):
        """Test all expected reasons are defined."""
        expected_reasons = {
            "GUARD_FAILURE",
            "TYPE_MISMATCH",
            "OVERFLOW",
            "DIV_BY_ZERO",
            "NULL_DEREFERENCE",
            "OUT_OF_BOUNDS",
            "SHAPE_MISMATCH",
            "IC_MISS",
            "ASSUMPTION_VIOLATED",
        }
        actual_reasons = {reason.name for reason in DeoptReason}
        assert actual_reasons == expected_reasons


class TestDeoptMode:
    """Test DeoptMode enum."""

    def test_eager_mode(self):
        """Test EAGER mode exists."""
        assert DeoptMode.EAGER is not None

    def test_lazy_mode(self):
        """Test LAZY mode exists."""
        assert DeoptMode.LAZY is not None


class TestValueLocation:
    """Test ValueLocation dataclass."""

    def test_create_register_location(self):
        """Test creating register location."""
        loc = ValueLocation(
            location_type="register",
            location_id=5,
            value_type="int"
        )
        assert loc.location_type == "register"
        assert loc.location_id == 5
        assert loc.value_type == "int"

    def test_create_stack_location(self):
        """Test creating stack location."""
        loc = ValueLocation(
            location_type="stack",
            location_id=10,
            value_type="object"
        )
        assert loc.location_type == "stack"
        assert loc.location_id == 10

    def test_create_constant_location(self):
        """Test creating constant location."""
        loc = ValueLocation(
            location_type="constant",
            location_id=0,
            value_type="int"
        )
        assert loc.location_type == "constant"


class TestDeoptInfo:
    """Test DeoptInfo dataclass."""

    def test_create_deopt_info(self):
        """Test creating DeoptInfo."""
        value_map = {
            "local0": ValueLocation("register", 5, "int"),
            "local1": ValueLocation("stack", 10, "object"),
        }
        info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=42,
            value_map=value_map,
            frame_size=2,
            reason=DeoptReason.GUARD_FAILURE
        )
        assert info.deopt_id == 1
        assert info.bytecode_offset == 42
        assert len(info.value_map) == 2
        assert info.frame_size == 2
        assert info.reason == DeoptReason.GUARD_FAILURE

    def test_deopt_info_with_empty_value_map(self):
        """Test DeoptInfo with empty value map."""
        info = DeoptInfo(
            deopt_id=2,
            bytecode_offset=0,
            value_map={},
            frame_size=0,
            reason=DeoptReason.TYPE_MISMATCH
        )
        assert len(info.value_map) == 0
        assert info.frame_size == 0


class TestJITFrame:
    """Test JITFrame dataclass."""

    def test_create_jit_frame(self):
        """Test creating JIT frame."""
        frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 42, "rbx": 100},
            stack=[1, 2, 3, 4]
        )
        assert frame.return_address == 0x1000
        assert frame.registers["rax"] == 42
        assert len(frame.stack) == 4

    def test_jit_frame_with_empty_registers(self):
        """Test JIT frame with no registers."""
        frame = JITFrame(
            return_address=0x2000,
            registers={},
            stack=[]
        )
        assert len(frame.registers) == 0
        assert len(frame.stack) == 0


class TestInterpreterFrame:
    """Test InterpreterFrame dataclass."""

    def test_create_interpreter_frame(self):
        """Test creating interpreter frame."""
        from unittest.mock import Mock

        locals_vals = [Mock(), Mock()]
        stack_vals = [Mock(), Mock(), Mock()]

        frame = InterpreterFrame(
            bytecode_offset=42,
            locals=locals_vals,
            stack=stack_vals
        )
        assert frame.bytecode_offset == 42
        assert len(frame.locals) == 2
        assert len(frame.stack) == 3

    def test_interpreter_frame_empty(self):
        """Test empty interpreter frame."""
        frame = InterpreterFrame(
            bytecode_offset=0,
            locals=[],
            stack=[]
        )
        assert frame.bytecode_offset == 0
        assert len(frame.locals) == 0
        assert len(frame.stack) == 0


class TestJITState:
    """Test JITState dataclass."""

    def test_create_jit_state(self):
        """Test creating JIT state."""
        state = JITState(
            registers={"rax": 10, "rbx": 20},
            stack_pointer=0x7fff,
            instruction_pointer=0x1234
        )
        assert state.registers["rax"] == 10
        assert state.stack_pointer == 0x7fff
        assert state.instruction_pointer == 0x1234


class TestDeoptStats:
    """Test DeoptStats dataclass."""

    def test_create_deopt_stats(self):
        """Test creating deopt statistics."""
        stats = DeoptStats(
            total_deopts=100,
            eager_deopts=30,
            lazy_deopts=70,
            reason_counts={
                DeoptReason.GUARD_FAILURE: 50,
                DeoptReason.TYPE_MISMATCH: 30,
                DeoptReason.OVERFLOW: 20,
            }
        )
        assert stats.total_deopts == 100
        assert stats.eager_deopts == 30
        assert stats.lazy_deopts == 70
        assert stats.reason_counts[DeoptReason.GUARD_FAILURE] == 50

    def test_deopt_stats_zero(self):
        """Test zero statistics."""
        stats = DeoptStats(
            total_deopts=0,
            eager_deopts=0,
            lazy_deopts=0,
            reason_counts={}
        )
        assert stats.total_deopts == 0
        assert len(stats.reason_counts) == 0


class TestDeoptHotspot:
    """Test DeoptHotspot dataclass."""

    def test_create_deopt_hotspot(self):
        """Test creating deopt hotspot."""
        hotspot = DeoptHotspot(
            function_id=42,
            location=100,
            count=500,
            reason=DeoptReason.GUARD_FAILURE
        )
        assert hotspot.function_id == 42
        assert hotspot.location == 100
        assert hotspot.count == 500
        assert hotspot.reason == DeoptReason.GUARD_FAILURE

    def test_multiple_hotspots(self):
        """Test creating multiple hotspots."""
        hotspots = [
            DeoptHotspot(1, 10, 100, DeoptReason.GUARD_FAILURE),
            DeoptHotspot(2, 20, 200, DeoptReason.TYPE_MISMATCH),
            DeoptHotspot(3, 30, 300, DeoptReason.OVERFLOW),
        ]
        assert len(hotspots) == 3
        assert hotspots[1].count == 200
