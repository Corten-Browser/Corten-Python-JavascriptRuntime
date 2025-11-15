"""
Unit tests for LocaleValidation - Locale validation utilities.

Tests cover:
- Validation of language subtags (ISO 639)
- Validation of script subtags (ISO 15924)
- Validation of region subtags (ISO 3166-1, UN M.49)
- Validation of calendar identifiers
- Validation of numbering system identifiers
"""

import pytest
from components.intl_locale.src.validation import LocaleValidation


class TestLanguageValidation:
    """Tests for LocaleValidation.validate_language() method."""

    def test_validate_two_letter_language(self):
        """Test validation of two-letter language codes."""
        validator = LocaleValidation()
        assert validator.validate_language("en") is True
        assert validator.validate_language("zh") is True
        assert validator.validate_language("fr") is True

    def test_validate_three_letter_language(self):
        """Test validation of three-letter language codes."""
        validator = LocaleValidation()
        assert validator.validate_language("yue") is True
        assert validator.validate_language("gsw") is True

    def test_validate_invalid_language_too_short(self):
        """Test validation rejects too short language codes."""
        validator = LocaleValidation()
        assert validator.validate_language("e") is False
        assert validator.validate_language("") is False

    def test_validate_invalid_language_too_long(self):
        """Test validation rejects too long language codes."""
        validator = LocaleValidation()
        assert validator.validate_language("engl") is False
        assert validator.validate_language("english") is False

    def test_validate_invalid_language_numeric(self):
        """Test validation rejects numeric language codes."""
        validator = LocaleValidation()
        assert validator.validate_language("e1") is False
        assert validator.validate_language("12") is False

    def test_validate_invalid_language_uppercase(self):
        """Test validation rejects uppercase language codes."""
        validator = LocaleValidation()
        # Language should be lowercase
        assert validator.validate_language("EN") is False


class TestScriptValidation:
    """Tests for LocaleValidation.validate_script() method."""

    def test_validate_common_scripts(self):
        """Test validation of common script codes."""
        validator = LocaleValidation()
        assert validator.validate_script("Latn") is True
        assert validator.validate_script("Hans") is True
        assert validator.validate_script("Hant") is True
        assert validator.validate_script("Cyrl") is True
        assert validator.validate_script("Arab") is True

    def test_validate_invalid_script_too_short(self):
        """Test validation rejects too short script codes."""
        validator = LocaleValidation()
        assert validator.validate_script("Lat") is False
        assert validator.validate_script("") is False

    def test_validate_invalid_script_too_long(self):
        """Test validation rejects too long script codes."""
        validator = LocaleValidation()
        assert validator.validate_script("Latnn") is False
        assert validator.validate_script("Latin") is False

    def test_validate_invalid_script_lowercase(self):
        """Test validation rejects lowercase script codes."""
        validator = LocaleValidation()
        # Script should be title case
        assert validator.validate_script("latn") is False

    def test_validate_invalid_script_uppercase(self):
        """Test validation rejects all uppercase script codes."""
        validator = LocaleValidation()
        # Script should be title case
        assert validator.validate_script("LATN") is False

    def test_validate_invalid_script_numeric(self):
        """Test validation rejects numeric script codes."""
        validator = LocaleValidation()
        assert validator.validate_script("L1tn") is False


class TestRegionValidation:
    """Tests for LocaleValidation.validate_region() method."""

    def test_validate_alpha_region(self):
        """Test validation of two-letter region codes."""
        validator = LocaleValidation()
        assert validator.validate_region("US") is True
        assert validator.validate_region("GB") is True
        assert validator.validate_region("CN") is True
        assert validator.validate_region("JP") is True

    def test_validate_numeric_region(self):
        """Test validation of three-digit region codes (UN M.49)."""
        validator = LocaleValidation()
        assert validator.validate_region("001") is True  # World
        assert validator.validate_region("419") is True  # Latin America
        assert validator.validate_region("150") is True  # Europe

    def test_validate_invalid_region_too_short(self):
        """Test validation rejects too short region codes."""
        validator = LocaleValidation()
        assert validator.validate_region("U") is False
        assert validator.validate_region("1") is False
        assert validator.validate_region("") is False

    def test_validate_invalid_region_too_long(self):
        """Test validation rejects too long region codes."""
        validator = LocaleValidation()
        assert validator.validate_region("USA") is False
        assert validator.validate_region("1234") is False

    def test_validate_invalid_region_lowercase(self):
        """Test validation rejects lowercase region codes."""
        validator = LocaleValidation()
        # Alpha regions should be uppercase
        assert validator.validate_region("us") is False

    def test_validate_invalid_region_mixed(self):
        """Test validation rejects mixed alpha-numeric regions."""
        validator = LocaleValidation()
        assert validator.validate_region("U1") is False
        assert validator.validate_region("1S") is False


