"""
Unit Tests for Intl.ListFormat

Tests all 5 requirements:
- FR-ES24-C-043: Constructor with locale and options
- FR-ES24-C-044: format() method
- FR-ES24-C-045: formatToParts() method
- FR-ES24-C-046: Type option (conjunction/disjunction/unit)
- FR-ES24-C-047: resolvedOptions() method
"""

import pytest
from components.intl_listformat.src.list_format import IntlListFormat


class TestConstructor:
    """Tests for FR-ES24-C-043: Constructor with locale and options"""

    def test_constructor_no_args(self):
        """Should create formatter with default locale and options"""
        lf = IntlListFormat()
        assert lf is not None

    def test_constructor_with_string_locale(self):
        """Should accept single locale as string"""
        lf = IntlListFormat('en-US')
        assert lf is not None

    def test_constructor_with_locale_list(self):
        """Should accept list of locales"""
        lf = IntlListFormat(['fr-FR', 'en-US'])
        assert lf is not None

    def test_constructor_with_type_option(self):
        """Should accept type option"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        assert lf is not None
        lf = IntlListFormat('en', {'type': 'disjunction'})
        assert lf is not None
        lf = IntlListFormat('en', {'type': 'unit'})
        assert lf is not None

    def test_constructor_with_style_option(self):
        """Should accept style option"""
        lf = IntlListFormat('en', {'style': 'long'})
        assert lf is not None
        lf = IntlListFormat('en', {'style': 'short'})
        assert lf is not None
        lf = IntlListFormat('en', {'style': 'narrow'})
        assert lf is not None

    def test_constructor_with_localeMatcher_option(self):
        """Should accept localeMatcher option"""
        lf = IntlListFormat('en', {'localeMatcher': 'lookup'})
        assert lf is not None
        lf = IntlListFormat('en', {'localeMatcher': 'best fit'})
        assert lf is not None

    def test_constructor_invalid_type_raises_error(self):
        """Should raise RangeError for invalid type"""
        with pytest.raises(ValueError, match="Invalid type"):
            IntlListFormat('en', {'type': 'invalid'})

    def test_constructor_invalid_style_raises_error(self):
        """Should raise RangeError for invalid style"""
        with pytest.raises(ValueError, match="Invalid style"):
            IntlListFormat('en', {'style': 'invalid'})

    def test_constructor_invalid_localeMatcher_raises_error(self):
        """Should raise RangeError for invalid localeMatcher"""
        with pytest.raises(ValueError, match="Invalid localeMatcher"):
            IntlListFormat('en', {'localeMatcher': 'invalid'})

    def test_constructor_non_dict_options_raises_error(self):
        """Should raise TypeError if options is not dict/None"""
        with pytest.raises(TypeError, match="options must be"):
            IntlListFormat('en', "not a dict")

    def test_constructor_stores_resolved_locale(self):
        """Should store resolved locale"""
        lf = IntlListFormat('en-US')
        # Should have internal locale property
        assert hasattr(lf, '_locale')
        assert lf._locale is not None


class TestFormatMethod:
    """Tests for FR-ES24-C-044: format() method"""

    def test_format_empty_list(self):
        """Should return empty string for empty list"""
        lf = IntlListFormat('en')
        result = lf.format([])
        assert result == ""

    def test_format_single_item(self):
        """Should return single item as-is"""
        lf = IntlListFormat('en')
        result = lf.format(['Apple'])
        assert result == "Apple"

    def test_format_two_items_conjunction(self):
        """Should format two items with conjunction (and)"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['Apple', 'Banana'])
        assert 'and' in result.lower()
        assert 'Apple' in result
        assert 'Banana' in result

    def test_format_three_items_conjunction(self):
        """Should format three items with conjunction"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['Apple', 'Banana', 'Orange'])
        # Should be "Apple, Banana, and Orange"
        assert result == "Apple, Banana, and Orange"

    def test_format_multiple_items_conjunction(self):
        """Should format multiple items with conjunction"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['A', 'B', 'C', 'D'])
        assert result == "A, B, C, and D"

    def test_format_two_items_disjunction(self):
        """Should format two items with disjunction (or)"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        result = lf.format(['red', 'blue'])
        assert 'or' in result.lower()

    def test_format_three_items_disjunction(self):
        """Should format three items with disjunction"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        result = lf.format(['red', 'green', 'blue'])
        assert result == "red, green, or blue"

    def test_format_unit_list(self):
        """Should format unit list without conjunction"""
        lf = IntlListFormat('en', {'type': 'unit'})
        result = lf.format(['5 lb', '12 oz'])
        # Unit lists typically don't have 'and' or 'or'
        assert 'and' not in result.lower()
        assert 'or' not in result.lower()

    def test_format_converts_items_to_string(self):
        """Should convert non-string items to strings"""
        lf = IntlListFormat('en')
        result = lf.format([1, 2, 3])
        assert "1" in result
        assert "2" in result
        assert "3" in result

    def test_format_with_non_iterable_raises_error(self):
        """Should raise TypeError for non-iterable"""
        lf = IntlListFormat('en')
        with pytest.raises(TypeError, match="iterable"):
            lf.format(123)

    def test_format_spanish_locale(self):
        """Should use Spanish conjunction"""
        lf = IntlListFormat('es', {'type': 'conjunction'})
        result = lf.format(['manzana', 'plátano', 'naranja'])
        # Spanish uses 'y' instead of 'and'
        assert 'y' in result

    def test_format_short_style(self):
        """Should apply short style formatting"""
        lf = IntlListFormat('en', {'style': 'short'})
        result = lf.format(['A', 'B', 'C'])
        # Short style might use '&' instead of 'and'
        assert result in ["A, B, & C", "A, B, and C"]  # Allow either

    def test_format_narrow_style(self):
        """Should apply narrow style formatting"""
        lf = IntlListFormat('en', {'style': 'narrow'})
        result = lf.format(['A', 'B', 'C'])
        # Narrow style uses minimal separators
        assert result is not None

    def test_format_special_characters(self):
        """Should handle special characters in list items"""
        lf = IntlListFormat('en')
        result = lf.format(['<html>', 'A & B', '"quote"'])
        assert '<html>' in result
        assert 'A & B' in result

    def test_format_unicode_characters(self):
        """Should handle Unicode characters"""
        lf = IntlListFormat('ja')
        result = lf.format(['りんご', 'バナナ', 'オレンジ'])
        assert 'りんご' in result


