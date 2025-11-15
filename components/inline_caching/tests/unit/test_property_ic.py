"""
Unit tests for PropertyLoadIC and PropertyStoreIC (RED phase).

Tests verify property load/store optimization with inline caching.
"""
import pytest
from components.inline_caching.src.property_ic import PropertyLoadIC, PropertyStoreIC
from components.inline_caching.src.ic_state import ICState
from components.inline_caching.src._shape_placeholder import Shape


class MockJSObject:
    """Mock JavaScript object for testing."""

    def __init__(self):
        """Initialize mock object."""
        self._properties = {}

    def get_property(self, name):
        """Get property by name."""
        return self._properties.get(name, MockUndefined())

    def set_property(self, name, value):
        """Set property by name."""
        self._properties[name] = value


class MockValue:
    """Mock JavaScript value."""

    def __init__(self, value):
        """Initialize with value."""
        self._value = value

    def to_smi(self):
        """Convert to small integer."""
        return self._value

    @staticmethod
    def from_smi(value):
        """Create from small integer."""
        return MockValue(value)


class MockUndefined:
    """Mock undefined value."""

    def __eq__(self, other):
        """Check equality."""
        return isinstance(other, MockUndefined)


@pytest.fixture
def gc():
    """Create garbage collector for tests (not needed for mocks)."""
    return None


class TestPropertyLoadIC:
    """Test PropertyLoadIC for optimized property access."""

    def test_property_load_ic_inherits_from_inline_cache(self):
        """
        Given PropertyLoadIC
        When checking its type
        Then it should be an InlineCache subclass
        """
        ic = PropertyLoadIC()
        assert ic.cache_type == "property_load"

    def test_load_from_uninitialized_ic_uses_slow_path(self, gc):
        """
        Given an uninitialized PropertyLoadIC
        When loading a property
        Then it should use slow path and initialize cache
        """
        ic = PropertyLoadIC()
        obj = MockJSObject()
        obj.set_property("x", MockValue.from_smi(42))

        # First access: slow path + cache initialization
        result = ic.load(obj, "x")

        assert result.to_smi() == 42
        assert ic.get_state() == ICState.MONOMORPHIC

    def test_load_monomorphic_cache_hit(self, gc):
        """
        Given a monomorphic PropertyLoadIC with cached shape
        When loading with same object shape
        Then it should use fast path (cache hit)
        """
        ic = PropertyLoadIC()
        obj = MockJSObject()
        obj.set_property("x", MockValue.from_smi(42))

        # Prime cache
        ic.load(obj, "x")

        # Second access: should hit cache
        obj.set_property("x", MockValue.from_smi(100))
        result = ic.load(obj, "x")

        assert result.to_smi() == 100
        assert ic.get_state() == ICState.MONOMORPHIC

    def test_load_polymorphic_cache_hit(self, gc):
        """
        Given a polymorphic PropertyLoadIC
        When loading with multiple object shapes
        Then it should handle all cached shapes
        """
        ic = PropertyLoadIC()

        # Create objects with different shapes
        obj1 = MockJSObject()
        obj1.set_property("x", MockValue.from_smi(1))

        obj2 = MockJSObject()
        obj2.set_property("y", MockValue.from_smi(2))
        obj2.set_property("x", MockValue.from_smi(20))

        # Prime polymorphic cache
        ic.load(obj1, "x")
        ic.load(obj2, "x")

        assert ic.get_state() == ICState.POLYMORPHIC

        # Both should hit cache
        assert ic.load(obj1, "x").to_smi() == 1
        assert ic.load(obj2, "x").to_smi() == 20

    def test_load_megamorphic_always_uses_slow_path(self, gc):
        """
        Given a megamorphic PropertyLoadIC
        When loading properties
        Then it should always use slow path
        """
        ic = PropertyLoadIC()

        # Create 5+ different shapes to trigger megamorphic
        for i in range(6):
            obj = MockJSObject()
            for j in range(i):
                obj.set_property(f"prop{j}", MockValue.from_smi(j))
            obj.set_property("x", MockValue.from_smi(i * 10))
            ic.load(obj, "x")

        assert ic.get_state() == ICState.MEGAMORPHIC

    def test_load_returns_undefined_for_missing_property(self, gc):
        """
        Given a PropertyLoadIC
        When loading a non-existent property
        Then it should return undefined
        """
        ic = PropertyLoadIC()
        obj = MockJSObject()

        result = ic.load(obj, "nonexistent")

        assert isinstance(result, MockUndefined)


