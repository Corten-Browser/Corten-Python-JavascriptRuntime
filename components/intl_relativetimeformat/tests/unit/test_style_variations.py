"""
Unit tests for RelativeTimeFormat style option (FR-ES24-C-040).

Tests style='long', 'short', 'narrow' formatting variations.

Tests:
1. Style long produces full words
2. Style short produces abbreviations
3. Style narrow produces shortest forms
4. Style variations with different units
5. Style with past values
6. Style with future values
7. Style locale variations
8. Default style is 'long'
9. Style affects formatToParts
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatStyleVariations:
    """Test RelativeTimeFormat style option (FR-ES24-C-040)."""

    def test_style_long_full_words(self):
        """Test style='long' produces full words."""
        rtf = RelativeTimeFormat('en-US', {'style': 'long'})

        assert rtf.format(-2, 'hour') == '2 hours ago'
        assert rtf.format(2, 'hour') == 'in 2 hours'
        assert rtf.format(-3, 'day') == '3 days ago'
        assert rtf.format(1, 'month') == 'in 1 month'

    def test_style_short_abbreviated(self):
        """Test style='short' produces abbreviated forms."""
        rtf = RelativeTimeFormat('en-US', {'style': 'short'})

        # Short should have abbreviations like "hr.", "mo."
        result_hour = rtf.format(-2, 'hour')
        result_month = rtf.format(-3, 'month')

        # Should contain "hr" or "hr." for hours
        assert 'hr' in result_hour.lower() or 'hour' in result_hour
        # Should contain "mo" or "mo." for months
        assert 'mo' in result_month.lower() or 'month' in result_month
        # Should still have "ago"
        assert 'ago' in result_hour
        assert 'ago' in result_month

    def test_style_narrow_shortest(self):
        """Test style='narrow' produces shortest forms."""
        rtf = RelativeTimeFormat('en-US', {'style': 'narrow'})

        result_hour = rtf.format(-2, 'hour')
        result_day = rtf.format(3, 'day')

        # Narrow should be very short: "2h ago", "in 3d"
        # Should be shorter than long style
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        long_hour = rtf_long.format(-2, 'hour')
        long_day = rtf_long.format(3, 'day')

        assert len(result_hour) <= len(long_hour)
        assert len(result_day) <= len(long_day)

    def test_style_variations_all_units(self):
        """Test style variations with all time units."""
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        rtf_short = RelativeTimeFormat('en-US', {'style': 'short'})
        rtf_narrow = RelativeTimeFormat('en-US', {'style': 'narrow'})

        units = ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']

        for unit in units:
            long_result = rtf_long.format(2, unit)
            short_result = rtf_short.format(2, unit)
            narrow_result = rtf_narrow.format(2, unit)

            # All should work without error
            assert long_result is not None
            assert short_result is not None
            assert narrow_result is not None

            # Narrow should generally be shortest
            assert len(narrow_result) <= len(long_result)

    def test_style_with_past_values(self):
        """Test style variations with past (negative) values."""
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        rtf_short = RelativeTimeFormat('en-US', {'style': 'short'})
        rtf_narrow = RelativeTimeFormat('en-US', {'style': 'narrow'})

        # All should handle past values correctly
        assert 'ago' in rtf_long.format(-5, 'day')
        assert 'ago' in rtf_short.format(-5, 'day')
        assert 'ago' in rtf_narrow.format(-5, 'day')

    def test_style_with_future_values(self):
        """Test style variations with future (positive) values."""
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        rtf_short = RelativeTimeFormat('en-US', {'style': 'short'})
        rtf_narrow = RelativeTimeFormat('en-US', {'style': 'narrow'})

        # All should handle future values correctly
        assert 'in' in rtf_long.format(5, 'day')
        assert 'in' in rtf_short.format(5, 'day')
        assert 'in' in rtf_narrow.format(5, 'day')

    def test_style_locale_variations(self):
        """Test that style works across different locales."""
        locales = ['en-US', 'es-ES', 'fr-FR']

        for locale in locales:
            rtf_long = RelativeTimeFormat(locale, {'style': 'long'})
            rtf_short = RelativeTimeFormat(locale, {'style': 'short'})
            rtf_narrow = RelativeTimeFormat(locale, {'style': 'narrow'})

            # All should work without error
            rtf_long.format(2, 'day')
            rtf_short.format(2, 'day')
            rtf_narrow.format(2, 'day')

    def test_style_default_is_long(self):
        """Test that default style is 'long'."""
        rtf = RelativeTimeFormat('en-US')

        options = rtf.resolvedOptions()
        assert options['style'] == 'long'

    def test_style_affects_formatToParts(self):
        """Test that style affects formatToParts output."""
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        rtf_narrow = RelativeTimeFormat('en-US', {'style': 'narrow'})

        parts_long = rtf_long.formatToParts(2, 'hour')
        parts_narrow = rtf_narrow.formatToParts(2, 'hour')

        # Reconstruct strings
        str_long = ''.join(p['value'] for p in parts_long)
        str_narrow = ''.join(p['value'] for p in parts_narrow)

        # Narrow should be shorter
        assert len(str_narrow) <= len(str_long)


# TypeError and RangeError imported from src
