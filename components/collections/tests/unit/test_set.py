"""
Unit tests for Set implementation.

Requirements:
- FR-P3-038: Set constructor and basic methods
- FR-P3-039: Set value equality (SameValueZero)
- FR-P3-045: Set iteration (keys, values, entries, forEach)
- FR-P3-046: Map/Set insertion order preservation
- FR-P3-048: Set.prototype.size property
- FR-P3-049: Map/Set clear method
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestSetConstructor:
    """Test Set constructor."""

    def test_create_empty_set(self):
        """Test creating an empty Set."""
        from components.collections.src.set import Set

        s = Set()
        assert s.size == 0

    def test_create_set_from_iterable(self):
        """Test creating Set from iterable of values."""
        from components.collections.src.set import Set

        values = [1, 2, 3, 4]
        s = Set(values)

        assert s.size == 4
        assert s.has(1) is True
        assert s.has(2) is True

    def test_create_set_removes_duplicates(self):
        """Test creating Set from iterable removes duplicates."""
        from components.collections.src.set import Set

        values = [1, 2, 2, 3, 3, 3, 4]
        s = Set(values)

        assert s.size == 4  # Only unique values


class TestSetBasicOperations:
    """Test basic Set operations."""

    def test_add_and_has(self):
        """Test add() and has() methods."""
        from components.collections.src.set import Set

        s = Set()
        result = s.add("value1")

        assert result is s  # add() returns this
        assert s.has("value1") is True
        assert s.size == 1

    def test_add_multiple_values(self):
        """Test adding multiple values."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)

        assert s.size == 3
        assert s.has(1) is True
        assert s.has(2) is True
        assert s.has(3) is True

    def test_add_duplicate_value(self):
        """Test adding duplicate value doesn't increase size."""
        from components.collections.src.set import Set

        s = Set()
        s.add("value")
        s.add("value")  # Duplicate

        assert s.size == 1

    def test_has_nonexistent_value(self):
        """Test has() returns False for non-existent value."""
        from components.collections.src.set import Set

        s = Set()
        assert s.has("nonexistent") is False

    def test_delete_method(self):
        """Test delete() method."""
        from components.collections.src.set import Set

        s = Set()
        s.add("value1")
        s.add("value2")

        assert s.delete("value1") is True
        assert s.has("value1") is False
        assert s.size == 1
        assert s.delete("nonexistent") is False

    def test_clear_method(self):
        """Test clear() method (FR-P3-049)."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add(2)
        s.clear()

        assert s.size == 0
        assert s.has(1) is False


class TestSetValueTypes:
    """Test Set with various value types."""

    def test_object_values(self):
        """Test using objects as values."""
        from components.collections.src.set import Set

        s = Set()
        obj1 = {"id": 1}
        obj2 = {"id": 2}

        s.add(obj1)
        s.add(obj2)

        assert s.has(obj1) is True
        assert s.has(obj2) is True
        assert s.size == 2

    def test_mixed_value_types(self):
        """Test Set with mixed value types."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add("1")
        s.add(True)
        s.add(None)

        assert s.size == 4


class TestSetSameValueZero:
    """Test Set value equality using SameValueZero (FR-P3-039)."""

    def test_nan_as_value(self):
        """Test NaN equals NaN as value."""
        from components.collections.src.set import Set

        s = Set()
        nan1 = float('nan')
        nan2 = float('nan')

        s.add(nan1)
        s.add(nan2)  # Should be seen as duplicate

        assert s.size == 1
        assert s.has(nan1) is True
        assert s.has(nan2) is True

    def test_positive_and_negative_zero_as_value(self):
        """Test +0 and -0 are equal as values."""
        from components.collections.src.set import Set

        s = Set()
        s.add(0.0)
        s.add(-0.0)  # Should be seen as duplicate

        assert s.size == 1
        assert s.has(0.0) is True
        assert s.has(-0.0) is True


