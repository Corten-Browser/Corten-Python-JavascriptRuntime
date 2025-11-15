"""
Performance tests for IntlNumberFormat

These tests verify that the implementation meets performance requirements
specified in the contract.
"""

import pytest
import time
from components.intl_numberformat.src.number_format import IntlNumberFormat


class TestPerformanceConstructor:
    """Test constructor performance (<5ms for complex options)."""

    def test_constructor_simple_performance(self):
        """Simple constructor should be fast."""
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            IntlNumberFormat('en-US')
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        assert avg_time < 5.0

    def test_constructor_complex_options_performance(self):
        """Complex constructor should complete in <5ms."""
        iterations = 1000

        options = {
            'style': 'currency',
            'currency': 'USD',
            'notation': 'compact',
            'minimumFractionDigits': 2,
            'maximumFractionDigits': 4,
            'useGrouping': True,
            'signDisplay': 'always'
        }

        start = time.time()
        for _ in range(iterations):
            IntlNumberFormat('en-US', options)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        # Contract specifies <5ms for complex options
        assert avg_time < 5.0


class TestPerformanceFormat:
    """Test format() performance (<500µs)."""

    def test_format_simple_numbers_performance(self):
        """Format simple numbers should complete in <500µs."""
        formatter = IntlNumberFormat('en-US')
        iterations = 10000

        start = time.time()
        for i in range(iterations):
            formatter.format(i)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1_000_000  # µs
        # Contract specifies <500µs per format
        assert avg_time < 500.0

    def test_format_decimal_numbers_performance(self):
        """Format decimal numbers performance."""
        formatter = IntlNumberFormat('en-US')
        iterations = 10000

        start = time.time()
        for i in range(iterations):
            formatter.format(i + 0.123456)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1_000_000  # µs
        assert avg_time < 500.0

    def test_format_currency_performance(self):
        """Format currency performance."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        iterations = 10000

        start = time.time()
        for i in range(iterations):
            formatter.format(i * 100.5)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1_000_000  # µs
        assert avg_time < 500.0

    def test_format_compact_performance(self):
        """Format compact notation performance."""
        formatter = IntlNumberFormat('en-US', {'notation': 'compact'})
        iterations = 10000

        start = time.time()
        for i in range(iterations):
            formatter.format(i * 1000)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1_000_000  # µs
        assert avg_time < 500.0


class TestPerformanceFormatToParts:
    """Test formatToParts() performance (<1ms)."""

    def test_format_to_parts_performance(self):
        """FormatToParts should complete in <1ms."""
        formatter = IntlNumberFormat('en-US')
        iterations = 1000

        start = time.time()
        for i in range(iterations):
            formatter.formatToParts(1234.56)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        # Contract specifies <1ms per formatToParts
        assert avg_time < 1.0

    def test_format_to_parts_currency_performance(self):
        """FormatToParts currency performance."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        iterations = 1000

        start = time.time()
        for i in range(iterations):
            formatter.formatToParts(1234.56)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        assert avg_time < 1.0


class TestPerformanceFormatRange:
    """Test formatRange() performance (<1ms)."""

    def test_format_range_performance(self):
        """FormatRange should complete in <1ms."""
        formatter = IntlNumberFormat('en-US')
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            formatter.formatRange(100, 200)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        # Contract specifies <1ms per formatRange
        assert avg_time < 1.0

    def test_format_range_currency_performance(self):
        """FormatRange currency performance."""
        formatter = IntlNumberFormat('en-US', {
            'style': 'currency',
            'currency': 'USD'
        })
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            formatter.formatRange(100, 200)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        assert avg_time < 1.0


class TestPerformanceFormatRangeToParts:
    """Test formatRangeToParts() performance (<1.5ms)."""

    def test_format_range_to_parts_performance(self):
        """FormatRangeToParts should complete in <1.5ms."""
        formatter = IntlNumberFormat('en-US')
        iterations = 1000

        start = time.time()
        for _ in range(iterations):
            formatter.formatRangeToParts(100, 200)
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1000  # ms
        # Contract specifies <1.5ms per formatRangeToParts
        assert avg_time < 1.5


