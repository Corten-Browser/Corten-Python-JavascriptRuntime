"""
Unit tests for Array.prototype.at() edge cases - ES2024 Wave D

Requirement: FR-ES24-D-012
Tests comprehensive edge case handling for array indexing with at()
"""

import pytest
import math
from components.array_polish.src.edge_cases import ArrayEdgeCases


class TestArrayAt:
    """Test Array.prototype.at() edge cases"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()

    # FR-ES24-D-012: Empty array edge cases
    def test_at_empty_array_positive_index(self):
        """Empty array with positive index returns undefined"""
        result = self.ec.at([], 0)
        assert result['is_undefined'] is True
        assert result.get('value') is None

    def test_at_empty_array_negative_index(self):
        """Empty array with negative index returns undefined"""
        result = self.ec.at([], -1)
        assert result['is_undefined'] is True

    # FR-ES24-D-012: Negative index handling
    def test_at_negative_index_within_bounds(self):
        """Negative index within bounds accesses from end"""
        result = self.ec.at([1, 2, 3], -1)
        assert result['is_undefined'] is False
        assert result['value'] == 3

    def test_at_negative_index_first_element(self):
        """Negative index -length accesses first element"""
        result = self.ec.at([1, 2, 3], -3)
        assert result['is_undefined'] is False
        assert result['value'] == 1

    def test_at_negative_index_out_of_bounds(self):
        """Negative index out of bounds returns undefined"""
        result = self.ec.at([1, 2, 3], -5)
        assert result['is_undefined'] is True

    # FR-ES24-D-012: Positive index edge cases
    def test_at_positive_index_first(self):
        """Index 0 accesses first element"""
        result = self.ec.at([42], 0)
        assert result['is_undefined'] is False
        assert result['value'] == 42

    def test_at_positive_index_last(self):
        """Index length-1 accesses last element"""
        result = self.ec.at([1, 2, 3], 2)
        assert result['is_undefined'] is False
        assert result['value'] == 3

    def test_at_positive_index_out_of_bounds(self):
        """Positive index >= length returns undefined"""
        result = self.ec.at([1, 2, 3], 5)
        assert result['is_undefined'] is True

    # FR-ES24-D-010: Sparse array handling
    def test_at_sparse_array_hole(self):
        """Accessing hole in sparse array returns undefined"""
        # Sparse array represented with None as hole marker
        result = self.ec.at([1, None, 3], 1, is_sparse=True)
        assert result['is_undefined'] is True

    def test_at_sparse_array_valid_element(self):
        """Accessing valid element in sparse array works"""
        result = self.ec.at([1, None, 3], 2, is_sparse=True)
        assert result['is_undefined'] is False
        assert result['value'] == 3

    # FR-ES24-D-012: Special values
    def test_at_array_with_nan(self):
        """Array containing NaN can be accessed"""
        result = self.ec.at([1, float('nan'), 3], 1)
        assert result['is_undefined'] is False
        assert math.isnan(result['value'])

    def test_at_array_with_negative_zero(self):
        """Array containing -0 can be accessed"""
        result = self.ec.at([1, -0.0, 3], 1)
        assert result['is_undefined'] is False
        assert result['value'] == 0
        assert math.copysign(1, result['value']) == -1  # Verify it's -0

    def test_at_array_with_infinity(self):
        """Array containing Infinity can be accessed"""
        result = self.ec.at([1, float('inf'), 3], 1)
        assert result['is_undefined'] is False
        assert math.isinf(result['value'])
        assert result['value'] > 0

    def test_at_array_with_negative_infinity(self):
        """Array containing -Infinity can be accessed"""
        result = self.ec.at([1, float('-inf'), 3], 1)
        assert result['is_undefined'] is False
        assert math.isinf(result['value'])
        assert result['value'] < 0

    def test_at_array_with_explicit_undefined(self):
        """Array with explicit undefined (None in Python)"""
        result = self.ec.at([1, None, 3], 1, is_sparse=False)
        assert result['is_undefined'] is False
        assert result['value'] is None

    # FR-ES24-D-012: Boundary conditions
    def test_at_single_element_array(self):
        """Single element array edge cases"""
        result = self.ec.at([42], 0)
        assert result['value'] == 42
        result = self.ec.at([42], -1)
        assert result['value'] == 42
        result = self.ec.at([42], 1)
        assert result['is_undefined'] is True

    def test_at_large_negative_index(self):
        """Very large negative index returns undefined"""
        result = self.ec.at([1, 2, 3], -1000)
        assert result['is_undefined'] is True

    def test_at_large_positive_index(self):
        """Very large positive index returns undefined"""
        result = self.ec.at([1, 2, 3], 1000)
        assert result['is_undefined'] is True

    # Error handling
    def test_at_invalid_array_type(self):
        """Non-array input raises TypeError"""
        with pytest.raises(TypeError, match="First argument must be an array"):
            self.ec.at("not an array", 0)

    def test_at_non_integer_index(self):
        """Non-integer index raises TypeError"""
        with pytest.raises(TypeError, match="Index must be an integer"):
            self.ec.at([1, 2, 3], 1.5)

    def test_at_index_as_string(self):
        """String index raises TypeError"""
        with pytest.raises(TypeError, match="Index must be an integer"):
            self.ec.at([1, 2, 3], "0")
