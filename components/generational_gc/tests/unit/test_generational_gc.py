"""
Unit tests for GenerationalGC.

Tests the main generational garbage collector integrating
young generation, old generation, write barriers, and remembered sets.
"""

import pytest


class TestGenerationalGCInit:
    """Test GenerationalGC initialization."""

    def test_create_with_default_sizes(self):
        """
        Given no parameters
        When GenerationalGC is created
        Then it should use default sizes (8MB young, 64MB old)
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        assert gc.young_gen.size == 8 * 1024 * 1024
        assert gc.old_gen.size == 64 * 1024 * 1024

    def test_create_with_custom_sizes(self):
        """
        Given custom young and old sizes
        When GenerationalGC is created
        Then it should use those sizes
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        young_size = 16 * 1024 * 1024
        old_size = 128 * 1024 * 1024

        gc = GenerationalGC(young_size=young_size, old_size=old_size)

        assert gc.young_gen.size == young_size
        assert gc.old_gen.size == old_size


class TestGenerationalGCAllocate:
    """Test object allocation."""

    def test_allocate_small_object_in_young_gen(self):
        """
        Given generational GC
        When allocating small object (<64KB)
        Then it should be allocated in young generation
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()
        obj_size = 100

        ptr = gc.allocate(size=obj_size)

        assert ptr is not None
        assert gc.young_gen.contains_object(ptr) is True

    def test_allocate_large_object_in_large_space(self):
        """
        Given generational GC
        When allocating large object (>64KB)
        Then it should be allocated in large object space
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()
        obj_size = 100 * 1024  # 100KB

        ptr = gc.allocate(size=obj_size)

        assert ptr is not None
        assert gc.large_object_space.contains_object(ptr) is True

    def test_allocate_multiple_objects(self):
        """
        Given generational GC
        When allocating multiple objects
        Then all should be allocated successfully
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        ptr1 = gc.allocate(size=100)
        ptr2 = gc.allocate(size=200)
        ptr3 = gc.allocate(size=50)

        assert ptr1 is not None
        assert ptr2 is not None
        assert ptr3 is not None


class TestGenerationalGCMinorGC:
    """Test minor GC (scavenge)."""

    def test_minor_gc_with_no_roots(self):
        """
        Given young generation with objects
        When minor GC is performed with no roots
        Then all objects should be collected
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        gc.allocate(size=100)
        gc.allocate(size=200)

        stats = gc.minor_gc()

        assert gc.young_gen.used_bytes == 0
        assert stats['bytes_freed'] > 0

    def test_minor_gc_with_roots(self):
        """
        Given young generation with reachable objects
        When minor GC is performed
        Then reachable objects should survive
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        ptr1 = gc.allocate(size=100)
        ptr2 = gc.allocate(size=200)

        gc.add_root(ptr1)

        gc.minor_gc()

        # ptr1 should survive (either in young gen or promoted)
        # ptr2 should be collected
        assert gc.young_gen.used_bytes <= 100 or gc.old_gen.used_bytes > 0


class TestGenerationalGCMajorGC:
    """Test major GC (mark-sweep old generation)."""

    def test_major_gc_with_empty_old_gen(self):
        """
        Given empty old generation
        When major GC is performed
        Then nothing should be collected
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        stats = gc.major_gc()

        assert stats['bytes_freed'] == 0

    def test_major_gc_with_unreachable_objects(self):
        """
        Given old generation with unreachable objects
        When major GC is performed
        Then unreachable objects should be collected
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        # Promote some objects to old gen
        ptr1 = gc.old_gen.promote(obj_ptr=1, size=100)
        ptr2 = gc.old_gen.promote(obj_ptr=2, size=200)

        # Only ptr1 is root
        gc.add_root(ptr1)

        stats = gc.major_gc()

        assert stats['bytes_freed'] == 200
        assert gc.old_gen.contains_object(ptr1) is True
        assert gc.old_gen.contains_object(ptr2) is False


class TestGenerationalGCTriggers:
    """Test GC triggering heuristics."""

    def test_should_trigger_minor_gc_when_young_gen_full(self):
        """
        Given young generation that is full
        When checking if minor GC should trigger
        Then it should return True
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=1000)

        # Fill young generation
        gc.allocate(size=950)  # 95% full

        assert gc.should_trigger_minor_gc() is True

    def test_should_trigger_major_gc_when_old_gen_full(self):
        """
        Given old generation >75% full
        When checking if major GC should trigger
        Then it should return True
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(old_size=1000)

        # Fill old generation
        gc.old_gen.promote(obj_ptr=1, size=800)  # 80% full

        assert gc.should_trigger_major_gc() is True


class TestGenerationalGCRoots:
    """Test root management."""

    def test_add_root(self):
        """
        Given generational GC
        When adding a root
        Then root should be tracked
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        ptr = gc.allocate(size=100)
        gc.add_root(ptr)

        assert ptr in gc._roots

    def test_remove_root(self):
        """
        Given generational GC with a root
        When removing the root
        Then root should no longer be tracked
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        ptr = gc.allocate(size=100)
        gc.add_root(ptr)
        gc.remove_root(ptr)

        assert ptr not in gc._roots


class TestGenerationalGCStatistics:
    """Test statistics tracking."""

    def test_get_stats_initially(self):
        """
        Given new generational GC
        When getting statistics
        Then stats should show no collections
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        stats = gc.get_stats()

        assert stats.minor_collections == 0
        assert stats.major_collections == 0

    def test_get_stats_after_minor_gc(self):
        """
        Given generational GC
        When performing minor GC
        Then stats should reflect the collection
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        gc.allocate(size=100)
        gc.minor_gc()

        stats = gc.get_stats()

        assert stats.minor_collections == 1
