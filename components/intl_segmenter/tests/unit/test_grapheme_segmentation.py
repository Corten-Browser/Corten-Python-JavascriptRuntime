"""
Unit tests for grapheme segmentation (FR-ES24-C-068)

Tests:
- Basic ASCII characters
- Combining marks (café -> c,a,f,é)
- Emoji ZWJ sequences (family emoji as single cluster)
- Regional indicator pairs (flag emojis)
- Devanagari and other scripts with combining characters
- Skin tone modifiers
- Multiple combining marks
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestGraphemeSegmentation:
    """FR-ES24-C-068: Grapheme segmentation (extended grapheme clusters)"""

    def test_basic_ascii_characters(self):
        """Should segment basic ASCII characters"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = list(segmenter.segment('ABC'))
        assert len(segments) == 3
        assert segments[0]['segment'] == 'A'
        assert segments[1]['segment'] == 'B'
        assert segments[2]['segment'] == 'C'

    def test_combining_accent_marks(self):
        """Should treat base + combining mark as single grapheme"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # café with combining acute accent: c + a + f + e + ◌́
        text = 'cafe\u0301'  # café (e + combining acute)
        segments = list(segmenter.segment(text))
        assert len(segments) == 4
        assert segments[0]['segment'] == 'c'
        assert segments[1]['segment'] == 'a'
        assert segments[2]['segment'] == 'f'
        assert segments[3]['segment'] == 'e\u0301'  # é as single grapheme

    def test_precomposed_vs_decomposed(self):
        """Should handle both precomposed and decomposed forms"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})

        # Precomposed é
        precomposed = 'café'  # Single codepoint é
        segments1 = list(segmenter.segment(precomposed))

        # Decomposed é (e + combining acute)
        decomposed = 'cafe\u0301'
        segments2 = list(segmenter.segment(decomposed))

        # Both should have 4 graphemes
        assert len(segments1) == 4
        assert len(segments2) == 4

    def test_emoji_zwj_sequence_family(self):
        """Should treat emoji ZWJ sequence as single grapheme cluster"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # Family emoji: 👨‍👩‍👧‍👦 (man-ZWJ-woman-ZWJ-girl-ZWJ-boy)
        family = '\U0001F468\u200D\U0001F469\u200D\U0001F467\u200D\U0001F466'
        segments = list(segmenter.segment(family))
        assert len(segments) == 1
        assert segments[0]['segment'] == family

    def test_emoji_with_skin_tone_modifier(self):
        """Should treat emoji + skin tone modifier as single grapheme"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # 👋🏽 (waving hand + medium skin tone)
        wave_with_tone = '\U0001F44B\U0001F3FD'
        segments = list(segmenter.segment(wave_with_tone))
        assert len(segments) == 1
        assert segments[0]['segment'] == wave_with_tone

    def test_regional_indicator_flag(self):
        """Should treat regional indicator pairs as single grapheme"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # 🇺🇸 (US flag: regional indicator U + S)
        us_flag = '\U0001F1FA\U0001F1F8'
        segments = list(segmenter.segment(us_flag))
        assert len(segments) == 1
        assert segments[0]['segment'] == us_flag

    def test_devanagari_combining_characters(self):
        """Should handle Devanagari combining characters"""
        segmenter = Segmenter('hi', {'granularity': 'grapheme'})
        # नमस्ते (Namaste in Devanagari)
        # न + म + स + ् + त + े
        namaste = 'नमस्ते'
        segments = list(segmenter.segment(namaste))
        # स्ते should be counted correctly with combining marks
        assert len(segments) >= 4  # At least 4 grapheme clusters

    def test_multiple_combining_marks(self):
        """Should handle multiple combining marks on single base"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # a + combining ring above + combining dot below
        text = 'a\u030A\u0323'
        segments = list(segmenter.segment(text))
        assert len(segments) == 1
        assert segments[0]['segment'] == text

    def test_crlf_line_break(self):
        """Should treat CRLF as single grapheme cluster"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        text = 'A\r\nB'
        segments = list(segmenter.segment(text))
        # A, \r\n, B
        assert len(segments) == 3
        assert segments[0]['segment'] == 'A'
        assert segments[1]['segment'] == '\r\n'
        assert segments[2]['segment'] == 'B'

    def test_hangul_syllables(self):
        """Should handle Korean Hangul syllables"""
        segmenter = Segmenter('ko', {'granularity': 'grapheme'})
        # 한글 (Hangul)
        text = '한글'
        segments = list(segmenter.segment(text))
        # Each Hangul syllable is one grapheme
        assert len(segments) == 2

    def test_emoji_without_zwj(self):
        """Should segment separate emojis without ZWJ"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # Two separate emojis (no ZWJ)
        text = '😀😁'
        segments = list(segmenter.segment(text))
        assert len(segments) == 2
        assert segments[0]['segment'] == '😀'
        assert segments[1]['segment'] == '😁'

    def test_mixed_text_and_emoji(self):
        """Should handle mixed text and emoji"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        text = 'Hi😀'
        segments = list(segmenter.segment(text))
        assert len(segments) == 3
        assert segments[0]['segment'] == 'H'
        assert segments[1]['segment'] == 'i'
        assert segments[2]['segment'] == '😀'

    def test_grapheme_segment_indices(self):
        """Should have correct indices for grapheme segments"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        text = 'ABC'
        segments = list(segmenter.segment(text))
        assert segments[0]['index'] == 0
        assert segments[1]['index'] == 1
        assert segments[2]['index'] == 2

    def test_grapheme_no_isWordLike_property(self):
        """Grapheme segments should not have isWordLike property"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        segments = list(segmenter.segment('Hello'))
        for seg in segments:
            # isWordLike only for word granularity
            assert 'isWordLike' not in seg or seg.get('isWordLike') is None

    def test_zero_width_joiner_without_emoji(self):
        """Should handle ZWJ in non-emoji contexts"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        # Text with ZWJ (used in some Indic scripts)
        text = 'a\u200Db'  # a + ZWJ + b
        segments = list(segmenter.segment(text))
        # ZWJ without proper emoji context may not join
        assert len(segments) >= 2
