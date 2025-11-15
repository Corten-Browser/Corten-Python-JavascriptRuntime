"""
Unit tests for BigInt creation and constructor.

Requirements tested:
- FR-P3-072: BigInt constructor from various types
- FR-P3-078: typeof bigint type checking

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigInt, BigIntValue, RangeError


class TestBigIntConstruction:
    """Test BigInt() constructor function."""

    def test_bigint_from_integer(self):
        """BigInt(42) should create BigInt with value 42."""
        result = BigInt(42)
        assert isinstance(result, BigIntValue)
        assert result.value == 42

    def test_bigint_from_string_decimal(self):
        """BigInt('123') should create BigInt with value 123."""
        result = BigInt('123')
        assert isinstance(result, BigIntValue)
        assert result.value == 123

    def test_bigint_from_string_hex(self):
        """BigInt('0xFF') should create BigInt with value 255."""
        result = BigInt('0xFF')
        assert isinstance(result, BigIntValue)
        assert result.value == 255

    def test_bigint_from_string_octal(self):
        """BigInt('0o77') should create BigInt with value 63."""
        result = BigInt('0o77')
        assert isinstance(result, BigIntValue)
        assert result.value == 63

    def test_bigint_from_string_binary(self):
        """BigInt('0b1010') should create BigInt with value 10."""
        result = BigInt('0b1010')
        assert isinstance(result, BigIntValue)
        assert result.value == 10

    def test_bigint_from_boolean_true(self):
        """BigInt(true) should create BigInt with value 1."""
        result = BigInt(True)
        assert isinstance(result, BigIntValue)
        assert result.value == 1

    def test_bigint_from_boolean_false(self):
        """BigInt(false) should create BigInt with value 0."""
        result = BigInt(False)
        assert isinstance(result, BigIntValue)
        assert result.value == 0

    def test_bigint_from_bigint(self):
        """BigInt(bigint) should return equivalent BigInt."""
        original = BigInt(42)
        result = BigInt(original)
        assert isinstance(result, BigIntValue)
        assert result.value == 42

    def test_bigint_with_new_throws_typeerror(self):
        """new BigInt() should throw TypeError."""
        with pytest.raises(TypeError, match="BigInt is not a constructor"):
            # Simulate calling with new - set __new_target__ flag
            BigInt.__new_target__ = True
            try:
                BigInt(42)
            finally:
                BigInt.__new_target__ = False

    def test_bigint_from_fractional_throws_rangeerror(self):
        """BigInt(3.14) should throw RangeError."""
        with pytest.raises(RangeError, match="Cannot convert.*fractional"):
            BigInt(3.14)

    def test_bigint_from_infinity_throws_rangeerror(self):
        """BigInt(Infinity) should throw RangeError."""
        with pytest.raises(RangeError, match="Cannot convert.*infinity"):
            BigInt(float('inf'))

    def test_bigint_from_nan_throws_rangeerror(self):
        """BigInt(NaN) should throw RangeError."""
        with pytest.raises(RangeError, match="Cannot convert.*NaN"):
            BigInt(float('nan'))


class TestBigIntValue:
    """Test BigIntValue internal type."""

    def test_bigint_stores_arbitrary_precision(self):
        """BigIntValue should store arbitrary precision integers."""
        # Very large number (>2^64)
        large = 2**100
        bigint = BigIntValue(large)
        assert bigint.value == large

    def test_bigint_typeof(self):
        """typeof bigint should be 'bigint'."""
        bigint = BigIntValue(42)
        assert bigint.typeof() == "bigint"

    def test_bigint_zero_equals_zero(self):
        """BigInt(0) should equal BigInt(0)."""
        zero1 = BigIntValue(0)
        zero2 = BigIntValue(0)
        assert zero1.value == zero2.value


class TestBigIntEdgeCases:
    """Test edge cases in BigInt creation."""

    def test_bigint_negative_number(self):
        """BigInt(-42) should create negative BigInt."""
        result = BigInt(-42)
        assert result.value == -42

    def test_bigint_zero(self):
        """BigInt(0) should create zero BigInt."""
        result = BigInt(0)
        assert result.value == 0

    def test_bigint_from_empty_string_throws(self):
        """BigInt('') should throw SyntaxError."""
        with pytest.raises(SyntaxError):
            BigInt('')

    def test_bigint_from_invalid_string_throws(self):
        """BigInt('abc') should throw SyntaxError."""
        with pytest.raises(SyntaxError):
            BigInt('abc')
