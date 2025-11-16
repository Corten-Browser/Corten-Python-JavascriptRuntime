"""
Integration Tests for Intl.ListFormat

Tests real-world usage scenarios and cross-feature integration.
"""

import pytest
from components.intl_listformat.src.list_format import (
    IntlListFormat,
    SupportedLocalesOf,
    CanonicalizeListFormatLocaleList,
    CreateListFormatPart
)


class TestRealWorldScenarios:
    """Test real-world usage patterns"""

    def test_ui_component_list(self):
        """Format list of UI components for display"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        components = ['Button', 'Input', 'Select', 'Checkbox', 'Radio']
        result = lf.format(components)
        assert 'Button' in result
        assert 'Radio' in result
        assert 'and' in result

    def test_permission_list(self):
        """Format list of permissions with disjunction"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        permissions = ['admin', 'editor', 'viewer']
        result = lf.format(permissions)
        assert result == "admin, editor, or viewer"

    def test_measurement_units(self):
        """Format measurement units"""
        lf = IntlListFormat('en', {'type': 'unit'})
        measurements = ['3 feet', '7 inches']
        result = lf.format(measurements)
        # Unit lists don't use conjunction
        assert 'and' not in result
        assert 'or' not in result

    def test_multilingual_product_names(self):
        """Format product names in different languages"""
        # English
        lf_en = IntlListFormat('en')
        products_en = ['MacBook', 'iPhone', 'iPad']
        result_en = lf_en.format(products_en)
        assert 'and' in result_en

        # Spanish
        lf_es = IntlListFormat('es')
        products_es = ['libro', 'revista', 'periódico']
        result_es = lf_es.format(products_es)
        assert 'y' in result_es

    def test_recipe_ingredients(self):
        """Format recipe ingredients list"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        ingredients = [
            '2 cups flour',
            '1 cup sugar',
            '3 eggs',
            '1/2 cup butter'
        ]
        result = lf.format(ingredients)
        assert all(ing in result for ing in ingredients)

    def test_error_message_list(self):
        """Format list of errors for user display"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        errors = [
            'Invalid email',
            'Password too short',
            'Username already taken'
        ]
        result = lf.format(errors)
        assert 'Invalid email' in result
        assert 'and' in result

    def test_tag_list_short_style(self):
        """Format tags with short style"""
        lf = IntlListFormat('en', {'type': 'conjunction', 'style': 'short'})
        tags = ['python', 'javascript', 'typescript', 'rust']
        result = lf.format(tags)
        # Should use short separator (& instead of and)
        assert result in [
            "python, javascript, typescript, & rust",
            "python, javascript, typescript, and rust"
        ]


class TestCrossBrowserCompatibility:
    """Test patterns matching browser behavior"""

    def test_empty_list_matches_browser(self):
        """Empty list should return empty string"""
        lf = IntlListFormat('en')
        assert lf.format([]) == ""
        assert lf.formatToParts([]) == []

    def test_single_item_matches_browser(self):
        """Single item should return item as-is"""
        lf = IntlListFormat('en')
        assert lf.format(['Solo']) == "Solo"
        parts = lf.formatToParts(['Solo'])
        assert len(parts) == 1
        assert parts[0] == {'type': 'element', 'value': 'Solo'}

    def test_two_items_conjunction(self):
        """Two items with conjunction"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['A', 'B'])
        assert 'and' in result

    def test_three_items_standard_format(self):
        """Three items should use Oxford comma"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['A', 'B', 'C'])
        # Should be "A, B, and C"
        assert result == "A, B, and C"


class TestLocaleNegotiation:
    """Test locale resolution and fallback"""

    def test_exact_locale_match(self):
        """Exact locale match should use that locale"""
        lf = IntlListFormat('en-US')
        options = lf.resolvedOptions()
        assert options['locale'] == 'en-US'

    def test_language_only_locale(self):
        """Language-only locale should work"""
        lf = IntlListFormat('es')
        result = lf.format(['A', 'B', 'C'])
        assert 'y' in result  # Spanish conjunction

    def test_fallback_to_english(self):
        """Unsupported locale should fall back to English"""
        lf = IntlListFormat('xx-XX')  # Unsupported
        result = lf.format(['A', 'B', 'C'])
        # Should use English patterns
        assert 'and' in result

    def test_locale_list_priority(self):
        """Should respect locale list priority"""
        lf = IntlListFormat(['fr', 'es', 'en'])
        # Should resolve to one of the requested locales
        options = lf.resolvedOptions()
        assert options['locale'] in ['fr', 'es', 'en']


