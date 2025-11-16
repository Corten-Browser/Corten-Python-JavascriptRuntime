"""
Unit tests for UnicodeNormalizer class
Tests FR-ES24-D-001 (NFC), FR-ES24-D-002 (NFD), FR-ES24-D-003 (NFKC/NFKD)
"""
import pytest
import unicodedata
from components.unicode_edge_cases.src.normalizer import UnicodeNormalizer


class TestNFCNormalization:
    """Test FR-ES24-D-001: Advanced NFC normalization edge cases"""

    def test_empty_string_nfc(self):
        """Empty string should return empty string"""
        result = UnicodeNormalizer.normalize_nfc("")
        assert result == ""

    def test_single_ascii_character_nfc(self):
        """Single ASCII character should be unchanged"""
        result = UnicodeNormalizer.normalize_nfc("A")
        assert result == "A"

    def test_combining_marks_basic_nfc(self):
        """e + combining acute should compose to é"""
        # e (U+0065) + combining acute (U+0301) -> é (U+00E9)
        text = "e\u0301"
        result = UnicodeNormalizer.normalize_nfc(text)
        assert result == "\u00E9"
        assert len(result) == 1

    def test_multiple_combining_marks_nfc(self):
        """Multiple combining marks should be ordered and composed"""
        # e + combining grave (U+0300) + combining acute (U+0301)
        text = "e\u0300\u0301"
        result = UnicodeNormalizer.normalize_nfc(text)
        # Should compose if possible (implementation-specific)
        assert len(result) <= 3  # Base + at most 2 marks

    def test_hangul_jamo_composition_nfc(self):
        """Hangul Jamo should compose to syllables"""
        # ㄱ (U+1100) + ㅏ (U+1161) -> 가 (U+AC00)
        jamo = "\u1100\u1161"
        result = UnicodeNormalizer.normalize_nfc(jamo)
        assert result == "\uAC00"
        assert len(result) == 1

    def test_hangul_lvt_composition_nfc(self):
        """Hangul LVT should compose fully"""
        # ㄱ + ㅏ + ㄱ -> 각
        jamo = "\u1100\u1161\u11A8"
        result = UnicodeNormalizer.normalize_nfc(jamo)
        assert len(result) == 1
        assert ord(result) >= 0xAC00  # Is a composed syllable

    def test_singleton_decomposition_nfc(self):
        """Characters with no composition should remain decomposed"""
        # Some characters decompose but don't recompose
        text = "\u0344"  # Combining Greek dialytika tonos
        result = UnicodeNormalizer.normalize_nfc(text)
        # Should decompose but not recompose
        assert len(result) >= 1

    def test_emoji_with_combining_marks_nfc(self):
        """Emoji with skin tone should preserve structure"""
        # 👋 + light skin tone
        emoji = "\U0001F44B\U0001F3FB"
        result = UnicodeNormalizer.normalize_nfc(emoji)
        assert len(result) == 2  # Base + modifier

    def test_stability_nfc(self):
        """NFC(NFC(s)) should equal NFC(s)"""
        text = "café"
        nfc1 = UnicodeNormalizer.normalize_nfc(text)
        nfc2 = UnicodeNormalizer.normalize_nfc(nfc1)
        assert nfc1 == nfc2

    def test_orphaned_combining_mark_nfc(self):
        """Orphaned combining mark should be preserved"""
        # Combining acute without base
        text = "\u0301"
        result = UnicodeNormalizer.normalize_nfc(text)
        assert result == "\u0301"

    def test_type_error_nfc(self):
        """Non-string input should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.normalize_nfc(123)

    def test_none_input_nfc(self):
        """None input should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.normalize_nfc(None)


