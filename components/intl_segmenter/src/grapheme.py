"""
Grapheme cluster segmentation (UAX #29)

FR-ES24-C-068: Grapheme segmentation (extended grapheme clusters)

Implements Unicode UAX #29 grapheme cluster boundaries.
Handles:
- Combining marks (café -> c,a,f,é)
- Emoji ZWJ sequences (👨‍👩‍👧‍👦 is one cluster)
- Regional indicators (flag emojis)
- Hangul syllables
- CRLF sequences
"""

import unicodedata
import re
from typing import Tuple, Optional


class GraphemeSegmenter:
    """
    Grapheme cluster segmenter using Unicode UAX #29

    Segments text by extended grapheme clusters (user-perceived characters).
    """

    # Unicode categories for grapheme cluster boundary detection
    ZWJ = '\u200D'  # Zero-width joiner
    REGIONAL_INDICATOR_START = 0x1F1E6
    REGIONAL_INDICATOR_END = 0x1F1FF

    def __init__(self, locale: str):
        """Initialize grapheme segmenter for locale"""
        self.locale = locale

    def next_segment(self, text: str, position: int) -> Tuple[Optional[str], Optional[bool]]:
        """
        Get next grapheme cluster from position

        Args:
            text: Input text
            position: Current position

        Returns:
            Tuple of (segment_text, None) or (None, None) if at end
            isWordLike is None for grapheme granularity
        """
        if position >= len(text):
            return None, None

        # Get grapheme cluster starting at position
        cluster = self._get_grapheme_cluster(text, position)
        return cluster, None

    def _get_grapheme_cluster(self, text: str, start: int) -> str:
        """
        Extract one extended grapheme cluster starting at position

        Implements simplified UAX #29 grapheme cluster algorithm:
        - Base character + combining marks
        - Emoji ZWJ sequences
        - Regional indicator pairs
        - Hangul syllable sequences
        - CRLF
        """
        if start >= len(text):
            return ''

        # Start with base character
        end = start + 1
        base_char = text[start]

        # Special case: CRLF
        if base_char == '\r' and end < len(text) and text[end] == '\n':
            return '\r\n'

        # Regional indicator pairs (flags)
        if self._is_regional_indicator(base_char):
            if end < len(text) and self._is_regional_indicator(text[end]):
                return text[start:end+1]
            return base_char

        # Extend with combining marks, ZWJ sequences, emoji modifiers
        while end < len(text):
            next_char = text[end]

            # Check if next character extends the cluster
            if self._extends_cluster(text, end):
                end += 1
            else:
                break

        return text[start:end]

    def _extends_cluster(self, text: str, position: int) -> bool:
        """Check if character at position extends the current cluster"""
        if position >= len(text):
            return False

        char = text[position]
        codepoint = ord(char)

        # Combining marks (Mn, Mc categories)
        category = unicodedata.category(char)
        if category in ['Mn', 'Mc', 'Me']:  # Combining marks
            return True

        # Zero-width joiner (for emoji sequences)
        if char == self.ZWJ:
            return True

        # Emoji variation selectors
        if 0xFE00 <= codepoint <= 0xFE0F:
            return True

        # Emoji skin tone modifiers
        if 0x1F3FB <= codepoint <= 0x1F3FF:
            return True

        # Emoji tag sequences
        if 0xE0020 <= codepoint <= 0xE007F:
            return True

        # Check if previous char was ZWJ (continue emoji sequence)
        if position > 0 and text[position - 1] == self.ZWJ:
            # If previous was ZWJ and this is emoji, continue cluster
            if self._is_emoji(char):
                return True

        # Hangul Jamo continuation
        if self._is_hangul_continuation(text, position):
            return True

        return False

    def _is_regional_indicator(self, char: str) -> bool:
        """Check if character is a regional indicator (for flags)"""
        codepoint = ord(char)
        return self.REGIONAL_INDICATOR_START <= codepoint <= self.REGIONAL_INDICATOR_END

    def _is_emoji(self, char: str) -> bool:
        """Check if character is an emoji"""
        codepoint = ord(char)

        # Common emoji ranges
        emoji_ranges = [
            (0x1F300, 0x1F9FF),  # Miscellaneous Symbols and Pictographs, Emoticons, etc.
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F680, 0x1F6FF),  # Transport and Map Symbols
            (0x2600, 0x26FF),    # Miscellaneous Symbols
            (0x2700, 0x27BF),    # Dingbats
        ]

        return any(start <= codepoint <= end for start, end in emoji_ranges)

    def _is_hangul_continuation(self, text: str, position: int) -> bool:
        """Check if character continues a Hangul syllable sequence"""
        if position == 0:
            return False

        prev_char = text[position - 1]
        curr_char = text[position]

        # Simplified Hangul check
        # Full implementation would check Hangul Jamo sequences
        prev_hangul = self._is_hangul(prev_char)
        curr_hangul = self._is_hangul(curr_char)

        # For now, don't extend Hangul (each syllable is its own cluster)
        return False

    def _is_hangul(self, char: str) -> bool:
        """Check if character is Hangul"""
        codepoint = ord(char)
        return 0xAC00 <= codepoint <= 0xD7AF
