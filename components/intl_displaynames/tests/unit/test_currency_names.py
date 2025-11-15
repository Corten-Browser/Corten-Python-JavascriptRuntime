"""
Unit tests for currency display names
FR-ES24-C-053: Currency display names (ISO 4217)
"""
import pytest


class TestCurrencyDisplayNames:
    """Test currency code to display name conversion"""

    def test_currency_usd_to_us_dollar(self):
        """FR-ES24-C-053: 'USD' should return 'US Dollar'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        result = dn.of('USD')
        assert 'Dollar' in result and ('US' in result or 'United States' in result)

    def test_currency_eur_to_euro(self):
        """FR-ES24-C-053: 'EUR' should return 'Euro'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        assert dn.of('EUR') == 'Euro'

    def test_currency_jpy_to_japanese_yen(self):
        """FR-ES24-C-053: 'JPY' should return 'Japanese Yen'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        result = dn.of('JPY')
        assert 'Yen' in result and 'Japan' in result

    def test_currency_gbp_to_british_pound(self):
        """FR-ES24-C-053: 'GBP' should return 'British Pound'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        result = dn.of('GBP')
        assert 'Pound' in result and ('British' in result or 'Sterling' in result)

    def test_currency_chf_to_swiss_franc(self):
        """FR-ES24-C-053: 'CHF' should return 'Swiss Franc'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        result = dn.of('CHF')
        assert 'Franc' in result and 'Swiss' in result

    def test_currency_cny_to_chinese_yuan(self):
        """FR-ES24-C-053: 'CNY' should return 'Chinese Yuan'"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        result = dn.of('CNY')
        assert ('Yuan' in result or 'Renminbi' in result) and 'Chin' in result

    def test_currency_localized_in_french(self):
        """FR-ES24-C-053: Currency names should be localized to target locale"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['fr'], {'type': 'currency'})
        result = dn.of('USD')
        assert 'dollar' in result.lower() and ('états-unis' in result.lower() or 'américain' in result.lower())

    def test_currency_localized_in_german(self):
        """FR-ES24-C-053: Currency names should be localized to German"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['de'], {'type': 'currency'})
        result = dn.of('EUR')
        assert result == 'Euro'

    def test_currency_with_style_long(self):
        """FR-ES24-C-053: style='long' should return full currency name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency', 'style': 'long'})
        result = dn.of('USD')
        assert isinstance(result, str) and len(result) > 3

    def test_currency_with_style_short(self):
        """FR-ES24-C-053: style='short' should return abbreviated name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency', 'style': 'short'})
        result = dn.of('USD')
        assert isinstance(result, str) and len(result) > 0

    def test_currency_with_style_narrow(self):
        """FR-ES24-C-053: style='narrow' should return compact name"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency', 'style': 'narrow'})
        result = dn.of('USD')
        assert isinstance(result, str) and len(result) > 0

    def test_currency_code_validation_requires_three_letters(self):
        """FR-ES24-C-053: Currency code must be exactly 3 letters"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('US')  # 2 letters not allowed

    def test_currency_code_validation_requires_uppercase(self):
        """FR-ES24-C-053: Currency code must be uppercase"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('usd')  # lowercase not allowed

    def test_currency_code_validation_rejects_numbers(self):
        """FR-ES24-C-053: Currency code cannot contain numbers"""
        from components.intl_displaynames.src.display_names import IntlDisplayNames

        dn = IntlDisplayNames(['en'], {'type': 'currency'})
        with pytest.raises(ValueError, match="Invalid.*code"):
            dn.of('US1')
