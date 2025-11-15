"""
Unit tests for Array.prototype.sort() stability (ES2024).

Tests FR-ES24-032: Array.prototype.sort() stability guarantee
ES2024 requires sort to be stable (equal elements maintain relative order)
"""

import pytest
from components.array_methods.src.array_sorting import ArraySorting


class TestArraySortStable:
    """Test Array.prototype.sort() stability."""

    def setup_method(self):
        """Set up test fixtures."""
        self.sorting = ArraySorting()

    def test_sort_stable_maintains_order(self):
        """
        Given an array with equal elements
        When sorting
        Then maintains relative order of equal elements (stable)
        """
        # Given
        # Objects with same value but different identities
        arr = [
            {"value": 2, "id": "a"},
            {"value": 1, "id": "b"},
            {"value": 2, "id": "c"},
            {"value": 1, "id": "d"},
        ]

        # When
        result = self.sorting.sort_stable(
            arr, compare_fn=lambda a, b: a["value"] - b["value"]
        )

        # Then
        # Elements with value=1: "b" should come before "d" (stable)
        # Elements with value=2: "a" should come before "c" (stable)
        assert result[0]["id"] == "b"
        assert result[1]["id"] == "d"
        assert result[2]["id"] == "a"
        assert result[3]["id"] == "c"

    def test_sort_stable_default_numeric(self):
        """
        Given an array of numbers
        When sorting without compare function
        Then sorts numerically in ascending order
        """
        # Given
        arr = [5, 2, 8, 1, 9, 3]

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result == [1, 2, 3, 5, 8, 9]

    def test_sort_stable_with_duplicates(self):
        """
        Given an array with many duplicates
        When sorting
        Then maintains relative order of duplicates
        """
        # Given
        arr = [
            {"value": 3, "order": 1},
            {"value": 1, "order": 2},
            {"value": 3, "order": 3},
            {"value": 1, "order": 4},
            {"value": 3, "order": 5},
        ]

        # When
        result = self.sorting.sort_stable(
            arr, compare_fn=lambda a, b: a["value"] - b["value"]
        )

        # Then
        # value=1 elements: order should be 2, 4
        assert result[0]["order"] == 2
        assert result[1]["order"] == 4
        # value=3 elements: order should be 1, 3, 5
        assert result[2]["order"] == 1
        assert result[3]["order"] == 3
        assert result[4]["order"] == 5

    def test_sort_stable_strings(self):
        """
        Given an array of strings
        When sorting
        Then sorts alphabetically
        """
        # Given
        arr = ["banana", "apple", "cherry", "date"]

        # When
        result = self.sorting.sort_stable(arr, compare_fn=lambda a, b: (a > b) - (a < b))

        # Then
        assert result == ["apple", "banana", "cherry", "date"]

    def test_sort_stable_empty_array(self):
        """
        Given an empty array
        When sorting
        Then returns empty array
        """
        # Given
        arr = []

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result == []

    def test_sort_stable_single_element(self):
        """
        Given an array with one element
        When sorting
        Then returns same array
        """
        # Given
        arr = [42]

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result == [42]

    def test_sort_stable_already_sorted(self):
        """
        Given an already sorted array
        When sorting
        Then maintains order
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_sort_stable_reverse_order(self):
        """
        Given an array in reverse order
        When sorting
        Then sorts correctly
        """
        # Given
        arr = [5, 4, 3, 2, 1]

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_sort_stable_mutates_array(self):
        """
        Given an array
        When sorting
        Then mutates array in place
        """
        # Given
        arr = [3, 1, 2]

        # When
        result = self.sorting.sort_stable(arr)

        # Then
        assert result is arr  # Same reference
        assert arr == [1, 2, 3]

    def test_sort_stable_complexity(self):
        """
        Given a large array
        When sorting
        Then completes in O(n log n) time
        """
        # Given
        import time
        arr = list(range(10000, 0, -1))  # Reverse sorted

        # When
        start = time.time()
        result = self.sorting.sort_stable(arr)
        elapsed = time.time() - start

        # Then
        assert result == list(range(1, 10001))
        # O(n log n) for 10000 elements should be <0.1s
        assert elapsed < 0.1

    def test_sort_stable_custom_compare_descending(self):
        """
        Given an array
        When sorting with custom descending compare
        Then sorts in descending order
        """
        # Given
        arr = [1, 5, 3, 2, 4]

        # When
        result = self.sorting.sort_stable(arr, compare_fn=lambda a, b: b - a)

        # Then
        assert result == [5, 4, 3, 2, 1]

    def test_sort_stable_preserves_stability_with_complex_objects(self):
        """
        Given an array of complex objects
        When sorting by one property
        Then other properties maintain original order
        """
        # Given
        arr = [
            {"name": "Alice", "age": 30, "id": 1},
            {"name": "Bob", "age": 25, "id": 2},
            {"name": "Charlie", "age": 30, "id": 3},
            {"name": "David", "age": 25, "id": 4},
        ]

        # When - sort by age only
        result = self.sorting.sort_stable(
            arr, compare_fn=lambda a, b: a["age"] - b["age"]
        )

        # Then - for same age, original order preserved
        # age=25: Bob (id=2) before David (id=4)
        assert result[0]["id"] == 2
        assert result[1]["id"] == 4
        # age=30: Alice (id=1) before Charlie (id=3)
        assert result[2]["id"] == 1
        assert result[3]["id"] == 3
