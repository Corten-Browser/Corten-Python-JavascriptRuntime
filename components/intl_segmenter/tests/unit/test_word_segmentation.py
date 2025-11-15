"""
Unit tests for word segmentation (FR-ES24-C-069)

Tests:
- Basic word segmentation
- isWordLike property for words vs punctuation
- Contractions (don't, it's)
- Hyphenated words
- Numbers as words
- Punctuation segmentation
- Multiple spaces
- Mixed punctuation
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestWordSegmentation:
    """FR-ES24-C-069: Word segmentation (locale-sensitive)"""

    def test_basic_word_segmentation(self):
        """Should segment words separated by spaces"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello world'))

        # Should get: "Hello", " ", "world"
        assert len(segments) == 3
        assert segments[0]['segment'] == 'Hello'
        assert segments[1]['segment'] == ' '
        assert segments[2]['segment'] == 'world'

    def test_isWordLike_for_words(self):
        """Words should have isWordLike=true"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello world'))

        # "Hello" and "world" are word-like
        assert segments[0]['isWordLike'] is True
        assert segments[2]['isWordLike'] is True

    def test_isWordLike_for_punctuation(self):
        """Punctuation should have isWordLike=false"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello, world!'))

        # Find comma and exclamation segments
        comma_seg = next(s for s in segments if s['segment'] == ',')
        exclaim_seg = next(s for s in segments if s['segment'] == '!')

        assert comma_seg['isWordLike'] is False
        assert exclaim_seg['isWordLike'] is False

    def test_isWordLike_for_whitespace(self):
        """Whitespace should have isWordLike=false"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello world'))

        # Space between words
        space_seg = segments[1]
        assert space_seg['segment'] == ' '
        assert space_seg['isWordLike'] is False

    def test_contraction_apostrophe(self):
        """Contractions should be treated as single word"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment("don't"))

        # "don't" should be one word
        word_segments = [s for s in segments if s.get('isWordLike')]
        assert len(word_segments) == 1
        assert word_segments[0]['segment'] == "don't"

    def test_multiple_contractions(self):
        """Should handle multiple contractions"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        text = "I'm sure you're right"
        segments = list(segmenter.segment(text))

        words = [s['segment'] for s in segments if s.get('isWordLike')]
        assert "I'm" in words
        assert "you're" in words
        assert 'sure' in words
        assert 'right' in words

    def test_hyphenated_words(self):
        """Should handle hyphenated words"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('well-known'))

        # Hyphenated words may be treated as one word or split
        # Just verify we get reasonable segmentation
        assert len(segments) >= 1

    def test_numbers_as_words(self):
        """Numbers should be word-like"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello 123 world'))

        # Find number segment
        num_seg = next((s for s in segments if '123' in s['segment']), None)
        assert num_seg is not None
        assert num_seg['isWordLike'] is True

    def test_mixed_alphanumeric(self):
        """Alphanumeric words should be word-like"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('ES2024'))

        word_segs = [s for s in segments if s.get('isWordLike')]
        assert len(word_segs) >= 1
        # Should include the alphanumeric part
        combined = ''.join(s['segment'] for s in word_segs)
        assert 'ES2024' in combined or combined == 'ES2024'

    def test_punctuation_only(self):
        """Punctuation-only input should have no word-like segments"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('.,!?'))

        # All should be non-word-like
        for seg in segments:
            assert seg['isWordLike'] is False

    def test_multiple_spaces(self):
        """Should handle multiple consecutive spaces"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello  world'))

        # Should get words and spaces
        space_segs = [s for s in segments if ' ' in s['segment']]
        assert len(space_segs) >= 1

    def test_mixed_punctuation_and_words(self):
        """Should segment complex punctuation"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello, world!'))

        # Expected segments (approximately):
        # "Hello", ",", " ", "world", "!"
        assert len(segments) >= 4

        words = [s['segment'] for s in segments if s.get('isWordLike')]
        assert 'Hello' in words
        assert 'world' in words

    def test_word_indices(self):
        """Word segments should have correct indices"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello world'))

        # "Hello" starts at 0
        assert segments[0]['index'] == 0

        # " " starts at 5
        assert segments[1]['index'] == 5

        # "world" starts at 6
        assert segments[2]['index'] == 6

    def test_unicode_word_segmentation(self):
        """Should handle Unicode words"""
        segmenter = Segmenter('fr', {'granularity': 'word'})
        segments = list(segmenter.segment('Café français'))

        words = [s['segment'] for s in segments if s.get('isWordLike')]
        assert 'Café' in words
        assert 'français' in words

    def test_empty_string_word_segmentation(self):
        """Empty string should yield no segments"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment(''))
        assert len(segments) == 0

    def test_single_word(self):
        """Single word should be one segment"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello'))
        assert len(segments) == 1
        assert segments[0]['segment'] == 'Hello'
        assert segments[0]['isWordLike'] is True

    def test_word_with_leading_trailing_spaces(self):
        """Should handle leading/trailing spaces"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment(' Hello '))

        # Should get: " ", "Hello", " "
        assert len(segments) == 3
        assert segments[1]['segment'] == 'Hello'
        assert segments[1]['isWordLike'] is True

    def test_sentence_with_period(self):
        """Should segment sentence with period"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = list(segmenter.segment('Hello.'))

        # "Hello", "."
        assert len(segments) >= 2
        words = [s['segment'] for s in segments if s.get('isWordLike')]
        assert 'Hello' in words

        punct = [s['segment'] for s in segments if not s.get('isWordLike')]
        assert '.' in punct
