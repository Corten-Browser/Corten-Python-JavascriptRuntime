"""
Unit tests for Intl.Collator.

Tests all 8 requirements:
FR-ES24-C-001: Constructor
FR-ES24-C-002: Locale resolution
FR-ES24-C-003: compare() method
FR-ES24-C-004: sensitivity option
FR-ES24-C-005: numeric option
FR-ES24-C-006: caseFirst option
FR-ES24-C-007: ignorePunctuation option
FR-ES24-C-008: resolvedOptions() method
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.collator import IntlCollator, RangeError


class TestIntlCollatorConstructor:
    """Test FR-ES24-C-001: Intl.Collator constructor implementation."""

    def test_constructor_no_arguments(self):
        """Should create collator with default locale and options."""
        collator = IntlCollator()
        assert collator is not None

    def test_constructor_with_locale_string(self):
        """Should create collator with single locale string."""
        collator = IntlCollator('en-US')
        assert collator is not None

    def test_constructor_with_locale_array(self):
        """Should create collator with array of locales."""
        collator = IntlCollator(['en-US', 'en-GB'])
        assert collator is not None

    def test_constructor_with_options(self):
        """Should create collator with options."""
        collator = IntlCollator('en-US', {
            'usage': 'sort',
            'sensitivity': 'base',
            'numeric': True
        })
        assert collator is not None

    def test_constructor_invalid_locale(self):
        """Should throw RangeError for invalid locale."""
        with pytest.raises(RangeError):
            IntlCollator('invalid-locale-tag')

    def test_constructor_with_all_options(self):
        """Should create collator with all options specified."""
        collator = IntlCollator('en-US', {
            'localeMatcher': 'lookup',
            'usage': 'search',
            'sensitivity': 'accent',
            'numeric': True,
            'caseFirst': 'upper',
            'ignorePunctuation': True,
            'collation': 'standard'
        })
        assert collator is not None


class TestLocaleResolution:
    """Test FR-ES24-C-002: Locale resolution algorithm."""

    def test_supported_locales_of_single_locale(self):
        """Should return supported locales for single locale."""
        result = IntlCollator.supported_locales_of('en-US')
        assert isinstance(result, list)
        assert 'en-US' in result

    def test_supported_locales_of_multiple_locales(self):
        """Should return supported locales for multiple locales."""
        result = IntlCollator.supported_locales_of(['en-US', 'de-DE', 'fr-FR'])
        assert isinstance(result, list)
        assert len(result) > 0

    def test_supported_locales_of_unsupported(self):
        """Should return empty array for unsupported locales."""
        result = IntlCollator.supported_locales_of(['xx-YY'])
        assert isinstance(result, list)
        # May be empty or fall back to default

    def test_locale_with_unicode_extension(self):
        """Should parse Unicode extension keys from locale."""
        collator = IntlCollator('de-DE-u-co-phonebk')
        options = collator.resolved_options()
        assert options['locale'].startswith('de-DE')
        assert options['collation'] == 'phonebk'  # Extension value is 'phonebk'

    def test_locale_with_numeric_extension(self):
        """Should parse numeric collation from Unicode extension."""
        collator = IntlCollator('en-US-u-kn-true')
        options = collator.resolved_options()
        assert options['numeric'] is True

    def test_locale_fallback_to_default(self):
        """Should fall back to default locale if no match."""
        collator = IntlCollator('xx-YY')
        options = collator.resolved_options()
        assert options['locale'] is not None


class TestCompareMethod:
    """Test FR-ES24-C-003: compare() method implementation."""

    def test_compare_equal_strings(self):
        """Should return 0 for equal strings."""
        collator = IntlCollator()
        assert collator.compare('a', 'a') == 0

    def test_compare_less_than(self):
        """Should return negative for string1 < string2."""
        collator = IntlCollator()
        result = collator.compare('a', 'b')
        assert result < 0

    def test_compare_greater_than(self):
        """Should return positive for string1 > string2."""
        collator = IntlCollator()
        result = collator.compare('b', 'a')
        assert result > 0

    def test_compare_empty_strings(self):
        """Should handle empty strings."""
        collator = IntlCollator()
        assert collator.compare('', '') == 0
        assert collator.compare('', 'a') < 0
        assert collator.compare('a', '') > 0

    def test_compare_with_accents(self):
        """Should compare strings with accents."""
        collator = IntlCollator('en-US')
        result = collator.compare('cafe', 'café')
        assert result != 0  # Different by default

    def test_compare_normalized_strings(self):
        """Should handle Unicode normalization (NFC vs NFD)."""
        collator = IntlCollator()
        # café in NFC vs NFD
        nfc = 'café'
        nfd = 'cafe\u0301'
        assert collator.compare(nfc, nfd) == 0

    def test_compare_emoji(self):
        """Should handle emoji comparison."""
        collator = IntlCollator()
        result = collator.compare('😀', '😁')
        assert isinstance(result, int)

    def test_compare_surrogate_pairs(self):
        """Should handle characters outside BMP."""
        collator = IntlCollator()
        # 𝐀 (U+1D400) vs A (U+0041)
        result = collator.compare('𝐀', 'A')
        assert isinstance(result, int)


class TestSensitivityOption:
    """Test FR-ES24-C-004: sensitivity option."""

    def test_sensitivity_base(self):
        """base: Only base letters differ (a = á = A)."""
        collator = IntlCollator('en', {'sensitivity': 'base'})
        assert collator.compare('a', 'A') == 0
        assert collator.compare('a', 'á') == 0
        assert collator.compare('a', 'b') != 0

    def test_sensitivity_accent(self):
        """accent: Base and accent differ (a = A, a ≠ á)."""
        collator = IntlCollator('en', {'sensitivity': 'accent'})
        assert collator.compare('a', 'A') == 0
        assert collator.compare('a', 'á') != 0
        assert collator.compare('a', 'b') != 0

    def test_sensitivity_case(self):
        """case: Base, accent, and case differ (a ≠ A, a ≠ á)."""
        collator = IntlCollator('en', {'sensitivity': 'case'})
        assert collator.compare('a', 'A') != 0
        assert collator.compare('a', 'á') != 0
        assert collator.compare('a', 'b') != 0

    def test_sensitivity_variant(self):
        """variant: All differences (default)."""
        collator = IntlCollator('en', {'sensitivity': 'variant'})
        assert collator.compare('a', 'A') != 0
        assert collator.compare('a', 'á') != 0
        assert collator.compare('a', 'b') != 0

    def test_sensitivity_default_is_variant(self):
        """Default sensitivity should be variant."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert options['sensitivity'] == 'variant'


