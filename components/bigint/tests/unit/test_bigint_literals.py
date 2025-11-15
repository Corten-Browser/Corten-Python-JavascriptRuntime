"""
Unit tests for BigInt literal parsing.

Requirements tested:
- FR-P3-071: BigInt literals (123n, 0xFFn, etc.)

This file follows TDD RED phase - tests written first.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bigint_parser import parse_bigint_literal
from bigint_value import BigIntValue


class TestBigIntLiteralParsing:
    """Test parsing of BigInt literals."""

    def test_parse_decimal_bigint_literal(self):
        """Parse '123n' as BigInt literal."""
        result = parse_bigint_literal('123n')
        assert isinstance(result, BigIntValue)
        assert result.value == 123

    def test_parse_hex_bigint_literal(self):
        """Parse '0xFFn' as BigInt literal."""
        result = parse_bigint_literal('0xFFn')
        assert isinstance(result, BigIntValue)
        assert result.value == 255

    def test_parse_octal_bigint_literal(self):
        """Parse '0o77n' as BigInt literal."""
        result = parse_bigint_literal('0o77n')
        assert isinstance(result, BigIntValue)
        assert result.value == 63

    def test_parse_binary_bigint_literal(self):
        """Parse '0b1010n' as BigInt literal."""
        result = parse_bigint_literal('0b1010n')
        assert isinstance(result, BigIntValue)
        assert result.value == 10

    def test_parse_negative_bigint_literal(self):
        """Parse '-123n' as negative BigInt literal."""
        result = parse_bigint_literal('-123n')
        assert isinstance(result, BigIntValue)
        assert result.value == -123

    def test_parse_zero_bigint_literal(self):
        """Parse '0n' as zero BigInt literal."""
        result = parse_bigint_literal('0n')
        assert isinstance(result, BigIntValue)
        assert result.value == 0

    def test_parse_large_bigint_literal(self):
        """Parse very large BigInt literal."""
        large_str = str(2**100) + 'n'
        result = parse_bigint_literal(large_str)
        assert isinstance(result, BigIntValue)
        assert result.value == 2**100

    def test_literal_without_n_suffix_not_bigint(self):
        """'123' without 'n' should not be parsed as BigInt."""
        result = parse_bigint_literal('123')
        assert result is None

    def test_invalid_bigint_literal_throws(self):
        """Invalid BigInt literal should throw SyntaxError."""
        with pytest.raises(SyntaxError):
            parse_bigint_literal('0xGGn')
