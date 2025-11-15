"""
RelativeTimeFormat class - Intl.RelativeTimeFormat implementation.

Provides locale-aware relative time formatting (FR-ES24-C-037 to FR-ES24-C-042).
"""

from .options import RelativeTimeFormatOptions
from .formatter import RelativeTimeFormatter
from .locale_resolver import LocaleResolver
from .exceptions import RangeError, TypeError


class RelativeTimeFormat:
    """
    Intl.RelativeTimeFormat for locale-aware relative time formatting.

    Implements FR-ES24-C-037 to FR-ES24-C-042.
    """

    def __init__(self, locales=None, options=None):
        """
        Create RelativeTimeFormat instance with locale and options.

        Args:
            locales: BCP 47 language tag(s) or array of tags (optional)
            options: Options dict with style, numeric, localeMatcher (optional)

        Raises:
            RangeError: Invalid locale or option values
        """
        # Resolve locale
        locale_resolver = LocaleResolver()
        if locales is None:
            resolved_locale = locale_resolver.get_default_locale()
        elif isinstance(locales, str):
            resolved_locale = locale_resolver.resolve_locale(locales)
        elif isinstance(locales, list):
            resolved_locale = locale_resolver.resolve_best_locale(locales)
        else:
            raise TypeError("Locales must be a string or array")

        # Parse options
        options_dict = options if options is not None else {}

        # Validate and extract options
        validator = RelativeTimeFormatOptions()

        # localeMatcher (not stored in resolved options, but used during resolution)
        locale_matcher = options_dict.get('localeMatcher', 'best fit')
        if locale_matcher not in ['lookup', 'best fit']:
            raise RangeError(f"Invalid value for option 'localeMatcher': {locale_matcher}")

        # style
        style = options_dict.get('style', 'long')
        self._style = validator.validate_style(style)

        # numeric
        numeric = options_dict.get('numeric', 'always')
        self._numeric = validator.validate_numeric(numeric)

        # Store resolved locale
        self._locale = resolved_locale

        # Get numbering system for locale
        self._numberingSystem = locale_resolver.get_numbering_system(resolved_locale)

        # Create formatter
        self._formatter = RelativeTimeFormatter()

    def format(self, value, unit):
        """
        Format relative time as a localized string.

        Args:
            value: Numeric value (positive=future, negative=past)
            unit: Time unit (second, minute, hour, day, week, month, quarter, year)

        Returns:
            Formatted relative time string

        Raises:
            TypeError: If value is not a number
            RangeError: If unit is not valid
        """
        # Validate value type
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be a number")

        # Validate and normalize unit
        validator = RelativeTimeFormatOptions()
        normalized_unit = validator.validate_unit(unit)

        # Format based on numeric mode
        if self._numeric == 'always':
            return self._formatter.format_numeric(
                value, normalized_unit, self._locale, self._style
            )
        else:  # auto
            return self._formatter.format_auto(
                value, normalized_unit, self._locale, self._style
            )

    def formatToParts(self, value, unit):
        """
        Format relative time as array of parts for custom formatting.

        Args:
            value: Numeric value
            unit: Time unit

        Returns:
            Array of {type, value} objects

        Raises:
            TypeError: If value is not a number
            RangeError: If unit is not valid
        """
        # Validate value type
        if not isinstance(value, (int, float)):
            raise TypeError("Value must be a number")

        # Validate and normalize unit
        validator = RelativeTimeFormatOptions()
        normalized_unit = validator.validate_unit(unit)

        # Format to string first
        formatted_string = self.format(value, unit)

        # Split into parts
        parts = self._formatter.split_to_parts(formatted_string, value)

        return parts

    def resolvedOptions(self):
        """
        Return resolved options used by formatter.

        Returns:
            Dict with locale, style, numeric, numberingSystem
        """
        return {
            'locale': self._locale,
            'style': self._style,
            'numeric': self._numeric,
            'numberingSystem': self._numberingSystem
        }
