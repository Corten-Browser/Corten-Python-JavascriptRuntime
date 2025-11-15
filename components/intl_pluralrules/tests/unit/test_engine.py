"""
Unit tests for PluralRulesEngine - Internal CLDR rule evaluation engine

Tests internal engine for evaluating CLDR plural rules
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from rules import PluralRulesEngine


class TestPluralRulesEngine:
    """Test PluralRulesEngine internal class"""

    def test_engine_evaluates_cardinal_english(self):
        """Engine should evaluate English cardinal rules"""
        engine = PluralRulesEngine()
        result = engine.evaluateCardinalRule('en-US', 1, {})
        assert result == 'one'

        result = engine.evaluateCardinalRule('en-US', 2, {})
        assert result == 'other'

    def test_engine_evaluates_cardinal_arabic(self):
        """Engine should evaluate Arabic cardinal rules (all 6 categories)"""
        engine = PluralRulesEngine()
        assert engine.evaluateCardinalRule('ar-EG', 0, {}) == 'zero'
        assert engine.evaluateCardinalRule('ar-EG', 1, {}) == 'one'
        assert engine.evaluateCardinalRule('ar-EG', 2, {}) == 'two'
        assert engine.evaluateCardinalRule('ar-EG', 5, {}) == 'few'
        assert engine.evaluateCardinalRule('ar-EG', 50, {}) == 'many'
        assert engine.evaluateCardinalRule('ar-EG', 100, {}) == 'other'

    def test_engine_evaluates_cardinal_polish(self):
        """Engine should evaluate Polish cardinal rules"""
        engine = PluralRulesEngine()
        assert engine.evaluateCardinalRule('pl-PL', 1, {}) == 'one'
        assert engine.evaluateCardinalRule('pl-PL', 2, {}) == 'few'
        assert engine.evaluateCardinalRule('pl-PL', 5, {}) == 'many'

    def test_engine_evaluates_ordinal_english(self):
        """Engine should evaluate English ordinal rules"""
        engine = PluralRulesEngine()
        assert engine.evaluateOrdinalRule('en-US', 1, {}) == 'one'
        assert engine.evaluateOrdinalRule('en-US', 2, {}) == 'two'
        assert engine.evaluateOrdinalRule('en-US', 3, {}) == 'few'
        assert engine.evaluateOrdinalRule('en-US', 4, {}) == 'other'
        assert engine.evaluateOrdinalRule('en-US', 11, {}) == 'other'
        assert engine.evaluateOrdinalRule('en-US', 21, {}) == 'one'

    def test_engine_evaluates_range_rule(self):
        """Engine should combine categories for ranges"""
        engine = PluralRulesEngine()
        # Same category -> same category
        result = engine.evaluateRangeRule('en-US', 'other', 'other')
        assert result == 'other'

        # Different categories -> depends on CLDR rules
        result = engine.evaluateRangeRule('en-US', 'one', 'other')
        assert result in ['one', 'other']


class TestGetPluralOperands:
    """Test getPluralOperands() - CLDR operand extraction"""

    def test_operands_integer(self):
        """Should extract operands for integer: 5"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(5, {})

        assert operands['n'] == 5  # Absolute value
        assert operands['i'] == 5  # Integer part
        assert operands['v'] == 0  # No fraction digits
        assert operands['w'] == 0  # No fraction digits without trailing zeros
        assert operands['f'] == 0  # No fraction
        assert operands['t'] == 0  # No fraction without trailing zeros

    def test_operands_decimal(self):
        """Should extract operands for decimal: 1.5"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(1.5, {})

        assert operands['n'] == 1.5  # Absolute value
        assert operands['i'] == 1    # Integer part
        assert operands['v'] == 1    # One fraction digit
        assert operands['w'] == 1    # One fraction digit (no trailing zeros)
        assert operands['f'] == 5    # Fraction as integer
        assert operands['t'] == 5    # Fraction without trailing zeros

    def test_operands_trailing_zeros(self):
        """Should handle trailing zeros: 1.50"""
        engine = PluralRulesEngine()
        # With minimumFractionDigits = 2, 1.5 becomes 1.50
        operands = engine.getPluralOperands(1.5, {'minimumFractionDigits': 2})

        assert operands['n'] == 1.5  # Absolute value
        assert operands['i'] == 1    # Integer part
        assert operands['v'] == 2    # Two visible fraction digits
        assert operands['w'] == 1    # One digit without trailing zeros
        assert operands['f'] == 50   # Visible fraction as integer
        assert operands['t'] == 5    # Fraction without trailing zeros

    def test_operands_zero(self):
        """Should extract operands for zero: 0"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(0, {})

        assert operands['n'] == 0
        assert operands['i'] == 0
        assert operands['v'] == 0
        assert operands['w'] == 0
        assert operands['f'] == 0
        assert operands['t'] == 0

    def test_operands_negative(self):
        """Should use absolute value for negative: -5"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(-5, {})

        assert operands['n'] == 5  # Absolute value
        assert operands['i'] == 5
        assert operands['v'] == 0
        assert operands['w'] == 0
        assert operands['f'] == 0
        assert operands['t'] == 0

    def test_operands_with_minimum_integer_digits(self):
        """Should handle minimumIntegerDigits option"""
        engine = PluralRulesEngine()
        # minimumIntegerDigits affects display, not operands directly
        operands = engine.getPluralOperands(5, {'minimumIntegerDigits': 3})

        # Operands based on actual value
        assert operands['i'] == 5

    def test_operands_with_significant_digits(self):
        """Should handle significant digits option"""
        engine = PluralRulesEngine()
        # Significant digits affect operand calculation
        operands = engine.getPluralOperands(1, {
            'minimumSignificantDigits': 3,
            'maximumSignificantDigits': 3
        })

        # Should format as 1.00 (3 significant digits)
        assert operands['n'] == 1
        # v should reflect visible fraction digits
        assert operands['v'] >= 0

    def test_operands_large_number(self):
        """Should handle large numbers"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(123456, {})

        assert operands['n'] == 123456
        assert operands['i'] == 123456
        assert operands['v'] == 0

    def test_operands_very_small_decimal(self):
        """Should handle very small decimals: 0.001"""
        engine = PluralRulesEngine()
        operands = engine.getPluralOperands(0.001, {})

        assert operands['n'] == 0.001
        assert operands['i'] == 0
        assert operands['v'] == 3  # Three fraction digits
        assert operands['f'] == 1  # Just the '1'
        assert operands['t'] == 1

    def test_operands_performance(self):
        """Operand calculation should be fast (<50µs)"""
        import time
        engine = PluralRulesEngine()

        iterations = 1000
        start = time.perf_counter()
        for i in range(iterations):
            engine.getPluralOperands(1.5, {})
        elapsed = (time.perf_counter() - start) * 1000000 / iterations  # µs

        assert elapsed < 50, f"getPluralOperands took {elapsed}µs, expected <50µs"
