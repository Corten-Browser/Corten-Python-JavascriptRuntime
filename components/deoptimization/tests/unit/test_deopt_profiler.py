"""Tests for deoptimization profiler."""
import pytest
from components.deoptimization.src.deopt_profiler import DeoptProfiler
from components.deoptimization.src.deopt_types import DeoptReason


class TestDeoptProfiler:
    def setup_method(self):
        self.profiler = DeoptProfiler()

    def test_create_profiler(self):
        assert self.profiler is not None

    def test_record_deopt(self):
        self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, 100)
        stats = self.profiler.get_stats()
        assert stats.total_deopts == 1

    def test_record_multiple_deopts(self):
        for i in range(10):
            self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, i * 10)
        stats = self.profiler.get_stats()
        assert stats.total_deopts == 10

    def test_get_stats_empty(self):
        stats = self.profiler.get_stats()
        assert stats.total_deopts == 0

    def test_reason_counting(self):
        self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, 10)
        self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, 20)
        self.profiler.record_deopt(1, DeoptReason.TYPE_MISMATCH, 30)
        stats = self.profiler.get_stats()
        assert stats.reason_counts[DeoptReason.GUARD_FAILURE] == 2
        assert stats.reason_counts[DeoptReason.TYPE_MISMATCH] == 1

    def test_get_hot_deopts_empty(self):
        hotspots = self.profiler.get_hot_deopts(threshold=10)
        assert len(hotspots) == 0

    def test_get_hot_deopts_identifies_hotspots(self):
        for i in range(150):
            self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, 100)
        hotspots = self.profiler.get_hot_deopts(threshold=100)
        assert len(hotspots) >= 1

    def test_get_hot_deopts_threshold(self):
        for i in range(50):
            self.profiler.record_deopt(1, DeoptReason.GUARD_FAILURE, 100)
        hotspots = self.profiler.get_hot_deopts(threshold=100)
        assert len(hotspots) == 0  # Below threshold
