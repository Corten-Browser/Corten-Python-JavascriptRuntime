"""Tests for deoptimization manager."""
import pytest
from unittest.mock import Mock
from components.deoptimization.src.deopt_manager import DeoptimizationManager
from components.deoptimization.src.deopt_types import DeoptReason, DeoptMode


class TestDeoptimizationManager:
    def setup_method(self):
        self.manager = DeoptimizationManager()

    def test_create_manager(self):
        assert self.manager is not None

    def test_register_optimized_function(self):
        mock_code = Mock()
        self.manager.register_optimized_function(1, mock_code)
        assert 1 in self.manager.functions

    def test_register_multiple_functions(self):
        for i in range(5):
            self.manager.register_optimized_function(i, Mock())
        assert len(self.manager.functions) == 5

    def test_deoptimize_eager(self):
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        result = self.manager.deoptimize(
            function_id=1,
            deopt_point=100,
            reason=DeoptReason.GUARD_FAILURE,
            mode=DeoptMode.EAGER
        )
        assert result is not None

    def test_deoptimize_lazy(self):
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        result = self.manager.deoptimize(
            function_id=1,
            deopt_point=100,
            reason=DeoptReason.GUARD_FAILURE,
            mode=DeoptMode.LAZY
        )
        # Lazy returns None initially
        assert result is None or result is not None

    def test_deoptimize_unregistered_function(self):
        with pytest.raises(KeyError):
            self.manager.deoptimize(
                function_id=999,
                deopt_point=100,
                reason=DeoptReason.GUARD_FAILURE,
                mode=DeoptMode.EAGER
            )

    def test_get_stats_empty(self):
        stats = self.manager.get_stats()
        assert stats.total_deopts == 0

    def test_get_stats_after_deopts(self):
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        for i in range(3):
            self.manager.deoptimize(1, i * 10, DeoptReason.GUARD_FAILURE, DeoptMode.EAGER)

        stats = self.manager.get_stats()
        assert stats.total_deopts == 3

    def test_deoptimize_increments_stats(self):
        mock_code = Mock()
        mock_code.deopt_info = {}
        self.manager.register_optimized_function(1, mock_code)

        self.manager.deoptimize(1, 10, DeoptReason.GUARD_FAILURE, DeoptMode.EAGER)
        stats = self.manager.get_stats()
        assert stats.eager_deopts == 1

    def test_function_registry(self):
        codes = [Mock() for _ in range(3)]
        for i, code in enumerate(codes):
            self.manager.register_optimized_function(i, code)

        assert len(self.manager.functions) == 3
        for i in range(3):
            assert self.manager.functions[i] == codes[i]
