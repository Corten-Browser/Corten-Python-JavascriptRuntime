"""
Unit tests for containing() method (FR-ES24-C-072)

Tests:
- Find segment at index
- Returns undefined for out-of-range index
- Handles negative index
- Returns correct segment data
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestContainingMethod:
    """FR-ES24-C-072: containing() method finds segment at code unit index"""

    def test_containing_first_segment(self):
        """Should find first segment"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        result = segments.containing(0)
        assert result is not None
        assert result['segment'] == 'Hello'
        assert result['index'] == 0

    def test_containing_middle_of_word(self):
        """Should find segment containing middle index"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        # Index 2 is in "Hello"
        result = segments.containing(2)
        assert result is not None
        assert result['segment'] == 'Hello'

    def test_containing_space(self):
        """Should find space segment"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        # Index 5 is the space
        result = segments.containing(5)
        assert result is not None
        assert result['segment'] == ' '
        assert result['index'] == 5

    def test_containing_second_word(self):
        """Should find second word"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        # Index 6 is start of "world"
        result = segments.containing(6)
        assert result is not None
        assert result['segment'] == 'world'
        assert result['index'] == 6

    def test_containing_out_of_range(self):
        """Should return None for out-of-range index"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello')

        result = segments.containing(100)
        assert result is None

    def test_containing_at_length(self):
        """Should return None for index == length"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello')

        result = segments.containing(5)  # len('Hello') == 5
        assert result is None

    def test_containing_negative_index_raises(self):
        """Should raise RangeError for negative index"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello')

        with pytest.raises(Exception):  # RangeError
            segments.containing(-1)

    def test_containing_returns_complete_data(self):
        """Should return complete SegmentData"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        result = segments.containing(0)
        assert 'segment' in result
        assert 'index' in result
        assert 'input' in result
        assert result['input'] == 'Hello world'

    def test_containing_with_word_granularity_has_isWordLike(self):
        """Should include isWordLike for word granularity"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        result = segments.containing(0)
        assert 'isWordLike' in result
        assert result['isWordLike'] is True

    def test_containing_grapheme_granularity(self):
        """Should work with grapheme granularity"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('ABC')

        result = segments.containing(1)
        assert result is not None
        assert result['segment'] == 'B'
        assert result['index'] == 1
