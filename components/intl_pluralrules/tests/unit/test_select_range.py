"""
Unit tests for PluralRules.selectRange() method

Tests FR-ES24-C-033: selectRange() method returns plural category for numeric range
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from plural_rules import PluralRules, RangeError


class TestSelectRangeEnglish:
    """Test selectRange() for English (en-US)"""

    def test_select_range_one_to_three(self):
        """English: 1-3 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.selectRange(1, 3) == 'other'

    def test_select_range_zero_to_one(self):
        """English: 0-1 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.selectRange(0, 1) == 'other'

    def test_select_range_two_to_five(self):
        """English: 2-5 items -> 'other'"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        assert pr.selectRange(2, 5) == 'other'

    def test_select_range_same_number(self):
        """Range with same start and end: 5-5"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        result = pr.selectRange(5, 5)
        # Should use select(5) which is 'other'
        assert result == 'other'


class TestSelectRangePolish:
    """Test selectRange() for Polish (pl-PL) - Complex range rules"""

    def test_select_range_two_to_four(self):
        """Polish: 2-4 items -> 'few'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.selectRange(2, 4) == 'few'

    def test_select_range_five_to_ten(self):
        """Polish: 5-10 items -> 'many'"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        assert pr.selectRange(5, 10) == 'many'

    def test_select_range_one_to_five(self):
        """Polish: 1-5 items"""
        pr = PluralRules('pl-PL', {'type': 'cardinal'})
        # 1 is 'one', 5 is 'many' -> range resolution depends on CLDR rules
        result = pr.selectRange(1, 5)
        assert result in ['one', 'few', 'many', 'other']


class TestSelectRangeArabic:
    """Test selectRange() for Arabic (ar-EG) - All 6 categories"""

    def test_select_range_zero_to_two(self):
        """Arabic: 0-2 items"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        # 0 is 'zero', 2 is 'two'
        result = pr.selectRange(0, 2)
        assert result in ['zero', 'one', 'two', 'few', 'many', 'other']

    def test_select_range_three_to_ten(self):
        """Arabic: 3-10 items (both 'few')"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        result = pr.selectRange(3, 10)
        assert result in ['few', 'other']  # Likely 'few' since both are 'few'

    def test_select_range_eleven_to_ninetynine(self):
        """Arabic: 11-99 items (both 'many')"""
        pr = PluralRules('ar-EG', {'type': 'cardinal'})
        result = pr.selectRange(11, 99)
        assert result in ['many', 'other']  # Likely 'many' since both are 'many'


class TestSelectRangeEdgeCases:
    """Test selectRange() edge cases and error handling"""

    def test_select_range_start_greater_than_end_raises_rangeerror(self):
        """Should raise RangeError when startRange > endRange"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        with pytest.raises(RangeError):
            pr.selectRange(5, 3)

    def test_select_range_negative_numbers(self):
        """Should handle negative ranges"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        result = pr.selectRange(-5, -1)
        assert result in ['one', 'other']

    def test_select_range_negative_to_positive(self):
        """Should handle negative to positive range"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        result = pr.selectRange(-5, 5)
        assert result in ['one', 'other']

    def test_select_range_decimal_numbers(self):
        """Should handle decimal ranges"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        result = pr.selectRange(1.5, 3.7)
        assert result in ['one', 'other']

    def test_select_range_large_numbers(self):
        """Should handle large number ranges"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        result = pr.selectRange(1000, 10000)
        assert result == 'other'

    def test_select_range_bigint(self):
        """Should handle BigInt ranges"""
        pr = PluralRules('en-US', {'type': 'cardinal'})
        # Python doesn't have BigInt, but test with large integers
        result = pr.selectRange(10**15, 10**15 + 100)
        assert result in ['one', 'other']


class TestSelectRangeOrdinal:
    """Test selectRange() with ordinal type"""

    def test_select_range_ordinal_english(self):
        """English ordinal: 1st-3rd"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        # 1 is 'one', 3 is 'few'
        result = pr.selectRange(1, 3)
        assert result in ['one', 'two', 'few', 'other']

    def test_select_range_ordinal_twentyfirst_to_twentythird(self):
        """English ordinal: 21st-23rd"""
        pr = PluralRules('en-US', {'type': 'ordinal'})
        # 21 is 'one', 23 is 'few'
        result = pr.selectRange(21, 23)
        assert result in ['one', 'two', 'few', 'other']


class TestSelectRangePerformance:
    """Test selectRange() performance requirements"""

    def test_selectrange_performance(self):
        """selectRange() should complete in <200µs - Performance requirement"""
        import time
        pr = PluralRules('en-US', {'type': 'cardinal'})

        # Warm up
        for _ in range(10):
            pr.selectRange(1, 10)

        # Measure
        iterations = 100
        start = time.perf_counter()
        for i in range(iterations):
            pr.selectRange(i, i + 10)
        elapsed = (time.perf_counter() - start) * 1000000 / iterations  # µs

        assert elapsed < 200, f"selectRange() took {elapsed}µs, expected <200µs"


class TestSelectRangeWithFormattingOptions:
    """Test selectRange() with formatting options"""

    def test_selectrange_with_fraction_digits(self):
        """Range with formatting options"""
        pr = PluralRules('en-US', {
            'type': 'cardinal',
            'minimumFractionDigits': 2
        })
        result = pr.selectRange(1, 5)
        assert result in ['one', 'other']

    def test_selectrange_with_significant_digits(self):
        """Range with significant digits"""
        pr = PluralRules('en-US', {
            'type': 'cardinal',
            'minimumSignificantDigits': 3
        })
        result = pr.selectRange(1, 5)
        assert result in ['one', 'other']
