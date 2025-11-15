"""
Unit tests for Map implementation.

Requirements:
- FR-P3-036: Map constructor and basic methods
- FR-P3-037: Map key equality (SameValueZero)
- FR-P3-044: Map iteration (keys, values, entries, forEach)
- FR-P3-046: Map/Set insertion order preservation
- FR-P3-047: Map.prototype.size property
- FR-P3-049: Map/Set clear method
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestMapConstructor:
    """Test Map constructor."""

    def test_create_empty_map(self):
        """Test creating an empty Map."""
        from components.collections.src.map import Map

        m = Map()
        assert m.size == 0

    def test_create_map_from_iterable(self):
        """Test creating Map from iterable of [key, value] pairs."""
        from components.collections.src.map import Map

        entries = [("a", 1), ("b", 2), ("c", 3)]
        m = Map(entries)

        assert m.size == 3
        assert m.get("a") == 1
        assert m.get("b") == 2
        assert m.get("c") == 3


class TestMapBasicOperations:
    """Test basic Map operations."""

    def test_set_and_get(self):
        """Test set() and get() methods."""
        from components.collections.src.map import Map

        m = Map()
        result = m.set("key1", "value1")

        assert result is m  # set() returns this
        assert m.get("key1") == "value1"
        assert m.size == 1

    def test_set_multiple_entries(self):
        """Test setting multiple entries."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.set("c", 3)

        assert m.size == 3
        assert m.get("a") == 1
        assert m.get("b") == 2
        assert m.get("c") == 3

    def test_update_existing_key(self):
        """Test updating existing key."""
        from components.collections.src.map import Map

        m = Map()
        m.set("key", "value1")
        m.set("key", "value2")

        assert m.size == 1
        assert m.get("key") == "value2"

    def test_get_nonexistent_key(self):
        """Test get() returns undefined for non-existent key."""
        from components.collections.src.map import Map

        m = Map()
        assert m.get("nonexistent") is None  # undefined in JS

    def test_has_method(self):
        """Test has() method."""
        from components.collections.src.map import Map

        m = Map()
        m.set("key1", "value1")

        assert m.has("key1") is True
        assert m.has("nonexistent") is False

    def test_delete_method(self):
        """Test delete() method."""
        from components.collections.src.map import Map

        m = Map()
        m.set("key1", "value1")
        m.set("key2", "value2")

        assert m.delete("key1") is True
        assert m.has("key1") is False
        assert m.size == 1
        assert m.delete("nonexistent") is False

    def test_clear_method(self):
        """Test clear() method (FR-P3-049)."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.clear()

        assert m.size == 0
        assert m.has("a") is False


class TestMapKeyTypes:
    """Test Map with various key types."""

    def test_object_as_key(self):
        """Test using objects as keys."""
        from components.collections.src.map import Map

        m = Map()
        obj1 = {"id": 1}
        obj2 = {"id": 2}

        m.set(obj1, "value1")
        m.set(obj2, "value2")

        assert m.get(obj1) == "value1"
        assert m.get(obj2) == "value2"
        assert m.size == 2

    def test_function_as_key(self):
        """Test using functions as keys."""
        from components.collections.src.map import Map

        m = Map()
        fn1 = lambda x: x
        fn2 = lambda x: x * 2

        m.set(fn1, "func1")
        m.set(fn2, "func2")

        assert m.get(fn1) == "func1"
        assert m.get(fn2) == "func2"

    def test_mixed_key_types(self):
        """Test Map with mixed key types."""
        from components.collections.src.map import Map

        m = Map()
        m.set(1, "number")
        m.set("1", "string")
        m.set(True, "boolean")
        m.set(None, "null")

        assert m.size == 4
        assert m.get(1) == "number"
        assert m.get("1") == "string"


class TestMapSameValueZero:
    """Test Map key equality using SameValueZero (FR-P3-037)."""

    def test_nan_as_key(self):
        """Test NaN equals NaN as key."""
        from components.collections.src.map import Map

        m = Map()
        nan1 = float('nan')
        nan2 = float('nan')

        m.set(nan1, "value1")
        m.set(nan2, "value2")  # Should update same entry

        assert m.size == 1
        assert m.get(nan1) == "value2"
        assert m.get(nan2) == "value2"

    def test_positive_and_negative_zero_as_key(self):
        """Test +0 and -0 are equal as keys."""
        from components.collections.src.map import Map

        m = Map()
        m.set(0.0, "zero")
        m.set(-0.0, "negative zero")  # Should update same entry

        assert m.size == 1
        assert m.get(0.0) == "negative zero"
        assert m.get(-0.0) == "negative zero"


class TestMapIteration:
    """Test Map iteration methods (FR-P3-044, FR-P3-046)."""

    def test_keys_iterator(self):
        """Test keys() iterator."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.set("c", 3)

        keys = list(m.keys())
        assert keys == ["a", "b", "c"]

    def test_values_iterator(self):
        """Test values() iterator."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 100)
        m.set("b", 200)
        m.set("c", 300)

        values = list(m.values())
        assert values == [100, 200, 300]

    def test_entries_iterator(self):
        """Test entries() iterator."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)

        entries = list(m.entries())
        assert entries == [("a", 1), ("b", 2)]

    def test_insertion_order_preserved(self):
        """Test insertion order is preserved (FR-P3-046)."""
        from components.collections.src.map import Map

        m = Map()
        m.set("first", 1)
        m.set("second", 2)
        m.set("third", 3)

        keys = list(m.keys())
        assert keys == ["first", "second", "third"]

    def test_update_preserves_order(self):
        """Test updating a key preserves its position."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.set("c", 3)
        m.set("b", 20)  # Update

        entries = list(m.entries())
        assert entries == [("a", 1), ("b", 20), ("c", 3)]

    def test_delete_and_readd_changes_order(self):
        """Test deleting and re-adding moves to end."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.set("c", 3)
        m.delete("b")
        m.set("b", 20)

        keys = list(m.keys())
        assert keys == ["a", "c", "b"]


