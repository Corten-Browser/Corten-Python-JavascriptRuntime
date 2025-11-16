"""
Unit tests for resolvedOptions() method (FR-ES24-C-075)

Tests:
- Returns locale and granularity
- Locale is string
- Granularity matches constructor option
"""

import pytest
import sys
sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/intl_segmenter/src')

from segmenter import Segmenter


class TestResolvedOptions:
    """FR-ES24-C-075: resolvedOptions() returns locale and granularity"""

    def test_resolved_options_returns_object(self):
        """Should return dictionary with locale and granularity"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        options = segmenter.resolved_options()

        assert isinstance(options, dict)
        assert 'locale' in options
        assert 'granularity' in options

    def test_resolved_locale_is_string(self):
        """Locale should be string"""
        segmenter = Segmenter('en-US')
        options = segmenter.resolved_options()

        assert isinstance(options['locale'], str)
        assert len(options['locale']) > 0

    def test_resolved_granularity_matches_constructor(self):
        """Granularity should match constructor option"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        options = segmenter.resolved_options()

        assert options['granularity'] == 'word'

    def test_resolved_default_granularity(self):
        """Default granularity should be grapheme"""
        segmenter = Segmenter('en')
        options = segmenter.resolved_options()

        assert options['granularity'] == 'grapheme'

    def test_resolved_options_immutable(self):
        """Modifying returned options should not affect segmenter"""
        segmenter = Segmenter('en', {'granularity': 'word'})
        options1 = segmenter.resolved_options()
        options1['granularity'] = 'sentence'

        # Get fresh options
        options2 = segmenter.resolved_options()
        assert options2['granularity'] == 'word'
