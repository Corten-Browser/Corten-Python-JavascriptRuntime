"""
Unit tests for BigInt edge cases and very large numbers.

Requirements tested:
- FR-P3-080: BigInt edge cases (very large numbers)

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigInt, BigIntValue
from bigint_arithmetic import bigint_add, bigint_multiply, bigint_exponentiate
from bigint_bitwise import bigint_left_shift
from bigint_comparison import bigint_less_than, bigint_strict_equal


class TestVeryLargeBigInts:
    """Test BigInts larger than 2^64."""

    def test_create_large_bigint(self):
        """Create BigInt larger than 2^64."""
        large = 2**100
        bigint = BigIntValue(large)
        assert bigint.value == large

    def test_add_very_large_bigints(self):
        """Add two very large BigInts."""
        a = BigIntValue(2**100)
        b = BigIntValue(2**100)
        result = bigint_add(a, b)
        assert result.value == 2 * (2**100)

    def test_multiply_to_huge_bigint(self):
        """Multiply to create extremely large BigInt."""
        a = BigIntValue(2**200)
        b = BigIntValue(2**200)
        result = bigint_multiply(a, b)
        assert result.value == 2**400

    def test_exponentiate_to_astronomical_bigint(self):
        """2n ** 1000n should work (very large result)."""
        a = BigIntValue(2)
        b = BigIntValue(1000)
        result = bigint_exponentiate(a, b)
        assert result.value == 2**1000

    def test_left_shift_creates_large_bigint(self):
        """1n << 1000n should create very large BigInt."""
        a = BigIntValue(1)
        b = BigIntValue(1000)
        result = bigint_left_shift(a, b)
        assert result.value == 2**1000


class TestBigIntPrecision:
    """Test BigInt maintains exact precision."""

    def test_no_precision_loss_large_addition(self):
        """Large BigInt addition maintains exact precision."""
        # Number would lose precision here
        a = BigIntValue(2**100 + 1)
        b = BigIntValue(2**100 + 2)
        result = bigint_add(a, b)
        assert result.value == 2 * (2**100) + 3

    def test_comparison_with_very_close_large_values(self):
        """Can distinguish between very close large values."""
        a = BigIntValue(2**100)
        b = BigIntValue(2**100 + 1)
        assert bigint_less_than(a, b) is True
        assert bigint_strict_equal(a, b) is False


class TestBigIntNegativeLarge:
    """Test very large negative BigInts."""

    def test_large_negative_bigint(self):
        """Create very large negative BigInt."""
        bigint = BigIntValue(-(2**100))
        assert bigint.value == -(2**100)

    def test_negate_large_positive_to_negative(self):
        """Negating large positive BigInt."""
        from bigint_arithmetic import bigint_negate
        positive = BigIntValue(2**100)
        negative = bigint_negate(positive)
        assert negative.value == -(2**100)


class TestBigIntBoundaries:
    """Test BigInt at various boundaries."""

    def test_bigint_at_max_safe_integer(self):
        """BigInt at Number.MAX_SAFE_INTEGER boundary."""
        # MAX_SAFE_INTEGER = 2^53 - 1
        max_safe = 2**53 - 1
        bigint = BigIntValue(max_safe)
        assert bigint.value == max_safe

    def test_bigint_beyond_max_safe_integer(self):
        """BigInt beyond Number.MAX_SAFE_INTEGER."""
        beyond_safe = 2**53
        bigint = BigIntValue(beyond_safe)
        assert bigint.value == beyond_safe

    def test_bigint_at_64_bit_boundary(self):
        """BigInt at 2^64 boundary."""
        at_64_bit = 2**64
        bigint = BigIntValue(at_64_bit)
        assert bigint.value == at_64_bit


class TestBigIntConstructorEdgeCases:
    """Test BigInt constructor edge cases."""

    def test_bigint_from_very_large_string(self):
        """BigInt from very large string."""
        large_str = str(2**1000)
        result = BigInt(large_str)
        assert result.value == 2**1000

    def test_bigint_from_hex_string_large(self):
        """BigInt from large hex string."""
        # 0xFFFFFFFFFFFFFFFFFFFFFFFF (96 bits of F)
        hex_str = '0x' + 'F' * 24
        result = BigInt(hex_str)
        assert result.value == int(hex_str, 16)

    def test_bigint_minimum_value(self):
        """BigInt can represent arbitrarily small negative values."""
        very_negative = -(2**1000)
        bigint = BigIntValue(very_negative)
        assert bigint.value == very_negative


class TestBigIntArithmeticEdgeCases:
    """Test arithmetic edge cases."""

    def test_division_very_large_by_small(self):
        """Divide very large BigInt by small BigInt."""
        from bigint_arithmetic import bigint_divide
        large = BigIntValue(2**1000)
        small = BigIntValue(2)
        result = bigint_divide(large, small)
        assert result.value == 2**999

    def test_remainder_large_numbers(self):
        """Remainder with large numbers."""
        from bigint_arithmetic import bigint_remainder
        large = BigIntValue(2**100 + 7)
        divisor = BigIntValue(10)
        result = bigint_remainder(large, divisor)
        assert result.value == (2**100 + 7) % 10


class TestBigIntStringConversion:
    """Test string conversion of large BigInts."""

    def test_to_string_very_large_bigint(self):
        """toString on very large BigInt."""
        from bigint_methods import bigint_to_string
        large = BigIntValue(2**100)
        result = bigint_to_string(large)
        assert result == str(2**100)
        # Verify length is reasonable (2^100 ≈ 1.27e30, so ~31 digits)
        assert len(result) > 20
