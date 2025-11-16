"""
Unit tests for IntlNumberFormat format() method (FR-ES24-C-022, 026-029)

These tests cover:
- Decimal formatting
- Percent formatting
- Currency formatting (various currencies)
- Unit formatting (various units)
- Standard notation
- Scientific notation
- Engineering notation
- Compact notation (short and long)
- Negative numbers
- Zero
- Large numbers
- Small decimals
- BigInt values
- NaN and Infinity
- Rounding modes
- Sign display options
"""

import pytest
import math
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestFormatDecimal:
    """Test decimal formatting (FR-ES24-C-022)."""

    def test_format_positive_integer(self):
        """Format positive integer."""
        formatter = IntlNumberFormat('en-US')
        assert formatter.format(1234) == '1,234'

    def test_format_positive_decimal(self):
        """Format positive decimal."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(1234.56)
        assert result == '1,234.56'

    def test_format_zero(self):
        """Format zero."""
        formatter = IntlNumberFormat('en-US')
        assert formatter.format(0) == '0'

    def test_format_negative_integer(self):
        """Format negative integer."""
        formatter = IntlNumberFormat('en-US')
        assert formatter.format(-1234) == '-1,234'

    def test_format_negative_decimal(self):
        """Format negative decimal."""
        formatter = IntlNumberFormat('en-US')
        assert formatter.format(-1234.56) == '-1,234.56'

    def test_format_large_number(self):
        """Format large number."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(1234567890)
        assert result == '1,234,567,890'

    def test_format_small_decimal(self):
        """Format small decimal."""
        formatter = IntlNumberFormat('en-US', {'maximumFractionDigits': 6})
        result = formatter.format(0.000123)
        assert '0.000123' in result

    def test_format_without_grouping(self):
        """Format without grouping separators."""
        formatter = IntlNumberFormat('en-US', {'useGrouping': False})
        assert formatter.format(1234567) == '1234567'

    def test_format_with_minimum_integer_digits(self):
        """Format with minimum integer digits (padding)."""
        formatter = IntlNumberFormat('en-US', {'minimumIntegerDigits': 5})
        result = formatter.format(42)
        assert '00042' in result or '00,042' in result

    def test_format_with_fraction_digits(self):
        """Format with specific fraction digits."""
        formatter = IntlNumberFormat('en-US', {
            'minimumFractionDigits': 2,
            'maximumFractionDigits': 4
        })
        assert '.00' in formatter.format(10)
        assert formatter.format(10.1) in ['10.10', '10.1']
        result = formatter.format(10.123456)
        assert result in ['10.1235', '10.123', '10.12', '10.1234']

    def test_format_locale_de(self):
        """Format with German locale (different separators)."""
        formatter = IntlNumberFormat('de-DE')
        result = formatter.format(1234.56)
        # German uses . for thousands and , for decimal
        assert '1.234,56' == result or '1234,56' in result


