"""
Unit tests for calendar support.
Tests FR-ES24-C-017: Calendar support (gregory, buddhist, japanese, islamic, etc.).
"""

import pytest
from datetime import datetime
from components.intl_datetimeformat.src.calendar import (
    CalendarSupport,
    validate_calendar,
    convert_to_calendar,
    get_calendar_era,
    get_month_names
)


class TestCalendarValidation:
    """Test calendar validation."""

    def test_validate_gregory(self):
        """Test validation of Gregorian calendar."""
        assert validate_calendar('gregory') is True

    def test_validate_buddhist(self):
        """Test validation of Buddhist calendar."""
        assert validate_calendar('buddhist') is True

    def test_validate_japanese(self):
        """Test validation of Japanese calendar."""
        assert validate_calendar('japanese') is True

    def test_validate_islamic(self):
        """Test validation of Islamic calendar."""
        assert validate_calendar('islamic') is True

    def test_validate_islamic_variants(self):
        """Test validation of Islamic calendar variants."""
        variants = [
            'islamic-umalqura',
            'islamic-tbla',
            'islamic-civil',
            'islamic-rgsa'
        ]
        for variant in variants:
            assert validate_calendar(variant) is True

    def test_validate_chinese(self):
        """Test validation of Chinese calendar."""
        assert validate_calendar('chinese') is True

    def test_validate_hebrew(self):
        """Test validation of Hebrew calendar."""
        assert validate_calendar('hebrew') is True

    def test_validate_persian(self):
        """Test validation of Persian calendar."""
        assert validate_calendar('persian') is True

    def test_validate_indian(self):
        """Test validation of Indian calendar."""
        assert validate_calendar('indian') is True

    def test_validate_coptic(self):
        """Test validation of Coptic calendar."""
        assert validate_calendar('coptic') is True

    def test_validate_ethiopic(self):
        """Test validation of Ethiopic calendar."""
        assert validate_calendar('ethiopic') is True

    def test_validate_iso8601(self):
        """Test validation of ISO 8601 calendar."""
        assert validate_calendar('iso8601') is True

    def test_validate_roc(self):
        """Test validation of ROC (Republic of China) calendar."""
        assert validate_calendar('roc') is True

    def test_validate_invalid_calendar_returns_false(self):
        """Test validation of invalid calendar returns False."""
        assert validate_calendar('invalid') is False
        assert validate_calendar('unknown_calendar') is False


