"""
Unit tests for RelativeTimeFormat.resolvedOptions() method (FR-ES24-C-042).

Tests:
1. resolvedOptions returns object
2. Contains locale property
3. Contains style property
4. Contains numeric property
5. Contains numberingSystem property
6. Reflects actual resolved values
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatResolvedOptions:
    """Test RelativeTimeFormat.resolvedOptions() method (FR-ES24-C-042)."""

    def test_resolvedOptions_returns_object(self):
        """Test that resolvedOptions returns an object/dict."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()

        assert isinstance(options, dict)
        assert len(options) > 0

    def test_resolvedOptions_contains_locale(self):
        """Test that resolvedOptions contains locale property."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()

        assert 'locale' in options
        assert isinstance(options['locale'], str)
        assert options['locale'] == 'en-US'

    def test_resolvedOptions_contains_style(self):
        """Test that resolvedOptions contains style property."""
        rtf = RelativeTimeFormat('en-US', {'style': 'short'})
        options = rtf.resolvedOptions()

        assert 'style' in options
        assert options['style'] == 'short'

    def test_resolvedOptions_contains_numeric(self):
        """Test that resolvedOptions contains numeric property."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})
        options = rtf.resolvedOptions()

        assert 'numeric' in options
        assert options['numeric'] == 'auto'

    def test_resolvedOptions_contains_numberingSystem(self):
        """Test that resolvedOptions contains numberingSystem property."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()

        assert 'numberingSystem' in options
        assert isinstance(options['numberingSystem'], str)
        # For en-US, should be "latn" (Latin numbering)
        assert options['numberingSystem'] == 'latn'

    def test_resolvedOptions_all_properties(self):
        """Test that resolvedOptions has all required properties."""
        rtf = RelativeTimeFormat('en-US', {
            'style': 'narrow',
            'numeric': 'auto'
        })
        options = rtf.resolvedOptions()

        # Must have these properties
        assert 'locale' in options
        assert 'style' in options
        assert 'numeric' in options
        assert 'numberingSystem' in options

        # Check values
        assert options['locale'] == 'en-US'
        assert options['style'] == 'narrow'
        assert options['numeric'] == 'auto'

    def test_resolvedOptions_default_values(self):
        """Test resolvedOptions with default values."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()

        # Defaults
        assert options['style'] == 'long'
        assert options['numeric'] == 'always'

    def test_resolvedOptions_locale_resolution(self):
        """Test that resolvedOptions shows actual resolved locale."""
        # Request locale with fallback
        rtf = RelativeTimeFormat(['fr-FR', 'en-US'])
        options = rtf.resolvedOptions()

        # Should resolve to one of the requested locales
        assert options['locale'] in ['fr-FR', 'en-US']

    def test_resolvedOptions_immutable(self):
        """Test that modifying returned options doesn't affect formatter."""
        rtf = RelativeTimeFormat('en-US', {'style': 'long'})
        options1 = rtf.resolvedOptions()

        # Modify returned options
        options1['style'] = 'short'

        # Get options again
        options2 = rtf.resolvedOptions()

        # Original formatter should be unchanged
        assert options2['style'] == 'long'

    def test_resolvedOptions_performance(self):
        """Test that resolvedOptions is fast (<100µs)."""
        import time

        rtf = RelativeTimeFormat('en-US')

        # Warm up
        rtf.resolvedOptions()

        # Measure
        start = time.perf_counter()
        for _ in range(1000):
            rtf.resolvedOptions()
        end = time.perf_counter()

        avg_time = (end - start) / 1000
        # Should be < 100µs (0.0001 seconds)
        assert avg_time < 0.0001, f"resolvedOptions too slow: {avg_time*1e6:.2f}µs"


# TypeError and RangeError imported from src
