"""
Core date/time formatting engine.
Handles formatting logic, pattern assembly, and part generation.
"""

from datetime import datetime, timezone
from .calendar import convert_to_calendar, get_month_names, get_calendar_era
from .timezone import apply_timezone, get_timezone_name


class FormattingEngine:
    """Core date/time formatting logic."""

    # Weekday names
    WEEKDAYS = {
        'en': {
            'long': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            'short': ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
            'narrow': ['S', 'M', 'T', 'W', 'T', 'F', 'S']
        },
        'de': {
            'long': ['Sonntag', 'Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag', 'Samstag'],
            'short': ['So', 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa'],
            'narrow': ['S', 'M', 'D', 'M', 'D', 'F', 'S']
        },
        'fr': {
            'long': ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'],
            'short': ['dim.', 'lun.', 'mar.', 'mer.', 'jeu.', 'ven.', 'sam.'],
            'narrow': ['D', 'L', 'M', 'M', 'J', 'V', 'S']
        },
        'ja': {
            'long': ['日曜日', '月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日'],
            'short': ['日', '月', '火', '水', '木', '金', '土'],
            'narrow': ['日', '月', '火', '水', '木', '金', '土']
        }
    }

    # Era names
    ERAS = {
        'en': {
            'AD': {'long': 'Anno Domini', 'short': 'AD', 'narrow': 'A'},
            'BC': {'long': 'Before Christ', 'short': 'BC', 'narrow': 'B'},
            'BE': {'long': 'Buddhist Era', 'short': 'BE', 'narrow': 'BE'},
            'reiwa': {'long': 'Reiwa', 'short': 'Reiwa', 'narrow': 'R'},
            'heisei': {'long': 'Heisei', 'short': 'Heisei', 'narrow': 'H'},
        }
    }

    # Day periods
    DAY_PERIODS = {
        'en': {
            'long': {
                'am': 'in the morning', 'pm': 'in the afternoon',
                'midnight': 'midnight', 'noon': 'noon'
            },
            'short': {'am': 'AM', 'pm': 'PM', 'midnight': 'midnight', 'noon': 'noon'},
            'narrow': {'am': 'a', 'pm': 'p', 'midnight': 'mi', 'noon': 'n'}
        }
    }


def format_date_part(date, part, style, calendar, locale):
    """
    Format individual date/time component.

    Args:
        date: Date to format
        part: Part to format (year, month, day, etc.)
        style: Style (numeric, 2-digit, narrow, short, long)
        calendar: Calendar system
        locale: Locale for formatting

    Returns:
        Formatted part value string
    """
    if not isinstance(date, datetime):
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now()

    # Convert to calendar
    cal_date = convert_to_calendar(date, calendar)
    lang = locale.split('-')[0] if locale else 'en'

    if part == 'year':
        year = cal_date['year']
        if style == '2-digit':
            return f"{year % 100:02d}"
        else:  # numeric
            return str(year)

    elif part == 'month':
        month = cal_date['month']
        if style == 'numeric':
            return str(month)
        elif style == '2-digit':
            return f"{month:02d}"
        else:
            # Get month names
            month_names = get_month_names(calendar, locale, style)
            return month_names[month - 1] if month <= len(month_names) else str(month)

    elif part == 'day':
        day = cal_date['day']
        if style == '2-digit':
            return f"{day:02d}"
        else:  # numeric
            return str(day)

    elif part == 'weekday':
        weekday_idx = date.weekday()
        if weekday_idx == 6:  # Python: Monday=0, Sunday=6
            weekday_idx = 0
        else:
            weekday_idx += 1

        weekdays = FormattingEngine.WEEKDAYS.get(lang, FormattingEngine.WEEKDAYS['en'])
        return weekdays.get(style, weekdays['long'])[weekday_idx]

    elif part == 'era':
        era = cal_date.get('era', 'AD')
        eras = FormattingEngine.ERAS.get(lang, FormattingEngine.ERAS['en'])
        era_info = eras.get(era, {'long': era, 'short': era, 'narrow': era})
        return era_info.get(style, era_info.get('long', era))

    return str(date.__getattribute__(part))


def format_time_part(date, part, style, hourCycle, locale):
    """
    Format individual time component.

    Args:
        date: Date to format
        part: Part (hour, minute, second, fractionalSecondDigits, dayPeriod)
        style: Style or digit count
        hourCycle: Hour cycle preference
        locale: Locale for formatting

    Returns:
        Formatted part value string
    """
    if not isinstance(date, datetime):
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now()

    lang = locale.split('-')[0] if locale else 'en'

    if part == 'hour':
        hour = date.hour

        # Apply hour cycle
        if hourCycle == 'h11':
            # 0-11
            hour = hour % 12
        elif hourCycle == 'h12':
            # 1-12
            hour = hour % 12
            if hour == 0:
                hour = 12
        elif hourCycle == 'h23':
            # 0-23 (default)
            pass
        elif hourCycle == 'h24':
            # 1-24
            if hour == 0:
                hour = 24

        if style == '2-digit':
            return f"{hour:02d}"
        else:  # numeric
            return str(hour)

    elif part == 'minute':
        if style == '2-digit':
            return f"{date.minute:02d}"
        else:  # numeric
            return str(date.minute)

    elif part == 'second':
        if style == '2-digit':
            return f"{date.second:02d}"
        else:  # numeric
            return str(date.second)

    elif part == 'fractionalSecondDigits':
        # style is the number of digits (1, 2, or 3)
        micros = date.microsecond
        if style == 1:
            return str(micros // 100000)
        elif style == 2:
            return f"{micros // 10000:02d}"
        elif style == 3:
            return f"{micros // 1000:03d}"

    elif part == 'dayPeriod':
        hour = date.hour
        periods = FormattingEngine.DAY_PERIODS.get(lang, FormattingEngine.DAY_PERIODS['en'])

        if hour == 0:
            period_key = 'midnight'
        elif hour == 12:
            period_key = 'noon'
        elif hour < 12:
            period_key = 'am'
        else:
            period_key = 'pm'

        return periods.get(style, periods['short']).get(period_key, period_key.upper())

    return ''


def assemble_pattern(parts, locale):
    """
    Assemble parts into final formatted string.

    Args:
        parts: Array of formatted parts (dicts with 'type' and 'value')
        locale: Locale for pattern

    Returns:
        Assembled formatted string
    """
    result = []
    for part in parts:
        result.append(part['value'])
    return ''.join(result)


def format_range_pattern(startParts, endParts, locale):
    """
    Format date range with appropriate pattern.

    Args:
        startParts: Start date parts
        endParts: End date parts
        locale: Locale for pattern

    Returns:
        Formatted range string
    """
    # Find where dates differ
    differ_at = None
    for i, (start, end) in enumerate(zip(startParts, endParts)):
        if start.get('type') != 'literal' and start.get('value') != end.get('value'):
            differ_at = start.get('type')
            break

    # Build range string
    result = []

    # Add shared prefix
    shared_prefix = []
    for i, part in enumerate(startParts):
        if i < len(endParts) and part.get('type') != 'literal':
            if part.get('value') == endParts[i].get('value'):
                shared_prefix.append(part)
            else:
                break
        elif part.get('type') == 'literal' and i < len(endParts) and endParts[i].get('type') == 'literal':
            shared_prefix.append(part)
        else:
            break

    # Add start-specific parts
    start_specific = []
    for i in range(len(shared_prefix), len(startParts)):
        part = startParts[i]
        if part.get('type') != 'literal' or not start_specific:
            start_specific.append(part)

    # Add end-specific parts
    end_specific = []
    for i in range(len(shared_prefix), len(endParts)):
        part = endParts[i]
        if part.get('type') != 'literal' or not end_specific:
            end_specific.append(part)

    # Assemble range
    if shared_prefix:
        result.extend([p['value'] for p in shared_prefix])

    if start_specific:
        result.append(''.join([p['value'] for p in start_specific if p.get('type') != 'literal']))

    result.append(' – ')

    if end_specific:
        result.append(''.join([p['value'] for p in end_specific]))

    return ''.join(result)


def create_date_time_parts(date, options, locale, calendar, timeZone, hourCycle):
    """
    Create array of formatted parts from date and options.

    Args:
        date: Date to format
        options: Formatting options
        locale: Locale
        calendar: Calendar system
        timeZone: Time zone
        hourCycle: Hour cycle

    Returns:
        Array of part dictionaries with 'type' and 'value'
    """
    if not isinstance(date, datetime):
        if isinstance(date, (int, float)):
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now()

    # Apply timezone
    if timeZone:
        from .timezone import apply_timezone
        date = apply_timezone(date, timeZone)

    parts = []

    # Determine what to format based on options
    dateStyle = options.get('dateStyle')
    timeStyle = options.get('timeStyle')

    # Use style-based formatting or component-based
    if dateStyle or timeStyle:
        # Style-based formatting
        if dateStyle:
            parts.extend(_get_date_style_parts(date, dateStyle, locale, calendar))

        if dateStyle and timeStyle:
            parts.append({'type': 'literal', 'value': ' at ' if locale.startswith('en') else ' '})

        if timeStyle:
            parts.extend(_get_time_style_parts(date, timeStyle, locale, hourCycle, timeZone))

    else:
        # Component-based formatting
        parts = _get_component_parts(date, options, locale, calendar, hourCycle, timeZone)

    return parts


def _get_date_style_parts(date, style, locale, calendar):
    """Get parts for dateStyle formatting."""
    parts = []
    lang = locale.split('-')[0]

    if style == 'full':
        # Full: "Monday, January 15, 2024"
        weekday = format_date_part(date, 'weekday', 'long', calendar, locale)
        month = format_date_part(date, 'month', 'long', calendar, locale)
        day = format_date_part(date, 'day', 'numeric', calendar, locale)
        year = format_date_part(date, 'year', 'numeric', calendar, locale)

        if lang == 'en':
            parts = [
                {'type': 'weekday', 'value': weekday},
                {'type': 'literal', 'value': ', '},
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ', '},
                {'type': 'year', 'value': year},
            ]
        else:
            # Generic format for other locales
            parts = [
                {'type': 'weekday', 'value': weekday},
                {'type': 'literal', 'value': ', '},
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ' '},
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'year', 'value': year},
            ]

    elif style == 'long':
        # Long: "January 15, 2024"
        month = format_date_part(date, 'month', 'long', calendar, locale)
        day = format_date_part(date, 'day', 'numeric', calendar, locale)
        year = format_date_part(date, 'year', 'numeric', calendar, locale)

        if lang == 'en':
            parts = [
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ', '},
                {'type': 'year', 'value': year},
            ]
        else:
            parts = [
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ' '},
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'year', 'value': year},
            ]

    elif style == 'medium':
        # Medium: "Jan 15, 2024"
        month = format_date_part(date, 'month', 'short', calendar, locale)
        day = format_date_part(date, 'day', 'numeric', calendar, locale)
        year = format_date_part(date, 'year', 'numeric', calendar, locale)

        if lang == 'en':
            parts = [
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ', '},
                {'type': 'year', 'value': year},
            ]
        else:
            parts = [
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': ' '},
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': ' '},
                {'type': 'year', 'value': year},
            ]

    elif style == 'short':
        # Short: "1/15/24" or "15/1/24"
        month = format_date_part(date, 'month', 'numeric', calendar, locale)
        day = format_date_part(date, 'day', 'numeric', calendar, locale)
        year = format_date_part(date, 'year', '2-digit', calendar, locale)

        if lang == 'en':
            parts = [
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': '/'},
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': '/'},
                {'type': 'year', 'value': year},
            ]
        else:
            parts = [
                {'type': 'day', 'value': day},
                {'type': 'literal', 'value': '/'},
                {'type': 'month', 'value': month},
                {'type': 'literal', 'value': '/'},
                {'type': 'year', 'value': year},
            ]

    return parts


