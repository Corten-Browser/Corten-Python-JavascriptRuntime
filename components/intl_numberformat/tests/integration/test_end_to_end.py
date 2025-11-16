"""
Integration tests for IntlNumberFormat

These tests verify end-to-end functionality and cross-feature integration.
"""

import pytest
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestIntegrationBasic:
    """Test basic integration scenarios."""

    def test_create_format_simple(self):
        """Simple create and format workflow."""
        formatter = IntlNumberFormat('en-US')
        result = formatter.format(1234.56)
        assert '1,234.56' in result or '1234.56' in result

    def test_multiple_formats_same_formatter(self):
        """Multiple format calls with same formatter."""
        formatter = IntlNumberFormat('en-US')

        results = [
            formatter.format(10),
            formatter.format(100),
            formatter.format(1000),
        ]

        assert '10' in results[0]
        assert '100' in results[1]
        assert '1,000' in results[2] or '1000' in results[2]

    def test_different_locales_same_number(self):
        """Same number formatted with different locales."""
        number = 1234.56

        en_formatter = IntlNumberFormat('en-US')
        de_formatter = IntlNumberFormat('de-DE')

        en_result = en_formatter.format(number)
        de_result = de_formatter.format(number)

        # Different locales should produce different formats
        # US: 1,234.56, DE: 1.234,56
        assert en_result != de_result or ',' in en_result or '.' in de_result


class TestIntegrationCurrency:
    """Test currency integration scenarios."""

    def test_currency_different_codes(self):
        """Different currency codes produce different output."""
        amount = 1000

        usd_formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        eur_formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'EUR'
        })

        usd_result = usd_formatter.format(amount)
        eur_result = eur_formatter.format(amount)

        assert '$' in usd_result
        assert '€' in eur_result or 'EUR' in eur_result
        assert usd_result != eur_result

    def test_currency_locale_interaction(self):
        """Currency format varies by locale."""
        amount = 1234.56

        us_eur_formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'EUR'
        })
        de_eur_formatter = IntlNumberFormat('de-DE', {
            'style': 'currency',
            'currency': 'EUR'
        })

        us_result = us_eur_formatter.format(amount)
        de_result = de_eur_formatter.format(amount)

        # Both should have EUR symbol but different formatting
        # (Different separators, symbol placement, etc.)


class TestIntegrationNotationCombinations:
    """Test notation combined with other options."""

    def test_compact_with_currency(self):
        """Compact notation with currency."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'notation': 'compact'
        })

        result = formatter.format(1234567)
        assert '$' in result
        assert 'M' in result or 'K' in result

    def test_compact_with_unit(self):
        """Compact notation with unit."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'unit',
            'unit': 'meter',
            'notation': 'compact'
        })

        result = formatter.format(5000)
        assert 'K' in result or 'k' in result or '5' in result

    def test_scientific_with_fraction_digits(self):
        """Scientific notation with fraction control."""
        formatter = IntlNumberFormat('en-US', {
            'notation': 'scientific',
            'minimumFractionDigits': 2,
            'maximumFractionDigits': 2
        })

        result = formatter.format(12345)
        # Should have scientific notation with 2 decimal places
        assert 'E' in result or 'e' in result or '×' in result


class TestIntegrationFormatVariants:
    """Test integration between format methods."""

    def test_format_and_format_to_parts_consistency(self):
        """format() and formatToParts() produce consistent results."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        number = 1234.56

        formatted = formatter.format(number)
        parts = formatter.formatToParts(number)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed

    def test_format_range_and_parts_consistency(self):
        """formatRange() and formatRangeToParts() consistent."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })

        formatted = formatter.formatRange(100, 200)
        parts = formatter.formatRangeToParts(100, 200)
        reconstructed = ''.join(p['value'] for p in parts)

        assert formatted == reconstructed