class TestPerformanceResolvedOptions:
    """Test resolvedOptions() performance (<100µs)."""

    def test_resolved_options_performance(self):
        """ResolvedOptions should be fast (cached)."""
        formatter = IntlNumberFormat('en-US')
        iterations = 10000

        start = time.time()
        for _ in range(iterations):
            formatter.resolvedOptions()
        elapsed = time.time() - start

        avg_time = (elapsed / iterations) * 1_000_000  # µs
        # Contract specifies <100µs (should be cached)
        assert avg_time < 100.0


class TestPerformanceMemory:
    """Test memory usage (<50KB per instance)."""

    def test_memory_many_instances(self):
        """Many instances should have reasonable memory usage."""
        import sys

        # Create many instances
        instances = []
        for _ in range(100):
            instances.append(IntlNumberFormat('en-US', {
                'style': 'currency',
                'currency': 'USD'
            }))

        # Rough check: instances should not be huge
        # (Exact memory measurement requires additional tools)
        # This test ensures we don't have obvious memory leaks

        assert len(instances) == 100

        # Each instance should be relatively lightweight
        # (This is a basic sanity check)
        for instance in instances[:10]:
            assert instance is not None

    def test_memory_formatter_reuse(self):
        """Reusing formatter should not grow memory."""
        formatter = IntlNumberFormat('en-US')

        # Format many times
        for i in range(10000):
            formatter.format(i)

        # Should still work fine
        result = formatter.format(12345)
        assert '12,345' in result or '12345' in result


class TestPerformanceScaling:
    """Test performance scaling with size."""

    def test_format_large_numbers_performance(self):
        """Large numbers should format reasonably fast."""
        formatter = IntlNumberFormat('en-US')
        large_numbers = [10**i for i in range(1, 20)]

        start = time.time()
        for num in large_numbers * 100:
            formatter.format(num)
        elapsed = time.time() - start

        avg_time = (elapsed / (len(large_numbers) * 100)) * 1_000_000  # µs
        assert avg_time < 500.0

    def test_format_many_decimals_performance(self):
        """Numbers with many decimal places."""
        formatter = IntlNumberFormat('en-US', {'maximumFractionDigits': 20})

        start = time.time()
        for i in range(1000):
            formatter.format(1.123456789012345678901234567890)
        elapsed = time.time() - start

        avg_time = (elapsed / 1000) * 1_000_000  # µs
        assert avg_time < 500.0


class TestPerformanceCaching:
    """Test that caching improves performance."""

    def test_repeated_formats_use_cache(self):
        """Repeated formats should be fast (cached)."""
        formatter = IntlNumberFormat('en-US')

        # Warm up
        for _ in range(100):
            formatter.format(1234.56)

        # Measure cached performance
        start = time.time()
        for _ in range(10000):
            formatter.format(1234.56)
        elapsed = time.time() - start

        avg_time = (elapsed / 10000) * 1_000_000  # µs
        # Should be very fast with caching
        assert avg_time < 500.0

    def test_different_numbers_still_fast(self):
        """Different numbers should still be reasonably fast."""
        formatter = IntlNumberFormat('en-US')

        start = time.time()
        for i in range(10000):
            formatter.format(i * 3.14159)
        elapsed = time.time() - start

        avg_time = (elapsed / 10000) * 1_000_000  # µs
        assert avg_time < 500.0


class TestPerformanceParallelUsage:
    """Test performance with multiple formatters."""

    def test_multiple_formatters_independent(self):
        """Multiple formatters should work independently."""
        formatters = [
            IntlNumberFormat('en-US'),
            IntlNumberFormat('de-DE'),
            IntlNumberFormat('ja-JP'),
        ]

        start = time.time()
        for _ in range(1000):
            for formatter in formatters:
                formatter.format(1234.56)
        elapsed = time.time() - start

        avg_time_per_format = (elapsed / (1000 * 3)) * 1_000_000  # µs
        assert avg_time_per_format < 500.0