class TestFormatPercent:
    """Test percent formatting (FR-ES24-C-026)."""

    def test_format_percent_basic(self):
        """Format as percent."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        result = formatter.format(0.5)
        assert '50' in result
        assert '%' in result

    def test_format_percent_zero(self):
        """Format zero percent."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        result = formatter.format(0)
        assert '0' in result
        assert '%' in result

    def test_format_percent_negative(self):
        """Format negative percent."""
        formatter = IntlNumberFormat('en-US', {'style': 'percent'})
        result = formatter.format(-0.25)
        assert '-25' in result or '25' in result
        assert '%' in result

    def test_format_percent_with_decimals(self):
        """Format percent with decimal places."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'percent',
            'minimumFractionDigits': 1
        })
        result = formatter.format(0.555)
        assert '55.5' in result or '55,5' in result


class TestFormatCurrency:
    """Test currency formatting (FR-ES24-C-027)."""

    def test_format_currency_usd(self):
        """Format USD currency."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        result = formatter.format(1234.56)
        assert '$' in result
        assert '1,234.56' in result

    def test_format_currency_eur(self):
        """Format EUR currency."""
        formatter = IntlNumberFormat('de-DE', {
            'style': 'currency',
            'currency': 'EUR'
        })
        result = formatter.format(1234.56)
        assert '€' in result or 'EUR' in result

    def test_format_currency_jpy(self):
        """Format JPY currency (no decimal places)."""
        formatter = IntlNumberFormat('ja-JP', {
            'style': 'currency',
            'currency': 'JPY'
        })
        result = formatter.format(1234)
        assert '¥' in result or 'JPY' in result
        assert '1,234' in result or '1234' in result

    def test_format_currency_display_code(self):
        """Format currency with code display."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencyDisplay': 'code'
        })
        result = formatter.format(1234.56)
        assert 'USD' in result

    def test_format_currency_display_name(self):
        """Format currency with name display."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencyDisplay': 'name'
        })
        result = formatter.format(1234.56)
        assert 'dollars' in result.lower() or 'dollar' in result.lower()

    def test_format_currency_negative(self):
        """Format negative currency."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        result = formatter.format(-1234.56)
        assert '-' in result or '(' in result
        assert '$' in result

    def test_format_currency_accounting(self):
        """Format currency with accounting sign (parentheses for negatives)."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'accounting'
        })
        result = formatter.format(-1234.56)
        # Accounting format typically uses parentheses
        assert '(' in result or '-' in result


class TestFormatUnit:
    """Test unit formatting (FR-ES24-C-028)."""

    def test_format_unit_meter(self):
        """Format meter unit."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter'
        })
        result = formatter.format(10)
        assert '10' in result
        assert 'm' in result.lower() or 'meter' in result.lower()

    def test_format_unit_kilometer(self):
        """Format kilometer unit."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'kilometer'
        })
        result = formatter.format(5.5)
        assert '5.5' in result or '5,5' in result
        assert 'km' in result.lower() or 'kilometer' in result.lower()

    def test_format_unit_celsius(self):
        """Format celsius unit."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'celsius'
        })
        result = formatter.format(25)
        assert '25' in result
        assert '°' in result or 'c' in result.lower()

    def test_format_unit_display_long(self):
        """Format unit with long display."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'unitDisplay': 'long'
        })
        result = formatter.format(10)
        assert 'meter' in result.lower()

    def test_format_unit_display_narrow(self):
        """Format unit with narrow display."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'unitDisplay': 'narrow'
        })
        result = formatter.format(10)
        assert '10' in result
        # Narrow might just be 'm'
        assert len(result) < 10


class TestFormatNotation:
    """Test notation formatting (FR-ES24-C-029)."""

    def test_format_scientific_notation(self):
        """Format with scientific notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'scientific'})
        result = formatter.format(123456)
        assert 'E' in result or 'e' in result or '×' in result
        assert '1.23' in result or '1,23' in result

    def test_format_engineering_notation(self):
        """Format with engineering notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'engineering'})
        result = formatter.format(123456)
        assert 'E' in result or 'e' in result or '×' in result

    def test_format_compact_short(self):
        """Format with compact notation (short)."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'compact',
            'compactDisplay': 'short'
        })
        result = formatter.format(1234567)
        assert 'M' in result or 'K' in result
        assert '1' in result

    def test_format_compact_long(self):
        """Format with compact notation (long)."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'compact',
            'compactDisplay': 'long'
        })
        result = formatter.format(1234567)
        assert 'million' in result.lower() or 'thousand' in result.lower()

    def test_format_compact_thousands(self):
        """Format thousands with compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.format(1500)
        # Could be "1.5K" or "2K" depending on rounding
        assert 'K' in result or 'k' in result or 'thousand' in result.lower()

    def test_format_compact_millions(self):
        """Format millions with compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.format(3400000)
        assert 'M' in result or 'million' in result.lower()

    def test_format_compact_billions(self):
        """Format billions with compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.format(7800000000)
        assert 'B' in result or 'billion' in result.lower()


