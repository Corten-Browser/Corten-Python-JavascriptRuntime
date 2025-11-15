"""
Unit tests for UnicodeSupport class - ES2024 Unicode handling

TDD Phase: RED - Write failing tests first
Requirements tested:
- FR-ES24-021: Unicode normalization (normalize())
- FR-ES24-022: Unicode escape sequences
- FR-ES24-023: Surrogate pair handling
- FR-ES24-024: Unicode-aware length/indexing
- FR-ES24-025: Full Unicode regex support
"""

import pytest
from components.string_methods.src.unicode_support import UnicodeSupport

# Check if regex library is available (needed for Unicode properties)
try:
    import regex
    HAS_REGEX = True
except ImportError:
    HAS_REGEX = False


class TestNormalize:
    """Tests for Unicode normalization - FR-ES24-021"""

    def test_normalize_nfc(self):
        """Test normalize() with NFC (Canonical Composition)"""
        # é can be represented as single character or e + combining accent
        result = UnicodeSupport.normalize("e\u0301", "NFC")
        assert result == "\u00e9"  # Single character

    def test_normalize_nfd(self):
        """Test normalize() with NFD (Canonical Decomposition)"""
        result = UnicodeSupport.normalize("\u00e9", "NFD")
        assert result == "e\u0301"  # Decomposed

    def test_normalize_nfkc(self):
        """Test normalize() with NFKC (Compatibility Composition)"""
        # ﬁ ligature to fi
        result = UnicodeSupport.normalize("\ufb01", "NFKC")
        assert result == "fi"

    def test_normalize_nfkd(self):
        """Test normalize() with NFKD (Compatibility Decomposition)"""
        result = UnicodeSupport.normalize("\ufb01", "NFKD")
        assert result == "fi"

    def test_normalize_default_nfc(self):
        """Test normalize() defaults to NFC"""
        result = UnicodeSupport.normalize("e\u0301")
        assert result == "\u00e9"

    def test_normalize_already_normalized(self):
        """Test normalize() with already normalized string"""
        result = UnicodeSupport.normalize("hello", "NFC")
        assert result == "hello"

    def test_normalize_mixed_characters(self):
        """Test normalize() with mixed ASCII and Unicode"""
        result = UnicodeSupport.normalize("cafe\u0301", "NFC")
        assert result == "café"


class TestUnicodeLength:
    """Tests for Unicode-aware length - FR-ES24-024"""

    def test_get_unicode_length_ascii(self):
        """Test get_unicode_length() with ASCII string"""
        result = UnicodeSupport.get_unicode_length("hello")
        assert result == 5

    def test_get_unicode_length_emoji(self):
        """Test get_unicode_length() with emoji (surrogate pairs)"""
        result = UnicodeSupport.get_unicode_length("😀")
        assert result == 1  # Single code point, not 2 UTF-16 units

    def test_get_unicode_length_multiple_emoji(self):
        """Test get_unicode_length() with multiple emoji"""
        result = UnicodeSupport.get_unicode_length("😀🎉👍")
        assert result == 3

    def test_get_unicode_length_mixed(self):
        """Test get_unicode_length() with mixed ASCII and emoji"""
        result = UnicodeSupport.get_unicode_length("Hello 😀 World")
        assert result == 13  # 12 ASCII + 1 emoji

    def test_get_unicode_length_combining_marks(self):
        """Test get_unicode_length() with combining marks"""
        # e + combining accent = 1 grapheme but 2 code points
        result = UnicodeSupport.get_unicode_length("e\u0301")
        assert result == 2  # 2 code points

    def test_get_unicode_length_empty(self):
        """Test get_unicode_length() with empty string"""
        result = UnicodeSupport.get_unicode_length("")
        assert result == 0


class TestSurrogatePairs:
    """Tests for surrogate pair handling - FR-ES24-023"""

    def test_handle_surrogate_pairs_emoji(self):
        """Test handle_surrogate_pairs() with emoji"""
        result = UnicodeSupport.handle_surrogate_pairs("😀🎉")
        assert result == ["😀", "🎉"]

    def test_handle_surrogate_pairs_ascii(self):
        """Test handle_surrogate_pairs() with ASCII"""
        result = UnicodeSupport.handle_surrogate_pairs("abc")
        assert result == ["a", "b", "c"]

    def test_handle_surrogate_pairs_mixed(self):
        """Test handle_surrogate_pairs() with mixed characters"""
        result = UnicodeSupport.handle_surrogate_pairs("a😀b")
        assert result == ["a", "😀", "b"]

    def test_handle_surrogate_pairs_complex_emoji(self):
        """Test handle_surrogate_pairs() with complex emoji (ZWJ sequences)"""
        # Family emoji with ZWJ (zero-width joiner)
        family = "👨\u200d👩\u200d👧"
        result = UnicodeSupport.handle_surrogate_pairs(family)
        # Should handle as separate code points (not grapheme clusters)
        assert len(result) == 5  # man, ZWJ, woman, ZWJ, girl

    def test_handle_surrogate_pairs_empty(self):
        """Test handle_surrogate_pairs() with empty string"""
        result = UnicodeSupport.handle_surrogate_pairs("")
        assert result == []