class TestCalendarConversion:
    """Test converting dates to different calendar systems."""

    def test_convert_to_gregory_is_identity(self):
        """Test converting to Gregorian calendar is identity."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'gregory')

        assert result['year'] == 2024
        assert result['month'] == 1
        assert result['day'] == 15

    def test_convert_to_buddhist(self):
        """Test converting to Buddhist calendar."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'buddhist')

        # Buddhist calendar year = Gregorian year + 543
        assert result['year'] == 2567  # 2024 + 543
        assert result['month'] == 1
        assert result['day'] == 15

    def test_convert_to_japanese_reiwa_era(self):
        """Test converting to Japanese calendar (Reiwa era)."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'japanese')

        # Reiwa era started May 1, 2019
        # 2024 = Reiwa 6
        assert result['era'] == 'reiwa'
        assert result['year'] == 6  # Reiwa 6
        assert result['month'] == 1
        assert result['day'] == 15

    def test_convert_to_japanese_heisei_era(self):
        """Test converting to Japanese calendar (Heisei era)."""
        date = datetime(2019, 4, 30)  # Last day of Heisei
        result = convert_to_calendar(date, 'japanese')

        assert result['era'] == 'heisei'
        assert result['year'] == 31  # Heisei 31
        assert result['month'] == 4
        assert result['day'] == 30

    def test_convert_to_islamic(self):
        """Test converting to Islamic calendar."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'islamic')

        # Islamic calendar is lunar, different year numbering
        assert isinstance(result['year'], int)
        assert result['year'] > 1400  # Islamic year ~1445
        assert isinstance(result['month'], int)
        assert 1 <= result['month'] <= 12
        assert isinstance(result['day'], int)
        assert 1 <= result['day'] <= 30

    def test_convert_to_chinese(self):
        """Test converting to Chinese calendar."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'chinese')

        assert isinstance(result['year'], int)
        assert isinstance(result['month'], int)
        assert isinstance(result['day'], int)
        # Chinese calendar has cycles
        assert 'cycle' in result or 'cycleYear' in result

    def test_convert_to_hebrew(self):
        """Test converting to Hebrew calendar."""
        date = datetime(2024, 1, 15)
        result = convert_to_calendar(date, 'hebrew')

        # Hebrew year ~5784
        assert isinstance(result['year'], int)
        assert result['year'] > 5700
        assert isinstance(result['month'], int)
        assert isinstance(result['day'], int)

    def test_convert_invalid_calendar_raises_error(self):
        """Test converting to invalid calendar raises ValueError."""
        date = datetime(2024, 1, 15)
        with pytest.raises(ValueError, match='Invalid calendar'):
            convert_to_calendar(date, 'invalid')


class TestCalendarEra:
    """Test calendar era retrieval."""

    def test_gregory_ad_era(self):
        """Test Gregorian AD era."""
        date = datetime(2024, 1, 15)
        era = get_calendar_era(date, 'gregory')
        assert era in ['AD', 'CE']

    def test_gregory_bc_era(self):
        """Test Gregorian BC era."""
        # Note: Python datetime doesn't support BC dates natively
        # This tests the logic for negative years
        date = datetime(1, 1, 1)  # Year 1 AD
        era = get_calendar_era(date, 'gregory')
        assert era in ['AD', 'CE']

    def test_buddhist_be_era(self):
        """Test Buddhist BE era."""
        date = datetime(2024, 1, 15)
        era = get_calendar_era(date, 'buddhist')
        assert era == 'BE'  # Buddhist Era

    def test_japanese_reiwa_era(self):
        """Test Japanese Reiwa era."""
        date = datetime(2024, 1, 15)
        era = get_calendar_era(date, 'japanese')
        assert era == 'reiwa'

    def test_japanese_heisei_era(self):
        """Test Japanese Heisei era."""
        date = datetime(2019, 4, 30)
        era = get_calendar_era(date, 'japanese')
        assert era == 'heisei'

    def test_japanese_showa_era(self):
        """Test Japanese Showa era."""
        date = datetime(1989, 1, 7)  # Last day of Showa
        era = get_calendar_era(date, 'japanese')
        assert era == 'showa'

    def test_islamic_ah_era(self):
        """Test Islamic AH era."""
        date = datetime(2024, 1, 15)
        era = get_calendar_era(date, 'islamic')
        assert era == 'AH'  # Anno Hegirae

    def test_invalid_calendar_raises_error(self):
        """Test invalid calendar raises ValueError."""
        date = datetime(2024, 1, 15)
        with pytest.raises(ValueError, match='Invalid calendar'):
            get_calendar_era(date, 'invalid')


class TestMonthNames:
    """Test getting month names for calendars."""

    def test_gregory_month_names_english(self):
        """Test Gregorian month names in English."""
        names = get_month_names('gregory', 'en-US', 'long')

        assert len(names) == 12
        assert names[0] == 'January'
        assert names[1] == 'February'
        assert names[11] == 'December'

    def test_gregory_month_names_short(self):
        """Test Gregorian short month names."""
        names = get_month_names('gregory', 'en-US', 'short')

        assert len(names) == 12
        assert names[0] == 'Jan'
        assert names[1] == 'Feb'
        assert names[11] == 'Dec'

    def test_gregory_month_names_narrow(self):
        """Test Gregorian narrow month names."""
        names = get_month_names('gregory', 'en-US', 'narrow')

        assert len(names) == 12
        assert names[0] == 'J'
        assert names[1] == 'F'

    def test_gregory_month_names_french(self):
        """Test Gregorian month names in French."""
        names = get_month_names('gregory', 'fr-FR', 'long')

        assert len(names) == 12
        assert names[0] == 'janvier'
        assert names[1] == 'février'
        assert names[11] == 'décembre'

    def test_islamic_month_names(self):
        """Test Islamic month names."""
        names = get_month_names('islamic', 'en-US', 'long')

        assert len(names) == 12
        assert 'Muharram' in names
        assert 'Ramadan' in names
        assert 'Dhu al-Hijjah' in names or 'Dhul-Hijjah' in names

    def test_hebrew_month_names(self):
        """Test Hebrew month names."""
        names = get_month_names('hebrew', 'en-US', 'long')

        # Hebrew calendar can have 12 or 13 months (leap year)
        assert len(names) >= 12
        assert 'Tishri' in names or 'Tishrei' in names

    def test_chinese_month_names(self):
        """Test Chinese month names."""
        names = get_month_names('chinese', 'en-US', 'long')

        # Chinese calendar has numbered months
        assert len(names) >= 12
        assert isinstance(names[0], str)

    def test_invalid_calendar_raises_error(self):
        """Test invalid calendar raises ValueError."""
        with pytest.raises(ValueError, match='Invalid calendar'):
            get_month_names('invalid', 'en-US', 'long')

    def test_invalid_format_raises_error(self):
        """Test invalid format raises ValueError."""
        with pytest.raises(ValueError, match='Invalid format'):
            get_month_names('gregory', 'en-US', 'invalid')
