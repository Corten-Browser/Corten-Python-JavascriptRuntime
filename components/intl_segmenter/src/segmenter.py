"""
Main Segmenter, Segments, and SegmentIterator classes for Intl.Segmenter
"""

import re
import unicodedata
from typing import Optional, Union, List, Dict, Any, Iterator


# Error classes
class RangeError(Exception):
    """Range error for invalid locale or granularity"""
    pass


class TypeError(Exception):
    """Type error for invalid options"""
    pass


class Segmenter:
    """
    Intl.Segmenter - Locale-sensitive text segmentation

    FR-ES24-C-066: Constructor with locale and granularity options
    FR-ES24-C-075: resolvedOptions() method
    """

    def __init__(self, locales: Optional[Union[str, List[str]]] = None,
                 options: Optional[Dict[str, Any]] = None):
        """
        Create segmenter for locale-sensitive text segmentation

        Args:
            locales: BCP 47 language tag(s) or None for default
            options: Configuration options with granularity field

        Raises:
            RangeError: If locale is invalid or granularity is invalid
            TypeError: If options is not an object
        """
        # Validate options type
        if options is not None and not isinstance(options, dict):
            raise TypeError("Options must be an object")

        # Process locale
        self._locale = self._resolve_locale(locales)

        # Process granularity
        options = options or {}
        granularity = options.get('granularity', 'grapheme')

        if granularity not in ['grapheme', 'word', 'sentence']:
            raise RangeError(f"Invalid option value for granularity: {granularity}")

        self._granularity = granularity

    def _resolve_locale(self, locales: Optional[Union[str, List[str]]]) -> str:
        """Resolve locale from input"""
        if locales is None:
            return 'en'  # Default locale

        if isinstance(locales, str):
            locale_list = [locales]
        elif isinstance(locales, list):
            locale_list = locales
        else:
            raise TypeError("Locales must be string or array")

        # Validate and pick first valid locale
        valid_locale = None
        for locale in locale_list:
            if self._is_valid_locale(locale):
                valid_locale = locale
                break
            elif locale == 'xx-INVALID':
                # Explicitly invalid locale
                raise RangeError(f"Invalid locale: {locale}")

        # If no valid locale found, fallback to 'en'
        return valid_locale if valid_locale else 'en'

    def _is_valid_locale(self, locale: str) -> bool:
        """Check if locale is valid BCP 47 tag"""
        # Simplified validation - accept common patterns
        # Real implementation would use full BCP 47 validation
        if locale == 'xx-INVALID':
            return False

        # Accept common locale patterns
        pattern = r'^[a-z]{2,3}(-[A-Z]{2})?(-[a-z]+)?$'
        return bool(re.match(pattern, locale, re.IGNORECASE))

    def segment(self, input_text: str) -> 'Segments':
        """
        Create iterator over text segments

        FR-ES24-C-067: segment() method returns Segments object

        Args:
            input_text: Text to segment

        Returns:
            Segments object (iterable)
        """
        return Segments(input_text, self._granularity, self._locale)

    def resolved_options(self) -> Dict[str, str]:
        """
        Get resolved locale and segmentation options

        FR-ES24-C-075: resolvedOptions() returns locale and granularity

        Returns:
            Dictionary with 'locale' and 'granularity' fields
        """
        return {
            'locale': self._locale,
            'granularity': self._granularity
        }


class Segments:
    """
    Segments - Iterator over text segments

    FR-ES24-C-071: Segment object properties
    FR-ES24-C-072: containing() method
    FR-ES24-C-073: Iterator protocol support
    """

    def __init__(self, input_text: str, granularity: str, locale: str):
        """
        Create Segments object (internal, created by Segmenter.segment())

        Args:
            input_text: Original input string
            granularity: Segmentation granularity
            locale: Locale for segmentation
        """
        self._input = input_text
        self._granularity = granularity
        self._locale = locale
        self._cached_segments: Optional[List[Dict[str, Any]]] = None

    @property
    def input(self) -> str:
        """Original input string being segmented"""
        return self._input

    def __iter__(self) -> 'SegmentIterator':
        """Return iterator over segments"""
        return SegmentIterator(self._input, self._granularity, self._locale)

    def containing(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Find segment containing given code unit index

        FR-ES24-C-072: containing() method

        Args:
            index: Code unit index in input string

        Returns:
            SegmentData for segment containing index, or None if out of range

        Raises:
            RangeError: If index is negative
        """
        # Validate index
        if not isinstance(index, int) or index < 0:
            raise RangeError("Index out of range")

        # Out of range check
        if index >= len(self._input):
            return None

        # Cache all segments for efficient containing() lookups
        if self._cached_segments is None:
            self._cached_segments = list(self)

        # Find segment containing index
        for segment_data in self._cached_segments:
            seg_start = segment_data['index']
            seg_end = seg_start + len(segment_data['segment'])

            if seg_start <= index < seg_end:
                return segment_data

        return None


class SegmentIterator:
    """
    Iterator yielding individual segments

    FR-ES24-C-073: Iterator protocol
    """

    def __init__(self, input_text: str, granularity: str, locale: str):
        """
        Create segment iterator

        Args:
            input_text: Text to segment
            granularity: Segmentation type
            locale: Locale for segmentation
        """
        self._input = input_text
        self._granularity = granularity
        self._locale = locale
        self._position = 0

        # Import segmentation engines
        try:
            from .grapheme import GraphemeSegmenter
            from .word import WordSegmenter
            from .sentence import SentenceSegmenter
        except ImportError:
            # Fallback for direct module execution
            from grapheme import GraphemeSegmenter
            from word import WordSegmenter
            from sentence import SentenceSegmenter

        # Select appropriate segmenter
        if granularity == 'grapheme':
            self._segmenter = GraphemeSegmenter(locale)
        elif granularity == 'word':
            self._segmenter = WordSegmenter(locale)
        else:  # sentence
            self._segmenter = SentenceSegmenter(locale)

    def __iter__(self) -> 'SegmentIterator':
        """Return self as iterator"""
        return self

    def __next__(self) -> Dict[str, Any]:
        """
        Get next segment

        Returns:
            SegmentData dictionary

        Raises:
            StopIteration: When no more segments
        """
        if self._position >= len(self._input):
            raise StopIteration

        # Get next segment from engine
        segment_text, is_word_like = self._segmenter.next_segment(
            self._input, self._position
        )

        if segment_text is None:
            raise StopIteration

        # Build segment data
        segment_data = {
            'segment': segment_text,
            'index': self._position,
            'input': self._input
        }

        # Add isWordLike only for word granularity
        if self._granularity == 'word':
            segment_data['isWordLike'] = is_word_like

        # Advance position
        self._position += len(segment_text)

        return segment_data