def _get_time_style_parts(date, style, locale, hourCycle, timeZone):
    """Get parts for timeStyle formatting."""
    parts = []

    # Default to h12 for en-US, h23 for others
    if not hourCycle:
        hourCycle = 'h12' if locale.startswith('en-US') else 'h23'

    if style == 'full':
        # Full: "2:30:45 PM Eastern Standard Time"
        hour = format_time_part(date, 'hour', '2-digit', hourCycle, locale)
        minute = format_time_part(date, 'minute', '2-digit', hourCycle, locale)
        second = format_time_part(date, 'second', '2-digit', hourCycle, locale)

        parts = [
            {'type': 'hour', 'value': hour},
            {'type': 'literal', 'value': ':'},
            {'type': 'minute', 'value': minute},
            {'type': 'literal', 'value': ':'},
            {'type': 'second', 'value': second},
        ]

        if hourCycle in ('h11', 'h12'):
            dayPeriod = format_time_part(date, 'dayPeriod', 'short', hourCycle, locale)
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'dayPeriod', 'value': dayPeriod})

        if timeZone:
            tzName = get_timezone_name(timeZone, locale, 'long')
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'timeZoneName', 'value': tzName})

    elif style == 'long':
        # Long: "2:30:45 PM UTC"
        hour = format_time_part(date, 'hour', '2-digit', hourCycle, locale)
        minute = format_time_part(date, 'minute', '2-digit', hourCycle, locale)
        second = format_time_part(date, 'second', '2-digit', hourCycle, locale)

        parts = [
            {'type': 'hour', 'value': hour},
            {'type': 'literal', 'value': ':'},
            {'type': 'minute', 'value': minute},
            {'type': 'literal', 'value': ':'},
            {'type': 'second', 'value': second},
        ]

        if hourCycle in ('h11', 'h12'):
            dayPeriod = format_time_part(date, 'dayPeriod', 'short', hourCycle, locale)
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'dayPeriod', 'value': dayPeriod})

        if timeZone:
            tzName = get_timezone_name(timeZone, locale, 'short')
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'timeZoneName', 'value': tzName})

    elif style == 'medium':
        # Medium: "2:30:45 PM"
        hour = format_time_part(date, 'hour', '2-digit', hourCycle, locale)
        minute = format_time_part(date, 'minute', '2-digit', hourCycle, locale)
        second = format_time_part(date, 'second', '2-digit', hourCycle, locale)

        parts = [
            {'type': 'hour', 'value': hour},
            {'type': 'literal', 'value': ':'},
            {'type': 'minute', 'value': minute},
            {'type': 'literal', 'value': ':'},
            {'type': 'second', 'value': second},
        ]

        if hourCycle in ('h11', 'h12'):
            dayPeriod = format_time_part(date, 'dayPeriod', 'short', hourCycle, locale)
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'dayPeriod', 'value': dayPeriod})

    elif style == 'short':
        # Short: "2:30 PM"
        hour = format_time_part(date, 'hour', '2-digit', hourCycle, locale)
        minute = format_time_part(date, 'minute', '2-digit', hourCycle, locale)

        parts = [
            {'type': 'hour', 'value': hour},
            {'type': 'literal', 'value': ':'},
            {'type': 'minute', 'value': minute},
        ]

        if hourCycle in ('h11', 'h12'):
            dayPeriod = format_time_part(date, 'dayPeriod', 'short', hourCycle, locale)
            parts.append({'type': 'literal', 'value': ' '})
            parts.append({'type': 'dayPeriod', 'value': dayPeriod})

    return parts


