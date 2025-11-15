"""
Unit tests for RememberedSet.

Tests the remembered set that tracks cross-generational pointers
(old generation → young generation).
"""

import pytest


class TestRememberedSetInit:
    """Test RememberedSet initialization."""

    def test_create_empty_remembered_set(self):
        """
        Given no pointers
        When RememberedSet is created
        Then it should be empty
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        assert len(rs) == 0
        assert list(rs.iterate()) == []


class TestRememberedSetAdd:
    """Test adding pointers to remembered set."""

    def test_add_single_pointer(self):
        """
        Given an empty remembered set
        When a pointer is added
        Then the set should contain that pointer
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        ptr = 12345

        rs.add(ptr)

        assert len(rs) == 1
        assert ptr in list(rs.iterate())

    def test_add_multiple_pointers(self):
        """
        Given an empty remembered set
        When multiple unique pointers are added
        Then the set should contain all pointers
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        pointers = [100, 200, 300, 400]

        for ptr in pointers:
            rs.add(ptr)

        assert len(rs) == 4
        result = list(rs.iterate())
        for ptr in pointers:
            assert ptr in result

    def test_add_duplicate_pointer(self):
        """
        Given a remembered set with a pointer
        When the same pointer is added again
        Then the set should still contain only one copy
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        ptr = 12345

        rs.add(ptr)
        rs.add(ptr)
        rs.add(ptr)

        assert len(rs) == 1
        assert list(rs.iterate()).count(ptr) == 1


class TestRememberedSetRemove:
    """Test removing pointers from remembered set."""

    def test_remove_existing_pointer(self):
        """
        Given a remembered set with a pointer
        When that pointer is removed
        Then the set should no longer contain it
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        ptr = 12345

        rs.add(ptr)
        rs.remove(ptr)

        assert len(rs) == 0
        assert ptr not in list(rs.iterate())

    def test_remove_nonexistent_pointer(self):
        """
        Given a remembered set
        When removing a pointer that doesn't exist
        Then no error should occur
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        # Should not raise
        rs.remove(12345)

        assert len(rs) == 0


class TestRememberedSetClear:
    """Test clearing the remembered set."""

    def test_clear_empty_set(self):
        """
        Given an empty remembered set
        When clear is called
        Then the set should remain empty
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        rs.clear()

        assert len(rs) == 0

    def test_clear_populated_set(self):
        """
        Given a remembered set with multiple pointers
        When clear is called
        Then the set should become empty
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        pointers = [100, 200, 300, 400, 500]

        for ptr in pointers:
            rs.add(ptr)

        assert len(rs) == 5

        rs.clear()

        assert len(rs) == 0
        assert list(rs.iterate()) == []


class TestRememberedSetIterate:
    """Test iterating over remembered set."""

    def test_iterate_empty_set(self):
        """
        Given an empty remembered set
        When iterating
        Then no pointers should be yielded
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        result = list(rs.iterate())

        assert result == []

    def test_iterate_populated_set(self):
        """
        Given a remembered set with pointers
        When iterating
        Then all pointers should be yielded
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        pointers = [100, 200, 300]

        for ptr in pointers:
            rs.add(ptr)

        result = set(rs.iterate())

        assert result == set(pointers)

    def test_iterate_multiple_times(self):
        """
        Given a remembered set
        When iterating multiple times
        Then results should be consistent
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        pointers = [100, 200, 300]

        for ptr in pointers:
            rs.add(ptr)

        result1 = set(rs.iterate())
        result2 = set(rs.iterate())

        assert result1 == result2 == set(pointers)


class TestRememberedSetContains:
    """Test checking if pointer is in remembered set."""

    def test_contains_existing_pointer(self):
        """
        Given a remembered set with a pointer
        When checking if it contains that pointer
        Then it should return True
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        ptr = 12345

        rs.add(ptr)

        assert rs.contains(ptr) is True

    def test_contains_nonexistent_pointer(self):
        """
        Given a remembered set
        When checking for a pointer not in the set
        Then it should return False
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        assert rs.contains(12345) is False


class TestRememberedSetStressTest:
    """Stress tests for remembered set."""

    def test_large_number_of_pointers(self):
        """
        Given a remembered set
        When adding a large number of pointers
        Then all should be stored correctly
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()
        num_pointers = 10000
        pointers = list(range(num_pointers))

        for ptr in pointers:
            rs.add(ptr)

        assert len(rs) == num_pointers

        result = set(rs.iterate())
        assert len(result) == num_pointers

    def test_add_remove_pattern(self):
        """
        Given a remembered set
        When adding and removing pointers in a pattern
        Then final state should be correct
        """
        from components.generational_gc.src.remembered_set import RememberedSet

        rs = RememberedSet()

        # Add 100 pointers
        for i in range(100):
            rs.add(i)

        # Remove even pointers
        for i in range(0, 100, 2):
            rs.remove(i)

        assert len(rs) == 50

        result = set(rs.iterate())
        expected = set(range(1, 100, 2))
        assert result == expected
