"""
Tests for deoptimization trigger handling (RED phase).
"""
import pytest
from unittest.mock import Mock
from components.deoptimization.src.trigger_handler import DeoptTriggerHandler
from components.deoptimization.src.deopt_types import DeoptReason


class TestDeoptTriggerHandler:
    """Test DeoptTriggerHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_manager = Mock()
        self.handler = DeoptTriggerHandler(self.mock_manager)

    def test_create_trigger_handler(self):
        """Test creating trigger handler."""
        assert self.handler is not None
        assert self.handler.manager == self.mock_manager

    def test_handle_guard_failure(self):
        """Test handling guard failure."""
        mock_value = Mock()
        mock_value.value = 42

        result = self.handler.handle_guard_failure(
            guard_id=1,
            guard_location=100,
            actual_value=mock_value
        )

        assert result is not None
        # Should call manager.deoptimize
        assert self.mock_manager.deoptimize.called

    def test_handle_guard_failure_calls_manager(self):
        """Test that guard failure triggers deoptimization."""
        mock_value = Mock()

        self.handler.handle_guard_failure(
            guard_id=5,
            guard_location=200,
            actual_value=mock_value
        )

        # Verify manager was called with GUARD_FAILURE reason
        call_args = self.mock_manager.deoptimize.call_args
        assert call_args is not None

    def test_handle_type_mismatch(self):
        """Test handling type mismatch."""
        result = self.handler.handle_type_mismatch(
            expected_type="int",
            actual_type="object",
            location=150
        )

        assert result is not None
        assert self.mock_manager.deoptimize.called

    def test_handle_type_mismatch_reason(self):
        """Test type mismatch uses TYPE_MISMATCH reason."""
        self.handler.handle_type_mismatch(
            expected_type="int",
            actual_type="string",
            location=50
        )

        # Should use TYPE_MISMATCH reason
        assert self.mock_manager.deoptimize.called

    def test_handle_different_deopt_reasons(self):
        """Test handling different deoptimization reasons."""
        # Guard failure
        self.handler.handle_guard_failure(1, 10, Mock())
        assert self.mock_manager.deoptimize.call_count == 1

        # Type mismatch
        self.handler.handle_type_mismatch("int", "string", 20)
        assert self.mock_manager.deoptimize.call_count == 2

    def test_multiple_guard_failures(self):
        """Test handling multiple guard failures."""
        for i in range(5):
            self.handler.handle_guard_failure(i, i * 10, Mock())

        assert self.mock_manager.deoptimize.call_count == 5

    def test_categorize_reason_guard_failure(self):
        """Test categorizing guard failure reason."""
        reason = self.handler._categorize_reason("guard_failure")
        assert reason == DeoptReason.GUARD_FAILURE

    def test_categorize_reason_type_mismatch(self):
        """Test categorizing type mismatch reason."""
        reason = self.handler._categorize_reason("type_mismatch")
        assert reason == DeoptReason.TYPE_MISMATCH

    def test_categorize_reason_unknown(self):
        """Test categorizing unknown reason defaults to ASSUMPTION_VIOLATED."""
        reason = self.handler._categorize_reason("unknown_reason")
        assert reason == DeoptReason.ASSUMPTION_VIOLATED
