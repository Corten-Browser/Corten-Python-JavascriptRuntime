"""
EmojiNormalizer - Specialized handler for emoji normalization variants
Handles emoji presentation selectors, ZWJ sequences, and skin tone modifiers
"""
from typing import Dict, Optional


class EmojiNormalizer:
    """
    Specialized handler for emoji normalization variants.
    Implements FR-ES24-D-004: Emoji normalization variants.
    """

    # Emoji modifier range (skin tones)
    EMOJI_MODIFIER_MIN = 0x1F3FB  # Light skin tone
    EMOJI_MODIFIER_MAX = 0x1F3FF  # Dark skin tone

    # Variation selectors
    VS15_TEXT = 0xFE0E       # Text presentation
    VS16_EMOJI = 0xFE0F      # Emoji presentation
    ZWJ = 0x200D             # Zero-width joiner

    @staticmethod
    def normalize_emoji_presentation(text: str) -> str:
        """
        Normalize emoji presentation sequences.

        Args:
            text: String containing emoji with variation selectors

        Returns:
            String with normalized emoji presentation
        """
        if not text:
            return text

        # For now, we preserve emoji sequences as-is
        # More sophisticated normalization would require emoji database
        # This handles basic preservation of ZWJ sequences, skin tones, etc.
        return text

    @staticmethod
    def decompose_skin_tone(emoji: str) -> Dict[str, Optional[str]]:
        """
        Decompose emoji with skin tone modifier.

        Args:
            emoji: Emoji with skin tone modifier

        Returns:
            Dictionary with 'base' and 'modifier' keys
        """
        if not emoji:
            return {'base': emoji, 'modifier': None}

        # Check if string ends with a skin tone modifier
        if len(emoji) >= 2:
            last_codepoint = ord(emoji[-1])
            if EmojiNormalizer.is_emoji_modifier(last_codepoint):
                # Split base and modifier
                return {
                    'base': emoji[:-1],
                    'modifier': emoji[-1]
                }

        # No skin tone modifier
        return {'base': emoji, 'modifier': None}

    @staticmethod
    def is_emoji_modifier(codepoint: int) -> bool:
        """
        Test if character is emoji modifier (skin tone).

        Args:
            codepoint: Unicode codepoint

        Returns:
            True if codepoint is emoji modifier (U+1F3FB-U+1F3FF)
        """
        return EmojiNormalizer.EMOJI_MODIFIER_MIN <= codepoint <= EmojiNormalizer.EMOJI_MODIFIER_MAX
