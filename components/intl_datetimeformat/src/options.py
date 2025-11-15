"""
DateTimeFormat options validation and processing.
Handles validation of date/time styles, component options, and other settings.
"""

# Valid style values
VALID_DATE_TIME_STYLES = {'full', 'long', 'medium', 'short'}

# Valid component option values
VALID_YEAR_OPTIONS = {'numeric', '2-digit'}
VALID_MONTH_OPTIONS = {'numeric', '2-digit', 'long', 'short', 'narrow'}
VALID_DAY_OPTIONS = {'numeric', '2-digit'}
VALID_WEEKDAY_OPTIONS = {'long', 'short', 'narrow'}
VALID_ERA_OPTIONS = {'long', 'short', 'narrow'}
VALID_HOUR_OPTIONS = {'numeric', '2-digit'}
VALID_MINUTE_OPTIONS = {'numeric', '2-digit'}
VALID_SECOND_OPTIONS = {'numeric', '2-digit'}
VALID_FRACTIONAL_SECOND_DIGITS = {1, 2, 3}
VALID_TIME_ZONE_NAME_OPTIONS = {'long', 'short', 'shortOffset', 'longOffset', 'shortGeneric', 'longGeneric'}

# Valid hour cycles
VALID_HOUR_CYCLES = {'h11', 'h12', 'h23', 'h24'}

# Valid day period options
VALID_DAY_PERIOD_OPTIONS = {'narrow', 'short', 'long'}

# Valid calendars (ES2024 requirement)
VALID_CALENDARS = {
    'gregory', 'buddhist', 'chinese', 'coptic', 'dangi', 'ethioaa', 'ethiopic',
    'hebrew', 'indian', 'islamic', 'islamic-umalqura', 'islamic-tbla',
    'islamic-civil', 'islamic-rgsa', 'iso8601', 'japanese', 'persian', 'roc',
    'islamicc'
}


class DateTimeFormatOptions:
    """
    Options object for DateTimeFormat configuration.
    """

    def __init__(self, **kwargs):
        """
        Create options object.

        Args:
            **kwargs: Option key-value pairs
        """
        self._options = {}

        # Process and validate all options
        for key, value in kwargs.items():
            if value is not None:
                self._options[key] = value

    def to_dict(self):
        """
        Convert options to dictionary.

        Returns:
            Dictionary of options
        """
        return self._options.copy()

    def get(self, key, default=None):
        """Get option value."""
        return self._options.get(key, default)

    def set(self, key, value):
        """Set option value."""
        if value is not None:
            self._options[key] = value

    def has(self, key):
        """Check if option exists."""
        return key in self._options


def validate_style_options(dateStyle, timeStyle):
    """
    Validate dateStyle/timeStyle options.

    Args:
        dateStyle: Date style (full, long, medium, short, or None)
        timeStyle: Time style (full, long, medium, short, or None)

    Returns:
        True if valid combination

    Raises:
        ValueError: If invalid style values
    """
    if dateStyle is not None and dateStyle not in VALID_DATE_TIME_STYLES:
        raise ValueError(f"Invalid dateStyle: {dateStyle}. Must be one of {VALID_DATE_TIME_STYLES}")

    if timeStyle is not None and timeStyle not in VALID_DATE_TIME_STYLES:
        raise ValueError(f"Invalid timeStyle: {timeStyle}. Must be one of {VALID_DATE_TIME_STYLES}")

    return True


def validate_component_options(options):
    """
    Validate component-specific formatting options.

    Args:
        options: Dict of component options

    Returns:
        True if valid

    Raises:
        ValueError: If invalid option values
    """
    if not isinstance(options, dict):
        raise ValueError("Options must be a dictionary")

    # Validate each component option
    if 'year' in options and options['year'] not in VALID_YEAR_OPTIONS:
        raise ValueError(f"Invalid year option: {options['year']}")

    if 'month' in options and options['month'] not in VALID_MONTH_OPTIONS:
        raise ValueError(f"Invalid month option: {options['month']}")

    if 'day' in options and options['day'] not in VALID_DAY_OPTIONS:
        raise ValueError(f"Invalid day option: {options['day']}")

    if 'weekday' in options and options['weekday'] not in VALID_WEEKDAY_OPTIONS:
        raise ValueError(f"Invalid weekday option: {options['weekday']}")

    if 'era' in options and options['era'] not in VALID_ERA_OPTIONS:
        raise ValueError(f"Invalid era option: {options['era']}")

    if 'hour' in options and options['hour'] not in VALID_HOUR_OPTIONS:
        raise ValueError(f"Invalid hour option: {options['hour']}")

    if 'minute' in options and options['minute'] not in VALID_MINUTE_OPTIONS:
        raise ValueError(f"Invalid minute option: {options['minute']}")

    if 'second' in options and options['second'] not in VALID_SECOND_OPTIONS:
        raise ValueError(f"Invalid second option: {options['second']}")

    if 'fractionalSecondDigits' in options:
        fsd = options['fractionalSecondDigits']
        if fsd not in VALID_FRACTIONAL_SECOND_DIGITS:
            raise ValueError(f"Invalid fractionalSecondDigits: {fsd}")

    if 'timeZoneName' in options and options['timeZoneName'] not in VALID_TIME_ZONE_NAME_OPTIONS:
        raise ValueError(f"Invalid timeZoneName option: {options['timeZoneName']}")

    return True


def set_time_zone(timeZone):
    """
    Set and validate IANA time zone.

    Args:
        timeZone: IANA time zone identifier

    Returns:
        Validated time zone identifier

    Raises:
        ValueError: If invalid time zone
    """
    from .timezone import validate_iana_timezone

    if not validate_iana_timezone(timeZone):
        raise ValueError(f"Invalid IANA time zone: {timeZone}")

    return timeZone


def set_calendar(calendar):
    """
    Set and validate calendar system.

    Args:
        calendar: Calendar type identifier

    Returns:
        Validated calendar identifier

    Raises:
        ValueError: If invalid calendar
    """
    if calendar not in VALID_CALENDARS:
        raise ValueError(f"Invalid calendar: {calendar}. Must be one of {VALID_CALENDARS}")

    return calendar


def set_hour_cycle(hourCycle):
    """
    Set hour cycle preference.

    Args:
        hourCycle: Hour cycle (h11, h12, h23, h24)

    Returns:
        Validated hour cycle

    Raises:
        ValueError: If invalid hour cycle
    """
    if hourCycle not in VALID_HOUR_CYCLES:
        raise ValueError(f"Invalid hourCycle: {hourCycle}. Must be one of {VALID_HOUR_CYCLES}")

    return hourCycle


def set_day_period(dayPeriod):
    """
    Set day period display style.

    Args:
        dayPeriod: Day period (narrow, short, long)

    Returns:
        Validated day period option

    Raises:
        ValueError: If invalid day period
    """
    if dayPeriod not in VALID_DAY_PERIOD_OPTIONS:
        raise ValueError(f"Invalid dayPeriod: {dayPeriod}. Must be one of {VALID_DAY_PERIOD_OPTIONS}")

    return dayPeriod
