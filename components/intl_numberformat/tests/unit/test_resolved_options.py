"""
Unit tests for resolvedOptions() method (FR-ES24-C-030)

These tests cover:
- Default options resolution
- Explicit options preservation
- Locale fallback
- Currency options resolution
- Unit options resolution
- Digit options resolution
- Immutability of returned object
"""

import pytest
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestResolvedOptionsBasic:
    """Test basic resolvedOptions functionality."""

    def test_resolved_options_returns_dict(self):
        """resolvedOptions should return a dictionary."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert isinstance(options, dict)
        assert len(options) > 0

    def test_resolved_options_has_required_fields(self):
        """resolvedOptions should have required fields."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        required = [
            'locale',
            'numberingSystem',
            'style',
            'minimumIntegerDigits',
            'useGrouping'
        ]

        for field in required:
            assert field in options

    def test_resolved_options_locale(self):
        """Resolved locale should match or be compatible."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'locale' in options
        assert options['locale'] == 'en-US'

    def test_resolved_options_numbering_system(self):
        """Numbering system should be resolved."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'numberingSystem' in options
        # Default for en-US is latn
        assert options['numberingSystem'] == 'latn'

    def test_resolved_options_style_default(self):
        """Default style should be decimal."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert options['style'] == 'decimal'


class TestResolvedOptionsExplicit:
    """Test explicit options preservation."""

    def test_resolved_options_currency(self):
        """Currency options should be preserved."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        options = formatter.resolvedOptions()

        assert options['style'] == 'currency'
        assert options['currency'] == 'USD'
        assert 'currencyDisplay' in options
        assert 'currencySign' in options

    def test_resolved_options_currency_display(self):
        """Currency display option preserved."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'EUR',
            'currencyDisplay': 'code'
        })
        options = formatter.resolvedOptions()

        assert options['currencyDisplay'] == 'code'

    def test_resolved_options_currency_sign(self):
        """Currency sign option preserved."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'accounting'
        })
        options = formatter.resolvedOptions()

        assert options['currencySign'] == 'accounting'

    def test_resolved_options_unit(self):
        """Unit options should be preserved."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        options = formatter.resolvedOptions()

        assert options['style'] == 'unit'
        assert options['unit'] == 'meter'
        assert 'unitDisplay' in options

    def test_resolved_options_unit_display(self):
        """Unit display option preserved."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'unitDisplay': 'long'
        })
        options = formatter.resolvedOptions()

        assert options['unitDisplay'] == 'long'

    def test_resolved_options_notation(self):
        """Notation option preserved."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        options = formatter.resolvedOptions()

        assert options['notation'] == 'compact'
        assert 'compactDisplay' in options

    def test_resolved_options_compact_display(self):
        """Compact display option preserved."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'compact',
            'compactDisplay': 'long'
        })
        options = formatter.resolvedOptions()

        assert options['compactDisplay'] == 'long'


