"""
Unit tests for BigInt comparison operations.

Requirements tested:
- FR-P3-075: BigInt comparison operators

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue
from bigint_comparison import (
    bigint_strict_equal, bigint_equal,
    bigint_less_than, bigint_less_than_or_equal,
    bigint_greater_than, bigint_greater_than_or_equal
)


class TestBigIntStrictEquality:
    """Test BigInt strict equality (===)."""

    def test_strict_equal_same_value(self):
        """5n === 5n should be true."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_strict_equal(a, b) is True

    def test_strict_equal_different_value(self):
        """5n === 3n should be false."""
        a = BigIntValue(5)
        b = BigIntValue(3)
        assert bigint_strict_equal(a, b) is False

    def test_strict_equal_zero(self):
        """0n === 0n should be true."""
        a = BigIntValue(0)
        b = BigIntValue(0)
        assert bigint_strict_equal(a, b) is True

    def test_strict_equal_negative(self):
        """(-5n) === (-5n) should be true."""
        a = BigIntValue(-5)
        b = BigIntValue(-5)
        assert bigint_strict_equal(a, b) is True


class TestBigIntAbstractEquality:
    """Test BigInt abstract equality (==)."""

    def test_equal_same_value(self):
        """5n == 5n should be true."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_equal(a, b) is True

    def test_equal_bigint_and_number_same_value(self):
        """5n == 5 should be true (mathematical value comparison)."""
        a = BigIntValue(5)
        b = 5  # Number
        assert bigint_equal(a, b) is True

    def test_equal_bigint_and_number_different_value(self):
        """5n == 3 should be false."""
        a = BigIntValue(5)
        b = 3  # Number
        assert bigint_equal(a, b) is False

    def test_equal_bigint_and_string(self):
        """5n == '5' should be true."""
        a = BigIntValue(5)
        b = '5'  # String
        assert bigint_equal(a, b) is True


class TestBigIntLessThan:
    """Test BigInt less than (<)."""

    def test_less_than_true(self):
        """3n < 5n should be true."""
        a = BigIntValue(3)
        b = BigIntValue(5)
        assert bigint_less_than(a, b) is True

    def test_less_than_false(self):
        """5n < 3n should be false."""
        a = BigIntValue(5)
        b = BigIntValue(3)
        assert bigint_less_than(a, b) is False

    def test_less_than_equal_values(self):
        """5n < 5n should be false."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_less_than(a, b) is False

    def test_less_than_negative(self):
        """(-5n) < 3n should be true."""
        a = BigIntValue(-5)
        b = BigIntValue(3)
        assert bigint_less_than(a, b) is True

    def test_less_than_bigint_and_number(self):
        """3n < 5 should be true."""
        a = BigIntValue(3)
        b = 5  # Number
        assert bigint_less_than(a, b) is True


class TestBigIntLessThanOrEqual:
    """Test BigInt less than or equal (<=)."""

    def test_less_than_or_equal_less(self):
        """3n <= 5n should be true."""
        a = BigIntValue(3)
        b = BigIntValue(5)
        assert bigint_less_than_or_equal(a, b) is True

    def test_less_than_or_equal_equal(self):
        """5n <= 5n should be true."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_less_than_or_equal(a, b) is True

    def test_less_than_or_equal_greater(self):
        """7n <= 5n should be false."""
        a = BigIntValue(7)
        b = BigIntValue(5)
        assert bigint_less_than_or_equal(a, b) is False


class TestBigIntGreaterThan:
    """Test BigInt greater than (>)."""

    def test_greater_than_true(self):
        """5n > 3n should be true."""
        a = BigIntValue(5)
        b = BigIntValue(3)
        assert bigint_greater_than(a, b) is True

    def test_greater_than_false(self):
        """3n > 5n should be false."""
        a = BigIntValue(3)
        b = BigIntValue(5)
        assert bigint_greater_than(a, b) is False

    def test_greater_than_equal_values(self):
        """5n > 5n should be false."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_greater_than(a, b) is False


class TestBigIntGreaterThanOrEqual:
    """Test BigInt greater than or equal (>=)."""

    def test_greater_than_or_equal_greater(self):
        """7n >= 5n should be true."""
        a = BigIntValue(7)
        b = BigIntValue(5)
        assert bigint_greater_than_or_equal(a, b) is True

    def test_greater_than_or_equal_equal(self):
        """5n >= 5n should be true."""
        a = BigIntValue(5)
        b = BigIntValue(5)
        assert bigint_greater_than_or_equal(a, b) is True

    def test_greater_than_or_equal_less(self):
        """3n >= 5n should be false."""
        a = BigIntValue(3)
        b = BigIntValue(5)
        assert bigint_greater_than_or_equal(a, b) is False
