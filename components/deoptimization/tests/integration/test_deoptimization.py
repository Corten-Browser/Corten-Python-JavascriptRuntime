"""Integration tests for deoptimization component."""
import pytest
from unittest.mock import Mock

from components.deoptimization.src.deopt_manager import DeoptimizationManager
from components.deoptimization.src.trigger_handler import DeoptTriggerHandler
from components.deoptimization.src.eager_deopt import EagerDeoptimizer
from components.deoptimization.src.deopt_types import (
    DeoptReason,
    DeoptMode,
    JITState,
    DeoptInfo,
    ValueLocation,
)


class TestDeoptimizationIntegration:
    """Test full deoptimization workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.manager = DeoptimizationManager()

    def test_full_eager_deopt_flow(self):
        """Test complete eager deoptimization flow."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {
            100: DeoptInfo(
                deopt_id=1,
                bytecode_offset=100,
                value_map={"local0": ValueLocation("register", "rax", "int")},
                frame_size=1,
                reason=DeoptReason.GUARD_FAILURE
            )
        }
        self.manager.register_optimized_function(1, mock_code)

        # Trigger deoptimization
        result = self.manager.deoptimize(
            function_id=1,
            deopt_point=100,
            reason=DeoptReason.GUARD_FAILURE,
            mode=DeoptMode.EAGER
        )

        # Verify result
        assert result is not None
        assert hasattr(result, "frame")
        assert result.frame.bytecode_offset == 100

    def test_full_lazy_deopt_flow(self):
        """Test complete lazy deoptimization flow."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Schedule lazy deopt
        result = self.manager.deoptimize(
            function_id=1,
            deopt_point=50,
            reason=DeoptReason.TYPE_MISMATCH,
            mode=DeoptMode.LAZY
        )

        # Should return None for lazy
        assert result is None

        # Process pending
        states = self.manager.lazy_deoptimizer.process_pending()
        assert len(states) == 1

    def test_trigger_handler_integration(self):
        """Test trigger handler with manager."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Create trigger handler
        handler = DeoptTriggerHandler(self.manager)

        # Trigger guard failure
        mock_value = Mock()
        mock_value.value = 42

        result = handler.handle_guard_failure(
            guard_id=1,
            guard_location=100,
            actual_value=mock_value,
            function_id=1  # Pass the registered function_id
        )

        # Verify deoptimization occurred
        stats = self.manager.get_stats()
        assert stats.total_deopts >= 1

    def test_eager_deoptimizer_integration(self):
        """Test eager deoptimizer with manager."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Create eager deoptimizer
        eager = EagerDeoptimizer(self.manager)

        # Trigger bailout
        jit_state = JITState(
            registers={"rax": 42},
            stack_pointer=0x7fff,
            instruction_pointer=0x1000
        )

        result = eager.bailout(
            function_id=1,
            bailout_point=200,
            jit_state=jit_state
        )

        assert result is not None

    def test_profiling_integration(self):
        """Test profiling across multiple deopts."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Multiple deopts
        for i in range(10):
            self.manager.deoptimize(
                function_id=1,
                deopt_point=i * 10,
                reason=DeoptReason.GUARD_FAILURE,
                mode=DeoptMode.EAGER
            )

        # Check stats
        stats = self.manager.get_stats()
        assert stats.total_deopts == 10
        assert stats.eager_deopts == 10
        assert stats.lazy_deopts == 0

    def test_hot_deopt_identification(self):
        """Test identifying hot deoptimization points."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Create hot deopt point
        for i in range(150):
            self.manager.deoptimize(
                function_id=1,
                deopt_point=100,  # Same location
                reason=DeoptReason.GUARD_FAILURE,
                mode=DeoptMode.EAGER
            )

        # Get hotspots
        hotspots = self.manager.profiler.get_hot_deopts(threshold=100)
        assert len(hotspots) >= 1
        assert hotspots[0].count >= 100

    def test_mixed_eager_lazy_deopts(self):
        """Test mixture of eager and lazy deoptimizations."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Eager deopts
        for i in range(5):
            self.manager.deoptimize(1, i * 10, DeoptReason.GUARD_FAILURE, DeoptMode.EAGER)

        # Lazy deopts
        for i in range(3):
            self.manager.deoptimize(1, i * 20, DeoptReason.TYPE_MISMATCH, DeoptMode.LAZY)

        # Check stats
        stats = self.manager.get_stats()
        assert stats.eager_deopts == 5
        assert stats.lazy_deopts == 3
        assert stats.total_deopts == 8

    def test_multiple_functions_deopt(self):
        """Test deoptimizing multiple functions."""
        # Register multiple functions
        for func_id in range(3):
            mock_code = Mock()
            mock_code.deopt_info = {}
            self.manager.register_optimized_function(func_id, mock_code)

        # Deopt each function
        for func_id in range(3):
            self.manager.deoptimize(
                function_id=func_id,
                deopt_point=100,
                reason=DeoptReason.GUARD_FAILURE,
                mode=DeoptMode.EAGER
            )

        # Check stats
        stats = self.manager.get_stats()
        assert stats.total_deopts == 3

    def test_reason_categorization(self):
        """Test different deopt reasons are tracked."""
        # Register function
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Different reasons
        reasons = [
            DeoptReason.GUARD_FAILURE,
            DeoptReason.TYPE_MISMATCH,
            DeoptReason.OVERFLOW,
            DeoptReason.DIV_BY_ZERO,
        ]

        for reason in reasons:
            self.manager.deoptimize(1, 100, reason, DeoptMode.EAGER)

        # Check reason counts
        stats = self.manager.get_stats()
        assert stats.total_deopts == 4
        assert len(stats.reason_counts) >= 4

    def test_state_reconstruction_correctness(self):
        """Test that reconstructed state is valid."""
        # Register function with deopt info
        mock_code = Mock()
        mock_code.deopt_info = {
            50: DeoptInfo(
                deopt_id=1,
                bytecode_offset=50,
                value_map={
                    "local0": ValueLocation("register", "rax", "int"),
                    "local1": ValueLocation("stack", 0, "int"),
                },
                frame_size=2,
                reason=DeoptReason.GUARD_FAILURE
            )
        }
        self.manager.register_optimized_function(1, mock_code)

        # Deopt
        result = self.manager.deoptimize(1, 50, DeoptReason.GUARD_FAILURE, DeoptMode.EAGER)

        # Verify correctness
        assert result is not None
        assert result.frame.bytecode_offset == 50

    def test_deopt_without_metadata(self):
        """Test deopt when no metadata is available (fallback)."""
        # Register function without deopt info
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        # Deopt anyway (should use fallback)
        result = self.manager.deoptimize(1, 100, DeoptReason.GUARD_FAILURE, DeoptMode.EAGER)

        # Should still work with minimal frame
        assert result is not None
        assert result.frame.bytecode_offset == 100
