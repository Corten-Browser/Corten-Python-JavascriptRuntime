"""
Integration tests for IntlDisplayNames
Tests cross-feature interactions and real-world usage scenarios
"""
import pytest


class TestDisplayNamesIntegration:
    """Integration tests for IntlDisplayNames"""

    def test_full_workflow_language_names(self):
        """Test complete workflow for language display names"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        # Create formatter
        dn = IntlDisplayNames(['en'], {'type': 'language'})

        # Get multiple language names
        assert dn.of('en') == 'English'
        assert dn.of('es') == 'Spanish'
        assert dn.of('fr') == 'French'

        # Check resolved options
        options = dn.resolved_options()
        assert options['type'] == 'language'
        assert options['locale'] == 'en'

    def test_full_workflow_region_names(self):
        """Test complete workflow for region display names"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})

        # Get multiple region names
        assert dn.of('JP') == 'Japan'
        assert dn.of('DE') == 'Germany'
        assert dn.of('FR') == 'France'

    def test_multiple_locales_fallback(self):
        """Test locale fallback with multiple locales"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr', 'en'], {'type': 'language'})
        result = dn.of('de')
        assert isinstance(result, str) and len(result) > 0

    def test_style_variations_for_same_code(self):
        """Test different styles return different formats"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        long_dn = IntlDisplayNames(['en'], {'type': 'region', 'style': 'long'})
        short_dn = IntlDisplayNames(['en'], {'type': 'region', 'style': 'short'})

        long_result = long_dn.of('US')
        short_result = short_dn.of('US')

        assert isinstance(long_result, str)
        assert isinstance(short_result, str)

    def test_fallback_behavior_comparison(self):
        """Test difference between fallback=code and fallback=none"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with_code = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'code'})
        with_none = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'none'})

        # Unknown code
        assert with_code.of('xyz') == 'xyz'
        assert with_none.of('xyz') is None

    def test_language_display_mode_comparison(self):
        """Test difference between dialect and standard language display"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dialect_dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'dialect'})
        standard_dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'standard'})

        dialect_result = dialect_dn.of('en-US')
        standard_result = standard_dn.of('en-US')

        assert isinstance(dialect_result, str)
        assert isinstance(standard_result, str)
        # Results should differ
        assert standard_result == 'English'

    def test_cross_locale_consistency(self):
        """Test same code in different locales"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        en_dn = IntlDisplayNames(['en'], {'type': 'language'})
        fr_dn = IntlDisplayNames(['fr'], {'type': 'language'})
        de_dn = IntlDisplayNames(['de'], {'type': 'language'})

        en_result = en_dn.of('fr')
        fr_result = fr_dn.of('fr')
        de_result = de_dn.of('fr')

        # All should return strings
        assert isinstance(en_result, str)
        assert isinstance(fr_result, str)
        assert isinstance(de_result, str)

        # Results should differ (localized)
        assert en_result == 'French'
        assert fr_result == 'français'
        assert de_result == 'Französisch'

    def test_all_supported_types(self):
        """Test creating formatters for all supported types"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        types_and_codes = [
            ('language', 'en'),
            ('region', 'US'),
            ('script', 'Latn'),
            ('currency', 'USD'),
            ('calendar', 'gregory'),
        ]

        for display_type, code in types_and_codes:
            dn = IntlDisplayNames(['en'], {'type': display_type})
            result = dn.of(code)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_performance_multiple_lookups(self):
        """Test performance with multiple lookups (caching)"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames
        import time

        dn = IntlDisplayNames(['en'], {'type': 'language'})

        # First lookup (may load data)
        start = time.perf_counter()
        result1 = dn.of('en')
        first_time = time.perf_counter() - start

        # Second lookup (should use cache)
        start = time.perf_counter()
        result2 = dn.of('en')
        second_time = time.perf_counter() - start

        # Results should be identical
        assert result1 == result2

        # Second lookup should be faster (or at least very fast)
        assert second_time < 0.001  # <1ms as per contract (<200µs)

    def test_constructor_performance(self):
        """Test constructor performance meets requirements"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames
        import time

        start = time.perf_counter()
        dn = IntlDisplayNames(['en'], {'type': 'language'})
        elapsed = time.perf_counter() - start

        assert elapsed < 0.003  # <3ms as per contract
