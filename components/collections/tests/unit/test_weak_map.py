"""
Unit tests for WeakMap implementation.

Requirements:
- FR-P3-040: WeakMap constructor and methods
- FR-P3-041: WeakMap garbage collection behavior (weak references)
- FR-P3-050: WeakMap object-only keys

WeakMap restrictions:
- Keys must be objects (primitives throw TypeError)
- Not enumerable (no size, no iteration)
- Weak references (entries GC'd when key unreachable)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestWeakMapConstructor:
    """Test WeakMap constructor."""

    def test_create_empty_weak_map(self):
        """Test creating an empty WeakMap."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        # WeakMap has no size property

    def test_create_weak_map_from_iterable(self):
        """Test creating WeakMap from iterable of [key, value] pairs."""
        from components.collections.src.weak_map import WeakMap

        obj1 = {"id": 1}
        obj2 = {"id": 2}
        entries = [(obj1, "value1"), (obj2, "value2")]
        wm = WeakMap(entries)

        assert wm.get(obj1) == "value1"
        assert wm.get(obj2) == "value2"


class TestWeakMapBasicOperations:
    """Test basic WeakMap operations."""

    def test_set_and_get(self):
        """Test set() and get() methods."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        result = wm.set(obj, "value")

        assert result is wm  # set() returns this
        assert wm.get(obj) == "value"

    def test_set_multiple_entries(self):
        """Test setting multiple entries."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj1 = {"id": 1}
        obj2 = {"id": 2}
        obj3 = {"id": 3}

        wm.set(obj1, "value1")
        wm.set(obj2, "value2")
        wm.set(obj3, "value3")

        assert wm.get(obj1) == "value1"
        assert wm.get(obj2) == "value2"
        assert wm.get(obj3) == "value3"

    def test_update_existing_key(self):
        """Test updating existing key."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        wm.set(obj, "value1")
        wm.set(obj, "value2")

        assert wm.get(obj) == "value2"

    def test_get_nonexistent_key(self):
        """Test get() returns undefined for non-existent key."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        assert wm.get(obj) is None  # undefined in JS

    def test_has_method(self):
        """Test has() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        wm.set(obj, "value")

        assert wm.has(obj) is True
        assert wm.has({"other": "obj"}) is False

    def test_delete_method(self):
        """Test delete() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj1 = {"id": 1}
        obj2 = {"id": 2}

        wm.set(obj1, "value1")
        wm.set(obj2, "value2")

        assert wm.delete(obj1) is True
        assert wm.has(obj1) is False
        assert wm.delete({"nonexistent": "obj"}) is False


class TestWeakMapObjectOnlyKeys:
    """Test WeakMap only accepts objects as keys (FR-P3-050)."""

    def test_primitive_number_key_throws_error(self):
        """Test that primitive number keys throw TypeError."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        with pytest.raises(TypeError, match="Invalid value used as weak map key"):
            wm.set(42, "value")

    def test_primitive_string_key_throws_error(self):
        """Test that primitive string keys throw TypeError."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        with pytest.raises(TypeError, match="Invalid value used as weak map key"):
            wm.set("string", "value")

    def test_primitive_boolean_key_throws_error(self):
        """Test that primitive boolean keys throw TypeError."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        with pytest.raises(TypeError, match="Invalid value used as weak map key"):
            wm.set(True, "value")

    def test_none_key_throws_error(self):
        """Test that None/null keys throw TypeError."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        with pytest.raises(TypeError, match="Invalid value used as weak map key"):
            wm.set(None, "value")

    def test_object_key_is_accepted(self):
        """Test that object keys are accepted."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        wm.set(obj, "value")  # Should not throw
        assert wm.get(obj) == "value"

    def test_list_key_is_accepted(self):
        """Test that lists (objects in JS) are accepted as keys."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        lst = [1, 2, 3]
        wm.set(lst, "value")
        assert wm.get(lst) == "value"

    def test_function_key_is_accepted(self):
        """Test that functions are accepted as keys."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        fn = lambda x: x
        wm.set(fn, "value")
        assert wm.get(fn) == "value"


class TestWeakMapNotEnumerable:
    """Test WeakMap is not enumerable."""

    def test_no_size_property(self):
        """Test WeakMap has no size property."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        wm.set({"a": 1}, "value")

        # WeakMap should not have size property
        assert not hasattr(wm, 'size')

    def test_no_keys_method(self):
        """Test WeakMap has no keys() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        # WeakMap should not have keys() method for iteration
        assert not hasattr(wm, 'keys')

    def test_no_values_method(self):
        """Test WeakMap has no values() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        # WeakMap should not have values() method for iteration
        assert not hasattr(wm, 'values')

    def test_no_entries_method(self):
        """Test WeakMap has no entries() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        # WeakMap should not have entries() method for iteration
        assert not hasattr(wm, 'entries')

    def test_no_foreach_method(self):
        """Test WeakMap has no forEach() method."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        # WeakMap should not have forEach() method
        assert not hasattr(wm, 'forEach')

    def test_not_iterable(self):
        """Test WeakMap is not iterable."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        wm.set({"a": 1}, "value")

        # WeakMap should not be iterable
        # Attempting to iterate should not work like Map/Set
        # (In Python, we just don't implement __iter__)


class TestWeakMapValueTypes:
    """Test WeakMap with various value types."""

    def test_object_as_value(self):
        """Test storing objects as values."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        key = {"key": 1}
        value = {"value": "obj"}

        wm.set(key, value)
        assert wm.get(key) == value

    def test_primitive_values_allowed(self):
        """Test that primitive values are allowed (only keys must be objects)."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        key = {"key": 1}

        wm.set(key, 42)
        assert wm.get(key) == 42

        wm.set(key, "string")
        assert wm.get(key) == "string"

        wm.set(key, True)
        assert wm.get(key) is True

        wm.set(key, None)
        assert wm.get(key) is None


class TestWeakMapEdgeCases:
    """Test edge cases."""

    def test_same_object_different_references(self):
        """Test that same object content but different references are different keys."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj1 = {"id": 1}
        obj2 = {"id": 1}  # Same content, different reference

        wm.set(obj1, "value1")
        wm.set(obj2, "value2")

        assert wm.get(obj1) == "value1"
        assert wm.get(obj2) == "value2"

    def test_none_as_value(self):
        """Test None/undefined as value."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        key = {"key": 1}
        wm.set(key, None)

        assert wm.has(key) is True
        assert wm.get(key) is None


class TestWeakMapGarbageCollection:
    """Test WeakMap garbage collection behavior (FR-P3-041).

    Note: Full GC integration requires memory_gc component.
    These tests verify the API, not actual weak reference behavior.
    """

    def test_weak_references_note(self):
        """Note that weak reference behavior requires GC integration."""
        from components.collections.src.weak_map import WeakMap

        wm = WeakMap()
        obj = {"key": "test"}
        wm.set(obj, "value")

        # When obj goes out of scope and is GC'd, the entry should be removed
        # This requires integration with memory_gc component
        # For now, we just test the API is correct
        assert wm.has(obj) is True
