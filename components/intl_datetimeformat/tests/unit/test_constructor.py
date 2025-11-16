"""
Unit tests for IntlDateTimeFormat constructor.
Tests FR-ES24-C-009: Constructor with locale and options support.
"""

import pytest
from datetime import datetime
from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat


class TestConstructor:
    """Test IntlDateTimeFormat constructor."""

    def test_constructor_no_args(self):
        """Test constructor with no arguments uses default locale."""
        formatter = IntlDateTimeFormat()
        assert formatter is not None
        options = formatter.resolvedOptions()
        assert 'locale' in options
        assert options['locale'] is not None

    def test_constructor_with_string_locale(self):
        """Test constructor with single locale string."""
        formatter = IntlDateTimeFormat('en-US')
        options = formatter.resolvedOptions()
        assert options['locale'] == 'en-US'

    def test_constructor_with_locale_array(self):
        """Test constructor with array of locales."""
        formatter = IntlDateTimeFormat(['fr-FR', 'en-US'])
        options = formatter.resolvedOptions()
        # Should negotiate and pick best match
        assert options['locale'] in ['fr-FR', 'en-US']

    def test_constructor_with_basic_options(self):
        """Test constructor with basic formatting options."""
        formatter = IntlDateTimeFormat('en-US', {
            'year': 'numeric',
            'month': 'long',
            'day': '2-digit'
        })
        options = formatter.resolvedOptions()
        assert options['year'] == 'numeric'
        assert options['month'] == 'long'
        assert options['day'] == '2-digit'

    def test_constructor_with_date_style(self):
        """Test constructor with dateStyle option."""
        formatter = IntlDateTimeFormat('en-US', {'dateStyle': 'full'})
        options = formatter.resolvedOptions()
        assert options['dateStyle'] == 'full'

    def test_constructor_with_time_style(self):
        """Test constructor with timeStyle option."""
        formatter = IntlDateTimeFormat('en-US', {'timeStyle': 'medium'})
        options = formatter.resolvedOptions()
        assert options['timeStyle'] == 'medium'

    def test_constructor_with_both_styles(self):
        """Test constructor with both dateStyle and timeStyle."""
        formatter = IntlDateTimeFormat('en-US', {
            'dateStyle': 'long',
            'timeStyle': 'short'
        })
        options = formatter.resolvedOptions()
        assert options['dateStyle'] == 'long'
        assert options['timeStyle'] == 'short'

    def test_constructor_with_timezone(self):
        """Test constructor with IANA time zone."""
        formatter = IntlDateTimeFormat('en-US', {
            'timeZone': 'America/New_York'
        })
        options = formatter.resolvedOptions()
        assert options['timeZone'] == 'America/New_York'

    def test_constructor_with_calendar(self):
        """Test constructor with calendar system."""
        formatter = IntlDateTimeFormat('en-US', {
            'calendar': 'gregory'
        })
        options = formatter.resolvedOptions()
        assert options['calendar'] == 'gregory'

    def test_constructor_with_hour_cycle(self):
        """Test constructor with hour cycle option."""
        formatter = IntlDateTimeFormat('en-US', {
            'hourCycle': 'h12',
            'hour': 'numeric'
        })
        options = formatter.resolvedOptions()
        assert options['hourCycle'] == 'h12'

    def test_constructor_invalid_locale_raises_error(self):
        """Test constructor with invalid locale raises RangeError."""
        with pytest.raises(ValueError, match='Invalid locale'):
            IntlDateTimeFormat('not-a-valid-locale!')

    def test_constructor_invalid_timezone_raises_error(self):
        """Test constructor with invalid time zone raises RangeError."""
        with pytest.raises(ValueError, match='Invalid time zone'):
            IntlDateTimeFormat('en-US', {'timeZone': 'InvalidTimeZone'})

    def test_constructor_invalid_calendar_raises_error(self):
        """Test constructor with invalid calendar raises RangeError."""
        with pytest.raises(ValueError, match='Invalid calendar'):
            IntlDateTimeFormat('en-US', {'calendar': 'invalid'})

    def test_constructor_invalid_hour_cycle_raises_error(self):
        """Test constructor with invalid hour cycle raises RangeError."""
        with pytest.raises(ValueError, match='Invalid hourCycle'):
            IntlDateTimeFormat('en-US', {
                'hourCycle': 'invalid',
                'hour': 'numeric'
            })

    def test_constructor_style_with_component_raises_error(self):
        """Test that dateStyle/timeStyle cannot be used with component options."""
        with pytest.raises(ValueError, match='Cannot use dateStyle'):
            IntlDateTimeFormat('en-US', {
                'dateStyle': 'full',
                'year': 'numeric'  # Conflict
            })

    def test_constructor_invalid_date_style_raises_error(self):
        """Test constructor with invalid dateStyle raises error."""
        with pytest.raises(ValueError, match='Invalid dateStyle'):
            IntlDateTimeFormat('en-US', {'dateStyle': 'invalid'})

    def test_constructor_invalid_time_style_raises_error(self):
        """Test constructor with invalid timeStyle raises error."""
        with pytest.raises(ValueError, match='Invalid timeStyle'):
            IntlDateTimeFormat('en-US', {'timeStyle': 'invalid'})

    def test_constructor_locale_with_unicode_extension(self):
        """Test constructor with locale containing Unicode extension."""
        formatter = IntlDateTimeFormat('en-US-u-ca-buddhist')
        options = formatter.resolvedOptions()
        assert options['calendar'] == 'buddhist'

    def test_constructor_multiple_calendars(self):
        """Test constructor with different calendar systems."""
        calendars = ['gregory', 'buddhist', 'japanese', 'islamic', 'chinese']
        for calendar in calendars:
            formatter = IntlDateTimeFormat('en-US', {'calendar': calendar})
            options = formatter.resolvedOptions()
            assert options['calendar'] == calendar

    def test_constructor_utc_timezone(self):
        """Test constructor with UTC time zone."""
        formatter = IntlDateTimeFormat('en-US', {'timeZone': 'UTC'})
        options = formatter.resolvedOptions()
        assert options['timeZone'] == 'UTC'
