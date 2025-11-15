"""
Unit tests for GlobalIC (BDD style).

Tests verify global variable access optimization with inline caching.
"""
import pytest
from components.inline_caching.src.global_ic import GlobalIC


class TestGlobalIC:
    """Test GlobalIC for optimized global access."""

    def test_global_ic_loads_and_stores_globals(self):
        """
        Given a GlobalIC
        When loading and storing global variables
        Then values should be correct
        """
        ic = GlobalIC()

        # Store
        ic.store_global("x", 42)

        # Load
        value = ic.load_global("x")
        assert value == 42

    def test_global_ic_caches_global_loads(self):
        """
        Given a GlobalIC with a cached global
        When loading the same global multiple times
        Then subsequent loads should hit the cache
        """
        ic = GlobalIC()

        ic.store_global("count", 10)

        # Multiple loads
        for _ in range(5):
            value = ic.load_global("count")
            assert value == 10

        stats = ic.get_statistics()
        assert stats['load_hits'] >= 4  # First load is a miss

    def test_global_ic_returns_none_for_undefined(self):
        """
        Given a GlobalIC
        When loading a non-existent global
        Then it should return None
        """
        ic = GlobalIC()

        value = ic.load_global("undefined_var")
        assert value is None

    def test_global_ic_invalidates_cache(self):
        """
        Given a GlobalIC with cached globals
        When invalidating a global
        Then next load should be a cache miss
        """
        ic = GlobalIC()

        ic.store_global("x", 42)
        ic.load_global("x")  # Cache it

        # Invalidate
        ic.invalidate_global("x")

        # Next load is a miss
        initial_misses = ic.get_statistics()['load_misses']
        ic.load_global("x")
        assert ic.get_statistics()['load_misses'] > initial_misses


class TestGlobalICStatistics:
    """Test GlobalIC statistics tracking."""

    def test_global_ic_tracks_load_hit_rate(self):
        """
        Given a GlobalIC with loads
        When calculating statistics
        Then load hit rate should be accurate
        """
        ic = GlobalIC()

        ic.store_global("value", 123)

        # 1 miss, 9 hits
        for _ in range(10):
            ic.load_global("value")

        stats = ic.get_statistics()
        assert stats['load_hit_rate'] > 0.8  # Should be ~90%

    def test_global_ic_tracks_store_count(self):
        """
        Given a GlobalIC
        When storing globals
        Then store count should be tracked
        """
        ic = GlobalIC()

        ic.store_global("a", 1)
        ic.store_global("b", 2)
        ic.store_global("c", 3)

        stats = ic.get_statistics()
        assert stats['store_count'] == 3
