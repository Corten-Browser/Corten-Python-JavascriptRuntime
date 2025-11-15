"""
Unit tests for SameValueZero equality algorithm.

Requirements: FR-P3-037, FR-P3-039
- +0 === -0: true
- NaN === NaN: true
- Object keys compared by reference
"""

import pytest
import math
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestSameValueZero:
    """Tests for SameValueZero equality algorithm."""

    def test_same_value_zero_with_integers(self):
        """Test SameValueZero with equal integers."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero(5, 5) is True
        assert same_value_zero(0, 0) is True
        assert same_value_zero(-10, -10) is True
        assert same_value_zero(5, 6) is False

    def test_same_value_zero_with_floats(self):
        """Test SameValueZero with floats."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero(3.14, 3.14) is True
        assert same_value_zero(3.14, 3.15) is False

    def test_same_value_zero_positive_and_negative_zero(self):
        """Test that +0 and -0 are considered equal (SameValueZero rule)."""
        from components.collections.src.same_value_zero import same_value_zero

        # SameValueZero treats +0 and -0 as equal (unlike SameValue)
        assert same_value_zero(0.0, -0.0) is True
        assert same_value_zero(-0.0, 0.0) is True
        assert same_value_zero(0.0, 0.0) is True
        assert same_value_zero(-0.0, -0.0) is True

    def test_same_value_zero_nan_equals_nan(self):
        """Test that NaN equals NaN (SameValueZero rule)."""
        from components.collections.src.same_value_zero import same_value_zero

        # SameValueZero treats NaN as equal to itself (unlike strict equality)
        assert same_value_zero(float('nan'), float('nan')) is True
        assert same_value_zero(math.nan, math.nan) is True

    def test_same_value_zero_with_strings(self):
        """Test SameValueZero with strings."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero("hello", "hello") is True
        assert same_value_zero("hello", "world") is False
        assert same_value_zero("", "") is True

    def test_same_value_zero_with_booleans(self):
        """Test SameValueZero with booleans."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero(True, True) is True
        assert same_value_zero(False, False) is True
        assert same_value_zero(True, False) is False

    def test_same_value_zero_with_none(self):
        """Test SameValueZero with None."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero(None, None) is True
        assert same_value_zero(None, 0) is False

    def test_same_value_zero_with_objects(self):
        """Test SameValueZero with objects (reference equality)."""
        from components.collections.src.same_value_zero import same_value_zero

        obj1 = {"a": 1}
        obj2 = {"a": 1}
        obj3 = obj1

        # Same reference
        assert same_value_zero(obj1, obj3) is True
        # Different references (even with same content)
        assert same_value_zero(obj1, obj2) is False
        assert same_value_zero(obj2, obj3) is False

    def test_same_value_zero_with_lists(self):
        """Test SameValueZero with lists (reference equality)."""
        from components.collections.src.same_value_zero import same_value_zero

        list1 = [1, 2, 3]
        list2 = [1, 2, 3]
        list3 = list1

        # Same reference
        assert same_value_zero(list1, list3) is True
        # Different references
        assert same_value_zero(list1, list2) is False

    def test_same_value_zero_different_types(self):
        """Test SameValueZero with different types."""
        from components.collections.src.same_value_zero import same_value_zero

        assert same_value_zero(5, "5") is False
        assert same_value_zero(0, False) is False
        assert same_value_zero(1, True) is False
        assert same_value_zero(None, 0) is False
        assert same_value_zero([], {}) is False
