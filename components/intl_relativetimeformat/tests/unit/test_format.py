"""
Unit tests for RelativeTimeFormat.format() method (FR-ES24-C-038).

Tests:
1. Format positive values (future)
2. Format negative values (past)
3. Format with different units
4. Format with zero
5. Format with large numbers
6. Format with decimal values
7. Invalid value (non-number)
8. Invalid unit
9. Unit normalization (singular/plural)
10. Locale-specific formatting
11. Style variations
12. Numeric mode variations
13. All supported units
14. Edge cases
15. Performance requirements
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatFormat:
    """Test RelativeTimeFormat.format() method (FR-ES24-C-038)."""

    def test_format_future_positive(self):
        """Test format with positive values (future)."""
        rtf = RelativeTimeFormat('en-US')

        assert rtf.format(1, 'day') == 'in 1 day'
        assert rtf.format(2, 'day') == 'in 2 days'
        assert rtf.format(5, 'hour') == 'in 5 hours'

    def test_format_past_negative(self):
        """Test format with negative values (past)."""
        rtf = RelativeTimeFormat('en-US')

        assert rtf.format(-1, 'day') == '1 day ago'
        assert rtf.format(-2, 'day') == '2 days ago'
        assert rtf.format(-5, 'hour') == '5 hours ago'

    def test_format_all_units(self):
        """Test format with all supported time units."""
        rtf = RelativeTimeFormat('en-US')

        assert rtf.format(1, 'second') == 'in 1 second'
        assert rtf.format(1, 'minute') == 'in 1 minute'
        assert rtf.format(1, 'hour') == 'in 1 hour'
        assert rtf.format(1, 'day') == 'in 1 day'
        assert rtf.format(1, 'week') == 'in 1 week'
        assert rtf.format(1, 'month') == 'in 1 month'
        assert rtf.format(1, 'quarter') == 'in 1 quarter'
        assert rtf.format(1, 'year') == 'in 1 year'

    def test_format_with_zero(self):
        """Test format with zero value."""
        rtf = RelativeTimeFormat('en-US')

        # Zero should format as "in 0 days" (numeric mode)
        assert rtf.format(0, 'day') == 'in 0 days'

    def test_format_with_large_numbers(self):
        """Test format with large numeric values."""
        rtf = RelativeTimeFormat('en-US')

        assert rtf.format(100, 'day') == 'in 100 days'
        assert rtf.format(-365, 'day') == '365 days ago'
        assert rtf.format(1000, 'year') == 'in 1,000 years'

    def test_format_with_decimal_values(self):
        """Test format with decimal/fractional values."""
        rtf = RelativeTimeFormat('en-US')

        # Should handle decimals
        result = rtf.format(1.5, 'day')
        assert 'day' in result
        # May format as "1.5" or "1" depending on implementation

    def test_format_unit_normalization_singular(self):
        """Test that singular and plural units work the same."""
        rtf = RelativeTimeFormat('en-US')

        # Both "day" and "days" should work
        result1 = rtf.format(2, 'day')
        result2 = rtf.format(2, 'days')
        assert result1 == result2 == 'in 2 days'

    def test_format_unit_normalization_all_units(self):
        """Test unit normalization for all units."""
        rtf = RelativeTimeFormat('en-US')

        units = [
            ('year', 'years'),
            ('quarter', 'quarters'),
            ('month', 'months'),
            ('week', 'weeks'),
            ('day', 'days'),
            ('hour', 'hours'),
            ('minute', 'minutes'),
            ('second', 'seconds')
        ]

        for singular, plural in units:
            result1 = rtf.format(2, singular)
            result2 = rtf.format(2, plural)
            assert result1 == result2

    def test_format_invalid_value_type(self):
        """Test format with non-number value raises TypeError."""
        rtf = RelativeTimeFormat('en-US')

        with pytest.raises(TypeError, match="Value must be a number"):
            rtf.format('not a number', 'day')

        with pytest.raises(TypeError, match="Value must be a number"):
            rtf.format(None, 'day')

    def test_format_invalid_unit(self):
        """Test format with invalid unit raises RangeError."""
        rtf = RelativeTimeFormat('en-US')

        with pytest.raises(RangeError, match="Invalid unit argument"):
            rtf.format(1, 'invalid')

        with pytest.raises(RangeError, match="Invalid unit argument"):
            rtf.format(1, 'decade')

    def test_format_locale_specific(self):
        """Test locale-specific formatting."""
        rtf_en = RelativeTimeFormat('en-US')
        rtf_es = RelativeTimeFormat('es-ES')
        rtf_fr = RelativeTimeFormat('fr-FR')

        # Different locales should produce different output
        result_en = rtf_en.format(-2, 'day')
        result_es = rtf_es.format(-2, 'day')
        result_fr = rtf_fr.format(-2, 'day')

        assert result_en == '2 days ago'
        assert 'día' in result_es  # Spanish
        assert 'jour' in result_fr  # French

    def test_format_with_style_long(self):
        """Test format with long style."""
        rtf = RelativeTimeFormat('en-US', {'style': 'long'})

        assert rtf.format(-2, 'hour') == '2 hours ago'
        assert rtf.format(2, 'hour') == 'in 2 hours'

    def test_format_with_style_short(self):
        """Test format with short style."""
        rtf = RelativeTimeFormat('en-US', {'style': 'short'})

        result = rtf.format(-2, 'hour')
        assert 'hr' in result or 'hour' in result
        assert 'ago' in result

    def test_format_with_style_narrow(self):
        """Test format with narrow style."""
        rtf = RelativeTimeFormat('en-US', {'style': 'narrow'})

        result = rtf.format(-2, 'hour')
        # Narrow should be shortest: "2h ago" or similar
        assert len(result) < 15
        assert 'ago' in result

    def test_format_numeric_always(self):
        """Test format with numeric='always'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'always'})

        # Always numeric, never "yesterday"
        assert rtf.format(-1, 'day') == '1 day ago'
        assert rtf.format(1, 'day') == 'in 1 day'
        assert rtf.format(0, 'day') == 'in 0 days'


# TypeError and RangeError imported from src