class TestPropertyStoreIC:
    """Test PropertyStoreIC for optimized property writes."""

    def test_property_store_ic_inherits_from_inline_cache(self):
        """
        Given PropertyStoreIC
        When checking its type
        Then it should be an InlineCache subclass
        """
        ic = PropertyStoreIC()
        assert ic.cache_type == "property_store"

    def test_store_to_uninitialized_ic_uses_slow_path(self, gc):
        """
        Given an uninitialized PropertyStoreIC
        When storing a property
        Then it should use slow path and initialize cache
        """
        ic = PropertyStoreIC()
        obj = MockJSObject()

        # First store: slow path + cache initialization
        ic.store(obj, "x", MockValue.from_smi(42))

        assert obj.get_property("x").to_smi() == 42
        assert ic.get_state() == ICState.MONOMORPHIC

    def test_store_monomorphic_cache_hit(self, gc):
        """
        Given a monomorphic PropertyStoreIC with cached shape
        When storing to same object shape
        Then it should use fast path (cache hit)
        """
        ic = PropertyStoreIC()
        obj = MockJSObject()

        # Prime cache
        ic.store(obj, "x", MockValue.from_smi(42))

        # Second store: should hit cache
        ic.store(obj, "x", MockValue.from_smi(100))

        assert obj.get_property("x").to_smi() == 100
        assert ic.get_state() == ICState.MONOMORPHIC

    def test_store_polymorphic_cache_hit(self, gc):
        """
        Given a polymorphic PropertyStoreIC
        When storing to multiple object shapes
        Then it should handle all cached shapes
        """
        ic = PropertyStoreIC()

        # Create objects with different shapes
        obj1 = MockJSObject()
        obj1.set_property("x", MockValue.from_smi(0))

        obj2 = MockJSObject()
        obj2.set_property("y", MockValue.from_smi(0))
        obj2.set_property("x", MockValue.from_smi(0))

        # Prime polymorphic cache
        ic.store(obj1, "x", MockValue.from_smi(1))
        ic.store(obj2, "x", MockValue.from_smi(2))

        assert ic.get_state() == ICState.POLYMORPHIC

        # Verify stores worked
        assert obj1.get_property("x").to_smi() == 1
        assert obj2.get_property("x").to_smi() == 2

    def test_store_creates_new_property_if_missing(self, gc):
        """
        Given a PropertyStoreIC
        When storing to a non-existent property
        Then it should create the property
        """
        ic = PropertyStoreIC()
        obj = MockJSObject()

        ic.store(obj, "newprop", MockValue.from_smi(99))

        assert obj.get_property("newprop").to_smi() == 99


class TestPropertyICStatistics:
    """Test IC statistics tracking."""

    def test_property_load_ic_tracks_hit_count(self, gc):
        """
        Given a PropertyLoadIC
        When performing multiple loads
        Then it should track cache hits
        """
        ic = PropertyLoadIC()
        obj = MockJSObject()
        obj.set_property("x", MockValue.from_smi(42))

        # Prime cache
        ic.load(obj, "x")

        # Multiple cache hits
        for _ in range(10):
            ic.load(obj, "x")

        stats = ic.get_statistics()
        assert stats['hits'] >= 10

    def test_property_load_ic_tracks_miss_count(self, gc):
        """
        Given a PropertyLoadIC
        When encountering cache misses
        Then it should track misses
        """
        ic = PropertyLoadIC()

        # Create multiple objects with different shapes (cache misses)
        for i in range(5):
            obj = MockJSObject()
            for j in range(i):
                obj.set_property(f"p{j}", MockValue.from_smi(j))
            obj.set_property("x", MockValue.from_smi(i))
            ic.load(obj, "x")

        stats = ic.get_statistics()
        assert stats['misses'] > 0

    def test_property_ic_calculates_hit_rate(self, gc):
        """
        Given a PropertyLoadIC with hits and misses
        When calculating statistics
        Then it should provide hit rate percentage
        """
        ic = PropertyLoadIC()
        obj = MockJSObject()
        obj.set_property("x", MockValue.from_smi(42))

        # 1 miss (initial), 9 hits
        for _ in range(10):
            ic.load(obj, "x")

        stats = ic.get_statistics()
        assert 'hit_rate' in stats
        assert stats['hit_rate'] > 0.8  # Should be ~90%
