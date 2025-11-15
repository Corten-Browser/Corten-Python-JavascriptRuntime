"""
Tests for state materialization (RED phase).
"""
import pytest
from unittest.mock import Mock, MagicMock
from components.deoptimization.src.state_materializer import StateMaterializer
from components.deoptimization.src.deopt_types import (
    JITState,
    DeoptInfo,
    ValueLocation,
    DeoptReason,
)


class TestStateMaterializer:
    """Test StateMaterializer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.materializer = StateMaterializer()

    def test_create_materializer(self):
        """Test creating StateMaterializer."""
        assert self.materializer is not None

    def test_materialize_from_register(self):
        """Test materializing value from register."""
        # JIT state with register values
        jit_state = JITState(
            registers={"rax": 42},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        # Deopt info mapping local0 to register
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

        # Materialize
        result = self.materializer.materialize(jit_state, deopt_info)

        # Should have interpreter state
        assert result is not None
        assert hasattr(result, "frame")
        # Frame should have local0 with value from rax
        assert len(result.frame.locals) >= 1

    def test_materialize_from_stack(self):
        """Test materializing value from stack."""
        # JIT state with stack values
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )
        jit_state.stack = [100, 200, 300]  # Stack values

        # Deopt info mapping local0 to stack offset
        value_map = {
            "local0": ValueLocation("stack", 0, "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )

        # Materialize
        result = self.materializer.materialize(jit_state, deopt_info)

        assert result is not None
        assert hasattr(result, "frame")
        assert len(result.frame.locals) >= 1

    def test_materialize_constant(self):
        """Test materializing constant value."""
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        # Deopt info with constant value
        value_map = {
            "local0": ValueLocation("constant", 0, "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )
        # Store constant value
        deopt_info.constants = {0: 42}

        result = self.materializer.materialize(jit_state, deopt_info)

        assert result is not None
        assert hasattr(result, "frame")

    def test_materialize_multiple_values(self):
        """Test materializing multiple values from different locations."""
        jit_state = JITState(
            registers={"rax": 10, "rbx": 20},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )
        jit_state.stack = [100, 200]

        value_map = {
            "local0": ValueLocation("register", "rax", "int"),
            "local1": ValueLocation("register", "rbx", "int"),
            "local2": ValueLocation("stack", 0, "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=3,
            reason=DeoptReason.GUARD_FAILURE
        )

        result = self.materializer.materialize(jit_state, deopt_info)

        assert result is not None
        assert hasattr(result, "frame")
        assert len(result.frame.locals) == 3

    def test_materialize_object_simple(self):
        """Test materializing simple JSObject."""
        # Mock Shape
        mock_shape = Mock()
        mock_shape.properties = {"x": 0, "y": 1}

        # Object data (escaped allocation)
        object_data = {
            "x": 10,
            "y": 20
        }

        result = self.materializer.materialize_object(object_data, mock_shape)

        assert result is not None
        # Should be JSObject-like with properties
        assert hasattr(result, "properties")
        assert result.properties["x"] == 10
        assert result.properties["y"] == 20

    def test_materialize_object_with_nested_values(self):
        """Test materializing object with nested property values."""
        mock_shape = Mock()
        mock_shape.properties = {"nested": 0}

        # Nested object reference
        object_data = {
            "nested": {"value": 42}
        }

        result = self.materializer.materialize_object(object_data, mock_shape)

        assert result is not None
        assert hasattr(result, "properties")
        assert result.properties["nested"] == {"value": 42}

    def test_convert_value_smi(self):
        """Test converting Smi (small integer) to JSValue."""
        # Small integer should be represented as Smi
        result = self.materializer._convert_value(42, "int")

        assert result is not None
        # Should be JSNumber or similar
        assert hasattr(result, "value")
        assert result.value == 42

    def test_convert_value_float64(self):
        """Test converting Float64 to JSValue."""
        result = self.materializer._convert_value(3.14, "float")

        assert result is not None
        assert hasattr(result, "value")
        assert abs(result.value - 3.14) < 0.001

    def test_convert_value_object_pointer(self):
        """Test converting object pointer to JSValue."""
        # Mock object pointer (address)
        object_ptr = 0x12345678

        result = self.materializer._convert_value(object_ptr, "object")

        assert result is not None
        # Should handle object references

    def test_materialize_with_empty_value_map(self):
        """Test materializing with no values."""
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map={},
            frame_size=0,
            reason=DeoptReason.GUARD_FAILURE
        )

        result = self.materializer.materialize(jit_state, deopt_info)

        assert result is not None
        assert hasattr(result, "frame")
        assert len(result.frame.locals) == 0

    def test_materialize_sets_bytecode_offset(self):
        """Test that materialized state has correct bytecode offset."""
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=42,
            value_map={},
            frame_size=0,
            reason=DeoptReason.GUARD_FAILURE
        )

        result = self.materializer.materialize(jit_state, deopt_info)

        assert result.frame.bytecode_offset == 42

    def test_materialize_preserves_stack_values(self):
        """Test that operand stack values are materialized correctly."""
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )
        jit_state.stack = [1, 2, 3]

        # Map stack values
        value_map = {
            "stack0": ValueLocation("stack", 0, "int"),
            "stack1": ValueLocation("stack", 1, "int"),
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=10,
            value_map=value_map,
            frame_size=0,
            reason=DeoptReason.GUARD_FAILURE
        )
        deopt_info.stack_map = ["stack0", "stack1"]

        result = self.materializer.materialize(jit_state, deopt_info)

        # Should have stack values
        assert len(result.frame.stack) == 2

    def test_invalid_location_type_raises_error(self):
        """Test that invalid location type raises error."""
        jit_state = JITState(
            registers={},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        value_map = {
            "local0": ValueLocation("invalid", 0, "int")
        }
        deopt_info = DeoptInfo(
            deopt_id=1,
            bytecode_offset=0,
            value_map=value_map,
            frame_size=1,
            reason=DeoptReason.GUARD_FAILURE
        )

        with pytest.raises(ValueError, match="Unknown location type"):
            self.materializer.materialize(jit_state, deopt_info)
