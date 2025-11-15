"""
Unit tests for script display names
FR-ES24-C-052: Script display names (ISO 15924)
"""
import pytest


class TestScriptDisplayNames:
    """Test script code to display name conversion"""

    def test_script_latn_to_latin(self):
        """FR-ES24-C-052: 'Latn' should return 'Latin'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        assert dn.of('Latn') == 'Latin'

    def test_script_cyrl_to_cyrillic(self):
        """FR-ES24-C-052: 'Cyrl' should return 'Cyrillic'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        assert dn.of('Cyrl') == 'Cyrillic'

    def test_script_arab_to_arabic(self):
        """FR-ES24-C-052: 'Arab' should return 'Arabic'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        assert dn.of('Arab') == 'Arabic'

    def test_script_hans_to_simplified_chinese(self):
        """FR-ES24-C-052: 'Hans' should return 'Simplified Han'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        result = dn.of('Hans')
        assert 'Han' in result or 'Simplified' in result

    def test_script_hant_to_traditional_chinese(self):
        """FR-ES24-C-052: 'Hant' should return 'Traditional Han'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        result = dn.of('Hant')
        assert 'Han' in result or 'Traditional' in result

    def test_script_hebr_to_hebrew(self):
        """FR-ES24-C-052: 'Hebr' should return 'Hebrew'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        assert dn.of('Hebr') == 'Hebrew'

    def test_script_localized_in_french(self):
        """FR-ES24-C-052: Script names should be localized to target locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr'], {'type': 'script'})
        result = dn.of('Latn')
        assert result == 'latin'

    def test_script_localized_in_german(self):
        """FR-ES24-C-052: Script names should be localized to German"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['de'], {'type': 'script'})
        result = dn.of('Latn')
        assert result == 'Lateinisch'

    def test_script_with_style_long(self):
        """FR-ES24-C-052: style='long' should return full script name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script', 'style': 'long'})
        result = dn.of('Latn')
        assert result == 'Latin'

    def test_script_with_style_short(self):
        """FR-ES24-C-052: style='short' should return abbreviated name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script', 'style': 'short'})
        result = dn.of('Latn')
        assert isinstance(result, str) and len(result) > 0

    def test_script_with_style_narrow(self):
        """FR-ES24-C-052: style='narrow' should return compact name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script', 'style': 'narrow'})
        result = dn.of('Latn')
        assert isinstance(result, str) and len(result) > 0

    def test_script_code_validation_requires_four_letters(self):
        """FR-ES24-C-052: Script code must be exactly 4 letters"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('Lat')  # 3 letters not allowed

    def test_script_code_validation_requires_titlecase(self):
        """FR-ES24-C-052: Script code must be titlecase (first letter uppercase)"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('LATN')  # all uppercase not allowed

    def test_script_code_validation_rejects_lowercase(self):
        """FR-ES24-C-052: Script code cannot be all lowercase"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('latn')  # all lowercase not allowed

    def test_script_code_validation_rejects_numbers(self):
        """FR-ES24-C-052: Script code cannot contain numbers"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'script'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('Lat1')
