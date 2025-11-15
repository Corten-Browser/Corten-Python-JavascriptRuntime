"""
Locale resolution for RelativeTimeFormat.

Handles BCP 47 locale resolution and numbering system detection.
"""

import re
from .exceptions import RangeError


class LocaleResolver:
    """Resolve locales using BCP 47 algorithm."""

    # Common locales we support
    SUPPORTED_LOCALES = {
        'en-US', 'en-GB', 'en',
        'es-ES', 'es-MX', 'es',
        'fr-FR', 'fr-CA', 'fr',
        'de-DE', 'de',
        'it-IT', 'it',
        'pt-BR', 'pt-PT', 'pt',
        'ja-JP', 'ja',
        'zh-CN', 'zh-TW', 'zh',
        'ko-KR', 'ko',
        'ru-RU', 'ru',
        'ar-SA', 'ar',
        'hi-IN', 'hi'
    }

    # BCP 47 locale pattern
    BCP47_PATTERN = re.compile(
        r'^([a-z]{2,3})'  # language
        r'(?:-([A-Z][a-z]{3}))?'  # script (optional)
        r'(?:-([A-Z]{2}|[0-9]{3}))?'  # region (optional)
        r'(?:-(.+))?$'  # variants and extensions (optional)
    )

    def get_default_locale(self):
        """
        Get default locale.

        Returns:
            Default locale string ('en-US')
        """
        return 'en-US'

    def resolve_locale(self, locale_tag):
        """
        Resolve single locale tag.

        Args:
            locale_tag: BCP 47 locale tag

        Returns:
            Resolved locale tag

        Raises:
            RangeError: Invalid locale tag
        """
        # Basic validation
        if not isinstance(locale_tag, str):
            raise RangeError(f"Invalid language tag: {locale_tag}")

        # Parse with BCP 47 pattern
        match = self.BCP47_PATTERN.match(locale_tag)
        if not match:
            raise RangeError(f"Invalid language tag: {locale_tag}")

        language = match.group(1).lower()
        script = match.group(2)
        region = match.group(3)

        # Build normalized tag
        if region:
            normalized = f"{language}-{region.upper()}"
        else:
            normalized = language

        # Check if supported (or return as-is for best fit)
        if normalized in self.SUPPORTED_LOCALES:
            return normalized
        elif language in self.SUPPORTED_LOCALES:
            return language
        else:
            # Best fit: return normalized tag even if not explicitly supported
            return normalized

    def resolve_best_locale(self, locale_list):
        """
        Resolve best matching locale from list.

        Args:
            locale_list: List of BCP 47 locale tags

        Returns:
            Best matching locale

        Raises:
            RangeError: Invalid locale tag(s)
        """
        if not locale_list:
            return self.get_default_locale()

        # Try each locale in order
        for locale in locale_list:
            try:
                resolved = self.resolve_locale(locale)
                return resolved
            except RangeError:
                continue

        # No valid locale found, use default
        return self.get_default_locale()

    def get_numbering_system(self, locale):
        """
        Get numbering system for locale.

        Args:
            locale: BCP 47 locale tag

        Returns:
            Numbering system identifier (e.g., 'latn')
        """
        # Simple mapping for common locales
        # Most Western locales use Latin numbering
        numbering_systems = {
            'ar': 'arab',  # Arabic
            'hi': 'deva',  # Devanagari
            'th': 'thai',  # Thai
            'bn': 'beng',  # Bengali
            'ta': 'taml',  # Tamil
        }

        # Extract language code
        language = locale.split('-')[0]

        return numbering_systems.get(language, 'latn')
