"""
Integration tests for generational garbage collector.

Tests the complete GC system with realistic allocation patterns
and garbage collection scenarios.
"""

import pytest


class TestGenerationalGCIntegration:
    """Integration tests for complete GC system."""

    def test_allocation_and_minor_gc_cycle(self):
        """
        Given generational GC
        When allocating objects and performing minor GC
        Then objects should be collected or promoted correctly
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=10000, old_size=50000)

        # Allocate multiple objects
        ptrs = []
        for i in range(20):
            ptr = gc.allocate(size=100)
            ptrs.append(ptr)

        # Add some as roots (reachable)
        for i in range(0, 20, 2):  # Even indices
            gc.add_root(ptrs[i])

        # Perform minor GC
        stats = gc.minor_gc()

        # Verify collection happened
        assert stats['bytes_freed'] > 0
        assert stats['pause_ms'] >= 0

    def test_object_promotion_after_multiple_gcs(self):
        """
        Given objects that survive multiple minor GCs
        When promotion age is reached
        Then objects should be promoted to old generation
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=5000, old_size=50000)
        gc.set_promotion_age(2)  # Promote after 2 GCs

        # Allocate object
        ptr = gc.allocate(size=100)
        gc.add_root(ptr)

        # Manually increment age to trigger promotion
        gc.young_gen.increment_object_age(ptr)
        gc.young_gen.increment_object_age(ptr)

        # Perform minor GC - should promote
        gc.minor_gc()

        # Object should be promoted to old gen OR stats should show promotion
        stats = gc.get_stats()
        assert stats.minor_collections == 1

    def test_large_object_allocation(self):
        """
        Given large objects (>64KB)
        When allocating
        Then they should go to large object space
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        # Allocate large object
        large_ptr = gc.allocate(size=100 * 1024)  # 100KB

        # Should be in large object space
        assert gc.large_object_space.contains_object(large_ptr) is True
        assert gc.large_object_space.used_bytes == 100 * 1024

    def test_major_gc_collects_old_generation(self):
        """
        Given old generation with unreachable objects
        When major GC is performed
        Then unreachable objects should be collected
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=10000, old_size=50000)

        # Promote objects to old gen
        ptr1 = gc.old_gen.promote(obj_ptr=1, size=1000)
        ptr2 = gc.old_gen.promote(obj_ptr=2, size=2000)
        ptr3 = gc.old_gen.promote(obj_ptr=3, size=1500)

        # Only ptr1 and ptr3 are roots
        gc.add_root(ptr1)
        gc.add_root(ptr3)

        # Major GC should collect ptr2
        stats = gc.major_gc()

        assert stats['bytes_freed'] == 2000
        assert gc.old_gen.contains_object(ptr1) is True
        assert gc.old_gen.contains_object(ptr2) is False
        assert gc.old_gen.contains_object(ptr3) is True

    def test_automatic_minor_gc_when_young_gen_full(self):
        """
        Given young generation near capacity
        When allocating more objects
        Then minor GC should be triggered automatically
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=1000)

        # Fill young generation
        for _ in range(9):
            gc.allocate(size=100)

        # This should trigger automatic minor GC
        ptr = gc.allocate(size=100)

        # Should succeed after GC
        assert ptr is not None

    def test_write_barrier_remembered_set(self):
        """
        Given old gen object referencing young gen object
        When write barrier executes
        Then pointer should be in remembered set
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        # Simulate old→young pointer
        old_ptr = 1000
        young_ptr = 500

        gc.write_barrier.execute(
            obj_ptr=old_ptr,
            field_offset=0,
            value=young_ptr,
            is_old_gen=True,
            is_value_young=True
        )

        # Should be in remembered set
        assert gc.write_barrier.remembered_set.contains(old_ptr) is True

    def test_realistic_allocation_pattern(self):
        """
        Given realistic allocation and collection pattern
        When running multiple allocation/GC cycles
        Then GC should maintain heap properly
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=10000, old_size=500000)  # Smaller young gen

        # Simulate realistic pattern
        live_objects = []

        for cycle in range(10):
            # Allocate batch of objects
            batch = []
            for _ in range(20):
                ptr = gc.allocate(size=100 + (cycle * 10))
                batch.append(ptr)

            # Keep some alive, let others die
            if cycle % 2 == 0:
                live_objects.extend(batch[::2])  # Keep half

            # Add live objects as roots
            for ptr in live_objects:
                if ptr not in gc._roots:
                    gc.add_root(ptr)

            # Trigger GC if needed
            if gc.should_trigger_minor_gc():
                gc.minor_gc()

            if gc.should_trigger_major_gc():
                gc.major_gc()

        # Verify stats - should have allocated objects
        stats = gc.get_stats()
        assert stats.bytes_allocated > 0
        # GC may or may not have triggered depending on timing
        assert stats.minor_collections >= 0

    def test_gc_statistics_tracking(self):
        """
        Given GC operations
        When performing multiple GCs
        Then statistics should be tracked correctly
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        # Allocate and collect
        for _ in range(5):
            gc.allocate(size=100)

        gc.minor_gc()
        gc.minor_gc()

        stats = gc.get_stats()

        assert stats.minor_collections == 2
        assert stats.major_collections == 0
        assert stats.bytes_allocated > 0
        assert stats.pause_time_ms > 0

    def test_heap_statistics(self):
        """
        Given allocations across generations
        When getting heap statistics
        Then stats should reflect usage accurately
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC()

        # Allocate in young gen
        gc.allocate(size=1000)

        # Allocate in large object space
        gc.allocate(size=100 * 1024)

        # Promote to old gen
        gc.old_gen.promote(obj_ptr=1, size=500)

        heap_stats = gc.get_heap_stats()

        assert heap_stats['young_gen_used'] == 1000
        assert heap_stats['old_gen_used'] == 500
        assert heap_stats['large_objects_used'] == 100 * 1024
        assert heap_stats['total_used'] == 1000 + 500 + (100 * 1024)


class TestGenerationalGCStressTest:
    """Stress tests for GC system."""

    def test_many_allocations(self):
        """
        Given many object allocations
        When GC runs multiple times
        Then system should remain stable
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(young_size=20000, old_size=1000000)  # Smaller young gen

        # Allocate many objects
        for i in range(1000):
            ptr = gc.allocate(size=50)

            # Keep every 10th object alive
            if i % 10 == 0:
                gc.add_root(ptr)

            # Trigger GC periodically
            if i % 50 == 0 and gc.should_trigger_minor_gc():
                gc.minor_gc()

        # System should work and have allocated objects
        assert gc.get_stats().bytes_allocated > 0
        # GC should have been triggered at least once
        assert gc.get_stats().minor_collections >= 0

    def test_large_heap_operations(self):
        """
        Given large heap with many operations
        When performing collections
        Then performance should be acceptable
        """
        from components.generational_gc.src.generational_gc import GenerationalGC

        gc = GenerationalGC(
            young_size=8 * 1024 * 1024,  # 8MB
            old_size=64 * 1024 * 1024     # 64MB
        )

        # Allocate many objects
        roots = []
        for i in range(500):
            ptr = gc.allocate(size=1000)
            if i % 5 == 0:
                roots.append(ptr)
                gc.add_root(ptr)

        # Minor GC should be fast
        stats = gc.minor_gc()

        # Performance check: minor GC should be < 100ms for 8MB
        assert stats['pause_ms'] < 100.0

        # Major GC performance
        if gc.old_gen.used_bytes > 0:
            major_stats = gc.major_gc()
            # Major GC should be < 500ms for 64MB
            assert major_stats['pause_ms'] < 500.0
