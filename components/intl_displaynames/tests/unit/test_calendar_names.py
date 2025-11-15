"""
Unit tests for calendar display names
FR-ES24-C-053: Calendar display names (bonus feature from contract)
"""
import pytest


class TestCalendarDisplayNames:
    """Test calendar code to display name conversion"""

    def test_calendar_gregory_to_gregorian(self):
        """Calendar 'gregory' should return 'Gregorian Calendar'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'calendar'})
        result = dn.of('gregory')
        assert 'Gregorian' in result

    def test_calendar_islamic_to_islamic(self):
        """Calendar 'islamic' should return 'Islamic Calendar'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'calendar'})
        result = dn.of('islamic')
        assert 'Islamic' in result

    def test_calendar_hebrew_to_hebrew(self):
        """Calendar 'hebrew' should return 'Hebrew Calendar'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'calendar'})
        result = dn.of('hebrew')
        assert 'Hebrew' in result

    def test_calendar_buddhist_to_buddhist(self):
        """Calendar 'buddhist' should return 'Buddhist Calendar'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'calendar'})
        result = dn.of('buddhist')
        assert 'Buddhist' in result

    def test_calendar_localized_in_french(self):
        """Calendar names should be localized to target locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr'], {'type': 'calendar'})
        result = dn.of('gregory')
        assert 'grégorien' in result.lower() or 'gregorien' in result.lower()