class TestUnicodeEscapes:
    """Tests for Unicode escape sequences - FR-ES24-022"""

    def test_parse_unicode_escape_basic(self):
        """Test parsing basic Unicode escape \\uXXXX"""
        result = UnicodeSupport.parse_unicode_escape("\\u0041")
        assert result == "A"

    def test_parse_unicode_escape_emoji(self):
        """Test parsing Unicode escape for emoji (\\u{XXXXX})"""
        result = UnicodeSupport.parse_unicode_escape("\\u{1F600}")
        assert result == "😀"

    def test_parse_unicode_escape_multiple(self):
        """Test parsing multiple Unicode escapes"""
        result = UnicodeSupport.parse_unicode_escape("\\u0048\\u0069")
        assert result == "Hi"

    def test_parse_unicode_escape_mixed(self):
        """Test parsing mixed text and Unicode escapes"""
        result = UnicodeSupport.parse_unicode_escape("Hello \\u{1F600}")
        assert result == "Hello 😀"

    def test_parse_unicode_escape_invalid(self):
        """Test parsing invalid Unicode escape"""
        with pytest.raises(ValueError):
            UnicodeSupport.parse_unicode_escape("\\uXXXX")


class TestUnicodeRegex:
    """Tests for Unicode-aware regex - FR-ES24-025"""

    def test_unicode_regex_match_emoji(self):
        """Test Unicode regex matches emoji"""
        result = UnicodeSupport.unicode_regex_match("😀", r"😀")
        assert result is not None

    @pytest.mark.skipif(not HAS_REGEX, reason="regex library required for Unicode properties")
    def test_unicode_regex_match_category(self):
        """Test Unicode regex with category \\p{...}"""
        # Match emoji category
        result = UnicodeSupport.unicode_regex_match("😀", r"\p{Emoji}")
        assert result is not None

    @pytest.mark.skipif(not HAS_REGEX, reason="regex library required for Unicode properties")
    def test_unicode_regex_match_script(self):
        """Test Unicode regex with script property"""
        # Match Greek letters
        result = UnicodeSupport.unicode_regex_match("α", r"\p{Script=Greek}")
        assert result is not None

    def test_unicode_regex_match_case_insensitive(self):
        """Test Unicode regex case insensitive matching"""
        result = UnicodeSupport.unicode_regex_match("Σ", r"σ", case_insensitive=True)
        assert result is not None

    def test_unicode_regex_no_match(self):
        """Test Unicode regex when no match"""
        result = UnicodeSupport.unicode_regex_match("abc", r"😀")
        assert result is None


class TestEdgeCases:
    """Edge case tests for Unicode handling"""

    def test_normalize_very_long_string(self):
        """Test normalize() with very long string"""
        long_string = "e\u0301" * 10000
        result = UnicodeSupport.normalize(long_string, "NFC")
        assert len(result) == 10000
        assert all(c == "\u00e9" for c in result)

    def test_get_unicode_length_only_emoji(self):
        """Test get_unicode_length() with only emoji"""
        emojis = "😀" * 100
        result = UnicodeSupport.get_unicode_length(emojis)
        assert result == 100

    def test_handle_surrogate_pairs_malformed(self):
        """Test handle_surrogate_pairs() with malformed surrogate"""
        # Lone high surrogate (invalid UTF-16)
        # Python handles this gracefully
        result = UnicodeSupport.handle_surrogate_pairs("\ud800")
        # Should return something (implementation dependent)
        assert isinstance(result, list)

    def test_mixed_normalization_forms(self):
        """Test string with mixed normalization forms"""
        # Mix NFC and NFD
        mixed = "\u00e9" + "e\u0301"  # café
        result = UnicodeSupport.normalize(mixed, "NFC")
        assert result == "\u00e9\u00e9"
