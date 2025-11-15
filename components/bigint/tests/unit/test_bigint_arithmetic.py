"""
Unit tests for BigInt arithmetic operations.

Requirements tested:
- FR-P3-073: BigInt arithmetic operations
- FR-P3-076: BigInt/Number mixing restrictions

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue, RangeError
from bigint_arithmetic import (
    bigint_add, bigint_subtract, bigint_multiply,
    bigint_divide, bigint_remainder, bigint_exponentiate,
    bigint_negate, bigint_unary_plus
)


class TestBigIntAddition:
    """Test BigInt addition."""

    def test_add_two_positive_bigints(self):
        """2n + 3n should equal 5n."""
        a = BigIntValue(2)
        b = BigIntValue(3)
        result = bigint_add(a, b)
        assert result.value == 5

    def test_add_negative_bigints(self):
        """(-5n) + (-3n) should equal -8n."""
        a = BigIntValue(-5)
        b = BigIntValue(-3)
        result = bigint_add(a, b)
        assert result.value == -8

    def test_add_large_bigints(self):
        """Test addition of very large BigInts."""
        a = BigIntValue(2**100)
        b = BigIntValue(2**100)
        result = bigint_add(a, b)
        assert result.value == 2 * (2**100)

    def test_add_bigint_and_number_throws_typeerror(self):
        """BigInt + Number should throw TypeError."""
        a = BigIntValue(5)
        b = 3  # Regular number
        with pytest.raises(TypeError, match="Cannot mix BigInt and other types"):
            bigint_add(a, b)


class TestBigIntSubtraction:
    """Test BigInt subtraction."""

    def test_subtract_bigints(self):
        """10n - 3n should equal 7n."""
        a = BigIntValue(10)
        b = BigIntValue(3)
        result = bigint_subtract(a, b)
        assert result.value == 7

    def test_subtract_to_negative(self):
        """3n - 10n should equal -7n."""
        a = BigIntValue(3)
        b = BigIntValue(10)
        result = bigint_subtract(a, b)
        assert result.value == -7

    def test_subtract_large_bigints(self):
        """Test subtraction of very large BigInts."""
        a = BigIntValue(2**100)
        b = BigIntValue(1)
        result = bigint_subtract(a, b)
        assert result.value == 2**100 - 1


class TestBigIntMultiplication:
    """Test BigInt multiplication."""

    def test_multiply_bigints(self):
        """6n * 7n should equal 42n."""
        a = BigIntValue(6)
        b = BigIntValue(7)
        result = bigint_multiply(a, b)
        assert result.value == 42

    def test_multiply_by_zero(self):
        """123n * 0n should equal 0n."""
        a = BigIntValue(123)
        b = BigIntValue(0)
        result = bigint_multiply(a, b)
        assert result.value == 0

    def test_multiply_negative_bigints(self):
        """(-5n) * (-3n) should equal 15n."""
        a = BigIntValue(-5)
        b = BigIntValue(-3)
        result = bigint_multiply(a, b)
        assert result.value == 15

    def test_multiply_large_bigints(self):
        """Test multiplication of large BigInts."""
        a = BigIntValue(2**50)
        b = BigIntValue(2**50)
        result = bigint_multiply(a, b)
        assert result.value == 2**100


class TestBigIntDivision:
    """Test BigInt division."""

    def test_divide_bigints(self):
        """10n / 3n should equal 3n (truncates toward zero)."""
        a = BigIntValue(10)
        b = BigIntValue(3)
        result = bigint_divide(a, b)
        assert result.value == 3

    def test_divide_negative_truncates_toward_zero(self):
        """(-10n) / 3n should equal -3n (truncates toward zero)."""
        a = BigIntValue(-10)
        b = BigIntValue(3)
        result = bigint_divide(a, b)
        assert result.value == -3

    def test_divide_by_zero_throws_rangeerror(self):
        """Division by zero should throw RangeError."""
        a = BigIntValue(10)
        b = BigIntValue(0)
        with pytest.raises(RangeError, match="Division by zero"):
            bigint_divide(a, b)

    def test_divide_exact(self):
        """20n / 4n should equal 5n."""
        a = BigIntValue(20)
        b = BigIntValue(4)
        result = bigint_divide(a, b)
        assert result.value == 5


class TestBigIntRemainder:
    """Test BigInt remainder."""

    def test_remainder_bigints(self):
        """10n % 3n should equal 1n."""
        a = BigIntValue(10)
        b = BigIntValue(3)
        result = bigint_remainder(a, b)
        assert result.value == 1

    def test_remainder_negative_dividend(self):
        """(-10n) % 3n should equal -1n."""
        a = BigIntValue(-10)
        b = BigIntValue(3)
        result = bigint_remainder(a, b)
        assert result.value == -1

    def test_remainder_by_zero_throws_rangeerror(self):
        """Remainder by zero should throw RangeError."""
        a = BigIntValue(10)
        b = BigIntValue(0)
        with pytest.raises(RangeError, match="Division by zero"):
            bigint_remainder(a, b)


class TestBigIntExponentiation:
    """Test BigInt exponentiation."""

    def test_exponentiate_bigints(self):
        """2n ** 10n should equal 1024n."""
        a = BigIntValue(2)
        b = BigIntValue(10)
        result = bigint_exponentiate(a, b)
        assert result.value == 1024

    def test_exponentiate_to_zero(self):
        """5n ** 0n should equal 1n."""
        a = BigIntValue(5)
        b = BigIntValue(0)
        result = bigint_exponentiate(a, b)
        assert result.value == 1

    def test_exponentiate_negative_exponent_throws_rangeerror(self):
        """BigInt ** negative should throw RangeError."""
        a = BigIntValue(2)
        b = BigIntValue(-1)
        with pytest.raises(RangeError, match="Exponent must be non-negative"):
            bigint_exponentiate(a, b)


class TestBigIntUnaryOperators:
    """Test BigInt unary operators."""

    def test_unary_negate(self):
        """-(-5n) should equal 5n."""
        a = BigIntValue(-5)
        result = bigint_negate(a)
        assert result.value == 5

    def test_unary_plus_throws_typeerror(self):
        """+bigint should throw TypeError."""
        a = BigIntValue(5)
        with pytest.raises(TypeError, match="Cannot convert.*BigInt.*number"):
            bigint_unary_plus(a)
