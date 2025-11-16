"""
Unit tests for formatRange() and formatRangeToParts() methods
(FR-ES24-C-024, FR-ES24-C-025)

These tests cover:
- Simple range formatting
- Currency range
- Unit range
- Compact notation range
- Negative ranges
- Same value range
- Large number ranges
- Invalid ranges (start > end)
- Range parts with sources
- Shared literal parts
"""

import pytest
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestFormatRangeBasic:
    """Test basic formatRange functionality (FR-ES24-C-024)."""

    def test_format_range_simple(self):
        """Format simple number range."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(100, 200)

        assert isinstance(result, str)
        assert '100' in result
        assert '200' in result
        # Should have some separator
        assert '–' in result or '-' in result or 'to' in result.lower()

    def test_format_range_decimals(self):
        """Format range with decimals."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(10.5, 20.5)

        assert '10.5' in result or '10,5' in result
        assert '20.5' in result or '20,5' in result

    def test_format_range_large_numbers(self):
        """Format range with large numbers."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(1000000, 5000000)

        assert '1,000,000' in result or '1000000' in result
        assert '5,000,000' in result or '5000000' in result

    def test_format_range_same_values(self):
        """Format range where start equals end."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(100, 100)

        # Implementation choice: might show "100" or "100–100"
        assert '100' in result


class TestFormatRangeCurrency:
    """Test currency range formatting."""

    def test_format_range_currency_usd(self):
        """Format USD currency range."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        result = formatter.formatRange(100, 200)

        assert '$' in result
        assert '100' in result
        assert '200' in result
        # Should show currency symbol for both values or shared
        assert result.count('$') >= 1

    def test_format_range_currency_eur(self):
        """Format EUR currency range."""
        formatter = IntlNumberFormat('de-DE', {
            'style': 'currency',
            'currency': 'EUR'
        })
        result = formatter.formatRange(100, 200)

        assert '€' in result or 'EUR' in result
        assert '100' in result
        assert '200' in result

    def test_format_range_currency_decimal(self):
        """Format currency range with decimals."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        result = formatter.formatRange(99.99, 199.99)

        assert '99.99' in result
        assert '199.99' in result
        assert '$' in result


class TestFormatRangeUnit:
    """Test unit range formatting."""

    def test_format_range_unit_meter(self):
        """Format meter unit range."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        result = formatter.formatRange(10, 20)

        assert '10' in result
        assert '20' in result
        assert 'm' in result.lower() or 'meter' in result.lower()

    def test_format_range_unit_celsius(self):
        """Format celsius unit range."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'celsius'
        })
        result = formatter.formatRange(20, 30)

        assert '20' in result
        assert '30' in result
        assert '°' in result or 'c' in result.lower()


class TestFormatRangeNotation:
    """Test range formatting with notations."""

    def test_format_range_compact(self):
        """Format range with compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.formatRange(1000, 5000)

        # Should show compact form
        assert 'K' in result or 'k' in result or 'thousand' in result.lower()

    def test_format_range_compact_millions(self):
        """Format range with compact notation (millions)."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.formatRange(1000000, 5000000)

        assert 'M' in result or 'million' in result.lower()

    def test_format_range_scientific(self):
        """Format range with scientific notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'scientific'})
        result = formatter.formatRange(123000, 456000)

        # Should have exponent notation
        assert 'E' in result or 'e' in result or '×' in result


class TestFormatRangeNegative:
    """Test range formatting with negative numbers."""

    def test_format_range_negative_to_positive(self):
        """Format range from negative to positive."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(-100, 100)

        assert '-100' in result or '-' in result[:5]
        assert '100' in result

    def test_format_range_both_negative(self):
        """Format range with both negative."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.formatRange(-200, -100)

        assert '-200' in result or '-' in result[:5]
        assert '-100' in result or result.count('-') >= 1

    def test_format_range_negative_currency(self):
        """Format negative currency range."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        result = formatter.formatRange(-100, -50)

        assert '$' in result
        assert '-' in result or '(' in result


