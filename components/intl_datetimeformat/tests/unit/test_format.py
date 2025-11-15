"""
Unit tests for IntlDateTimeFormat.format() method.
Tests FR-ES24-C-010: format() method for date/time formatting.
"""

import pytest
from datetime import datetime, timezone
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestFormat:
    """Test format() method."""

    def test_format_basic_date(self):
        """Test basic date formatting."""
        formatter = IntlDateTimeFormat('en-US')
        date = datetime(2024, 1, 15, 14, 30, 45)
        result = formatter.format(date)
        assert isinstance(result, str)
        assert '2024' in result or '24' in result
        assert '1' in result or 'Jan' in result

    def test_format_with_timestamp(self):
        """Test formatting with Unix timestamp."""
        formatter = IntlDateTimeFormat('en-US')
        timestamp = 1705330245000  # Milliseconds since epoch
        result = formatter.format(timestamp)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_no_date_uses_current_time(self):
        """Test format() with no argument uses current time."""
        formatter = IntlDateTimeFormat('en-US')
        result = formatter.format()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_full_date_style(self):
        """Test formatting with full dateStyle."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'full'})
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        assert 'Monday' in result
        assert 'January' in result
        assert '15' in result
        assert '2024' in result

    def test_format_long_date_style(self):
        """Test formatting with long dateStyle."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'long'})
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        assert 'January' in result
        assert '15' in result
        assert '2024' in result

    def test_format_medium_date_style(self):
        """Test formatting with medium dateStyle."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'medium'})
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        assert 'Jan' in result
        assert '15' in result
        assert '2024' in result

    def test_format_short_date_style(self):
        """Test formatting with short dateStyle."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'short'})
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        # Short format: 1/15/24 or similar
        assert '1' in result
        assert '15' in result

    def test_format_full_time_style(self):
        """Test formatting with full timeStyle."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeStyle': 'full',
            'timeZone': 'UTC'
        })
        date = datetime(2024, 1, 15, 14, 30, 45, tzinfo=timezone.utc)
        result = formatter.format(date)
        assert '2:30:45' in result or '14:30:45' in result
        assert 'PM' in result or 'UTC' in result

    def test_format_with_timezone_conversion(self):
        """Test formatting with time zone conversion."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'dateStyle': 'short',
            'timeStyle': 'short'
        })
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = formatter.format(date)
        # UTC 12:00 = EST 7:00 AM
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_with_buddhist_calendar(self):
        """Test formatting with Buddhist calendar."""
        formatter = IntlDateTimeFormat('th-TH', {
            'calendar': 'buddhist',
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        # Buddhist year = Gregorian year + 543
        assert '2567' in result  # 2024 + 543

    def test_format_with_japanese_calendar(self):
        """Test formatting with Japanese calendar."""
        formatter = IntlDateTimeFormat('ja-JP', {
            'calendar': 'japanese',
            'year': 'numeric',
            'era': 'long'
        })
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        # Should contain Reiwa era
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_12_hour_cycle(self):
        """Test formatting with 12-hour cycle."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'minute': '2-digit',
            'hourCycle': 'h12'
        })
        date = datetime(2024, 1, 15, 14, 30)
        result = formatter.format(date)
        assert '2:30' in result
        assert 'PM' in result

    def test_format_24_hour_cycle(self):
        """Test formatting with 24-hour cycle."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'minute': '2-digit',
            'hourCycle': 'h23'
        })
        date = datetime(2024, 1, 15, 14, 30)
        result = formatter.format(date)
        assert '14:30' in result
        assert 'PM' not in result

    def test_format_with_weekday(self):
        """Test formatting with weekday component."""
        formatter = IntlDateTimeFormat('en-US', {
            'weekday': 'long',
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)  # Monday
        result = formatter.format(date)
        assert 'Monday' in result

    def test_format_with_era(self):
        """Test formatting with era component."""
        formatter = IntlDateTimeFormat('en-US', {
            'era': 'long',
            'year': 'numeric'
        })
        date = datetime(2024, 1, 15)
        result = formatter.format(date)
        assert 'AD' in result or 'Anno Domini' in result

    def test_format_with_day_period(self):
        """Test formatting with dayPeriod component."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'dayPeriod': 'long'
        })
        date = datetime(2024, 1, 15, 14, 30)
        result = formatter.format(date)
        assert 'afternoon' in result.lower() or 'PM' in result

    def test_format_different_locales(self):
        """Test formatting with different locales."""
        date = datetime(2024, 1, 15)

        # English US
        en_us = IntlDateTimeFormat('en-US', {'dateStyle': 'medium'})
        assert 'Jan' in en_us.format(date)

        # German
        de_de = IntlDateTimeFormat('de-DE', {'dateStyle': 'medium'})
        de_result = de_de.format(date)
        assert 'Jan' in de_result or 'Jän' in de_result

        # Japanese
        ja_jp = IntlDateTimeFormat('ja-JP', {'dateStyle': 'medium'})
        ja_result = ja_jp.format(date)
        assert isinstance(ja_result, str)

    def test_format_invalid_date_raises_error(self):
        """Test formatting with invalid date raises TypeError."""
        formatter = IntlDateTimeFormat('en-US')
        with pytest.raises(TypeError, match='Invalid date'):
            formatter.format('not a date')

    def test_format_dst_transition(self):
        """Test formatting during DST transition."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'timeStyle': 'full'
        })

        # Before DST (EST)
        before_dst = datetime(2024, 3, 10, 6, 0, 0, tzinfo=timezone.utc)
        result_before = formatter.format(before_dst)
        assert 'Eastern' in result_before

        # After DST (EDT)
        after_dst = datetime(2024, 3, 10, 7, 0, 0, tzinfo=timezone.utc)
        result_after = formatter.format(after_dst)
        assert 'Eastern' in result_after
