"""
Unit tests for IntlDisplayNames.resolvedOptions()
FR-ES24-C-054: resolvedOptions() method
"""
import pytest


class TestResolvedOptions:
    """Test IntlDisplayNames.resolvedOptions() method"""

    def test_resolved_options_returns_dict(self):
        """FR-ES24-C-054: resolvedOptions() should return a dictionary"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert isinstance(options, dict)

    def test_resolved_options_contains_locale(self):
        """FR-ES24-C-054: resolvedOptions() should contain locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert 'locale' in options
        assert options['locale'] == 'en'

    def test_resolved_options_contains_type(self):
        """FR-ES24-C-054: resolvedOptions() should contain type"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        options = dn.resolved_options()
        assert 'type' in options
        assert options['type'] == 'region'

    def test_resolved_options_contains_style(self):
        """FR-ES24-C-054: resolvedOptions() should contain style"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'short'})
        options = dn.resolved_options()
        assert 'style' in options
        assert options['style'] == 'short'

    def test_resolved_options_contains_fallback(self):
        """FR-ES24-C-054: resolvedOptions() should contain fallback"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'none'})
        options = dn.resolved_options()
        assert 'fallback' in options
        assert options['fallback'] == 'none'

    def test_resolved_options_contains_language_display(self):
        """FR-ES24-C-054: resolvedOptions() should contain languageDisplay for type=language"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'standard'})
        options = dn.resolved_options()
        assert 'languageDisplay' in options
        assert options['languageDisplay'] == 'standard'

    def test_resolved_options_no_language_display_for_region(self):
        """FR-ES24-C-054: languageDisplay should only be present for type=language"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        options = dn.resolved_options()
        # languageDisplay should not be present or should be None for non-language types
        assert options.get('languageDisplay') is None

    def test_resolved_options_with_locale_fallback(self):
        """FR-ES24-C-054: Should resolve to best matching locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en-US'], {'type': 'language'})
        options = dn.resolved_options()
        assert 'locale' in options
        # Should resolve to en or en-US
        assert options['locale'].startswith('en')

    def test_resolved_options_with_multiple_locales(self):
        """FR-ES24-C-054: Should resolve first matching locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr', 'en'], {'type': 'language'})
        options = dn.resolved_options()
        assert 'locale' in options
        # Should resolve to fr or en based on availability
        assert options['locale'] in ['fr', 'en']

    def test_resolved_options_default_values(self):
        """FR-ES24-C-054: Should have correct default values"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert options['style'] == 'long'
        assert options['fallback'] == 'code'
        assert options['languageDisplay'] == 'dialect'

    def test_resolved_options_is_immutable(self):
        """FR-ES24-C-054: Modifying returned options should not affect instance"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options1 = dn.resolved_options()
        options1['type'] = 'region'  # Try to modify
        options2 = dn.resolved_options()
        assert options2['type'] == 'language'  # Should not be affected
