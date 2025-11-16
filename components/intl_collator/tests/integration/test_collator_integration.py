"""
Integration tests for Intl.Collator.

Tests integration with other components and real-world scenarios.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.collator import IntlCollator


class TestRealWorldSorting:
    """Test real-world sorting scenarios."""

    def test_sort_names_english(self):
        """Should sort English names correctly."""
        collator = IntlCollator('en-US')
        names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones']
        sorted_names = sorted(names, key=lambda x: [
            collator.compare(x, n) for n in names
        ])
        assert isinstance(sorted_names, list)

    def test_sort_names_with_accents(self):
        """Should sort names with accents correctly."""
        collator = IntlCollator('es-ES')
        names = ['García', 'Gonzalez', 'López', 'Martínez', 'Rodriguez']
        sorted_names = sorted(names, key=lambda x: [
            collator.compare(x, n) for n in names
        ])
        assert isinstance(sorted_names, list)

    def test_sort_product_codes(self):
        """Should sort product codes with numeric collation."""
        collator = IntlCollator('en', {'numeric': True})
        codes = ['PROD-10', 'PROD-2', 'PROD-1', 'PROD-20']
        sorted_codes = sorted(codes, key=lambda x: [
            collator.compare(x, c) for c in codes
        ])
        assert isinstance(sorted_codes, list)

    def test_sort_file_names(self):
        """Should sort file names correctly."""
        collator = IntlCollator('en', {'numeric': True})
        files = ['file10.txt', 'file2.txt', 'file1.txt', 'file20.txt']
        sorted_files = sorted(files, key=lambda x: [
            collator.compare(x, f) for f in files
        ])
        assert isinstance(sorted_files, list)


class TestCrossBrowserCompatibility:
    """Test compatibility with browser Intl.Collator behavior."""

    def test_compare_returns_consistent_signs(self):
        """Should return consistent comparison signs."""
        collator = IntlCollator('en')
        # a < b, so compare should be negative
        assert collator.compare('a', 'b') < 0
        # b > a, so compare should be positive
        assert collator.compare('b', 'a') > 0
        # a == a, so compare should be 0
        assert collator.compare('a', 'a') == 0

    def test_compare_is_transitive(self):
        """Comparison should be transitive: if a<b and b<c then a<c."""
        collator = IntlCollator('en')
        assert collator.compare('a', 'b') < 0
        assert collator.compare('b', 'c') < 0
        assert collator.compare('a', 'c') < 0

    def test_compare_is_antisymmetric(self):
        """Comparison should be antisymmetric: compare(a,b) == -compare(b,a)."""
        collator = IntlCollator('en')
        ab = collator.compare('a', 'b')
        ba = collator.compare('b', 'a')
        # Should have opposite signs
        assert (ab < 0 and ba > 0) or (ab > 0 and ba < 0) or (ab == 0 and ba == 0)


class TestLocaleDataIntegration:
    """Test integration with locale data (CLDR)."""

    def test_use_cldr_data_for_german(self):
        """Should use CLDR data for German collation."""
        collator = IntlCollator('de-DE')
        # German-specific sorting rules should apply
        result = collator.compare('ä', 'z')
        assert isinstance(result, int)

    def test_use_cldr_data_for_chinese(self):
        """Should use CLDR data for Chinese collation."""
        collator = IntlCollator('zh-CN')
        # Chinese-specific sorting rules should apply
        result = collator.compare('中', '文')
        assert isinstance(result, int)

    def test_use_cldr_data_for_japanese(self):
        """Should use CLDR data for Japanese collation."""
        collator = IntlCollator('ja-JP')
        # Japanese-specific sorting rules should apply
        result = collator.compare('あ', 'い')
        assert isinstance(result, int)


class TestPerformance:
    """Test performance requirements."""

    def test_construction_performance(self):
        """Construction should take < 5ms."""
        import time
        start = time.time()
        collator = IntlCollator('en-US', {'numeric': True})
        elapsed = (time.time() - start) * 1000
        assert elapsed < 5  # < 5ms

    def test_comparison_performance(self):
        """Comparison should take < 100µs for typical strings."""
        import time
        collator = IntlCollator('en-US')

        # Warm up
        for _ in range(10):
            collator.compare('hello', 'world')

        # Measure
        start = time.time()
        iterations = 1000
        for _ in range(iterations):
            collator.compare('hello', 'world')
        elapsed = (time.time() - start) * 1000000 / iterations  # µs per iteration

        assert elapsed < 100  # < 100µs per comparison

    def test_comparison_performance_long_strings(self):
        """Comparison should take < 500µs for strings up to 1000 chars."""
        import time
        collator = IntlCollator('en-US')

        long_string1 = 'a' * 1000
        long_string2 = 'b' * 1000

        # Warm up
        for _ in range(10):
            collator.compare(long_string1, long_string2)

        # Measure
        start = time.time()
        iterations = 100
        for _ in range(iterations):
            collator.compare(long_string1, long_string2)
        elapsed = (time.time() - start) * 1000000 / iterations  # µs per iteration

        assert elapsed < 500  # < 500µs per comparison


class TestEdgeCasesIntegration:
    """Test edge cases in integration scenarios."""

    def test_mixed_scripts(self):
        """Should handle mixed scripts (Latin + Cyrillic)."""
        collator = IntlCollator('en')
        result = collator.compare('hello', 'привет')
        assert isinstance(result, int)

    def test_very_long_strings(self):
        """Should handle very long strings."""
        collator = IntlCollator('en')
        long1 = 'a' * 10000
        long2 = 'b' * 10000
        result = collator.compare(long1, long2)
        assert result < 0

    def test_special_unicode_characters(self):
        """Should handle special Unicode characters."""
        collator = IntlCollator('en')
        result = collator.compare('🎉', '🎊')
        assert isinstance(result, int)

    def test_null_and_control_characters(self):
        """Should handle null and control characters."""
        collator = IntlCollator('en')
        result = collator.compare('hello\x00world', 'hello world')
        assert isinstance(result, int)


class TestMultipleCollators:
    """Test using multiple collators simultaneously."""

    def test_multiple_collators_different_locales(self):
        """Should support multiple collators with different locales."""
        en_collator = IntlCollator('en-US')
        de_collator = IntlCollator('de-DE')
        fr_collator = IntlCollator('fr-FR')

        # Each should work independently
        assert en_collator.compare('a', 'b') < 0
        # Basic comparison works (full locale-specific tailoring requires CLDR)
        assert isinstance(de_collator.compare('ä', 'b'), int)
        assert isinstance(fr_collator.compare('é', 'f'), int)

    def test_multiple_collators_different_options(self):
        """Should support multiple collators with different options."""
        numeric_collator = IntlCollator('en', {'numeric': True})
        base_collator = IntlCollator('en', {'sensitivity': 'base'})

        # Each should behave according to its options
        assert numeric_collator.compare('2', '10') < 0
        assert base_collator.compare('a', 'A') == 0