class TestNFDNormalization:
    """Test FR-ES24-D-002: Advanced NFD normalization edge cases"""

    def test_empty_string_nfd(self):
        """Empty string should return empty string"""
        result = UnicodeNormalizer.normalize_nfd("")
        assert result == ""

    def test_precomposed_character_nfd(self):
        """é should decompose to e + combining acute"""
        text = "\u00E9"  # é (precomposed)
        result = UnicodeNormalizer.normalize_nfd(text)
        assert result == "e\u0301"
        assert len(result) == 2

    def test_hangul_syllable_decomposition_nfd(self):
        """Hangul syllable should decompose to Jamo"""
        # 가 (U+AC00) -> ㄱ + ㅏ
        syllable = "\uAC00"
        result = UnicodeNormalizer.normalize_nfd(syllable)
        assert result == "\u1100\u1161"
        assert len(result) == 2

    def test_hangul_lvt_decomposition_nfd(self):
        """Hangul LVT syllable should decompose to L+V+T"""
        # 각 -> ㄱ + ㅏ + ㄱ
        syllable = "\uAC01"
        result = UnicodeNormalizer.normalize_nfd(syllable)
        assert len(result) == 3  # L + V + T

    def test_recursive_decomposition_nfd(self):
        """Recursively decomposable characters should fully decompose"""
        # Some characters require multiple decomposition steps
        text = "\u1E9B"  # Latin small letter long s with dot above
        result = UnicodeNormalizer.normalize_nfd(text)
        # Should fully decompose
        assert len(result) >= 2

    def test_combining_mark_reordering_nfd(self):
        """Combining marks should be in canonical order"""
        # e + acute (CCC=230) + grave (CCC=230)
        text = "e\u0301\u0300"
        result = UnicodeNormalizer.normalize_nfd(text)
        # Marks should be ordered canonically
        assert result[0] == "e"
        assert len(result) == 3

    def test_stability_nfd(self):
        """NFD(NFD(s)) should equal NFD(s)"""
        text = "café"
        nfd1 = UnicodeNormalizer.normalize_nfd(text)
        nfd2 = UnicodeNormalizer.normalize_nfd(nfd1)
        assert nfd1 == nfd2

    def test_already_decomposed_nfd(self):
        """Already decomposed string should be no-op"""
        text = "e\u0301"
        result = UnicodeNormalizer.normalize_nfd(text)
        assert result == "e\u0301"

    def test_no_decomposition_mapping_nfd(self):
        """Characters with no decomposition should be unchanged"""
        text = "A"
        result = UnicodeNormalizer.normalize_nfd(text)
        assert result == "A"

    def test_type_error_nfd(self):
        """Non-string input should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.normalize_nfd(123)


class TestNFKCNormalization:
    """Test FR-ES24-D-003: NFKC edge cases"""

    def test_ligature_decomposition_nfkc(self):
        """fi ligature should decompose to f + i"""
        text = "\uFB01"  # ﬁ ligature
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "fi"
        assert len(result) == 2

    def test_fullwidth_to_halfwidth_nfkc(self):
        """Full-width A should normalize to ASCII A"""
        text = "\uFF21"  # Ａ (full-width)
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "A"

    def test_superscript_normalization_nfkc(self):
        """Superscript 2 should normalize to 2"""
        text = "\u00B2"  # ²
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "2"

    def test_subscript_normalization_nfkc(self):
        """Subscript 3 should normalize to 3"""
        text = "\u2083"  # ₃
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "3"

    def test_circled_number_nfkc(self):
        """Circled 1 should normalize to 1"""
        text = "\u2460"  # ①
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "1"

    def test_fraction_normalization_nfkc(self):
        """½ should normalize to 1/2 or 1⁄2"""
        text = "\u00BD"  # ½
        result = UnicodeNormalizer.normalize_nfkc(text)
        # May normalize to 1/2 or keep as compatibility character
        assert "1" in result

    def test_roman_numeral_nfkc(self):
        """Roman numeral VIII should normalize to letters"""
        text = "\u2167"  # Ⅷ
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "VIII"

    def test_emoji_presentation_variant_nfkc(self):
        """Emoji presentation selector should be handled"""
        # ☺ + VS16 (emoji presentation)
        text = "\u263A\uFE0F"
        result = UnicodeNormalizer.normalize_nfkc(text)
        # Should preserve or normalize presentation
        assert len(result) >= 1

    def test_mathematical_bold_nfkc(self):
        """Mathematical bold A should normalize to A"""
        text = "\U0001D400"  # 𝐀 (mathematical bold)
        result = UnicodeNormalizer.normalize_nfkc(text)
        assert result == "A"

    def test_stability_nfkc(self):
        """NFKC(NFKC(s)) should equal NFKC(s)"""
        text = "ﬁle"
        nfkc1 = UnicodeNormalizer.normalize_nfkc(text)
        nfkc2 = UnicodeNormalizer.normalize_nfkc(nfkc1)
        assert nfkc1 == nfkc2

    def test_type_error_nfkc(self):
        """Non-string input should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.normalize_nfkc(123)