class TestResolvedOptionsDigits:
    """Test digit options resolution."""

    def test_resolved_options_minimum_integer_digits(self):
        """Minimum integer digits preserved."""
        formatter = IntlNumberFormat('en-US', {'minimumIntegerDigits': 3})
        options = formatter.resolvedOptions()

        assert options['minimumIntegerDigits'] == 3

    def test_resolved_options_fraction_digits(self):
        """Fraction digits preserved."""
        formatter = IntlNumberFormat('en-US', {
            'minimumFractionDigits': 2,
            'maximumFractionDigits': 4
        })
        options = formatter.resolvedOptions()

        assert options['minimumFractionDigits'] == 2
        assert options['maximumFractionDigits'] == 4

    def test_resolved_options_significant_digits(self):
        """Significant digits preserved."""
        formatter = IntlNumberFormat('en-US', {
            'minimumSignificantDigits': 2,
            'maximumSignificantDigits': 5
        })
        options = formatter.resolvedOptions()

        assert options['minimumSignificantDigits'] == 2
        assert options['maximumSignificantDigits'] == 5

    def test_resolved_options_default_fraction_digits(self):
        """Default fraction digits for decimal style."""
        formatter = IntlNumberFormat('en-US', {'style': 'decimal'})
        options = formatter.resolvedOptions()

        # Decimal style typically has specific defaults
        assert 'minimumFractionDigits' in options
        assert 'maximumFractionDigits' in options

    def test_resolved_options_currency_fraction_defaults(self):
        """Currency style has appropriate fraction defaults."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        options = formatter.resolvedOptions()

        # USD typically has 2 decimal places
        assert options['minimumFractionDigits'] == 2
        assert options['maximumFractionDigits'] == 2

    def test_resolved_options_currency_jpy_no_fractions(self):
        """JPY currency has no fraction digits."""
        formatter = IntlNumberFormat('ja-JP', {
            'style': 'currency',
            'currency': 'JPY'
        })
        options = formatter.resolvedOptions()

        # JPY has 0 decimal places
        assert options['minimumFractionDigits'] == 0
        assert options['maximumFractionDigits'] == 0


class TestResolvedOptionsOther:
    """Test other options resolution."""

    def test_resolved_options_use_grouping_default(self):
        """Default useGrouping."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert 'useGrouping' in options
        # Default is typically 'auto' or True
        assert options['useGrouping'] in [True, 'auto', 'always']

    def test_resolved_options_use_grouping_false(self):
        """useGrouping false preserved."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': False})
        options = formatter.resolvedOptions()

        assert options['useGrouping'] is False

    def test_resolved_options_use_grouping_string(self):
        """useGrouping string value preserved."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': 'min2'})
        options = formatter.resolvedOptions()

        assert options['useGrouping'] == 'min2'

    def test_resolved_options_sign_display(self):
        """Sign display option preserved."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'always'})
        options = formatter.resolvedOptions()

        assert options['signDisplay'] == 'always'

    def test_resolved_options_rounding_mode(self):
        """Rounding mode option preserved."""
        formatter = IntlNumberFormat('en-US', {'roundingMode': 'ceil'})
        options = formatter.resolvedOptions()

        assert options['roundingMode'] == 'ceil'

    def test_resolved_options_rounding_priority(self):
        """Rounding priority option preserved."""
        formatter = IntlNumberFormat('en-US', {'roundingPriority': 'morePrecision'})
        options = formatter.resolvedOptions()

        assert options['roundingPriority'] == 'morePrecision'

    def test_resolved_options_rounding_increment(self):
        """Rounding increment option preserved."""
        formatter = IntlNumberFormat('en-US', {'roundingIncrement': 5})
        options = formatter.resolvedOptions()

        assert options['roundingIncrement'] == 5

    def test_resolved_options_trailing_zero_display(self):
        """Trailing zero display option preserved."""
        formatter = IntlNumberFormat('en-US', {'trailingZeroDisplay': 'stripIfInteger'})
        options = formatter.resolvedOptions()

        assert options['trailingZeroDisplay'] == 'stripIfInteger'


class TestResolvedOptionsLocaleFallback:
    """Test locale fallback in resolved options."""

    def test_resolved_options_unsupported_locale(self):
        """Unsupported locale falls back."""
        # Try to create with invalid locale, should fall back
        formatter = IntlNumberFormat(['xx-XX', 'en-US'])
        options = formatter.resolvedOptions()

        # Should fall back to a valid locale
        assert options['locale'] in ['en-US', 'en']

    def test_resolved_options_locale_canonicalization(self):
        """Locale should be canonicalized."""
        formatter = IntlNumberFormat('EN-us')
        options = formatter.resolvedOptions()

        # Should be canonical form
        assert options['locale'] == 'en-US'

    def test_resolved_options_multiple_locales(self):
        """Multiple locales resolve to best match."""
        formatter = IntlNumberFormat(['de-DE', 'en-US'])
        options = formatter.resolvedOptions()

        # Should pick first supported locale
        assert options['locale'] in ['de-DE', 'en-US']


class TestResolvedOptionsImmutability:
    """Test immutability of resolved options."""

    def test_resolved_options_returns_new_object(self):
        """Each call returns a new object."""
        formatter = IntlNumberFormat('en-US')
        options1 = formatter.resolvedOptions()
        options2 = formatter.resolvedOptions()

        # Should be equal but not same object
        assert options1 == options2
        assert options1 is not options2

    def test_resolved_options_modification_no_effect(self):
        """Modifying returned options doesn't affect formatter."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        # Try to modify
        original_locale = options['locale']
        options['locale'] = 'de-DE'

        # Get fresh options
        fresh_options = formatter.resolvedOptions()

        # Should still have original locale
        assert fresh_options['locale'] == original_locale


class TestResolvedOptionsCompleteness:
    """Test that all options are resolved."""

    def test_resolved_options_all_set_decimal(self):
        """All options should be set for decimal style."""
        formatter = IntlNumberFormat('en-US', {'style': 'decimal'})
        options = formatter.resolvedOptions()

        expected = [
            'locale', 'numberingSystem', 'style',
            'minimumIntegerDigits', 'useGrouping',
            'notation', 'signDisplay'
        ]

        for field in expected:
            assert field in options
            assert options[field] is not None

    def test_resolved_options_all_set_currency(self):
        """All options should be set for currency style."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        options = formatter.resolvedOptions()

        expected = [
            'locale', 'numberingSystem', 'style',
            'currency', 'currencyDisplay', 'currencySign',
            'minimumIntegerDigits', 'minimumFractionDigits',
            'maximumFractionDigits', 'useGrouping'
        ]

        for field in expected:
            assert field in options
            assert options[field] is not None

    def test_resolved_options_all_set_unit(self):
        """All options should be set for unit style."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        options = formatter.resolvedOptions()

        expected = [
            'locale', 'numberingSystem', 'style',
            'unit', 'unitDisplay',
            'minimumIntegerDigits', 'useGrouping'
        ]

        for field in expected:
            assert field in options
            assert options[field] is not None


class TestResolvedOptionsDefaults:
    """Test default values in resolved options."""

    def test_resolved_options_defaults_decimal(self):
        """Check defaults for decimal style."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()

        assert options['style'] == 'decimal'
        assert options['notation'] == 'standard'
        assert options['signDisplay'] == 'auto'
        assert options['minimumIntegerDigits'] == 1

    def test_resolved_options_defaults_percent(self):
        """Check defaults for percent style."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        options = formatter.resolvedOptions()

        assert options['style'] == 'percent'
        assert options['minimumIntegerDigits'] == 1

    def test_resolved_options_defaults_currency(self):
        """Check defaults for currency style."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        options = formatter.resolvedOptions()

        assert options['currencyDisplay'] == 'symbol'
        assert options['currencySign'] == 'standard'

    def test_resolved_options_defaults_compact(self):
        """Check defaults for compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        options = formatter.resolvedOptions()

        assert options['compactDisplay'] == 'short'
