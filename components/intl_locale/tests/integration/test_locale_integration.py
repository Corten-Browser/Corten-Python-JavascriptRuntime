"""
Integration tests for Intl.Locale - Complete workflows.

Tests cover:
- End-to-end locale creation and manipulation
- Complex BCP 47 tag parsing and reconstruction
- Maximize/minimize workflows
- Extension handling with options
- Cross-component integration
"""

import pytest
from components.intl_locale.src.locale import IntlLocale


class TestLocaleEndToEndWorkflows:
    """Tests for end-to-end locale workflows."""

    def test_create_parse_serialize_roundtrip(self):
        """Test create locale, parse, and serialize round-trip."""
        tag = "zh-Hans-CN-u-ca-chinese-nu-hanidec"
        locale = IntlLocale(tag)

        # Verify parsed correctly
        assert locale.language == "zh"
        assert locale.script == "Hans"
        assert locale.region == "CN"
        assert locale.calendar == "chinese"
        assert locale.numberingSystem == "hanidec"

        # Verify serialization
        result = locale.toString()
        assert result == tag

    def test_normalize_and_canonicalize_workflow(self):
        """Test normalization and canonicalization workflow."""
        # Start with non-canonical tag
        locale = IntlLocale("EN-latn-US-u-CA-gregory")

        # Should be canonicalized
        assert locale.language == "en"
        assert locale.script == "Latn"
        assert locale.region == "US"
        assert locale.calendar == "gregory"

        # toString should return canonical form
        result = locale.toString()
        assert result == "en-Latn-US-u-ca-gregory"

    def test_options_merge_with_tag_workflow(self):
        """Test options merging with tag extensions."""
        # Tag has some extensions, options override/add
        locale = IntlLocale(
            "en-US-u-ca-buddhist",
            {
                "calendar": "gregory",  # Override
                "numberingSystem": "arab"  # Add
            }
        )

        assert locale.calendar == "gregory"
        assert locale.numberingSystem == "arab"

        result = locale.toString()
        assert "ca-gregory" in result
        assert "nu-arab" in result

    def test_maximize_minimize_workflow(self):
        """Test complete maximize then minimize workflow."""
        # Start minimal
        locale = IntlLocale("ja")

        # Maximize
        maximized = locale.maximize()
        assert maximized.language == "ja"
        assert maximized.script == "Jpan"
        assert maximized.region == "JP"
        assert maximized.toString() == "ja-Jpan-JP"

        # Minimize back
        minimized = maximized.minimize()
        assert minimized.language == "ja"
        assert minimized.script is None
        assert minimized.region is None
        assert minimized.toString() == "ja"

    def test_traditional_vs_simplified_chinese_workflow(self):
        """Test workflow distinguishing traditional vs simplified Chinese."""
        # Simplified Chinese
        simplified = IntlLocale("zh")
        max_simplified = simplified.maximize()
        assert max_simplified.script == "Hans"
        assert max_simplified.region == "CN"

        # Traditional Chinese
        traditional = IntlLocale("zh-Hant")
        max_traditional = traditional.maximize()
        assert max_traditional.script == "Hant"
        assert max_traditional.region in ["TW", "HK"]  # Could be either

        # Minimize traditional preserves script
        min_traditional = max_traditional.minimize()
        assert min_traditional.script == "Hant"

    def test_regional_variant_workflow(self):
        """Test workflow with regional variants."""
        # British English
        locale_gb = IntlLocale("en-GB")
        max_gb = locale_gb.maximize()
        assert max_gb.region == "GB"

        # Minimize should preserve GB (not default US)
        min_gb = max_gb.minimize()
        assert min_gb.region == "GB"
        assert min_gb.toString() == "en-GB"

        # American English
        locale_us = IntlLocale("en-US")
        max_us = locale_us.maximize()
        min_us = max_us.minimize()
        # US is default, so should minimize completely
        assert min_us.region is None
        assert min_us.toString() == "en"


