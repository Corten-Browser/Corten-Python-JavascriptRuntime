"""
Unit tests for JSString class.

Tests JavaScript string representation.
"""

import pytest


class TestJSStringCreation:
    """Test JSString instantiation."""

    def test_create_string_with_value(self):
        """Test creating JSString with a string value."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        assert s is not None
        assert s.get_value() == "hello"

    def test_create_empty_string(self):
        """Test creating empty JSString."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "")

        assert s.get_value() == ""

    def test_string_has_length_property(self):
        """Test that strings have a length property."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        length = s.get_property("length")
        assert length.to_smi() == 5


class TestJSStringValue:
    """Test string value operations."""

    def test_get_value_returns_string(self):
        """Test getting string value."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "test string")

        value = s.get_value()

        assert isinstance(value, str)
        assert value == "test string"

    def test_length_returns_correct_count(self):
        """Test length returns character count."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello world")

        length = s.length()

        assert length == 11


class TestJSStringCharAt:
    """Test charAt operation."""

    def test_char_at_valid_index(self):
        """Test charAt with valid index."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        char = s.char_at(0)

        assert char == "h"

    def test_char_at_last_index(self):
        """Test charAt at last index."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        char = s.char_at(4)

        assert char == "o"

    def test_char_at_out_of_bounds_returns_empty(self):
        """Test charAt with out of bounds index returns empty string."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        char = s.char_at(10)

        assert char == ""

    def test_char_at_negative_index_returns_empty(self):
        """Test charAt with negative index returns empty string."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "hello")

        char = s.char_at(-1)

        assert char == ""


class TestJSStringGCIntegration:
    """Test garbage collection integration."""

    def test_get_references_returns_prototype(self):
        """Test get_references returns prototype."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)

        s = JSString(gc, "test", prototype=prototype)

        references = s.get_references()

        assert prototype in references

    def test_string_in_gc_heap(self):
        """Test that string is registered in GC heap."""
        from components.memory_gc.src import GarbageCollector
        from js_string import JSString

        gc = GarbageCollector()
        s = JSString(gc, "test")

        assert s in gc.heap
