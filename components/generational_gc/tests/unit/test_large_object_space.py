"""
Unit tests for LargeObjectSpace.

Tests the separate space for large objects (>64KB).
"""

import pytest


class TestLargeObjectSpaceInit:
    """Test LargeObjectSpace initialization."""

    def test_create_large_object_space(self):
        """
        Given no parameters
        When LargeObjectSpace is created
        Then it should be empty
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        assert los.used_bytes == 0
        assert los.object_count == 0


class TestLargeObjectSpaceAllocate:
    """Test allocating large objects."""

    def test_allocate_large_object(self):
        """
        Given large object space
        When allocating a large object
        Then it should be allocated
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()
        size = 100 * 1024  # 100KB

        ptr = los.allocate(size=size)

        assert ptr is not None
        assert los.used_bytes == size
        assert los.object_count == 1

    def test_allocate_multiple_large_objects(self):
        """
        Given large object space
        When allocating multiple large objects
        Then all should be allocated
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        ptr1 = los.allocate(size=100 * 1024)
        ptr2 = los.allocate(size=200 * 1024)
        ptr3 = los.allocate(size=150 * 1024)

        assert ptr1 is not None
        assert ptr2 is not None
        assert ptr3 is not None
        assert los.object_count == 3
        assert los.used_bytes == 450 * 1024


class TestLargeObjectSpaceMarkSweep:
    """Test mark-sweep collection for large objects."""

    def test_mark_sweep_with_all_reachable(self):
        """
        Given large object space with objects
        When mark-sweep is performed with all as roots
        Then no objects should be collected
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        ptr1 = los.allocate(size=100 * 1024)
        ptr2 = los.allocate(size=200 * 1024)

        # All objects are roots
        bytes_freed = los.mark_sweep(roots=[ptr1, ptr2])

        assert bytes_freed == 0
        assert los.object_count == 2

    def test_mark_sweep_with_unreachable_objects(self):
        """
        Given large object space with unreachable objects
        When mark-sweep is performed
        Then unreachable objects should be collected
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        ptr1 = los.allocate(size=100 * 1024)
        ptr2 = los.allocate(size=200 * 1024)

        # Only ptr1 is reachable
        bytes_freed = los.mark_sweep(roots=[ptr1])

        assert bytes_freed == 200 * 1024
        assert los.object_count == 1
        assert los.contains_object(ptr1) is True
        assert los.contains_object(ptr2) is False


class TestLargeObjectSpaceContains:
    """Test checking if object exists."""

    def test_contains_allocated_object(self):
        """
        Given allocated large object
        When checking if it exists
        Then it should return True
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        ptr = los.allocate(size=100 * 1024)

        assert los.contains_object(ptr) is True

    def test_contains_nonexistent_object(self):
        """
        Given large object space
        When checking for non-existent object
        Then it should return False
        """
        from components.generational_gc.src.large_object_space import LargeObjectSpace

        los = LargeObjectSpace()

        assert los.contains_object(12345) is False
