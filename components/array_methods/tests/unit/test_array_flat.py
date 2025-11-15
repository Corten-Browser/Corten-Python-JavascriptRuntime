"""
Unit tests for Array.prototype.flat() (ES2024).

Tests FR-ES24-027: Array.prototype.flat()
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods


class TestArrayFlat:
    """Test Array.prototype.flat() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_methods = ArrayMethods()

    def test_flat_default_depth_one(self):
        """
        Given a nested array with depth 2
        When flattening with default depth (1)
        Then flattens one level
        """
        # Given
        arr = [1, [2, 3], [4, [5, 6]]]

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == [1, 2, 3, 4, [5, 6]]

    def test_flat_depth_zero(self):
        """
        Given a nested array
        When flattening with depth 0
        Then returns shallow copy without flattening
        """
        # Given
        arr = [1, [2, 3], [4, [5, 6]]]

        # When
        result = self.array_methods.flat(arr, depth=0)

        # Then
        assert result == [1, [2, 3], [4, [5, 6]]]
        assert result is not arr  # Verify it's a copy

    def test_flat_depth_two(self):
        """
        Given a nested array with depth 3
        When flattening with depth 2
        Then flattens two levels
        """
        # Given
        arr = [1, [2, [3, [4, 5]]]]

        # When
        result = self.array_methods.flat(arr, depth=2)

        # Then
        assert result == [1, 2, 3, [4, 5]]

    def test_flat_depth_infinity(self):
        """
        Given a deeply nested array
        When flattening with depth=float('inf')
        Then completely flattens array
        """
        # Given
        arr = [1, [2, [3, [4, [5]]]]]

        # When
        result = self.array_methods.flat(arr, depth=float('inf'))

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_flat_empty_array(self):
        """
        Given an empty array
        When flattening
        Then returns empty array
        """
        # Given
        arr = []

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == []

    def test_flat_no_nesting(self):
        """
        Given a flat array (no nesting)
        When flattening
        Then returns copy of array
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == [1, 2, 3, 4, 5]
        assert result is not arr

    def test_flat_removes_empty_slots(self):
        """
        Given an array with empty slots
        When flattening
        Then removes empty slots
        """
        # Given
        arr = [1, 2, None, 4, 5]

        # When
        result = self.array_methods.flat(arr)

        # Then
        # In JavaScript, flat() removes empty slots
        assert None not in result or result == [1, 2, 4, 5]

    def test_flat_with_nested_empty_arrays(self):
        """
        Given an array with nested empty arrays
        When flattening
        Then removes empty arrays
        """
        # Given
        arr = [1, [], 2, [[]], 3]

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == [1, 2, [], 3]

    def test_flat_mixed_types(self):
        """
        Given an array with mixed types
        When flattening
        Then preserves non-array elements
        """
        # Given
        arr = [1, "hello", [2, "world"], {"key": "value"}]

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == [1, "hello", 2, "world", {"key": "value"}]

    def test_flat_preserves_order(self):
        """
        Given a nested array
        When flattening
        Then preserves element order
        """
        # Given
        arr = [[1, 2], [3, 4], [5, 6]]

        # When
        result = self.array_methods.flat(arr)

        # Then
        assert result == [1, 2, 3, 4, 5, 6]