class TestFormatToPartsMethod:
    """Tests for FR-ES24-C-045: formatToParts() method"""

    def test_formatToParts_empty_list(self):
        """Should return empty array for empty list"""
        lf = IntlListFormat('en')
        result = lf.formatToParts([])
        assert result == []

    def test_formatToParts_single_item(self):
        """Should return single element part"""
        lf = IntlListFormat('en')
        result = lf.formatToParts(['Apple'])
        assert len(result) == 1
        assert result[0]['type'] == 'element'
        assert result[0]['value'] == 'Apple'

    def test_formatToParts_two_items(self):
        """Should return parts for two items with literal separator"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.formatToParts(['A', 'B'])
        # Should have: element, literal, element
        assert len(result) >= 3
        assert result[0]['type'] == 'element'
        assert result[0]['value'] == 'A'
        assert result[-1]['type'] == 'element'
        assert result[-1]['value'] == 'B'
        # Middle part(s) should be literal
        assert any(p['type'] == 'literal' for p in result[1:-1])

    def test_formatToParts_three_items(self):
        """Should return parts for three items"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.formatToParts(['A', 'B', 'C'])
        # Should alternate: element, literal, element, literal, element
        elements = [p for p in result if p['type'] == 'element']
        literals = [p for p in result if p['type'] == 'literal']
        assert len(elements) == 3
        assert len(literals) >= 2
        assert elements[0]['value'] == 'A'
        assert elements[1]['value'] == 'B'
        assert elements[2]['value'] == 'C'

    def test_formatToParts_part_structure(self):
        """Each part should have 'type' and 'value' properties"""
        lf = IntlListFormat('en')
        result = lf.formatToParts(['X', 'Y'])
        for part in result:
            assert 'type' in part
            assert 'value' in part
            assert part['type'] in ['element', 'literal']
            assert isinstance(part['value'], str)

    def test_formatToParts_disjunction_literal(self):
        """Should use 'or' in literal for disjunction"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        result = lf.formatToParts(['A', 'B', 'C'])
        literals = [p['value'] for p in result if p['type'] == 'literal']
        # At least one literal should contain 'or'
        assert any('or' in lit for lit in literals)

    def test_formatToParts_reconstructs_format(self):
        """Joining parts should equal format() result"""
        lf = IntlListFormat('en')
        items = ['Apple', 'Banana', 'Orange']
        formatted = lf.format(items)
        parts = lf.formatToParts(items)
        reconstructed = ''.join(p['value'] for p in parts)
        assert reconstructed == formatted

    def test_formatToParts_with_non_iterable_raises_error(self):
        """Should raise TypeError for non-iterable"""
        lf = IntlListFormat('en')
        with pytest.raises(TypeError, match="iterable"):
            lf.formatToParts(123)

    def test_formatToParts_preserves_order(self):
        """Parts should maintain correct order"""
        lf = IntlListFormat('en')
        result = lf.formatToParts(['First', 'Second', 'Third'])
        element_values = [p['value'] for p in result if p['type'] == 'element']
        assert element_values == ['First', 'Second', 'Third']

    def test_formatToParts_spanish_locale(self):
        """Should use locale-specific separators in parts"""
        lf = IntlListFormat('es')
        result = lf.formatToParts(['A', 'B', 'C'])
        # Spanish should have 'y' in literal parts
        literals = [p['value'] for p in result if p['type'] == 'literal']
        assert any('y' in lit for lit in literals)


class TestTypeOption:
    """Tests for FR-ES24-C-046: Type option (conjunction/disjunction/unit)"""

    def test_type_conjunction_default(self):
        """Default type should be conjunction"""
        lf = IntlListFormat('en')
        result = lf.format(['A', 'B', 'C'])
        assert 'and' in result

    def test_type_conjunction_explicit(self):
        """Explicit conjunction type should work"""
        lf = IntlListFormat('en', {'type': 'conjunction'})
        result = lf.format(['A', 'B', 'C'])
        assert 'and' in result

    def test_type_disjunction(self):
        """Disjunction type should use 'or'"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        result = lf.format(['A', 'B', 'C'])
        assert 'or' in result
        assert 'and' not in result

    def test_type_unit(self):
        """Unit type should not use conjunction"""
        lf = IntlListFormat('en', {'type': 'unit'})
        result = lf.format(['5 lb', '12 oz'])
        assert 'and' not in result
        assert 'or' not in result

    def test_type_conjunction_spanish(self):
        """Spanish conjunction should use 'y'"""
        lf = IntlListFormat('es', {'type': 'conjunction'})
        result = lf.format(['A', 'B', 'C'])
        assert 'y' in result

    def test_type_disjunction_spanish(self):
        """Spanish disjunction should use 'o'"""
        lf = IntlListFormat('es', {'type': 'disjunction'})
        result = lf.format(['A', 'B', 'C'])
        assert 'o' in result

    def test_type_affects_formatToParts(self):
        """Type option should affect formatToParts output"""
        lf_conj = IntlListFormat('en', {'type': 'conjunction'})
        lf_disj = IntlListFormat('en', {'type': 'disjunction'})
        items = ['A', 'B', 'C']
        parts_conj = lf_conj.formatToParts(items)
        parts_disj = lf_disj.formatToParts(items)
        # The literal parts should be different
        literals_conj = [p['value'] for p in parts_conj if p['type'] == 'literal']
        literals_disj = [p['value'] for p in parts_disj if p['type'] == 'literal']
        assert literals_conj != literals_disj

    def test_type_preserves_through_resolvedOptions(self):
        """Type should be reflected in resolvedOptions"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        options = lf.resolvedOptions()
        assert options['type'] == 'disjunction'


class TestResolvedOptions:
    """Tests for FR-ES24-C-047: resolvedOptions() method"""

    def test_resolvedOptions_returns_dict(self):
        """Should return dictionary"""
        lf = IntlListFormat('en')
        options = lf.resolvedOptions()
        assert isinstance(options, dict)

    def test_resolvedOptions_has_locale(self):
        """Should include locale property"""
        lf = IntlListFormat('en-US')
        options = lf.resolvedOptions()
        assert 'locale' in options
        assert isinstance(options['locale'], str)

    def test_resolvedOptions_has_type(self):
        """Should include type property"""
        lf = IntlListFormat('en', {'type': 'disjunction'})
        options = lf.resolvedOptions()
        assert 'type' in options
        assert options['type'] == 'disjunction'

    def test_resolvedOptions_has_style(self):
        """Should include style property"""
        lf = IntlListFormat('en', {'style': 'short'})
        options = lf.resolvedOptions()
        assert 'style' in options
        assert options['style'] == 'short'

    def test_resolvedOptions_default_values(self):
        """Should return default values when not specified"""
        lf = IntlListFormat('en')
        options = lf.resolvedOptions()
        assert options['type'] == 'conjunction'
        assert options['style'] == 'long'

    def test_resolvedOptions_reflects_actual_locale(self):
        """Should return resolved locale, not requested"""
        lf = IntlListFormat(['fr-FR', 'en-US'])
        options = lf.resolvedOptions()
        # Should resolve to one of the supported locales
        assert options['locale'] in ['fr-FR', 'fr', 'en-US', 'en']


class TestEdgeCases:
    """Additional edge case tests"""

    def test_large_list_performance(self):
        """Should handle large lists efficiently"""
        lf = IntlListFormat('en')
        large_list = [f'Item{i}' for i in range(100)]
        result = lf.format(large_list)
        assert result is not None
        assert 'Item0' in result
        assert 'Item99' in result

    def test_items_with_whitespace(self):
        """Should preserve whitespace in items"""
        lf = IntlListFormat('en')
        result = lf.format(['  spaced  ', 'normal'])
        assert '  spaced  ' in result

    def test_empty_string_items(self):
        """Should handle empty strings in list"""
        lf = IntlListFormat('en')
        result = lf.format(['A', '', 'B'])
        # Empty strings are still items
        parts = lf.formatToParts(['A', '', 'B'])
        elements = [p for p in parts if p['type'] == 'element']
        assert len(elements) == 3

    def test_duplicate_items(self):
        """Should handle duplicate items"""
        lf = IntlListFormat('en')
        result = lf.format(['A', 'A', 'B'])
        assert result == "A, A, and B"

    def test_format_with_generator(self):
        """Should accept generator as iterable"""
        lf = IntlListFormat('en')
        gen = (x for x in ['A', 'B', 'C'])
        result = lf.format(gen)
        assert result == "A, B, and C"

    def test_format_with_tuple(self):
        """Should accept tuple as iterable"""
        lf = IntlListFormat('en')
        result = lf.format(('A', 'B', 'C'))
        assert result == "A, B, and C"