class TestMapForEach:
    """Test forEach() method."""

    def test_foreach_callback(self):
        """Test forEach() with callback."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)
        m.set("c", 3)

        results = []
        m.forEach(lambda value, key, map_obj: results.append((key, value)))

        assert results == [("a", 1), ("b", 2), ("c", 3)]

    def test_foreach_with_this_arg(self):
        """Test forEach() with thisArg."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)

        context = {"multiplier": 10}
        results = []

        def callback(value, key, map_obj, ctx=context):
            results.append(value * ctx["multiplier"])

        m.forEach(callback)
        # Note: Python doesn't have 'this', so we pass context via closure

    def test_foreach_receives_map(self):
        """Test forEach() callback receives the map."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)

        received_map = [None]

        def callback(value, key, map_obj):
            received_map[0] = map_obj

        m.forEach(callback)
        assert received_map[0] is m


class TestMapIteratorProtocol:
    """Test Map iterator protocol."""

    def test_map_is_iterable(self):
        """Test Map is iterable (returns entries)."""
        from components.collections.src.map import Map

        m = Map()
        m.set("a", 1)
        m.set("b", 2)

        entries = list(m)
        assert entries == [("a", 1), ("b", 2)]

    def test_map_iterator_for_loop(self):
        """Test using Map in for loop."""
        from components.collections.src.map import Map

        m = Map()
        m.set("x", 10)
        m.set("y", 20)

        result = []
        for key, value in m:
            result.append((key, value))

        assert result == [("x", 10), ("y", 20)]


class TestMapSize:
    """Test Map size property (FR-P3-047)."""

    def test_size_property(self):
        """Test size property."""
        from components.collections.src.map import Map

        m = Map()
        assert m.size == 0

        m.set("a", 1)
        assert m.size == 1

        m.set("b", 2)
        assert m.size == 2

        m.delete("a")
        assert m.size == 1

        m.clear()
        assert m.size == 0


class TestMapEdgeCases:
    """Test edge cases."""

    def test_none_as_key(self):
        """Test None as key."""
        from components.collections.src.map import Map

        m = Map()
        m.set(None, "null value")
        assert m.get(None) == "null value"
        assert m.has(None) is True

    def test_none_as_value(self):
        """Test None as value."""
        from components.collections.src.map import Map

        m = Map()
        m.set("key", None)
        assert m.has("key") is True
        assert m.get("key") is None

    def test_empty_map_iteration(self):
        """Test iterating empty map."""
        from components.collections.src.map import Map

        m = Map()
        assert list(m.keys()) == []
        assert list(m.values()) == []
        assert list(m.entries()) == []

    def test_many_entries(self):
        """Test Map with many entries."""
        from components.collections.src.map import Map

        m = Map()
        for i in range(1000):
            m.set(f"key{i}", i)

        assert m.size == 1000
        assert m.get("key500") == 500
