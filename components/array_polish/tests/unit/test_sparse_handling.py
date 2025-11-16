"""
Unit tests for sparse array handling - ES2024 Wave D

Requirement: FR-ES24-D-010, FR-ES24-D-014
Tests comprehensive sparse array edge case handling
"""

import pytest
from components.array_polish.src.edge_cases import ArrayEdgeCases


class TestSparseArrayHandling:
    """Test sparse array handling with multiple modes"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()

    # FR-ES24-D-010: Empty array
    def test_handle_sparse_empty_array(self):
        """Empty array - no holes to handle"""
        result = self.ec.handle_sparse([], mode='remove_holes')
        assert result['normalized_array'] == []
        assert result['holes_removed'] is False
        assert result['original_holes'] == []

    # FR-ES24-D-010: Dense array (no holes)
    def test_handle_sparse_dense_array(self):
        """Dense array - no holes to remove"""
        result = self.ec.handle_sparse([1, 2, 3], mode='remove_holes')
        assert result['normalized_array'] == [1, 2, 3]
        assert result['holes_removed'] is False
        assert result['original_holes'] == []

    # FR-ES24-D-010: Sparse array - remove holes mode
    def test_handle_sparse_remove_holes(self):
        """Sparse array - remove holes compacts array"""
        result = self.ec.handle_sparse([1, None, 3, None, 5], mode='remove_holes', is_sparse=True)
        assert result['normalized_array'] == [1, 3, 5]
        assert result['holes_removed'] is True
        assert result['original_holes'] == [1, 3]

    def test_handle_sparse_remove_holes_beginning(self):
        """Hole at beginning of array"""
        result = self.ec.handle_sparse([None, 2, 3], mode='remove_holes', is_sparse=True)
        assert result['normalized_array'] == [2, 3]
        assert result['holes_removed'] is True
        assert result['original_holes'] == [0]

    def test_handle_sparse_remove_holes_end(self):
        """Hole at end of array"""
        result = self.ec.handle_sparse([1, 2, None], mode='remove_holes', is_sparse=True)
        assert result['normalized_array'] == [1, 2]
        assert result['holes_removed'] is True
        assert result['original_holes'] == [2]

    def test_handle_sparse_all_holes(self):
        """Array with all holes becomes empty"""
        result = self.ec.handle_sparse([None, None, None], mode='remove_holes', is_sparse=True)
        assert result['normalized_array'] == []
        assert result['holes_removed'] is True
        assert result['original_holes'] == [0, 1, 2]

    # FR-ES24-D-010: Sparse array - preserve holes mode
    def test_handle_sparse_preserve_holes(self):
        """Preserve holes mode keeps holes as-is"""
        result = self.ec.handle_sparse([1, None, 3], mode='preserve_holes', is_sparse=True)
        assert result['normalized_array'] == [1, None, 3]
        assert result['holes_removed'] is False
        assert result['original_holes'] == [1]

    def test_handle_sparse_preserve_holes_dense_array(self):
        """Preserve holes on dense array is no-op"""
        result = self.ec.handle_sparse([1, 2, 3], mode='preserve_holes')
        assert result['normalized_array'] == [1, 2, 3]
        assert result['holes_removed'] is False
        assert result['original_holes'] == []

    # FR-ES24-D-010: Sparse array - explicit undefined mode
    def test_handle_sparse_explicit_undefined(self):
        """Explicit undefined mode converts holes to undefined"""
        result = self.ec.handle_sparse([1, None, 3], mode='explicit_undefined', is_sparse=True)
        # Holes become explicit undefined (None in Python)
        assert len(result['normalized_array']) == 3
        assert result['normalized_array'][0] == 1
        assert result['normalized_array'][1] is None  # Explicit undefined
        assert result['normalized_array'][2] == 3
        assert result['holes_removed'] is True
        assert result['original_holes'] == [1]

    def test_handle_sparse_explicit_undefined_all_holes(self):
        """All holes become explicit undefined"""
        result = self.ec.handle_sparse([None, None, None], mode='explicit_undefined', is_sparse=True)
        assert len(result['normalized_array']) == 3
        assert all(x is None for x in result['normalized_array'])
        assert result['holes_removed'] is True
        assert result['original_holes'] == [0, 1, 2]

    # FR-ES24-D-010: Sparse array with explicit undefined vs holes
    def test_handle_sparse_explicit_undefined_vs_hole(self):
        """Distinguish explicit undefined from hole"""
        # In sparse array: [1, <hole>, 3, undefined]
        # We'll use a dict to mark which are holes
        arr = [1, None, 3, None]
        result = self.ec.handle_sparse(arr, mode='remove_holes', is_sparse=True, holes=[1])
        # Should remove index 1 (hole), keep index 3 (explicit undefined)
        assert result['normalized_array'] == [1, 3, None]
        assert result['original_holes'] == [1]

    # FR-ES24-D-010: Mixed values
    def test_handle_sparse_with_special_values(self):
        """Sparse array with special values"""
        result = self.ec.handle_sparse(
            [1, float('nan'), None, float('-0'), None, float('inf')],
            mode='remove_holes',
            is_sparse=True
        )
        assert len(result['normalized_array']) == 4
        assert result['holes_removed'] is True
        assert result['original_holes'] == [2, 4]

    # FR-ES24-D-014: Consecutive holes
    def test_handle_sparse_consecutive_holes(self):
        """Multiple consecutive holes"""
        result = self.ec.handle_sparse(
            [1, None, None, None, 5],
            mode='remove_holes',
            is_sparse=True
        )
        assert result['normalized_array'] == [1, 5]
        assert result['original_holes'] == [1, 2, 3]

    # Error handling
    def test_handle_sparse_invalid_array(self):
        """Non-array input raises TypeError"""
        with pytest.raises(TypeError, match="First argument must be an array"):
            self.ec.handle_sparse("not an array")

    def test_handle_sparse_invalid_mode_type(self):
        """Non-string mode raises TypeError"""
        with pytest.raises(TypeError, match="Mode must be a string"):
            self.ec.handle_sparse([1, 2, 3], mode=123)

    def test_handle_sparse_invalid_mode_value(self):
        """Invalid mode value raises RangeError"""
        with pytest.raises(ValueError, match="Mode must be one of"):
            self.ec.handle_sparse([1, 2, 3], mode='invalid_mode')

    # FR-ES24-D-014: Performance edge case
    def test_handle_sparse_large_sparse_array(self):
        """Large sparse array with many holes"""
        # Create array with holes at even indices
        arr = [i if i % 2 == 0 else None for i in range(1000)]
        result = self.ec.handle_sparse(arr, mode='remove_holes', is_sparse=True)
        assert len(result['normalized_array']) == 500
        assert result['holes_removed'] is True
        assert len(result['original_holes']) == 500
