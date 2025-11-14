"""
Unit tests for JSArray class.

Tests JavaScript array implementation.
"""

import pytest


class TestJSArrayCreation:
    """Test JSArray instantiation."""

    def test_create_array_with_default_length(self):
        """Test creating JSArray with default length."""
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        assert arr.get_property("length").to_smi() == 0

    def test_create_array_with_length(self):
        """Test creating JSArray with specified length."""
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc, length=5)

        assert arr.get_property("length").to_smi() == 5


class TestJSArrayElementAccess:
    """Test array element get/set operations."""

    def test_set_and_get_element(self):
        """Test setting and getting an element."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        arr.set_element(0, Value.from_smi(42))
        result = arr.get_element(0)

        assert result.is_smi()
        assert result.to_smi() == 42

    def test_get_out_of_bounds_element(self):
        """Test getting out of bounds element returns undefined."""
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc, length=5)

        result = arr.get_element(10)
        assert result is not None  # Returns undefined


class TestJSArrayPushPop:
    """Test push and pop operations."""

    def test_push_returns_new_length(self):
        """Test push returns new length."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        new_length = arr.push(Value.from_smi(42))

        assert new_length == 1
        assert arr.get_element(0).to_smi() == 42

    def test_multiple_pushes(self):
        """Test multiple pushes."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        length = arr.push(Value.from_smi(3))

        assert length == 3
        assert arr.get_element(0).to_smi() == 1
        assert arr.get_element(2).to_smi() == 3

    def test_pop_returns_element(self):
        """Test pop returns element."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        arr.push(Value.from_smi(42))
        result = arr.pop()

        assert result.to_smi() == 42
        assert arr.get_property("length").to_smi() == 0

    def test_pop_empty_array(self):
        """Test pop on empty array returns undefined."""
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        result = arr.pop()
        assert result is not None  # Returns undefined
