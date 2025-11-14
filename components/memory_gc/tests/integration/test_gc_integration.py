"""
Integration tests for memory_gc component.

Tests the complete garbage collection system with realistic scenarios.
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from garbage_collector import GarbageCollector
from heap_object import HeapObject
from allocators import AllocateObject, AllocateArray, AllocateString


class TestGCIntegration:
    """Integration tests for complete GC system."""

    def test_complete_allocation_and_collection_cycle(self):
        """
        Integration test: Complete allocation and GC cycle.

        Scenario:
        1. Allocate multiple objects of different types
        2. Create references between objects
        3. Remove some roots
        4. Trigger GC
        5. Verify correct objects collected
        """
        # Given
        gc = GarbageCollector(heap_size_mb=10)

        # Allocate various types
        obj1 = AllocateObject(gc, property_count=10)
        arr1 = AllocateArray(gc, length=100)
        str1 = AllocateString(gc, value="reachable")

        # Allocate garbage (not rooted)
        garbage1 = AllocateObject(gc, property_count=5)
        garbage2 = AllocateArray(gc, length=50)
        garbage3 = AllocateString(gc, value="garbage")

        # Root some objects
        gc.add_root(obj1)
        gc.add_root(arr1)
        gc.add_root(str1)

        initial_count = len(gc.heap)
        assert initial_count == 6

        # When - trigger GC
        stats = gc.collect()

        # Then - garbage should be collected
        assert len(gc.heap) == 3  # Only rooted objects remain
        assert obj1 in gc.heap
        assert arr1 in gc.heap
        assert str1 in gc.heap
        assert garbage1 not in gc.heap
        assert garbage2 not in gc.heap
        assert garbage3 not in gc.heap

        # Verify stats
        assert stats["objects_before"] == 6
        assert stats["objects_after"] == 3
        assert stats["bytes_freed"] > 0

    def test_object_graph_with_transitive_references(self):
        """
        Integration test: Object graph with transitive references.

        Scenario:
        1. Create object graph: root -> obj1 -> obj2 -> obj3
        2. Allocate unreachable objects
        3. Run GC
        4. Verify all reachable objects kept, unreachable collected
        """
        # Given
        gc = GarbageCollector(heap_size_mb=10)

        # Create object graph with references
        class RefObject(HeapObject):
            def __init__(self, size, refs=None):
                super().__init__(size)
                self._refs = refs or []

            def get_references(self):
                return self._refs

        # Build chain: root -> obj1 -> obj2 -> obj3
        obj3 = gc.allocate(100)
        obj2 = RefObject(size=200, refs=[obj3])
        gc.heap.add(obj2)
        obj1 = RefObject(size=300, refs=[obj2])
        gc.heap.add(obj1)
        root = RefObject(size=400, refs=[obj1])
        gc.heap.add(root)

        # Add unreachable objects
        unreachable1 = gc.allocate(150)
        unreachable2 = gc.allocate(250)

        # Root only the root object
        gc.add_root(root)

        # When - run GC
        stats = gc.collect()

        # Then - entire chain should be preserved
        assert root in gc.heap
        assert obj1 in gc.heap
        assert obj2 in gc.heap
        assert obj3 in gc.heap

        # Unreachable objects should be collected
        assert unreachable1 not in gc.heap
        assert unreachable2 not in gc.heap

        assert stats["objects_after"] == 4  # root, obj1, obj2, obj3

    def test_circular_reference_collection(self):
        """
        Integration test: Circular references are collected when unreachable.

        Scenario:
        1. Create cycle: objA -> objB -> objA
        2. Don't root either object
        3. Run GC
        4. Verify both collected (cycle doesn't prevent collection)
        """
        # Given
        gc = GarbageCollector(heap_size_mb=10)

        class RefObject(HeapObject):
            def __init__(self, size):
                super().__init__(size)
                self._refs = []

            def add_reference(self, obj):
                self._refs.append(obj)

            def get_references(self):
                return self._refs

        # Create circular reference
        objA = RefObject(size=100)
        objB = RefObject(size=200)
        objA.add_reference(objB)
        objB.add_reference(objA)

        gc.heap.add(objA)
        gc.heap.add(objB)

        # Add a rooted object for comparison
        rooted = gc.allocate(50)
        gc.add_root(rooted)

        # When - run GC
        stats = gc.collect()

        # Then - cycle should be collected (not rooted)
        assert objA not in gc.heap
        assert objB not in gc.heap
        assert rooted in gc.heap
        assert len(gc.heap) == 1  # Only rooted object remains

    def test_multiple_gc_cycles(self):
        """
        Integration test: Multiple GC cycles work correctly.

        Scenario:
        1. Allocate and root objects
        2. Run GC (should keep all)
        3. Remove some roots
        4. Run GC (should collect unrooted)
        5. Add new roots
        6. Run GC (should keep new roots)
        """
        # Given
        gc = GarbageCollector(heap_size_mb=10)

        # Phase 1: Initial allocations
        obj1 = AllocateObject(gc, property_count=10)
        obj2 = AllocateArray(gc, length=20)
        obj3 = AllocateString(gc, value="test")

        gc.add_root(obj1)
        gc.add_root(obj2)
        gc.add_root(obj3)

        # GC cycle 1 - all rooted
        stats1 = gc.collect()
        assert len(gc.heap) == 3
        assert stats1["bytes_freed"] == 0  # Nothing collected

        # Phase 2: Remove some roots and add garbage
        gc.remove_root(obj2)
        garbage = AllocateObject(gc, property_count=5)

        # GC cycle 2 - should collect obj2 and garbage
        stats2 = gc.collect()
        assert obj1 in gc.heap
        assert obj3 in gc.heap
        assert obj2 not in gc.heap
        assert garbage not in gc.heap
        assert len(gc.heap) == 2

        # Phase 3: Add new roots
        obj4 = AllocateArray(gc, length=30)
        gc.add_root(obj4)

        # GC cycle 3 - should keep all rooted
        stats3 = gc.collect()
        assert len(gc.heap) == 3
        assert obj1 in gc.heap
        assert obj3 in gc.heap
        assert obj4 in gc.heap

    def test_realistic_javascript_heap_simulation(self):
        """
        Integration test: Simulate realistic JavaScript heap usage.

        Scenario:
        1. Simulate creating JavaScript objects, arrays, and strings
        2. Simulate some becoming garbage
        3. Verify GC reclaims memory correctly
        """
        # Given
        gc = GarbageCollector(heap_size_mb=5)

        # Simulate creating objects for a program
        global_objects = []

        # Create some "global" objects (persisted)
        window_obj = AllocateObject(gc, property_count=20)
        gc.add_root(window_obj)
        global_objects.append(window_obj)

        document_obj = AllocateObject(gc, property_count=15)
        gc.add_root(document_obj)
        global_objects.append(document_obj)

        # Simulate function calls creating temporary objects
        for i in range(10):
            # Temporary objects (function locals)
            temp_obj = AllocateObject(gc, property_count=5)
            temp_arr = AllocateArray(gc, length=10)
            temp_str = AllocateString(gc, value=f"temporary {i}")
            # These go out of scope (not rooted)

        # Simulate some persistent data
        data_array = AllocateArray(gc, length=100)
        gc.add_root(data_array)
        global_objects.append(data_array)

        # When - trigger GC (simulating periodic collection)
        stats = gc.collect()

        # Then - only rooted objects should remain
        assert len(gc.heap) == len(global_objects)
        for obj in global_objects:
            assert obj in gc.heap

        # Verify substantial memory was freed (30 temporary objects)
        assert stats["bytes_freed"] > 1000  # At least 1KB freed

    def test_allocation_after_full_collection(self):
        """
        Integration test: Allocations work correctly after full collection.

        Scenario:
        1. Fill heap
        2. Run GC (everything garbage)
        3. Allocate new objects
        4. Verify new objects tracked correctly
        """
        # Given
        gc = GarbageCollector(heap_size_mb=2)

        # Fill heap with garbage
        for _ in range(20):
            AllocateObject(gc, property_count=100)

        # When - run GC (everything garbage)
        stats = gc.collect()

        # Then - heap should be empty
        assert len(gc.heap) == 0
        assert gc.used_bytes == 0

        # Allocate new objects
        obj1 = AllocateObject(gc, property_count=10)
        obj2 = AllocateArray(gc, length=20)
        obj3 = AllocateString(gc, value="new")

        # Verify new objects work correctly
        assert len(gc.heap) == 3
        assert obj1 in gc.heap
        assert obj2 in gc.heap
        assert obj3 in gc.heap
        assert gc.used_bytes > 0