class TestCalendarValidation:
    """Tests for LocaleValidation.validate_calendar() method."""

    def test_validate_common_calendars(self):
        """Test validation of common calendar types."""
        validator = LocaleValidation()
        assert validator.validate_calendar("gregory") is True
        assert validator.validate_calendar("buddhist") is True
        assert validator.validate_calendar("chinese") is True
        assert validator.validate_calendar("islamic") is True

    def test_validate_all_calendar_types(self):
        """Test validation of all standard calendar types."""
        validator = LocaleValidation()
        calendars = [
            "gregory", "buddhist", "chinese", "coptic", "dangi",
            "ethioaa", "ethiopic", "hebrew", "indian", "islamic",
            "islamic-civil", "islamic-rgsa", "islamic-tbla",
            "islamic-umalqura", "iso8601", "japanese", "persian", "roc"
        ]
        for calendar in calendars:
            assert validator.validate_calendar(calendar) is True, f"{calendar} should be valid"

    def test_validate_invalid_calendar(self):
        """Test validation rejects invalid calendar types."""
        validator = LocaleValidation()
        assert validator.validate_calendar("invalid") is False
        assert validator.validate_calendar("") is False
        assert validator.validate_calendar("greg") is False

    def test_validate_calendar_case_sensitive(self):
        """Test validation is case-sensitive for calendars."""
        validator = LocaleValidation()
        # Calendars should be lowercase
        assert validator.validate_calendar("GREGORY") is False
        assert validator.validate_calendar("Gregory") is False


class TestNumberingSystemValidation:
    """Tests for LocaleValidation.validate_numbering_system() method."""

    def test_validate_common_numbering_systems(self):
        """Test validation of common numbering systems."""
        validator = LocaleValidation()
        assert validator.validate_numbering_system("latn") is True
        assert validator.validate_numbering_system("arab") is True
        assert validator.validate_numbering_system("hanidec") is True

    def test_validate_all_numbering_systems(self):
        """Test validation of all standard numbering systems."""
        validator = LocaleValidation()
        systems = [
            "arab", "arabext", "bali", "beng", "deva", "fullwide",
            "gujr", "guru", "hanidec", "khmr", "knda", "laoo", "latn",
            "limb", "mlym", "mong", "mymr", "orya", "tamldec", "telu",
            "thai", "tibt"
        ]
        for system in systems:
            assert validator.validate_numbering_system(system) is True, f"{system} should be valid"

    def test_validate_invalid_numbering_system(self):
        """Test validation rejects invalid numbering systems."""
        validator = LocaleValidation()
        assert validator.validate_numbering_system("invalid") is False
        assert validator.validate_numbering_system("") is False
        assert validator.validate_numbering_system("latin") is False  # Should be 'latn'

    def test_validate_numbering_system_case_sensitive(self):
        """Test validation is case-sensitive for numbering systems."""
        validator = LocaleValidation()
        # Numbering systems should be lowercase
        assert validator.validate_numbering_system("LATN") is False
        assert validator.validate_numbering_system("Latn") is False


class TestValidationEdgeCases:
    """Tests for LocaleValidation edge cases."""

    def test_validate_language_none(self):
        """Test validation handles None input."""
        validator = LocaleValidation()
        assert validator.validate_language(None) is False

    def test_validate_script_none(self):
        """Test validation handles None input."""
        validator = LocaleValidation()
        assert validator.validate_script(None) is False

    def test_validate_region_none(self):
        """Test validation handles None input."""
        validator = LocaleValidation()
        assert validator.validate_region(None) is False

    def test_validate_calendar_none(self):
        """Test validation handles None input."""
        validator = LocaleValidation()
        assert validator.validate_calendar(None) is False

    def test_validate_numbering_system_none(self):
        """Test validation handles None input."""
        validator = LocaleValidation()
        assert validator.validate_numbering_system(None) is False

    def test_validate_language_whitespace(self):
        """Test validation rejects whitespace."""
        validator = LocaleValidation()
        assert validator.validate_language(" ") is False
        assert validator.validate_language("en ") is False

    def test_validate_script_whitespace(self):
        """Test validation rejects whitespace."""
        validator = LocaleValidation()
        assert validator.validate_script("Latn ") is False

    def test_validate_region_whitespace(self):
        """Test validation rejects whitespace."""
        validator = LocaleValidation()
        assert validator.validate_region("US ") is False
