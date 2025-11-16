"""
Unit tests for IntlDateTimeFormat.formatToParts() method.
Tests FR-ES24-C-011: formatToParts() returning array of parts with type and value.
"""

import pytest
from datetime import datetime, timezone
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestFormatToParts:
    """Test formatToParts() method."""

    def test_format_to_parts_basic(self):
        """Test basic formatToParts() functionality."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        assert isinstance(parts, list)
        assert len(parts) > 0

        # Check that parts have correct structure
        for part in parts:
            assert 'type' in part
            assert 'value' in part
            assert isinstance(part['type'], str)
            assert isinstance(part['value'], str)

    def test_format_to_parts_contains_month(self):
        """Test formatToParts() contains month part."""
        formatter = IntlDateTimeFormat('en-US', {
            'month': 'long'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        month_parts = [p for p in parts if p['type'] == 'month']
        assert len(month_parts) == 1
        assert month_parts[0]['value'] == 'January'

    def test_format_to_parts_contains_day(self):
        """Test formatToParts() contains day part."""
        formatter = IntlDateTimeFormat('en-US', {
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        day_parts = [p for p in parts if p['type'] == 'day']
        assert len(day_parts) == 1
        assert day_parts[0]['value'] == '15'

    def test_format_to_parts_contains_year(self):
        """Test formatToParts() contains year part."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        year_parts = [p for p in parts if p['type'] == 'year']
        assert len(year_parts) == 1
        assert year_parts[0]['value'] == '2024'

    def test_format_to_parts_contains_weekday(self):
        """Test formatToParts() contains weekday part."""
        formatter = IntlDateTimeFormat('en-US', {
            'weekday': 'long'
        })
        date = datetime(2024, 1, 15)  # Monday
        parts = formatter.formatToParts(date)

        weekday_parts = [p for p in parts if p['type'] == 'weekday']
        assert len(weekday_parts) == 1
        assert weekday_parts[0]['value'] == 'Monday'

    def test_format_to_parts_contains_hour(self):
        """Test formatToParts() contains hour part."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'hourCycle': 'h23'
        })
        date = datetime(2024, 1, 15, 14, 30)
        parts = formatter.formatToParts(date)

        hour_parts = [p for p in parts if p['type'] == 'hour']
        assert len(hour_parts) == 1
        assert hour_parts[0]['value'] == '14'

    def test_format_to_parts_contains_minute(self):
        """Test formatToParts() contains minute part."""
        formatter = IntlDateTimeFormat('en-US', {
            'minute': '2-digit'
        })
        date = datetime(2024, 1, 15, 14, 30)
        parts = formatter.formatToParts(date)

        minute_parts = [p for p in parts if p['type'] == 'minute']
        assert len(minute_parts) == 1
        assert minute_parts[0]['value'] == '30'

    def test_format_to_parts_contains_second(self):
        """Test formatToParts() contains second part."""
        formatter = IntlDateTimeFormat('en-US', {
            'second': '2-digit'
        })
        date = datetime(2024, 1, 15, 14, 30, 45)
        parts = formatter.formatToParts(date)

        second_parts = [p for p in parts if p['type'] == 'second']
        assert len(second_parts) == 1
        assert second_parts[0]['value'] == '45'

    def test_format_to_parts_contains_day_period(self):
        """Test formatToParts() contains dayPeriod part."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'dayPeriod': 'short',
            'hourCycle': 'h12'
        })
        date = datetime(2024, 1, 15, 14, 30)
        parts = formatter.formatToParts(date)

        day_period_parts = [p for p in parts if p['type'] == 'dayPeriod']
        assert len(day_period_parts) >= 1

    def test_format_to_parts_contains_literals(self):
        """Test formatToParts() contains literal parts (separators)."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'numeric',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        literal_parts = [p for p in parts if p['type'] == 'literal']
        # Should have separators like "/" or "-"
        assert len(literal_parts) > 0

    def test_format_to_parts_with_timezone_name(self):
        """Test formatToParts() contains timeZoneName part."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'timeZoneName': 'long'
        })
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        parts = formatter.formatToParts(date)

        tz_parts = [p for p in parts if p['type'] == 'timeZoneName']
        assert len(tz_parts) >= 1
        assert 'Eastern' in tz_parts[0]['value']

    def test_format_to_parts_with_era(self):
        """Test formatToParts() contains era part."""
        formatter = IntlDateTimeFormat('en-US', {
            'era': 'short',
            'year': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        era_parts = [p for p in parts if p['type'] == 'era']
        assert len(era_parts) == 1
        assert 'AD' in era_parts[0]['value']

    def test_format_to_parts_parts_order(self):
        """Test formatToParts() parts are in correct order."""
        formatter = IntlDateTimeFormat('en-US', {
            'month': 'long',
            'day': 'numeric',
            'year': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatToParts(date)

        # Extract non-literal parts
        non_literal = [p for p in parts if p['type'] != 'literal']

        # In US format: month, day, year
        assert non_literal[0]['type'] == 'month'
        assert non_literal[1]['type'] == 'day'
        assert non_literal[2]['type'] == 'year'

    def test_format_to_parts_different_locale_order(self):
        """Test formatToParts() respects locale ordering."""
        date = datetime(2024, 1, 15)

        # US format: month/day/year
        us_formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'numeric',
            'day': 'numeric'
        })
        us_parts = us_formatter.formatToParts(date)
        us_types = [p['type'] for p in us_parts if p['type'] != 'literal']
        assert us_types == ['month', 'day', 'year']

        # ISO format: year-month-day
        iso_formatter = IntlDateTimeFormat('en-CA', {
            'year': 'numeric',
            'month': 'numeric',
            'day': 'numeric'
        })
        iso_parts = iso_formatter.formatToParts(date)
        iso_types = [p['type'] for p in iso_parts if p['type'] != 'literal']
        assert iso_types == ['year', 'month', 'day']

    def test_format_to_parts_no_date_uses_current(self):
        """Test formatToParts() with no argument uses current time."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric'
        })
        parts = formatter.formatToParts()

        assert isinstance(parts, list)
        assert len(parts) > 0

    def test_format_to_parts_invalid_date_raises_error(self):
        """Test formatToParts() with invalid date raises TypeError."""
        formatter = IntlDateTimeFormat('en-US')
        with pytest.raises(TypeError, match='Invalid date'):
            formatter.formatToParts('invalid')

    def test_format_to_parts_fractional_seconds(self):
        """Test formatToParts() with fractionalSecondDigits."""
        formatter = IntlDateTimeFormat('en-US', {
            'second': 'numeric',
            'fractionalSecondDigits': 3
        })
        date = datetime(2024, 1, 15, 14, 30, 45, 123000)
        parts = formatter.formatToParts(date)

        # Should have fractionalSecond part
        frac_parts = [p for p in parts if p['type'] == 'fractionalSecond']
        assert len(frac_parts) == 1
        assert '123' in frac_parts[0]['value']
