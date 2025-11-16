"""
Intl.Collator implementation.

FR-ES24-C-001: Intl.Collator constructor
FR-ES24-C-002: Locale resolution
FR-ES24-C-003: compare() method
FR-ES24-C-008: resolvedOptions() method
"""

import re
from .comparison import compare_strings


class RangeError(Exception):
    """Range error for invalid values."""
    pass


class IntlCollator:
    """
    Intl.Collator - Language-sensitive string comparison.

    Implements Unicode Collation Algorithm (UCA) for locale-aware
    string comparison and sorting.
    """

    # Supported locales
    SUPPORTED_LOCALES = [
        'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES',
        'zh-CN', 'ja-JP', 'ko-KR', 'en', 'de', 'fr', 'es', 'zh', 'ja', 'ko'
    ]

    # Default locale
    DEFAULT_LOCALE = 'en-US'

    def __init__(self, locales=None, options=None):
        """
        Create Collator with locale and collation settings.

        Args:
            locales: BCP 47 language tag(s) for locale selection
            options: Collation configuration options

        Raises:
            RangeError: If locale is invalid
        """
        # Initialize options with defaults
        if options is None:
            options = {}

        # Resolve locale
        self._locale = self._resolve_locale(locales)

        # Parse Unicode extension keys from locale
        locale_info = self._parse_locale_extensions(self._locale)

        # Set options (options parameter overrides locale extensions)
        self._usage = options.get('usage', 'sort')
        self._sensitivity = options.get('sensitivity', 'variant')
        self._numeric = options.get('numeric',
                                    locale_info.get('numeric', False))
        self._case_first = options.get('caseFirst',
                                       locale_info.get('caseFirst', 'false'))
        self._ignore_punctuation = options.get('ignorePunctuation', False)
        self._collation = options.get('collation',
                                      locale_info.get('collation', 'default'))
        self._locale_matcher = options.get('localeMatcher', 'best fit')

        # Validate options
        self._validate_options()

    def _resolve_locale(self, locales):
        """
        Resolve locale from requested locales.

        Args:
            locales: String, list of strings, or None

        Returns:
            str: Resolved locale

        Raises:
            RangeError: If locale is invalid
        """
        if locales is None:
            return self.DEFAULT_LOCALE

        # Convert to list
        if isinstance(locales, str):
            locale_list = [locales]
        elif isinstance(locales, list):
            locale_list = locales
        else:
            locale_list = [str(locales)]

        # Try each locale
        for locale in locale_list:
            # Validate BCP 47 format
            if not self._is_valid_locale(locale):
                raise RangeError(f"Invalid locale: {locale}")

            # Check if supported
            base_locale = self._get_base_locale(locale)
            if base_locale in self.SUPPORTED_LOCALES:
                return locale

            # Try just language code
            lang_code = locale.split('-')[0]
            if lang_code in self.SUPPORTED_LOCALES:
                return lang_code

        # Fall back to default
        return self.DEFAULT_LOCALE

    def _is_valid_locale(self, locale):
        """
        Check if locale is a valid BCP 47 language tag.

        Args:
            locale: Locale string to validate

        Returns:
            bool: True if valid
        """
        # Basic BCP 47 pattern
        # language[-script][-region][-variant][-extension]
        pattern = r'^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?(-[a-z0-9]+)*(-u(-[a-z0-9]+)+)?$'
        return bool(re.match(pattern, locale, re.IGNORECASE))

    def _get_base_locale(self, locale):
        """
        Get base locale without extensions.

        Args:
            locale: Full locale string

        Returns:
            str: Base locale (e.g., 'en-US' from 'en-US-u-kn-true')
        """
        # Remove Unicode extensions (-u-...)
        parts = locale.split('-u-')
        return parts[0]

    def _parse_locale_extensions(self, locale):
        """
        Parse Unicode extension keys from locale.

        Args:
            locale: Locale string

        Returns:
            dict: Parsed extension values
        """
        extensions = {}

        # Check for Unicode extension (-u-)
        if '-u-' not in locale:
            return extensions

        # Extract extension part
        parts = locale.split('-u-')
        if len(parts) < 2:
            return extensions

        ext_part = parts[1]
        ext_tokens = ext_part.split('-')

        # Parse key-value pairs
        i = 0
        while i < len(ext_tokens):
            key = ext_tokens[i]

            # co: collation
            if key == 'co' and i + 1 < len(ext_tokens):
                extensions['collation'] = ext_tokens[i + 1]
                i += 2
            # kn: numeric
            elif key == 'kn' and i + 1 < len(ext_tokens):
                extensions['numeric'] = ext_tokens[i + 1] == 'true'
                i += 2
            # kf: caseFirst
            elif key == 'kf' and i + 1 < len(ext_tokens):
                extensions['caseFirst'] = ext_tokens[i + 1]
                i += 2
            else:
                i += 1

        return extensions

    def _validate_options(self):
        """Validate collator options."""
        valid_usage = ['sort', 'search']
        if self._usage not in valid_usage:
            raise RangeError(f"Invalid usage: {self._usage}")

        valid_sensitivity = ['base', 'accent', 'case', 'variant']
        if self._sensitivity not in valid_sensitivity:
            raise RangeError(f"Invalid sensitivity: {self._sensitivity}")

        valid_case_first = ['upper', 'lower', 'false']
        if self._case_first not in valid_case_first:
            raise RangeError(f"Invalid caseFirst: {self._case_first}")

    def compare(self, string1, string2):
        """
        Compare two strings according to collation rules.

        Args:
            string1: First string to compare
            string2: Second string to compare

        Returns:
            number: negative if string1 < string2, 0 if equal, positive if string1 > string2
        """
        # Convert to strings if needed
        s1 = str(string1) if string1 is not None else ''
        s2 = str(string2) if string2 is not None else ''

        # Use comparison algorithm
        return compare_strings(
            s1, s2,
            sensitivity=self._sensitivity,
            numeric=self._numeric,
            case_first=self._case_first,
            ignore_punctuation=self._ignore_punctuation,
            locale=self._locale
        )

    def resolved_options(self):
        """
        Returns object with resolved locale and collation options.

        Returns:
            dict: Resolved options
        """
        return {
            'locale': self._get_base_locale(self._locale),
            'usage': self._usage,
            'sensitivity': self._sensitivity,
            'numeric': self._numeric,
            'caseFirst': self._case_first,
            'ignorePunctuation': self._ignore_punctuation,
            'collation': self._collation
        }

    @staticmethod
    def supported_locales_of(locales, options=None):
        """
        Returns array of supported locales from requested locales.

        Args:
            locales: Locale(s) to check
            options: Options for locale matching

        Returns:
            list: Supported locales
        """
        # Convert to list
        if isinstance(locales, str):
            locale_list = [locales]
        else:
            locale_list = list(locales)

        supported = []
        for locale in locale_list:
            # Check if locale or its base is supported
            base_locale = locale.split('-u-')[0]  # Remove extensions
            if base_locale in IntlCollator.SUPPORTED_LOCALES:
                supported.append(locale)
            else:
                # Try language code only
                lang_code = locale.split('-')[0]
                if lang_code in IntlCollator.SUPPORTED_LOCALES:
                    supported.append(locale)

        return supported
