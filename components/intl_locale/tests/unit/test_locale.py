"""
Unit tests for IntlLocale - Main Intl.Locale class.

Tests cover:
- FR-ES24-C-055: Intl.Locale constructor - Create locale from BCP 47 tag with options
- FR-ES24-C-057: Language subtag - baseName and language properties
- FR-ES24-C-058: Script subtag - script property (ISO 15924)
- FR-ES24-C-059: Region subtag - region property (ISO 3166-1 or UN M.49)
- FR-ES24-C-060: Locale extensions - Unicode extension (-u-) handling
- FR-ES24-C-061: Calendar extension - calendar property from -u-ca-
- FR-ES24-C-062: Numbering system - numberingSystem property from -u-nu-
- FR-ES24-C-063: maximize() method - Add likely subtags using CLDR
- FR-ES24-C-064: minimize() method - Remove likely subtags using CLDR
- FR-ES24-C-065: toString() method - Serialize to canonical BCP 47
"""

import pytest
from components.intl_locale.src.locale import IntlLocale


class TestIntlLocaleConstructor:
    """Tests for IntlLocale constructor."""

    def test_constructor_simple_language(self):
        """Test constructor with simple language tag."""
        locale = IntlLocale("en")
        assert locale.language == "en"
        assert locale.script is None
        assert locale.region is None

    def test_constructor_language_region(self):
        """Test constructor with language-region tag."""
        locale = IntlLocale("en-US")
        assert locale.language == "en"
        assert locale.region == "US"

    def test_constructor_language_script_region(self):
        """Test constructor with full tag."""
        locale = IntlLocale("zh-Hans-CN")
        assert locale.language == "zh"
        assert locale.script == "Hans"
        assert locale.region == "CN"

    def test_constructor_with_options_override_region(self):
        """Test constructor with options overriding region."""
        locale = IntlLocale("en-US", {"region": "GB"})
        assert locale.language == "en"
        assert locale.region == "GB"

    def test_constructor_with_options_override_calendar(self):
        """Test constructor with options overriding calendar."""
        locale = IntlLocale("en-US-u-ca-buddhist", {"calendar": "gregory"})
        assert locale.calendar == "gregory"

    def test_constructor_with_options_add_calendar(self):
        """Test constructor with options adding calendar."""
        locale = IntlLocale("en-US", {"calendar": "gregory"})
        assert locale.calendar == "gregory"

    def test_constructor_with_options_numbering_system(self):
        """Test constructor with options adding numbering system."""
        locale = IntlLocale("en-US", {"numberingSystem": "arab"})
        assert locale.numberingSystem == "arab"

    def test_constructor_invalid_tag_raises_error(self):
        """Test constructor with invalid tag raises RangeError."""
        with pytest.raises(ValueError, match="Invalid language tag"):
            IntlLocale("")

    def test_constructor_invalid_language_raises_error(self):
        """Test constructor with invalid language raises RangeError."""
        with pytest.raises(ValueError, match="Invalid language tag"):
            IntlLocale("e")

    def test_constructor_case_normalization(self):
        """Test constructor normalizes case."""
        locale = IntlLocale("EN-us")
        assert locale.language == "en"
        assert locale.region == "US"


