"""
Main IntlDateTimeFormat class.
Implements the Intl.DateTimeFormat API.
"""

from datetime import datetime, timezone
from .options import (
    DateTimeFormatOptions,
    validate_style_options,
    validate_component_options,
    set_time_zone,
    set_calendar,
    set_hour_cycle,
    set_day_period
)
from .locale_support import negotiate_locale, canonicalize_locale, LocaleSupport
from .timezone import apply_timezone
from .formatter import create_date_time_parts, assemble_pattern, format_range_pattern


class IntlDateTimeFormat:
    """
    Intl.DateTimeFormat implementation.

    Provides locale-aware date and time formatting with support for:
    - Multiple locales and locale negotiation
    - IANA time zones
    - Multiple calendar systems
    - Date/time styles and component options
    - Date range formatting
    """

    def __init__(self, locales=None, options=None):
        """
        Create IntlDateTimeFormat instance.

        Args:
            locales: String, array of strings, or None for default locale
            options: Formatting options dictionary
        """
        # Normalize locales
        if locales is None:
            requested_locales = []
        elif isinstance(locales, str):
            requested_locales = [locales]
        elif isinstance(locales, (list, tuple)):
            requested_locales = list(locales)
        else:
            requested_locales = []

        # Normalize options
        if options is None:
            options = {}
        elif not isinstance(options, dict):
            raise TypeError("Options must be a dictionary")

        # Negotiate locale
        self._locale = negotiate_locale(
            requested_locales,
            LocaleSupport.AVAILABLE_LOCALES,
            'en-US'
        )

        # Process options
        self._options = {}
        self._dateStyle = options.get('dateStyle')
        self._timeStyle = options.get('timeStyle')
        self._calendar = options.get('calendar', 'gregory')
        self._timeZone = options.get('timeZone', 'UTC')
        self._hourCycle = options.get('hourCycle')
        self._numberingSystem = options.get('numberingSystem', 'latn')

        # Validate style options
        if self._dateStyle or self._timeStyle:
            validate_style_options(self._dateStyle, self._timeStyle)

            # Cannot mix styles with component options
            component_keys = {'year', 'month', 'day', 'weekday', 'era',
                            'hour', 'minute', 'second', 'fractionalSecondDigits',
                            'dayPeriod', 'timeZoneName'}
            if any(key in options for key in component_keys):
                raise TypeError("Cannot specify both style and component options")

            self._options['dateStyle'] = self._dateStyle
            self._options['timeStyle'] = self._timeStyle
        else:
            # Component-based options
            component_options = {}
            for key in ['year', 'month', 'day', 'weekday', 'era',
                       'hour', 'minute', 'second', 'fractionalSecondDigits',
                       'dayPeriod', 'timeZoneName']:
                if key in options:
                    component_options[key] = options[key]
                    self._options[key] = options[key]

            if component_options:
                validate_component_options(component_options)

            # Set defaults if no options specified
            if not component_options:
                self._options['year'] = 'numeric'
                self._options['month'] = 'numeric'
                self._options['day'] = 'numeric'

        # Validate and set calendar
        if self._calendar:
            self._calendar = set_calendar(self._calendar)

        # Validate and set time zone
        if self._timeZone:
            self._timeZone = set_time_zone(self._timeZone)

        # Validate and set hour cycle
        if self._hourCycle:
            self._hourCycle = set_hour_cycle(self._hourCycle)
        else:
            # Default hour cycle based on locale
            if self._locale.startswith('en-US'):
                self._hourCycle = 'h12'
            else:
                self._hourCycle = 'h23'

        # Validate day period
        if 'dayPeriod' in options:
            set_day_period(options['dayPeriod'])

    def format(self, date=None):
        """
        Format date to string.

        Args:
            date: datetime, timestamp (int), or None for current time

        Returns:
            Formatted date/time string
        """
        # Convert date if needed
        date = self._normalize_date(date)

        # Get formatted parts
        parts = create_date_time_parts(
            date,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        # Assemble into string
        return assemble_pattern(parts, self._locale)

    def formatToParts(self, date=None):
        """
        Format date to array of parts.

        Args:
            date: datetime, timestamp (int), or None for current time

        Returns:
            Array of dicts with 'type' and 'value' keys
        """
        # Convert date if needed
        date = self._normalize_date(date)

        # Get formatted parts
        parts = create_date_time_parts(
            date,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        return parts

    def formatRange(self, startDate, endDate):
        """
        Format date range to string.

        Args:
            startDate: Start date (datetime or timestamp)
            endDate: End date (datetime or timestamp)

        Returns:
            Formatted date range string
        """
        # Normalize dates
        start = self._normalize_date(startDate)
        end = self._normalize_date(endDate)

        # Validate range
        if start > end:
            raise RangeError("startDate must be before or equal to endDate")

        # Get parts for both dates
        startParts = create_date_time_parts(
            start,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        endParts = create_date_time_parts(
            end,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        # Format range
        return format_range_pattern(startParts, endParts, self._locale)

    def formatRangeToParts(self, startDate, endDate):
        """
        Format date range to array of parts with source indicators.

        Args:
            startDate: Start date (datetime or timestamp)
            endDate: End date (datetime or timestamp)

        Returns:
            Array of dicts with 'type', 'value', and 'source' keys
        """
        # Normalize dates
        start = self._normalize_date(startDate)
        end = self._normalize_date(endDate)

        # Validate range
        if start > end:
            raise RangeError("startDate must be before or equal to endDate")

        # Get parts for both dates
        startParts = create_date_time_parts(
            start,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        endParts = create_date_time_parts(
            end,
            self._options,
            self._locale,
            self._calendar,
            self._timeZone,
            self._hourCycle
        )

        # Add source indicators
        result = []

        # Find shared parts
        shared_count = 0
        for i, (start_part, end_part) in enumerate(zip(startParts, endParts)):
            if start_part.get('type') == end_part.get('type') and \
               start_part.get('value') == end_part.get('value'):
                shared_count = i + 1
            else:
                break

        # Add shared prefix parts
        for i in range(shared_count):
            part = startParts[i].copy()
            part['source'] = 'shared'
            result.append(part)

        # Add start-specific parts
        for i in range(shared_count, len(startParts)):
            part = startParts[i].copy()
            if part.get('type') != 'literal':
                part['source'] = 'startRange'
            else:
                part['source'] = 'shared'
            result.append(part)

        # Add range separator
        result.append({'type': 'literal', 'value': ' – ', 'source': 'shared'})

        # Add end-specific parts
        for i in range(shared_count, len(endParts)):
            part = endParts[i].copy()
            if part.get('type') != 'literal':
                part['source'] = 'endRange'
            else:
                part['source'] = 'shared'
            result.append(part)

        return result

    def resolvedOptions(self):
        """
        Get resolved formatting options.

        Returns:
            Dictionary with resolved locale, calendar, timeZone, and options
        """
        result = {
            'locale': self._locale,
            'calendar': self._calendar,
            'numberingSystem': self._numberingSystem,
            'timeZone': self._timeZone,
        }

        # Add hour cycle if set
        if self._hourCycle:
            result['hourCycle'] = self._hourCycle

        # Add all formatting options
        result.update(self._options)

        return result

    @staticmethod
    def supportedLocalesOf(locales, options=None):
        """
        Get array of supported locales from input list.

        Args:
            locales: String or array of locale identifiers
            options: Optional dict with localeMatcher option

        Returns:
            Array of supported locale strings
        """
        # Normalize input
        if isinstance(locales, str):
            locales = [locales]
        elif not isinstance(locales, (list, tuple)):
            locales = []

        supported = []
        available = LocaleSupport.AVAILABLE_LOCALES

        for locale in locales:
            canonical = canonicalize_locale(locale)
            if canonical in available:
                supported.append(canonical)
            else:
                # Try language-only match
                lang = locale.split('-')[0]
                if lang in available:
                    supported.append(lang)

        return supported

    def _normalize_date(self, date):
        """
        Normalize date input to datetime object.

        Args:
            date: datetime, int/float timestamp, or None

        Returns:
            datetime object
        """
        if date is None:
            return datetime.now(timezone.utc)

        if isinstance(date, datetime):
            # Ensure timezone aware
            if date.tzinfo is None:
                return date.replace(tzinfo=timezone.utc)
            return date

        if isinstance(date, (int, float)):
            # Assume milliseconds if large number
            if date > 1e10:
                return datetime.fromtimestamp(date / 1000.0, tz=timezone.utc)
            else:
                return datetime.fromtimestamp(date, tz=timezone.utc)

        # Try to parse string
        if isinstance(date, str):
            try:
                return datetime.fromisoformat(date.replace('Z', '+00:00'))
            except:
                pass

        raise TypeError(f"Invalid date type: {type(date)}")


# Custom errors
class RangeError(ValueError):
    """Range error for invalid date ranges."""
    pass
