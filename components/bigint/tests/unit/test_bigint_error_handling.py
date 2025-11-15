"""
Additional tests for error handling paths to increase coverage.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue
from bigint_coercion import bigint_typeof, bigint_to_boolean, bigint_to_string_coerce, bigint_to_number_explicit
from bigint_comparison import bigint_strict_equal, bigint_equal, bigint_less_than
from bigint_methods import bigint_to_string, bigint_as_int_n, bigint_as_uint_n
from bigint_bitwise import bigint_and


class TestCoercionErrorHandling:
    """Test error handling in coercion functions."""

    def test_typeof_non_bigint_throws(self):
        """typeof on non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="Expected BigInt"):
            bigint_typeof(123)

    def test_to_boolean_non_bigint_throws(self):
        """Boolean() on non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="Expected BigInt"):
            bigint_to_boolean(123)

    def test_to_string_coerce_non_bigint_throws(self):
        """String() on non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="Expected BigInt"):
            bigint_to_string_coerce(123)

    def test_to_number_non_bigint_throws(self):
        """Number() on non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="Expected BigInt"):
            bigint_to_number_explicit(123)


class TestComparisonNullValues:
    """Test comparison with null/invalid values."""

    def test_strict_equal_non_bigint_operands(self):
        """Strict equality with non-BigInt operands should return false."""
        assert bigint_strict_equal(123, 456) is False
        assert bigint_strict_equal(BigIntValue(5), 5) is False

    def test_equal_with_invalid_values(self):
        """Abstract equality with invalid values should return false."""
        # These should handle gracefully and return False
        assert bigint_equal(None, BigIntValue(5)) is False
        assert bigint_equal(BigIntValue(5), None) is False

    def test_less_than_with_invalid_values(self):
        """Less than with invalid values should return false."""
        assert bigint_less_than(None, BigIntValue(5)) is False
        assert bigint_less_than(BigIntValue(5), None) is False


class TestMethodsErrorHandling:
    """Test error handling in methods."""

    def test_to_string_non_bigint_throws(self):
        """toString on non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="must be BigInt"):
            bigint_to_string(123)

    def test_to_string_radix_too_low_throws(self):
        """toString with radix < 2 should throw RangeError."""
        from bigint_value import RangeError
        with pytest.raises(RangeError, match="radix"):
            bigint_to_string(BigIntValue(10), radix=1)

    def test_to_string_radix_too_high_throws(self):
        """toString with radix > 36 should throw RangeError."""
        from bigint_value import RangeError
        with pytest.raises(RangeError, match="radix"):
            bigint_to_string(BigIntValue(10), radix=37)

    def test_as_int_n_non_bigint_throws(self):
        """asIntN with non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="must be BigInt"):
            bigint_as_int_n(8, 123)

    def test_as_int_n_invalid_bits_throws(self):
        """asIntN with invalid bits should throw TypeError."""
        with pytest.raises(TypeError, match="non-negative integer"):
            bigint_as_int_n(-1, BigIntValue(10))

    def test_as_int_n_non_int_bits_throws(self):
        """asIntN with non-int bits should throw TypeError."""
        with pytest.raises(TypeError, match="non-negative integer"):
            bigint_as_int_n(8.5, BigIntValue(10))

    def test_as_uint_n_non_bigint_throws(self):
        """asUintN with non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="must be BigInt"):
            bigint_as_uint_n(8, 123)

    def test_as_uint_n_invalid_bits_throws(self):
        """asUintN with invalid bits should throw TypeError."""
        with pytest.raises(TypeError, match="non-negative integer"):
            bigint_as_uint_n(-1, BigIntValue(10))


class TestBitwiseErrorHandling:
    """Test error handling in bitwise operations."""

    def test_bitwise_and_non_bigint_throws(self):
        """Bitwise AND with non-BigInt should throw TypeError."""
        with pytest.raises(TypeError, match="non-BigInt"):
            bigint_and(123, BigIntValue(5))

        with pytest.raises(TypeError, match="non-BigInt"):
            bigint_and(BigIntValue(5), 123)


class TestMethodsRadixEdgeCases:
    """Test methods with various radix values."""

    def test_to_string_radix_3(self):
        """Test toString with radix 3."""
        result = bigint_to_string(BigIntValue(10), radix=3)
        assert result == '101'  # 10 in base 3 is 101

    def test_to_string_radix_36(self):
        """Test toString with radix 36 (max)."""
        result = bigint_to_string(BigIntValue(1295), radix=36)
        assert result == 'zz'  # 35*36 + 35 = 1295 in base 36

    def test_to_string_radix_5_negative(self):
        """Test toString with radix 5 for negative number."""
        result = bigint_to_string(BigIntValue(-25), radix=5)
        assert result == '-100'  # -25 in base 5 is -100
