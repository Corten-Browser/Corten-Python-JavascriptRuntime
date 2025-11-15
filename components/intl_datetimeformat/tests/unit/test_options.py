"""
Unit tests for DateTimeFormat options validation.
Tests FR-ES24-C-014: Date/time style options.
Tests FR-ES24-C-015: Component options.
Tests FR-ES24-C-018: Hour cycle support.
Tests FR-ES24-C-019: dayPeriod option.
"""

import pytest
from components.intl_datetimeformat.src.options import (
    DateTimeFormatOptions,
    validate_style_options,
    validate_component_options,
    set_time_zone,
    set_calendar,
    set_hour_cycle,
    set_day_period
)


class TestStyleOptionsValidation:
    """Test dateStyle and timeStyle validation."""

    def test_validate_date_style_full(self):
        """Test validation of dateStyle='full'."""
        assert validate_style_options('full', None) is True

    def test_validate_date_style_long(self):
        """Test validation of dateStyle='long'."""
        assert validate_style_options('long', None) is True

    def test_validate_date_style_medium(self):
        """Test validation of dateStyle='medium'."""
        assert validate_style_options('medium', None) is True

    def test_validate_date_style_short(self):
        """Test validation of dateStyle='short'."""
        assert validate_style_options('short', None) is True

    def test_validate_time_style_full(self):
        """Test validation of timeStyle='full'."""
        assert validate_style_options(None, 'full') is True

    def test_validate_time_style_long(self):
        """Test validation of timeStyle='long'."""
        assert validate_style_options(None, 'long') is True

    def test_validate_time_style_medium(self):
        """Test validation of timeStyle='medium'."""
        assert validate_style_options(None, 'medium') is True

    def test_validate_time_style_short(self):
        """Test validation of timeStyle='short'."""
        assert validate_style_options(None, 'short') is True

    def test_validate_both_styles(self):
        """Test validation of both dateStyle and timeStyle."""
        assert validate_style_options('full', 'long') is True
        assert validate_style_options('short', 'short') is True

    def test_validate_invalid_date_style_raises_error(self):
        """Test invalid dateStyle raises ValueError."""
        with pytest.raises(ValueError, match='Invalid dateStyle'):
            validate_style_options('invalid', None)

    def test_validate_invalid_time_style_raises_error(self):
        """Test invalid timeStyle raises ValueError."""
        with pytest.raises(ValueError, match='Invalid timeStyle'):
            validate_style_options(None, 'invalid')

    def test_validate_none_styles_allowed(self):
        """Test both styles can be None."""
        assert validate_style_options(None, None) is True


