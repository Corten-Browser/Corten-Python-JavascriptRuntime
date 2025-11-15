"""
Unit tests for base InlineCache class (RED phase).

Tests verify inline cache initialization, state transitions, and cache operations.
"""
import pytest
from components.inline_caching.src.inline_cache import InlineCache
from components.inline_caching.src.ic_state import ICState
from components.inline_caching.src._shape_placeholder import Shape


class TestInlineCacheInitialization:
    """Test InlineCache initialization."""

    def test_inline_cache_initializes_as_uninitialized(self):
        """
        Given a new InlineCache
        When created with a cache type
        Then it should start in UNINITIALIZED state
        """
        ic = InlineCache("property_load")
        assert ic.get_state() == ICState.UNINITIALIZED

    def test_inline_cache_stores_cache_type(self):
        """
        Given a new InlineCache
        When created with cache_type "property_load"
        Then it should store that type
        """
        ic = InlineCache("property_load")
        assert ic.cache_type == "property_load"

    def test_inline_cache_has_empty_cache_slots(self):
        """
        Given a new InlineCache
        When created
        Then cache slots should be empty
        """
        ic = InlineCache("property_store")
        # Monomorphic cache should be None
        # Polymorphic cache should be empty list
        assert ic._mono_shape is None
        assert ic._poly_cache == []


