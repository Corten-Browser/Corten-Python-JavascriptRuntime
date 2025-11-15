"""
Unit tests for BigInt bitwise operations.

Requirements tested:
- FR-P3-074: BigInt bitwise operations

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue
from bigint_bitwise import (
    bigint_and, bigint_or, bigint_xor, bigint_not,
    bigint_left_shift, bigint_signed_right_shift,
    bigint_unsigned_right_shift
)


class TestBigIntBitwiseAND:
    """Test BigInt bitwise AND."""

    def test_and_bigints(self):
        """0b1100n & 0b1010n should equal 0b1000n (8n)."""
        a = BigIntValue(0b1100)  # 12
        b = BigIntValue(0b1010)  # 10
        result = bigint_and(a, b)
        assert result.value == 0b1000  # 8

    def test_and_with_zero(self):
        """123n & 0n should equal 0n."""
        a = BigIntValue(123)
        b = BigIntValue(0)
        result = bigint_and(a, b)
        assert result.value == 0

    def test_and_negative_bigints(self):
        """(-1n) & 0xFFn should equal 0xFFn."""
        a = BigIntValue(-1)
        b = BigIntValue(0xFF)
        result = bigint_and(a, b)
        assert result.value == 0xFF


class TestBigIntBitwiseOR:
    """Test BigInt bitwise OR."""

    def test_or_bigints(self):
        """0b1100n | 0b1010n should equal 0b1110n (14n)."""
        a = BigIntValue(0b1100)  # 12
        b = BigIntValue(0b1010)  # 10
        result = bigint_or(a, b)
        assert result.value == 0b1110  # 14

    def test_or_with_zero(self):
        """123n | 0n should equal 123n."""
        a = BigIntValue(123)
        b = BigIntValue(0)
        result = bigint_or(a, b)
        assert result.value == 123


class TestBigIntBitwiseXOR:
    """Test BigInt bitwise XOR."""

    def test_xor_bigints(self):
        """0b1100n ^ 0b1010n should equal 0b0110n (6n)."""
        a = BigIntValue(0b1100)  # 12
        b = BigIntValue(0b1010)  # 10
        result = bigint_xor(a, b)
        assert result.value == 0b0110  # 6

    def test_xor_with_self_is_zero(self):
        """123n ^ 123n should equal 0n."""
        a = BigIntValue(123)
        result = bigint_xor(a, a)
        assert result.value == 0


class TestBigIntBitwiseNOT:
    """Test BigInt bitwise NOT."""

    def test_not_bigint(self):
        """~0n should equal -1n."""
        a = BigIntValue(0)
        result = bigint_not(a)
        assert result.value == -1

    def test_not_positive(self):
        """~5n should equal -6n."""
        a = BigIntValue(5)
        result = bigint_not(a)
        assert result.value == -6

    def test_not_negative(self):
        """~(-1n) should equal 0n."""
        a = BigIntValue(-1)
        result = bigint_not(a)
        assert result.value == 0


class TestBigIntLeftShift:
    """Test BigInt left shift."""

    def test_left_shift_bigint(self):
        """5n << 2n should equal 20n."""
        a = BigIntValue(5)
        b = BigIntValue(2)
        result = bigint_left_shift(a, b)
        assert result.value == 20

    def test_left_shift_by_zero(self):
        """5n << 0n should equal 5n."""
        a = BigIntValue(5)
        b = BigIntValue(0)
        result = bigint_left_shift(a, b)
        assert result.value == 5

    def test_left_shift_large_amount(self):
        """1n << 100n should equal 2**100."""
        a = BigIntValue(1)
        b = BigIntValue(100)
        result = bigint_left_shift(a, b)
        assert result.value == 2**100

    def test_left_shift_negative_amount_is_right_shift(self):
        """20n << -2n should equal 5n (right shift by 2)."""
        a = BigIntValue(20)
        b = BigIntValue(-2)
        result = bigint_left_shift(a, b)
        assert result.value == 5


class TestBigIntSignedRightShift:
    """Test BigInt signed right shift."""

    def test_right_shift_bigint(self):
        """20n >> 2n should equal 5n."""
        a = BigIntValue(20)
        b = BigIntValue(2)
        result = bigint_signed_right_shift(a, b)
        assert result.value == 5

    def test_right_shift_negative_preserves_sign(self):
        """(-20n) >> 2n should equal -5n."""
        a = BigIntValue(-20)
        b = BigIntValue(2)
        result = bigint_signed_right_shift(a, b)
        assert result.value == -5

    def test_right_shift_by_zero(self):
        """5n >> 0n should equal 5n."""
        a = BigIntValue(5)
        b = BigIntValue(0)
        result = bigint_signed_right_shift(a, b)
        assert result.value == 5


class TestBigIntUnsignedRightShift:
    """Test BigInt unsigned right shift (should throw)."""

    def test_unsigned_right_shift_throws_typeerror(self):
        """BigInt >>> BigInt should throw TypeError."""
        a = BigIntValue(20)
        b = BigIntValue(2)
        with pytest.raises(TypeError, match="BigInts have no unsigned right shift"):
            bigint_unsigned_right_shift(a, b)
