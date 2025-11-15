"""
Unit tests for Array.prototype.flatMap() (ES2024).

Tests FR-ES24-028: Array.prototype.flatMap()
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods


class TestArrayFlatMap:
    """Test Array.prototype.flatMap() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_methods = ArrayMethods()

    def test_flat_map_basic_mapping(self):
        """
        Given an array of numbers
        When flat mapping with function that returns array
        Then maps and flattens result
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.flat_map(arr, lambda x: [x, x * 2])

        # Then
        assert result == [1, 2, 2, 4, 3, 6]

    def test_flat_map_single_depth_flatten(self):
        """
        Given an array
        When flat mapping with nested return
        Then only flattens one level
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.flat_map(arr, lambda x: [[x]])

        # Then
        assert result == [[1], [2], [3]]

    def test_flat_map_filter_operation(self):
        """
        Given an array
        When flat mapping with conditional empty array
        Then effectively filters elements
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.array_methods.flat_map(
            arr, lambda x: [x] if x % 2 == 0 else []
        )

        # Then
        assert result == [2, 4]

    def test_flat_map_with_index(self):
        """
        Given an array
        When flat mapping with callback receiving index
        Then uses both element and index
        """
        # Given
        arr = [10, 20, 30]

        # When
        result = self.array_methods.flat_map(
            arr, lambda x, i: [x, i]
        )

        # Then
        assert result == [10, 0, 20, 1, 30, 2]

    def test_flat_map_empty_array(self):
        """
        Given an empty array
        When flat mapping
        Then returns empty array
        """
        # Given
        arr = []

        # When
        result = self.array_methods.flat_map(arr, lambda x: [x, x])

        # Then
        assert result == []

    def test_flat_map_string_splitting(self):
        """
        Given an array of strings
        When flat mapping with split operation
        Then flattens characters
        """
        # Given
        arr = ["hello", "world"]

        # When
        result = self.array_methods.flat_map(arr, lambda s: list(s))

        # Then
        assert result == ['h', 'e', 'l', 'l', 'o', 'w', 'o', 'r', 'l', 'd']

    def test_flat_map_this_arg_binding(self):
        """
        Given an array and this_arg
        When flat mapping with this_arg
        Then callback has correct this binding
        """
        # Given
        arr = [1, 2, 3]
        context = {"multiplier": 10}

        # When
        def callback(x):
            # In Python, we simulate this with a closure
            return [x * context["multiplier"]]

        result = self.array_methods.flat_map(arr, callback, this_arg=context)

        # Then
        assert result == [10, 20, 30]

    def test_flat_map_with_non_array_return(self):
        """
        Given an array
        When flat mapping with non-array return
        Then wraps in array
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.flat_map(arr, lambda x: x * 2)

        # Then
        # Behavior: non-array returns should be treated as single element
        assert result == [2, 4, 6]

    def test_flat_map_multiple_elements(self):
        """
        Given an array
        When flat mapping returns variable length arrays
        Then correctly flattens all
        """
        # Given
        arr = [1, 2, 3]

        # When
        result = self.array_methods.flat_map(
            arr, lambda x: [x] * x
        )

        # Then
        assert result == [1, 2, 2, 3, 3, 3]

    def test_flat_map_performance_characteristic(self):
        """
        Given a large array
        When flat mapping
        Then completes in reasonable time (O(n))
        """
        # Given
        arr = list(range(1000))

        # When
        import time
        start = time.time()
        result = self.array_methods.flat_map(arr, lambda x: [x, x + 1])
        elapsed = time.time() - start

        # Then
        assert len(result) == 2000
        assert elapsed < 0.1  # Should be very fast for 1000 elements
