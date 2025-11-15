"""
Unit tests for IntlNumberFormat constructor (FR-ES24-C-021)

These tests cover:
- Constructor with no arguments
- Constructor with single locale
- Constructor with multiple locales
- Constructor with options object
- All style options (decimal, percent, currency, unit)
- Invalid locale handling
- Invalid options handling
- BigInt support
"""

import pytest
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestConstructorBasic:
    """Test basic constructor functionality."""

    def test_constructor_no_arguments(self):
        """Constructor with no arguments should use default locale."""
        formatter = IntlNumberFormat()
        assert formatter is not None
        assert hasattr(formatter, 'format')
        assert hasattr(formatter, 'formatToParts')
        assert hasattr(formatter, 'resolvedOptions')

    def test_constructor_single_locale(self):
        """Constructor with single locale string."""
        formatter = IntlNumberFormat('en-US')
        options = formatter.resolvedOptions()
        assert options['locale'] == 'en-US'

    def test_constructor_multiple_locales(self):
        """Constructor with multiple locales should use best available."""
        formatter = IntlNumberFormat(['xx-XX', 'en-US', 'de-DE'])
        options = formatter.resolvedOptions()
        # Should fall back to first valid locale
        assert options['locale'] in ['en-US', 'de-DE']

    def test_constructor_with_region_only_locale(self):
        """Constructor with different locale formats."""
        formatters = {
            'en': IntlNumberFormat('en'),
            'en-US': IntlNumberFormat('en-US'),
            'de-DE': IntlNumberFormat('de-DE'),
            'ja-JP': IntlNumberFormat('ja-JP'),
        }
        for locale, formatter in formatters.items():
            options = formatter.resolvedOptions()
            assert locale in options['locale']


class TestConstructorStyleOptions:
    """Test constructor with different style options (FR-ES24-C-026)."""

    def test_style_decimal(self):
        """Default and explicit decimal style."""
        formatter1 = IntlNumberFormat('en-US')
        formatter2 = IntlNumberFormat('en-US', {'style': 'decimal'})

        options1 = formatter1.resolvedOptions()
        options2 = formatter2.resolvedOptions()

        assert options1['style'] == 'decimal'
        assert options2['style'] == 'decimal'

    def test_style_percent(self):
        """Percent style formatting."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        options = formatter.resolvedOptions()
        assert options['style'] == 'percent'

    def test_style_currency_requires_currency_code(self):
        """Currency style requires currency option."""
        with pytest.raises((ValueError, TypeError)):
            IntlNumberFormat('en-US', {'style': 'currency'})

    def test_style_currency_with_code(self):
        """Currency style with currency code."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        options = formatter.resolvedOptions()
        assert options['style'] == 'currency'
        assert options['currency'] == 'USD'

    def test_style_unit_requires_unit(self):
        """Unit style requires unit option."""
        with pytest.raises((ValueError, TypeError)):
            IntlNumberFormat('en-US', {'style': 'unit'})

    def test_style_unit_with_identifier(self):
        """Unit style with unit identifier."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        options = formatter.resolvedOptions()
        assert options['style'] == 'unit'
        assert options['unit'] == 'meter'


class TestConstructorCurrencyOptions:
    """Test currency-related options (FR-ES24-C-027)."""

    def test_currency_display_symbol(self):
        """Currency display as symbol."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencyDisplay': 'symbol'
        })
        options = formatter.resolvedOptions()
        assert options['currencyDisplay'] == 'symbol'

    def test_currency_display_modes(self):
        """All currency display modes."""
        modes = ['symbol', 'narrowSymbol', 'code', 'name']
        for mode in modes:
            formatter = IntlNumberFormat('en-US', {
                'style': 'currency',
                'currency': 'USD',
                'currencyDisplay': mode
            })
            options = formatter.resolvedOptions()
            assert options['currencyDisplay'] == mode

    def test_currency_sign_standard(self):
        """Currency sign standard format."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'standard'
        })
        options = formatter.resolvedOptions()
        assert options['currencySign'] == 'standard'

    def test_currency_sign_accounting(self):
        """Currency sign accounting format."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'accounting'
        })
        options = formatter.resolvedOptions()
        assert options['currencySign'] == 'accounting'

    def test_iso4217_currency_codes(self):
        """Test various ISO 4217 currency codes."""
        currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CNY']
        for currency in currencies:
            formatter = IntlNumberFormat('en-US', {
                'style': 'currency',
                'currency': currency
            })
            options = formatter.resolvedOptions()
            assert options['currency'] == currency

    def test_invalid_currency_code(self):
        """Invalid currency code should raise error."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {
                'style': 'currency',
                'currency': 'INVALID'
            })

    def test_currency_code_lowercase_rejected(self):
        """Currency codes must be uppercase."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {
                'style': 'currency',
                'currency': 'usd'
            })


