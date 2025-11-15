"""
Unit tests for WeakSet implementation.

Requirements:
- FR-P3-042: WeakSet constructor and methods
- FR-P3-043: WeakSet garbage collection behavior (weak references)
- FR-P3-050: WeakSet object-only values

WeakSet restrictions:
- Values must be objects (primitives throw TypeError)
- Not enumerable (no size, no iteration)
- Weak references (values GC'd when unreachable)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestWeakSetConstructor:
    """Test WeakSet constructor."""

    def test_create_empty_weak_set(self):
        """Test creating an empty WeakSet."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        # WeakSet has no size property

    def test_create_weak_set_from_iterable(self):
        """Test creating WeakSet from iterable of values."""
        from components.collections.src.weak_set import WeakSet

        obj1 = {"id": 1}
        obj2 = {"id": 2}
        values = [obj1, obj2]
        ws = WeakSet(values)

        assert ws.has(obj1) is True
        assert ws.has(obj2) is True


class TestWeakSetBasicOperations:
    """Test basic WeakSet operations."""

    def test_add_and_has(self):
        """Test add() and has() methods."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj = {"key": "test"}
        result = ws.add(obj)

        assert result is ws  # add() returns this
        assert ws.has(obj) is True

    def test_add_multiple_values(self):
        """Test adding multiple values."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj1 = {"id": 1}
        obj2 = {"id": 2}
        obj3 = {"id": 3}

        ws.add(obj1)
        ws.add(obj2)
        ws.add(obj3)

        assert ws.has(obj1) is True
        assert ws.has(obj2) is True
        assert ws.has(obj3) is True

    def test_add_duplicate_value(self):
        """Test adding duplicate value is idempotent."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj = {"key": "test"}
        ws.add(obj)
        ws.add(obj)  # Duplicate

        assert ws.has(obj) is True

    def test_has_nonexistent_value(self):
        """Test has() returns False for non-existent value."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj = {"key": "test"}
        assert ws.has(obj) is False

    def test_delete_method(self):
        """Test delete() method."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj1 = {"id": 1}
        obj2 = {"id": 2}

        ws.add(obj1)
        ws.add(obj2)

        assert ws.delete(obj1) is True
        assert ws.has(obj1) is False
        assert ws.delete({"nonexistent": "obj"}) is False


class TestWeakSetObjectOnlyValues:
    """Test WeakSet only accepts objects as values (FR-P3-050)."""

    def test_primitive_number_value_throws_error(self):
        """Test that primitive number values throw TypeError."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        with pytest.raises(TypeError, match="Invalid value used in weak set"):
            ws.add(42)

    def test_primitive_string_value_throws_error(self):
        """Test that primitive string values throw TypeError."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        with pytest.raises(TypeError, match="Invalid value used in weak set"):
            ws.add("string")

    def test_primitive_boolean_value_throws_error(self):
        """Test that primitive boolean values throw TypeError."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        with pytest.raises(TypeError, match="Invalid value used in weak set"):
            ws.add(True)

    def test_none_value_throws_error(self):
        """Test that None/null values throw TypeError."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        with pytest.raises(TypeError, match="Invalid value used in weak set"):
            ws.add(None)

    def test_object_value_is_accepted(self):
        """Test that object values are accepted."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj = {"key": "test"}
        ws.add(obj)  # Should not throw
        assert ws.has(obj) is True

    def test_list_value_is_accepted(self):
        """Test that lists (objects in JS) are accepted as values."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        lst = [1, 2, 3]
        ws.add(lst)
        assert ws.has(lst) is True

    def test_function_value_is_accepted(self):
        """Test that functions are accepted as values."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        fn = lambda x: x
        ws.add(fn)
        assert ws.has(fn) is True


class TestWeakSetNotEnumerable:
    """Test WeakSet is not enumerable."""

    def test_no_size_property(self):
        """Test WeakSet has no size property."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        ws.add({"a": 1})

        # WeakSet should not have size property
        assert not hasattr(ws, 'size')

    def test_no_keys_method(self):
        """Test WeakSet has no keys() method."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        # WeakSet should not have keys() method for iteration
        assert not hasattr(ws, 'keys')

    def test_no_values_method(self):
        """Test WeakSet has no values() method."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        # WeakSet should not have values() method for iteration
        assert not hasattr(ws, 'values')

    def test_no_entries_method(self):
        """Test WeakSet has no entries() method."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        # WeakSet should not have entries() method for iteration
        assert not hasattr(ws, 'entries')

    def test_no_foreach_method(self):
        """Test WeakSet has no forEach() method."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        # WeakSet should not have forEach() method
        assert not hasattr(ws, 'forEach')

    def test_not_iterable(self):
        """Test WeakSet is not iterable."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        ws.add({"a": 1})

        # WeakSet should not be iterable
        # (In Python, we just don't implement __iter__)


class TestWeakSetEdgeCases:
    """Test edge cases."""

    def test_same_object_different_references(self):
        """Test that same object content but different references are different values."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj1 = {"id": 1}
        obj2 = {"id": 1}  # Same content, different reference

        ws.add(obj1)
        ws.add(obj2)

        assert ws.has(obj1) is True
        assert ws.has(obj2) is True


class TestWeakSetGarbageCollection:
    """Test WeakSet garbage collection behavior (FR-P3-043).

    Note: Full GC integration requires memory_gc component.
    These tests verify the API, not actual weak reference behavior.
    """

    def test_weak_references_note(self):
        """Note that weak reference behavior requires GC integration."""
        from components.collections.src.weak_set import WeakSet

        ws = WeakSet()
        obj = {"key": "test"}
        ws.add(obj)

        # When obj goes out of scope and is GC'd, it should be removed
        # This requires integration with memory_gc component
        # For now, we just test the API is correct
        assert ws.has(obj) is True