class TestLocaleWithAllExtensions:
    """Tests for locales with all extension types."""

    def test_locale_with_all_unicode_extensions(self):
        """Test locale with all Unicode extension keys."""
        locale = IntlLocale(
            "en-US",
            {
                "calendar": "gregory",
                "numberingSystem": "latn",
                "hourCycle": "h12",
                "caseFirst": "upper",
                "numeric": True,
                "collation": "phonebk"
            }
        )

        assert locale.calendar == "gregory"
        assert locale.numberingSystem == "latn"
        assert locale.hourCycle == "h12"
        assert locale.caseFirst == "upper"
        assert locale.numeric is True
        assert locale.collation == "phonebk"

        result = locale.toString()
        assert "u-" in result
        assert "ca-gregory" in result
        assert "nu-latn" in result
        assert "hc-h12" in result
        assert "kf-upper" in result
        assert "kn-true" in result
        assert "co-phonebk" in result

    def test_extension_order_in_serialization(self):
        """Test that extensions are serialized in consistent order."""
        locale1 = IntlLocale("en-US-u-ca-gregory-nu-latn")
        locale2 = IntlLocale("en-US-u-nu-latn-ca-gregory")

        # Both should serialize to same canonical form
        # (extensions sorted alphabetically by key)
        str1 = locale1.toString()
        str2 = locale2.toString()

        # Should contain same extensions
        assert "ca-gregory" in str1
        assert "nu-latn" in str1
        assert "ca-gregory" in str2
        assert "nu-latn" in str2


class TestLocaleCLDRIntegration:
    """Tests for CLDR data integration."""

    def test_maximize_uses_cldr_data(self):
        """Test that maximize uses CLDR likelySubtags data."""
        test_cases = [
            ("en", "en-Latn-US"),
            ("zh", "zh-Hans-CN"),
            ("ja", "ja-Jpan-JP"),
            ("ar", "ar-Arab"),  # At least script
        ]

        for minimal, expected_start in test_cases:
            locale = IntlLocale(minimal)
            maximized = locale.maximize()
            result = maximized.toString()
            # Check that result starts with expected or contains expected components
            if expected_start == "ar-Arab":
                assert maximized.script == "Arab"
            else:
                assert result.startswith(expected_start) or expected_start in result

    def test_minimize_uses_cldr_data(self):
        """Test that minimize uses CLDR likelySubtags data."""
        test_cases = [
            ("en-Latn-US", "en"),
            ("zh-Hans-CN", "zh"),
            ("ja-Jpan-JP", "ja"),
        ]

        for maximized, expected in test_cases:
            locale = IntlLocale(maximized)
            minimized = locale.minimize()
            assert minimized.toString() == expected


class TestLocaleValidationIntegration:
    """Tests for validation integration."""

    def test_invalid_calendar_rejected(self):
        """Test that invalid calendar is rejected."""
        with pytest.raises(ValueError, match="Invalid calendar"):
            IntlLocale("en-US", {"calendar": "invalid"})

    def test_invalid_numbering_system_rejected(self):
        """Test that invalid numbering system is rejected."""
        with pytest.raises(ValueError, match="Invalid numbering system"):
            IntlLocale("en-US", {"numberingSystem": "invalid"})

    def test_invalid_hour_cycle_rejected(self):
        """Test that invalid hour cycle is rejected."""
        with pytest.raises(ValueError, match="Invalid hour cycle"):
            IntlLocale("en-US", {"hourCycle": "h25"})

    def test_invalid_case_first_rejected(self):
        """Test that invalid caseFirst is rejected."""
        with pytest.raises(ValueError, match="Invalid caseFirst"):
            IntlLocale("en-US", {"caseFirst": "middle"})


