"""
Unit tests for Array.prototype.copyWithin() (ES2024).

Tests FR-ES24-033: Array.prototype.copyWithin()
Mutates array by copying sequence to different position
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods


class TestArrayCopyWithin:
    """Test Array.prototype.copyWithin() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_methods = ArrayMethods()

    def test_copy_within_basic(self):
        """
        Given an array
        When copying elements within array
        Then mutates array with copied sequence
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=3, end=5)

        # Then
        assert result == [4, 5, 3, 4, 5]
        assert result is arr  # Mutates in place

    def test_copy_within_no_end(self):
        """
        Given an array
        When copying without end parameter
        Then copies to end of array
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=3)

        # Then
        assert result == [4, 5, 3, 4, 5]

    def test_copy_within_overlapping(self):
        """
        Given an array
        When copy range overlaps target
        Then handles overlap correctly
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=2, start=0, end=2)

        # Then
        assert result == [1, 2, 1, 2, 5]

    def test_copy_within_negative_target(self):
        """
        Given an array
        When target is negative
        Then counts from end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=-2, start=0, end=2)

        # Then
        assert result == [1, 2, 3, 1, 2]

    def test_copy_within_negative_start(self):
        """
        Given an array
        When start is negative
        Then counts from end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=-2, end=5)

        # Then
        assert result == [4, 5, 3, 4, 5]

    def test_copy_within_negative_end(self):
        """
        Given an array
        When end is negative
        Then counts from end
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=1, end=-1)

        # Then
        assert result == [2, 3, 4, 4, 5]

    def test_copy_within_empty_range(self):
        """
        Given an array
        When start >= end
        Then no change to array
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=3, end=3)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_copy_within_beyond_length(self):
        """
        Given an array
        When target beyond length
        Then only copies what fits
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=10, start=0, end=2)

        # Then
        assert result == [1, 2, 3, 4, 5]  # No change

    def test_copy_within_entire_array(self):
        """
        Given an array
        When copying entire array to position 0
        Then array remains same
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=0)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_copy_within_returns_same_array(self):
        """
        Given an array
        When using copyWithin
        Then returns same array reference
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.copy_within(arr, target=0, start=1)

        # Then
        assert result is arr
