"""
Intl.Segmenter implementation for ES2024 Wave C

Provides locale-sensitive text segmentation by grapheme clusters, words, and sentences.
"""

from .segmenter import Segmenter, Segments, SegmentIterator, RangeError, TypeError

__all__ = ['Segmenter', 'Segments', 'SegmentIterator', 'RangeError', 'TypeError']
__version__ = '0.1.0'
