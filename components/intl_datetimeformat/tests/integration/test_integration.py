"""
Integration tests for IntlDateTimeFormat.
Tests end-to-end functionality and real-world usage scenarios.
"""

import pytest
from datetime import datetime, timezone
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""

    def test_basic_date_formatting_workflow(self):
        """Test basic date formatting workflow."""
        # Create formatter
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })

        # Format a date
        date = datetime(2024, 1, 15)
        result = formatter.format(date)

        assert 'January' in result
        assert '15' in result
        assert '2024' in result

    def test_multi_locale_formatting(self):
        """Test formatting same date in multiple locales."""
        date = datetime(2024, 1, 15, 14, 30)

        # US English
        us_formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'hour': 'numeric',
            'minute': '2-digit'
        })
        us_result = us_formatter.format(date)
        assert 'January' in us_result

        # German
        de_formatter = IntlDateTimeFormat('de-DE', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'hour': 'numeric',
            'minute': '2-digit'
        })
        de_result = de_formatter.format(date)
        assert isinstance(de_result, str)

        # Japanese
        ja_formatter = IntlDateTimeFormat('ja-JP', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })
        ja_result = ja_formatter.format(date)
        assert isinstance(ja_result, str)

    def test_timezone_conversion_workflow(self):
        """Test complete time zone conversion workflow."""
        # UTC time
        utc_time = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Format in different time zones
        formatters = {
            'UTC': IntlDateTimeFormat('en-US', {
                'timeZone': 'UTC',
                'timeStyle': 'full',
                'dateStyle': 'full'
            }),
            'New York': IntlDateTimeFormat('en-US', {
                'timeZone': 'America/New_York',
                'timeStyle': 'full',
                'dateStyle': 'full'
            }),
            'Tokyo': IntlDateTimeFormat('ja-JP', {
                'timeZone': 'Asia/Tokyo',
                'timeStyle': 'full',
                'dateStyle': 'full'
            })
        }

        results = {}
        for name, formatter in formatters.items():
            results[name] = formatter.format(utc_time)
            assert isinstance(results[name], str)
            assert len(results[name]) > 0

    def test_calendar_conversion_workflow(self):
        """Test complete calendar conversion workflow."""
        date = datetime(2024, 1, 15)

        # Format in different calendars
        calendars = {
            'Gregorian': IntlDateTimeFormat('en-US', {
                'calendar': 'gregory',
                'year': 'numeric',
                'month': 'long',
                'day': 'numeric',
                'era': 'short'
            }),
            'Buddhist': IntlDateTimeFormat('th-TH', {
                'calendar': 'buddhist',
                'year': 'numeric',
                'month': 'long',
                'day': 'numeric'
            }),
            'Japanese': IntlDateTimeFormat('ja-JP', {
                'calendar': 'japanese',
                'year': 'numeric',
                'month': 'long',
                'day': 'numeric',
                'era': 'long'
            })
        }

        for name, formatter in calendars.items():
            result = formatter.format(date)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_date_range_formatting_workflow(self):
        """Test complete date range formatting workflow."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })

        # Different range scenarios
        ranges = {
            'Same day': (
                datetime(2024, 1, 15, 10, 0),
                datetime(2024, 1, 15, 14, 0)
            ),
            'Same month': (
                datetime(2024, 1, 15),
                datetime(2024, 1, 20)
            ),
            'Different months': (
                datetime(2024, 1, 15),
                datetime(2024, 3, 20)
            ),
            'Different years': (
                datetime(2024, 1, 15),
                datetime(2025, 3, 20)
            )
        }

        for scenario, (start, end) in ranges.items():
            result = formatter.formatRange(start, end)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_format_to_parts_workflow(self):
        """Test complete formatToParts workflow."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'weekday': 'long'
        })

        date = datetime(2024, 1, 15)  # Monday
        parts = formatter.formatToParts(date)

        # Verify structure
        assert isinstance(parts, list)
        part_types = [p['type'] for p in parts if p['type'] != 'literal']

        assert 'weekday' in part_types
        assert 'month' in part_types
        assert 'day' in part_types
        assert 'year' in part_types

        # Verify can reconstruct formatted string
        reconstructed = ''.join(p['value'] for p in parts)
        full_formatted = formatter.format(date)
        assert reconstructed == full_formatted

    def test_dst_handling_workflow(self):
        """Test DST handling in real scenarios."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York',
            'dateStyle': 'full',
            'timeStyle': 'full'
        })

        # Test dates around DST transitions
        # Spring forward (March)
        before_spring = datetime(2024, 3, 10, 6, 0, 0, tzinfo=timezone.utc)
        after_spring = datetime(2024, 3, 10, 7, 0, 0, tzinfo=timezone.utc)

        result_before = formatter.format(before_spring)
        result_after = formatter.format(after_spring)

        assert isinstance(result_before, str)
        assert isinstance(result_after, str)

        # Fall back (November)
        before_fall = datetime(2024, 11, 3, 5, 0, 0, tzinfo=timezone.utc)
        after_fall = datetime(2024, 11, 3, 7, 0, 0, tzinfo=timezone.utc)

        result_before_fall = formatter.format(before_fall)
        result_after_fall = formatter.format(after_fall)

        assert isinstance(result_before_fall, str)
        assert isinstance(result_after_fall, str)

    def test_performance_formatting_many_dates(self):
        """Test performance when formatting many dates."""
        import time

        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })

        dates = [datetime(2024, 1, i) for i in range(1, 29)]

        start_time = time.time()
        results = [formatter.format(date) for date in dates]
        elapsed = time.time() - start_time

        # Should format 28 dates quickly (< 50ms)
        assert elapsed < 0.05
        assert len(results) == 28
        assert all(isinstance(r, str) for r in results)

    def test_resolved_options_consistency(self):
        """Test resolvedOptions consistency across operations."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'timeZone': 'America/New_York',
            'calendar': 'gregory'
        })

        # Get resolved options before and after formatting
        options_before = formatter.resolvedOptions()

        formatter.format(datetime(2024, 1, 15))
        formatter.formatToParts(datetime(2024, 1, 15))
        formatter.formatRange(datetime(2024, 1, 15), datetime(2024, 1, 20))

        options_after = formatter.resolvedOptions()

        # Options should remain consistent
        assert options_before == options_after

    def test_edge_case_leap_year(self):
        """Test formatting leap year dates."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric'
        })

        # February 29, 2024 (leap year)
        leap_date = datetime(2024, 2, 29)
        result = formatter.format(leap_date)

        assert 'February' in result
        assert '29' in result
        assert '2024' in result

    def test_edge_case_year_boundaries(self):
        """Test formatting dates at year boundaries."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': 'numeric',
            'hour': 'numeric',
            'minute': '2-digit',
            'timeZone': 'America/New_York'
        })

        # New Year's Eve/Day across time zones
        nye_utc = datetime(2024, 1, 1, 4, 0, 0, tzinfo=timezone.utc)
        result = formatter.format(nye_utc)

        # Should be Dec 31, 2023 at 11 PM EST
        assert isinstance(result, str)

    def test_multiple_formatters_independence(self):
        """Test multiple formatter instances are independent."""
        date = datetime(2024, 1, 15)

        formatter1 = IntlDateTimeFormat('en-US', {'dateStyle': 'full'})
        formatter2 = IntlDateTimeFormat('fr-FR', {'dateStyle': 'full'})

        result1 = formatter1.format(date)
        result2 = formatter2.format(date)

        # Results should be different (different locales)
        assert result1 != result2
        assert 'Monday' in result1  # English
        assert isinstance(result2, str)  # French