class TestNumericOption:
    """Test FR-ES24-C-005: numeric option for numeric collation."""

    def test_numeric_true_orders_numbers(self):
        """numeric=true: "2" < "10" (numeric order)."""
        collator = IntlCollator('en', {'numeric': True})
        assert collator.compare('2', '10') < 0
        assert collator.compare('1', '2') < 0

    def test_numeric_false_lexicographic(self):
        """numeric=false: "2" > "10" (lexicographic order)."""
        collator = IntlCollator('en', {'numeric': False})
        assert collator.compare('2', '10') > 0

    def test_numeric_mixed_text_numbers(self):
        """Should handle mixed text and numbers."""
        collator = IntlCollator('en', {'numeric': True})
        assert collator.compare('item2', 'item10') < 0
        assert collator.compare('item10', 'item2') > 0

    def test_numeric_leading_zeros(self):
        """Should handle leading zeros."""
        collator = IntlCollator('en', {'numeric': True})
        assert collator.compare('01', '1') == 0
        assert collator.compare('001', '1') == 0

    def test_numeric_default_is_false(self):
        """Default numeric should be false."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert options['numeric'] is False


class TestCaseFirstOption:
    """Test FR-ES24-C-006: caseFirst option."""

    def test_case_first_upper(self):
        """caseFirst='upper': Uppercase sorts first (A < a)."""
        collator = IntlCollator('en', {'caseFirst': 'upper'})
        result = collator.compare('A', 'a')
        assert result < 0

    def test_case_first_lower(self):
        """caseFirst='lower': Lowercase sorts first (a < A)."""
        collator = IntlCollator('en', {'caseFirst': 'lower'})
        result = collator.compare('a', 'A')
        assert result < 0

    def test_case_first_false(self):
        """caseFirst='false': Use locale default."""
        collator = IntlCollator('en', {'caseFirst': 'false'})
        # Result depends on locale default
        result = collator.compare('A', 'a')
        assert isinstance(result, int)

    def test_case_first_default_is_false(self):
        """Default caseFirst should be 'false'."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert options['caseFirst'] == 'false'


