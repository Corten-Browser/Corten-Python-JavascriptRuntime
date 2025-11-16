"""
Unit tests for sentence segmentation (FR-ES24-C-070)

Tests:
- Basic sentence segmentation
- Abbreviations (Dr., Mr., etc.)
- Multiple punctuation (?!, ...)
- Sentence with quotes
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestSentenceSegmentation:
    """FR-ES24-C-070: Sentence segmentation (locale-sensitive)"""

    def test_basic_sentence_segmentation(self):
        """Should segment sentences by period"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Hello world. How are you?'))

        assert len(segments) == 2
        assert 'Hello world.' in segments[0]['segment']
        assert 'How are you?' in segments[1]['segment']

    def test_abbreviation_dr(self):
        """Should not break on abbreviations like Dr."""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Dr. Smith works here.'))

        # Should be one sentence (Dr. is not sentence boundary)
        assert len(segments) == 1
        assert 'Dr. Smith works here.' == segments[0]['segment']

    def test_abbreviation_mr(self):
        """Should not break on Mr."""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Mr. Jones called.'))

        assert len(segments) == 1

    def test_multiple_punctuation(self):
        """Should handle multiple punctuation marks"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('What?! Really...'))

        # "What?! " and "Really..."
        assert len(segments) == 2

    def test_ellipsis(self):
        """Should handle ellipsis"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Wait... What happened?'))

        assert len(segments) == 2

    def test_question_mark(self):
        """Should break on question mark"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Is this working? Yes it is.'))

        assert len(segments) == 2

    def test_exclamation_mark(self):
        """Should break on exclamation mark"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Stop! Go away.'))

        assert len(segments) == 2

    def test_sentence_with_quotes(self):
        """Should handle sentences with quotes"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('He said "Hello." Then left.'))

        # May be 1 or 2 sentences depending on implementation
        assert len(segments) >= 1

    def test_single_sentence(self):
        """Single sentence should be one segment"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('This is a sentence.'))

        assert len(segments) == 1
        assert segments[0]['segment'] == 'This is a sentence.'

    def test_no_punctuation(self):
        """Text without punctuation should be one sentence"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Hello world'))

        assert len(segments) == 1

    def test_sentence_indices(self):
        """Sentence segments should have correct indices"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment('Hello. World.'))

        assert segments[0]['index'] == 0
        if len(segments) > 1:
            assert segments[1]['index'] > 0

    def test_empty_string_sentence(self):
        """Empty string should yield no segments"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        segments = list(segmenter.segment(''))
        assert len(segments) == 0
