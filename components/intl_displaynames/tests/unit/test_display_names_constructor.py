"""
Unit tests for IntlDisplayNames constructor
FR-ES24-C-048: Intl.DisplayNames constructor validation
"""
import pytest


class TestDisplayNamesConstructor:
    """Test IntlDisplayNames constructor behavior"""

    def test_constructor_with_valid_language_type(self):
        """FR-ES24-C-048: Constructor with type='language' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn is not None

    def test_constructor_with_valid_region_type(self):
        """FR-ES24-C-048: Constructor with type='region' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        assert dn is not None

    def test_constructor_with_valid_script_type(self):
        """FR-ES24-C-048: Constructor with type='script' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        assert dn is not None

    def test_constructor_with_valid_currency_type(self):
        """FR-ES24-C-048: Constructor with type='currency' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        assert dn is not None

    def test_constructor_with_valid_calendar_type(self):
        """FR-ES24-C-048: Constructor with type='calendar' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'calendar'})
        assert dn is not None

    def test_constructor_with_missing_type_throws_type_error(self):
        """FR-ES24-C-048: Missing type option should throw TypeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(TypeError, match="type.*required"):
            IntlDisplayNames(['en'], {})

    def test_constructor_with_invalid_type_throws_range_error(self):
        """FR-ES24-C-048: Invalid type value should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(ValueError, match="Invalid.*type"):
            IntlDisplayNames(['en'], {'type': 'invalid'})

    def test_constructor_with_invalid_locale_throws_range_error(self):
        """FR-ES24-C-048: Invalid locale should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(ValueError, match="Invalid locale"):
            IntlDisplayNames(['invalid-locale-!!!'], {'type': 'language'})

    def test_constructor_with_style_long(self):
        """FR-ES24-C-048: Constructor with style='long' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'long'})
        assert dn is not None

    def test_constructor_with_style_short(self):
        """FR-ES24-C-048: Constructor with style='short' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'short'})
        assert dn is not None

    def test_constructor_with_style_narrow(self):
        """FR-ES24-C-048: Constructor with style='narrow' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'narrow'})
        assert dn is not None

    def test_constructor_with_invalid_style_throws_range_error(self):
        """FR-ES24-C-048: Invalid style value should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(ValueError, match="Invalid.*style"):
            IntlDisplayNames(['en'], {'type': 'language', 'style': 'invalid'})

    def test_constructor_with_fallback_code(self):
        """FR-ES24-C-048: Constructor with fallback='code' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'code'})
        assert dn is not None

    def test_constructor_with_fallback_none(self):
        """FR-ES24-C-048: Constructor with fallback='none' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'none'})
        assert dn is not None

    def test_constructor_with_invalid_fallback_throws_range_error(self):
        """FR-ES24-C-048: Invalid fallback value should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(ValueError, match="Invalid.*fallback"):
            IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'invalid'})

    def test_constructor_with_language_display_dialect(self):
        """FR-ES24-C-048: Constructor with languageDisplay='dialect' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'dialect'})
        assert dn is not None

    def test_constructor_with_language_display_standard(self):
        """FR-ES24-C-048: Constructor with languageDisplay='standard' should succeed"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'standard'})
        assert dn is not None

    def test_constructor_with_invalid_language_display_throws_range_error(self):
        """FR-ES24-C-048: Invalid languageDisplay value should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        with pytest.raises(ValueError, match="Invalid.*languageDisplay"):
            IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'invalid'})

    def test_constructor_with_locale_array(self):
        """FR-ES24-C-048: Constructor should accept array of locales"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en', 'fr', 'de'], {'type': 'language'})
        assert dn is not None

    def test_constructor_with_single_locale_string(self):
        """FR-ES24-C-048: Constructor should accept single locale string"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames('en', {'type': 'language'})
        assert dn is not None

    def test_constructor_default_style_is_long(self):
        """FR-ES24-C-048: Default style should be 'long'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert options['style'] == 'long'

    def test_constructor_default_fallback_is_code(self):
        """FR-ES24-C-048: Default fallback should be 'code'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert options['fallback'] == 'code'

    def test_constructor_default_language_display_is_dialect(self):
        """FR-ES24-C-048: Default languageDisplay should be 'dialect'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        options = dn.resolved_options()
        assert options.get('languageDisplay') == 'dialect'
