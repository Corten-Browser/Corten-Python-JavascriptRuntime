"""
Integration tests for array_polish component - ES2024 Wave D

Tests complete workflows combining multiple edge case handling features
"""

import pytest
import math
from components.array_polish.src.edge_cases import ArrayEdgeCases
from components.array_polish.src.typed_array import TypedArrayHandler
from components.array_polish.src.sparse_handling import SparseArrayHandler


class TestArrayPolishIntegration:
    """Integration tests combining multiple array edge case features"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()
        self.ta = TypedArrayHandler()
        self.sparse = SparseArrayHandler()

    # Integration: Detect edge cases + handle sparse + find_last
    def test_complete_sparse_array_workflow(self):
        """Complete workflow: detect, handle, search sparse array"""
        # Step 1: Create sparse array with special values
        sparse_array = [1, float('nan'), None, -0.0, None, float('inf'), 3]

        # Step 2: Detect edge cases
        info = self.ec.detect_edge_cases(sparse_array, is_sparse=True)
        assert info['is_sparse'] is True
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True

        # Step 3: Handle sparse array (remove holes)
        result = self.ec.handle_sparse(sparse_array, mode='remove_holes', is_sparse=True)
        normalized = result['normalized_array']
        assert len(normalized) == 5  # Original 7 - 2 holes
        assert result['holes_removed'] is True
        assert result['original_holes'] == [2, 4]

        # Step 4: Find last finite value
        last_finite = self.ec.find_last(
            normalized,
            lambda x, i, a: isinstance(x, (int, float)) and math.isfinite(x) and x > 0
        )
        assert last_finite['found'] is True
        assert last_finite['value'] == 3

    # Integration: TypedArray + at() + edge case detection
    def test_typed_array_complete_workflow(self):
        """Complete TypedArray workflow with boundary values"""
        # Step 1: Create TypedArray with boundary values
        elements = [-128, 0, 127]
        typed_arr = self.ta.create_typed_array('Int8Array', elements)

        # Step 2: Validate boundaries
        validation = self.ta.validate_typed_array('Int8Array', elements)
        assert validation['valid'] is True
        assert validation['min_value'] == -128
        assert validation['max_value'] == 127

        # Step 3: Access elements with at()
        min_val = self.ta.at(typed_arr, 0)
        assert min_val['value'] == -128
        assert min_val['is_undefined'] is False

        max_val = self.ta.at(typed_arr, -1)
        assert max_val['value'] == 127

        # Step 4: Detect edge cases
        edge_info = self.ta.detect_edge_cases(typed_arr)
        assert edge_info['is_sparse'] is False  # TypedArrays always dense
        assert edge_info['is_empty'] is False

    # Integration: Complex predicate with sparse arrays
    def test_complex_predicate_workflow(self):
        """Complex predicate with multiple array operations"""
        # Array with duplicates and holes
        array = [1, 2, None, 3, 2, None, 1, 2]

        # Find last occurrence of 2, skipping holes
        result = self.ec.find_last_index(
            array,
            lambda x, i, a: x == 2,
            is_sparse=True
        )
        assert result['found'] is True
        assert result['index'] == 7  # Last occurrence

        # Find holes
        holes = self.sparse.find_holes(array, is_sparse=True)
        assert holes == [2, 5]

        # Compact array
        compacted = self.sparse.compact_array(array, holes)
        assert compacted == [1, 2, 3, 2, 1, 2]
        assert len(compacted) == 6

    # Integration: Multiple edge case types
    def test_multiple_special_values_workflow(self):
        """Workflow with all special value types"""
        # Create array with all special values
        special_array = [
            1,
            float('nan'),
            -0.0,
            float('inf'),
            float('-inf'),
            None,
            2
        ]

        # Detect all edge cases
        info = self.ec.detect_edge_cases(special_array, is_sparse=False)
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True
        assert info['has_undefined'] is True

        # Find last finite positive number
        result = self.ec.find_last(
            special_array,
            lambda x, i, a: (
                isinstance(x, (int, float)) and
                not math.isnan(x) and
                math.isfinite(x) and
                x > 0
            )
        )
        assert result['found'] is True
        assert result['value'] == 2

        # Access boundary elements
        first = self.ec.at(special_array, 0)
        assert first['value'] == 1

        last = self.ec.at(special_array, -1)
        assert last['value'] == 2

    # Integration: TypedArray with offset and search
    def test_typed_array_offset_search_workflow(self):
        """TypedArray with offset, then search"""
        # Create TypedArray with offset
        elements = [1, 2, 3, 4, 5, 6]
        typed_arr = self.ta.create_typed_array(
            'Int32Array',
            elements,
            byte_offset=8,  # Skip first 2 elements (4 bytes each)
            length=3
        )

        # Should have elements [3, 4, 5]
        assert typed_arr['length'] == 3
        assert typed_arr['elements'] == [3, 4, 5]

        # Find last even number
        result = self.ta.find_last(
            typed_arr,
            lambda x, i, a: x % 2 == 0
        )
        assert result['found'] is True
        assert result['value'] == 4

        # Access with negative index
        last_elem = self.ta.at(typed_arr, -1)
        assert last_elem['value'] == 5

    # Integration: Empty array edge cases across all methods
    def test_empty_array_complete_coverage(self):
        """Test all methods with empty array"""
        empty = []

        # Edge case detection
        info = self.ec.detect_edge_cases(empty)
        assert info['is_empty'] is True
        assert info['has_nan'] is False

        # at() on empty
        result = self.ec.at(empty, 0)
        assert result['is_undefined'] is True

        # find_last on empty
        result = self.ec.find_last(empty, lambda x, i, a: True)
        assert result['found'] is False

        # find_last_index on empty
        result = self.ec.find_last_index(empty, lambda x, i, a: True)
        assert result['index'] == -1
        assert result['found'] is False

        # handle_sparse on empty
        result = self.ec.handle_sparse(empty, mode='remove_holes')
        assert result['normalized_array'] == []
        assert result['holes_removed'] is False

    # Integration: Performance test with large arrays
    def test_large_array_performance(self):
        """Test performance with large arrays (<10ms for 10K elements)"""
        import time

        # Create large array
        large_array = list(range(10000))

        # Test at() - should be O(1), very fast
        start = time.time()
        result = self.ec.at(large_array, -1)
        elapsed = time.time() - start
        assert result['value'] == 9999
        assert elapsed < 0.01  # <10ms (extremely fast for O(1))

        # Test detect_edge_cases - should be O(n) but still fast
        start = time.time()
        info = self.ec.detect_edge_cases(large_array)
        elapsed = time.time() - start
        assert info['is_empty'] is False
        assert elapsed < 0.01  # <10ms for 10K elements

        # Test find_last - O(n) linear search
        start = time.time()
        result = self.ec.find_last(large_array, lambda x, i, a: x == 9999)
        elapsed = time.time() - start
        assert result['found'] is True
        assert result['value'] == 9999
        assert elapsed < 0.01  # <10ms for 10K elements

    # Integration: Sparse array with explicit undefined vs holes
    def test_sparse_vs_explicit_undefined_workflow(self):
        """Distinguish sparse holes from explicit undefined"""
        # Array: [1, <hole>, 3, undefined]
        array = [1, None, 3, None]

        # Scenario 1: Treat all None as holes
        result = self.ec.handle_sparse(
            array,
            mode='remove_holes',
            is_sparse=True
        )
        assert result['normalized_array'] == [1, 3]

        # Scenario 2: Specific holes only
        result = self.ec.handle_sparse(
            array,
            mode='remove_holes',
            is_sparse=True,
            holes=[1]  # Only index 1 is a hole
        )
        assert result['normalized_array'] == [1, 3, None]  # Keep explicit undefined at index 3

    # Integration: Float TypedArray special values
    def test_float_typed_array_special_values(self):
        """Float TypedArray with all special values"""
        elements = [1.5, float('nan'), -0.0, float('inf'), float('-inf'), 2.5]

        # Validate
        validation = self.ta.validate_typed_array('Float32Array', elements)
        assert validation['valid'] is True
        assert validation['has_nan'] is True
        assert validation['has_negative_zero'] is True
        assert validation['has_infinity'] is True

        # Create TypedArray
        typed_arr = self.ta.create_typed_array('Float32Array', elements)

        # Detect edge cases
        info = self.ta.detect_edge_cases(typed_arr)
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True

        # Find last finite value
        result = self.ta.find_last(
            typed_arr,
            lambda x, i, a: isinstance(x, (int, float)) and math.isfinite(x) and x > 0
        )
        assert result['found'] is True
        assert result['value'] == 2.5
