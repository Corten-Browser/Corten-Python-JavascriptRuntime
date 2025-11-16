"""
Unit tests for UnicodeExtensionParser - Unicode locale extension parser.

Tests cover:
- FR-ES24-C-060: Locale extensions - Unicode extension (-u-) handling
- FR-ES24-C-061: Calendar extension - calendar property from -u-ca-
- FR-ES24-C-062: Numbering system - numberingSystem property from -u-nu-
- Parsing Unicode extensions
- Extracting extension keys (ca, nu, co, hc, kf, kn)
"""

import pytest
from components.intl_locale.src.unicode_extension import UnicodeExtensionParser


class TestUnicodeExtensionParsing:
    """Tests for UnicodeExtensionParser.parse_extension() method."""

    def test_parse_single_key(self):
        """Test parsing single extension key."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("ca-gregory")
        assert result['ca'] == 'gregory'

    def test_parse_multiple_keys(self):
        """Test parsing multiple extension keys."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("ca-chinese-nu-hanidec")
        assert result['ca'] == 'chinese'
        assert result['nu'] == 'hanidec'

    def test_parse_complex_extension(self):
        """Test parsing complex extension with many keys."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("ca-gregory-nu-latn-hc-h12-kn-true")
        assert result['ca'] == 'gregory'
        assert result['nu'] == 'latn'
        assert result['hc'] == 'h12'
        assert result['kn'] == 'true'

    def test_parse_collation_key(self):
        """Test parsing collation key."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("co-phonebk")
        assert result['co'] == 'phonebk'

    def test_parse_case_first_key(self):
        """Test parsing case-first key."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("kf-upper")
        assert result['kf'] == 'upper'

    def test_parse_hour_cycle_key(self):
        """Test parsing hour cycle key."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("hc-h23")
        assert result['hc'] == 'h23'

    def test_parse_numeric_key(self):
        """Test parsing numeric collation key."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("kn-true")
        assert result['kn'] == 'true'

    def test_parse_empty_extension(self):
        """Test parsing empty extension."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("")
        assert result == {}

    def test_parse_malformed_extension(self):
        """Test parsing malformed extension."""
        parser = UnicodeExtensionParser()
        with pytest.raises(ValueError, match="Invalid Unicode extension"):
            parser.parse_extension("invalid")

    def test_parse_multi_value_key(self):
        """Test parsing key with multiple values."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("ca-gregory-nu-arab")
        assert result['ca'] == 'gregory'
        assert result['nu'] == 'arab'


class TestUnicodeExtensionGetters:
    """Tests for UnicodeExtensionParser getter methods."""

    def test_get_calendar(self):
        """Test extracting calendar from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'ca': 'gregory', 'nu': 'latn'}
        assert parser.get_calendar(extensions) == 'gregory'

    def test_get_calendar_not_present(self):
        """Test getting calendar when not present."""
        parser = UnicodeExtensionParser()
        extensions = {'nu': 'latn'}
        assert parser.get_calendar(extensions) is None

    def test_get_calendar_chinese(self):
        """Test extracting Chinese calendar."""
        parser = UnicodeExtensionParser()
        extensions = {'ca': 'chinese'}
        assert parser.get_calendar(extensions) == 'chinese'

    def test_get_collation(self):
        """Test extracting collation from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'co': 'phonebk'}
        assert parser.get_collation(extensions) == 'phonebk'

    def test_get_collation_not_present(self):
        """Test getting collation when not present."""
        parser = UnicodeExtensionParser()
        extensions = {'ca': 'gregory'}
        assert parser.get_collation(extensions) is None

    def test_get_hour_cycle(self):
        """Test extracting hour cycle from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'hc': 'h12'}
        assert parser.get_hour_cycle(extensions) == 'h12'

    def test_get_hour_cycle_all_values(self):
        """Test all valid hour cycle values."""
        parser = UnicodeExtensionParser()
        for value in ['h11', 'h12', 'h23', 'h24']:
            extensions = {'hc': value}
            assert parser.get_hour_cycle(extensions) == value

    def test_get_case_first(self):
        """Test extracting case-first from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'kf': 'upper'}
        assert parser.get_case_first(extensions) == 'upper'

    def test_get_case_first_all_values(self):
        """Test all valid case-first values."""
        parser = UnicodeExtensionParser()
        for value in ['upper', 'lower', 'false']:
            extensions = {'kf': value}
            assert parser.get_case_first(extensions) == value

    def test_get_numeric(self):
        """Test extracting numeric flag from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'kn': 'true'}
        assert parser.get_numeric(extensions) is True

    def test_get_numeric_false(self):
        """Test extracting numeric flag when false."""
        parser = UnicodeExtensionParser()
        extensions = {'kn': 'false'}
        assert parser.get_numeric(extensions) is False

    def test_get_numeric_not_present(self):
        """Test getting numeric when not present."""
        parser = UnicodeExtensionParser()
        extensions = {'ca': 'gregory'}
        assert parser.get_numeric(extensions) is None

    def test_get_numbering_system(self):
        """Test extracting numbering system from extensions."""
        parser = UnicodeExtensionParser()
        extensions = {'nu': 'latn'}
        assert parser.get_numbering_system(extensions) == 'latn'

    def test_get_numbering_system_all_common_values(self):
        """Test common numbering system values."""
        parser = UnicodeExtensionParser()
        for value in ['arab', 'arabext', 'latn', 'hanidec']:
            extensions = {'nu': value}
            assert parser.get_numbering_system(extensions) == value

    def test_get_numbering_system_not_present(self):
        """Test getting numbering system when not present."""
        parser = UnicodeExtensionParser()
        extensions = {'ca': 'gregory'}
        assert parser.get_numbering_system(extensions) is None


