"""
Integration tests for BigInt component.

These tests verify BigInt works correctly in combination with other features.

Requirements tested:
- All FR-P3-071 through FR-P3-080 integrated together
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_value import BigInt, BigIntValue
from bigint_parser import parse_bigint_literal
from bigint_arithmetic import bigint_add, bigint_multiply, bigint_exponentiate
from bigint_bitwise import bigint_and, bigint_or, bigint_left_shift
from bigint_comparison import bigint_strict_equal, bigint_less_than
from bigint_methods import bigint_to_string, bigint_as_int_n, bigint_as_uint_n
from bigint_coercion import bigint_to_boolean, bigint_typeof


class TestBigIntEndToEnd:
    """Test BigInt operations end-to-end."""

    def test_literal_to_arithmetic_to_string(self):
        """Parse literal, do arithmetic, convert to string."""
        # Parse "10n"
        a = parse_bigint_literal('10n')
        # Parse "20n"
        b = parse_bigint_literal('20n')
        # Add them
        result = bigint_add(a, b)
        # Convert to string
        string = bigint_to_string(result)
        assert string == '30'

    def test_constructor_to_bitwise_to_comparison(self):
        """Create BigInt, do bitwise, compare."""
        # Create BigInts
        a = BigInt(12)  # 0b1100
        b = BigInt(10)  # 0b1010
        # Bitwise AND
        result = bigint_and(a, b)
        # Compare to expected value
        expected = BigIntValue(8)  # 0b1000
        assert bigint_strict_equal(result, expected) is True

    def test_complex_expression(self):
        """Test complex BigInt expression: (2n ** 10n + 5n) * 3n."""
        # 2 ** 10 = 1024
        base = BigIntValue(2)
        exp = BigIntValue(10)
        power_result = bigint_exponentiate(base, exp)

        # 1024 + 5 = 1029
        five = BigIntValue(5)
        add_result = bigint_add(power_result, five)

        # 1029 * 3 = 3087
        three = BigIntValue(3)
        final_result = bigint_multiply(add_result, three)

        assert final_result.value == 3087

    def test_hex_literal_to_bitwise_to_string(self):
        """Parse hex literal, do bitwise, convert to hex string."""
        # Parse 0xFFn
        a = parse_bigint_literal('0xFFn')
        # Parse 0x0Fn
        b = parse_bigint_literal('0x0Fn')
        # Bitwise AND
        result = bigint_and(a, b)
        # Convert to hex string
        string = bigint_to_string(result, radix=16)
        assert string == 'f'

    def test_shift_then_wrap(self):
        """Left shift then wrap with asUintN."""
        # 1n << 10n = 1024n
        one = BigIntValue(1)
        ten = BigIntValue(10)
        shifted = bigint_left_shift(one, ten)

        # Wrap to 8 bits: 1024 % 256 = 0
        wrapped = bigint_as_uint_n(8, shifted)
        assert wrapped.value == 0


class TestBigIntWithConditionals:
    """Test BigInt in conditional contexts."""

    def test_bigint_in_boolean_context(self):
        """BigInt used in boolean context."""
        zero = BigIntValue(0)
        nonzero = BigIntValue(5)

        assert bigint_to_boolean(zero) is False
        assert bigint_to_boolean(nonzero) is True

    def test_bigint_comparison_chain(self):
        """Chain of comparisons."""
        a = BigIntValue(1)
        b = BigIntValue(2)
        c = BigIntValue(3)

        # 1 < 2 < 3
        assert bigint_less_than(a, b) is True
        assert bigint_less_than(b, c) is True
        assert bigint_less_than(a, c) is True


class TestBigIntRoundTrip:
    """Test BigInt conversions round-trip correctly."""

    def test_bigint_to_string_to_bigint(self):
        """Convert BigInt to string and back."""
        original = BigIntValue(12345)
        string = bigint_to_string(original)
        reconstructed = BigInt(string)
        assert bigint_strict_equal(original, reconstructed) is True

    def test_bigint_to_hex_string_to_bigint(self):
        """Convert BigInt to hex string and back."""
        original = BigIntValue(255)
        hex_string = bigint_to_string(original, radix=16)
        reconstructed = BigInt('0x' + hex_string)
        assert bigint_strict_equal(original, reconstructed) is True


class TestBigIntTypeofIntegration:
    """Test typeof integration."""

    def test_typeof_bigint_literal(self):
        """typeof on BigInt literal."""
        bigint = parse_bigint_literal('42n')
        assert bigint_typeof(bigint) == 'bigint'

    def test_typeof_bigint_constructor(self):
        """typeof on BigInt from constructor."""
        bigint = BigInt(42)
        assert bigint_typeof(bigint) == 'bigint'


class TestBigIntErrorHandling:
    """Test error handling across operations."""

    def test_type_mixing_prevented_in_arithmetic(self):
        """Type mixing throws TypeError in arithmetic."""
        from bigint_arithmetic import bigint_add
        bigint = BigIntValue(5)
        number = 3
        with pytest.raises(TypeError):
            bigint_add(bigint, number)

    def test_unary_plus_throws(self):
        """Unary plus on BigInt throws TypeError."""
        from bigint_arithmetic import bigint_unary_plus
        bigint = BigIntValue(5)
        with pytest.raises(TypeError):
            bigint_unary_plus(bigint)

    def test_unsigned_right_shift_throws(self):
        """Unsigned right shift on BigInt throws TypeError."""
        from bigint_bitwise import bigint_unsigned_right_shift
        a = BigIntValue(20)
        b = BigIntValue(2)
        with pytest.raises(TypeError):
            bigint_unsigned_right_shift(a, b)


class TestBigIntPerformance:
    """Test BigInt handles performance-critical cases."""

    def test_many_sequential_operations(self):
        """Perform many operations sequentially."""
        result = BigIntValue(1)
        for i in range(100):
            result = bigint_add(result, BigIntValue(1))
        assert result.value == 101

    def test_very_large_arithmetic_chain(self):
        """Chain arithmetic on very large numbers."""
        # Start with large number
        result = BigIntValue(2**100)
        # Multiply by 2
        result = bigint_multiply(result, BigIntValue(2))
        # Add 1
        result = bigint_add(result, BigIntValue(1))
        # Result should be 2^101 + 1
        expected = 2**101 + 1
        assert result.value == expected