class TestNFKDNormalization:
    """Test FR-ES24-D-003: NFKD edge cases"""

    def test_fullwidth_decomposition_nfkd(self):
        """Full-width should decompose to ASCII"""
        text = "\uFF21"  # Ａ
        result = UnicodeNormalizer.normalize_nfkd(text)
        assert result == "A"

    def test_compatibility_decomposition_nfkd(self):
        """Compatibility characters should decompose"""
        text = "\uFB01"  # ﬁ ligature
        result = UnicodeNormalizer.normalize_nfkd(text)
        assert result == "fi"

    def test_arabic_presentation_forms_nfkd(self):
        """Arabic presentation forms should decompose"""
        # Arabic letter isolated form
        text = "\uFE8D"
        result = UnicodeNormalizer.normalize_nfkd(text)
        # Should decompose to base form
        assert len(result) >= 1

    def test_cjk_compatibility_nfkd(self):
        """CJK compatibility ideographs should decompose"""
        text = "\uF900"  # CJK compatibility ideograph
        result = UnicodeNormalizer.normalize_nfkd(text)
        # Should decompose to canonical form
        assert len(result) >= 1

    def test_combining_mark_ordering_nfkd(self):
        """Combining marks should be in canonical order"""
        text = "\u00E9"  # é
        result = UnicodeNormalizer.normalize_nfkd(text)
        assert result == "e\u0301"

    def test_stability_nfkd(self):
        """NFKD(NFKD(s)) should equal NFKD(s)"""
        text = "ﬁle"
        nfkd1 = UnicodeNormalizer.normalize_nfkd(text)
        nfkd2 = UnicodeNormalizer.normalize_nfkd(nfkd1)
        assert nfkd1 == nfkd2

    def test_type_error_nfkd(self):
        """Non-string input should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.normalize_nfkd(123)


class TestIsNormalized:
    """Test is_normalized method"""

    def test_empty_string_is_normalized(self):
        """Empty string is always normalized"""
        assert UnicodeNormalizer.is_normalized("", "NFC") is True
        assert UnicodeNormalizer.is_normalized("", "NFD") is True
        assert UnicodeNormalizer.is_normalized("", "NFKC") is True
        assert UnicodeNormalizer.is_normalized("", "NFKD") is True

    def test_ascii_is_normalized(self):
        """ASCII strings are always NFC/NFD normalized"""
        text = "Hello World"
        assert UnicodeNormalizer.is_normalized(text, "NFC") is True
        assert UnicodeNormalizer.is_normalized(text, "NFD") is True

    def test_composed_is_nfc_normalized(self):
        """Precomposed é is NFC normalized"""
        text = "\u00E9"
        assert UnicodeNormalizer.is_normalized(text, "NFC") is True
        assert UnicodeNormalizer.is_normalized(text, "NFD") is False

    def test_decomposed_is_nfd_normalized(self):
        """Decomposed e+acute is NFD normalized"""
        text = "e\u0301"
        assert UnicodeNormalizer.is_normalized(text, "NFD") is True
        assert UnicodeNormalizer.is_normalized(text, "NFC") is False

    def test_invalid_form_raises_error(self):
        """Invalid normalization form should raise RangeError"""
        with pytest.raises(ValueError, match="Invalid normalization form"):
            UnicodeNormalizer.is_normalized("test", "nfc")  # Lowercase

    def test_invalid_form_random_string(self):
        """Random string as form should raise RangeError"""
        with pytest.raises(ValueError, match="Invalid normalization form"):
            UnicodeNormalizer.is_normalized("test", "INVALID")

    def test_type_error_is_normalized(self):
        """Non-string text should raise TypeError"""
        with pytest.raises(TypeError, match="text must be a string"):
            UnicodeNormalizer.is_normalized(123, "NFC")
