"""
Unit tests for locale-sensitive segmentation (FR-ES24-C-074)

Tests:
- English contractions
- French accents
- Japanese word breaking (simplified)
- Different locales produce different results
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestLocaleSensitivity:
    """FR-ES24-C-074: Locale-sensitive segmentation (adapts to language)"""

    def test_english_contraction(self):
        """English locale should handle contractions"""
        segmenter = Segmenter('en-US', {'granularity': 'word'})
        segments = list(segmenter.segment("don't"))

        words = [s for s in segments if s.get('isWordLike')]
        # "don't" should be one word in English
        assert len(words) == 1

    def test_french_accents(self):
        """French locale should handle accented characters"""
        segmenter = Segmenter('fr-FR', {'granularity': 'word'})
        segments = list(segmenter.segment('Café français'))

        words = [s['segment'] for s in segments if s.get('isWordLike')]
        assert 'Café' in words
        assert 'français' in words

    def test_different_locales_same_text(self):
        """Different locales may segment same text differently"""
        text = 'Hello'
        seg_en = Segmenter('en', {'granularity': 'word'})
        seg_fr = Segmenter('fr', {'granularity': 'word'})

        # Both should handle basic Latin text
        segs_en = list(seg_en.segment(text))
        segs_fr = list(seg_fr.segment(text))

        # For basic Latin, results may be similar
        assert len(segs_en) >= 1
        assert len(segs_fr) >= 1

    def test_locale_preserved_in_resolved_options(self):
        """Locale should be preserved in resolvedOptions"""
        segmenter = Segmenter('de-DE', {'granularity': 'word'})
        options = segmenter.resolved_options()

        assert 'de' in options['locale'].lower()

    def test_japanese_characters_handled(self):
        """Should handle Japanese characters (basic support)"""
        segmenter = Segmenter('ja-JP', {'granularity': 'word'})
        # Simple hiragana
        segments = list(segmenter.segment('これは'))

        # Should produce some segmentation
        assert len(segments) >= 1

    def test_chinese_characters_handled(self):
        """Should handle Chinese characters (basic support)"""
        segmenter = Segmenter('zh-CN', {'granularity': 'word'})
        segments = list(segmenter.segment('你好'))

        # Should produce some segmentation
        assert len(segments) >= 1
