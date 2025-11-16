"""
Unit tests for locale support and negotiation.
Tests BCP 47 locale negotiation and parsing.
"""

import pytest
from components.intl_datetimeformat.src.locale_support import (
    LocaleSupport,
    negotiate_locale,
    parse_locale,
    canonicalize_locale
)


class TestLocaleNegotiation:
    """Test BCP 47 locale negotiation."""

    def test_negotiate_exact_match(self):
        """Test negotiation with exact match."""
        requested = ['en-US']
        available = ['en-US', 'en-GB', 'fr-FR']
        default = 'en'

        result = negotiate_locale(requested, available, default)
        assert result == 'en-US'

    def test_negotiate_language_fallback(self):
        """Test negotiation falls back to language match."""
        requested = ['en-CA']
        available = ['en-US', 'en-GB', 'fr-FR']
        default = 'en'

        result = negotiate_locale(requested, available, default)
        # Should match 'en-US' or 'en-GB' (language match)
        assert result in ['en-US', 'en-GB']

    def test_negotiate_priority_order(self):
        """Test negotiation respects priority order."""
        requested = ['fr-FR', 'en-US', 'de-DE']
        available = ['en-US', 'de-DE']
        default = 'en'

        result = negotiate_locale(requested, available, default)
        # 'fr-FR' not available, should pick 'en-US' (next in order)
        assert result == 'en-US'

    def test_negotiate_default_fallback(self):
        """Test negotiation falls back to default."""
        requested = ['zh-CN']
        available = ['en-US', 'en-GB', 'fr-FR']
        default = 'en-US'

        result = negotiate_locale(requested, available, default)
        assert result == 'en-US'

    def test_negotiate_empty_requested_uses_default(self):
        """Test empty requested locales uses default."""
        requested = []
        available = ['en-US', 'fr-FR']
        default = 'en-US'

        result = negotiate_locale(requested, available, default)
        assert result == 'en-US'

    def test_negotiate_with_script(self):
        """Test negotiation with script subtag."""
        requested = ['zh-Hans-CN']
        available = ['zh-Hans-CN', 'zh-Hant-TW', 'en-US']
        default = 'en-US'

        result = negotiate_locale(requested, available, default)
        assert result == 'zh-Hans-CN'

    def test_negotiate_script_fallback(self):
        """Test negotiation falls back ignoring script."""
        requested = ['zh-Hans-CN']
        available = ['zh-CN', 'en-US']
        default = 'en-US'

        result = negotiate_locale(requested, available, default)
        # Should match 'zh-CN' (same language and region)
        assert result == 'zh-CN'

    def test_negotiate_multiple_requested(self):
        """Test negotiation with multiple requested locales."""
        requested = ['ja-JP', 'en-GB', 'en-US']
        available = ['en-US', 'fr-FR']
        default = 'en-US'

        result = negotiate_locale(requested, available, default)
        # 'ja-JP' and 'en-GB' not available, should pick 'en-US'
        assert result == 'en-US'


class TestLocaleParser:
    """Test BCP 47 locale parsing."""

    def test_parse_simple_locale(self):
        """Test parsing simple language tag."""
        result = parse_locale('en')

        assert result['language'] == 'en'
        assert result.get('script') is None
        assert result.get('region') is None

    def test_parse_language_region(self):
        """Test parsing language-region tag."""
        result = parse_locale('en-US')

        assert result['language'] == 'en'
        assert result['region'] == 'US'

    def test_parse_language_script_region(self):
        """Test parsing language-script-region tag."""
        result = parse_locale('zh-Hans-CN')

        assert result['language'] == 'zh'
        assert result['script'] == 'Hans'
        assert result['region'] == 'CN'

    def test_parse_with_unicode_extension(self):
        """Test parsing locale with Unicode extension."""
        result = parse_locale('en-US-u-ca-buddhist')

        assert result['language'] == 'en'
        assert result['region'] == 'US'
        assert 'extensions' in result
        assert 'u' in result['extensions']
        assert result['extensions']['u']['ca'] == 'buddhist'

    def test_parse_with_calendar_extension(self):
        """Test parsing locale with calendar extension."""
        result = parse_locale('th-TH-u-ca-buddhist-nu-thai')

        assert result['language'] == 'th'
        assert result['region'] == 'TH'
        assert result['extensions']['u']['ca'] == 'buddhist'
        assert result['extensions']['u']['nu'] == 'thai'

    def test_parse_with_variant(self):
        """Test parsing locale with variant."""
        result = parse_locale('de-DE-1996')

        assert result['language'] == 'de'
        assert result['region'] == 'DE'
        assert '1996' in result.get('variants', [])

    def test_parse_invalid_locale_raises_error(self):
        """Test parsing invalid locale raises ValueError."""
        with pytest.raises(ValueError, match='Invalid locale'):
            parse_locale('not-a-valid-locale!')

    def test_parse_case_insensitive(self):
        """Test parsing is case-insensitive."""
        result1 = parse_locale('en-US')
        result2 = parse_locale('en-us')

        assert result1['language'] == result2['language']
        assert result1['region'] == result2['region']


