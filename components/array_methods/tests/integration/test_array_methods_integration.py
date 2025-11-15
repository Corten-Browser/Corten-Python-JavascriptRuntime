"""
Integration tests for array_methods component.

Tests comprehensive workflows and interactions between array methods.
"""

import pytest
from components.array_methods.src.array_methods import ArrayMethods
from components.array_methods.src.array_constructor import ArrayConstructorMethods
from components.array_methods.src.array_sorting import ArraySorting


class TestArrayMethodsIntegration:
    """Integration tests for array methods working together."""

    def setup_method(self):
        """Set up test fixtures."""
        self.methods = ArrayMethods()
        self.constructor = ArrayConstructorMethods()
        self.sorting = ArraySorting()

    def test_chain_flat_and_includes(self):
        """
        Given a nested array
        When flattening and checking includes
        Then operations work together correctly
        """
        # Given
        arr = [[1, 2], [3, 4], [5, 6]]

        # When
        flattened = self.methods.flat(arr)
        has_four = self.methods.includes(flattened, 4)

        # Then
        assert flattened == [1, 2, 3, 4, 5, 6]
        assert has_four is True

    def test_from_iterable_then_sort(self):
        """
        Given a generator
        When creating array and sorting
        Then operations chain correctly
        """
        # Given
        def gen():
            yield 5
            yield 2
            yield 8
            yield 1

        # When
        arr = self.constructor.from_iterable(gen())
        sorted_arr = self.sorting.sort_stable(arr)

        # Then
        assert sorted_arr == [1, 2, 5, 8]

    def test_array_of_then_fill(self):
        """
        Given Array.of() creation
        When filling array
        Then mutations work correctly
        """
        # Given
        arr = self.constructor.of(1, 2, 3, 4, 5)

        # When
        filled = self.methods.fill(arr, value=0, start=2, end=4)

        # Then
        assert filled == [1, 2, 0, 0, 5]
        assert filled is arr  # Mutated in place

    def test_flat_map_then_sort(self):
        """
        Given an array
        When flat mapping and sorting
        Then operations chain correctly
        """
        # Given
        arr = [3, 1, 2]

        # When
        flat_mapped = self.methods.flat_map(arr, lambda x: [x, x * 10])
        sorted_result = self.sorting.sort_stable(flat_mapped)

        # Then
        assert sorted_result == [1, 2, 3, 10, 20, 30]

    def test_copy_within_then_includes(self):
        """
        Given an array
        When using copyWithin and checking includes
        Then mutations and checks work together
        """
        # Given
        arr = [1, 2, 3, 4, 5]

        # When
        copied = self.methods.copy_within(arr, target=0, start=3, end=5)
        has_four = self.methods.includes(copied, 4)

        # Then
        assert copied == [4, 5, 3, 4, 5]
        assert has_four is True

    def test_from_with_map_then_flat(self):
        """
        Given an iterable with mapping
        When creating array and flattening
        Then operations combine correctly
        """
        # Given
        iterable = [1, 2, 3]

        # When
        arr = self.constructor.from_iterable(iterable, map_fn=lambda x: [x, x * 2])
        flattened = self.methods.flat(arr)

        # Then
        assert flattened == [1, 2, 2, 4, 3, 6]

    def test_at_with_sorted_array(self):
        """
        Given an unsorted array
        When sorting and accessing with at()
        Then can access sorted elements correctly
        """
        # Given
        arr = [5, 2, 8, 1, 9]

        # When
        sorted_arr = self.sorting.sort_stable(arr)
        first = self.methods.at(sorted_arr, 0)
        last = self.methods.at(sorted_arr, -1)

        # Then
        assert first == 1
        assert last == 9

    def test_complex_data_pipeline(self):
        """
        Given complex data processing pipeline
        When using multiple array methods
        Then all operations work together correctly
        """
        # Given
        data = [[1, 2], [3, 4], [5, 6]]

        # When - flatten, double values, sort, check
        step1 = self.methods.flat(data)
        step2 = self.constructor.from_iterable(step1, map_fn=lambda x: x * 2)
        step3 = self.sorting.sort_stable(step2)
        has_twelve = self.methods.includes(step3, 12)

        # Then
        assert step3 == [2, 4, 6, 8, 10, 12]
        assert has_twelve is True

    def test_fill_array_of_objects_then_access(self):
        """
        Given an array created with Array.of()
        When filling with objects and accessing
        Then object references work correctly
        """
        # Given
        obj = {"value": 42}
        arr = self.constructor.of(1, 2, 3, 4, 5)

        # When
        filled = self.methods.fill(arr, value=obj, start=1, end=4)
        accessed = self.methods.at(filled, 2)

        # Then
        assert accessed is obj
        assert accessed["value"] == 42

    def test_stable_sort_maintains_equality_order(self):
        """
        Given an array with equal elements from multiple sources
        When sorting with stable sort
        Then maintains insertion order for equals
        """
        # Given
        arr1 = self.constructor.of(
            {"val": 2, "src": "a"},
            {"val": 1, "src": "b"},
        )
        arr2 = self.constructor.of(
            {"val": 2, "src": "c"},
            {"val": 1, "src": "d"},
        )
        combined = arr1 + arr2

        # When
        sorted_arr = self.sorting.sort_stable(
            combined, compare_fn=lambda a, b: a["val"] - b["val"]
        )

        # Then - for val=1: b before d, for val=2: a before c
        assert sorted_arr[0]["src"] == "b"
        assert sorted_arr[1]["src"] == "d"
        assert sorted_arr[2]["src"] == "a"
        assert sorted_arr[3]["src"] == "c"

    def test_array_is_array_with_constructor_methods(self):
        """
        Given arrays created with different constructors
        When checking with isArray
        Then all are identified as arrays
        """
        # Given
        arr1 = self.constructor.of(1, 2, 3)
        arr2 = self.constructor.from_iterable([4, 5, 6])
        arr3 = [7, 8, 9]

        # When/Then
        assert self.constructor.is_array(arr1) is True
        assert self.constructor.is_array(arr2) is True
        assert self.constructor.is_array(arr3) is True
        assert self.constructor.is_array("not array") is False

    def test_deeply_nested_flat_with_includes(self):
        """
        Given deeply nested array
        When flattening completely and searching
        Then finds elements at any depth
        """
        # Given
        arr = [1, [2, [3, [4, [5]]]]]

        # When
        flattened = self.methods.flat(arr, depth=float('inf'))
        has_five = self.methods.includes(flattened, 5)

        # Then
        assert flattened == [1, 2, 3, 4, 5]
        assert has_five is True

    def test_performance_large_dataset(self):
        """
        Given large dataset
        When processing with multiple methods
        Then completes in reasonable time
        """
        # Given
        import time
        large_array = list(range(10000))

        # When
        start = time.time()
        arr = self.constructor.from_iterable(large_array, map_fn=lambda x: x * 2)
        sorted_arr = self.sorting.sort_stable(arr)
        has_element = self.methods.includes(sorted_arr, 10000)
        last = self.methods.at(sorted_arr, -1)
        elapsed = time.time() - start

        # Then
        assert len(sorted_arr) == 10000
        assert has_element is True
        assert last == 19998
        assert elapsed < 0.5  # Should be fast

    def test_all_methods_coexist(self):
        """
        Verify all methods are accessible and can be used together.
        """
        # Given
        arr = [3, 1, 4, 1, 5, 9, 2, 6]

        # When - use every method at least once
        sorted_arr = self.sorting.sort_stable(arr[:])
        flattened = self.methods.flat([[1, 2], [3, 4]])
        flat_mapped = self.methods.flat_map([1, 2], lambda x: [x, x * 2])
        has_five = self.methods.includes(arr, 5)
        filled = self.methods.fill([0] * 5, value=1, start=0, end=3)
        copied = self.methods.copy_within([1, 2, 3, 4, 5], target=0, start=3)
        at_val = self.methods.at(arr, -1)
        from_arr = self.constructor.from_iterable(range(3))
        of_arr = self.constructor.of(7, 8, 9)
        is_arr = self.constructor.is_array(arr)

        # Then - all operations successful
        assert sorted_arr == [1, 1, 2, 3, 4, 5, 6, 9]
        assert flattened == [1, 2, 3, 4]
        assert flat_mapped == [1, 2, 2, 4]
        assert has_five is True
        assert filled == [1, 1, 1, 0, 0]
        assert copied == [4, 5, 3, 4, 5]
        assert at_val == 6
        assert from_arr == [0, 1, 2]
        assert of_arr == [7, 8, 9]
        assert is_arr is True
