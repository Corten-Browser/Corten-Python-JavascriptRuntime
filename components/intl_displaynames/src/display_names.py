"""
IntlDisplayNames implementation for ES2024 Wave C
Provides localized display names for language, region, script, currency, and calendar codes
"""
import re
from typing import Union, List, Dict, Optional, Any


class IntlDisplayNames:
    """
    Intl.DisplayNames API implementation

    Provides localized display names for:
    - Language codes (ISO 639)
    - Region codes (ISO 3166-1)
    - Script codes (ISO 15924)
    - Currency codes (ISO 4217)
    - Calendar identifiers
    """

    # Valid option values
    VALID_TYPES = {'language', 'region', 'script', 'currency', 'calendar', 'dateTimeField'}
    VALID_STYLES = {'long', 'short', 'narrow'}
    VALID_FALLBACK = {'code', 'none'}
    VALID_LANGUAGE_DISPLAY = {'dialect', 'standard'}

    def __init__(self, locales: Union[str, List[str]], options: Dict[str, Any]):
        """
        Create a new IntlDisplayNames instance

        Args:
            locales: BCP 47 language tag(s)
            options: Configuration options (type, style, fallback, languageDisplay)

        Raises:
            TypeError: If type option is missing
            ValueError: If options have invalid values
        """
        # Validate required type option
        if not isinstance(options, dict) or 'type' not in options:
            raise TypeError("type option is required")

        # Validate type
        display_type = options['type']
        if display_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {display_type}. Must be one of {self.VALID_TYPES}")

        # Validate style
        style = options.get('style', 'long')
        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid style: {style}. Must be one of {self.VALID_STYLES}")

        # Validate fallback
        fallback = options.get('fallback', 'code')
        if fallback not in self.VALID_FALLBACK:
            raise ValueError(f"Invalid fallback: {fallback}. Must be one of {self.VALID_FALLBACK}")

        # Validate languageDisplay
        language_display = options.get('languageDisplay', 'dialect')
        if language_display not in self.VALID_LANGUAGE_DISPLAY:
            raise ValueError(f"Invalid languageDisplay: {language_display}. Must be one of {self.VALID_LANGUAGE_DISPLAY}")

        # Normalize and validate locales
        if isinstance(locales, str):
            locales = [locales]
        elif not isinstance(locales, list):
            raise ValueError("locales must be a string or list of strings")

        # Validate locale format (basic BCP 47 validation)
        resolved_locale = self._resolve_locale(locales)

        # Store resolved options
        self._locale = resolved_locale
        self._type = display_type
        self._style = style
        self._fallback = fallback
        self._language_display = language_display

        # Initialize name provider (lazy loaded)
        from components.intl_displaynames.src.name_provider import NameProvider
        self._provider = NameProvider(resolved_locale, display_type, style, language_display)

    def _resolve_locale(self, locales: List[str]) -> str:
        """
        Resolve best matching locale from list

        Args:
            locales: List of BCP 47 language tags

        Returns:
            Resolved locale identifier

        Raises:
            ValueError: If locale is invalid
        """
        # Simple locale validation pattern
        locale_pattern = re.compile(r'^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?(-[a-zA-Z0-9]+)*$')

        for locale in locales:
            # Basic validation
            if not locale or not isinstance(locale, str):
                raise ValueError(f"Invalid locale: {locale}")

            # Check for obviously invalid characters
            if '!' in locale or '?' in locale or ' ' in locale:
                raise ValueError(f"Invalid locale: {locale}")

            # For now, accept the first locale (simple resolution)
            # In a full implementation, this would check against available locales
            # Normalize to lowercase language code
            parts = locale.split('-')
            if len(parts) > 0 and len(parts[0]) >= 2:
                return locale

        # If no valid locale found, raise error
        raise ValueError(f"Invalid locale identifiers: {locales}")

    def of(self, code: str) -> Optional[str]:
        """
        Get display name for given code

        Args:
            code: Language/region/script/currency/calendar code

        Returns:
            Localized display name, or code itself (fallback=code), or None (fallback=none)

        Raises:
            TypeError: If code is not a string
            ValueError: If code format is invalid for the type
        """
        # Validate argument type
        if code is None:
            raise TypeError("code must be a string, not None")
        if not isinstance(code, str):
            raise TypeError(f"code must be a string, not {type(code).__name__}")

        # Validate code is not empty
        if not code:
            raise ValueError("Invalid code: empty string")

        # Validate code format based on type
        self._validate_code_format(code)

        # Get display name from provider
        display_name = self._provider.get_display_name(code)

        # Apply fallback behavior
        if display_name is None:
            if self._fallback == 'code':
                return code
            else:  # fallback == 'none'
                return None

        return display_name

    def _validate_code_format(self, code: str):
        """
        Validate code format based on display type

        Args:
            code: Code to validate

        Raises:
            ValueError: If code format is invalid for the type
        """
        if self._type == 'language':
            # Language codes: 2-3 letter codes (ISO 639), optionally with subtags
            # Examples: "en", "es", "eng", "en-US"
            if not re.match(r'^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?(-[a-zA-Z0-9]+)*$', code):
                raise ValueError(f"Invalid language code format: {code}")

        elif self._type == 'region':
            # Region codes: 2 uppercase letters (ISO 3166-1 alpha-2)
            # Examples: "US", "GB", "JP"
            if not re.match(r'^[A-Z]{2}$', code):
                raise ValueError(f"Invalid region code format: {code}. Must be 2 uppercase letters")

        elif self._type == 'script':
            # Script codes: 4 letters, titlecase (ISO 15924)
            # Examples: "Latn", "Cyrl", "Arab"
            if not re.match(r'^[A-Z][a-z]{3}$', code):
                raise ValueError(f"Invalid script code format: {code}. Must be 4 letters in titlecase")

        elif self._type == 'currency':
            # Currency codes: 3 uppercase letters (ISO 4217)
            # Examples: "USD", "EUR", "JPY"
            if not re.match(r'^[A-Z]{3}$', code):
                raise ValueError(f"Invalid currency code format: {code}. Must be 3 uppercase letters")

        elif self._type == 'calendar':
            # Calendar identifiers: lowercase alphanumeric
            # Examples: "gregory", "islamic", "hebrew"
            if not re.match(r'^[a-z][a-z0-9-]*$', code):
                raise ValueError(f"Invalid calendar code format: {code}")

    def resolved_options(self) -> Dict[str, Any]:
        """
        Return resolved configuration options

        Returns:
            Dictionary with resolved locale, type, style, fallback, and languageDisplay
        """
        options = {
            'locale': self._locale,
            'type': self._type,
            'style': self._style,
            'fallback': self._fallback,
        }

        # Only include languageDisplay for type=language
        if self._type == 'language':
            options['languageDisplay'] = self._language_display

        # Return a copy to prevent modification
        return options.copy()