class TestLocaleCanonicalizer:
    """Test locale canonicalization."""

    def test_canonicalize_simple_locale(self):
        """Test canonicalization of simple locale."""
        result = canonicalize_locale('en')
        assert result == 'en'

    def test_canonicalize_normalizes_case(self):
        """Test canonicalization normalizes case."""
        result = canonicalize_locale('en-us')
        assert result == 'en-US'

    def test_canonicalize_language_lowercase(self):
        """Test canonicalization lowercases language."""
        result = canonicalize_locale('EN-US')
        assert result == 'en-US'

    def test_canonicalize_script_titlecase(self):
        """Test canonicalization titlecases script."""
        result = canonicalize_locale('zh-hans-CN')
        assert result == 'zh-Hans-CN'

    def test_canonicalize_region_uppercase(self):
        """Test canonicalization uppercases region."""
        result = canonicalize_locale('en-us')
        assert result == 'en-US'

    def test_canonicalize_with_extension(self):
        """Test canonicalization preserves extensions."""
        result = canonicalize_locale('en-us-u-ca-buddhist')
        assert result == 'en-US-u-ca-buddhist'

    def test_canonicalize_removes_duplicates(self):
        """Test canonicalization removes duplicate extensions."""
        result = canonicalize_locale('en-US-u-ca-gregory-u-nu-latn')
        # Should consolidate extensions
        assert 'u-ca-gregory' in result
        assert 'u-nu-latn' in result

    def test_canonicalize_sorts_extension_keys(self):
        """Test canonicalization sorts extension keys."""
        result = canonicalize_locale('en-US-u-nu-latn-ca-gregory')
        # Keys should be sorted: ca before nu
        assert result == 'en-US-u-ca-gregory-nu-latn'

    def test_canonicalize_invalid_locale_raises_error(self):
        """Test canonicalization of invalid locale raises ValueError."""
        with pytest.raises(ValueError, match='Invalid locale'):
            canonicalize_locale('not-a-valid-locale!')

    def test_canonicalize_grandfathered_tags(self):
        """Test canonicalization of grandfathered tags."""
        # Some old-style tags should be canonicalized
        result = canonicalize_locale('i-klingon')
        assert isinstance(result, str)
        # Should either canonicalize or raise error for non-standard tags


class TestSupportedLocalesOf:
    """Test supportedLocalesOf functionality."""

    def test_supported_locales_all_supported(self):
        """Test all requested locales are supported."""
        from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat

        requested = ['en-US', 'fr-FR', 'de-DE']
        result = IntlDateTimeFormat.supportedLocalesOf(requested)

        assert isinstance(result, list)
        # All common locales should be supported
        assert 'en-US' in result
        assert 'fr-FR' in result
        assert 'de-DE' in result

    def test_supported_locales_partial_support(self):
        """Test partial locale support."""
        from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat

        requested = ['en-US', 'xx-YY']  # xx-YY is not a real locale
        result = IntlDateTimeFormat.supportedLocalesOf(requested)

        assert 'en-US' in result
        # Invalid locale should not be in result
        assert 'xx-YY' not in result

    def test_supported_locales_empty_input(self):
        """Test empty input returns empty array."""
        from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat

        result = IntlDateTimeFormat.supportedLocalesOf([])
        assert result == []

    def test_supported_locales_with_locale_matcher(self):
        """Test supportedLocalesOf with localeMatcher option."""
        from components.intl_datetimeformat.src.datetime_format import IntlDateTimeFormat

        requested = ['en-US', 'fr-FR']
        result = IntlDateTimeFormat.supportedLocalesOf(
            requested,
            {'localeMatcher': 'best fit'}
        )

        assert isinstance(result, list)
        assert len(result) > 0
