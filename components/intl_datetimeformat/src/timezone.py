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

    # UTC is always valid
    if timeZone.upper() in ('UTC', 'GMT'):
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

    # Fallback to pytz
    try:
        pytz.timezone(timeZone)
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
    """
    if not isinstance(date, datetime):
        # Convert timestamp to datetime
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now(timezone.utc)

    # Handle UTC/GMT specially
    if timeZone.upper() in ('UTC', 'GMT'):
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
        return 0


def apply_timezone(date, timeZone):
    """
    Convert date to specific time zone.

    Args:
        date: Date to convert
        timeZone: Target time zone

    Returns:
        Date adjusted to time zone
    """
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
    if timeZone.upper() in ('UTC', 'GMT'):
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
        return date


def get_timezone_name(timeZone, locale, style):
    """
    Get localized time zone name/abbreviation.

    Args:
        timeZone: IANA time zone identifier
        locale: Locale for localized name
        style: Name style (long, short, shortOffset, longOffset, etc.)

    Returns:
        Localized time zone name
    """
    # Simplified timezone name mapping
    # In a full implementation, this would use CLDR data

    if timeZone.upper() == 'UTC':
        if style == 'long':
            return 'Coordinated Universal Time'
        elif style in ('short', 'shortGeneric'):
            return 'UTC'
        elif style == 'shortOffset':
            return '+00:00'
        elif style == 'longOffset':
            return 'UTC+00:00'
        return 'UTC'

    # For other time zones, construct a simple name
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

        # Try to get abbreviated name from pytz
        try:
            tz = pytz.timezone(timeZone)
            now_tz = now.astimezone(tz)
            tzname = now_tz.strftime('%Z')
            if tzname and tzname != timeZone:
                return tzname
        except:
            pass

        # Fallback to timezone name
        if style == 'long':
            return timeZone.replace('_', ' ')
        elif style == 'short':
            # Try to create abbreviation
            parts = timeZone.split('/')
            return parts[-1].replace('_', ' ') if parts else timeZone

        return timeZone

    except:
        return timeZone
