"""
Unit tests for language display names
FR-ES24-C-050: Language display names (ISO 639)
"""
import pytest


class TestLanguageDisplayNames:
    """Test language code to display name conversion"""

    def test_language_en_to_english(self):
        """FR-ES24-C-050: 'en' should return 'English'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('en') == 'English'

    def test_language_es_to_spanish(self):
        """FR-ES24-C-050: 'es' should return 'Spanish'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('es') == 'Spanish'

    def test_language_fr_to_french(self):
        """FR-ES24-C-050: 'fr' should return 'French'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('fr') == 'French'

    def test_language_de_to_german(self):
        """FR-ES24-C-050: 'de' should return 'German'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('de') == 'German'

    def test_language_zh_to_chinese(self):
        """FR-ES24-C-050: 'zh' should return 'Chinese'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('zh') == 'Chinese'

    def test_language_ja_to_japanese(self):
        """FR-ES24-C-050: 'ja' should return 'Japanese'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        assert dn.of('ja') == 'Japanese'

    def test_language_localized_in_french(self):
        """FR-ES24-C-050: Language names should be localized to target locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr'], {'type': 'language'})
        result = dn.of('fr')
        assert result == 'français'

    def test_language_localized_in_german(self):
        """FR-ES24-C-050: Language names should be localized to German"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['de'], {'type': 'language'})
        result = dn.of('fr')
        assert result == 'Französisch'

    def test_language_display_dialect_mode(self):
        """FR-ES24-C-050: languageDisplay='dialect' should distinguish dialects"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'dialect'})
        result = dn.of('en-US')
        assert 'American' in result or 'US' in result

    def test_language_display_standard_mode(self):
        """FR-ES24-C-050: languageDisplay='standard' should use standard names"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'languageDisplay': 'standard'})
        result = dn.of('en-US')
        assert result == 'English'

    def test_language_three_letter_code(self):
        """FR-ES24-C-050: Should support 3-letter ISO 639-2 codes"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        result = dn.of('eng')
        assert result == 'English'

    def test_language_with_style_long(self):
        """FR-ES24-C-050: style='long' should return full language name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'long'})
        result = dn.of('en')
        assert result == 'English'

    def test_language_with_style_short(self):
        """FR-ES24-C-050: style='short' should return abbreviated name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'short'})
        result = dn.of('en')
        assert isinstance(result, str) and len(result) > 0

    def test_language_with_style_narrow(self):
        """FR-ES24-C-050: style='narrow' should return compact name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language', 'style': 'narrow'})
        result = dn.of('en')
        assert isinstance(result, str) and len(result) > 0

    def test_language_code_validation_rejects_invalid(self):
        """FR-ES24-C-050: Should reject invalid language codes"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'language'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('invalid123')
