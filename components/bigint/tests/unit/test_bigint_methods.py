"""
Unit tests for BigInt methods.

Requirements tested:
- FR-P3-077: BigInt methods (toString, asIntN, asUintN)

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue, RangeError
from bigint_methods import bigint_to_string, bigint_as_int_n, bigint_as_uint_n


class TestBigIntToString:
    """Test BigInt.prototype.toString()."""

    def test_to_string_decimal(self):
        """BigInt(123).toString() should return '123'."""
        bigint = BigIntValue(123)
        result = bigint_to_string(bigint)
        assert result == '123'

    def test_to_string_radix_16(self):
        """BigInt(255).toString(16) should return 'ff'."""
        bigint = BigIntValue(255)
        result = bigint_to_string(bigint, radix=16)
        assert result == 'ff'

    def test_to_string_radix_2(self):
        """BigInt(10).toString(2) should return '1010'."""
        bigint = BigIntValue(10)
        result = bigint_to_string(bigint, radix=2)
        assert result == '1010'

    def test_to_string_radix_8(self):
        """BigInt(63).toString(8) should return '77'."""
        bigint = BigIntValue(63)
        result = bigint_to_string(bigint, radix=8)
        assert result == '77'

    def test_to_string_negative(self):
        """BigInt(-123).toString() should return '-123'."""
        bigint = BigIntValue(-123)
        result = bigint_to_string(bigint)
        assert result == '-123'

    def test_to_string_zero(self):
        """BigInt(0).toString() should return '0'."""
        bigint = BigIntValue(0)
        result = bigint_to_string(bigint)
        assert result == '0'

    def test_to_string_invalid_radix_throws(self):
        """toString with invalid radix should throw RangeError."""
        bigint = BigIntValue(123)
        with pytest.raises(RangeError, match="radix"):
            bigint_to_string(bigint, radix=1)


class TestBigIntAsIntN:
    """Test BigInt.asIntN()."""

    def test_as_int_n_fits_in_range(self):
        """BigInt.asIntN(8, 127n) should return 127n."""
        bigint = BigIntValue(127)
        result = bigint_as_int_n(8, bigint)
        assert result.value == 127

    def test_as_int_n_wraps_overflow(self):
        """BigInt.asIntN(8, 128n) should return -128n (wraps)."""
        bigint = BigIntValue(128)
        result = bigint_as_int_n(8, bigint)
        assert result.value == -128

    def test_as_int_n_wraps_large_positive(self):
        """BigInt.asIntN(8, 255n) should return -1n."""
        bigint = BigIntValue(255)
        result = bigint_as_int_n(8, bigint)
        assert result.value == -1

    def test_as_int_n_negative_in_range(self):
        """BigInt.asIntN(8, -128n) should return -128n."""
        bigint = BigIntValue(-128)
        result = bigint_as_int_n(8, bigint)
        assert result.value == -128

    def test_as_int_n_64_bits(self):
        """BigInt.asIntN(64, 2n**63n) should wrap to -2n**63n."""
        bigint = BigIntValue(2**63)
        result = bigint_as_int_n(64, bigint)
        assert result.value == -(2**63)


class TestBigIntAsUintN:
    """Test BigInt.asUintN()."""

    def test_as_uint_n_fits_in_range(self):
        """BigInt.asUintN(8, 255n) should return 255n."""
        bigint = BigIntValue(255)
        result = bigint_as_uint_n(8, bigint)
        assert result.value == 255

    def test_as_uint_n_wraps_overflow(self):
        """BigInt.asUintN(8, 256n) should return 0n."""
        bigint = BigIntValue(256)
        result = bigint_as_uint_n(8, bigint)
        assert result.value == 0

    def test_as_uint_n_wraps_negative(self):
        """BigInt.asUintN(8, -1n) should return 255n."""
        bigint = BigIntValue(-1)
        result = bigint_as_uint_n(8, bigint)
        assert result.value == 255

    def test_as_uint_n_64_bits(self):
        """BigInt.asUintN(64, -1n) should return 2n**64n - 1n."""
        bigint = BigIntValue(-1)
        result = bigint_as_uint_n(64, bigint)
        assert result.value == 2**64 - 1


class TestBigIntValueOf:
    """Test BigInt.prototype.valueOf()."""

    def test_value_of_returns_primitive(self):
        """BigInt(123).valueOf() should return the BigInt primitive."""
        bigint = BigIntValue(123)
        # valueOf should return self for primitive
        assert bigint.value_of() is bigint
