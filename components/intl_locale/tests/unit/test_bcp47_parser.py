"""
Unit tests for BCP47Parser - BCP 47 language tag parser.

Tests cover:
- FR-ES24-C-056: Locale parsing - Parse BCP 47 strings per RFC 5646
- Parsing valid and invalid language tags
- Validation of BCP 47 grammar
- Canonicalization (proper casing)
"""

import pytest
from components.intl_locale.src.bcp47_parser import BCP47Parser


class TestBCP47ParserParsing:
    """Tests for BCP47Parser.parse() method."""

    def test_parse_simple_language(self):
        """Test parsing simple language tag."""
        parser = BCP47Parser()
        result = parser.parse("en")
        assert result['language'] == 'en'
        assert result.get('script') is None
        assert result.get('region') is None
        assert result.get('variants') == []

    def test_parse_language_region(self):
        """Test parsing language-region tag."""
        parser = BCP47Parser()
        result = parser.parse("en-US")
        assert result['language'] == 'en'
        assert result.get('script') is None
        assert result['region'] == 'US'

    def test_parse_language_script_region(self):
        """Test parsing language-script-region tag."""
        parser = BCP47Parser()
        result = parser.parse("zh-Hans-CN")
        assert result['language'] == 'zh'
        assert result['script'] == 'Hans'
        assert result['region'] == 'CN'

    def test_parse_with_variants(self):
        """Test parsing tag with variant subtags."""
        parser = BCP47Parser()
        result = parser.parse("de-CH-1996")
        assert result['language'] == 'de'
        assert result['region'] == 'CH'
        assert '1996' in result.get('variants', [])

    def test_parse_with_unicode_extension(self):
        """Test parsing tag with Unicode extension."""
        parser = BCP47Parser()
        result = parser.parse("en-US-u-ca-gregory")
        assert result['language'] == 'en'
        assert result['region'] == 'US'
        assert 'u' in result.get('extensions', {})
        assert result['extensions']['u'] == 'ca-gregory'

    def test_parse_complex_unicode_extension(self):
        """Test parsing tag with multiple Unicode extension keys."""
        parser = BCP47Parser()
        result = parser.parse("zh-Hans-CN-u-ca-chinese-nu-hanidec")
        assert result['language'] == 'zh'
        assert result['script'] == 'Hans'
        assert result['region'] == 'CN'
        assert result['extensions']['u'] == 'ca-chinese-nu-hanidec'

    def test_parse_with_private_use(self):
        """Test parsing tag with private use subtags."""
        parser = BCP47Parser()
        result = parser.parse("en-US-x-private")
        assert result['language'] == 'en'
        assert result['region'] == 'US'
        assert result.get('privateUse') == 'private'

    def test_parse_three_letter_language(self):
        """Test parsing three-letter language code."""
        parser = BCP47Parser()
        result = parser.parse("yue-HK")
        assert result['language'] == 'yue'
        assert result['region'] == 'HK'

    def test_parse_numeric_region(self):
        """Test parsing numeric region code (UN M.49)."""
        parser = BCP47Parser()
        result = parser.parse("es-419")
        assert result['language'] == 'es'
        assert result['region'] == '419'

    def test_parse_invalid_empty_tag(self):
        """Test parsing empty tag raises RangeError."""
        parser = BCP47Parser()
        with pytest.raises(ValueError, match="Invalid language tag"):
            parser.parse("")

    def test_parse_invalid_no_language(self):
        """Test parsing tag without language raises RangeError."""
        parser = BCP47Parser()
        with pytest.raises(ValueError, match="Invalid language tag"):
            parser.parse("-US")

    def test_parse_invalid_language_too_long(self):
        """Test parsing tag with invalid language (>3 letters)."""
        parser = BCP47Parser()
        with pytest.raises(ValueError, match="Invalid language tag"):
            parser.parse("engl-US")

    def test_parse_invalid_script_wrong_length(self):
        """Test parsing tag with invalid script (not 4 letters)."""
        parser = BCP47Parser()
        with pytest.raises(ValueError, match="Invalid language tag"):
            parser.parse("en-Lat-US")

    def test_parse_invalid_region_wrong_format(self):
        """Test parsing tag with invalid region."""
        parser = BCP47Parser()
        with pytest.raises(ValueError, match="Invalid language tag"):
            parser.parse("en-USA")


