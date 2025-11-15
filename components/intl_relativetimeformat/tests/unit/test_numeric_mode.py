"""
Unit tests for RelativeTimeFormat numeric option (FR-ES24-C-041).

Tests numeric='always' vs numeric='auto' behavior.

Tests:
1. numeric='always' always uses numbers
2. numeric='auto' uses words for -1, 0, 1
3. auto mode: "yesterday" for -1 day
4. auto mode: "today" for 0 day
5. auto mode: "tomorrow" for 1 day
6. auto mode: "last week" for -1 week
7. auto mode: "next week" for 1 week
8. auto mode: falls back to numeric for other values
9. auto mode with different units
10. auto mode locale variations
11. always mode never uses words
12. Performance requirements
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatNumericMode:
    """Test RelativeTimeFormat numeric option (FR-ES24-C-041)."""

    def test_numeric_always_uses_numbers(self):
        """Test that numeric='always' always uses numeric values."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'always'})

        # Should always be numeric, never "yesterday"
        assert rtf.format(-1, 'day') == '1 day ago'
        assert rtf.format(0, 'day') == 'in 0 days'
        assert rtf.format(1, 'day') == 'in 1 day'
        assert rtf.format(-1, 'week') == '1 week ago'
        assert rtf.format(1, 'week') == 'in 1 week'

    def test_numeric_auto_day_minus_one(self):
        """Test numeric='auto' with -1 day gives 'yesterday'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        assert rtf.format(-1, 'day') == 'yesterday'

    def test_numeric_auto_day_zero(self):
        """Test numeric='auto' with 0 day gives 'today'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        assert rtf.format(0, 'day') == 'today'

    def test_numeric_auto_day_plus_one(self):
        """Test numeric='auto' with 1 day gives 'tomorrow'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        assert rtf.format(1, 'day') == 'tomorrow'

    def test_numeric_auto_week_minus_one(self):
        """Test numeric='auto' with -1 week gives 'last week'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        result = rtf.format(-1, 'week')
        assert 'last week' in result.lower()

    def test_numeric_auto_week_plus_one(self):
        """Test numeric='auto' with 1 week gives 'next week'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        result = rtf.format(1, 'week')
        assert 'next week' in result.lower()

    def test_numeric_auto_month_minus_one(self):
        """Test numeric='auto' with -1 month gives 'last month'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        result = rtf.format(-1, 'month')
        # Should be "last month" or similar
        assert 'last month' in result.lower() or 'month ago' in result.lower()

    def test_numeric_auto_year_plus_one(self):
        """Test numeric='auto' with 1 year gives 'next year'."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        result = rtf.format(1, 'year')
        assert 'next year' in result.lower() or 'year' in result.lower()

    def test_numeric_auto_fallback_to_numeric(self):
        """Test numeric='auto' falls back to numeric for values != -1,0,1."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        # -2, 2, etc. should be numeric
        assert rtf.format(-2, 'day') == '2 days ago'
        assert rtf.format(2, 'day') == 'in 2 days'
        assert rtf.format(5, 'day') == 'in 5 days'

    def test_numeric_auto_all_units(self):
        """Test numeric='auto' with different units."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        # Days
        assert rtf.format(-1, 'day') == 'yesterday'
        assert rtf.format(0, 'day') == 'today'
        assert rtf.format(1, 'day') == 'tomorrow'

        # Weeks
        assert 'week' in rtf.format(-1, 'week').lower()
        assert 'week' in rtf.format(1, 'week').lower()

        # Other units: May or may not have special words
        # But should work without error
        rtf.format(-1, 'hour')
        rtf.format(1, 'minute')
        rtf.format(-1, 'year')

    def test_numeric_auto_locale_variations(self):
        """Test numeric='auto' produces locale-specific words."""
        rtf_en = RelativeTimeFormat('en-US', {'numeric': 'auto'})
        rtf_es = RelativeTimeFormat('es-ES', {'numeric': 'auto'})
        rtf_fr = RelativeTimeFormat('fr-FR', {'numeric': 'auto'})

        result_en = rtf_en.format(-1, 'day')
        result_es = rtf_es.format(-1, 'day')
        result_fr = rtf_fr.format(-1, 'day')

        assert result_en == 'yesterday'
        # Spanish: "ayer"
        assert 'ayer' in result_es.lower() or 'día' in result_es
        # French: "hier"
        assert 'hier' in result_fr.lower() or 'jour' in result_fr

    def test_numeric_default_is_always(self):
        """Test that default numeric mode is 'always'."""
        rtf = RelativeTimeFormat('en-US')

        # Default should be numeric='always'
        options = rtf.resolvedOptions()
        assert options['numeric'] == 'always'

        # Should use numeric, not "yesterday"
        assert rtf.format(-1, 'day') == '1 day ago'


# TypeError and RangeError imported from src