class TestIntlLocaleProperties:
    """Tests for IntlLocale properties."""

    def test_language_property(self):
        """Test language property."""
        locale = IntlLocale("en-US")
        assert locale.language == "en"

    def test_script_property_present(self):
        """Test script property when present."""
        locale = IntlLocale("zh-Hans-CN")
        assert locale.script == "Hans"

    def test_script_property_absent(self):
        """Test script property when absent."""
        locale = IntlLocale("en-US")
        assert locale.script is None

    def test_region_property_alpha(self):
        """Test region property with alpha code."""
        locale = IntlLocale("en-US")
        assert locale.region == "US"

    def test_region_property_numeric(self):
        """Test region property with numeric code."""
        locale = IntlLocale("es-419")
        assert locale.region == "419"

    def test_region_property_absent(self):
        """Test region property when absent."""
        locale = IntlLocale("en")
        assert locale.region is None

    def test_basename_simple(self):
        """Test baseName property for simple tag."""
        locale = IntlLocale("en")
        assert locale.baseName == "en"

    def test_basename_with_region(self):
        """Test baseName property with region."""
        locale = IntlLocale("en-US")
        assert locale.baseName == "en-US"

    def test_basename_with_script_region(self):
        """Test baseName property with script and region."""
        locale = IntlLocale("zh-Hans-CN")
        assert locale.baseName == "zh-Hans-CN"

    def test_basename_excludes_extensions(self):
        """Test baseName excludes extensions."""
        locale = IntlLocale("en-US-u-ca-gregory")
        assert locale.baseName == "en-US"

    def test_calendar_property_from_extension(self):
        """Test calendar property from extension."""
        locale = IntlLocale("en-US-u-ca-gregory")
        assert locale.calendar == "gregory"

    def test_calendar_property_from_options(self):
        """Test calendar property from options."""
        locale = IntlLocale("en-US", {"calendar": "buddhist"})
        assert locale.calendar == "buddhist"

    def test_calendar_property_absent(self):
        """Test calendar property when absent."""
        locale = IntlLocale("en-US")
        assert locale.calendar is None

    def test_numbering_system_property_from_extension(self):
        """Test numberingSystem property from extension."""
        locale = IntlLocale("zh-CN-u-nu-hanidec")
        assert locale.numberingSystem == "hanidec"

    def test_numbering_system_property_from_options(self):
        """Test numberingSystem property from options."""
        locale = IntlLocale("en-US", {"numberingSystem": "arab"})
        assert locale.numberingSystem == "arab"

    def test_numbering_system_property_absent(self):
        """Test numberingSystem property when absent."""
        locale = IntlLocale("en-US")
        assert locale.numberingSystem is None

    def test_collation_property_from_extension(self):
        """Test collation property from extension."""
        locale = IntlLocale("de-DE-u-co-phonebk")
        assert locale.collation == "phonebk"

    def test_collation_property_absent(self):
        """Test collation property when absent."""
        locale = IntlLocale("en-US")
        assert locale.collation is None

    def test_hour_cycle_property_from_extension(self):
        """Test hourCycle property from extension."""
        locale = IntlLocale("en-US-u-hc-h12")
        assert locale.hourCycle == "h12"

    def test_hour_cycle_property_absent(self):
        """Test hourCycle property when absent."""
        locale = IntlLocale("en-US")
        assert locale.hourCycle is None

    def test_case_first_property_from_extension(self):
        """Test caseFirst property from extension."""
        locale = IntlLocale("en-US-u-kf-upper")
        assert locale.caseFirst == "upper"

    def test_case_first_property_absent(self):
        """Test caseFirst property when absent."""
        locale = IntlLocale("en-US")
        assert locale.caseFirst is None

    def test_numeric_property_from_extension_true(self):
        """Test numeric property from extension (true)."""
        locale = IntlLocale("en-US-u-kn-true")
        assert locale.numeric is True

    def test_numeric_property_from_extension_false(self):
        """Test numeric property from extension (false)."""
        locale = IntlLocale("en-US-u-kn-false")
        assert locale.numeric is False

    def test_numeric_property_absent(self):
        """Test numeric property when absent."""
        locale = IntlLocale("en-US")
        assert locale.numeric is None


class TestIntlLocaleMaximize:
    """Tests for IntlLocale.maximize() method."""

    def test_maximize_simple_language(self):
        """Test maximize() on simple language."""
        locale = IntlLocale("en")
        maximized = locale.maximize()
        assert maximized.language == "en"
        assert maximized.script == "Latn"
        assert maximized.region == "US"

    def test_maximize_chinese(self):
        """Test maximize() on Chinese."""
        locale = IntlLocale("zh")
        maximized = locale.maximize()
        assert maximized.language == "zh"
        assert maximized.script == "Hans"
        assert maximized.region == "CN"

    def test_maximize_japanese(self):
        """Test maximize() on Japanese."""
        locale = IntlLocale("ja")
        maximized = locale.maximize()
        assert maximized.language == "ja"
        assert maximized.script == "Jpan"
        assert maximized.region == "JP"

    def test_maximize_preserves_extensions(self):
        """Test maximize() preserves extensions."""
        locale = IntlLocale("en-u-ca-gregory")
        maximized = locale.maximize()
        assert maximized.calendar == "gregory"

    def test_maximize_returns_new_locale(self):
        """Test maximize() returns new locale object."""
        locale = IntlLocale("en")
        maximized = locale.maximize()
        assert locale is not maximized
        assert locale.script is None
        assert maximized.script == "Latn"

    def test_maximize_already_maximized(self):
        """Test maximize() on already maximized locale."""
        locale = IntlLocale("en-Latn-US")
        maximized = locale.maximize()
        assert maximized.language == "en"
        assert maximized.script == "Latn"
        assert maximized.region == "US"


class TestIntlLocaleMinimize:
    """Tests for IntlLocale.minimize() method."""

    def test_minimize_english(self):
        """Test minimize() on English."""
        locale = IntlLocale("en-Latn-US")
        minimized = locale.minimize()
        assert minimized.language == "en"
        assert minimized.script is None
        assert minimized.region is None

    def test_minimize_chinese_simplified(self):
        """Test minimize() on Simplified Chinese."""
        locale = IntlLocale("zh-Hans-CN")
        minimized = locale.minimize()
        assert minimized.language == "zh"
        # Should be minimized
        assert minimized.baseName == "zh"

    def test_minimize_preserves_non_likely_script(self):
        """Test minimize() preserves non-likely script."""
        locale = IntlLocale("zh-Hant-TW")
        minimized = locale.minimize()
        assert minimized.language == "zh"
        assert minimized.script == "Hant"

    def test_minimize_preserves_non_likely_region(self):
        """Test minimize() preserves non-likely region."""
        locale = IntlLocale("en-GB")
        minimized = locale.minimize()
        assert minimized.language == "en"
        assert minimized.region == "GB"

    def test_minimize_preserves_extensions(self):
        """Test minimize() preserves extensions."""
        locale = IntlLocale("en-Latn-US-u-ca-gregory")
        minimized = locale.minimize()
        assert minimized.calendar == "gregory"

    def test_minimize_returns_new_locale(self):
        """Test minimize() returns new locale object."""
        locale = IntlLocale("en-Latn-US")
        minimized = locale.minimize()
        assert locale is not minimized


