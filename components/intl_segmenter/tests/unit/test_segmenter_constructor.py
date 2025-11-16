"""
Unit tests for Intl.Segmenter constructor (FR-ES24-C-066)

Tests:
- Constructor with no arguments (default locale and granularity)
- Constructor with locale string
- Constructor with locale array
- Constructor with granularity options (grapheme, word, sentence)
- Invalid locale raises RangeError
- Invalid granularity raises RangeError
- Invalid options type raises TypeError
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter, RangeError, TypeError


class TestSegmenterConstructor:
    """FR-ES24-C-066: Intl.Segmenter constructor with locale and granularity options"""

    def test_constructor_no_arguments(self):
        """Should create segmenter with default locale and grapheme granularity"""
        segmenter = Segmenter()
        options = segmenter.resolved_options()
        assert 'locale' in options
        assert options['granularity'] == 'grapheme'

    def test_constructor_with_locale_string(self):
        """Should create segmenter with specified locale"""
        segmenter = Segmenter('en-US')
        options = segmenter.resolved_options()
        assert options['locale'] == 'en-US'

    def test_constructor_with_locale_array(self):
        """Should create segmenter with first valid locale from array"""
        segmenter = Segmenter(['fr-FR', 'en-US'])
        options = segmenter.resolved_options()
        assert options['locale'] in ['fr-FR', 'en-US']

    def test_constructor_with_grapheme_granularity(self):
        """Should create segmenter with grapheme granularity"""
        segmenter = Segmenter('en', {'granularity': 'grapheme'})
        options = segmenter.resolved_options()
        assert options['granularity'] == 'grapheme'

    def test_constructor_with_word_granularity(self):
        """Should create segmenter with word granularity"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        options = segmenter.resolved_options()
        assert options['granularity'] == 'word'

    def test_constructor_with_sentence_granularity(self):
        """Should create segmenter with sentence granularity"""
        segmenter = Segmenter('en', {'granularity': 'sentence'})
        options = segmenter.resolved_options()
        assert options['granularity'] == 'sentence'

    def test_constructor_default_granularity(self):
        """Should default to grapheme granularity when not specified"""
        segmenter = Segmenter('en', {})
        options = segmenter.resolved_options()
        assert options['granularity'] == 'grapheme'

    def test_constructor_invalid_locale_raises_error(self):
        """Should raise RangeError for invalid locale"""
        with pytest.raises(RangeError):
            Segmenter('xx-INVALID')

    def test_constructor_invalid_granularity_raises_error(self):
        """Should raise RangeError for invalid granularity"""
        with pytest.raises(RangeError):
            Segmenter('en', {'granularity': 'invalid'})

    def test_constructor_invalid_options_type_raises_error(self):
        """Should raise TypeError when options is not an object"""
        with pytest.raises(TypeError):
            Segmenter('en', 'not-an-object')

    def test_constructor_creates_instance(self):
        """Should create instance of Segmenter"""
        segmenter = Segmenter('en')
        assert isinstance(segmenter, Segmenter)

    def test_constructor_multiple_locales_fallback(self):
        """Should fallback through locale list"""
        segmenter = Segmenter(['tlh', 'en-US'])  # Klingon -> English
        options = segmenter.resolved_options()
        # Should fallback to en-US or system default
        assert 'locale' in options
