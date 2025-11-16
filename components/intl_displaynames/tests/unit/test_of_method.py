"""
Unit tests for IntlDisplayNames.of() method
FR-ES24-C-049: of() method validation and fallback behavior
"""
import pytest


class TestOfMethod:
    """Test IntlDisplayNames.of() method"""

    def test_of_returns_string_for_valid_code(self):
        """FR-ES24-C-049: of() should return string for valid code"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        result = dn.of('en')
        assert isinstance(result, str)
        assert len(result) > 0

    def test_of_with_fallback_code_returns_code_for_unknown(self):
        """FR-ES24-C-049: of() with fallback='code' returns code for unknown"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'code'})
        result = dn.of('xyz')
        assert result == 'xyz'

    def test_of_with_fallback_none_returns_undefined_for_unknown(self):
        """FR-ES24-C-049: of() with fallback='none' returns None for unknown"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'fallback': 'none'})
        result = dn.of('xyz')
        assert result is None

    def test_of_validates_code_format_for_language(self):
        """FR-ES24-C-049: of() should validate language code format"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        # Invalid language codes should throw RangeError
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('1234')

    def test_of_validates_code_format_for_region(self):
        """FR-ES24-C-049: of() should validate region code format"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        # Invalid region codes should throw RangeError
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('123')

    def test_of_validates_code_format_for_script(self):
        """FR-ES24-C-049: of() should validate script code format"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        # Invalid script codes should throw RangeError
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('lat')  # Must be 4 letters titlecase

    def test_of_validates_code_format_for_currency(self):
        """FR-ES24-C-049: of() should validate currency code format"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        # Invalid currency codes should throw RangeError
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('us')  # Must be 3 uppercase letters

    def test_of_with_invalid_argument_type(self):
        """FR-ES24-C-049: of() with invalid argument should throw TypeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        with pytest.raises(TypeError):
            dn.of(123)  # Must be string

    def test_of_with_none_argument(self):
        """FR-ES24-C-049: of() with None should throw TypeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        with pytest.raises(TypeError):
            dn.of(None)

    def test_of_with_empty_string(self):
        """FR-ES24-C-049: of() with empty string should throw RangeError"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('')
