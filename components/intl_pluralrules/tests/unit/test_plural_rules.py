"""
Unit tests for Intl.PluralRules constructor

Tests FR-ES24-C-031: Intl.PluralRules constructor with locale and options support
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from plural_rules import PluralRules, RangeError


class TestPluralRulesConstructor:
    """Test Intl.PluralRules constructor - FR-ES24-C-031"""

    def test_constructor_no_arguments(self):
        """Should create PluralRules with default locale"""
        pr = PluralRules()
        assert pr is not None

    def test_constructor_with_locale_string(self):
        """Should accept single locale string"""
        pr = PluralRules('en-US')
        assert pr is not None

    def test_constructor_with_locale_array(self):
        """Should accept array of locales"""
        pr = PluralRules(['en-US', 'en-GB'])
        assert pr is not None

    def test_constructor_with_undefined_locale(self):
        """Should accept None/undefined locale"""
        pr = PluralRules(None)
        assert pr is not None

    def test_constructor_with_options(self):
        """Should accept options object"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr is not None

    def test_constructor_cardinal_type(self):
        """Should support cardinal type option"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr is not None

    def test_constructor_ordinal_type(self):
        """Should support ordinal type option"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr is not None

    def test_constructor_locale_matcher_lookup(self):
        """Should support lookup locale matcher"""
        pr = PluralRules('en-US', {'localeMatcher': 'lookup'})
        assert pr is not None

    def test_constructor_locale_matcher_best_fit(self):
        """Should support best fit locale matcher (default)"""
        pr = PluralRules('en-US', {'localeMatcher': 'best fit'})
        assert pr is not None

    def test_constructor_minimum_integer_digits(self):
        """Should accept minimumIntegerDigits option"""
        pr = PluralRules('en-US', {'minimumIntegerDigits': 3})
        assert pr is not None

    def test_constructor_minimum_fraction_digits(self):
        """Should accept minimumFractionDigits option"""
        pr = PluralRules('en-US', {'minimumFractionDigits': 2})
        assert pr is not None

    def test_constructor_maximum_fraction_digits(self):
        """Should accept maximumFractionDigits option"""
        pr = PluralRules('en-US', {'maximumFractionDigits': 5})
        assert pr is not None

    def test_constructor_significant_digits(self):
        """Should accept significant digits options"""
        pr = PluralRules('en-US', {
            'minimumSignificantDigits': 2,
            'maximumSignificantDigits': 4
        })
        assert pr is not None

    def test_constructor_invalid_type_raises_typeerror(self):
        """Should raise TypeError for invalid type"""
        with pytest.raises(TypeError):
            PluralRules('en-US', {'type': 'invalid'})

    def test_constructor_invalid_options_raises_typeerror(self):
        """Should raise TypeError for invalid options object"""
        with pytest.raises(TypeError):
            PluralRules('en-US', 'invalid')

    def test_constructor_minimum_integer_digits_too_small(self):
        """Should raise RangeError for minimumIntegerDigits < 1"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumIntegerDigits': 0})

    def test_constructor_minimum_integer_digits_too_large(self):
        """Should raise RangeError for minimumIntegerDigits > 21"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumIntegerDigits': 22})

    def test_constructor_minimum_fraction_digits_negative(self):
        """Should raise RangeError for minimumFractionDigits < 0"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumFractionDigits': -1})

    def test_constructor_minimum_fraction_digits_too_large(self):
        """Should raise RangeError for minimumFractionDigits > 20"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumFractionDigits': 21})

    def test_constructor_maximum_fraction_digits_negative(self):
        """Should raise RangeError for maximumFractionDigits < 0"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'maximumFractionDigits': -1})

    def test_constructor_maximum_fraction_digits_too_large(self):
        """Should raise RangeError for maximumFractionDigits > 20"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'maximumFractionDigits': 21})

    def test_constructor_minimum_significant_digits_too_small(self):
        """Should raise RangeError for minimumSignificantDigits < 1"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumSignificantDigits': 0})

    def test_constructor_minimum_significant_digits_too_large(self):
        """Should raise RangeError for minimumSignificantDigits > 21"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'minimumSignificantDigits': 22})

    def test_constructor_maximum_significant_digits_too_small(self):
        """Should raise RangeError for maximumSignificantDigits < 1"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'maximumSignificantDigits': 0})

    def test_constructor_maximum_significant_digits_too_large(self):
        """Should raise RangeError for maximumSignificantDigits > 21"""
        with pytest.raises(RangeError):
            PluralRules('en-US', {'maximumSignificantDigits': 22})

    def test_constructor_performance(self):
        """Constructor should complete in <2ms - Performance requirement"""
        import time
        start = time.perf_counter()
        pr = PluralRules('en-US')
        elapsed = (time.perf_counter() - start) * 1000  # ms
        assert elapsed < 2.0, f"Constructor took {elapsed}ms, expected <2ms"

    def test_constructor_multiple_locales(self):
        """Should handle multiple common locales"""
        locales = ['en-US', 'ar-EG', 'pl-PL', 'ja-JP', 'cy-GB', 'fr-FR', 'ru-RU', 'zh-CN']
        for locale in locales:
            pr = PluralRules(locale)
            assert pr is not None