class TestComponentOptionsValidation:
    """Test component-specific options validation."""

    def test_validate_year_numeric(self):
        """Test validation of year='numeric'."""
        assert validate_component_options({'year': 'numeric'}) is True

    def test_validate_year_2_digit(self):
        """Test validation of year='2-digit'."""
        assert validate_component_options({'year': '2-digit'}) is True

    def test_validate_month_numeric(self):
        """Test validation of month='numeric'."""
        assert validate_component_options({'month': 'numeric'}) is True

    def test_validate_month_2_digit(self):
        """Test validation of month='2-digit'."""
        assert validate_component_options({'month': '2-digit'}) is True

    def test_validate_month_long(self):
        """Test validation of month='long'."""
        assert validate_component_options({'month': 'long'}) is True

    def test_validate_month_short(self):
        """Test validation of month='short'."""
        assert validate_component_options({'month': 'short'}) is True

    def test_validate_month_narrow(self):
        """Test validation of month='narrow'."""
        assert validate_component_options({'month': 'narrow'}) is True

    def test_validate_day_numeric(self):
        """Test validation of day='numeric'."""
        assert validate_component_options({'day': 'numeric'}) is True

    def test_validate_day_2_digit(self):
        """Test validation of day='2-digit'."""
        assert validate_component_options({'day': '2-digit'}) is True

    def test_validate_weekday_long(self):
        """Test validation of weekday='long'."""
        assert validate_component_options({'weekday': 'long'}) is True

    def test_validate_weekday_short(self):
        """Test validation of weekday='short'."""
        assert validate_component_options({'weekday': 'short'}) is True

    def test_validate_weekday_narrow(self):
        """Test validation of weekday='narrow'."""
        assert validate_component_options({'weekday': 'narrow'}) is True

    def test_validate_era_long(self):
        """Test validation of era='long'."""
        assert validate_component_options({'era': 'long'}) is True

    def test_validate_era_short(self):
        """Test validation of era='short'."""
        assert validate_component_options({'era': 'short'}) is True

    def test_validate_era_narrow(self):
        """Test validation of era='narrow'."""
        assert validate_component_options({'era': 'narrow'}) is True

    def test_validate_hour_numeric(self):
        """Test validation of hour='numeric'."""
        assert validate_component_options({'hour': 'numeric'}) is True

    def test_validate_hour_2_digit(self):
        """Test validation of hour='2-digit'."""
        assert validate_component_options({'hour': '2-digit'}) is True

    def test_validate_minute_numeric(self):
        """Test validation of minute='numeric'."""
        assert validate_component_options({'minute': 'numeric'}) is True

    def test_validate_minute_2_digit(self):
        """Test validation of minute='2-digit'."""
        assert validate_component_options({'minute': '2-digit'}) is True

    def test_validate_second_numeric(self):
        """Test validation of second='numeric'."""
        assert validate_component_options({'second': 'numeric'}) is True

    def test_validate_second_2_digit(self):
        """Test validation of second='2-digit'."""
        assert validate_component_options({'second': '2-digit'}) is True

    def test_validate_fractional_second_digits(self):
        """Test validation of fractionalSecondDigits."""
        assert validate_component_options({'fractionalSecondDigits': 1}) is True
        assert validate_component_options({'fractionalSecondDigits': 2}) is True
        assert validate_component_options({'fractionalSecondDigits': 3}) is True

    def test_validate_fractional_second_digits_invalid_raises_error(self):
        """Test invalid fractionalSecondDigits raises ValueError."""
        with pytest.raises(ValueError, match='fractionalSecondDigits'):
            validate_component_options({'fractionalSecondDigits': 0})

        with pytest.raises(ValueError, match='fractionalSecondDigits'):
            validate_component_options({'fractionalSecondDigits': 4})

    def test_validate_timezone_name_long(self):
        """Test validation of timeZoneName='long'."""
        assert validate_component_options({'timeZoneName': 'long'}) is True

    def test_validate_timezone_name_short(self):
        """Test validation of timeZoneName='short'."""
        assert validate_component_options({'timeZoneName': 'short'}) is True

    def test_validate_timezone_name_offset_styles(self):
        """Test validation of timeZoneName offset styles."""
        assert validate_component_options({'timeZoneName': 'shortOffset'}) is True
        assert validate_component_options({'timeZoneName': 'longOffset'}) is True
        assert validate_component_options({'timeZoneName': 'shortGeneric'}) is True
        assert validate_component_options({'timeZoneName': 'longGeneric'}) is True

    def test_validate_multiple_components(self):
        """Test validation of multiple component options."""
        options = {
            'year': 'numeric',
            'month': 'long',
            'day': '2-digit',
            'hour': 'numeric',
            'minute': '2-digit',
            'second': '2-digit'
        }
        assert validate_component_options(options) is True

    def test_validate_invalid_year_value_raises_error(self):
        """Test invalid year value raises ValueError."""
        with pytest.raises(ValueError, match='Invalid.*year'):
            validate_component_options({'year': 'invalid'})

    def test_validate_invalid_month_value_raises_error(self):
        """Test invalid month value raises ValueError."""
        with pytest.raises(ValueError, match='Invalid.*month'):
            validate_component_options({'month': 'invalid'})

    def test_validate_invalid_weekday_value_raises_error(self):
        """Test invalid weekday value raises ValueError."""
        with pytest.raises(ValueError, match='Invalid.*weekday'):
            validate_component_options({'weekday': 'invalid'})


class TestTimeZoneSetting:
    """Test time zone setting and validation."""

    def test_set_timezone_utc(self):
        """Test setting UTC time zone."""
        result = set_time_zone('UTC')
        assert result == 'UTC'

    def test_set_timezone_america_new_york(self):
        """Test setting America/New_York time zone."""
        result = set_time_zone('America/New_York')
        assert result == 'America/New_York'

    def test_set_timezone_europe_london(self):
        """Test setting Europe/London time zone."""
        result = set_time_zone('Europe/London')
        assert result == 'Europe/London'

    def test_set_timezone_asia_tokyo(self):
        """Test setting Asia/Tokyo time zone."""
        result = set_time_zone('Asia/Tokyo')
        assert result == 'Asia/Tokyo'

    def test_set_timezone_invalid_raises_error(self):
        """Test setting invalid time zone raises ValueError."""
        with pytest.raises(ValueError, match='Invalid time zone'):
            set_time_zone('Invalid/TimeZone')


