"""
Unit tests for PluralRules.resolvedOptions() method

Tests FR-ES24-C-036: resolvedOptions() returns locale, type, and formatting options
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from plural_rules import PluralRules


class TestResolvedOptions:
    """Test resolvedOptions() method - FR-ES24-C-036"""

    def test_resolved_options_returns_object(self):
        """Should return an object"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert isinstance(options, dict)

    def test_resolved_options_has_locale(self):
        """Should include locale property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'locale' in options
        assert isinstance(options['locale'], str)

    def test_resolved_options_locale_value(self):
        """Should return resolved locale"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert options['locale'] == 'en-US'

    def test_resolved_options_has_type(self):
        """Should include type property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'type' in options
        assert options['type'] in ['cardinal', 'ordinal']

    def test_resolved_options_type_cardinal(self):
        """Should return 'cardinal' type when specified"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        options = pr.resolvedOptions()
        assert options['type'] == 'cardinal'

    def test_resolved_options_type_ordinal(self):
        """Should return 'ordinal' type when specified"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        options = pr.resolvedOptions()
        assert options['type'] == 'ordinal'

    def test_resolved_options_type_default(self):
        """Should return 'cardinal' as default type"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert options['type'] == 'cardinal'

    def test_resolved_options_has_minimum_integer_digits(self):
        """Should include minimumIntegerDigits property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'minimumIntegerDigits' in options
        assert isinstance(options['minimumIntegerDigits'], int)

    def test_resolved_options_minimum_integer_digits_default(self):
        """Should return default minimumIntegerDigits = 1"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert options['minimumIntegerDigits'] == 1

    def test_resolved_options_minimum_integer_digits_custom(self):
        """Should return custom minimumIntegerDigits"""
        pr = PluralRules('en-US', {'minimumIntegerDigits': 3})
        options = pr.resolvedOptions()
        assert options['minimumIntegerDigits'] == 3

    def test_resolved_options_has_minimum_fraction_digits(self):
        """Should include minimumFractionDigits property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'minimumFractionDigits' in options
        assert isinstance(options['minimumFractionDigits'], int)

    def test_resolved_options_minimum_fraction_digits_default(self):
        """Should return default minimumFractionDigits = 0"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert options['minimumFractionDigits'] == 0

    def test_resolved_options_minimum_fraction_digits_custom(self):
        """Should return custom minimumFractionDigits"""
        pr = PluralRules('en-US', {'minimumFractionDigits': 2})
        options = pr.resolvedOptions()
        assert options['minimumFractionDigits'] == 2

    def test_resolved_options_has_maximum_fraction_digits(self):
        """Should include maximumFractionDigits property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'maximumFractionDigits' in options
        assert isinstance(options['maximumFractionDigits'], int)

    def test_resolved_options_maximum_fraction_digits_default(self):
        """Should return default maximumFractionDigits = 3"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert options['maximumFractionDigits'] == 3

    def test_resolved_options_maximum_fraction_digits_custom(self):
        """Should return custom maximumFractionDigits"""
        pr = PluralRules('en-US', {'maximumFractionDigits': 5})
        options = pr.resolvedOptions()
        assert options['maximumFractionDigits'] == 5

    def test_resolved_options_has_plural_categories(self):
        """Should include pluralCategories property"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'pluralCategories' in options
        assert isinstance(options['pluralCategories'], list)

    def test_resolved_options_plural_categories_english(self):
        """Should return correct plural categories for English"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        options = pr.resolvedOptions()
        # English cardinal has 'one' and 'other'
        assert set(options['pluralCategories']) == {'one', 'other'}

    def test_resolved_options_plural_categories_arabic(self):
        """Should return all 6 categories for Arabic"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        options = pr.resolvedOptions()
        # Arabic has all 6 categories
        assert set(options['pluralCategories']) == {'zero', 'one', 'two', 'few', 'many', 'other'}

    def test_resolved_options_plural_categories_polish(self):
        """Should return correct categories for Polish"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        options = pr.resolvedOptions()
        # Polish has 'one', 'few', 'many', 'other'
        assert set(options['pluralCategories']) == {'one', 'few', 'many', 'other'}

    def test_resolved_options_plural_categories_japanese(self):
        """Should return minimal categories for Japanese"""
        pr = PluralRules('ja-JP', {'type': 'cardinal'})
        options = pr.resolvedOptions()
        # Japanese only has 'other'
        assert set(options['pluralCategories']) == {'other'}

    def test_resolved_options_plural_categories_ordinal_english(self):
        """Should return ordinal categories for English"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        options = pr.resolvedOptions()
        # English ordinal has 'one', 'two', 'few', 'other'
        assert set(options['pluralCategories']) == {'one', 'two', 'few', 'other'}

    def test_resolved_options_significant_digits_undefined_by_default(self):
        """Should return undefined for significant digits when not set"""
        pr = PluralRules('en-US')
        options = pr.resolvedOptions()
        assert 'minimumSignificantDigits' in options
        assert 'maximumSignificantDigits' in options
        # Should be None/undefined when not set
        assert options['minimumSignificantDigits'] is None
        assert options['maximumSignificantDigits'] is None

    def test_resolved_options_significant_digits_when_set(self):
        """Should return significant digits when set"""
        pr = PluralRules('en-US', {
            'minimumSignificantDigits': 2,
            'maximumSignificantDigits': 4
        })
        options = pr.resolvedOptions()
        assert options['minimumSignificantDigits'] == 2
        assert options['maximumSignificantDigits'] == 4

    def test_resolved_options_complex_configuration(self):
        """Should return all options for complex configuration"""
        pr = PluralRules('ar-EG', {
            'type': 'cardinal',
            'minimumIntegerDigits': 2,
            'minimumFractionDigits': 2,
            'maximumFractionDigits': 4
        })
        options = pr.resolvedOptions()

        assert options['locale'] == 'ar-EG'
        assert options['type'] == 'cardinal'
        assert options['minimumIntegerDigits'] == 2
        assert options['minimumFractionDigits'] == 2
        assert options['maximumFractionDigits'] == 4
        assert options['minimumSignificantDigits'] is None
        assert options['maximumSignificantDigits'] is None
        assert set(options['pluralCategories']) == {'zero', 'one', 'two', 'few', 'many', 'other'}

    def test_resolved_options_locale_fallback(self):
        """Should return resolved locale with fallback"""
        pr = PluralRules('en-US-x-custom')
        options = pr.resolvedOptions()
        # Should resolve to valid BCP 47 locale
        assert isinstance(options['locale'], str)
        assert len(options['locale']) > 0

    def test_resolved_options_immutable(self):
        """Modifying returned object should not affect instance"""
        pr = PluralRules('en-US')
        options1 = pr.resolvedOptions()
        options1['type'] = 'ordinal'  # Try to modify

        options2 = pr.resolvedOptions()
        # Should still be 'cardinal'
        assert options2['type'] == 'cardinal'

    def test_resolved_options_multiple_calls(self):
        """Multiple calls should return equivalent objects"""
        pr = PluralRules('en-US', {'minimumFractionDigits': 2})
        options1 = pr.resolvedOptions()
        options2 = pr.resolvedOptions()

        assert options1 == options2
        assert options1 is not options2  # Different objects
