"""
Unit tests for region display names
FR-ES24-C-051: Region display names (ISO 3166-1)
"""
import pytest


class TestRegionDisplayNames:
    """Test region code to display name conversion"""

    def test_region_us_to_united_states(self):
        """FR-ES24-C-051: 'US' should return 'United States'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        result = dn.of('US')
        assert 'United States' in result or 'USA' in result

    def test_region_gb_to_united_kingdom(self):
        """FR-ES24-C-051: 'GB' should return 'United Kingdom'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        result = dn.of('GB')
        assert 'United Kingdom' in result or 'Britain' in result

    def test_region_jp_to_japan(self):
        """FR-ES24-C-051: 'JP' should return 'Japan'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        assert dn.of('JP') == 'Japan'

    def test_region_de_to_germany(self):
        """FR-ES24-C-051: 'DE' should return 'Germany'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        assert dn.of('DE') == 'Germany'

    def test_region_fr_to_france(self):
        """FR-ES24-C-051: 'FR' should return 'France'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        assert dn.of('FR') == 'France'

    def test_region_cn_to_china(self):
        """FR-ES24-C-051: 'CN' should return 'China'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        assert dn.of('CN') == 'China'

    def test_region_localized_in_french(self):
        """FR-ES24-C-051: Region names should be localized to target locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr'], {'type': 'region'})
        result = dn.of('US')
        assert 'États-Unis' in result or 'Etats-Unis' in result

    def test_region_localized_in_german(self):
        """FR-ES24-C-051: Region names should be localized to German"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['de'], {'type': 'region'})
        result = dn.of('FR')
        assert result == 'Frankreich'

    def test_region_with_style_long(self):
        """FR-ES24-C-051: style='long' should return full region name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region', 'style': 'long'})
        result = dn.of('US')
        assert isinstance(result, str) and len(result) > 2

    def test_region_with_style_short(self):
        """FR-ES24-C-051: style='short' should return abbreviated name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region', 'style': 'short'})
        result = dn.of('US')
        assert isinstance(result, str) and len(result) > 0

    def test_region_with_style_narrow(self):
        """FR-ES24-C-051: style='narrow' should return compact name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region', 'style': 'narrow'})
        result = dn.of('US')
        assert isinstance(result, str) and len(result) > 0

    def test_region_code_validation_requires_two_letters(self):
        """FR-ES24-C-051: Region code must be 2 uppercase letters"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('USA')  # 3 letters not allowed

    def test_region_code_validation_requires_uppercase(self):
        """FR-ES24-C-051: Region code must be uppercase"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('us')  # lowercase not allowed

    def test_region_code_validation_rejects_numbers(self):
        """FR-ES24-C-051: Region code cannot contain numbers"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'region'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('U2')
