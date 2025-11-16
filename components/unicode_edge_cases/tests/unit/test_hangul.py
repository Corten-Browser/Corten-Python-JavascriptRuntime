"""
Unit tests for HangulNormalizer class
Tests Hangul syllable composition and decomposition
"""
import pytest
from components.unicode_edge_cases.src.hangul import HangulNormalizer


class TestComposeJamo:
    """Test Hangul Jamo composition"""

    def test_lv_composition(self):
        """L + V should compose to LV syllable"""
        # ㄱ (U+1100) + ㅏ (U+1161) -> 가 (U+AC00)
        jamo = "\u1100\u1161"
        result = HangulNormalizer.compose_jamo(jamo)
        assert result == "\uAC00"
        assert len(result) == 1

    def test_lvt_composition(self):
        """L + V + T should compose to LVT syllable"""
        # ㄱ + ㅏ + ㄱ -> 각
        jamo = "\u1100\u1161\u11A8"
        result = HangulNormalizer.compose_jamo(jamo)
        assert len(result) == 1
        assert result >= "\uAC00"

    def test_isolated_l_jamo(self):
        """Isolated L Jamo should be preserved"""
        jamo = "\u1100"  # ㄱ alone
        result = HangulNormalizer.compose_jamo(jamo)
        assert result == "\u1100"

    def test_isolated_v_jamo(self):
        """Isolated V Jamo should be preserved"""
        jamo = "\u1161"  # ㅏ alone
        result = HangulNormalizer.compose_jamo(jamo)
        assert result == "\u1161"

    def test_partial_lv_sequence(self):
        """L + V + L (non-trailing) should partially compose"""
        # ㄱ + ㅏ + ㄴ (not a valid T)
        jamo = "\u1100\u1161\u1102"
        result = HangulNormalizer.compose_jamo(jamo)
        # Should compose first two, leave third
        assert len(result) == 2

    def test_multiple_syllables(self):
        """Multiple Jamo sequences should all compose"""
        # 가 + 나 in Jamo form
        jamo = "\u1100\u1161\u1102\u1161"
        result = HangulNormalizer.compose_jamo(jamo)
        assert len(result) == 2

    def test_empty_string(self):
        """Empty string should be unchanged"""
        result = HangulNormalizer.compose_jamo("")
        assert result == ""

    def test_non_jamo_characters(self):
        """Non-Jamo characters should be preserved"""
        text = "Hello \u1100\u1161"
        result = HangulNormalizer.compose_jamo(text)
        assert "Hello" in result
        assert "\uAC00" in result


class TestDecomposeSyllables:
    """Test Hangul syllable decomposition"""

    def test_lv_syllable_decomposition(self):
        """LV syllable should decompose to L + V"""
        # 가 (U+AC00) -> ㄱ + ㅏ
        syllable = "\uAC00"
        result = HangulNormalizer.decompose_syllables(syllable)
        assert result == "\u1100\u1161"
        assert len(result) == 2

    def test_lvt_syllable_decomposition(self):
        """LVT syllable should decompose to L + V + T"""
        # 각 -> ㄱ + ㅏ + ㄱ
        syllable = "\uAC01"
        result = HangulNormalizer.decompose_syllables(syllable)
        assert len(result) == 3
        assert result[0] == "\u1100"

    def test_multiple_syllables(self):
        """Multiple syllables should all decompose"""
        text = "\uAC00\uB098"  # 가나
        result = HangulNormalizer.decompose_syllables(text)
        assert len(result) >= 4  # At least 2 Jamo per syllable

    def test_non_hangul_preserved(self):
        """Non-Hangul characters should be preserved"""
        text = "Hello \uAC00"
        result = HangulNormalizer.decompose_syllables(text)
        assert "Hello" in result
        assert "\u1100" in result

    def test_empty_string(self):
        """Empty string should be unchanged"""
        result = HangulNormalizer.decompose_syllables("")
        assert result == ""

    def test_boundary_syllable_first(self):
        """First Hangul syllable (U+AC00)"""
        syllable = "\uAC00"
        result = HangulNormalizer.decompose_syllables(syllable)
        assert len(result) == 2

    def test_boundary_syllable_last(self):
        """Last Hangul syllable (U+D7A3)"""
        syllable = "\uD7A3"
        result = HangulNormalizer.decompose_syllables(syllable)
        assert len(result) >= 2


class TestIsHangulSyllable:
    """Test Hangul syllable detection"""

    def test_first_syllable(self):
        """First Hangul syllable"""
        assert HangulNormalizer.is_hangul_syllable(0xAC00) is True

    def test_last_syllable(self):
        """Last Hangul syllable"""
        assert HangulNormalizer.is_hangul_syllable(0xD7A3) is True

    def test_middle_syllable(self):
        """Middle Hangul syllable"""
        assert HangulNormalizer.is_hangul_syllable(0xB098) is True

    def test_before_range(self):
        """Codepoint before Hangul range"""
        assert HangulNormalizer.is_hangul_syllable(0xABFF) is False

    def test_after_range(self):
        """Codepoint after Hangul range"""
        assert HangulNormalizer.is_hangul_syllable(0xD7A4) is False

    def test_ascii(self):
        """ASCII is not Hangul syllable"""
        assert HangulNormalizer.is_hangul_syllable(ord('A')) is False

    def test_jamo_is_not_syllable(self):
        """Jamo is not a syllable"""
        assert HangulNormalizer.is_hangul_syllable(0x1100) is False
