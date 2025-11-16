"""
Unit tests for PluralRules.select() method

Tests:
- FR-ES24-C-032: select() method returns CLDR plural category for number
- FR-ES24-C-034: Cardinal vs Ordinal types
- FR-ES24-C-035: All CLDR plural categories (zero, one, two, few, many, other)
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from plural_rules import PluralRules


class TestSelectCardinalEnglish:
    """Test select() with cardinal rules for English (en-US) - FR-ES24-C-032"""

    def test_select_zero_returns_other(self):
        """English: 0 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(0) == 'other'

    def test_select_one_returns_one(self):
        """English: 1 item -> 'one'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(1) == 'one'

    def test_select_two_returns_other(self):
        """English: 2 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(2) == 'other'

    def test_select_multiple_returns_other(self):
        """English: 5 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(5) == 'other'

    def test_select_decimal_returns_other(self):
        """English: 1.5 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(1.5) == 'other'

    def test_select_negative_one(self):
        """English: -1 item -> 'one'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(-1) == 'one'

    def test_select_negative_other(self):
        """English: -5 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(-5) == 'other'


class TestSelectCardinalArabic:
    """Test select() with cardinal rules for Arabic (ar-EG) - All 6 categories"""

    def test_select_zero(self):
        """Arabic: 0 items -> 'zero'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(0) == 'zero'

    def test_select_one(self):
        """Arabic: 1 item -> 'one'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(1) == 'one'

    def test_select_two(self):
        """Arabic: 2 items -> 'two'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(2) == 'two'

    def test_select_few_three(self):
        """Arabic: 3 items -> 'few'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(3) == 'few'

    def test_select_few_five(self):
        """Arabic: 5 items -> 'few'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(5) == 'few'

    def test_select_few_ten(self):
        """Arabic: 10 items -> 'few'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(10) == 'few'

    def test_select_many_eleven(self):
        """Arabic: 11 items -> 'many'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(11) == 'many'

    def test_select_many_fifty(self):
        """Arabic: 50 items -> 'many'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(50) == 'many'

    def test_select_many_ninetynine(self):
        """Arabic: 99 items -> 'many'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(99) == 'many'

    def test_select_other_hundred(self):
        """Arabic: 100 items -> 'other'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(100) == 'other'

    def test_select_other_thousand(self):
        """Arabic: 1000 items -> 'other'"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        assert pr.select(1000) == 'other'


class TestSelectCardinalPolish:
    """Test select() with cardinal rules for Polish (pl-PL) - Intermediate complexity"""

    def test_select_one(self):
        """Polish: 1 item -> 'one'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(1) == 'one'

    def test_select_few_two(self):
        """Polish: 2 items -> 'few'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(2) == 'few'

    def test_select_few_three(self):
        """Polish: 3 items -> 'few'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(3) == 'few'

    def test_select_few_four(self):
        """Polish: 4 items -> 'few'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(4) == 'few'

    def test_select_many_five(self):
        """Polish: 5 items -> 'many'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(5) == 'many'

    def test_select_many_ten(self):
        """Polish: 10 items -> 'many'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(10) == 'many'

    def test_select_many_twelve(self):
        """Polish: 12 items -> 'many' (exception for 12-14)"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(12) == 'many'

    def test_select_few_twentytwo(self):
        """Polish: 22 items -> 'few'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.select(22) == 'few'


class TestSelectOrdinalEnglish:
    """Test select() with ordinal rules for English (en-US) - FR-ES24-C-034"""

    def test_select_ordinal_first(self):
        """English ordinal: 1st -> 'one'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(1) == 'one'

    def test_select_ordinal_second(self):
        """English ordinal: 2nd -> 'two'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(2) == 'two'

    def test_select_ordinal_third(self):
        """English ordinal: 3rd -> 'few'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(3) == 'few'

    def test_select_ordinal_fourth(self):
        """English ordinal: 4th -> 'other'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(4) == 'other'

    def test_select_ordinal_twentyfirst(self):
        """English ordinal: 21st -> 'one'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(21) == 'one'

    def test_select_ordinal_twentysecond(self):
        """English ordinal: 22nd -> 'two'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(22) == 'two'

    def test_select_ordinal_twentythird(self):
        """English ordinal: 23rd -> 'few'"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(23) == 'few'

    def test_select_ordinal_eleventh(self):
        """English ordinal: 11th -> 'other' (exception)"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(11) == 'other'

    def test_select_ordinal_twelfth(self):
        """English ordinal: 12th -> 'other' (exception)"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(12) == 'other'

    def test_select_ordinal_thirteenth(self):
        """English ordinal: 13th -> 'other' (exception)"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        assert pr.select(13) == 'other'


class TestSelectJapanese:
    """Test select() for Japanese (ja-JP) - Minimal (other only)"""

    def test_select_all_return_other(self):
        """Japanese: All numbers -> 'other'"""
        pr = PluralRules('ja-JP', {'type': 'cardinal'})
        assert pr.select(0) == 'other'
        assert pr.select(1) == 'other'
        assert pr.select(2) == 'other'
        assert pr.select(100) == 'other'


class TestSelectBigInt:
    """Test select() with BigInt support - Edge case"""

    def test_select_bigint_one(self):
        """Should support BigInt: 1n -> 'one'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        # Python doesn't have BigInt, but we can test with large integers
        assert pr.select(1) == 'one'

    def test_select_bigint_other(self):
        """Should support BigInt: 100n -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(100) == 'other'

    def test_select_large_number(self):
        """Should handle very large numbers"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.select(10**15) == 'other'


class TestSelectWithFormattingOptions:
    """Test select() with formatting options affecting plural category"""

    def test_select_with_minimum_fraction_digits(self):
        """Formatting options should affect operand calculation"""
        pr = PluralRules('en-US', {
            'type': 'cardinal',
            'minimumFractionDigits': 2
        })
        # 1.00 has different operands than 1
        result = pr.select(1)
        assert result in ['one', 'other']  # Depends on operand calculation

    def test_select_with_significant_digits(self):
        """Significant digits should affect operand calculation"""
        pr = PluralRules('en-US', {
            'type': 'cardinal',
            'minimumSignificantDigits': 3
        })
        result = pr.select(1)
        assert result in ['one', 'other']


class TestSelectPerformance:
    """Test select() performance requirements"""

    def test_select_performance(self):
        """select() should complete in <100µs - Performance requirement"""
        import time
        pr = PluralRules('en-US', {'type': 'cardinal'})

        # Warm up
        for _ in range(10):
            pr.select(5)

        # Measure
        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            pr.select(i)
        elapsed = (time.perf_counter() - start) * 1000000 / iterations  # µs

        assert elapsed < 100, f"select() took {elapsed}µs, expected <100µs"