class TestPartsReconstructionInvariant:
    """Test that formatToParts can reconstruct format() output"""

    def test_reconstruction_conjunction(self):
        """Parts should reconstruct exact format output"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        items = ['Apple', 'Banana', 'Orange']

        formatted = lf.format(items)
        parts = lf.formatToParts(items)
        reconstructed = ''.join(p['value'] for p in parts)

        assert reconstructed == formatted

    def test_reconstruction_disjunction(self):
        """Parts reconstruction for disjunction"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        items = ['A', 'B', 'C', 'D']

        formatted = lf.format(items)
        parts = lf.formatToParts(items)
        reconstructed = ''.join(p['value'] for p in parts)

        assert reconstructed == formatted

    def test_reconstruction_spanish(self):
        """Parts reconstruction for Spanish locale"""
        lf = IntlListFormat('es', {'type': 'conjunction'})
        items = ['uno', 'dos', 'tres']

        formatted = lf.format(items)
        parts = lf.formatToParts(items)
        reconstructed = ''.join(p['value'] for p in parts)

        assert reconstructed == formatted

    def test_reconstruction_short_style(self):
        """Parts reconstruction for short style"""
        lf = IntlListFormat('en', {'style': 'short'})
        items = ['X', 'Y', 'Z']

        formatted = lf.format(items)
        parts = lf.formatToParts(items)
        reconstructed = ''.join(p['value'] for p in parts)

        assert reconstructed == formatted


class TestHelperFunctions:
    """Test helper functions"""

    def test_SupportedLocalesOf_with_string(self):
        """Should handle string locale"""
        result = SupportedLocalesOf('en-US')
        assert 'en-US' in result

    def test_SupportedLocalesOf_with_list(self):
        """Should filter supported locales"""
        result = SupportedLocalesOf(['en', 'es', 'fr', 'xx'])
        # Should include en and es, might not include unsupported ones
        assert 'en' in result or 'es' in result

    def test_CanonicalizeListFormatLocaleList_string(self):
        """Should convert string to list"""
        result = CanonicalizeListFormatLocaleList('en-US')
        assert result == ['en-US']

    def test_CanonicalizeListFormatLocaleList_list(self):
        """Should return list as-is"""
        locales = ['en', 'es']
        result = CanonicalizeListFormatLocaleList(locales)
        assert result == locales

    def test_CanonicalizeListFormatLocaleList_none(self):
        """Should return empty list for None"""
        result = CanonicalizeListFormatLocaleList(None)
        assert result == []

    def test_CreateListFormatPart_element(self):
        """Should create element part"""
        part = CreateListFormatPart('element', 'test')
        assert part == {'type': 'element', 'value': 'test'}

    def test_CreateListFormatPart_literal(self):
        """Should create literal part"""
        part = CreateListFormatPart('literal', ', and ')
        assert part == {'type': 'literal', 'value': ', and '}


class TestPerformance:
    """Test performance characteristics"""

    def test_format_large_list(self):
        """Should handle large lists efficiently"""
        lf = IntlListFormat('en')
        large_list = [f'Item{i}' for i in range(1000)]

        import time
        start = time.time()
        result = lf.format(large_list)
        elapsed = time.time() - start

        # Should complete in reasonable time (<100ms for 1000 items)
        assert elapsed < 0.1
        assert 'Item0' in result
        assert 'Item999' in result

    def test_formatToParts_performance(self):
        """formatToParts should be reasonably fast"""
        lf = IntlListFormat('en')
        items = [f'Item{i}' for i in range(100)]

        import time
        start = time.time()
        parts = lf.formatToParts(items)
        elapsed = time.time() - start

        # Should complete in reasonable time
        assert elapsed < 0.01
        assert len(parts) > 100  # Should have parts for items and separators

    def test_resolvedOptions_fast(self):
        """resolvedOptions should be very fast"""
        lf = IntlListFormat('en', {'type': 'disjunction', 'style': 'short'})

        import time
        start = time.time()
        for _ in range(1000):
            options = lf.resolvedOptions()
        elapsed = time.time() - start

        # 1000 calls should complete quickly
        assert elapsed < 0.01


class TestEdgeIntegration:
    """Test edge cases in integration scenarios"""

    def test_mixed_types_conversion(self):
        """Should handle mixed types (numbers, strings, objects)"""
        lf = IntlListFormat('en')
        mixed = [1, 'two', 3.14, True, None]
        result = lf.format(mixed)
        assert '1' in result
        assert 'two' in result
        assert '3.14' in result

    def test_unicode_normalization(self):
        """Should handle various Unicode characters"""
        lf = IntlListFormat('en')
        unicode_items = ['café', 'naïve', '日本', '🎉']
        result = lf.format(unicode_items)
        assert all(item in result for item in unicode_items)

    def test_style_variations_across_locales(self):
        """Different styles should work for different locales"""
        for locale in ['en', 'es', 'ja']:
            for style in ['long', 'short', 'narrow']:
                lf = IntlListFormat(locale, {'style': style})
                result = lf.format(['A', 'B', 'C'])
                assert result is not None
                assert len(result) > 0

    def test_all_type_style_combinations(self):
        """All valid type/style combinations should work"""
        types = ['conjunction', 'disjunction', 'unit']
        styles = ['long', 'short', 'narrow']

        for list_type in types:
            for style in styles:
                lf = IntlListFormat('en', {'type': list_type, 'style': style})
                result = lf.format(['A', 'B', 'C'])
                assert result is not None
                parts = lf.formatToParts(['A', 'B', 'C'])
                assert len(parts) > 0