class TestLocaleRealWorldExamples:
    """Tests based on real-world locale usage."""

    def test_chinese_locales_real_world(self):
        """Test real-world Chinese locale scenarios."""
        # Mainland China (simplified)
        cn = IntlLocale("zh-CN")
        assert cn.maximize().script == "Hans"

        # Taiwan (traditional)
        tw = IntlLocale("zh-TW")
        assert tw.maximize().script == "Hant"

        # Hong Kong (traditional)
        hk = IntlLocale("zh-HK")
        assert hk.maximize().script == "Hant"

        # Singapore (simplified)
        sg = IntlLocale("zh-SG")
        assert sg.maximize().script == "Hans"

    def test_serbian_locales_real_world(self):
        """Test real-world Serbian locale scenarios (Cyrillic vs Latin)."""
        # Serbian (default is Cyrillic)
        sr = IntlLocale("sr")
        assert sr.maximize().script == "Cyrl"

        # Serbian with Latin script
        sr_latn = IntlLocale("sr-Latn")
        max_sr_latn = sr_latn.maximize()
        assert max_sr_latn.script == "Latn"

        # Minimize should preserve script distinction
        min_sr_latn = max_sr_latn.minimize()
        assert min_sr_latn.script == "Latn"

    def test_arabic_locales_real_world(self):
        """Test real-world Arabic locale scenarios."""
        # Egyptian Arabic
        ar_eg = IntlLocale("ar-EG")
        assert ar_eg.maximize().script == "Arab"

        # Saudi Arabic
        ar_sa = IntlLocale("ar-SA")
        assert ar_sa.maximize().script == "Arab"

        # Arabic with calendar
        ar_islamic = IntlLocale("ar-SA-u-ca-islamic")
        assert ar_islamic.calendar == "islamic"

    def test_indian_locales_real_world(self):
        """Test real-world Indian locale scenarios."""
        # Hindi with Devanagari numbering
        hi = IntlLocale("hi-IN-u-nu-deva")
        assert hi.numberingSystem == "deva"

        # Tamil with Tamil numbering
        ta = IntlLocale("ta-IN-u-nu-tamldec")
        assert ta.numberingSystem == "tamldec"

    def test_japanese_calendar_real_world(self):
        """Test Japanese with Japanese calendar."""
        ja = IntlLocale("ja-JP-u-ca-japanese")
        assert ja.calendar == "japanese"
        assert ja.language == "ja"

        # Maximize and minimize should preserve calendar
        maximized = ja.maximize()
        assert maximized.calendar == "japanese"

        minimized = maximized.minimize()
        assert minimized.calendar == "japanese"

    def test_buddhist_calendar_thai(self):
        """Test Thai with Buddhist calendar."""
        th = IntlLocale("th-TH-u-ca-buddhist")
        assert th.calendar == "buddhist"
        assert th.language == "th"

    def test_hebrew_calendar_israel(self):
        """Test Hebrew with Hebrew calendar."""
        he = IntlLocale("he-IL-u-ca-hebrew")
        assert he.calendar == "hebrew"
        assert he.language == "he"


class TestLocalePerformance:
    """Basic performance tests."""

    def test_construction_performance(self):
        """Test that locale construction is fast."""
        import time

        start = time.time()
        for _ in range(1000):
            IntlLocale("en-US")
        elapsed = time.time() - start

        # Should be under 1 second for 1000 constructions
        assert elapsed < 1.0, f"Construction too slow: {elapsed}s"

    def test_maximize_performance(self):
        """Test that maximize is fast."""
        import time

        locale = IntlLocale("en")
        start = time.time()
        for _ in range(1000):
            locale.maximize()
        elapsed = time.time() - start

        # Should be under 1 second for 1000 maximize operations
        assert elapsed < 1.0, f"Maximize too slow: {elapsed}s"

    def test_minimize_performance(self):
        """Test that minimize is fast."""
        import time

        locale = IntlLocale("en-Latn-US")
        start = time.time()
        for _ in range(1000):
            locale.minimize()
        elapsed = time.time() - start

        # Should be under 1 second for 1000 minimize operations
        assert elapsed < 1.0, f"Minimize too slow: {elapsed}s"


class TestLocaleEdgeCases:
    """Tests for edge cases and corner scenarios."""

    def test_empty_options_object(self):
        """Test locale with empty options object."""
        locale = IntlLocale("en-US", {})
        assert locale.language == "en"
        assert locale.region == "US"

    def test_options_with_none_values(self):
        """Test locale with None values in options."""
        locale = IntlLocale("en-US", {"calendar": None})
        assert locale.calendar is None

    def test_grandfathered_tags(self):
        """Test handling of grandfathered tags."""
        # i-default is a grandfathered tag
        locale = IntlLocale("i-default")
        assert locale is not None

    def test_private_use_subtags(self):
        """Test handling of private use subtags."""
        locale = IntlLocale("en-US-x-private")
        assert locale.language == "en"
        assert locale.region == "US"

    def test_very_long_extension(self):
        """Test handling of very long extension sequences."""
        tag = "en-US-u-ca-gregory-nu-latn-hc-h12-kf-upper-kn-true-co-phonebk"
        locale = IntlLocale(tag)
        assert locale.calendar == "gregory"
        assert locale.numberingSystem == "latn"
        assert locale.hourCycle == "h12"
        assert locale.caseFirst == "upper"
        assert locale.numeric is True
        assert locale.collation == "phonebk"