class TestFormatSignDisplay:
    """Test sign display options."""

    def test_sign_display_auto_positive(self):
        """Auto sign display for positive (no sign)."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'auto'})
        result = formatter.format(42)
        assert '+' not in result

    def test_sign_display_auto_negative(self):
        """Auto sign display for negative (with sign)."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'auto'})
        result = formatter.format(-42)
        assert '-' in result

    def test_sign_display_never(self):
        """Never show sign."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'never'})
        result_pos = formatter.format(42)
        result_neg = formatter.format(-42)
        assert '+' not in result_pos
        assert '-' not in result_neg

    def test_sign_display_always(self):
        """Always show sign."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'always'})
        result_pos = formatter.format(42)
        result_neg = formatter.format(-42)
        assert '+' in result_pos
        assert '-' in result_neg

    def test_sign_display_except_zero(self):
        """Show sign except for zero."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'exceptZero'})
        result_zero = formatter.format(0)
        result_pos = formatter.format(42)
        result_neg = formatter.format(-42)
        assert '+' not in result_zero
        assert '-' not in result_zero
        assert '+' in result_pos
        assert '-' in result_neg


class TestFormatSpecialValues:
    """Test formatting of special values."""

    def test_format_nan(self):
        """Format NaN."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(float('nan'))
        assert 'NaN' in result

    def test_format_infinity(self):
        """Format positive infinity."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(float('inf'))
        assert '∞' in result or 'Infinity' in result

    def test_format_negative_infinity(self):
        """Format negative infinity."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(float('-inf'))
        assert '-' in result
        assert '∞' in result or 'Infinity' in result


class TestFormatBigInt:
    """Test BigInt formatting."""

    def test_format_bigint_small(self):
        """Format small BigInt."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(12345678901234567890)
        assert '12,345,678,901,234,567,890' in result or '12345678901234567890' in result

    def test_format_bigint_large(self):
        """Format large BigInt."""
        formatter = IntlNumberFormat('en-US')
        big_int = 10**30
        result = formatter.format(big_int)
        assert '1' in result

    def test_format_bigint_with_compact(self):
        """Format BigInt with compact notation."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        result = formatter.format(10**12)
        assert 'T' in result or 'trillion' in result.lower() or 'B' in result


class TestFormatRounding:
    """Test rounding modes."""

    def test_rounding_half_expand(self):
        """Half expand rounding (default)."""
        formatter = IntlNumberFormat('en-US', {
            'maximumFractionDigits': 0,
            'roundingMode': 'halfExpand'
        })
        assert '3' in formatter.format(2.5)
        assert '2' in formatter.format(1.5)

    def test_rounding_ceil(self):
        """Ceiling rounding."""
        formatter = IntlNumberFormat('en-US', {
            'maximumFractionDigits': 0,
            'roundingMode': 'ceil'
        })
        assert '3' in formatter.format(2.1)
        assert '-2' in formatter.format(-2.9)

    def test_rounding_floor(self):
        """Floor rounding."""
        formatter = IntlNumberFormat('en-US', {
            'maximumFractionDigits': 0,
            'roundingMode': 'floor'
        })
        assert '2' in formatter.format(2.9)
        assert '-3' in formatter.format(-2.1)

    def test_rounding_trunc(self):
        """Truncate rounding."""
        formatter = IntlNumberFormat('en-US', {
            'maximumFractionDigits': 0,
            'roundingMode': 'trunc'
        })
        assert '2' in formatter.format(2.9)
        assert '-2' in formatter.format(-2.9)


class TestFormatErrorHandling:
    """Test error handling in format()."""

    def test_format_invalid_type_string(self):
        """Format should reject string."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises(TypeError):
            formatter.format("not a number")

    def test_format_invalid_type_none(self):
        """Format should reject None."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises(TypeError):
            formatter.format(None)

    def test_format_invalid_type_object(self):
        """Format should reject arbitrary objects."""
        formatter = IntlNumberFormat('en-US')
        with pytest.raises(TypeError):
            formatter.format({'not': 'a number'})