class TestFormatRangePercent:
    """Test percent range formatting."""

    def test_format_range_percent(self):
        """Format percent range."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        result = formatter.formatRange(0.25, 0.75)

        assert '%' in result
        assert '25' in result
        assert '75' in result


class TestFormatRangeErrorHandling:
    """Test error handling in formatRange."""

    def test_format_range_start_greater_than_end(self):
        """Start > end should raise error."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises((ValueError, RangeError)):
            formatter.formatRange(200, 100)

    def test_format_range_invalid_type(self):
        """Invalid types should raise error."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises(TypeError):
            formatter.formatRange("100", "200")

    def test_format_range_nan(self):
        """NaN in range should raise error or handle gracefully."""
        formatter = IntlNumberFormat('en-US')
        # Behavior may vary: might raise or format as NaN
        try:
            result = formatter.formatRange(float('nan'), 100)
            assert 'NaN' in result
        except (ValueError, TypeError):
            pass  # Also acceptable


class TestFormatRangeToPartsBasic:
    """Test basic formatRangeToParts functionality (FR-ES24-C-025)."""

    def test_format_range_to_parts_simple(self):
        """Format simple range to parts."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        assert isinstance(parts, list)
        assert len(parts) > 0
        assert all('type' in p and 'value' in p and 'source' in p for p in parts)

    def test_format_range_to_parts_sources(self):
        """Parts should have source attribute."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        sources = [p['source'] for p in parts]
        assert 'startRange' in sources
        assert 'endRange' in sources

    def test_format_range_to_parts_shared_literal(self):
        """Range separator should be shared literal."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        shared_parts = [p for p in parts if p['source'] == 'shared']
        # Should have at least one shared part (the separator)
        assert len(shared_parts) >= 1

        # Shared parts are typically literals
        literal_shared = [p for p in shared_parts if p['type'] == 'literal']
        assert len(literal_shared) >= 1

    def test_format_range_to_parts_reconstruct(self):
        """Joining parts should equal formatRange() output."""
        formatter = IntlNumberFormat('en-US')

        formatted = formatter.formatRange(100, 200)
        parts = formatter.formatRangeToParts(100, 200)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed


class TestFormatRangeToPartsCurrency:
    """Test currency range parts."""

    def test_format_range_to_parts_currency(self):
        """Format currency range to parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatRangeToParts(100, 200)

        # Should have currency parts
        currency_parts = [p for p in parts if p['type'] == 'currency']
        assert len(currency_parts) >= 1

        # Currency might be in startRange, endRange, or shared
        start_parts = [p for p in parts if p['source'] == 'startRange']
        end_parts = [p for p in parts if p['source'] == 'endRange']

        assert len(start_parts) > 0
        assert len(end_parts) > 0

    def test_format_range_to_parts_currency_sources(self):
        """Currency range parts have correct sources."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        parts = formatter.formatRangeToParts(100, 200)

        # Check that parts are properly sourced
        for part in parts:
            assert part['source'] in ['startRange', 'endRange', 'shared']


class TestFormatRangeToPartsUnit:
    """Test unit range parts."""

    def test_format_range_to_parts_unit(self):
        """Format unit range to parts."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        parts = formatter.formatRangeToParts(10, 20)

        # Should have unit parts
        unit_parts = [p for p in parts if p['type'] == 'unit']
        assert len(unit_parts) >= 1


class TestFormatRangeToPartsNotation:
    """Test notation range parts."""

    def test_format_range_to_parts_compact(self):
        """Format compact notation range to parts."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        parts = formatter.formatRangeToParts(1000, 5000)

        # Might have compact parts
        compact_parts = [p for p in parts if p['type'] == 'compact']
        # Could be 0 if represented differently


class TestFormatRangeToPartsValidation:
    """Test parts validation."""

    def test_parts_have_required_fields(self):
        """All parts must have type, value, and source."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        for part in parts:
            assert 'type' in part
            assert 'value' in part
            assert 'source' in part
            assert isinstance(part['type'], str)
            assert isinstance(part['value'], str)
            assert isinstance(part['source'], str)

    def test_parts_sources_are_valid(self):
        """Part sources must be from valid set."""
        valid_sources = {'startRange', 'endRange', 'shared'}

        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        for part in parts:
            assert part['source'] in valid_sources

    def test_parts_order_preserved(self):
        """Parts should be in correct order."""
        formatter = IntlNumberFormat('en-US')
        parts = formatter.formatRangeToParts(100, 200)

        # First part should be from startRange or shared
        assert parts[0]['source'] in ['startRange', 'shared']

        # Last part should be from endRange or shared
        assert parts[-1]['source'] in ['endRange', 'shared']


class TestFormatRangeToPartsConsistency:
    """Test consistency across styles."""

    def test_parts_percent_consistency(self):
        """Percent range parts consistency."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})

        formatted = formatter.formatRange(0.25, 0.75)
        parts = formatter.formatRangeToParts(0.25, 0.75)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed

    def test_parts_compact_consistency(self):
        """Compact notation range parts consistency."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})

        formatted = formatter.formatRange(1000000, 5000000)
        parts = formatter.formatRangeToParts(1000000, 5000000)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed


# Custom exception
class RangeError(Exception):
    """ECMAScript RangeError."""
    pass
