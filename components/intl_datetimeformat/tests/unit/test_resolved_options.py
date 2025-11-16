"""
Unit tests for IntlDateTimeFormat.resolvedOptions() method.
Tests FR-ES24-C-020: resolvedOptions() returning resolved locale and options.
"""

import pytest
from datetime import datetime
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestResolvedOptions:
    """Test resolvedOptions() method."""

    def test_resolved_options_returns_dict(self):
        """Test resolvedOptions() returns a dictionary."""
        formatter = IntlDateTimeFormat('en-US')
        options = formatter.resolvedOptions()

        assert isinstance(options, dict)

    def test_resolved_options_contains_locale(self):
        """Test resolvedOptions() contains locale."""
        formatter = IntlDateTimeFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'locale' in options
        assert options['locale'] == 'en-US'

    def test_resolved_options_contains_calendar(self):
        """Test resolvedOptions() contains calendar."""
        formatter = IntlDateTimeFormat('en-US', {'calendar': 'gregory'})
        options = formatter.resolvedOptions()

        assert 'calendar' in options
        assert options['calendar'] == 'gregory'

    def test_resolved_options_contains_numbering_system(self):
        """Test resolvedOptions() contains numberingSystem."""
        formatter = IntlDateTimeFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'numberingSystem' in options
        assert isinstance(options['numberingSystem'], str)

    def test_resolved_options_contains_timezone(self):
        """Test resolvedOptions() contains timeZone."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York'
        })
        options = formatter.resolvedOptions()

        assert 'timeZone' in options
        assert options['timeZone'] == 'America/New_York'

    def test_resolved_options_default_timezone(self):
        """Test resolvedOptions() has default time zone if not specified."""
        formatter = IntlDateTimeFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'timeZone' in options
        # Default is system time zone (likely UTC in tests)
        assert isinstance(options['timeZone'], str)

    def test_resolved_options_contains_component_options(self):
        """Test resolvedOptions() contains component options."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': '2-digit'
        })
        options = formatter.resolvedOptions()

        assert options['year'] == 'numeric'
        assert options['month'] == 'long'
        assert options['day'] == '2-digit'

    def test_resolved_options_contains_date_style(self):
        """Test resolvedOptions() contains dateStyle."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'full'})
        options = formatter.resolvedOptions()

        assert 'dateStyle' in options
        assert options['dateStyle'] == 'full'

    def test_resolved_options_contains_time_style(self):
        """Test resolvedOptions() contains timeStyle."""
        formatter = IntlDateTimeFormat('en-US', {'timeStyle': 'medium'})
        options = formatter.resolvedOptions()

        assert 'timeStyle' in options
        assert options['timeStyle'] == 'medium'

    def test_resolved_options_contains_hour_cycle(self):
        """Test resolvedOptions() contains hourCycle."""
        formatter = IntlDateTimeFormat('en-US', {
            'hourCycle': 'h12',
            'hour': 'numeric'
        })
        options = formatter.resolvedOptions()

        assert 'hourCycle' in options
        assert options['hourCycle'] == 'h12'

    def test_resolved_options_default_hour_cycle(self):
        """Test resolvedOptions() has default hourCycle for locale."""
        formatter = IntlDateTimeFormat('en-US', {'hour': 'numeric'})
        options = formatter.resolvedOptions()

        # en-US defaults to 12-hour
        assert 'hourCycle' in options
        assert options['hourCycle'] in ['h11', 'h12']

    def test_resolved_options_contains_hour12(self):
        """Test resolvedOptions() contains hour12 property."""
        formatter = IntlDateTimeFormat('en-US', {
            'hourCycle': 'h12',
            'hour': 'numeric'
        })
        options = formatter.resolvedOptions()

        # hour12 is derived from hourCycle
        assert 'hour12' in options
        assert options['hour12'] is True

    def test_resolved_options_hour12_false_for_24_hour(self):
        """Test resolvedOptions() hour12 is false for 24-hour cycle."""
        formatter = IntlDateTimeFormat('en-US', {
            'hourCycle': 'h23',
            'hour': 'numeric'
        })
        options = formatter.resolvedOptions()

        assert options['hour12'] is False

    def test_resolved_options_locale_negotiation(self):
        """Test resolvedOptions() shows negotiated locale."""
        # Request locale that might not be exact match
        formatter = IntlDateTimeFormat(['fr-CA', 'fr-FR', 'en-US'])
        options = formatter.resolvedOptions()

        assert 'locale' in options
        # Should negotiate to one of the requested or a fallback
        assert isinstance(options['locale'], str)

    def test_resolved_options_calendar_from_locale_extension(self):
        """Test resolvedOptions() extracts calendar from locale extension."""
        formatter = IntlDateTimeFormat('en-US-u-ca-buddhist')
        options = formatter.resolvedOptions()

        assert options['calendar'] == 'buddhist'

    def test_resolved_options_calendar_option_overrides_locale(self):
        """Test options parameter overrides locale extension."""
        formatter = IntlDateTimeFormat('en-US-u-ca-buddhist', {
            'calendar': 'gregory'
        })
        options = formatter.resolvedOptions()

        # Explicit option should override locale extension
        assert options['calendar'] == 'gregory'

    def test_resolved_options_contains_weekday(self):
        """Test resolvedOptions() contains weekday if specified."""
        formatter = IntlDateTimeFormat('en-US', {'weekday': 'long'})
        options = formatter.resolvedOptions()

        assert 'weekday' in options
        assert options['weekday'] == 'long'

    def test_resolved_options_contains_era(self):
        """Test resolvedOptions() contains era if specified."""
        formatter = IntlDateTimeFormat('en-US', {'era': 'short'})
        options = formatter.resolvedOptions()

        assert 'era' in options
        assert options['era'] == 'short'

    def test_resolved_options_contains_timezone_name(self):
        """Test resolvedOptions() contains timeZoneName if specified."""
        formatter = IntlDateTimeFormat('en-US', {'timeZoneName': 'long'})
        options = formatter.resolvedOptions()

        assert 'timeZoneName' in options
        assert options['timeZoneName'] == 'long'

    def test_resolved_options_contains_day_period(self):
        """Test resolvedOptions() contains dayPeriod if specified."""
        formatter = IntlDateTimeFormat('en-US', {
            'hour': 'numeric',
            'dayPeriod': 'long'
        })
        options = formatter.resolvedOptions()

        assert 'dayPeriod' in options
        assert options['dayPeriod'] == 'long'

    def test_resolved_options_contains_fractional_second_digits(self):
        """Test resolvedOptions() contains fractionalSecondDigits if specified."""
        formatter = IntlDateTimeFormat('en-US', {
            'second': 'numeric',
            'fractionalSecondDigits': 3
        })
        options = formatter.resolvedOptions()

        assert 'fractionalSecondDigits' in options
        assert options['fractionalSecondDigits'] == 3

    def test_resolved_options_immutable(self):
        """Test resolvedOptions() returns new object each time."""
        formatter = IntlDateTimeFormat('en-US')
        options1 = formatter.resolvedOptions()
        options2 = formatter.resolvedOptions()

        # Should be equal but not the same object
        assert options1 == options2
        assert options1 is not options2

    def test_resolved_options_modification_doesnt_affect_formatter(self):
        """Test modifying resolvedOptions() doesn't affect formatter."""
        formatter = IntlDateTimeFormat('en-US', {'year': 'numeric'})
        options = formatter.resolvedOptions()

        # Modify returned options
        options['year'] = '2-digit'

        # Get options again
        options2 = formatter.resolvedOptions()

        # Should still be original value
        assert options2['year'] == 'numeric'

    def test_resolved_options_all_fields_present(self):
        """Test resolvedOptions() contains all expected fields."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': '2-digit',
            'hour': 'numeric',
            'minute': '2-digit',
            'second': '2-digit',
            'timeZone': 'America/New_York',
            'calendar': 'gregory'
        })
        options = formatter.resolvedOptions()

        required_fields = [
            'locale',
            'calendar',
            'numberingSystem',
            'timeZone',
            'year',
            'month',
            'day',
            'hour',
            'minute',
            'second'
        ]

        for field in required_fields:
            assert field in options, f"Missing required field: {field}"
