"""
Unit tests for CLDRDataProvider - CLDR plural rule data provider

Tests data provider for CLDR plural rules
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from rules import CLDRDataProvider


class TestCLDRDataProvider:
    """Test CLDRDataProvider class"""

    def test_provider_get_cardinal_rules_english(self):
        """Should provide cardinal rules for English"""
        provider = CLDRDataProvider()
        rules = provider.getCardinalRules('en-US')

        assert isinstance(rules, dict)
        assert 'one' in rules
        assert 'other' in rules
        # English only has 'one' and 'other' for cardinal
        assert callable(rules['one']) or isinstance(rules['one'], type(lambda: None))

    def test_provider_get_cardinal_rules_arabic(self):
        """Should provide all 6 categories for Arabic"""
        provider = CLDRDataProvider()
        rules = provider.getCardinalRules('ar-EG')

        assert isinstance(rules, dict)
        assert 'zero' in rules
        assert 'one' in rules
        assert 'two' in rules
        assert 'few' in rules
        assert 'many' in rules
        assert 'other' in rules

    def test_provider_get_cardinal_rules_polish(self):
        """Should provide Polish cardinal rules"""
        provider = CLDRDataProvider()
        rules = provider.getCardinalRules('pl-PL')

        assert isinstance(rules, dict)
        assert 'one' in rules
        assert 'few' in rules
        assert 'many' in rules
        assert 'other' in rules

    def test_provider_get_cardinal_rules_japanese(self):
        """Should provide Japanese cardinal rules (minimal)"""
        provider = CLDRDataProvider()
        rules = provider.getCardinalRules('ja-JP')

        assert isinstance(rules, dict)
        assert 'other' in rules
        # Japanese only has 'other'
        assert len(rules) == 1

    def test_provider_get_ordinal_rules_english(self):
        """Should provide ordinal rules for English"""
        provider = CLDRDataProvider()
        rules = provider.getOrdinalRules('en-US')

        assert isinstance(rules, dict)
        assert 'one' in rules
        assert 'two' in rules
        assert 'few' in rules
        assert 'other' in rules

    def test_provider_get_range_rules_english(self):
        """Should provide range resolution rules for English"""
        provider = CLDRDataProvider()
        rules = provider.getRangeRules('en-US')

        assert isinstance(rules, dict)
        # Range rules map (start, end) -> result
        # Example: ('one', 'other') -> 'other'

    def test_provider_get_plural_categories_cardinal_english(self):
        """Should return cardinal categories for English"""
        provider = CLDRDataProvider()
        categories = provider.getPluralCategories('en-US', 'cardinal')

        assert isinstance(categories, list)
        assert set(categories) == {'one', 'other'}

    def test_provider_get_plural_categories_cardinal_arabic(self):
        """Should return all 6 categories for Arabic"""
        provider = CLDRDataProvider()
        categories = provider.getPluralCategories('ar-EG', 'cardinal')

        assert isinstance(categories, list)
        assert set(categories) == {'zero', 'one', 'two', 'few', 'many', 'other'}

    def test_provider_get_plural_categories_ordinal_english(self):
        """Should return ordinal categories for English"""
        provider = CLDRDataProvider()
        categories = provider.getPluralCategories('en-US', 'ordinal')

        assert isinstance(categories, list)
        assert set(categories) == {'one', 'two', 'few', 'other'}

    def test_provider_get_plural_categories_cardinal_japanese(self):
        """Should return minimal categories for Japanese"""
        provider = CLDRDataProvider()
        categories = provider.getPluralCategories('ja-JP', 'cardinal')

        assert isinstance(categories, list)
        assert set(categories) == {'other'}

    def test_provider_lazy_loading(self):
        """Should support lazy loading of locale data"""
        provider = CLDRDataProvider()

        # First access loads data
        rules1 = provider.getCardinalRules('en-US')

        # Second access should use cached data
        rules2 = provider.getCardinalRules('en-US')

        # Should be the same data (or equivalent)
        assert rules1.keys() == rules2.keys()

    def test_provider_multiple_locales(self):
        """Should handle multiple locales simultaneously"""
        provider = CLDRDataProvider()

        rules_en = provider.getCardinalRules('en-US')
        rules_ar = provider.getCardinalRules('ar-EG')
        rules_pl = provider.getCardinalRules('pl-PL')

        # Each locale should have its own rules
        assert len(rules_en) != len(rules_ar)
        assert len(rules_ar) != len(rules_pl)

    def test_provider_locale_fallback(self):
        """Should handle locale fallback for unavailable locales"""
        provider = CLDRDataProvider()

        # If specific locale not available, should fall back to parent
        rules = provider.getCardinalRules('en-US-x-custom')

        # Should still return valid rules (fallback to en or en-US)
        assert isinstance(rules, dict)
        assert 'other' in rules

    def test_provider_supports_required_locales(self):
        """Should support all required locales from contract"""
        provider = CLDRDataProvider()
        required_locales = ['en-US', 'ar-EG', 'pl-PL', 'ja-JP', 'cy-GB', 'fr-FR', 'ru-RU', 'zh-CN']

        for locale in required_locales:
            rules = provider.getCardinalRules(locale)
            assert isinstance(rules, dict)
            assert len(rules) > 0

    def test_provider_cardinal_vs_ordinal_different(self):
        """Cardinal and ordinal rules should differ for same locale"""
        provider = CLDRDataProvider()

        cardinal = provider.getCardinalRules('en-US')
        ordinal = provider.getOrdinalRules('en-US')

        # English cardinal has 'one', 'other'
        # English ordinal has 'one', 'two', 'few', 'other'
        assert len(cardinal) != len(ordinal)

    def test_provider_get_categories_matches_rules(self):
        """getPluralCategories should match keys in getCardinalRules"""
        provider = CLDRDataProvider()

        rules = provider.getCardinalRules('ar-EG')
        categories = provider.getPluralCategories('ar-EG', 'cardinal')

        # Categories should match rule keys
        assert set(categories) == set(rules.keys())
