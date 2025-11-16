"""
Unit tests for segment() method (FR-ES24-C-067)

Tests:
- segment() returns Segments object
- Segments object is iterable
- Segments object has containing() method
- Segments object has input property
- segment() accepts string input
- segment() works with empty string
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter, Segments


class TestSegmentMethod:
    """FR-ES24-C-067: segment() method returns Segments object (iterable)"""

    def test_segment_returns_segments_object(self):
        """Should return Segments object"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('Hello')
        assert isinstance(segments, Segments)

    def test_segments_is_iterable(self):
        """Segments object should be iterable"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('Hello')
        # Should have __iter__ method
        assert hasattr(segments, '__iter__')

    def test_segments_has_containing_method(self):
        """Segments object should have containing() method"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('Hello')
        assert hasattr(segments, 'containing')
        assert callable(segments.containing)

    def test_segments_has_input_property(self):
        """Segments object should have input property"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('Hello world')
        assert hasattr(segments, 'input')
        assert segments.input == 'Hello world'

    def test_segment_empty_string(self):
        """Should handle empty string"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('')
        assert isinstance(segments, Segments)
        assert segments.input == ''
        # Empty string should yield no segments
        segment_list = list(segments)
        assert len(segment_list) == 0

    def test_segment_single_character(self):
        """Should handle single character"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('A')
        segment_list = list(segments)
        assert len(segment_list) == 1
        assert segment_list[0]['segment'] == 'A'

    def test_segment_multiple_iterations(self):
        """Should allow multiple iterations over same Segments object"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('AB')

        # First iteration
        list1 = list(segments)
        assert len(list1) == 2

        # Second iteration
        list2 = list(segments)
        assert len(list2) == 2
        assert list1 == list2

    def test_segment_input_immutable(self):
        """Segments.input should be immutable reference to original string"""
        original = 'Hello'
        segmenter = Segmenter('en')
        segments = segmenter.segment(original)
        assert segments.input is not None
        assert segments.input == original

    def test_segment_different_inputs(self):
        """Should create different Segments for different inputs"""
        segmenter = Segmenter('en')
        segments1 = segmenter.segment('Hello')
        segments2 = segmenter.segment('World')
        assert segments1.input == 'Hello'
        assert segments2.input == 'World'

    def test_segment_unicode_input(self):
        """Should handle Unicode input"""
        segmenter = Segmenter('en')
        segments = segmenter.segment('café')
        assert isinstance(segments, Segments)
        assert segments.input == 'café'
