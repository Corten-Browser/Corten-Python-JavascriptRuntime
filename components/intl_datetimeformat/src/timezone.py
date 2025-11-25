"""
IANA time zone support.
Handles time zone validation, offset calculation, and conversions.
"""

from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, available_timezones
import pytz


class TimeZoneSupport:
    """Support for IANA time zones."""

    # Cache of validated time zones
    _validated_zones = set()


def validate_iana_timezone(timeZone):
    """
    Validate IANA time zone identifier.

    Args:
        timeZone: Time zone identifier string

    Returns:
        True if valid, False otherwise
    """
    if not timeZone:
        return False

    # Check cache first
    if timeZone in TimeZoneSupport._validated_zones:
        return True

    # UTC and GMT are always valid (case-sensitive)
    if timeZone in ('UTC', 'GMT'):
        TimeZoneSupport._validated_zones.add(timeZone)
        return True

    # Check against available time zones
    try:
        # Try zoneinfo first (Python 3.9+)
        if timeZone in available_timezones():
            TimeZoneSupport._validated_zones.add(timeZone)
            return True
    except:
        pass

    # Fallback to pytz - but be strict about case
    try:
        # pytz accepts case-insensitive aliases, so we need to validate strictly
        # Check if the timezone is in pytz's all_timezones set
        if timeZone in pytz.all_timezones:
            TimeZoneSupport._validated_zones.add(timeZone)
            return True
        # Also check common timezones
        if timeZone in pytz.common_timezones:
            TimeZoneSupport._validated_zones.add(timeZone)
            return True
    except:
        pass

    return False


def get_timezone_offset(timeZone, date):
    """
    Get UTC offset for time zone at specific date.

    Args:
        timeZone: IANA time zone identifier
        date: Date for offset calculation (handles DST)

    Returns:
        Offset in minutes from UTC

    Raises:
        ValueError: If timeZone is invalid
    """
    # Validate timezone first
    if not validate_iana_timezone(timeZone):
        raise ValueError(f"Invalid time zone: {timeZone}")

    if not isinstance(date, datetime):
        # Convert timestamp to datetime
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now(timezone.utc)

    # Handle UTC/GMT specially
    if timeZone in ('UTC', 'GMT'):
        return 0

    try:
        # Try zoneinfo (preferred for Python 3.9+)
        tz = ZoneInfo(timeZone)
        localized = date.astimezone(tz)
        offset = localized.utcoffset()
        return int(offset.total_seconds() / 60)
    except:
        pass

    try:
        # Fallback to pytz
        tz = pytz.timezone(timeZone)
        if date.tzinfo is None:
            date = date.replace(tzinfo=timezone.utc)
        localized = date.astimezone(tz)
        offset = localized.utcoffset()
        return int(offset.total_seconds() / 60)
    except:
        raise ValueError(f"Invalid time zone: {timeZone}")


def apply_timezone(date, timeZone):
    """
    Convert date to specific time zone.

    Args:
        date: Date to convert
        timeZone: Target time zone

    Returns:
        Date adjusted to time zone

    Raises:
        ValueError: If timeZone is invalid
    """
    # Validate timezone first
    if not validate_iana_timezone(timeZone):
        raise ValueError(f"Invalid time zone: {timeZone}")

    if not isinstance(date, datetime):
        # Convert timestamp to datetime
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now(timezone.utc)

    # Ensure date has timezone info
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Handle UTC/GMT
    if timeZone in ('UTC', 'GMT'):
        return date.astimezone(timezone.utc)

    try:
        # Try zoneinfo
        tz = ZoneInfo(timeZone)
        return date.astimezone(tz)
    except:
        pass

    try:
        # Fallback to pytz
        tz = pytz.timezone(timeZone)
        return date.astimezone(tz)
    except:
        raise ValueError(f"Invalid time zone: {timeZone}")


def get_timezone_name(timeZone, locale, style):
    """
    Get localized time zone name/abbreviation.

    Args:
        timeZone: IANA time zone identifier
        locale: Locale for localized name
        style: Name style (long, short, shortOffset, longOffset, etc.)

    Returns:
        Localized time zone name

    Raises:
        ValueError: If timeZone is invalid or style is unsupported
    """
    # Validate timezone first
    if not validate_iana_timezone(timeZone):
        raise ValueError(f"Invalid time zone: {timeZone}")

    # Validate style
    valid_styles = {'long', 'short', 'shortOffset', 'longOffset', 'shortGeneric', 'longGeneric'}
    if style not in valid_styles:
        raise ValueError(f"Invalid style: {style}")

    # Simplified timezone name mapping
    # In a full implementation, this would use CLDR data

    if timeZone == 'UTC':
        if style == 'long':
            return 'Coordinated Universal Time'
        elif style in ('short', 'shortGeneric'):
            return 'UTC'
        elif style == 'shortOffset':
            return '+00:00'
        elif style == 'longOffset':
            return 'UTC+00:00'
        return 'UTC'

    # For other time zones, construct a proper name
    try:
        # Get current offset
        now = datetime.now(timezone.utc)
        offset_minutes = get_timezone_offset(timeZone, now)
        offset_hours = offset_minutes // 60
        offset_mins = abs(offset_minutes % 60)

        if style in ('shortOffset', 'longOffset'):
            sign = '+' if offset_minutes >= 0 else '-'
            offset_str = f"{sign}{abs(offset_hours):02d}:{offset_mins:02d}"
            if style == 'longOffset':
                return f"UTC{offset_str}"
            return offset_str

        # Special handling for common timezone names (long style)
        if style == 'long':
            # Map common timezones to their long names
            long_names = {
                'America/New_York': 'Eastern Standard Time',
                'America/Chicago': 'Central Standard Time',
                'America/Denver': 'Mountain Standard Time',
                'America/Los_Angeles': 'Pacific Standard Time',
                'Europe/London': 'Greenwich Mean Time',
                'Europe/Paris': 'Central European Time',
                'Asia/Tokyo': 'Japan Standard Time',
                'Australia/Sydney': 'Australian Eastern Standard Time',
            }
            if timeZone in long_names:
                return long_names[timeZone]
            # Fallback: replace underscores and add "Time"
            return timeZone.replace('_', ' ') + ' Time'

        # Try to get abbreviated name from pytz for short style
        if style in ('short', 'shortGeneric'):
            try:
                tz = pytz.timezone(timeZone)
                now_tz = now.astimezone(tz)
                tzname = now_tz.strftime('%Z')
                if tzname and tzname != timeZone:
                    return tzname
            except:
                pass

            # Fallback to city name
            parts = timeZone.split('/')
            return parts[-1].replace('_', ' ') if parts else timeZone

        return timeZone

    except:
        return timeZone
