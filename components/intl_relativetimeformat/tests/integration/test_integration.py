"""
Integration tests for RelativeTimeFormat.

Tests real-world usage scenarios and integration with other components.
"""

import pytest
from src.relative_time_format import RelativeTimeFormat, RangeError, TypeError


class TestRelativeTimeFormatIntegration:
    """Integration tests for RelativeTimeFormat."""

    def test_real_world_scenario_timeline(self):
        """Test realistic timeline display scenario."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto'})

        # User activity timeline
        activities = [
            (-2, 'minute', 'Posted a comment'),
            (-30, 'minute', 'Liked a post'),
            (-2, 'hour', 'Uploaded a photo'),
            (-1, 'day', 'Created account')
        ]

        for value, unit, action in activities:
            time_str = rtf.format(value, unit)
            assert time_str is not None
            assert 'ago' in time_str or time_str in ['yesterday', 'today', 'tomorrow']

    def test_real_world_scenario_scheduling(self):
        """Test future event scheduling scenario."""
        rtf = RelativeTimeFormat('en-US', {'numeric': 'auto', 'style': 'long'})

        # Upcoming events
        events = [
            (1, 'hour', 'Team meeting'),
            (3, 'hour', 'Code review'),
            (1, 'day', 'Project deadline'),
            (1, 'week', 'Sprint planning')
        ]

        for value, unit, event in events:
            time_str = rtf.format(value, unit)
            assert time_str is not None
            assert 'in' in time_str.lower() or time_str in ['tomorrow', 'next week']

    def test_multilingual_support(self):
        """Test same data formatted in multiple locales."""
        locales = ['en-US', 'es-ES', 'fr-FR', 'de-DE']

        for locale in locales:
            rtf = RelativeTimeFormat(locale)
            result = rtf.format(-2, 'day')
            assert result is not None
            assert len(result) > 0

    def test_format_and_formatToParts_consistency(self):
        """Test that format and formatToParts are consistent."""
        rtf = RelativeTimeFormat('en-US')

        test_cases = [
            (1, 'second'),
            (-5, 'minute'),
            (24, 'hour'),
            (-7, 'day'),
            (2, 'week'),
            (-3, 'month'),
            (1, 'year')
        ]

        for value, unit in test_cases:
            formatted = rtf.format(value, unit)
            parts = rtf.formatToParts(value, unit)
            reconstructed = ''.join(p['value'] for p in parts)

            assert formatted == reconstructed, \
                f"Mismatch for {value} {unit}: '{formatted}' != '{reconstructed}'"

    def test_performance_batch_formatting(self):
        """Test performance with batch formatting operations."""
        import time

        rtf = RelativeTimeFormat('en-US')

        # Format 1000 different values
        start = time.perf_counter()
        for i in range(1, 1001):
            rtf.format(i, 'day')
        end = time.perf_counter()

        total_time = end - start
        avg_time = total_time / 1000

        # Should average < 500µs per call
        assert avg_time < 0.0005, f"format() too slow: {avg_time*1e6:.2f}µs avg"

    def test_instance_isolation(self):
        """Test that multiple instances don't interfere with each other."""
        rtf1 = RelativeTimeFormat('en-US', {'style': 'long', 'numeric': 'always'})
        rtf2 = RelativeTimeFormat('en-US', {'style': 'short', 'numeric': 'auto'})
        rtf3 = RelativeTimeFormat('es-ES', {'style': 'narrow'})

        # Each should maintain its own options
        assert rtf1.resolvedOptions()['style'] == 'long'
        assert rtf1.resolvedOptions()['numeric'] == 'always'

        assert rtf2.resolvedOptions()['style'] == 'short'
        assert rtf2.resolvedOptions()['numeric'] == 'auto'

        assert rtf3.resolvedOptions()['locale'] == 'es-ES'
        assert rtf3.resolvedOptions()['style'] == 'narrow'

    def test_edge_cases_comprehensive(self):
        """Test various edge cases."""
        rtf = RelativeTimeFormat('en-US')

        # Very large numbers
        assert rtf.format(999999, 'year') is not None

        # Very small (negative large)
        assert rtf.format(-999999, 'year') is not None

        # Zero
        assert rtf.format(0, 'second') is not None

        # Decimal values
        assert rtf.format(1.5, 'day') is not None
        assert rtf.format(-2.7, 'hour') is not None


# TypeError and RangeError imported from src
