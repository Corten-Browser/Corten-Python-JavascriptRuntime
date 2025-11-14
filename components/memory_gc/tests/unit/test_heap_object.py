"""
Unit tests for HeapObject base class.

Given-When-Then format for behavior-driven testing.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from heap_object import HeapObject


class TestHeapObjectInitialization:
    """Test HeapObject initialization."""

    def test_heap_object_can_be_created_with_size(self):
        """
        Given a size value
        When HeapObject is created
        Then it should store the size
        """
        # Given
        size = 100

        # When
        obj = HeapObject(size=size)

        # Then
        assert obj.size == 100

    def test_heap_object_marked_defaults_to_false(self):
        """
        Given no marked value specified
        When HeapObject is created
        Then marked should default to False
        """
        # Given/When
        obj = HeapObject(size=50)

        # Then
        assert obj.marked is False

    def test_heap_object_can_be_created_with_marked_true(self):
        """
        Given marked=True specified
        When HeapObject is created
        Then marked should be True
        """
        # Given/When
        obj = HeapObject(size=50, marked=True)

        # Then
        assert obj.marked is True


class TestHeapObjectReferences:
    """Test get_references method."""

    def test_get_references_returns_empty_list_by_default(self):
        """
        Given a basic HeapObject with no references
        When get_references is called
        Then it should return an empty list
        """
        # Given
        obj = HeapObject(size=100)

        # When
        refs = obj.get_references()

        # Then
        assert refs == []
        assert isinstance(refs, list)

    def test_get_references_can_return_referenced_objects(self):
        """
        Given a HeapObject subclass that tracks references
        When get_references is called
        Then it should return the list of referenced objects
        """
        # Given
        class ObjectWithRefs(HeapObject):
            def __init__(self, size, refs=None):
                super().__init__(size)
                self._refs = refs or []

            def get_references(self):
                return self._refs

        obj1 = HeapObject(size=50)
        obj2 = HeapObject(size=60)
        parent = ObjectWithRefs(size=100, refs=[obj1, obj2])

        # When
        refs = parent.get_references()

        # Then
        assert len(refs) == 2
        assert obj1 in refs
        assert obj2 in refs


class TestHeapObjectMarking:
    """Test mark bit manipulation."""

    def test_marked_bit_can_be_set(self):
        """
        Given an unmarked object
        When marked is set to True
        Then marked should be True
        """
        # Given
        obj = HeapObject(size=100)
        assert obj.marked is False

        # When
        obj.marked = True

        # Then
        assert obj.marked is True

    def test_marked_bit_can_be_cleared(self):
        """
        Given a marked object
        When marked is set to False
        Then marked should be False
        """
        # Given
        obj = HeapObject(size=100, marked=True)
        assert obj.marked is True

        # When
        obj.marked = False

        # Then
        assert obj.marked is False


class TestHeapObjectSize:
    """Test size field."""

    def test_size_is_stored_correctly(self):
        """
        Given various size values
        When HeapObject is created
        Then size should be stored accurately
        """
        # Test multiple sizes
        for size in [0, 1, 100, 1024, 1000000]:
            obj = HeapObject(size=size)
            assert obj.size == size

    def test_size_must_be_provided(self):
        """
        Given no size provided
        When HeapObject is created
        Then it should raise TypeError
        """
        with pytest.raises(TypeError):
            HeapObject()
