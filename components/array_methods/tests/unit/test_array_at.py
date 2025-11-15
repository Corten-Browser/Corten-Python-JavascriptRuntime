"""
Unit tests for Array.prototype.at() (ES2024).

Tests FR-ES24-026: Array.prototype.at()
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value


class TestArrayAt:
    """Test Array.prototype.at() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gc = GarbageCollector()
        self.array_methods = ArrayMethods()

    def test_at_positive_index(self):
        """
        Given an array with elements
        When accessing with positive index
        Then returns element at that index
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.at(arr, 2)

        # Then
        assert result == 3

    def test_at_negative_index(self):
        """
        Given an array with elements
        When accessing with negative index
        Then returns element from end (at -1 is last element)
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.at(arr, -1)

        # Then
        assert result == 5

    def test_at_negative_index_middle(self):
        """
        Given an array with elements
        When accessing with negative index -2
        Then returns second-to-last element
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.at(arr, -2)

        # Then
        assert result == 4

    def test_at_index_out_of_bounds_positive(self):
        """
        Given an array with elements
        When accessing with positive index >= length
        Then returns None (undefined behavior)
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.at(arr, 10)

        # Then
        assert result is None

    def test_at_index_out_of_bounds_negative(self):
        """
        Given an array with elements
        When accessing with negative index < -length
        Then returns None (undefined behavior)
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.at(arr, -10)

        # Then
        assert result is None

    def test_at_empty_array(self):
        """
        Given an empty array
        When accessing any index
        Then returns None
        """
        # Given
        arr = []

        # When
        result = self.array_methods.at(arr, 0)

        # Then
        assert result is None

    def test_at_zero_index(self):
        """
        Given an array with elements
        When accessing index 0
        Then returns first element
        """
        # Given
        arr = [10, 20, 30]

        # When
        result = self.array_methods.at(arr, 0)

        # Then
        assert result == 10

    def test_at_negative_one_single_element(self):
        """
        Given an array with one element
        When accessing index -1
        Then returns that element
        """
        # Given
        arr = [42]

        # When
        result = self.array_methods.at(arr, -1)

        # Then
        assert result == 42

    def test_at_with_sparse_array(self):
        """
        Given a sparse array (with holes)
        When accessing hole position
        Then returns None
        """
        # Given
        arr = [1, None, 3]

        # When
        result = self.array_methods.at(arr, 1)

        # Then
        assert result is None

    def test_at_with_string_elements(self):
        """
        Given an array of strings
        When accessing with positive index
        Then returns string at that position
        """
        # Given
        arr = ["a", "b", "c", "d"]

        # When
        result = self.array_methods.at(arr, 1)

        # Then
        assert result == "b"
