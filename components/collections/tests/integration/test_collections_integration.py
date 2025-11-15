"""
Integration tests for collections component.

Tests cross-collection interactions and real-world usage patterns.
Requirements covered: FR-P3-036 to FR-P3-050
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestMapSetInteroperation:
    """Test Map and Set working together."""

    def test_map_of_sets(self):
        """Test using Sets as values in a Map."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        users_by_role = Map()
        users_by_role.set("admin", Set(["alice", "bob"]))
        users_by_role.set("user", Set(["charlie", "david"]))

        admins = users_by_role.get("admin")
        assert admins.has("alice") is True
        assert admins.size == 2

    def test_set_of_maps(self):
        """Test using Maps in a Set (by reference)."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        config1 = Map([("theme", "dark"), ("lang", "en")])
        config2 = Map([("theme", "light"), ("lang", "es")])

        configs = Set()
        configs.add(config1)
        configs.add(config2)

        assert configs.size == 2
        assert configs.has(config1) is True


class TestCollectionsWithComplexData:
    """Test collections with complex data structures."""

    def test_map_with_nested_structures(self):
        """Test Map with nested objects and arrays."""
        from components.collections.src.map import Map

        data = Map()
        user = {
            "name": "Alice",
            "roles": ["admin", "moderator"],
            "settings": {"theme": "dark", "notifications": True}
        }
        data.set("user:1", user)

        retrieved = data.get("user:1")
        assert retrieved["name"] == "Alice"
        assert "admin" in retrieved["roles"]

    def test_set_with_objects_preserves_order(self):
        """Test Set with objects maintains insertion order."""
        from components.collections.src.set import Set

        s = Set()
        obj1 = {"id": 1, "name": "first"}
        obj2 = {"id": 2, "name": "second"}
        obj3 = {"id": 3, "name": "third"}

        s.add(obj1)
        s.add(obj2)
        s.add(obj3)

        values = list(s.values())
        assert values[0] is obj1
        assert values[1] is obj2
        assert values[2] is obj3


class TestWeakCollectionsWithRegularCollections:
    """Test weak collections interacting with regular collections."""

    def test_weak_map_with_map_keys(self):
        """Test WeakMap using Map objects as keys."""
        from components.collections.src.weak_map import WeakMap
        from components.collections.src.map import Map

        wm = WeakMap()
        config = Map([("key", "value")])
        wm.set(config, "config metadata")

        assert wm.get(config) == "config metadata"

    def test_weak_set_with_set_values(self):
        """Test WeakSet using Set objects as values."""
        from components.collections.src.weak_set import WeakSet
        from components.collections.src.set import Set

        ws = WeakSet()
        s = Set([1, 2, 3])
        ws.add(s)

        assert ws.has(s) is True


class TestIterationPatterns:
    """Test various iteration patterns."""

    def test_map_iteration_with_destructuring(self):
        """Test Map iteration with destructuring."""
        from components.collections.src.map import Map

        m = Map([("a", 1), ("b", 2), ("c", 3)])

        keys = []
        values = []
        for key, value in m:
            keys.append(key)
            values.append(value)

        assert keys == ["a", "b", "c"]
        assert values == [1, 2, 3]

    def test_set_iteration_with_filtering(self):
        """Test Set iteration with filtering."""
        from components.collections.src.set import Set

        s = Set([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        evens = Set()
        for value in s:
            if value % 2 == 0:
                evens.add(value)

        assert evens.size == 5
        assert evens.has(2) is True
        assert evens.has(4) is True


class TestMapSetConversions:
    """Test converting between Map and Set."""

    def test_map_keys_to_set(self):
        """Test converting Map keys to Set."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        m = Map([("a", 1), ("b", 2), ("c", 3), ("a", 4)])  # Duplicate key

        keys_set = Set(m.keys())
        assert keys_set.size == 3  # Only unique keys

    def test_set_to_map_with_indices(self):
        """Test converting Set to Map with indices."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        s = Set(["apple", "banana", "cherry"])

        m = Map()
        for i, value in enumerate(s):
            m.set(i, value)

        assert m.get(0) == "apple"
        assert m.size == 3


class TestForEachWithModifications:
    """Test forEach behavior when modifying collections."""

    def test_map_foreach_with_accumulation(self):
        """Test Map forEach for accumulation patterns."""
        from components.collections.src.map import Map

        prices = Map([("apple", 1.5), ("banana", 0.8), ("cherry", 2.0)])

        total = [0]  # Use list for closure

        def add_price(value, key, map_obj):
            total[0] += value

        prices.forEach(add_price)
        assert total[0] == 4.3

    def test_set_foreach_with_transformation(self):
        """Test Set forEach for transformation patterns."""
        from components.collections.src.set import Set

        numbers = Set([1, 2, 3, 4, 5])

        squared = []

        def square_value(value, value2, set_obj):
            squared.append(value * value)

        numbers.forEach(square_value)
        assert squared == [1, 4, 9, 16, 25]


class TestSameValueZeroAcrossCollections:
    """Test SameValueZero behavior across collections."""

    def test_nan_consistency_map_and_set(self):
        """Test NaN handling is consistent between Map and Set."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        nan = float('nan')

        m = Map()
        m.set(nan, "value")
        assert m.has(nan) is True

        s = Set()
        s.add(nan)
        assert s.has(nan) is True

    def test_zero_consistency_map_and_set(self):
        """Test +0/-0 handling is consistent between Map and Set."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        m = Map()
        m.set(0.0, "zero")
        m.set(-0.0, "negative zero")
        assert m.size == 1  # Same key

        s = Set()
        s.add(0.0)
        s.add(-0.0)
        assert s.size == 1  # Same value


class TestChainableOperations:
    """Test method chaining."""

    def test_map_chaining(self):
        """Test Map method chaining."""
        from components.collections.src.map import Map

        m = Map().set("a", 1).set("b", 2).set("c", 3)

        assert m.size == 3
        assert m.get("b") == 2

    def test_set_chaining(self):
        """Test Set method chaining."""
        from components.collections.src.set import Set

        s = Set().add(1).add(2).add(3)

        assert s.size == 3
        assert s.has(2) is True

    def test_weak_map_chaining(self):
        """Test WeakMap method chaining."""
        from components.collections.src.weak_map import WeakMap

        obj1 = {"a": 1}
        obj2 = {"b": 2}

        wm = WeakMap().set(obj1, "val1").set(obj2, "val2")

        assert wm.get(obj1) == "val1"

    def test_weak_set_chaining(self):
        """Test WeakSet method chaining."""
        from components.collections.src.weak_set import WeakSet

        obj1 = {"a": 1}
        obj2 = {"b": 2}

        ws = WeakSet().add(obj1).add(obj2)

        assert ws.has(obj1) is True


class TestLargeScaleOperations:
    """Test collections with large amounts of data."""

    def test_map_with_large_dataset(self):
        """Test Map with thousands of entries."""
        from components.collections.src.map import Map

        m = Map()
        for i in range(10000):
            m.set(f"key{i}", i * 2)

        assert m.size == 10000
        assert m.get("key5000") == 10000
        assert m.has("key9999") is True

    def test_set_with_large_dataset(self):
        """Test Set with thousands of values."""
        from components.collections.src.set import Set

        s = Set()
        for i in range(10000):
            s.add(i)

        assert s.size == 10000
        assert s.has(5000) is True

    def test_map_iteration_order_with_large_dataset(self):
        """Test insertion order is preserved with many entries."""
        from components.collections.src.map import Map

        m = Map()
        for i in range(1000):
            m.set(i, i * 10)

        keys = list(m.keys())
        assert keys == list(range(1000))


class TestEdgeCasesIntegration:
    """Test edge cases across collections."""

    def test_map_and_set_with_mixed_types(self):
        """Test Map and Set with mixed key/value types."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        m = Map()
        m.set(1, "number")
        m.set("1", "string")
        m.set(True, "boolean")
        m.set(None, "null")
        m.set({"obj": 1}, "object")

        assert m.size == 5

        s = Set()
        s.add(1)
        s.add("1")
        s.add(True)
        s.add(None)
        s.add({"obj": 1})

        assert s.size == 5

    def test_clear_and_rebuild(self):
        """Test clearing and rebuilding collections."""
        from components.collections.src.map import Map
        from components.collections.src.set import Set

        m = Map([("a", 1), ("b", 2)])
        m.clear()
        assert m.size == 0

        m.set("x", 10)
        assert m.size == 1

        s = Set([1, 2, 3])
        s.clear()
        assert s.size == 0

        s.add(100)
        assert s.size == 1
