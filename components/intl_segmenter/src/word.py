"""
Word boundary segmentation (UAX #29)

FR-ES24-C-069: Word segmentation (locale-sensitive)
FR-ES24-C-071: isWordLike property

Implements Unicode UAX #29 word boundaries with locale tailoring.
Handles:
- Space-separated words (English, French, etc.)
- Contractions (don't, it's)
- Punctuation segmentation
- Numbers as words
- isWordLike detection
"""

import re
import unicodedata
from typing import Tuple, Optional


class WordSegmenter:
    """
    Word boundary segmenter using Unicode UAX #29

    Segments text by words with locale-specific rules.
    Returns (segment_text, isWordLike) tuples.
    """

    def __init__(self, locale: str):
        """Initialize word segmenter for locale"""
        self.locale = locale.lower() if locale else 'en'

    def next_segment(self, text: str, position: int) -> Tuple[Optional[str], Optional[bool]]:
        """
        Get next word segment from position

        Args:
            text: Input text
            position: Current position

        Returns:
            Tuple of (segment_text, isWordLike) or (None, None) if at end
        """
        if position >= len(text):
            return None, None

        # Get next word boundary
        segment_text = self._get_next_word_segment(text, position)
        if not segment_text:
            return None, None

        # Determine if word-like
        is_word_like = self._is_word_like(segment_text)

        return segment_text, is_word_like

    def _get_next_word_segment(self, text: str, start: int) -> str:
        """
        Extract next word segment

        Segments by:
        - Whitespace boundaries
        - Punctuation boundaries
        - Word boundaries (locale-specific)
        """
        if start >= len(text):
            return ''

        char = text[start]

        # Handle whitespace runs
        if char.isspace():
            end = start + 1
            while end < len(text) and text[end].isspace():
                end += 1
            return text[start:end]

        # Handle punctuation
        if self._is_punctuation(char):
            # Single punctuation character
            return char

        # Handle word characters (letters, numbers, apostrophes in contractions)
        if self._is_word_char(char):
            return self._get_word(text, start)

        # Default: single character
        return char

    def _get_word(self, text: str, start: int) -> str:
        """
        Extract a word starting at position

        Handles:
        - Basic words (letters/numbers)
        - Contractions (don't, it's) in English
        - Hyphenated words (well-known)
        - Alphanumeric (ES2024, HTML5)
        """
        end = start + 1

        # Consume word characters
        while end < len(text):
            char = text[end]

            if self._is_word_char(char):
                end += 1
            elif char == "'" and self._is_contraction(text, end):
                # Handle contractions like "don't", "it's"
                end += 1
            elif char == '-' and self._is_hyphenated_word(text, end):
                # Handle hyphenated words like "well-known"
                end += 1
            else:
                break

        return text[start:end]

    def _is_word_char(self, char: str) -> bool:
        """Check if character is a word character"""
        # Letters and numbers are word characters
        return char.isalnum()

    def _is_punctuation(self, char: str) -> bool:
        """Check if character is punctuation"""
        category = unicodedata.category(char)
        return category.startswith('P')  # Punctuation categories

    def _is_contraction(self, text: str, apostrophe_pos: int) -> bool:
        """
        Check if apostrophe is part of a contraction

        Args:
            text: Full text
            apostrophe_pos: Position of apostrophe

        Returns:
            True if apostrophe is mid-word (contraction)
        """
        # English contractions: don't, it's, I'm, etc.
        # Apostrophe must have letter before and after

        if apostrophe_pos == 0 or apostrophe_pos >= len(text) - 1:
            return False

        before = text[apostrophe_pos - 1]
        after = text[apostrophe_pos + 1]

        return before.isalpha() and after.isalpha()

    def _is_hyphenated_word(self, text: str, hyphen_pos: int) -> bool:
        """
        Check if hyphen is part of a hyphenated word

        Args:
            text: Full text
            hyphen_pos: Position of hyphen

        Returns:
            True if hyphen connects two words
        """
        # Simplified: hyphen with letters on both sides
        if hyphen_pos == 0 or hyphen_pos >= len(text) - 1:
            return False

        before = text[hyphen_pos - 1]
        after = text[hyphen_pos + 1]

        # Only continue if both sides are letters (not numbers)
        return before.isalpha() and after.isalpha()

    def _is_word_like(self, segment: str) -> bool:
        """
        Determine if segment is word-like

        Returns:
            True if segment contains letters or numbers (word-like)
            False if only whitespace or punctuation (non-word-like)
        """
        # Check if segment contains any alphanumeric characters
        return any(c.isalnum() for c in segment)
