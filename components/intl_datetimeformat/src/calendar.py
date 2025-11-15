"""
Calendar system support.
Handles multiple calendar systems (Gregorian, Buddhist, Japanese, Islamic, etc.).
"""

from datetime import datetime


class CalendarSupport:
    """Support for multiple calendar systems."""

    SUPPORTED_CALENDARS = {
        'gregory', 'buddhist', 'chinese', 'coptic', 'dangi', 'ethioaa', 'ethiopic',
        'hebrew', 'indian', 'islamic', 'islamic-umalqura', 'islamic-tbla',
        'islamic-civil', 'islamic-rgsa', 'iso8601', 'japanese', 'persian', 'roc',
        'islamicc'
    }

    # Japanese eras (Reiwa started May 1, 2019)
    JAPANESE_ERAS = [
        {'name': 'reiwa', 'abbr': 'R', 'start': datetime(2019, 5, 1), 'offset': 2018},
        {'name': 'heisei', 'abbr': 'H', 'start': datetime(1989, 1, 8), 'offset': 1988},
        {'name': 'showa', 'abbr': 'S', 'start': datetime(1926, 12, 25), 'offset': 1925},
        {'name': 'taisho', 'abbr': 'T', 'start': datetime(1912, 7, 30), 'offset': 1911},
        {'name': 'meiji', 'abbr': 'M', 'start': datetime(1868, 1, 1), 'offset': 1867},
    ]


def validate_calendar(calendar):
    """
    Validate calendar system identifier.

    Args:
        calendar: Calendar identifier string

    Returns:
        True if supported, False otherwise
    """
    return calendar in CalendarSupport.SUPPORTED_CALENDARS


def convert_to_calendar(date, calendar):
    """
    Convert date to specific calendar system.

    Args:
        date: Gregorian date
        calendar: Target calendar system

    Returns:
        Dict with date components in target calendar (year, month, day, era)
    """
    if not isinstance(date, datetime):
        if isinstance(date, (int, float)):
            from datetime import timezone
            date = datetime.fromtimestamp(date / 1000.0 if date > 1e10 else date, tz=timezone.utc)
        else:
            date = datetime.now()

    # Gregorian and ISO8601 use standard year
    if calendar in ('gregory', 'iso8601'):
        era = 'AD' if date.year > 0 else 'BC'
        return {
            'year': abs(date.year),
            'month': date.month,
            'day': date.day,
            'era': era
        }

    # Buddhist calendar (543 years ahead)
    elif calendar == 'buddhist':
        return {
            'year': date.year + 543,
            'month': date.month,
            'day': date.day,
            'era': 'BE'  # Buddhist Era
        }

    # Japanese calendar (era-based)
    elif calendar == 'japanese':
        # Find the appropriate era
        era_info = None
        for era in CalendarSupport.JAPANESE_ERAS:
            if date >= era['start']:
                era_info = era
                break

        if era_info:
            year = date.year - era_info['offset']
            return {
                'year': year,
                'month': date.month,
                'day': date.day,
                'era': era_info['name']
            }
        else:
            # Before Meiji era, use Gregorian
            return {
                'year': date.year,
                'month': date.month,
                'day': date.day,
                'era': 'ce'
            }

    # ROC (Republic of China) calendar (Minguo, 1911 offset)
    elif calendar == 'roc':
        roc_year = date.year - 1911
        era = 'minguo' if roc_year > 0 else 'before-roc'
        return {
            'year': abs(roc_year) if roc_year != 0 else 1,
            'month': date.month,
            'day': date.day,
            'era': era
        }

    # Islamic calendars (simplified - use approximate 354-day year)
    elif calendar.startswith('islamic'):
        # Approximate conversion (not astronomically accurate)
        # Islamic calendar started July 16, 622 CE
        gregorian_days = (date - datetime(622, 7, 16)).days
        islamic_year = int(gregorian_days / 354.367) + 1

        # Approximate month and day (simplified)
        year_days = gregorian_days % 354
        islamic_month = min(int(year_days / 29.5) + 1, 12)
        islamic_day = int(year_days % 29.5) + 1

        return {
            'year': islamic_year,
            'month': islamic_month,
            'day': islamic_day,
            'era': 'ah'  # Anno Hegirae
        }

    # Persian (Solar Hijri) calendar
    elif calendar == 'persian':
        # Simplified conversion
        persian_year = date.year - 621
        return {
            'year': persian_year,
            'month': date.month,
            'day': date.day,
            'era': 'ap'  # Anno Persarum
        }

    # Hebrew calendar (simplified)
    elif calendar == 'hebrew':
        hebrew_year = date.year + 3760
        return {
            'year': hebrew_year,
            'month': date.month,
            'day': date.day,
            'era': 'am'  # Anno Mundi
        }

    # For other calendars, return Gregorian as fallback
    else:
        return {
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'era': 'ce'
        }


def get_calendar_era(date, calendar):
    """
    Get era for date in calendar system.

    Args:
        date: Date to check
        calendar: Calendar system

    Returns:
        Era identifier (e.g., "BC", "AD", "BE", "reiwa")
    """
    converted = convert_to_calendar(date, calendar)
    return converted.get('era', 'ce')


def get_month_names(calendar, locale, format):
    """
    Get localized month names for calendar.

    Args:
        calendar: Calendar system
        locale: Locale for names
        format: Format (long, short, narrow)

    Returns:
        Array of month names
    """
    # Simplified month names (in real implementation, use CLDR data)

    if calendar in ('gregory', 'iso8601', 'buddhist', 'japanese', 'roc'):
        if locale.startswith('en'):
            if format == 'long':
                return ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
            elif format == 'short':
                return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            else:  # narrow
                return ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D']

        elif locale.startswith('ja'):
            return ['1月', '2月', '3月', '4月', '5月', '6月',
                    '7月', '8月', '9月', '10月', '11月', '12月']

        elif locale.startswith('de'):
            if format == 'long':
                return ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni',
                        'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
            else:
                return ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',
                        'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']

        elif locale.startswith('fr'):
            if format == 'long':
                return ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre']
            else:
                return ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin',
                        'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.']

    # Islamic months
    elif calendar.startswith('islamic'):
        if locale.startswith('ar'):
            return ['محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة',
                    'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة']
        else:
            return ['Muharram', 'Safar', 'Rabi I', 'Rabi II', 'Jumada I', 'Jumada II',
                    'Rajab', 'Shaban', 'Ramadan', 'Shawwal', 'Dhu al-Qadah', 'Dhu al-Hijjah']

    # Hebrew months
    elif calendar == 'hebrew':
        return ['Nisan', 'Iyar', 'Sivan', 'Tammuz', 'Av', 'Elul',
                'Tishrei', 'Cheshvan', 'Kislev', 'Tevet', 'Shevat', 'Adar']

    # Default English month names
    return ['January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December']
