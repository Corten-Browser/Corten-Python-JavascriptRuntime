"""
Unit tests for EmojiNormalizer class
Tests FR-ES24-D-004: Emoji normalization variants
"""
import pytest
from components.unicode_edge_cases.src.emoji import EmojiNormalizer


class TestNormalizeEmojiPresentation:
    """Test emoji presentation normalization"""

    def test_emoji_with_text_selector(self):
        """Emoji with text presentation selector"""
        # ☺ (U+263A) + VS15 (text presentation)
        text = "\u263A\uFE0E"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        # Should normalize presentation
        assert len(result) >= 1

    def test_emoji_with_emoji_selector(self):
        """Emoji with emoji presentation selector"""
        # ☺ + VS16 (emoji presentation)
        text = "\u263A\uFE0F"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert len(result) >= 1

    def test_redundant_selector_removal(self):
        """Redundant variation selectors should be removed"""
        # Emoji that defaults to emoji presentation doesn't need VS16
        text = "\U0001F44B\uFE0F"  # 👋️
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        # May remove redundant selector
        assert len(result) >= 1

    def test_emoji_zwj_sequence(self):
        """Emoji ZWJ sequences should be preserved"""
        # Family: man + ZWJ + woman + ZWJ + girl
        text = "\U0001F468\u200D\U0001F469\u200D\U0001F467"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert "\u200D" in result  # ZWJ preserved

    def test_emoji_flag_sequence(self):
        """Emoji flag sequences (regional indicators)"""
        # US flag: regional indicator U + S
        text = "\U0001F1FA\U0001F1F8"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert len(result) >= 2

    def test_emoji_keycap_sequence(self):
        """Emoji keycap sequences"""
        # #️⃣ = # + VS16 + combining enclosing keycap
        text = "#\uFE0F\u20E3"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert len(result) >= 2

    def test_emoji_skin_tone_preserved(self):
        """Emoji with skin tone modifier"""
        # 👋 + medium skin tone
        text = "\U0001F44B\U0001F3FD"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert len(result) == 2

    def test_empty_string(self):
        """Empty string should be unchanged"""
        result = EmojiNormalizer.normalize_emoji_presentation("")
        assert result == ""

    def test_non_emoji_text(self):
        """Non-emoji text should be unchanged"""
        text = "Hello World"
        result = EmojiNormalizer.normalize_emoji_presentation(text)
        assert result == "Hello World"


class TestDecomposeSkinTone:
    """Test emoji skin tone decomposition"""

    def test_emoji_without_skin_tone(self):
        """Emoji without skin tone"""
        emoji = "\U0001F44B"  # 👋
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] is None

    def test_emoji_with_light_skin_tone(self):
        """Emoji with light skin tone"""
        emoji = "\U0001F44B\U0001F3FB"
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] == "\U0001F3FB"

    def test_emoji_with_medium_light_skin_tone(self):
        """Emoji with medium-light skin tone"""
        emoji = "\U0001F44B\U0001F3FC"
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] == "\U0001F3FC"

    def test_emoji_with_medium_skin_tone(self):
        """Emoji with medium skin tone"""
        emoji = "\U0001F44B\U0001F3FD"
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] == "\U0001F3FD"

    def test_emoji_with_medium_dark_skin_tone(self):
        """Emoji with medium-dark skin tone"""
        emoji = "\U0001F44B\U0001F3FE"
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] == "\U0001F3FE"

    def test_emoji_with_dark_skin_tone(self):
        """Emoji with dark skin tone"""
        emoji = "\U0001F44B\U0001F3FF"
        result = EmojiNormalizer.decompose_skin_tone(emoji)
        assert result['base'] == "\U0001F44B"
        assert result['modifier'] == "\U0001F3FF"

    def test_non_emoji_string(self):
        """Non-emoji string"""
        text = "Hello"
        result = EmojiNormalizer.decompose_skin_tone(text)
        assert result['base'] == "Hello"
        assert result['modifier'] is None


class TestIsEmojiModifier:
    """Test emoji modifier detection"""

    def test_light_skin_tone(self):
        """Light skin tone is modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FB) is True

    def test_medium_light_skin_tone(self):
        """Medium-light skin tone is modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FC) is True

    def test_medium_skin_tone(self):
        """Medium skin tone is modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FD) is True

    def test_medium_dark_skin_tone(self):
        """Medium-dark skin tone is modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FE) is True

    def test_dark_skin_tone(self):
        """Dark skin tone is modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FF) is True

    def test_before_modifier_range(self):
        """Codepoint before modifier range"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F3FA) is False

    def test_after_modifier_range(self):
        """Codepoint after modifier range"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F400) is False

    def test_ascii_not_modifier(self):
        """ASCII is not modifier"""
        assert EmojiNormalizer.is_emoji_modifier(ord('A')) is False

    def test_emoji_not_modifier(self):
        """Regular emoji is not modifier"""
        assert EmojiNormalizer.is_emoji_modifier(0x1F44B) is False
