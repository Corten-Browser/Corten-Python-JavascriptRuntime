"""
Unit tests for LocaleLikelySubtags - Likely subtag computation using Unicode CLDR.

Tests cover:
- FR-ES24-C-063: maximize() method - Add likely subtags using CLDR
- FR-ES24-C-064: minimize() method - Remove likely subtags using CLDR
- Adding likely script and region
- Removing likely script and region
- Round-trip maximize/minimize
"""

import pytest
from components.intl_locale.src.likely_subtags import LocaleLikelySubtags


class TestAddLikelySubtags:
    """Tests for LocaleLikelySubtags.add_likely_subtags() method."""

    def test_add_likely_subtags_simple_language(self):
        """Test adding likely subtags to simple language."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("en", None, None)
        assert result['language'] == 'en'
        assert result['script'] == 'Latn'
        assert result['region'] == 'US'

    def test_add_likely_subtags_chinese(self):
        """Test adding likely subtags to Chinese."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("zh", None, None)
        assert result['language'] == 'zh'
        assert result['script'] == 'Hans'
        assert result['region'] == 'CN'

    def test_add_likely_subtags_japanese(self):
        """Test adding likely subtags to Japanese."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("ja", None, None)
        assert result['language'] == 'ja'
        assert result['script'] == 'Jpan'
        assert result['region'] == 'JP'

    def test_add_likely_subtags_arabic(self):
        """Test adding likely subtags to Arabic."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("ar", None, None)
        assert result['language'] == 'ar'
        assert result['script'] == 'Arab'
        # Region could be various (EG, SA, etc.)
        assert result['region'] is not None

    def test_add_likely_subtags_with_script(self):
        """Test adding likely subtags when script is present."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("zh", "Hans", None)
        assert result['language'] == 'zh'
        assert result['script'] == 'Hans'
        assert result['region'] == 'CN'

    def test_add_likely_subtags_traditional_chinese(self):
        """Test adding likely subtags to traditional Chinese."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("zh", "Hant", None)
        assert result['language'] == 'zh'
        assert result['script'] == 'Hant'
        assert result['region'] in ['TW', 'HK']  # Could be Taiwan or Hong Kong

    def test_add_likely_subtags_with_region(self):
        """Test adding likely subtags when region is present."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("en", None, "GB")
        assert result['language'] == 'en'
        assert result['script'] == 'Latn'
        assert result['region'] == 'GB'

    def test_add_likely_subtags_all_present(self):
        """Test adding likely subtags when all parts are present."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("en", "Latn", "US")
        assert result['language'] == 'en'
        assert result['script'] == 'Latn'
        assert result['region'] == 'US'

    def test_add_likely_subtags_preserves_script(self):
        """Test that provided script is preserved."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("sr", "Cyrl", None)
        assert result['script'] == 'Cyrl'

    def test_add_likely_subtags_preserves_region(self):
        """Test that provided region is preserved."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("en", None, "AU")
        assert result['region'] == 'AU'


class TestRemoveLikelySubtags:
    """Tests for LocaleLikelySubtags.remove_likely_subtags() method."""

    def test_remove_likely_subtags_english(self):
        """Test removing likely subtags from English."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("en", "Latn", "US")
        assert result['language'] == 'en'
        assert result['script'] is None
        assert result['region'] is None

    def test_remove_likely_subtags_chinese_simplified(self):
        """Test removing likely subtags from Simplified Chinese."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("zh", "Hans", "CN")
        assert result['language'] == 'zh'
        assert result['script'] is None
        assert result['region'] is None

    def test_remove_likely_subtags_japanese(self):
        """Test removing likely subtags from Japanese."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("ja", "Jpan", "JP")
        assert result['language'] == 'ja'
        assert result['script'] is None
        assert result['region'] is None

    def test_remove_likely_subtags_non_default_script(self):
        """Test that non-likely script is preserved."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("zh", "Hant", "TW")
        assert result['language'] == 'zh'
        # Hant is not the likely script for 'zh' alone, so keep it
        assert result['script'] == 'Hant'

    def test_remove_likely_subtags_non_default_region(self):
        """Test that non-likely region is preserved."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("en", "Latn", "GB")
        assert result['language'] == 'en'
        # GB is not the likely region for 'en', so keep it
        assert result['region'] == 'GB'

    def test_remove_likely_subtags_language_only(self):
        """Test removing likely subtags from language-only."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("fr", None, None)
        assert result['language'] == 'fr'
        assert result['script'] is None
        assert result['region'] is None

    def test_remove_likely_subtags_script_only(self):
        """Test removing likely subtags with only script."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("sr", "Cyrl", None)
        assert result['language'] == 'sr'
        # Script should be kept if it disambiguates
        assert result['script'] == 'Cyrl'

    def test_remove_likely_subtags_region_only(self):
        """Test removing likely subtags with only region."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("pt", None, "BR")
        assert result['language'] == 'pt'
        # Region should be kept if it disambiguates
        assert result['region'] == 'BR'