class TestIntlLocaleToString:
    """Tests for IntlLocale.toString() method."""

    def test_to_string_simple(self):
        """Test toString() on simple locale."""
        locale = IntlLocale("en")
        assert locale.toString() == "en"

    def test_to_string_with_region(self):
        """Test toString() with region."""
        locale = IntlLocale("en-US")
        assert locale.toString() == "en-US"

    def test_to_string_with_script_region(self):
        """Test toString() with script and region."""
        locale = IntlLocale("zh-Hans-CN")
        assert locale.toString() == "zh-Hans-CN"

    def test_to_string_with_extension(self):
        """Test toString() with extension."""
        locale = IntlLocale("en-US-u-ca-gregory")
        assert locale.toString() == "en-US-u-ca-gregory"

    def test_to_string_multiple_extensions(self):
        """Test toString() with multiple extension keys."""
        locale = IntlLocale("zh-CN-u-ca-chinese-nu-hanidec")
        result = locale.toString()
        assert result.startswith("zh-CN-u-")
        assert "ca-chinese" in result
        assert "nu-hanidec" in result

    def test_to_string_canonicalized(self):
        """Test toString() returns canonicalized form."""
        locale = IntlLocale("EN-us")
        assert locale.toString() == "en-US"

    def test_to_string_with_options(self):
        """Test toString() with options-based extensions."""
        locale = IntlLocale("en-US", {"calendar": "gregory", "numberingSystem": "latn"})
        result = locale.toString()
        assert "u-ca-gregory" in result
        assert "nu-latn" in result


class TestIntlLocaleRoundTrip:
    """Tests for round-trip operations."""

    def test_roundtrip_maximize_minimize(self):
        """Test maximize then minimize returns to minimal form."""
        locale = IntlLocale("en")
        maximized = locale.maximize()
        minimized = maximized.minimize()
        assert minimized.toString() == "en"

    def test_roundtrip_chinese(self):
        """Test maximize then minimize for Chinese."""
        locale = IntlLocale("zh")
        maximized = locale.maximize()
        minimized = maximized.minimize()
        assert minimized.toString() == "zh"

    def test_roundtrip_preserves_extensions(self):
        """Test round-trip preserves extensions."""
        locale = IntlLocale("en-u-ca-gregory")
        maximized = locale.maximize()
        minimized = maximized.minimize()
        assert minimized.calendar == "gregory"


class TestIntlLocaleEdgeCases:
    """Tests for IntlLocale edge cases."""

    def test_complex_tag_with_all_features(self):
        """Test complex tag with all features."""
        locale = IntlLocale("zh-Hans-CN-u-ca-chinese-nu-hanidec-hc-h12")
        assert locale.language == "zh"
        assert locale.script == "Hans"
        assert locale.region == "CN"
        assert locale.calendar == "chinese"
        assert locale.numberingSystem == "hanidec"
        assert locale.hourCycle == "h12"

    def test_options_override_all_extensions(self):
        """Test options override all extension values."""
        locale = IntlLocale(
            "en-US-u-ca-buddhist-nu-arab",
            {"calendar": "gregory", "numberingSystem": "latn"}
        )
        assert locale.calendar == "gregory"
        assert locale.numberingSystem == "latn"

    def test_three_letter_language_code(self):
        """Test three-letter language code."""
        locale = IntlLocale("yue-HK")
        assert locale.language == "yue"
        assert locale.region == "HK"

    def test_numeric_region_code(self):
        """Test numeric region code (UN M.49)."""
        locale = IntlLocale("es-419")
        assert locale.language == "es"
        assert locale.region == "419"

    def test_all_hour_cycle_values(self):
        """Test all hour cycle values."""
        for hc in ["h11", "h12", "h23", "h24"]:
            locale = IntlLocale(f"en-US-u-hc-{hc}")
            assert locale.hourCycle == hc

    def test_all_case_first_values(self):
        """Test all case-first values."""
        for kf in ["upper", "lower", "false"]:
            locale = IntlLocale(f"en-US-u-kf-{kf}")
            assert locale.caseFirst == kf

    def test_various_calendar_types(self):
        """Test various calendar types."""
        calendars = ["gregory", "buddhist", "chinese", "islamic", "hebrew", "japanese"]
        for cal in calendars:
            locale = IntlLocale(f"en-US-u-ca-{cal}")
            assert locale.calendar == cal

    def test_various_numbering_systems(self):
        """Test various numbering systems."""
        systems = ["latn", "arab", "hanidec", "deva", "thai"]
        for system in systems:
            locale = IntlLocale(f"en-US-u-nu-{system}")
            assert locale.numberingSystem == system

    def test_locale_is_immutable(self):
        """Test that locale objects are immutable."""
        locale = IntlLocale("en-US")
        # Properties should be read-only (no setters)
        with pytest.raises(AttributeError):
            locale.language = "fr"
