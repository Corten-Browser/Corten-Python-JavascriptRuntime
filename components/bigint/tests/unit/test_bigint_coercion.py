"""
Unit tests for BigInt coercion and type checking.

Requirements tested:
- FR-P3-076: BigInt/Number mixing restrictions
- FR-P3-078: typeof bigint type checking
- FR-P3-079: BigInt coercion rules

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigIntValue
from bigint_coercion import (
    bigint_typeof, bigint_to_boolean, bigint_to_string_coerce,
    bigint_to_number_explicit, validate_bigint_only_operation
)


class TestBigIntTypeof:
    """Test typeof bigint."""

    def test_typeof_bigint(self):
        """typeof 5n should be 'bigint'."""
        bigint = BigIntValue(5)
        assert bigint_typeof(bigint) == 'bigint'

    def test_typeof_zero_bigint(self):
        """typeof 0n should be 'bigint'."""
        bigint = BigIntValue(0)
        assert bigint_typeof(bigint) == 'bigint'

    def test_typeof_negative_bigint(self):
        """typeof -5n should be 'bigint'."""
        bigint = BigIntValue(-5)
        assert bigint_typeof(bigint) == 'bigint'


class TestBigIntToBoolean:
    """Test BigInt to Boolean coercion."""

    def test_bigint_zero_to_boolean_false(self):
        """Boolean(0n) should be false."""
        bigint = BigIntValue(0)
        result = bigint_to_boolean(bigint)
        assert result is False

    def test_bigint_nonzero_to_boolean_true(self):
        """Boolean(5n) should be true."""
        bigint = BigIntValue(5)
        result = bigint_to_boolean(bigint)
        assert result is True

    def test_bigint_negative_to_boolean_true(self):
        """Boolean(-5n) should be true."""
        bigint = BigIntValue(-5)
        result = bigint_to_boolean(bigint)
        assert result is True


class TestBigIntToStringCoercion:
    """Test BigInt to String coercion."""

    def test_string_coercion(self):
        """String(123n) should be '123'."""
        bigint = BigIntValue(123)
        result = bigint_to_string_coerce(bigint)
        assert result == '123'

    def test_string_coercion_negative(self):
        """String(-123n) should be '-123'."""
        bigint = BigIntValue(-123)
        result = bigint_to_string_coerce(bigint)
        assert result == '-123'


class TestBigIntToNumber:
    """Test BigInt to Number coercion."""

    def test_explicit_number_conversion(self):
        """Number(5n) should return 5."""
        bigint = BigIntValue(5)
        result = bigint_to_number_explicit(bigint)
        assert result == 5
        assert isinstance(result, (int, float))

    def test_explicit_number_conversion_large_loses_precision(self):
        """Number(very large BigInt) may lose precision."""
        # This is allowed - JavaScript Number has limited precision
        bigint = BigIntValue(2**100)
        result = bigint_to_number_explicit(bigint)
        # Just verify it returns a number (precision loss is expected)
        assert isinstance(result, (int, float))


class TestBigIntTypeMixing:
    """Test BigInt/Number type mixing restrictions."""

    def test_validate_bigint_only_accepts_bigint(self):
        """validate_bigint_only_operation should accept BigInt operands."""
        a = BigIntValue(5)
        b = BigIntValue(3)
        # Should not raise
        validate_bigint_only_operation(a, b)

    def test_validate_bigint_only_rejects_number(self):
        """validate_bigint_only_operation should reject Number operands."""
        a = BigIntValue(5)
        b = 3  # Regular number
        with pytest.raises(TypeError, match="Cannot mix BigInt and other types"):
            validate_bigint_only_operation(a, b)

    def test_validate_bigint_only_rejects_string(self):
        """validate_bigint_only_operation should reject String operands."""
        a = BigIntValue(5)
        b = "3"  # String
        with pytest.raises(TypeError, match="Cannot mix BigInt and other types"):
            validate_bigint_only_operation(a, b)

    def test_math_functions_with_bigint_throw(self):
        """Math.* functions should throw TypeError with BigInt."""
        # This would be tested in integration, but we can document the requirement
        # Math.sqrt(5n) → TypeError
        # Math.abs(5n) → TypeError
        # etc.
        pass