class TestRoundTripMaximizeMinimize:
    """Tests for round-trip maximize then minimize operations."""

    def test_roundtrip_english(self):
        """Test maximize then minimize returns to original."""
        subtagger = LocaleLikelySubtags()
        # Start with minimal
        result1 = subtagger.add_likely_subtags("en", None, None)
        # Maximize: "en" -> "en-Latn-US"
        result2 = subtagger.remove_likely_subtags(
            result1['language'], result1['script'], result1['region']
        )
        # Minimize: "en-Latn-US" -> "en"
        assert result2['language'] == 'en'
        assert result2['script'] is None
        assert result2['region'] is None

    def test_roundtrip_chinese_simplified(self):
        """Test maximize then minimize for Chinese."""
        subtagger = LocaleLikelySubtags()
        # Start with minimal
        result1 = subtagger.add_likely_subtags("zh", None, None)
        # Maximize: "zh" -> "zh-Hans-CN"
        result2 = subtagger.remove_likely_subtags(
            result1['language'], result1['script'], result1['region']
        )
        # Minimize: "zh-Hans-CN" -> "zh"
        assert result2['language'] == 'zh'
        assert result2['script'] is None
        assert result2['region'] is None

    def test_roundtrip_japanese(self):
        """Test maximize then minimize for Japanese."""
        subtagger = LocaleLikelySubtags()
        result1 = subtagger.add_likely_subtags("ja", None, None)
        result2 = subtagger.remove_likely_subtags(
            result1['language'], result1['script'], result1['region']
        )
        assert result2['language'] == 'ja'
        assert result2['script'] is None
        assert result2['region'] is None

    def test_roundtrip_preserves_non_likely_script(self):
        """Test that non-likely script is preserved through round-trip."""
        subtagger = LocaleLikelySubtags()
        # Start with "zh-Hant" (traditional Chinese)
        result1 = subtagger.add_likely_subtags("zh", "Hant", None)
        # Should add region: "zh-Hant" -> "zh-Hant-TW"
        result2 = subtagger.remove_likely_subtags(
            result1['language'], result1['script'], result1['region']
        )
        # Should minimize to: "zh-Hant-TW" -> "zh-Hant"
        assert result2['language'] == 'zh'
        assert result2['script'] == 'Hant'

    def test_roundtrip_preserves_non_likely_region(self):
        """Test that non-likely region is preserved through round-trip."""
        subtagger = LocaleLikelySubtags()
        # Start with "en-GB" (British English)
        result1 = subtagger.add_likely_subtags("en", None, "GB")
        # Should add script: "en-GB" -> "en-Latn-GB"
        result2 = subtagger.remove_likely_subtags(
            result1['language'], result1['script'], result1['region']
        )
        # Should minimize to: "en-Latn-GB" -> "en-GB"
        assert result2['language'] == 'en'
        assert result2['region'] == 'GB'


class TestLikelySubtagsEdgeCases:
    """Tests for LocaleLikelySubtags edge cases."""

    def test_add_likely_subtags_unknown_language(self):
        """Test adding likely subtags for unknown language."""
        subtagger = LocaleLikelySubtags()
        # Unknown language should not crash, just return as-is or default
        result = subtagger.add_likely_subtags("zzz", None, None)
        assert result['language'] == 'zzz'

    def test_add_likely_subtags_uncommon_language(self):
        """Test adding likely subtags for uncommon language."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("gsw", None, None)
        assert result['language'] == 'gsw'
        # Should have likely subtags from CLDR

    def test_remove_likely_subtags_minimal_input(self):
        """Test removing likely subtags with minimal input."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.remove_likely_subtags("en", None, None)
        assert result['language'] == 'en'
        assert result['script'] is None
        assert result['region'] is None

    def test_add_likely_subtags_serbian_cyrillic(self):
        """Test Serbian with Cyrillic script."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("sr", "Cyrl", None)
        assert result['script'] == 'Cyrl'
        assert result['region'] is not None

    def test_add_likely_subtags_serbian_latin(self):
        """Test Serbian with Latin script."""
        subtagger = LocaleLikelySubtags()
        result = subtagger.add_likely_subtags("sr", "Latn", None)
        assert result['script'] == 'Latn'
        assert result['region'] is not None
