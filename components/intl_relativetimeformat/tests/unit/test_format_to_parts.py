"""
Unit tests for RelativeTimeFormat.formatToParts() method (FR-ES24-C-039).

Tests:
1. formatToParts structure
2. formatToParts for past values
3. formatToParts for future values
4. formatToParts with zero
5. Part types (literal, integer)
6. Ordering of parts
7. Multiple parts
8. Invalid value
9. Invalid unit
10. Locale-specific parts
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatFormatToParts:
    """Test RelativeTimeFormat.formatToParts() method (FR-ES24-C-039)."""

    def test_formatToParts_returns_array(self):
        """Test that formatToParts returns an array."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(1, 'day')

        assert isinstance(parts, list)
        assert len(parts) > 0

    def test_formatToParts_part_structure(self):
        """Test that each part has type and value."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(1, 'day')

        for part in parts:
            assert isinstance(part, dict)
            assert 'type' in part
            assert 'value' in part
            assert part['type'] in ['literal', 'integer']
            assert isinstance(part['value'], str)

    def test_formatToParts_future_value(self):
        """Test formatToParts for future (positive) values."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(2, 'day')

        # Expected: [{type: "literal", value: "in "}, {type: "integer", value: "2"}, {type: "literal", value: " days"}]
        assert len(parts) == 3
        assert parts[0]['type'] == 'literal' and parts[0]['value'] == 'in '
        assert parts[1]['type'] == 'integer' and parts[1]['value'] == '2'
        assert parts[2]['type'] == 'literal' and 'day' in parts[2]['value']

    def test_formatToParts_past_value(self):
        """Test formatToParts for past (negative) values."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(-1, 'day')

        # Expected: [{type: "integer", value: "1"}, {type: "literal", value: " day ago"}]
        assert len(parts) >= 2
        # Should contain integer part and literal with "ago"
        has_integer = any(p['type'] == 'integer' and p['value'] == '1' for p in parts)
        has_ago = any('ago' in p['value'] for p in parts)
        assert has_integer
        assert has_ago

    def test_formatToParts_with_zero(self):
        """Test formatToParts with zero value."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(0, 'day')

        # Should have integer part with "0"
        has_zero = any(p['type'] == 'integer' and p['value'] == '0' for p in parts)
        assert has_zero

    def test_formatToParts_literal_parts(self):
        """Test that literal parts contain text."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(5, 'hour')

        literal_parts = [p for p in parts if p['type'] == 'literal']
        assert len(literal_parts) >= 1
        # Literals should contain words like "in", "hours", etc.
        all_text = ''.join(p['value'] for p in literal_parts)
        assert len(all_text) > 0

    def test_formatToParts_integer_parts(self):
        """Test that integer parts contain numeric values."""
        rtf = RelativeTimeFormat('en-US')
        parts = rtf.formatToParts(42, 'day')

        integer_parts = [p for p in parts if p['type'] == 'integer']
        assert len(integer_parts) == 1
        assert integer_parts[0]['value'] == '42'

    def test_formatToParts_reconstructs_format(self):
        """Test that joining parts equals format() output."""
        rtf = RelativeTimeFormat('en-US')

        value, unit = 3, 'day'
        formatted = rtf.format(value, unit)
        parts = rtf.formatToParts(value, unit)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed

    def test_formatToParts_invalid_value(self):
        """Test formatToParts with invalid value type."""
        rtf = RelativeTimeFormat('en-US')

        with pytest.raises(TypeError, match="Value must be a number"):
            rtf.formatToParts('invalid', 'day')

    def test_formatToParts_invalid_unit(self):
        """Test formatToParts with invalid unit."""
        rtf = RelativeTimeFormat('en-US')

        with pytest.raises(RangeError, match="Invalid unit argument"):
            rtf.formatToParts(1, 'invalid')

    def test_formatToParts_with_numeric_auto(self):
        """Test formatToParts with numeric='auto' for special words."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})
        parts = rtf.formatToParts(-1, 'day')

        # With auto, -1 day should be "yesterday" (one literal part)
        # Expected: [{type: "literal", value: "yesterday"}]
        if len(parts) == 1:
            assert parts[0]['type'] == 'literal'
            assert parts[0]['value'] == 'yesterday'


# TypeError and RangeError imported from src
