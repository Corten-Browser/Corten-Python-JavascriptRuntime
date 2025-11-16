"""
Unit tests for IntlDateTimeFormat.formatRange() and formatRangeToParts() methods.
Tests FR-ES24-C-012: formatRange() for date range formatting.
Tests FR-ES24-C-013: formatRangeToParts() with source indicators.
"""

import pytest
from datetime import datetime, timezone
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestFormatRange:
    """Test formatRange() method."""

    def test_format_range_same_day_different_times(self):
        """Test formatRange() for same day, different times."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'hour': 'numeric',
            'minute': 'numeric'
        })
        start = datetime(2024, 1, 15, 10, 0)
        end = datetime(2024, 1, 15, 14, 30)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        assert 'January 15' in result
        assert '2024' in result
        # Should show both times
        assert '10' in result or '10:00' in result
        assert '14' in result or '14:30' in result or '2:30' in result

    def test_format_range_different_days_same_month(self):
        """Test formatRange() for different days, same month."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        assert 'January' in result
        assert '15' in result
        assert '20' in result
        assert '2024' in result
        # Should optimize: "January 15 – 20, 2024" not "January 15, 2024 – January 20, 2024"

    def test_format_range_different_months_same_year(self):
        """Test formatRange() for different months, same year."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 3, 20)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        assert 'January' in result
        assert 'March' in result
        assert '15' in result
        assert '20' in result
        assert '2024' in result

    def test_format_range_different_years(self):
        """Test formatRange() for different years."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2025, 3, 20)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        assert '2024' in result
        assert '2025' in result
        assert 'January' in result
        assert 'March' in result

    def test_format_range_start_after_end_raises_error(self):
        """Test formatRange() raises error when start > end."""
        formatter = IntlDateTimeFormat('en-US')
        start = datetime(2024, 1, 20)
        end = datetime(2024, 1, 15)

        with pytest.raises(ValueError, match='startDate.*endDate'):
            formatter.formatRange(start, end)

    def test_format_range_same_date_returns_single_format(self):
        """Test formatRange() with same date returns single formatted date."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        result = formatter.formatRange(date, date)

        assert isinstance(result, str)
        assert 'January 15, 2024' in result

    def test_format_range_with_timezone(self):
        """Test formatRange() with time zone conversion."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'dateStyle': 'short',
            'timeStyle': 'short'
        })
        start = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_range_crossing_dst(self):
        """Test formatRange() crossing DST boundary."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'dateStyle': 'short',
            'timeStyle': 'full'
        })
        # Before DST
        start = datetime(2024, 3, 10, 6, 0, 0, tzinfo=timezone.utc)
        # After DST
        end = datetime(2024, 3, 10, 7, 0, 0, tzinfo=timezone.utc)
        result = formatter.formatRange(start, end)

        assert isinstance(result, str)
        # Should show correct time zone names

    def test_format_range_invalid_start_date_raises_error(self):
        """Test formatRange() with invalid start date raises TypeError."""
        formatter = IntlDateTimeFormat('en-US')
        with pytest.raises(TypeError, match='Invalid date'):
            formatter.formatRange('invalid', datetime(2024, 1, 15))

    def test_format_range_invalid_end_date_raises_error(self):
        """Test formatRange() with invalid end date raises TypeError."""
        formatter = IntlDateTimeFormat('en-US')
        with pytest.raises(TypeError, match='Invalid date'):
            formatter.formatRange(datetime(2024, 1, 15), 'invalid')


class TestFormatRangeToParts:
    """Test formatRangeToParts() method."""

    def test_format_range_to_parts_basic(self):
        """Test basic formatRangeToParts() functionality."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        parts = formatter.formatRangeToParts(start, end)

        assert isinstance(parts, list)
        assert len(parts) > 0

        # Check structure
        for part in parts:
            assert 'type' in part
            assert 'value' in part
            assert 'source' in part
            assert part['source'] in ['startRange', 'endRange', 'shared']

    def test_format_range_to_parts_has_start_range_parts(self):
        """Test formatRangeToParts() has startRange parts."""
        formatter = IntlDateTimeFormat('en-US', {
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        parts = formatter.formatRangeToParts(start, end)

        start_parts = [p for p in parts if p['source'] == 'startRange']
        assert len(start_parts) > 0
        # Start day should be 15
        day_parts = [p for p in start_parts if p['type'] == 'day']
        assert any(p['value'] == '15' for p in day_parts)

    def test_format_range_to_parts_has_end_range_parts(self):
        """Test formatRangeToParts() has endRange parts."""
        formatter = IntlDateTimeFormat('en-US', {
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        parts = formatter.formatRangeToParts(start, end)

        end_parts = [p for p in parts if p['source'] == 'endRange']
        assert len(end_parts) > 0
        # End day should be 20
        day_parts = [p for p in end_parts if p['type'] == 'day']
        assert any(p['value'] == '20' for p in day_parts)

    def test_format_range_to_parts_has_shared_parts(self):
        """Test formatRangeToParts() has shared parts."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        parts = formatter.formatRangeToParts(start, end)

        shared_parts = [p for p in parts if p['source'] == 'shared']
        assert len(shared_parts) > 0
        # Month and year should be shared
        month_parts = [p for p in shared_parts if p['type'] == 'month']
        year_parts = [p for p in shared_parts if p['type'] == 'year']
        assert len(month_parts) > 0 or len(year_parts) > 0

    def test_format_range_to_parts_shared_month_and_year(self):
        """Test formatRangeToParts() shares month and year for same-month range."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 1, 20)
        parts = formatter.formatRangeToParts(start, end)

        # Month should be shared
        month_parts = [p for p in parts if p['type'] == 'month']
        shared_months = [p for p in month_parts if p['source'] == 'shared']
        assert len(shared_months) > 0

        # Year should be shared
        year_parts = [p for p in parts if p['type'] == 'year']
        shared_years = [p for p in year_parts if p['source'] == 'shared']
        assert len(shared_years) > 0

    def test_format_range_to_parts_different_months(self):
        """Test formatRangeToParts() for different months."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        start = datetime(2024, 1, 15)
        end = datetime(2024, 3, 20)
        parts = formatter.formatRangeToParts(start, end)

        # Should have months in both start and end
        month_parts = [p for p in parts if p['type'] == 'month']
        assert len(month_parts) >= 2

    def test_format_range_to_parts_same_date(self):
        """Test formatRangeToParts() with same date."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        date = datetime(2024, 1, 15)
        parts = formatter.formatRangeToParts(date, date)

        assert isinstance(parts, list)
        # All parts should be shared
        assert all(p['source'] == 'shared' for p in parts)

    def test_format_range_to_parts_start_after_end_raises_error(self):
        """Test formatRangeToParts() raises error when start > end."""
        formatter = IntlDateTimeFormat('en-US')
        start = datetime(2024, 1, 20)
        end = datetime(2024, 1, 15)

        with pytest.raises(ValueError, match='startDate.*endDate'):
            formatter.formatRangeToParts(start, end)

    def test_format_range_to_parts_invalid_dates_raise_error(self):
        """Test formatRangeToParts() with invalid dates raises TypeError."""
        formatter = IntlDateTimeFormat('en-US')

        with pytest.raises(TypeError, match='Invalid date'):
            formatter.formatRangeToParts('invalid', datetime(2024, 1, 15))

        with pytest.raises(TypeError, match='Invalid date'):
            formatter.formatRangeToParts(datetime(2024, 1, 15), 'invalid')