class TestSetIteration:
    """Test Set iteration methods (FR-P3-045, FR-P3-046)."""

    def test_keys_iterator(self):
        """Test keys() iterator (same as values for Set)."""
        from components.collections.src.set import Set

        s = Set()
        s.add("a")
        s.add("b")
        s.add("c")

        keys = list(s.keys())
        assert keys == ["a", "b", "c"]

    def test_values_iterator(self):
        """Test values() iterator."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)

        values = list(s.values())
        assert values == [1, 2, 3]

    def test_entries_iterator(self):
        """Test entries() iterator (returns [value, value] pairs for Set)."""
        from components.collections.src.set import Set

        s = Set()
        s.add("a")
        s.add("b")

        entries = list(s.entries())
        assert entries == [("a", "a"), ("b", "b")]

    def test_insertion_order_preserved(self):
        """Test insertion order is preserved (FR-P3-046)."""
        from components.collections.src.set import Set

        s = Set()
        s.add("first")
        s.add("second")
        s.add("third")

        values = list(s.values())
        assert values == ["first", "second", "third"]

    def test_readd_preserves_order(self):
        """Test re-adding a value preserves its position."""
        from components.collections.src.set import Set

        s = Set()
        s.add("a")
        s.add("b")
        s.add("c")
        s.add("b")  # Re-add

        values = list(s.values())
        assert values == ["a", "b", "c"]  # Order preserved

    def test_delete_and_readd_changes_order(self):
        """Test deleting and re-adding moves to end."""
        from components.collections.src.set import Set

        s = Set()
        s.add("a")
        s.add("b")
        s.add("c")
        s.delete("b")
        s.add("b")

        values = list(s.values())
        assert values == ["a", "c", "b"]


class TestSetForEach:
    """Test forEach() method."""

    def test_foreach_callback(self):
        """Test forEach() with callback."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add(2)
        s.add(3)

        results = []
        s.forEach(lambda value, value2, set_obj: results.append(value))

        assert results == [1, 2, 3]

    def test_foreach_receives_value_twice(self):
        """Test forEach() callback receives value twice (for consistency with Map)."""
        from components.collections.src.set import Set

        s = Set()
        s.add("x")

        received = []

        def callback(value, value2, set_obj):
            received.append((value, value2))

        s.forEach(callback)
        assert received == [("x", "x")]

    def test_foreach_receives_set(self):
        """Test forEach() callback receives the set."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)

        received_set = [None]

        def callback(value, value2, set_obj):
            received_set[0] = set_obj

        s.forEach(callback)
        assert received_set[0] is s


class TestSetIteratorProtocol:
    """Test Set iterator protocol."""

    def test_set_is_iterable(self):
        """Test Set is iterable (returns values)."""
        from components.collections.src.set import Set

        s = Set()
        s.add(1)
        s.add(2)

        values = list(s)
        assert values == [1, 2]

    def test_set_iterator_for_loop(self):
        """Test using Set in for loop."""
        from components.collections.src.set import Set

        s = Set()
        s.add("x")
        s.add("y")

        result = []
        for value in s:
            result.append(value)

        assert result == ["x", "y"]


class TestSetSize:
    """Test Set size property (FR-P3-048)."""

    def test_size_property(self):
        """Test size property."""
        from components.collections.src.set import Set

        s = Set()
        assert s.size == 0

        s.add(1)
        assert s.size == 1

        s.add(2)
        assert s.size == 2

        s.delete(1)
        assert s.size == 1

        s.clear()
        assert s.size == 0


class TestSetEdgeCases:
    """Test edge cases."""

    def test_none_as_value(self):
        """Test None as value."""
        from components.collections.src.set import Set

        s = Set()
        s.add(None)
        assert s.has(None) is True
        assert s.size == 1

    def test_empty_set_iteration(self):
        """Test iterating empty set."""
        from components.collections.src.set import Set

        s = Set()
        assert list(s.keys()) == []
        assert list(s.values()) == []
        assert list(s.entries()) == []

    def test_many_values(self):
        """Test Set with many values."""
        from components.collections.src.set import Set

        s = Set()
        for i in range(1000):
            s.add(i)

        assert s.size == 1000
        assert s.has(500) is True

    def test_boolean_values(self):
        """Test booleans as values."""
        from components.collections.src.set import Set

        s = Set()
        s.add(True)
        s.add(False)

        assert s.size == 2
        assert s.has(True) is True
        assert s.has(False) is True
