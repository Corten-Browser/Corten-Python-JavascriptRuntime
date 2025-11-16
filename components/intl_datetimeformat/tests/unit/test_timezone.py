"""
Unit tests for time zone support.
Tests FR-ES24-C-016: IANA time zone support.
"""

import pytest
from datetime import datetime, timezone, timedelta
from components.intl_datetimeformat.src.timezone import (
    TimeZoneSupport,
    validate_iana_timezone,
    get_timezone_offset,
    apply_timezone,
    get_timezone_name
)


class TestTimeZoneValidation:
    """Test IANA time zone validation."""

    def test_validate_utc(self):
        """Test validation of UTC time zone."""
        assert validate_iana_timezone('UTC') is True

    def test_validate_gmt(self):
        """Test validation of GMT time zone."""
        assert validate_iana_timezone('GMT') is True

    def test_validate_america_new_york(self):
        """Test validation of America/New_York."""
        assert validate_iana_timezone('America/New_York') is True

    def test_validate_europe_london(self):
        """Test validation of Europe/London."""
        assert validate_iana_timezone('Europe/London') is True

    def test_validate_asia_tokyo(self):
        """Test validation of Asia/Tokyo."""
        assert validate_iana_timezone('Asia/Tokyo') is True

    def test_validate_australia_sydney(self):
        """Test validation of Australia/Sydney."""
        assert validate_iana_timezone('Australia/Sydney') is True

    def test_validate_invalid_timezone_returns_false(self):
        """Test validation of invalid time zone returns False."""
        assert validate_iana_timezone('Invalid/TimeZone') is False

    def test_validate_case_sensitive(self):
        """Test time zone validation is case-sensitive."""
        assert validate_iana_timezone('utc') is False  # Should be 'UTC'
        assert validate_iana_timezone('UTC') is True

    def test_validate_numeric_offset_invalid(self):
        """Test numeric offsets are invalid as IANA identifiers."""
        # These are valid in some contexts but not as IANA identifiers
        assert validate_iana_timezone('+05:00') is False
        assert validate_iana_timezone('-08:00') is False


class TestTimeZoneOffset:
    """Test time zone offset calculations."""

    def test_utc_offset_is_zero(self):
        """Test UTC offset is always zero."""
        date = datetime(2024, 1, 15, 12, 0, 0)
        offset = get_timezone_offset('UTC', date)
        assert offset == 0

    def test_est_offset(self):
        """Test EST offset (UTC-5)."""
        # Winter time (EST, not EDT)
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        offset = get_timezone_offset('America/New_York', date)
        assert offset == -300  # -5 hours in minutes

    def test_edt_offset(self):
        """Test EDT offset (UTC-4) during daylight saving."""
        # Summer time (EDT)
        date = datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
        offset = get_timezone_offset('America/New_York', date)
        assert offset == -240  # -4 hours in minutes

    def test_jst_offset(self):
        """Test JST offset (UTC+9)."""
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        offset = get_timezone_offset('Asia/Tokyo', date)
        assert offset == 540  # +9 hours in minutes

    def test_dst_transition_spring_forward(self):
        """Test DST transition (spring forward)."""
        tz = 'America/New_York'

        # Before DST (2:00 AM EST -> 3:00 AM EDT on March 10, 2024)
        before = datetime(2024, 3, 10, 6, 0, 0, tzinfo=timezone.utc)  # 1 AM EST
        offset_before = get_timezone_offset(tz, before)
        assert offset_before == -300  # EST

        # After DST
        after = datetime(2024, 3, 10, 7, 0, 0, tzinfo=timezone.utc)  # 3 AM EDT
        offset_after = get_timezone_offset(tz, after)
        assert offset_after == -240  # EDT

    def test_dst_transition_fall_back(self):
        """Test DST transition (fall back)."""
        tz = 'America/New_York'

        # Before fall back (2:00 AM EDT -> 1:00 AM EST on November 3, 2024)
        before = datetime(2024, 11, 3, 5, 0, 0, tzinfo=timezone.utc)  # 1 AM EDT
        offset_before = get_timezone_offset(tz, before)
        assert offset_before == -240  # EDT

        # After fall back
        after = datetime(2024, 11, 3, 7, 0, 0, tzinfo=timezone.utc)  # 2 AM EST
        offset_after = get_timezone_offset(tz, after)
        assert offset_after == -300  # EST

    def test_invalid_timezone_raises_error(self):
        """Test invalid time zone raises ValueError."""
        date = datetime(2024, 1, 15, 12, 0, 0)
        with pytest.raises(ValueError, match='Invalid time zone'):
            get_timezone_offset('Invalid/Zone', date)