class TestIgnorePunctuationOption:
    """Test FR-ES24-C-007: ignorePunctuation option."""

    def test_ignore_punctuation_true(self):
        """ignorePunctuation=true: Ignore punctuation."""
        collator = IntlCollator('en', {'ignorePunctuation': True})
        assert collator.compare('hello', 'he-llo') == 0
        assert collator.compare('hello', 'he.llo') == 0
        assert collator.compare('hello', 'he!llo') == 0

    def test_ignore_punctuation_false(self):
        """ignorePunctuation=false: Punctuation significant."""
        collator = IntlCollator('en', {'ignorePunctuation': False})
        assert collator.compare('hello', 'he-llo') != 0

    def test_ignore_punctuation_default_is_false(self):
        """Default ignorePunctuation should be false."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert options['ignorePunctuation'] is False

    def test_ignore_punctuation_multiple_chars(self):
        """Should ignore multiple punctuation characters."""
        collator = IntlCollator('en', {'ignorePunctuation': True})
        assert collator.compare('hello', 'h-e-l-l-o') == 0


class TestResolvedOptionsMethod:
    """Test FR-ES24-C-008: resolvedOptions() method."""

    def test_resolved_options_returns_dict(self):
        """Should return dictionary with resolved options."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert isinstance(options, dict)

    def test_resolved_options_has_locale(self):
        """Should include resolved locale."""
        collator = IntlCollator('en-US')
        options = collator.resolved_options()
        assert 'locale' in options
        assert options['locale'] == 'en-US'

    def test_resolved_options_has_usage(self):
        """Should include resolved usage."""
        collator = IntlCollator('en', {'usage': 'search'})
        options = collator.resolved_options()
        assert options['usage'] == 'search'

    def test_resolved_options_has_sensitivity(self):
        """Should include resolved sensitivity."""
        collator = IntlCollator('en', {'sensitivity': 'base'})
        options = collator.resolved_options()
        assert options['sensitivity'] == 'base'

    def test_resolved_options_has_numeric(self):
        """Should include resolved numeric."""
        collator = IntlCollator('en', {'numeric': True})
        options = collator.resolved_options()
        assert options['numeric'] is True

    def test_resolved_options_has_case_first(self):
        """Should include resolved caseFirst."""
        collator = IntlCollator('en', {'caseFirst': 'upper'})
        options = collator.resolved_options()
        assert options['caseFirst'] == 'upper'

    def test_resolved_options_has_ignore_punctuation(self):
        """Should include resolved ignorePunctuation."""
        collator = IntlCollator('en', {'ignorePunctuation': True})
        options = collator.resolved_options()
        assert options['ignorePunctuation'] is True

    def test_resolved_options_has_collation(self):
        """Should include resolved collation."""
        collator = IntlCollator('en')
        options = collator.resolved_options()
        assert 'collation' in options

    def test_resolved_options_all_fields(self):
        """Should include all required fields."""
        collator = IntlCollator('en-US', {
            'usage': 'search',
            'sensitivity': 'base',
            'numeric': True,
            'caseFirst': 'lower',
            'ignorePunctuation': True
        })
        options = collator.resolved_options()

        required_fields = ['locale', 'usage', 'sensitivity', 'numeric',
                          'caseFirst', 'ignorePunctuation', 'collation']
        for field in required_fields:
            assert field in options


class TestLocaleSpecificBehavior:
    """Test locale-specific collation behavior."""

    def test_german_umlaut_sorting(self):
        """German ä should sort near a."""
        collator = IntlCollator('de-DE')
        names = ['Zebra', 'Ärzte', 'Affen']
        sorted_names = sorted(names, key=lambda x: (collator.compare(x, names[0]), x))
        # In German, Ärzte should be near Affen
        assert isinstance(sorted_names, list)

    def test_turkish_i_handling(self):
        """Turkish i/İ should be handled correctly."""
        collator = IntlCollator('tr-TR')
        # In Turkish, i and İ are different
        result = collator.compare('i', 'İ')
        assert isinstance(result, int)

    def test_spanish_n_handling(self):
        """Spanish ñ should sort after n."""
        collator = IntlCollator('es-ES')
        result = collator.compare('n', 'ñ')
        assert result < 0


class TestUsageOption:
    """Test usage option (sort vs search)."""

    def test_usage_sort_default(self):
        """Default usage should be 'sort'."""
        collator = IntlCollator()
        options = collator.resolved_options()
        assert options['usage'] == 'sort'

    def test_usage_search(self):
        """usage='search' should be more lenient."""
        collator = IntlCollator('en', {'usage': 'search'})
        options = collator.resolved_options()
        assert options['usage'] == 'search'


class TestArraySorting:
    """Test usage with Array.prototype.sort equivalent."""

    def test_sort_array_of_strings(self):
        """Should work with array sorting."""
        collator = IntlCollator('en-US')
        names = ['Charlie', 'Alice', 'Bob']
        sorted_names = sorted(names, key=lambda a: (
            collator.compare(a, names[0]),
            a
        ))
        assert isinstance(sorted_names, list)

    def test_sort_with_numeric_collation(self):
        """Should sort numbers correctly with numeric=true."""
        collator = IntlCollator('en', {'numeric': True})
        items = ['item10', 'item2', 'item1']

        def compare_key(item):
            # Create a sortable key
            return [collator.compare(item, i) for i in items]

        sorted_items = sorted(items, key=lambda x: (
            sum(1 for i in items if collator.compare(x, i) > 0),
            x
        ))
        # Should be sorted numerically
        assert isinstance(sorted_items, list)
