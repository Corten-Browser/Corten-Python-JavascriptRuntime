"""
Unit tests for GarbageCollector.

Tests the mark-and-sweep garbage collection algorithm.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from garbage_collector import GarbageCollector
from heap_object import HeapObject


class TestGarbageCollectorInitialization:
    """Test GarbageCollector initialization."""

    def test_garbage_collector_can_be_created_with_default_heap_size(self):
        """
        Given no heap size specified
        When GarbageCollector is created
        Then it should use default 64MB heap size
        """
        # When
        gc = GarbageCollector()

        # Then
        assert gc.heap_size_bytes == 64 * 1024 * 1024

    def test_garbage_collector_can_be_created_with_custom_heap_size(self):
        """
        Given a custom heap size
        When GarbageCollector is created
        Then it should use the specified heap size
        """
        # Given
        heap_size_mb = 128

        # When
        gc = GarbageCollector(heap_size_mb=heap_size_mb)

        # Then
        assert gc.heap_size_bytes == 128 * 1024 * 1024

    def test_garbage_collector_initializes_with_no_roots(self):
        """
        Given a new GarbageCollector
        When initialized
        Then it should have no GC roots
        """
        # When
        gc = GarbageCollector()

        # Then
        assert len(gc.roots) == 0


class TestGarbageCollectorRoots:
    """Test GC root management."""

    def test_add_root_adds_object_to_roots(self):
        """
        Given a GarbageCollector and an object
        When add_root is called with the object
        Then the object should be in roots
        """
        # Given
        gc = GarbageCollector()
        obj = HeapObject(size=100)

        # When
        gc.add_root(obj)

        # Then
        assert obj in gc.roots

    def test_add_root_does_not_add_duplicates(self):
        """
        Given an object already in roots
        When add_root is called again with same object
        Then roots should only contain one instance
        """
        # Given
        gc = GarbageCollector()
        obj = HeapObject(size=100)
        gc.add_root(obj)

        # When
        gc.add_root(obj)

        # Then
        assert gc.roots.count(obj) == 1

    def test_remove_root_removes_object_from_roots(self):
        """
        Given an object in roots
        When remove_root is called with the object
        Then the object should not be in roots
        """
        # Given
        gc = GarbageCollector()
        obj = HeapObject(size=100)
        gc.add_root(obj)

        # When
        gc.remove_root(obj)

        # Then
        assert obj not in gc.roots

    def test_remove_root_does_nothing_if_object_not_in_roots(self):
        """
        Given an object not in roots
        When remove_root is called with the object
        Then no error should occur
        """
        # Given
        gc = GarbageCollector()
        obj = HeapObject(size=100)

        # When/Then (should not raise)
        gc.remove_root(obj)


class TestGarbageCollectorAllocate:
    """Test object allocation."""

    def test_allocate_creates_heap_object_with_correct_size(self):
        """
        Given a GarbageCollector and a size
        When allocate is called
        Then it should return HeapObject with correct size
        """
        # Given
        gc = GarbageCollector()
        size = 100

        # When
        obj = gc.allocate(size)

        # Then
        assert isinstance(obj, HeapObject)
        assert obj.size == 100

    def test_allocate_tracks_object_in_heap(self):
        """
        Given a GarbageCollector
        When allocate is called
        Then the object should be tracked in the heap
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = gc.allocate(100)

        # Then
        assert obj in gc.heap

    def test_allocate_updates_used_memory(self):
        """
        Given a GarbageCollector
        When objects are allocated
        Then used memory should increase
        """
        # Given
        gc = GarbageCollector()
        initial_used = gc.used_bytes

        # When
        gc.allocate(100)
        gc.allocate(200)

        # Then
        assert gc.used_bytes == initial_used + 300

    def test_allocate_triggers_gc_when_heap_is_full(self):
        """
        Given a GarbageCollector with small heap
        And some unreachable objects
        When allocation would exceed heap size
        Then GC should be triggered and free unreachable objects
        """
        # Given - small heap for testing
        gc = GarbageCollector(heap_size_mb=1)  # 1MB
        heap_size = gc.heap_size_bytes

        # Allocate some rooted and unrooted objects
        obj1 = gc.allocate(heap_size // 4)
        gc.add_root(obj1)  # Keep alive

        # Allocate garbage (not rooted)
        garbage1 = gc.allocate(heap_size // 4)
        garbage2 = gc.allocate(heap_size // 4)

        # Now heap is ~75% full (786432 bytes used)
        # When - allocate more that would exceed without GC
        # heap_size // 4 + 10000 = 272144 bytes
        # Total would be: 786432 + 272144 = 1058576 > 1048576 (heap size)
        obj2 = gc.allocate(heap_size // 4 + 10000)

        # Then - should succeed because GC freed garbage
        assert obj2 is not None
        assert isinstance(obj2, HeapObject)
        # Garbage should be collected
        assert garbage1 not in gc.heap
        assert garbage2 not in gc.heap

    def test_allocate_raises_memory_error_if_gc_cannot_free_space(self):
        """
        Given a GarbageCollector with small heap
        And all objects are rooted (cannot be collected)
        When allocation exceeds available space
        Then MemoryError should be raised
        """
        # Given - very small heap
        gc = GarbageCollector(heap_size_mb=1)
        heap_size = gc.heap_size_bytes

        # Fill heap with rooted objects
        obj1 = gc.allocate(heap_size // 2)
        gc.add_root(obj1)
        obj2 = gc.allocate(heap_size // 2 - 1000)
        gc.add_root(obj2)

        # When/Then - trying to allocate more should fail
        with pytest.raises(MemoryError):
            gc.allocate(heap_size)


class TestGarbageCollectorCollect:
    """Test mark-and-sweep collection."""

    def test_collect_returns_statistics_dict(self):
        """
        Given a GarbageCollector
        When collect is called
        Then it should return dict with statistics
        """
        # Given
        gc = GarbageCollector()
        gc.allocate(100)

        # When
        stats = gc.collect()

        # Then
        assert isinstance(stats, dict)
        assert "objects_before" in stats
        assert "objects_after" in stats
        assert "bytes_freed" in stats
        assert "duration_ms" in stats

    def test_collect_marks_reachable_objects_from_roots(self):
        """
        Given objects reachable from roots
        When collect is called
        Then reachable objects should be marked
        """
        # Given
        gc = GarbageCollector()
        root_obj = gc.allocate(100)
        gc.add_root(root_obj)

        # When
        gc.collect()

        # Then
        assert root_obj.marked is True

    def test_collect_marks_transitively_reachable_objects(self):
        """
        Given objects reachable through references
        When collect is called
        Then all transitively reachable objects should be marked
        """
        # Given
        gc = GarbageCollector()

        # Create object graph: root -> obj1 -> obj2
        class ObjectWithRefs(HeapObject):
            def __init__(self, size, refs=None):
                super().__init__(size)
                self._refs = refs or []

            def get_references(self):
                return self._refs

        obj2 = gc.allocate(50)
        obj1 = ObjectWithRefs(size=100, refs=[obj2])
        gc.heap.add(obj1)
        root = ObjectWithRefs(size=200, refs=[obj1])
        gc.heap.add(root)
        gc.add_root(root)

        # When
        gc.collect()

        # Then - all reachable objects should be marked
        assert root.marked is True
        assert obj1.marked is True
        assert obj2.marked is True

    def test_collect_frees_unreachable_objects(self):
        """
        Given unreachable objects in heap
        When collect is called
        Then unreachable objects should be freed
        """
        # Given
        gc = GarbageCollector()
        reachable = gc.allocate(100)
        gc.add_root(reachable)
        unreachable = gc.allocate(200)

        initial_count = len(gc.heap)

        # When
        stats = gc.collect()

        # Then
        assert unreachable not in gc.heap
        assert reachable in gc.heap
        assert stats["objects_before"] == initial_count
        assert stats["objects_after"] < stats["objects_before"]

    def test_collect_updates_used_memory(self):
        """
        Given allocated objects
        When collect frees objects
        Then used memory should decrease
        """
        # Given
        gc = GarbageCollector()
        reachable = gc.allocate(100)
        gc.add_root(reachable)
        gc.allocate(200)  # Unreachable

        # When
        stats = gc.collect()

        # Then
        assert stats["bytes_freed"] >= 200
        assert gc.used_bytes < 300

    def test_collect_clears_mark_bits_after_collection(self):
        """
        Given marked objects after collection
        When collect is called again
        Then mark bits should be cleared first
        """
        # Given
        gc = GarbageCollector()
        obj = gc.allocate(100)
        gc.add_root(obj)
        gc.collect()  # First collection marks obj
        assert obj.marked is True

        # When
        gc.collect()  # Second collection

        # Then - obj should still be marked (cleared then marked again)
        assert obj.marked is True

    def test_collect_reports_duration(self):
        """
        Given a GarbageCollector
        When collect is called
        Then duration_ms should be positive
        """
        # Given
        gc = GarbageCollector()
        gc.allocate(100)

        # When
        stats = gc.collect()

        # Then
        assert stats["duration_ms"] >= 0
        assert isinstance(stats["duration_ms"], (int, float))


class TestGarbageCollectorEdgeCases:
    """Test edge cases and error conditions."""

    def test_collect_handles_empty_heap(self):
        """
        Given an empty heap
        When collect is called
        Then it should complete without error
        """
        # Given
        gc = GarbageCollector()

        # When
        stats = gc.collect()

        # Then
        assert stats["objects_before"] == 0
        assert stats["objects_after"] == 0
        assert stats["bytes_freed"] == 0

    def test_collect_handles_circular_references(self):
        """
        Given objects with circular references
        When collect is called
        Then it should handle cycles correctly
        """
        # Given
        gc = GarbageCollector()

        class ObjectWithRefs(HeapObject):
            def __init__(self, size, refs=None):
                super().__init__(size)
                self._refs = refs or []

            def get_references(self):
                return self._refs

        # Create cycle: obj1 -> obj2 -> obj1
        obj1 = ObjectWithRefs(size=100)
        obj2 = ObjectWithRefs(size=100, refs=[obj1])
        obj1._refs = [obj2]

        gc.heap.add(obj1)
        gc.heap.add(obj2)

        # No roots - cycle is unreachable

        # When
        gc.collect()

        # Then - cycle should be collected
        assert obj1 not in gc.heap
        assert obj2 not in gc.heap

    def test_allocate_with_zero_size(self):
        """
        Given size of 0
        When allocate is called
        Then it should create object with size 0
        """
        # Given
        gc = GarbageCollector()

        # When
        obj = gc.allocate(0)

        # Then
        assert obj.size == 0

    def test_allocate_with_negative_size_raises_error(self):
        """
        Given negative size
        When allocate is called
        Then it should raise ValueError
        """
        # Given
        gc = GarbageCollector()

        # When/Then
        with pytest.raises(ValueError):
            gc.allocate(-100)
