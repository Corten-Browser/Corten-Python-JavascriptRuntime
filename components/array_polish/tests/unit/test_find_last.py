"""
Unit tests for Array.prototype.findLast() and findLastIndex() - ES2024 Wave D

Requirement: FR-ES24-D-013
Tests comprehensive edge case handling for reverse array searching
"""

import pytest
import math
from components.array_polish.src.edge_cases import ArrayEdgeCases


class TestFindLast:
    """Test Array.prototype.findLast() edge cases"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()

    # FR-ES24-D-013: Empty array
    def test_find_last_empty_array(self):
        """Empty array returns undefined"""
        result = self.ec.find_last([], lambda x, i, a: True)
        assert result['found'] is False
        assert result.get('value') is None

    # FR-ES24-D-013: No matching element
    def test_find_last_no_match(self):
        """No matching element returns undefined"""
        result = self.ec.find_last([1, 2, 3], lambda x, i, a: x < 0)
        assert result['found'] is False

    # FR-ES24-D-013: Single matching element
    def test_find_last_single_match(self):
        """Single matching element is found"""
        result = self.ec.find_last([1, 2, 3], lambda x, i, a: x == 2)
        assert result['found'] is True
        assert result['value'] == 2

    # FR-ES24-D-013: Multiple matches - returns last
    def test_find_last_multiple_matches(self):
        """Multiple matches returns last occurrence"""
        result = self.ec.find_last([1, 2, 3, 2, 1], lambda x, i, a: x == 2)
        assert result['found'] is True
        assert result['value'] == 2
        # Should be the element at index 3, not index 1

    def test_find_last_all_match(self):
        """All elements match - returns last"""
        result = self.ec.find_last([1, 1, 1], lambda x, i, a: x == 1)
        assert result['found'] is True
        assert result['value'] == 1

    # FR-ES24-D-010: Sparse array handling
    def test_find_last_sparse_array_skip_holes(self):
        """Sparse array skips holes"""
        # [1, <hole>, 3] - hole should be skipped
        result = self.ec.find_last([1, None, 3], lambda x, i, a: True, is_sparse=True)
        assert result['found'] is True
        assert result['value'] == 3  # Last non-hole element

    def test_find_last_sparse_array_match_before_hole(self):
        """Match element before hole in sparse array"""
        result = self.ec.find_last([1, None, 3], lambda x, i, a: x == 1, is_sparse=True)
        assert result['found'] is True
        assert result['value'] == 1

    # FR-ES24-D-014: Special values
    def test_find_last_array_with_nan(self):
        """Find NaN in array"""
        result = self.ec.find_last(
            [1, float('nan'), 3, float('nan')],
            lambda x, i, a: math.isnan(x) if isinstance(x, float) else False
        )
        assert result['found'] is True
        assert math.isnan(result['value'])

    def test_find_last_array_with_negative_zero(self):
        """Find -0 in array"""
        result = self.ec.find_last(
            [1, -0.0, 3],
            lambda x, i, a: x == 0 and math.copysign(1, x) == -1
        )
        assert result['found'] is True
        assert result['value'] == 0

    def test_find_last_array_with_infinity(self):
        """Find finite numbers (excluding Infinity)"""
        result = self.ec.find_last(
            [float('nan'), -0.0, float('inf')],
            lambda x, i, a: isinstance(x, (int, float)) and math.isfinite(x)
        )
        assert result['found'] is True
        assert result['value'] == -0.0

    # FR-ES24-D-014: Predicate edge cases
    def test_find_last_predicate_always_true(self):
        """Predicate always returns true - gets last element"""
        result = self.ec.find_last([1, 2, 3], lambda x, i, a: True)
        assert result['found'] is True
        assert result['value'] == 3

    def test_find_last_predicate_always_false(self):
        """Predicate always returns false - not found"""
        result = self.ec.find_last([1, 2, 3], lambda x, i, a: False)
        assert result['found'] is False

    def test_find_last_predicate_uses_index(self):
        """Predicate uses index parameter"""
        result = self.ec.find_last([10, 20, 30], lambda x, i, a: i == 1)
        assert result['found'] is True
        assert result['value'] == 20

    def test_find_last_predicate_uses_array(self):
        """Predicate uses array parameter"""
        result = self.ec.find_last(
            [1, 2, 3],
            lambda x, i, a: x == len(a)  # Find element equal to array length
        )
        assert result['found'] is True
        assert result['value'] == 3

    # FR-ES24-D-013: Match at boundaries
    def test_find_last_match_at_index_0(self):
        """Match at first index"""
        result = self.ec.find_last([42, 1, 2], lambda x, i, a: x == 42)
        assert result['found'] is True
        assert result['value'] == 42

    def test_find_last_match_at_last_index(self):
        """Match at last index"""
        result = self.ec.find_last([1, 2, 42], lambda x, i, a: x == 42)
        assert result['found'] is True
        assert result['value'] == 42

    # Error handling
    def test_find_last_invalid_array(self):
        """Non-array input raises TypeError"""
        with pytest.raises(TypeError, match="First argument must be an array"):
            self.ec.find_last("not an array", lambda x, i, a: True)

    def test_find_last_non_callable_predicate(self):
        """Non-callable predicate raises TypeError"""
        with pytest.raises(TypeError, match="Predicate must be a callable"):
            self.ec.find_last([1, 2, 3], "not callable")

    def test_find_last_predicate_throws_error(self):
        """Predicate throwing error is handled"""
        def bad_predicate(x, i, a):
            raise ValueError("Predicate error")

        with pytest.raises(Exception):  # Should propagate or wrap error
            self.ec.find_last([1, 2, 3], bad_predicate)


class TestFindLastIndex:
    """Test Array.prototype.findLastIndex() edge cases"""

    def setup_method(self):
        """Setup test fixtures"""
        self.ec = ArrayEdgeCases()

    # FR-ES24-D-013: Empty array
    def test_find_last_index_empty_array(self):
        """Empty array returns -1"""
        result = self.ec.find_last_index([], lambda x, i, a: True)
        assert result['found'] is False
        assert result['index'] == -1

    # FR-ES24-D-013: No matching element
    def test_find_last_index_no_match(self):
        """No matching element returns -1"""
        result = self.ec.find_last_index([1, 2, 3], lambda x, i, a: x < 0)
        assert result['found'] is False
        assert result['index'] == -1

    # FR-ES24-D-013: Single matching element
    def test_find_last_index_single_match(self):
        """Single matching element returns its index"""
        result = self.ec.find_last_index([1, 2, 3], lambda x, i, a: x == 2)
        assert result['found'] is True
        assert result['index'] == 1

    # FR-ES24-D-013: Multiple matches - returns last index
    def test_find_last_index_multiple_matches(self):
        """Multiple matches returns last index"""
        result = self.ec.find_last_index([1, 2, 3, 2, 1], lambda x, i, a: x == 2)
        assert result['found'] is True
        assert result['index'] == 3  # Last occurrence at index 3

    # FR-ES24-D-010: Sparse array handling
    def test_find_last_index_sparse_array_skip_holes(self):
        """Sparse array skips holes, returns last non-hole index"""
        result = self.ec.find_last_index([1, None, 3], lambda x, i, a: True, is_sparse=True)
        assert result['found'] is True
        assert result['index'] == 2  # Last non-hole element

    # FR-ES24-D-013: Match at boundaries
    def test_find_last_index_match_at_index_0(self):
        """Match at index 0"""
        result = self.ec.find_last_index([42, 1, 2], lambda x, i, a: x == 42)
        assert result['found'] is True
        assert result['index'] == 0

    def test_find_last_index_match_at_last_index(self):
        """Match at last index"""
        result = self.ec.find_last_index([1, 2, 42], lambda x, i, a: x == 42)
        assert result['found'] is True
        assert result['index'] == 2

    # FR-ES24-D-014: Predicate edge cases
    def test_find_last_index_predicate_always_true(self):
        """Predicate always true returns last index"""
        result = self.ec.find_last_index([1, 2, 3], lambda x, i, a: True)
        assert result['found'] is True
        assert result['index'] == 2  # Last index

    def test_find_last_index_predicate_always_false(self):
        """Predicate always false returns -1"""
        result = self.ec.find_last_index([1, 2, 3], lambda x, i, a: False)
        assert result['found'] is False
        assert result['index'] == -1

    # Error handling
    def test_find_last_index_invalid_array(self):
        """Non-array input raises TypeError"""
        with pytest.raises(TypeError, match="First argument must be an array"):
            self.ec.find_last_index("not an array", lambda x, i, a: True)

    def test_find_last_index_non_callable_predicate(self):
        """Non-callable predicate raises TypeError"""
        with pytest.raises(TypeError, match="Predicate must be a callable"):
            self.ec.find_last_index([1, 2, 3], "not callable")
