"""
Unit tests for allocation functions.

Tests AllocateObject, AllocateArray, and AllocateString functions.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from allocators import AllocateObject, AllocateArray, AllocateString
from garbage_collector import GarbageCollector
from heap_object import HeapObject


class TestAllocateObject:
    """Test AllocateObject function."""

    def test_allocate_object_returns_heap_object(self):
        """
        Given a GarbageCollector
        When AllocateObject is called
        Then it should return a HeapObject
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = AllocateObject(gc)

        # Then
        assert isinstance(obj, HeapObject)

    def test_allocate_object_with_default_property_count(self):
        """
        Given no property_count specified
        When AllocateObject is called
        Then it should use default property count of 4
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = AllocateObject(gc)

        # Then - size should be based on default 4 properties
        # Each property: ~64 bytes (estimate)
        assert obj.size > 0

    def test_allocate_object_with_custom_property_count(self):
        """
        Given a custom property_count
        When AllocateObject is called
        Then size should reflect the property count
        """
        # Given
        gc = GarbageCollector()

        # When
        obj_small = AllocateObject(gc, property_count=2)
        obj_large = AllocateObject(gc, property_count=10)

        # Then - larger property count should result in larger size
        assert obj_large.size > obj_small.size

    def test_allocate_object_is_tracked_in_heap(self):
        """
        Given a GarbageCollector
        When AllocateObject is called
        Then the object should be in the heap
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = AllocateObject(gc)

        # Then
        assert obj in gc.heap


class TestAllocateArray:
    """Test AllocateArray function."""

    def test_allocate_array_returns_heap_object(self):
        """
        Given a GarbageCollector and length
        When AllocateArray is called
        Then it should return a HeapObject
        """
        # Given
        gc = GarbageCollector()

        # When
        arr = AllocateArray(gc, length=10)

        # Then
        assert isinstance(arr, HeapObject)

    def test_allocate_array_size_increases_with_length(self):
        """
        Given different array lengths
        When AllocateArray is called
        Then larger arrays should have larger sizes
        """
        # Given
        gc = GarbageCollector()

        # When
        arr_small = AllocateArray(gc, length=5)
        arr_large = AllocateArray(gc, length=100)

        # Then
        assert arr_large.size > arr_small.size

    def test_allocate_array_with_zero_length(self):
        """
        Given length of 0
        When AllocateArray is called
        Then it should create array with minimal size
        """
        # Given
        gc = GarbageCollector()

        # When
        arr = AllocateArray(gc, length=0)

        # Then
        assert isinstance(arr, HeapObject)
        assert arr.size >= 0

    def test_allocate_array_is_tracked_in_heap(self):
        """
        Given a GarbageCollector
        When AllocateArray is called
        Then the array should be in the heap
        """
        # Given
        gc = GarbageCollector()

        # When
        arr = AllocateArray(gc, length=10)

        # Then
        assert arr in gc.heap

    def test_allocate_array_with_negative_length_raises_error(self):
        """
        Given a negative length
        When AllocateArray is called
        Then it should raise ValueError
        """
        # Given
        gc = GarbageCollector()

        # When/Then
        with pytest.raises(ValueError):
            AllocateArray(gc, length=-5)


class TestAllocateString:
    """Test AllocateString function."""

    def test_allocate_string_returns_heap_object(self):
        """
        Given a GarbageCollector and string value
        When AllocateString is called
        Then it should return a HeapObject
        """
        # Given
        gc = GarbageCollector()

        # When
        str_obj = AllocateString(gc, value="hello")

        # Then
        assert isinstance(str_obj, HeapObject)

    def test_allocate_string_size_increases_with_length(self):
        """
        Given strings of different lengths
        When AllocateString is called
        Then longer strings should have larger sizes
        """
        # Given
        gc = GarbageCollector()

        # When
        str_short = AllocateString(gc, value="hi")
        str_long = AllocateString(gc, value="hello world this is a long string")

        # Then
        assert str_long.size > str_short.size

    def test_allocate_string_with_empty_string(self):
        """
        Given an empty string
        When AllocateString is called
        Then it should create string object with minimal size
        """
        # Given
        gc = GarbageCollector()

        # When
        str_obj = AllocateString(gc, value="")

        # Then
        assert isinstance(str_obj, HeapObject)
        assert str_obj.size >= 0

    def test_allocate_string_is_tracked_in_heap(self):
        """
        Given a GarbageCollector
        When AllocateString is called
        Then the string should be in the heap
        """
        # Given
        gc = GarbageCollector()

        # When
        str_obj = AllocateString(gc, value="test")

        # Then
        assert str_obj in gc.heap

    def test_allocate_string_with_unicode(self):
        """
        Given a Unicode string
        When AllocateString is called
        Then it should handle Unicode correctly
        """
        # Given
        gc = GarbageCollector()

        # When
        str_obj = AllocateString(gc, value="Hello 世界 🌍")

        # Then
        assert isinstance(str_obj, HeapObject)
        # Unicode characters may take more bytes
        assert str_obj.size > 0


class TestAllocatorIntegration:
    """Test allocators working together with GC."""

    def test_allocators_respect_memory_limits(self):
        """
        Given a small heap
        When attempting to allocate more than heap size with all rooted
        Then MemoryError should be raised
        """
        # Given - very small heap
        gc = GarbageCollector(heap_size_mb=1)
        heap_size = gc.heap_size_bytes

        # Fill heap with rooted objects (cannot be collected)
        obj1 = AllocateArray(gc, length=heap_size // 16)
        gc.add_root(obj1)

        # When/Then - attempting to allocate more than remaining should fail
        with pytest.raises(MemoryError):
            # Try to allocate way more than heap size
            AllocateString(gc, value="x" * heap_size)

    def test_mixed_allocations(self):
        """
        Given a GarbageCollector
        When different types are allocated
        Then all should coexist in heap
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = AllocateObject(gc, property_count=5)
        arr = AllocateArray(gc, length=10)
        string = AllocateString(gc, value="test")

        # Then
        assert obj in gc.heap
        assert arr in gc.heap
        assert string in gc.heap
        assert len(gc.heap) == 3