class TestConstructorUnitOptions:
    """Test unit-related options (FR-ES24-C-028)."""

    def test_unit_meter(self):
        """Unit: meter (length)."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        options = formatter.resolvedOptions()
        assert options['unit'] == 'meter'

    def test_unit_various_types(self):
        """Various unit types."""
        units = [
            'meter', 'kilometer', 'centimeter',
            'kilogram', 'gram',
            'celsius', 'fahrenheit',
            'liter', 'milliliter',
            'second', 'minute', 'hour',
        ]
        for unit in units:
            formatter = IntlNumberFormat('en-US', {
                'style': 'unit',
                'unit': unit
            })
            options = formatter.resolvedOptions()
            assert options['unit'] == unit

    def test_unit_display_short(self):
        """Unit display: short."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'unitDisplay': 'short'
        })
        options = formatter.resolvedOptions()
        assert options['unitDisplay'] == 'short'

    def test_unit_display_modes(self):
        """All unit display modes."""
        modes = ['short', 'narrow', 'long']
        for mode in modes:
            formatter = IntlNumberFormat('en-US', {
                'style': 'unit',
                'unit': 'meter',
                'unitDisplay': mode
            })
            options = formatter.resolvedOptions()
            assert options['unitDisplay'] == mode

    def test_invalid_unit(self):
        """Invalid unit identifier should raise error."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {
                'style': 'unit',
                'unit': 'invalid_unit'
            })


class TestConstructorNotationOptions:
    """Test notation options (FR-ES24-C-029)."""

    def test_notation_standard(self):
        """Standard notation (default)."""
        formatter = IntlNumberFormat('en-US', {'notation': 'standard'})
        options = formatter.resolvedOptions()
        assert options['notation'] == 'standard'

    def test_notation_scientific(self):
        """Scientific notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'scientific'})
        options = formatter.resolvedOptions()
        assert options['notation'] == 'scientific'

    def test_notation_engineering(self):
        """Engineering notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'engineering'})
        options = formatter.resolvedOptions()
        assert options['notation'] == 'engineering'

    def test_notation_compact(self):
        """Compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        options = formatter.resolvedOptions()
        assert options['notation'] == 'compact'

    def test_compact_display_short(self):
        """Compact display: short."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'compact',
            'compactDisplay': 'short'
        })
        options = formatter.resolvedOptions()
        assert options['compactDisplay'] == 'short'

    def test_compact_display_long(self):
        """Compact display: long."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'compact',
            'compactDisplay': 'long'
        })
        options = formatter.resolvedOptions()
        assert options['compactDisplay'] == 'long'


class TestConstructorDigitOptions:
    """Test digit-related options."""

    def test_minimum_integer_digits(self):
        """Minimum integer digits."""
        formatter = IntlNumberFormat('en-US', {'minimumIntegerDigits': 3})
        options = formatter.resolvedOptions()
        assert options['minimumIntegerDigits'] == 3

    def test_minimum_fraction_digits(self):
        """Minimum fraction digits."""
        formatter = IntlNumberFormat('en-US', {'minimumFractionDigits': 2})
        options = formatter.resolvedOptions()
        assert options['minimumFractionDigits'] == 2

    def test_maximum_fraction_digits(self):
        """Maximum fraction digits."""
        formatter = IntlNumberFormat('en-US', {'maximumFractionDigits': 4})
        options = formatter.resolvedOptions()
        assert options['maximumFractionDigits'] == 4

    def test_significant_digits(self):
        """Significant digits."""
        formatter = IntlNumberFormat('en-US', {
            'minimumSignificantDigits': 3,
            'maximumSignificantDigits': 5
        })
        options = formatter.resolvedOptions()
        assert options['minimumSignificantDigits'] == 3
        assert options['maximumSignificantDigits'] == 5

    def test_invalid_digit_range(self):
        """Invalid digit ranges should raise error."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {'minimumIntegerDigits': 22})

        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {'minimumFractionDigits': 21})

    def test_conflicting_digit_options(self):
        """Conflicting digit options should raise error."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('en-US', {
                'minimumFractionDigits': 5,
                'maximumFractionDigits': 2
            })


