"""
Unit tests for iterator protocol (FR-ES24-C-073)

Tests:
- Segments implements __iter__
- Iterator has __next__
- Works with for loops
- Works with list()
- Multiple iterations
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestIteratorProtocol:
    """FR-ES24-C-073: Iterator protocol support (for-of, spread, Array.from)"""

    def test_segments_has_iter(self):
        """Segments should have __iter__ method"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('ABC')
        assert hasattr(segments, '__iter__')

    def test_iterator_has_next(self):
        """Iterator should have __next__ method"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('ABC')
        iterator = iter(segments)
        assert hasattr(iterator, '__next__')

    def test_iteration_with_for_loop(self):
        """Should work with for loop"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('ABC')

        result = []
        for seg in segments:
            result.append(seg['segment'])

        assert result == ['A', 'B', 'C']

    def test_iteration_with_list_conversion(self):
        """Should work with list()"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('ABC')

        result = list(segments)
        assert len(result) == 3
        assert all('segment' in s for s in result)

    def test_multiple_iterations(self):
        """Should support multiple iterations"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('AB')

        # First iteration
        list1 = list(segments)
        # Second iteration
        list2 = list(segments)

        assert list1 == list2
        assert len(list1) == 2

    def test_iterator_exhaustion(self):
        """Iterator should raise StopIteration when exhausted"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('A')
        iterator = iter(segments)

        # Get first item
        next(iterator)

        # Should raise StopIteration
        with pytest.raises(StopIteration):
            next(iterator)

    def test_empty_iteration(self):
        """Empty string should iterate zero times"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = segmenter.segment('')

        result = list(segments)
        assert len(result) == 0

    def test_segment_data_structure(self):
        """Each iteration should yield proper SegmentData"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment('Hello world')

        for seg in segments:
            assert 'segment' in seg
            assert 'index' in seg
            assert 'input' in seg
            assert isinstance(seg['segment'], str)
            assert isinstance(seg['index'], int)
            assert isinstance(seg['input'], str)