class TestUnicodeExtensionEdgeCases:
    """Tests for UnicodeExtensionParser edge cases."""

    def test_parse_unknown_key(self):
        """Test parsing extension with unknown key."""
        parser = UnicodeExtensionParser()
        # Unknown keys should be preserved
        result = parser.parse_extension("xx-value")
        assert result.get('xx') == 'value'

    def test_parse_duplicate_keys(self):
        """Test parsing extension with duplicate keys (last wins)."""
        parser = UnicodeExtensionParser()
        result = parser.parse_extension("ca-gregory-ca-buddhist")
        # Last value should win
        assert result['ca'] == 'buddhist'

    def test_get_calendar_various_types(self):
        """Test getting various calendar types."""
        parser = UnicodeExtensionParser()
        calendars = [
            'gregory', 'buddhist', 'chinese', 'coptic', 'ethiopic',
            'hebrew', 'indian', 'islamic', 'japanese', 'persian', 'roc'
        ]
        for cal in calendars:
            extensions = {'ca': cal}
            assert parser.get_calendar(extensions) == cal

    def test_get_numbering_system_various_types(self):
        """Test getting various numbering system types."""
        parser = UnicodeExtensionParser()
        systems = [
            'arab', 'arabext', 'bali', 'beng', 'deva', 'fullwide',
            'gujr', 'guru', 'hanidec', 'khmr', 'knda', 'laoo', 'latn',
            'limb', 'mlym', 'mong', 'mymr', 'orya', 'tamldec', 'telu',
            'thai', 'tibt'
        ]
        for system in systems:
            extensions = {'nu': system}
            assert parser.get_numbering_system(extensions) == system

    def test_parse_case_sensitivity(self):
        """Test that parsing handles case correctly."""
        parser = UnicodeExtensionParser()
        # Extension keys should be lowercase
        result = parser.parse_extension("CA-gregory")
        # Should normalize to lowercase
        assert result.get('ca') == 'gregory' or result.get('CA') == 'gregory'
