"""
Unit tests for YoungGeneration.

Tests the nursery space for newly allocated objects using
bump-pointer allocation and semi-space copying collection.
"""

import pytest


class TestYoungGenerationInit:
    """Test YoungGeneration initialization."""

    def test_create_with_default_size(self):
        """
        Given no size specified
        When YoungGeneration is created
        Then it should have default 8MB size
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration()

        assert young_gen.size == 8 * 1024 * 1024  # 8MB
        assert young_gen.used_bytes == 0
        assert young_gen.free_bytes == 8 * 1024 * 1024

    def test_create_with_custom_size(self):
        """
        Given a custom size
        When YoungGeneration is created
        Then it should use that size
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        size = 16 * 1024 * 1024  # 16MB
        young_gen = YoungGeneration(size=size)

        assert young_gen.size == size
        assert young_gen.used_bytes == 0
        assert young_gen.free_bytes == size

    def test_create_with_invalid_size(self):
        """
        Given an invalid size (<=0)
        When YoungGeneration is created
        Then it should raise ValueError
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        with pytest.raises(ValueError, match="size must be positive"):
            YoungGeneration(size=0)

        with pytest.raises(ValueError, match="size must be positive"):
            YoungGeneration(size=-1024)


class TestYoungGenerationAllocate:
    """Test bump-pointer allocation in young generation."""

    def test_allocate_small_object(self):
        """
        Given young generation with space
        When allocating a small object
        Then allocation should succeed with bump pointer
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)
        obj_size = 100

        ptr = young_gen.allocate(obj_size)

        assert ptr is not None
        assert young_gen.used_bytes == obj_size
        assert young_gen.free_bytes == 1024 - obj_size

    def test_allocate_multiple_objects(self):
        """
        Given young generation
        When allocating multiple objects
        Then pointers should be sequential (bump allocation)
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        ptr1 = young_gen.allocate(100)
        ptr2 = young_gen.allocate(200)
        ptr3 = young_gen.allocate(50)

        assert ptr1 is not None
        assert ptr2 is not None
        assert ptr3 is not None
        # Pointers should be sequential with bump allocation
        assert ptr2 > ptr1
        assert ptr3 > ptr2
        assert young_gen.used_bytes == 350

    def test_allocate_when_full(self):
        """
        Given young generation that is full
        When trying to allocate
        Then allocation should fail (return None)
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1000)

        # Fill the space
        young_gen.allocate(900)

        # Try to allocate more than remaining
        ptr = young_gen.allocate(200)

        assert ptr is None

    def test_allocate_exact_remaining_space(self):
        """
        Given young generation with exact space remaining
        When allocating that exact amount
        Then allocation should succeed
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1000)
        young_gen.allocate(600)

        ptr = young_gen.allocate(400)

        assert ptr is not None
        assert young_gen.used_bytes == 1000
        assert young_gen.free_bytes == 0

    def test_allocate_zero_bytes(self):
        """
        Given young generation
        When allocating zero bytes
        Then it should raise ValueError
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        with pytest.raises(ValueError, match="size must be positive"):
            young_gen.allocate(0)

    def test_allocate_negative_bytes(self):
        """
        Given young generation
        When allocating negative bytes
        Then it should raise ValueError
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        with pytest.raises(ValueError, match="size must be positive"):
            young_gen.allocate(-100)


class TestYoungGenerationIsFull:
    """Test checking if young generation is full."""

    def test_is_full_when_empty(self):
        """
        Given empty young generation
        When checking if full
        Then it should return False
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        assert young_gen.is_full() is False

    def test_is_full_when_partially_filled(self):
        """
        Given partially filled young generation
        When checking if full
        Then it should return False
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)
        young_gen.allocate(500)

        assert young_gen.is_full() is False

    def test_is_full_when_completely_full(self):
        """
        Given completely full young generation
        When checking if full
        Then it should return True
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)
        young_gen.allocate(1024)

        assert young_gen.is_full() is True

    def test_is_full_threshold(self):
        """
        Given young generation at >90% capacity
        When checking if full
        Then it should return True (trigger GC early)
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1000)
        young_gen.allocate(950)  # 95% full

        assert young_gen.is_full() is True


class TestYoungGenerationReset:
    """Test resetting young generation after scavenge."""

    def test_reset_empty_generation(self):
        """
        Given empty young generation
        When reset is called
        Then it should remain empty
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        young_gen.reset()

        assert young_gen.used_bytes == 0
        assert young_gen.free_bytes == 1024

    def test_reset_full_generation(self):
        """
        Given full young generation
        When reset is called
        Then all space should be reclaimed
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)
        young_gen.allocate(500)
        young_gen.allocate(300)

        young_gen.reset()

        assert young_gen.used_bytes == 0
        assert young_gen.free_bytes == 1024

    def test_allocate_after_reset(self):
        """
        Given reset young generation
        When allocating
        Then allocation should work normally
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)
        young_gen.allocate(800)
        young_gen.reset()

        ptr = young_gen.allocate(100)

        assert ptr is not None
        assert young_gen.used_bytes == 100


class TestYoungGenerationObjectTracking:
    """Test object tracking in young generation."""

    def test_track_allocated_object(self):
        """
        Given young generation
        When allocating an object
        Then the object should be tracked
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        ptr = young_gen.allocate(100)

        assert young_gen.contains_object(ptr) is True

    def test_track_multiple_objects(self):
        """
        Given young generation
        When allocating multiple objects
        Then all should be tracked
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        ptr1 = young_gen.allocate(100)
        ptr2 = young_gen.allocate(200)
        ptr3 = young_gen.allocate(50)

        assert young_gen.contains_object(ptr1) is True
        assert young_gen.contains_object(ptr2) is True
        assert young_gen.contains_object(ptr3) is True

    def test_get_object_age(self):
        """
        Given an allocated object
        When getting its age
        Then it should start at 0
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        ptr = young_gen.allocate(100)

        assert young_gen.get_object_age(ptr) == 0

    def test_increment_object_age(self):
        """
        Given an object that survived GC
        When incrementing its age
        Then age should increase
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=1024)

        ptr = young_gen.allocate(100)

        young_gen.increment_object_age(ptr)
        assert young_gen.get_object_age(ptr) == 1

        young_gen.increment_object_age(ptr)
        assert young_gen.get_object_age(ptr) == 2


class TestYoungGenerationStatistics:
    """Test statistics tracking."""

    def test_get_statistics(self):
        """
        Given young generation with allocations
        When getting statistics
        Then stats should reflect current state
        """
        from components.generational_gc.src.young_generation import YoungGeneration

        young_gen = YoungGeneration(size=2048)
        young_gen.allocate(500)
        young_gen.allocate(300)

        stats = young_gen.get_stats()

        assert stats['size'] == 2048
        assert stats['used_bytes'] == 800
        assert stats['free_bytes'] == 1248
        assert stats['utilization'] == pytest.approx(800 / 2048)