class TestInlineCacheMonomorphic:
    """Test monomorphic inline cache (single shape)."""

    def test_check_returns_false_for_uninitialized_cache(self):
        """
        Given an uninitialized InlineCache
        When checking with any shape
        Then it should return False (cache miss)
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})
        assert ic.check(shape) is False

    def test_update_transitions_to_monomorphic_on_first_shape(self):
        """
        Given an uninitialized InlineCache
        When updating with a shape
        Then it should transition to MONOMORPHIC state
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})

        ic.update(shape, offset=0)

        assert ic.get_state() == ICState.MONOMORPHIC

    def test_check_returns_true_for_cached_shape_in_monomorphic(self):
        """
        Given a monomorphic InlineCache with cached shape
        When checking with the same shape
        Then it should return True (cache hit)
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})
        ic.update(shape, offset=0)

        assert ic.check(shape) is True

    def test_check_returns_false_for_different_shape_in_monomorphic(self):
        """
        Given a monomorphic InlineCache with one cached shape
        When checking with a different shape
        Then it should return False (cache miss)
        """
        ic = InlineCache("property_load")
        shape1 = Shape({"x": 0})
        shape2 = Shape({"y": 1})

        ic.update(shape1, offset=0)

        assert ic.check(shape2) is False


class TestInlineCachePolymorphic:
    """Test polymorphic inline cache (2-4 shapes)."""

    def test_update_with_second_shape_transitions_to_polymorphic(self):
        """
        Given a monomorphic InlineCache
        When updating with a second different shape
        Then it should transition to POLYMORPHIC state
        """
        ic = InlineCache("property_load")
        shape1 = Shape({"x": 0})
        shape2 = Shape({"y": 1})

        ic.update(shape1, offset=0)
        ic.update(shape2, offset=1)

        assert ic.get_state() == ICState.POLYMORPHIC

    def test_polymorphic_cache_handles_up_to_4_shapes(self):
        """
        Given a polymorphic InlineCache
        When updating with up to 4 different shapes
        Then all shapes should be cached
        """
        ic = InlineCache("property_load")
        shapes = [
            Shape({"a": 0}),
            Shape({"b": 1}),
            Shape({"c": 2}),
            Shape({"d": 3})
        ]

        for i, shape in enumerate(shapes):
            ic.update(shape, offset=i)

        # All 4 shapes should hit
        for shape in shapes:
            assert ic.check(shape) is True

        assert ic.get_state() == ICState.POLYMORPHIC

    def test_polymorphic_check_returns_true_for_any_cached_shape(self):
        """
        Given a polymorphic InlineCache with multiple shapes
        When checking with any cached shape
        Then it should return True
        """
        ic = InlineCache("property_load")
        shape1 = Shape({"x": 0})
        shape2 = Shape({"y": 1})

        ic.update(shape1, offset=0)
        ic.update(shape2, offset=1)

        assert ic.check(shape1) is True
        assert ic.check(shape2) is True


class TestInlineCacheMegamorphic:
    """Test megamorphic inline cache (>4 shapes)."""

    def test_update_with_fifth_shape_transitions_to_megamorphic(self):
        """
        Given a polymorphic InlineCache with 4 shapes
        When updating with a fifth shape
        Then it should transition to MEGAMORPHIC state
        """
        ic = InlineCache("property_load")
        shapes = [Shape({f"prop{i}": i}) for i in range(5)]

        for i, shape in enumerate(shapes):
            ic.update(shape, offset=i)

        assert ic.get_state() == ICState.MEGAMORPHIC

    def test_megamorphic_always_returns_false_on_check(self):
        """
        Given a megamorphic InlineCache
        When checking with any shape
        Then it should return False (uses slow path)
        """
        ic = InlineCache("property_load")
        shapes = [Shape({f"prop{i}": i}) for i in range(6)]

        for i, shape in enumerate(shapes):
            ic.update(shape, offset=i)

        # Megamorphic cache always misses (fallback to dict lookup)
        for shape in shapes:
            assert ic.check(shape) is False

    def test_megamorphic_state_is_permanent(self):
        """
        Given a megamorphic InlineCache
        When updating with more shapes
        Then it should remain MEGAMORPHIC
        """
        ic = InlineCache("property_load")

        # Add 10 shapes
        for i in range(10):
            shape = Shape({f"prop{i}": i})
            ic.update(shape, offset=i)

        assert ic.get_state() == ICState.MEGAMORPHIC


class TestInlineCacheInvalidation:
    """Test inline cache invalidation."""

    def test_invalidate_resets_to_uninitialized(self):
        """
        Given an InlineCache in any state
        When invalidate() is called
        Then it should reset to UNINITIALIZED
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})
        ic.update(shape, offset=0)

        ic.invalidate()

        assert ic.get_state() == ICState.UNINITIALIZED

    def test_invalidate_clears_monomorphic_cache(self):
        """
        Given a monomorphic InlineCache
        When invalidate() is called
        Then cached shape should be cleared
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})
        ic.update(shape, offset=0)

        ic.invalidate()

        assert ic.check(shape) is False

    def test_invalidate_clears_polymorphic_cache(self):
        """
        Given a polymorphic InlineCache
        When invalidate() is called
        Then all cached shapes should be cleared
        """
        ic = InlineCache("property_load")
        shape1 = Shape({"x": 0})
        shape2 = Shape({"y": 1})
        ic.update(shape1, offset=0)
        ic.update(shape2, offset=1)

        ic.invalidate()

        assert ic.check(shape1) is False
        assert ic.check(shape2) is False


class TestInlineCacheOffset:
    """Test cached offset retrieval."""

    def test_get_cached_offset_returns_none_for_uninitialized(self):
        """
        Given an uninitialized InlineCache
        When getting cached offset
        Then it should return None
        """
        ic = InlineCache("property_load")
        assert ic.get_cached_offset() is None

    def test_get_cached_offset_returns_offset_for_monomorphic(self):
        """
        Given a monomorphic InlineCache
        When getting cached offset
        Then it should return the cached offset
        """
        ic = InlineCache("property_load")
        shape = Shape({"x": 0})
        ic.update(shape, offset=42)

        offset = ic.get_cached_offset()
        assert offset == 42

    def test_get_cached_offset_with_shape_for_polymorphic(self):
        """
        Given a polymorphic InlineCache
        When getting cached offset for a specific shape
        Then it should return the correct offset
        """
        ic = InlineCache("property_load")
        shape1 = Shape({"x": 0})
        shape2 = Shape({"y": 1})

        ic.update(shape1, offset=10)
        ic.update(shape2, offset=20)

        assert ic.get_cached_offset(shape1) == 10
        assert ic.get_cached_offset(shape2) == 20