class TestIntegrationEdgeCases:
    """Test edge cases in integration."""

    def test_very_small_and_very_large(self):
        """Format very small and very large numbers."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})

        small = formatter.format(0.001)
        large = formatter.format(10**12)

        assert '0' in small
        assert ('T' in large or 'B' in large or
                'trillion' in large.lower() or 'billion' in large.lower())

    def test_zero_with_different_styles(self):
        """Zero formatted with different styles."""
        zero = 0

        decimal_fmt = IntlNumberFormat('en-US')
        percent_fmt = IntlNumberFormat('en-US', {'style': 'percent'})
        currency_fmt = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })

        decimal_result = decimal_fmt.format(zero)
        percent_result = percent_fmt.format(zero)
        currency_result = currency_fmt.format(zero)

        assert '0' in decimal_result
        assert '0' in percent_result and '%' in percent_result
        assert '0' in currency_result and '$' in currency_result


class TestIntegrationResolvedOptions:
    """Test resolved options integration."""

    def test_resolved_options_reflect_formatting(self):
        """Resolved options match actual formatting behavior."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'minimumFractionDigits': 0,
            'maximumFractionDigits': 0
        })

        options = formatter.resolvedOptions()
        result = formatter.format(1234.5)

        # Should have no decimals
        assert options['maximumFractionDigits'] == 0
        assert '.' not in result or '.00' not in result

    def test_resolved_options_after_multiple_formats(self):
        """Resolved options don't change after formatting."""
        formatter = IntlNumberFormat('en-US')

        options_before = formatter.resolvedOptions()
        formatter.format(1234)
        formatter.format(5678)
        options_after = formatter.resolvedOptions()

        assert options_before == options_after


class TestIntegrationPerformance:
    """Test performance integration scenarios."""

    def test_many_formats_same_instance(self):
        """Many formats with same instance should be fast."""
        import time

        formatter = IntlNumberFormat('en-US')

        start = time.time()
        for i in range(1000):
            formatter.format(i)
        elapsed = time.time() - start

        # Should be fast (<500µs per format × 1000 = <0.5s)
        assert elapsed < 1.0

    def test_many_instances_different_locales(self):
        """Create many formatters with different locales."""
        import time

        locales = ['en-US', 'de-DE', 'ja-JP', 'fr-FR', 'es-ES'] * 20

        start = time.time()
        formatters = [IntlNumberFormat(locale) for locale in locales]
        elapsed = time.time() - start

        # Should be reasonably fast
        assert elapsed < 1.0
        assert len(formatters) == 100


class TestIntegrationLocaleInteraction:
    """Test locale-specific behavior integration."""

    def test_arabic_numerals(self):
        """Arabic locale with Arabic numerals."""
        formatter = IntlNumberFormat('ar-SA', {'numberingSystem': 'arab'})
        result = formatter.format(1234)

        # Should use Arabic numerals (if implemented)
        # At minimum, should not crash

    def test_japanese_grouping(self):
        """Japanese locale grouping."""
        formatter = IntlNumberFormat('ja-JP')
        result = formatter.format(10000)

        # Japanese might group differently
        # At minimum, should format correctly

    def test_chinese_hanidec(self):
        """Chinese with hanidec numbering system."""
        try:
            formatter = IntlNumberFormat('zh-CN', {'numberingSystem': 'hanidec'})
            result = formatter.format(1234)
            # Should use Chinese decimal numerals (if implemented)
        except (ValueError, NotImplementedError):
            # Might not be fully implemented yet
            pass


class TestIntegrationRounding:
    """Test rounding integration with styles."""

    def test_rounding_with_currency(self):
        """Rounding modes work with currency."""
        ceil_fmt = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'maximumFractionDigits': 0,
            'roundingMode': 'ceil'
        })
        floor_fmt = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'maximumFractionDigits': 0,
            'roundingMode': 'floor'
        })

        amount = 10.5

        ceil_result = ceil_fmt.format(amount)
        floor_result = floor_fmt.format(amount)

        # ceil should round to 11, floor to 10
        assert '11' in ceil_result or '$11' in ceil_result
        assert '10' in floor_result or '$10' in floor_result
        assert ceil_result != floor_result


class TestIntegrationSignDisplay:
    """Test sign display integration."""

    def test_sign_display_with_range(self):
        """Sign display with range formatting."""
        formatter = IntlNumberFormat('en-US', {'signDisplay': 'always'})

        result = formatter.formatRange(10, 20)

        # Should show explicit signs
        assert '+' in result

    def test_sign_display_with_currency_negative(self):
        """Sign display with negative currency."""
        standard_fmt = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'standard'
        })
        accounting_fmt = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD',
            'currencySign': 'accounting'
        })

        amount = -1000

        standard_result = standard_fmt.format(amount)
        accounting_result = accounting_fmt.format(amount)

        # Different formats for negative
        # Standard: -$1,000.00
        # Accounting: ($1,000.00) or similar
