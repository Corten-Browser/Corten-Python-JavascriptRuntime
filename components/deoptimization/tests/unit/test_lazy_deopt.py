"""Tests for lazy deoptimization."""
import pytest
from components.deoptimization.src.lazy_deopt import LazyDeoptimizer
from components.deoptimization.src.deopt_types import DeoptReason


class TestLazyDeoptimizer:
    def setup_method(self):
        self.deoptimizer = LazyDeoptimizer()

    def test_create_lazy_deoptimizer(self):
        assert self.deoptimizer is not None

    def test_schedule_deopt(self):
        self.deoptimizer.schedule_deopt(
            function_id=1,
            deopt_point=100,
            reason=DeoptReason.GUARD_FAILURE
        )
        assert len(self.deoptimizer.pending) == 1

    def test_schedule_multiple_deopts(self):
        for i in range(5):
            self.deoptimizer.schedule_deopt(i, i * 10, DeoptReason.GUARD_FAILURE)
        assert len(self.deoptimizer.pending) == 5

    def test_process_pending_empty(self):
        results = self.deoptimizer.process_pending()
        assert len(results) == 0

    def test_process_pending_clears_queue(self):
        self.deoptimizer.schedule_deopt(1, 10, DeoptReason.GUARD_FAILURE)
        self.deoptimizer.process_pending()
        assert len(self.deoptimizer.pending) == 0

    def test_process_pending_returns_states(self):
        self.deoptimizer.schedule_deopt(1, 10, DeoptReason.GUARD_FAILURE)
        self.deoptimizer.schedule_deopt(2, 20, DeoptReason.TYPE_MISMATCH)
        results = self.deoptimizer.process_pending()
        assert len(results) == 2