class TestConstructorOtherOptions:
    """Test other formatting options."""

    def test_use_grouping_true(self):
        """Use grouping: true."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': True})
        options = formatter.resolvedOptions()
        assert options['useGrouping'] in [True, 'auto', 'always']

    def test_use_grouping_false(self):
        """Use grouping: false."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': False})
        options = formatter.resolvedOptions()
        assert options['useGrouping'] is False

    def test_use_grouping_string_values(self):
        """Use grouping string values."""
        values = ['always', 'auto', 'min2']
        for value in values:
            formatter = IntlNumberFormat('en-US', {'useGrouping': value})
            options = formatter.resolvedOptions()
            assert options['useGrouping'] == value

    def test_sign_display_auto(self):
        """Sign display: auto."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'auto'})
        options = formatter.resolvedOptions()
        assert options['signDisplay'] == 'auto'

    def test_sign_display_modes(self):
        """All sign display modes."""
        modes = ['auto', 'never', 'always', 'exceptZero']
        for mode in modes:
            formatter = IntlNumberFormat('en-US', {'signDisplay': mode})
            options = formatter.resolvedOptions()
            assert options['signDisplay'] == mode

    def test_rounding_mode_half_expand(self):
        """Rounding mode: halfExpand (default)."""
        formatter = IntlNumberFormat('en-US', {'roundingMode': 'halfExpand'})
        options = formatter.resolvedOptions()
        assert options['roundingMode'] == 'halfExpand'

    def test_rounding_modes(self):
        """All rounding modes."""
        modes = ['ceil', 'floor', 'expand', 'trunc',
                 'halfCeil', 'halfFloor', 'halfExpand', 'halfTrunc', 'halfEven']
        for mode in modes:
            formatter = IntlNumberFormat('en-US', {'roundingMode': mode})
            options = formatter.resolvedOptions()
            assert options['roundingMode'] == mode


class TestConstructorErrorHandling:
    """Test constructor error handling."""

    def test_invalid_locale(self):
        """Invalid locale should raise error."""
        with pytest.raises((ValueError, RangeError)):
            IntlNumberFormat('invalid-locale-tag')

    def test_invalid_style(self):
        """Invalid style should raise error."""
        with pytest.raises((ValueError, TypeError)):
            IntlNumberFormat('en-US', {'style': 'invalid'})

    def test_invalid_option_type(self):
        """Invalid option type should raise error."""
        with pytest.raises(TypeError):
            IntlNumberFormat('en-US', "not a dict")

    def test_readonly_after_construction(self):
        """Options should be read-only after construction."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises(AttributeError):
            formatter.locale = 'de-DE'


class TestConstructorNumberingSystem:
    """Test numbering system option."""

    def test_numbering_system_latn(self):
        """Latin numbering system."""
        formatter = IntlNumberFormat('en-US', {'numberingSystem': 'latn'})
        options = formatter.resolvedOptions()
        assert options['numberingSystem'] == 'latn'

    def test_numbering_system_arab(self):
        """Arabic numbering system."""
        formatter = IntlNumberFormat('ar-SA', {'numberingSystem': 'arab'})
        options = formatter.resolvedOptions()
        assert options['numberingSystem'] == 'arab'

    def test_numbering_system_hanidec(self):
        """Chinese decimal numbering system."""
        formatter = IntlNumberFormat('zh-CN', {'numberingSystem': 'hanidec'})
        options = formatter.resolvedOptions()
        assert options['numberingSystem'] == 'hanidec'


# Custom exception for RangeError to match ECMAScript
class RangeError(Exception):
    """ECMAScript RangeError."""
    pass
