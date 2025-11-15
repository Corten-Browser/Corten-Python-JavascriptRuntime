"""
Tests for frame reconstruction (RED phase).
"""
import pytest
from unittest.mock import Mock
from components.deoptimization.src.frame_reconstructor import FrameReconstructor
from components.deoptimization.src.deopt_types import (
    JITFrame,
    DeoptInfo,
    ValueLocation,
    DeoptReason,
)


class TestFrameReconstructor:
    """Test FrameReconstructor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.reconstructor = FrameReconstructor()

    def test_create_reconstructor(self):
        """Test creating FrameReconstructor."""
        assert self.reconstructor is not None

    def test_reconstruct_simple_frame(self):
        """Test reconstructing simple frame with one local."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 42},
            stack=[]
        )

        value_map = {
            "local0": ValueLocation("register", "rax", "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert frame is not None
        assert frame.bytecode_offset == 10
        assert len(frame.locals) == 1
        assert len(frame.stack) == 0

    def test_reconstruct_frame_with_multiple_locals(self):
        """Test reconstructing frame with multiple locals."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 10, "rbx": 20, "rcx": 30},
            stack=[]
        )

        value_map = {
            "local0": ValueLocation("register", "rax", "int"),
            "local1": ValueLocation("register", "rbx", "int"),
            "local2": ValueLocation("register", "rcx", "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=20,
            value_map=value_map,
            frame_size=3,
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.locals) == 3
        assert frame.bytecode_offset == 20

    def test_reconstruct_frame_with_stack_values(self):
        """Test reconstructing frame with operand stack."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={},
            stack=[100, 200, 300]
        )

        value_map = {
            "stack0": ValueLocation("stack", 0, "int"),
            "stack1": ValueLocation("stack", 1, "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=15,
            value_map=value_map,
            frame_size=0,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.stack_map = ["stack0", "stack1"]

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.stack) == 2
        assert len(frame.locals) == 0

    def test_reconstruct_frame_mixed_locations(self):
        """Test reconstructing frame with values from different locations."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 42},
            stack=[100, 200]
        )

        value_map = {
            "local0": ValueLocation("register", "rax", "int"),
            "local1": ValueLocation("stack", 0, "int"),
            "stack0": ValueLocation("stack", 1, "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=25,
            value_map=value_map,
            frame_size=2,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.stack_map = ["stack0"]

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.locals) == 2
        assert len(frame.stack) == 1

    def test_materialize_values_from_registers(self):
        """Test materializing values from registers."""
        value_map = {
            "local0": ValueLocation("register", "rax", "int"),
            "local1": ValueLocation("register", "rbx", "int"),
        }
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 10, "rbx": 20},
            stack=[]
        )
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map=value_map,
            frame_size=2,
            reason=DeoptReason.GUARD_FAILURE
        )

        values = self.reconstructor.materialize_values(value_map, deopt_info)

        assert len(values) == 2
        assert all(hasattr(v, "value") for v in values)

    def test_materialize_values_from_stack(self):
        """Test materializing values from stack."""
        value_map = {
            "local0": ValueLocation("stack", 0, "int"),
            "local1": ValueLocation("stack", 1, "int"),
        }
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={},
            stack=[100, 200]
        )
        # Store jit_frame for access
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map=value_map,
            frame_size=2,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.jit_frame = jit_frame

        values = self.reconstructor.materialize_values(value_map, deopt_info)

        assert len(values) == 2

    def test_materialize_values_from_constants(self):
        """Test materializing constant values."""
        value_map = {
            "local0": ValueLocation("constant", 0, "int"),
            "local1": ValueLocation("constant", 1, "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map=value_map,
            frame_size=2,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.constants = {0: 42, 1: 100}

        values = self.reconstructor.materialize_values(value_map, deopt_info)

        assert len(values) == 2

    def test_reconstruct_nested_frame_simple_inlining(self):
        """Test reconstructing nested frames (inlined function)."""
        # Outer frame
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 10},
            stack=[]
        )

        # Deopt info for inlined function
        value_map = {
            "local0": ValueLocation("register", "rax", "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=30,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.inlined_frames = []  # No nested frames for now

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert frame is not None
        assert frame.bytecode_offset == 30

    def test_reconstruct_frame_preserves_bytecode_offset(self):
        """Test that bytecode offset is correctly set."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={},
            stack=[]
        )

        for offset in [0, 10, 50, 100, 1000]:
            deopt_info = DeoptInfo(
                deopt_id=1,
                bytecode_offset=offset,
                value_map={},
                frame_size=0,
                reason=DeoptReason.GUARD_FAILURE
            )

            frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)
            assert frame.bytecode_offset == offset

    def test_reconstruct_frame_with_missing_register_value(self):
        """Test handling missing register values (uses default)."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={},  # Missing rax
            stack=[]
        )

        value_map = {
            "local0": ValueLocation("register", "rax", "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        # Should handle gracefully with default value
        assert len(frame.locals) == 1

    def test_reconstruct_frame_validates_frame_size(self):
        """Test that frame size matches number of locals."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"rax": 10},
            stack=[]
        )

        value_map = {
            "local0": ValueLocation("register", "rax", "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,  # Matches number of locals
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.locals) == deopt_info.frame_size

    def test_reconstruct_empty_frame(self):
        """Test reconstructing frame with no locals or stack."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={},
            stack=[]
        )

        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map={},
            frame_size=0,
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.locals) == 0
        assert len(frame.stack) == 0

    def test_reconstruct_frame_with_float_values(self):
        """Test reconstructing frame with floating point values."""
        jit_frame = JITFrame(
            return_address=0x1000,
            registers={"xmm0": 3.14},  # Float register
            stack=[]
        )

        value_map = {
            "local0": ValueLocation("register", "xmm0", "float")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )

        frame = self.reconstructor.reconstruct_frame(jit_frame, deopt_info)

        assert len(frame.locals) == 1
