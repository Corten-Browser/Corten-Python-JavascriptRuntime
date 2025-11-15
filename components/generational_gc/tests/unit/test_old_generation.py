"""
Unit tests for OldGeneration.

Tests the tenured space for long-lived objects using
free-list allocation and mark-sweep collection.
"""

import pytest


class TestOldGenerationInit:
    """Test OldGeneration initialization."""

    def test_create_with_default_size(self):
        """
        Given no size specified
        When OldGeneration is created
        Then it should have default 64MB size
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration()

        assert old_gen.size == 64 * 1024 * 1024  # 64MB
        assert old_gen.used_bytes == 0

    def test_create_with_custom_size(self):
        """
        Given a custom size
        When OldGeneration is created
        Then it should use that size
        """
        from components.generational_gc.src.old_generation import OldGeneration

        size = 128 * 1024 * 1024  # 128MB
        old_gen = OldGeneration(size=size)

        assert old_gen.size == size
        assert old_gen.used_bytes == 0

    def test_create_with_invalid_size(self):
        """
        Given an invalid size (<=0)
        When OldGeneration is created
        Then it should raise ValueError
        """
        from components.generational_gc.src.old_generation import OldGeneration

        with pytest.raises(ValueError, match="size must be positive"):
            OldGeneration(size=0)


class TestOldGenerationPromote:
    """Test promoting objects from young to old generation."""

    def test_promote_single_object(self):
        """
        Given old generation with space
        When promoting an object from young generation
        Then object should be allocated in old generation
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)
        obj_size = 100

        new_ptr = old_gen.promote(obj_ptr=12345, size=obj_size)

        assert new_ptr is not None
        assert old_gen.used_bytes == obj_size
        assert old_gen.contains_object(new_ptr) is True

    def test_promote_multiple_objects(self):
        """
        Given old generation
        When promoting multiple objects
        Then all should be allocated successfully
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        ptr1 = old_gen.promote(obj_ptr=100, size=100)
        ptr2 = old_gen.promote(obj_ptr=200, size=200)
        ptr3 = old_gen.promote(obj_ptr=300, size=50)

        assert ptr1 is not None
        assert ptr2 is not None
        assert ptr3 is not None
        assert old_gen.used_bytes == 350

    def test_promote_when_full(self):
        """
        Given full old generation
        When trying to promote an object
        Then promotion should fail (return None)
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1000)

        # Fill the space
        old_gen.promote(obj_ptr=1, size=900)

        # Try to promote more than remaining
        ptr = old_gen.promote(obj_ptr=2, size=200)

        assert ptr is None


class TestOldGenerationNeedsMajorGC:
    """Test checking if major GC is needed."""

    def test_needs_gc_when_empty(self):
        """
        Given empty old generation
        When checking if major GC needed
        Then it should return False
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        assert old_gen.needs_major_gc() is False

    def test_needs_gc_when_partially_filled(self):
        """
        Given partially filled old generation (<75%)
        When checking if major GC needed
        Then it should return False
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1000)
        old_gen.promote(obj_ptr=1, size=500)  # 50% full

        assert old_gen.needs_major_gc() is False

    def test_needs_gc_when_over_threshold(self):
        """
        Given old generation >75% full
        When checking if major GC needed
        Then it should return True
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1000)
        old_gen.promote(obj_ptr=1, size=800)  # 80% full

        assert old_gen.needs_major_gc() is True


class TestOldGenerationMarkSweep:
    """Test mark-sweep collection."""

    def test_mark_sweep_with_all_reachable(self):
        """
        Given old generation with reachable objects
        When mark-sweep is performed with all as roots
        Then no objects should be collected
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        ptr1 = old_gen.promote(obj_ptr=1, size=100)
        ptr2 = old_gen.promote(obj_ptr=2, size=200)

        # All objects are roots (reachable)
        roots = [ptr1, ptr2]
        stats = old_gen.mark_sweep(roots=roots)

        assert stats['objects_freed'] == 0
        assert stats['bytes_freed'] == 0
        assert old_gen.used_bytes == 300

    def test_mark_sweep_with_unreachable_objects(self):
        """
        Given old generation with unreachable objects
        When mark-sweep is performed
        Then unreachable objects should be collected
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        ptr1 = old_gen.promote(obj_ptr=1, size=100)
        ptr2 = old_gen.promote(obj_ptr=2, size=200)
        ptr3 = old_gen.promote(obj_ptr=3, size=50)

        # Only ptr1 is reachable
        roots = [ptr1]
        stats = old_gen.mark_sweep(roots=roots)

        assert stats['objects_freed'] == 2
        assert stats['bytes_freed'] == 250
        assert old_gen.used_bytes == 100
        assert old_gen.contains_object(ptr1) is True
        assert old_gen.contains_object(ptr2) is False
        assert old_gen.contains_object(ptr3) is False

    def test_mark_sweep_with_no_roots(self):
        """
        Given old generation with objects
        When mark-sweep is performed with no roots
        Then all objects should be collected
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        old_gen.promote(obj_ptr=1, size=100)
        old_gen.promote(obj_ptr=2, size=200)

        # No roots - all objects unreachable
        stats = old_gen.mark_sweep(roots=[])

        assert stats['objects_freed'] == 2
        assert stats['bytes_freed'] == 300
        assert old_gen.used_bytes == 0


class TestOldGenerationContainsObject:
    """Test checking if object exists."""

    def test_contains_promoted_object(self):
        """
        Given promoted object in old generation
        When checking if it exists
        Then it should return True
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        ptr = old_gen.promote(obj_ptr=1, size=100)

        assert old_gen.contains_object(ptr) is True

    def test_contains_nonexistent_object(self):
        """
        Given old generation
        When checking for non-existent object
        Then it should return False
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=1024)

        assert old_gen.contains_object(12345) is False


class TestOldGenerationStatistics:
    """Test statistics tracking."""

    def test_get_statistics(self):
        """
        Given old generation with promoted objects
        When getting statistics
        Then stats should reflect current state
        """
        from components.generational_gc.src.old_generation import OldGeneration

        old_gen = OldGeneration(size=2048)
        old_gen.promote(obj_ptr=1, size=500)
        old_gen.promote(obj_ptr=2, size=300)

        stats = old_gen.get_stats()

        assert stats['size'] == 2048
        assert stats['used_bytes'] == 800
        assert stats['free_bytes'] == 1248
        assert stats['utilization'] == pytest.approx(800 / 2048)
        assert stats['object_count'] == 2
