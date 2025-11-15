"""
Unit tests for Array.prototype.includes() (ES2024).

Tests FR-ES24-029: Array.prototype.includes()
Uses SameValueZero comparison (similar to === but treats NaN as equal to NaN)
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods


class TestArrayIncludes:
    """Test Array.prototype.includes() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_methods = ArrayMethods()

    def test_includes_element_present(self):
        """
        Given an array with elements
        When checking if element is included
        Then returns True
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.includes(arr, 3)

        # Then
        assert result is True

    def test_includes_element_not_present(self):
        """
        Given an array with elements
        When checking if element not in array
        Then returns False
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.includes(arr, 10)

        # Then
        assert result is False

    def test_includes_with_from_index(self):
        """
        Given an array with elements
        When checking with from_index parameter
        Then searches from that index
        """
        # Given
        arr = [1, 2, 3, 2, 1]

        # When
        result = self.array_methods.includes(arr, 2, from_index=2)

        # Then
        assert result is True  # Found at index 3

    def test_includes_with_from_index_not_found(self):
        """
        Given an array with elements
        When checking with from_index past element
        Then returns False
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.includes(arr, 2, from_index=3)

        # Then
        assert result is False

    def test_includes_with_negative_from_index(self):
        """
        Given an array with elements
        When checking with negative from_index
        Then starts from end (similar to at())
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.includes(arr, 4, from_index=-2)

        # Then
        assert result is True  # Searches from index 3

    def test_includes_nan_handling(self):
        """
        Given an array with NaN
        When checking for NaN
        Then returns True (SameValueZero)
        """
        # Given
        arr = [1, 2, float('nan'), 4, 5]

        # When
        result = self.array_methods.includes(arr, float('nan'))

        # Then
        # SameValueZero treats NaN as equal to NaN
        assert result is True

    def test_includes_string_element(self):
        """
        Given an array of strings
        When checking for string
        Then returns True if found
        """
        # Given
        arr = ["apple", "banana", "cherry"]

        # When
        result = self.array_methods.includes(arr, "banana")

        # Then
        assert result is True

    def test_includes_empty_array(self):
        """
        Given an empty array
        When checking for any element
        Then returns False
        """
        # Given
        arr = []

        # When
        result = self.array_methods.includes(arr, 1)

        # Then
        assert result is False

    def test_includes_zero_values(self):
        """
        Given an array with +0 and -0
        When checking for zero
        Then treats +0 and -0 as equal (SameValueZero)
        """
        # Given
        arr = [1, -0, 3]

        # When
        result = self.array_methods.includes(arr, +0)

        # Then
        assert result is True

    def test_includes_first_element(self):
        """
        Given an array
        When checking for first element
        Then returns True
        """
        # Given
        arr = [10, 20, 30]

        # When
        result = self.array_methods.includes(arr, 10)

        # Then
        assert result is True

    def test_includes_last_element(self):
        """
        Given an array
        When checking for last element
        Then returns True
        """
        # Given
        arr = [10, 20, 30]

        # When
        result = self.array_methods.includes(arr, 30)

        # Then
        assert result is True
