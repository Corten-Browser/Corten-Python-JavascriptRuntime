"""
Unit tests for CallIC (BDD style).

Tests verify function call optimization with inline caching.
"""
import pytest
from components.inline_caching.src.call_ic import CallIC


class TestCallIC:
    """Test CallIC for optimized function calls."""

    def test_call_ic_caches_function_calls(self):
        """
        Given a CallIC
        When calling the same function multiple times
        Then subsequent calls should hit the cache
        """
        ic = CallIC()

        def add(a, b):
            return a + b

        # First call: miss
        result1 = ic.call(add, [1, 2])
        assert result1 == 3

        # Subsequent calls: hits
        result2 = ic.call(add, [3, 4])
        result3 = ic.call(add, [5, 6])

        assert result2 == 7
        assert result3 == 11

        stats = ic.get_statistics()
        assert stats['hits'] >= 2
        assert stats['misses'] == 1

    def test_call_ic_handles_different_functions(self):
        """
        Given a CallIC
        When calling different functions
        Then each should be a cache miss initially
        """
        ic = CallIC()

        def add(a, b):
            return a + b

        def multiply(a, b):
            return a * b

        # Different functions = cache misses
        ic.call(add, [1, 2])
        ic.call(multiply, [3, 4])

        stats = ic.get_statistics()
        assert stats['misses'] >= 2

    def test_call_ic_handles_no_arguments(self):
        """
        Given a CallIC
        When calling a function with no arguments
        Then it should work correctly
        """
        ic = CallIC()

        def get_value():
            return 42

        result = ic.call(get_value, [])
        assert result == 42


class TestCallICStatistics:
    """Test CallIC statistics tracking."""

    def test_call_ic_tracks_hit_rate(self):
        """
        Given a CallIC with multiple calls
        When calculating statistics
        Then hit rate should be accurate
        """
        ic = CallIC()

        def func():
            return 1

        # 1 miss, 9 hits
        for _ in range(10):
            ic.call(func, [])

        stats = ic.get_statistics()
        assert stats['hit_rate'] > 0.8  # Should be ~90%
