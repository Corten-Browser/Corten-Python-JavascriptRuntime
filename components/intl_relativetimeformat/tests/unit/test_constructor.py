"""
Unit tests for RelativeTimeFormat constructor (FR-ES24-C-037).

Tests:
1. Basic constructor with no arguments
2. Constructor with locale string
3. Constructor with locale array
4. Constructor with options
5. Invalid locale handling
6. Invalid style option
7. Invalid numeric option
8. Invalid localeMatcher option
9. Default options
10. Locale resolution
11. Options normalization
12. Instance creation
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatConstructor:
    """Test RelativeTimeFormat constructor (FR-ES24-C-037)."""

    def test_constructor_no_arguments(self):
        """Test constructor with no arguments uses default locale."""
        rtf = RelativeTimeFormat()
        assert rtf is not None
        options = rtf.resolvedOptions()
        assert 'locale' in options
        assert options['style'] == 'long'
        assert options['numeric'] == 'always'

    def test_constructor_with_locale_string(self):
        """Test constructor with single locale string."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()
        assert options['locale'] == 'en-US'

    def test_constructor_with_locale_array(self):
        """Test constructor with array of locales."""
        rtf = RelativeTimeFormat(['fr-FR', 'en-US'])
        options = rtf.resolvedOptions()
        # Should resolve to first available locale
        assert options['locale'] in ['fr-FR', 'en-US']

    def test_constructor_with_style_option(self):
        """Test constructor with style option."""
        rtf_long = RelativeTimeFormat('en-US', {'style': 'long'})
        rtf_short = RelativeTimeFormat('en-US', {'style': 'short'})
        rtf_narrow = RelativeTimeFormat('en-US', {'style': 'narrow'})

        assert rtf_long.resolvedOptions()['style'] == 'long'
        assert rtf_short.resolvedOptions()['style'] == 'short'
        assert rtf_narrow.resolvedOptions()['style'] == 'narrow'

    def test_constructor_with_numeric_option(self):
        """Test constructor with numeric option."""
        rtf_always = RelativeTimeFormat('en-US', {'numeric': 'always'})
        rtf_auto = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        assert rtf_always.resolvedOptions()['numeric'] == 'always'
        assert rtf_auto.resolvedOptions()['numeric'] == 'auto'

    def test_constructor_with_localeMatcher_option(self):
        """Test constructor with localeMatcher option."""
        rtf_lookup = RelativeTimeFormat('en-US', {'localeMatcher': 'lookup'})
        rtf_bestfit = RelativeTimeFormat('en-US', {'localeMatcher': 'best fit'})

        # localeMatcher doesn't appear in resolvedOptions, but shouldn't error
        assert rtf_lookup is not None
        assert rtf_bestfit is not None

    def test_constructor_invalid_locale(self):
        """Test constructor with invalid locale raises RangeError."""
        with pytest.raises(RangeError, match="Invalid language tag"):
            RelativeTimeFormat('invalid-locale-tag')

    def test_constructor_invalid_style(self):
        """Test constructor with invalid style raises RangeError."""
        with pytest.raises(RangeError, match="Invalid value for option 'style'"):
            RelativeTimeFormat('en-US', {'style': 'invalid'})

    def test_constructor_invalid_numeric(self):
        """Test constructor with invalid numeric raises RangeError."""
        with pytest.raises(RangeError, match="Invalid value for option 'numeric'"):
            RelativeTimeFormat('en-US', {'numeric': 'invalid'})

    def test_constructor_default_options(self):
        """Test that constructor uses correct default options."""
        rtf = RelativeTimeFormat('en-US')
        options = rtf.resolvedOptions()

        assert options['style'] == 'long'
        assert options['numeric'] == 'always'
        assert 'numberingSystem' in options

    def test_constructor_all_options(self):
        """Test constructor with all options specified."""
        rtf = RelativeTimeFormat('en-US', {
            'style': 'short',
            'numeric': 'auto',
            'localeMatcher': 'lookup'
        })

        options = rtf.resolvedOptions()
        assert options['style'] == 'short'
        assert options['numeric'] == 'auto'
        assert options['locale'] == 'en-US'

    def test_constructor_instance_type(self):
        """Test that constructor returns proper instance."""
        rtf = RelativeTimeFormat('en-US')
        assert isinstance(rtf, RelativeTimeFormat)
        assert hasattr(rtf, 'format')
        assert hasattr(rtf, 'formatToParts')
        assert hasattr(rtf, 'resolvedOptions')


# RangeError imported from src