def _get_component_parts(date, options, locale, calendar, hourCycle, timeZone):
    """Get parts for component-based formatting."""
    parts = []
    lang = locale.split('-')[0]

    # Order matters for proper formatting
    component_order = ['era', 'year', 'month', 'day', 'weekday', 'hour', 'minute', 'second',
                      'fractionalSecondDigits', 'dayPeriod', 'timeZoneName']

    prev_was_date = False
    prev_was_time = False

    for component in component_order:
        if component not in options:
            continue

        style = options[component]

        # Add separator between date and time
        is_time_component = component in ('hour', 'minute', 'second', 'fractionalSecondDigits', 'dayPeriod', 'timeZoneName')
        is_date_component = component in ('era', 'year', 'month', 'day', 'weekday')

        if is_time_component and prev_was_date and not prev_was_time:
            parts.append({'type': 'literal', 'value': ', ' if lang == 'en' else ' '})

        # Format the component
        if component in ('year', 'month', 'day', 'weekday', 'era'):
            value = format_date_part(date, component, style, calendar, locale)
            parts.append({'type': component, 'value': value})

            # Add separators between date components
            if component == 'month' and 'day' in options:
                parts.append({'type': 'literal', 'value': ' ' if style in ('long', 'short', 'narrow') else '/'})
            elif component == 'day' and 'year' in options:
                parts.append({'type': 'literal', 'value': ', ' if 'month' in options and options['month'] in ('long', 'short', 'narrow') else '/'})

        elif component in ('hour', 'minute', 'second', 'fractionalSecondDigits', 'dayPeriod'):
            value = format_time_part(date, component, style, hourCycle or 'h23', locale)
            parts.append({'type': component, 'value': value})

            # Add time separators
            if component == 'hour' and 'minute' in options:
                parts.append({'type': 'literal', 'value': ':'})
            elif component == 'minute' and 'second' in options:
                parts.append({'type': 'literal', 'value': ':'})
            elif component == 'second' and 'fractionalSecondDigits' in options:
                parts.append({'type': 'literal', 'value': '.'})
            elif component in ('dayPeriod', 'timeZoneName'):
                if parts and parts[-1]['type'] != 'literal':
                    parts.append({'type': 'literal', 'value': ' '})

        elif component == 'timeZoneName':
            if timeZone:
                value = get_timezone_name(timeZone, locale, style)
                parts.append({'type': component, 'value': value})

        prev_was_date = is_date_component
        prev_was_time = is_time_component

    return parts
