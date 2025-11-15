"""
Unit tests for TypedArrayExtensions (ES2024)
Requirements: FR-ES24-007, FR-ES24-008
"""

import pytest
from unittest.mock import Mock


class TestTypedArrayExtensions:
    """Test TypedArray.prototype extensions (toReversed, toSorted)"""

    def test_to_reversed_basic(self):
        """FR-ES24-007: Basic toReversed operation"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [1, 2, 3, 4, 5]
        array.length = 5

        reversed_array = ext.to_reversed(array)

        assert reversed_array is not None
        assert reversed_array is not array  # New instance

    def test_to_reversed_original_unchanged(self):
        """FR-ES24-007: Original array should not be modified"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [1, 2, 3, 4, 5]
        array.length = 5
        original_values = array.values.copy()

        reversed_array = ext.to_reversed(array)

        assert array.values == original_values  # Original unchanged

    def test_to_reversed_empty_array(self):
        """FR-ES24-007: Reversing empty array"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = []
        array.length = 0

        reversed_array = ext.to_reversed(array)

        assert reversed_array is not None

    def test_to_reversed_single_element(self):
        """FR-ES24-007: Reversing single element array"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [42]
        array.length = 1

        reversed_array = ext.to_reversed(array)

        assert reversed_array is not None

    def test_to_sorted_basic(self):
        """FR-ES24-008: Basic toSorted operation"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [5, 2, 8, 1, 9]
        array.length = 5

        sorted_array = ext.to_sorted(array)

        assert sorted_array is not None
        assert sorted_array is not array  # New instance

    def test_to_sorted_original_unchanged(self):
        """FR-ES24-008: Original array should not be modified"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [5, 2, 8, 1, 9]
        array.length = 5
        original_values = array.values.copy()

        sorted_array = ext.to_sorted(array)

        assert array.values == original_values  # Original unchanged

    def test_to_sorted_with_compare_function(self):
        """FR-ES24-008: toSorted with custom compare function"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [5, 2, 8, 1, 9]
        array.length = 5

        def compare_fn(a, b):
            return b - a  # Descending

        sorted_array = ext.to_sorted(array, compare_fn=compare_fn)

        assert sorted_array is not None

    def test_to_sorted_empty_array(self):
        """FR-ES24-008: Sorting empty array"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = []
        array.length = 0

        sorted_array = ext.to_sorted(array)

        assert sorted_array is not None

    def test_to_sorted_already_sorted(self):
        """FR-ES24-008: Sorting already sorted array"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [1, 2, 3, 4, 5]
        array.length = 5

        sorted_array = ext.to_sorted(array)

        assert sorted_array is not None
