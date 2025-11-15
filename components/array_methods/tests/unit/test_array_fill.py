"""
Unit tests for Array.prototype.fill() (ES2024).

Tests FR-ES24-034: Array.prototype.fill()
Mutates array by filling with value
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods


class TestArrayFill:
    """Test Array.prototype.fill() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_methods = ArrayMethods()

    def test_fill_entire_array(self):
        """
        Given an array
        When filling without start/end
        Then fills entire array with value
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0)

        # Then
        assert result == [0, 0, 0, 0, 0]
        assert result is arr  # Mutates in place

    def test_fill_with_start(self):
        """
        Given an array
        When filling with start index
        Then fills from start to end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0, start=2)

        # Then
        assert result == [1, 2, 0, 0, 0]

    def test_fill_with_start_and_end(self):
        """
        Given an array
        When filling with start and end indices
        Then fills range [start, end)
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0, start=1, end=4)

        # Then
        assert result == [1, 0, 0, 0, 5]

    def test_fill_negative_start(self):
        """
        Given an array
        When filling with negative start
        Then counts from end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0, start=-3)

        # Then
        assert result == [1, 2, 0, 0, 0]

    def test_fill_negative_end(self):
        """
        Given an array
        When filling with negative end
        Then counts from end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0, start=1, end=-1)

        # Then
        assert result == [1, 0, 0, 0, 5]

    def test_fill_with_object(self):
        """
        Given an array
        When filling with object
        Then fills with same object reference
        """
        # Given
        arr = [1, 2, 3, 4, 5]
        obj = {"key": "value"}

        # When
        result = self.array_methods.fill(arr, value=obj)

        # Then
        assert result == [obj, obj, obj, obj, obj]
        assert result[0] is result[1]  # Same reference

    def test_fill_with_string(self):
        """
        Given an array
        When filling with string
        Then fills with string value
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value="x")

        # Then
        assert result == ["x", "x", "x", "x", "x"]

    def test_fill_empty_range(self):
        """
        Given an array
        When start >= end
        Then no change to array
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0, start=3, end=3)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_fill_empty_array(self):
        """
        Given an empty array
        When filling
        Then returns empty array
        """
        # Given
        arr = []

        # When
        result = self.array_methods.fill(arr, value=0)

        # Then
        assert result == []

    def test_fill_single_element(self):
        """
        Given an array with one element
        When filling
        Then replaces that element
        """
        # Given
        arr = [1]

        # When
        result = self.array_methods.fill(arr, value=99)

        # Then
        assert result == [99]

    def test_fill_returns_same_array(self):
        """
        Given an array
        When using fill
        Then returns same array reference
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.fill(arr, value=0)

        # Then
        assert result is arr