class TestCalendarSetting:
    """Test calendar setting and validation."""

    def test_set_calendar_gregory(self):
        """Test setting Gregorian calendar."""
        result = set_calendar('gregory')
        assert result == 'gregory'

    def test_set_calendar_buddhist(self):
        """Test setting Buddhist calendar."""
        result = set_calendar('buddhist')
        assert result == 'buddhist'

    def test_set_calendar_japanese(self):
        """Test setting Japanese calendar."""
        result = set_calendar('japanese')
        assert result == 'japanese'

    def test_set_calendar_islamic(self):
        """Test setting Islamic calendar."""
        result = set_calendar('islamic')
        assert result == 'islamic'

    def test_set_calendar_invalid_raises_error(self):
        """Test setting invalid calendar raises ValueError."""
        with pytest.raises(ValueError, match='Invalid calendar'):
            set_calendar('invalid')


class TestHourCycleSetting:
    """Test hour cycle setting and validation."""

    def test_set_hour_cycle_h11(self):
        """Test setting h11 hour cycle."""
        result = set_hour_cycle('h11')
        assert result == 'h11'

    def test_set_hour_cycle_h12(self):
        """Test setting h12 hour cycle."""
        result = set_hour_cycle('h12')
        assert result == 'h12'

    def test_set_hour_cycle_h23(self):
        """Test setting h23 hour cycle."""
        result = set_hour_cycle('h23')
        assert result == 'h23'

    def test_set_hour_cycle_h24(self):
        """Test setting h24 hour cycle."""
        result = set_hour_cycle('h24')
        assert result == 'h24'

    def test_set_hour_cycle_invalid_raises_error(self):
        """Test setting invalid hour cycle raises ValueError."""
        with pytest.raises(ValueError, match='Invalid hourCycle'):
            set_hour_cycle('invalid')

    def test_set_hour_cycle_h13_invalid(self):
        """Test h13 is invalid."""
        with pytest.raises(ValueError, match='Invalid hourCycle'):
            set_hour_cycle('h13')


class TestDayPeriodSetting:
    """Test day period setting and validation."""

    def test_set_day_period_narrow(self):
        """Test setting narrow day period."""
        result = set_day_period('narrow')
        assert result == 'narrow'

    def test_set_day_period_short(self):
        """Test setting short day period."""
        result = set_day_period('short')
        assert result == 'short'

    def test_set_day_period_long(self):
        """Test setting long day period."""
        result = set_day_period('long')
        assert result == 'long'

    def test_set_day_period_invalid_raises_error(self):
        """Test setting invalid day period raises ValueError."""
        with pytest.raises(ValueError, match='Invalid dayPeriod'):
            set_day_period('invalid')


class TestOptionsClass:
    """Test DateTimeFormatOptions class."""

    def test_options_creation_with_styles(self):
        """Test creating options with dateStyle and timeStyle."""
        options = DateTimeFormatOptions(dateStyle='full', timeStyle='long')
        assert options.dateStyle == 'full'
        assert options.timeStyle == 'long'

    def test_options_creation_with_components(self):
        """Test creating options with component options."""
        options = DateTimeFormatOptions(
            year='numeric',
            month='long',
            day='2-digit'
        )
        assert options.year == 'numeric'
        assert options.month == 'long'
        assert options.day == '2-digit'

    def test_options_with_timezone_and_calendar(self):
        """Test creating options with timeZone and calendar."""
        options = DateTimeFormatOptions(
            timeZone='America/New_York',
            calendar='gregory'
        )
        assert options.timeZone == 'America/New_York'
        assert options.calendar == 'gregory'

    def test_options_with_hour_cycle(self):
        """Test creating options with hourCycle."""
        options = DateTimeFormatOptions(
            hour='numeric',
            hourCycle='h12'
        )
        assert options.hour == 'numeric'
        assert options.hourCycle == 'h12'

    def test_options_with_day_period(self):
        """Test creating options with dayPeriod."""
        options = DateTimeFormatOptions(
            hour='numeric',
            dayPeriod='long'
        )
        assert options.hour == 'numeric'
        assert options.dayPeriod == 'long'

    def test_options_style_and_component_conflict_raises_error(self):
        """Test styles and component options cannot be mixed."""
        with pytest.raises(ValueError, match='Cannot use dateStyle'):
            DateTimeFormatOptions(
                dateStyle='full',
                year='numeric'  # Conflict
            )

    def test_options_to_dict(self):
        """Test converting options to dictionary."""
        options = DateTimeFormatOptions(
            year='numeric',
            month='long',
            day='2-digit'
        )
        result = options.to_dict()

        assert isinstance(result, dict)
        assert result['year'] == 'numeric'
        assert result['month'] == 'long'
        assert result['day'] == '2-digit'
