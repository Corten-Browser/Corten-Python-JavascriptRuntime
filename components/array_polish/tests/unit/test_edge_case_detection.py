"""
Unit tests for edge case detection - ES2024 Wave D

Requirement: FR-ES24-D-010, FR-ES24-D-014
Tests comprehensive edge case detection for arrays
"""

import pytest
import math
from components.array_polish.src.edge_cases import ArrayEdgeCases


class TestEdgeCaseDetection:
    """Test edge case detection for arrays"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()

    # FR-ES24-D-010: Empty array
    def test_detect_edge_cases_empty_array(self):
        """Empty array detection"""
        info = self.ec.detect_edge_cases([])
        assert info['is_empty'] is True
        assert info['is_sparse'] is False
        assert info['has_negative_zero'] is False
        assert info['has_nan'] is False
        assert info['has_infinity'] is False
        assert info['has_undefined'] is False

    # FR-ES24-D-010: Dense array with normal values
    def test_detect_edge_cases_normal_array(self):
        """Dense array with normal values"""
        info = self.ec.detect_edge_cases([1, 2, 3])
        assert info['is_empty'] is False
        assert info['is_sparse'] is False
        assert info['has_negative_zero'] is False
        assert info['has_nan'] is False
        assert info['has_infinity'] is False
        assert info['has_undefined'] is False

    # FR-ES24-D-010: Sparse array
    def test_detect_edge_cases_sparse_array(self):
        """Sparse array detection"""
        info = self.ec.detect_edge_cases([1, None, 3], is_sparse=True)
        assert info['is_empty'] is False
        assert info['is_sparse'] is True
        assert info['has_negative_zero'] is False
        assert info['has_nan'] is False
        assert info['has_infinity'] is False
        assert info['has_undefined'] is False

    # FR-ES24-D-014: Special value detection - NaN
    def test_detect_edge_cases_with_nan(self):
        """Array containing NaN"""
        info = self.ec.detect_edge_cases([1, float('nan'), 3])
        assert info['is_empty'] is False
        assert info['is_sparse'] is False
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is False
        assert info['has_infinity'] is False

    # FR-ES24-D-014: Special value detection - negative zero
    def test_detect_edge_cases_with_negative_zero(self):
        """Array containing -0"""
        info = self.ec.detect_edge_cases([1, -0.0, 3])
        assert info['is_empty'] is False
        assert info['has_negative_zero'] is True
        assert info['has_nan'] is False
        assert info['has_infinity'] is False

    # FR-ES24-D-014: Special value detection - Infinity
    def test_detect_edge_cases_with_infinity(self):
        """Array containing Infinity"""
        info = self.ec.detect_edge_cases([1, float('inf'), 3])
        assert info['is_empty'] is False
        assert info['has_infinity'] is True
        assert info['has_nan'] is False
        assert info['has_negative_zero'] is False

    def test_detect_edge_cases_with_negative_infinity(self):
        """Array containing -Infinity"""
        info = self.ec.detect_edge_cases([1, float('-inf'), 3])
        assert info['is_empty'] is False
        assert info['has_infinity'] is True

    # FR-ES24-D-014: Explicit undefined (None)
    def test_detect_edge_cases_with_explicit_undefined(self):
        """Array with explicit undefined (not sparse)"""
        info = self.ec.detect_edge_cases([1, None, 3], is_sparse=False)
        assert info['is_empty'] is False
        assert info['is_sparse'] is False
        assert info['has_undefined'] is True

    # FR-ES24-D-014: All special values
    def test_detect_edge_cases_all_special_values(self):
        """Array with all special values"""
        info = self.ec.detect_edge_cases([
            1,
            float('nan'),
            -0.0,
            float('inf'),
            None
        ])
        assert info['is_empty'] is False
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True
        assert info['has_undefined'] is True

    # FR-ES24-D-014: Multiple occurrences
    def test_detect_edge_cases_multiple_nans(self):
        """Multiple NaN values still detected"""
        info = self.ec.detect_edge_cases([float('nan'), 1, float('nan'), 2])
        assert info['has_nan'] is True

    def test_detect_edge_cases_multiple_negative_zeros(self):
        """Multiple -0 values detected"""
        info = self.ec.detect_edge_cases([-0.0, 1, -0.0, 2])
        assert info['has_negative_zero'] is True

    # FR-ES24-D-010: Sparse array with special values
    def test_detect_edge_cases_sparse_with_special_values(self):
        """Sparse array with special values"""
        info = self.ec.detect_edge_cases(
            [float('nan'), None, -0.0, None, float('inf')],
            is_sparse=True
        )
        assert info['is_sparse'] is True
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True

    # FR-ES24-D-014: Edge case combinations
    def test_detect_edge_cases_only_special_values(self):
        """Array with only special values"""
        info = self.ec.detect_edge_cases([
            float('nan'),
            -0.0,
            float('inf'),
            float('-inf')
        ])
        assert info['is_empty'] is False
        assert info['has_nan'] is True
        assert info['has_negative_zero'] is True
        assert info['has_infinity'] is True

    def test_detect_edge_cases_single_element_special(self):
        """Single element array with special value"""
        info = self.ec.detect_edge_cases([float('nan')])
        assert info['is_empty'] is False
        assert info['has_nan'] is True

    # FR-ES24-D-014: Normal zero vs negative zero
    def test_detect_edge_cases_positive_zero_not_flagged(self):
        """Positive zero is not flagged as negative zero"""
        info = self.ec.detect_edge_cases([0.0, 1, 2])
        assert info['has_negative_zero'] is False

    def test_detect_edge_cases_mixed_zeros(self):
        """Mix of positive and negative zeros"""
        info = self.ec.detect_edge_cases([0.0, -0.0, 1])
        assert info['has_negative_zero'] is True

    # Error handling
    def test_detect_edge_cases_invalid_array(self):
        """Non-array input raises TypeError"""
        with pytest.raises(TypeError, match="Argument must be an array"):
            self.ec.detect_edge_cases("not an array")

    # FR-ES24-D-014: Large arrays
    def test_detect_edge_cases_large_array_normal(self):
        """Large array with normal values"""
        info = self.ec.detect_edge_cases(list(range(10000)))
        assert info['is_empty'] is False
        assert info['is_sparse'] is False
        assert info['has_nan'] is False

    def test_detect_edge_cases_large_array_with_one_special(self):
        """Large array with one special value"""
        arr = list(range(10000))
        arr[5000] = float('nan')
        info = self.ec.detect_edge_cases(arr)
        assert info['has_nan'] is True