class TestBCP47ParserValidation:
    """Tests for BCP47Parser.validate() method."""

    def test_validate_simple_language(self):
        """Test validation of simple language tag."""
        parser = BCP47Parser()
        assert parser.validate("en") is True

    def test_validate_language_region(self):
        """Test validation of language-region tag."""
        parser = BCP47Parser()
        assert parser.validate("en-US") is True

    def test_validate_language_script_region(self):
        """Test validation of language-script-region tag."""
        parser = BCP47Parser()
        assert parser.validate("zh-Hans-CN") is True

    def test_validate_with_extension(self):
        """Test validation of tag with extension."""
        parser = BCP47Parser()
        assert parser.validate("en-US-u-ca-gregory") is True

    def test_validate_invalid_empty(self):
        """Test validation of empty tag."""
        parser = BCP47Parser()
        assert parser.validate("") is False

    def test_validate_invalid_language(self):
        """Test validation of invalid language."""
        parser = BCP47Parser()
        assert parser.validate("e") is False  # Too short
        assert parser.validate("engl") is False  # Too long

    def test_validate_invalid_script(self):
        """Test validation of invalid script."""
        parser = BCP47Parser()
        assert parser.validate("en-Lat-US") is False  # Script too short

    def test_validate_invalid_region(self):
        """Test validation of invalid region."""
        parser = BCP47Parser()
        assert parser.validate("en-USA") is False  # Region too long
        assert parser.validate("en-1") is False  # Numeric region too short


class TestBCP47ParserCanonicalization:
    """Tests for BCP47Parser.canonicalize() method."""

    def test_canonicalize_language_lowercase(self):
        """Test canonicalization converts language to lowercase."""
        parser = BCP47Parser()
        assert parser.canonicalize("EN") == "en"
        assert parser.canonicalize("EN-US") == "en-US"

    def test_canonicalize_script_titlecase(self):
        """Test canonicalization converts script to title case."""
        parser = BCP47Parser()
        assert parser.canonicalize("en-LATN") == "en-Latn"
        assert parser.canonicalize("zh-hans-CN") == "zh-Hans-CN"

    def test_canonicalize_region_uppercase(self):
        """Test canonicalization converts region to uppercase."""
        parser = BCP47Parser()
        assert parser.canonicalize("en-us") == "en-US"
        assert parser.canonicalize("zh-Hans-cn") == "zh-Hans-CN"

    def test_canonicalize_mixed_case(self):
        """Test canonicalization with mixed case input."""
        parser = BCP47Parser()
        assert parser.canonicalize("EN-latn-US") == "en-Latn-US"

    def test_canonicalize_with_extension(self):
        """Test canonicalization preserves extensions."""
        parser = BCP47Parser()
        result = parser.canonicalize("EN-US-u-ca-gregory")
        assert result == "en-US-u-ca-gregory"

    def test_canonicalize_extension_keys_lowercase(self):
        """Test canonicalization converts extension keys to lowercase."""
        parser = BCP47Parser()
        result = parser.canonicalize("en-US-u-CA-GREGORY")
        assert result == "en-US-u-ca-gregory"

    def test_canonicalize_already_canonical(self):
        """Test canonicalization of already canonical tag."""
        parser = BCP47Parser()
        tag = "en-Latn-US"
        assert parser.canonicalize(tag) == tag

    def test_canonicalize_numeric_region(self):
        """Test canonicalization preserves numeric region."""
        parser = BCP47Parser()
        assert parser.canonicalize("es-419") == "es-419"


class TestBCP47ParserEdgeCases:
    """Tests for BCP47Parser edge cases."""

    def test_parse_grandfathered_tag(self):
        """Test parsing grandfathered tags (legacy support)."""
        parser = BCP47Parser()
        # i-default is a grandfathered tag
        result = parser.parse("i-default")
        assert result is not None

    def test_validate_multiple_extensions(self):
        """Test validation of tag with multiple extensions."""
        parser = BCP47Parser()
        assert parser.validate("en-US-u-ca-gregory-t-de") is True

    def test_canonicalize_preserves_variants(self):
        """Test canonicalization preserves variant subtags."""
        parser = BCP47Parser()
        result = parser.canonicalize("de-CH-1996")
        assert "1996" in result

    def test_parse_long_variant(self):
        """Test parsing tag with 8-letter variant."""
        parser = BCP47Parser()
        result = parser.parse("sl-rozaj-biske")
        assert result['language'] == 'sl'
        assert 'rozaj' in result.get('variants', [])
        assert 'biske' in result.get('variants', [])