class TestApplyTimezone:
    """Test applying time zone to dates."""

    def test_apply_utc_no_change(self):
        """Test applying UTC time zone doesn't change time."""
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = apply_timezone(date, 'UTC')
        assert result.hour == 12
        assert result.minute == 0

    def test_apply_est_converts_time(self):
        """Test applying EST converts time correctly."""
        # 12:00 UTC = 07:00 EST
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = apply_timezone(date, 'America/New_York')
        assert result.hour == 7  # EST is UTC-5

    def test_apply_jst_converts_time(self):
        """Test applying JST converts time correctly."""
        # 12:00 UTC = 21:00 JST
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = apply_timezone(date, 'Asia/Tokyo')
        assert result.hour == 21  # JST is UTC+9

    def test_apply_timezone_preserves_date_across_midnight(self):
        """Test time zone conversion handles date changes correctly."""
        # 01:00 UTC = previous day 20:00 EST
        date = datetime(2024, 1, 15, 1, 0, 0, tzinfo=timezone.utc)
        result = apply_timezone(date, 'America/New_York')
        assert result.day == 14
        assert result.hour == 20

    def test_apply_timezone_during_dst(self):
        """Test applying time zone during DST."""
        # Summer: 12:00 UTC = 08:00 EDT (UTC-4)
        date = datetime(2024, 7, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = apply_timezone(date, 'America/New_York')
        assert result.hour == 8  # EDT is UTC-4

    def test_apply_invalid_timezone_raises_error(self):
        """Test applying invalid time zone raises ValueError."""
        date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match='Invalid time zone'):
            apply_timezone(date, 'Invalid/Zone')


class TestTimeZoneName:
    """Test time zone name/abbreviation retrieval."""

    def test_utc_long_name(self):
        """Test UTC long name."""
        name = get_timezone_name('UTC', 'en-US', 'long')
        assert 'Coordinated Universal Time' in name or 'UTC' in name

    def test_utc_short_name(self):
        """Test UTC short name."""
        name = get_timezone_name('UTC', 'en-US', 'short')
        assert name == 'UTC'

    def test_est_long_name(self):
        """Test EST long name."""
        name = get_timezone_name('America/New_York', 'en-US', 'long')
        assert 'Eastern' in name
        assert 'Time' in name

    def test_est_short_name(self):
        """Test EST short name."""
        name = get_timezone_name('America/New_York', 'en-US', 'short')
        assert 'EST' in name or 'EDT' in name or 'ET' in name

    def test_timezone_name_different_locales(self):
        """Test time zone names in different locales."""
        # English
        en_name = get_timezone_name('Europe/Paris', 'en-US', 'long')
        assert isinstance(en_name, str)
        assert len(en_name) > 0

        # French
        fr_name = get_timezone_name('Europe/Paris', 'fr-FR', 'long')
        assert isinstance(fr_name, str)
        assert len(fr_name) > 0

    def test_timezone_name_short_offset(self):
        """Test time zone short offset style."""
        name = get_timezone_name('America/New_York', 'en-US', 'shortOffset')
        # Should be like "GMT-5" or "-05:00"
        assert 'GMT' in name or '-' in name or '+' in name

    def test_timezone_name_long_offset(self):
        """Test time zone long offset style."""
        name = get_timezone_name('America/New_York', 'en-US', 'longOffset')
        # Should be like "GMT-05:00"
        assert 'GMT' in name or '-' in name or '+' in name

    def test_invalid_timezone_name_raises_error(self):
        """Test invalid time zone raises ValueError."""
        with pytest.raises(ValueError, match='Invalid time zone'):
            get_timezone_name('Invalid/Zone', 'en-US', 'long')

    def test_invalid_style_raises_error(self):
        """Test invalid style raises ValueError."""
        with pytest.raises(ValueError, match='Invalid style'):
            get_timezone_name('UTC', 'en-US', 'invalid')
