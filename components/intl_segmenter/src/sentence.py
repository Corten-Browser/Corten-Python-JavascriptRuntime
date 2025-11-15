"""
Sentence boundary segmentation (UAX #29)

FR-ES24-C-070: Sentence segmentation (locale-sensitive)

Implements Unicode UAX #29 sentence boundaries.
Handles:
- Period, question mark, exclamation point
- Abbreviations (Dr., Mr., etc.)
- Multiple punctuation (?!, ...)
- Quotes and parentheses
"""

import re
from typing import Tuple, Optional, Set


class SentenceSegmenter:
    """
    Sentence boundary segmenter using Unicode UAX #29

    Segments text by sentences with locale-specific rules.
    """

    # Common English abbreviations that don't end sentences
    ABBREVIATIONS: Set[str] = {
        'Dr', 'Mr', 'Mrs', 'Ms', 'Prof', 'Sr', 'Jr',
        'etc', 'vs', 'i.e', 'e.g', 'Ph.D', 'M.D',
        'Inc', 'Ltd', 'Co', 'Corp',
        'St', 'Ave', 'Rd', 'Blvd',  # Street abbreviations
    }

    def __init__(self, locale: str):
        """Initialize sentence segmenter for locale"""
        self.locale = locale.lower() if locale else 'en'

    def next_segment(self, text: str, position: int) -> Tuple[Optional[str], Optional[bool]]:
        """
        Get next sentence segment from position

        Args:
            text: Input text
            position: Current position

        Returns:
            Tuple of (segment_text, None) or (None, None) if at end
            isWordLike is None for sentence granularity
        """
        if position >= len(text):
            return None, None

        # Find next sentence boundary
        segment_text = self._get_next_sentence(text, position)
        if not segment_text:
            return None, None

        return segment_text, None

    def _get_next_sentence(self, text: str, start: int) -> str:
        """
        Extract next sentence starting at position

        A sentence ends at:
        - Period followed by space and capital letter (not abbreviation)
        - Question mark
        - Exclamation point
        - End of text
        """
        if start >= len(text):
            return ''

        # Find sentence boundary
        end = self._find_sentence_end(text, start)

        return text[start:end]

    def _find_sentence_end(self, text: str, start: int) -> int:
        """
        Find the end position of the sentence starting at start

        Returns:
            Index of first character after sentence boundary
        """
        position = start

        while position < len(text):
            char = text[position]

            # Check for sentence-ending punctuation
            if char in '.!?':
                # Look ahead to determine if this truly ends the sentence
                boundary_pos = self._check_sentence_boundary(text, position)
                if boundary_pos is not None:
                    return boundary_pos

            position += 1

        # End of text is end of sentence
        return len(text)

    def _check_sentence_boundary(self, text: str, punct_pos: int) -> Optional[int]:
        """
        Check if punctuation at position ends a sentence

        Args:
            text: Full text
            punct_pos: Position of punctuation (., !, ?)

        Returns:
            End position if sentence boundary, None otherwise
        """
        char = text[punct_pos]

        # For !, ? - almost always sentence boundary
        if char in '!?':
            # Include trailing punctuation (!!, ?!, etc.)
            end = punct_pos + 1
            while end < len(text) and text[end] in '!?':
                end += 1

            # Include trailing whitespace in sentence
            while end < len(text) and text[end].isspace():
                end += 1

            return end

        # For period - check if abbreviation
        if char == '.':
            # Check for abbreviation
            if self._is_abbreviation(text, punct_pos):
                return None  # Not a sentence boundary

            # Check for ellipsis (...)
            if self._is_ellipsis(text, punct_pos):
                # Ellipsis ends sentence
                end = punct_pos + 1
                while end < len(text) and text[end] == '.':
                    end += 1
                # Include trailing whitespace
                while end < len(text) and text[end].isspace():
                    end += 1
                return end

            # Regular period - include it and trailing whitespace
            end = punct_pos + 1

            # Skip whitespace after period
            while end < len(text) and text[end].isspace():
                end += 1

            # If followed by capital letter or end of text, it's a boundary
            if end >= len(text) or text[end].isupper():
                return end

            # Otherwise, might not be sentence boundary
            # (could be decimal number, etc.)
            # For simplicity, treat as boundary if followed by space
            if punct_pos + 1 < len(text) and text[punct_pos + 1].isspace():
                return end

        return None

    def _is_abbreviation(self, text: str, period_pos: int) -> bool:
        """
        Check if period is part of an abbreviation

        Args:
            text: Full text
            period_pos: Position of period

        Returns:
            True if period is in abbreviation
        """
        # Extract word before period
        word_start = period_pos - 1
        while word_start >= 0 and text[word_start].isalpha():
            word_start -= 1
        word_start += 1

        if word_start == period_pos:
            return False  # No word before period

        word = text[word_start:period_pos]

        # Check against known abbreviations
        return word in self.ABBREVIATIONS

    def _is_ellipsis(self, text: str, period_pos: int) -> bool:
        """
        Check if period is part of ellipsis (...)

        Args:
            text: Full text
            period_pos: Position of first period

        Returns:
            True if part of ellipsis
        """
        # Check for at least two more periods
        if period_pos + 2 < len(text):
            return text[period_pos:period_pos+3] == '...'

        return False
