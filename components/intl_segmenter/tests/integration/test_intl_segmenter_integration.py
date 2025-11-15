"""
Integration tests for Intl.Segmenter

Tests end-to-end workflows combining multiple features.
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestIntlSegmenterIntegration:
    """Integration tests for complete workflows"""

    def test_complete_grapheme_workflow(self):
        """Complete workflow: create segmenter, segment text, iterate, check results"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})

        # Segment text with emoji
        text = 'Hi👋'
        segments = segmenter.segment(text)

        # Iterate and collect
        result = list(segments)

        # Verify results
        assert len(result) == 3
        assert result[0]['segment'] == 'H'
        assert result[1]['segment'] == 'i'
        assert result[2]['segment'] == '👋'

        # Verify all have correct properties
        for seg in result:
            assert 'segment' in seg
            assert 'index' in seg
            assert 'input' in seg
            assert seg['input'] == text

    def test_complete_word_workflow_with_containing(self):
        """Complete workflow: segment words, use containing(), verify isWordLike"""
        segmenter = Segmenter('en', {'granularity': 'word'})

        text = "Hello, world!"
        segments = segmenter.segment(text)

        # Test containing() method
        seg0 = segments.containing(0)  # 'Hello'
        assert seg0['segment'] == 'Hello'
        assert seg0['isWordLike'] is True

        seg5 = segments.containing(5)  # ','
        assert seg5['segment'] == ','
        assert seg5['isWordLike'] is False

        # Iterate and filter by isWordLike
        all_segments = list(segments)
        words = [s['segment'] for s in all_segments if s['isWordLike']]

        assert words == ['Hello', 'world']

    def test_complete_sentence_workflow(self):
        """Complete workflow: segment sentences, iterate, verify boundaries"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})

        text = "Hello world. How are you? I'm fine."
        segments = segmenter.segment(text)

        sentences = [s['segment'] for s in segments]

        assert len(sentences) == 3
        assert 'Hello world.' in sentences[0]
        assert 'How are you?' in sentences[1]
        assert "I'm fine." in sentences[2]

    def test_locale_switching(self):
        """Test switching between different locales"""
        text = "Café français"

        # English locale
        seg_en = Segmenter('en', {'granularity': 'word'})
        words_en = [s['segment'] for s in seg_en.segment(text) if s.get('isWordLike')]

        # French locale
        seg_fr = Segmenter('fr-FR', {'granularity': 'word'})
        words_fr = [s['segment'] for s in seg_fr.segment(text) if s.get('isWordLike')]

        # Both should get the words
        assert 'Café' in words_en
        assert 'français' in words_en
        assert 'Café' in words_fr
        assert 'français' in words_fr

    def test_granularity_switching(self):
        """Test switching between different granularities for same text"""
        text = "Hi!"

        # Grapheme
        seg_grapheme = Segmenter('en', {'granularity': 'grapheme'})
        graphemes = list(seg_grapheme.segment(text))
        assert len(graphemes) == 3  # H, i, !

        # Word
        seg_word = Segmenter('en', {'granularity': 'word'})
        words = list(seg_word.segment(text))
        assert len(words) == 2  # Hi, !

        # Sentence
        seg_sentence = Segmenter('en', {'granularity': 'sentence'})
        sentences = list(seg_sentence.segment(text))
        assert len(sentences) == 1  # Hi!

    def test_empty_and_edge_cases(self):
        """Test edge cases across all granularities"""
        empty = ""
        single = "A"

        for granularity in ['grapheme', 'word', 'sentence']:
            segmenter = Segmenter('en', {'granularity': granularity})

            # Empty string
            assert list(segmenter.segment(empty)) == []

            # Single character
            single_segs = list(segmenter.segment(single))
            assert len(single_segs) == 1
            assert single_segs[0]['segment'] == 'A'

    def test_resolved_options_accuracy(self):
        """Test that resolvedOptions accurately reflects configuration"""
        for granularity in ['grapheme', 'word', 'sentence']:
            segmenter = Segmenter('en-US', {'granularity': granularity})
            options = segmenter.resolved_options()

            assert options['locale'] == 'en-US'
            assert options['granularity'] == granularity

    def test_complex_unicode_text(self):
        """Test with complex Unicode text"""
        # Combining marks, emoji, multiple scripts
        text = "café 👨‍👩‍👧‍👦 नमस्ते"

        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = list(segmenter.segment(text))

        # Should handle all Unicode correctly
        assert len(segments) > 0

        # Family emoji should be one grapheme
        family_seg = next((s for s in segments if '👨' in s['segment']), None)
        assert family_seg is not None

    def test_performance_simple_benchmark(self):
        """Simple performance test for typical use case"""
        import time

        segmenter = Segmenter('en', {'granularity': 'word'})

        # Typical sentence
        text = "The quick brown fox jumps over the lazy dog."

        start = time.time()
        for _ in range(100):
            list(segmenter.segment(text))
        elapsed = time.time() - start

        # Should complete 100 iterations in reasonable time (< 1 second)
        assert elapsed < 1.0

    def test_multiple_iterations_independence(self):
        """Test that multiple iterations don't interfere with each other"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        segments = segmenter.segment("Hello world")

        # Multiple iterations should be identical
        iter1 = list(segments)
        iter2 = list(segments)
        iter3 = list(segments)

        assert iter1 == iter2 == iter3
        assert len(iter1) == 3  # Hello, space, world
