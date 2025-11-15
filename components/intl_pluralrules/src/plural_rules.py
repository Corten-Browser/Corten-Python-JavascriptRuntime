"""
Intl.PluralRules implementation

ES2024 Wave C - Internationalization
Provides locale-aware plural form selection for cardinal and ordinal numbers.
"""
from typing import Union, List, Dict, Any, Optional

# Handle both relative and absolute imports
try:
    from .rules import PluralRulesEngine, CLDRDataProvider
except ImportError:
    from rules import PluralRulesEngine, CLDRDataProvider


# Use ValueError for RangeError (Python doesn't have built-in RangeError)
# TypeError is built-in
class RangeError(ValueError):
    """RangeError for out-of-range values"""
    pass


class PluralRules:
    """
    Intl.PluralRules API

    Enables locale-aware plural form selection based on CLDR plural rules.
    Supports both cardinal (quantities) and ordinal (ordering) plural forms.

    Implements FR-ES24-C-031 through FR-ES24-C-036.
    """

    def __init__(
        self,
        locales: Optional[Union[str, List[str]]] = None,
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Create new PluralRules instance

        Args:
            locales: BCP 47 language tag(s) or None for default locale
            options: Optional configuration object

        Options:
            - localeMatcher: 'lookup' or 'best fit' (default: 'best fit')
            - type: 'cardinal' or 'ordinal' (default: 'cardinal')
            - minimumIntegerDigits: 1-21 (default: 1)
            - minimumFractionDigits: 0-20 (default: 0)
            - maximumFractionDigits: 0-20 (default: 3)
            - minimumSignificantDigits: 1-21 (default: undefined)
            - maximumSignificantDigits: 1-21 (default: undefined)

        Raises:
            TypeError: If options is invalid
            RangeError: If digit range values are out of bounds

        Implements FR-ES24-C-031: Constructor with locale and options support
        """
        # Validate and normalize options
        if options is not None and not isinstance(options, dict):
            raise TypeError("Options must be an object/dict")

        options = options or {}

        # Validate type option
        rule_type = options.get('type', 'cardinal')
        if rule_type not in ['cardinal', 'ordinal']:
            raise TypeError(f"Invalid type: {rule_type}. Must be 'cardinal' or 'ordinal'")

        # Validate locale matcher
        locale_matcher = options.get('localeMatcher', 'best fit')
        if locale_matcher not in ['lookup', 'best fit']:
            raise TypeError(f"Invalid localeMatcher: {locale_matcher}")

        # Validate digit options
        min_integer = options.get('minimumIntegerDigits', 1)
        min_fraction = options.get('minimumFractionDigits', 0)
        max_fraction = options.get('maximumFractionDigits', 3)
        min_significant = options.get('minimumSignificantDigits')
        max_significant = options.get('maximumSignificantDigits')

        # Validate minimumIntegerDigits [1, 21]
        if not isinstance(min_integer, int) or min_integer < 1 or min_integer > 21:
            raise RangeError(f"minimumIntegerDigits must be between 1 and 21, got {min_integer}")

        # Validate minimumFractionDigits [0, 20]
        if not isinstance(min_fraction, int) or min_fraction < 0 or min_fraction > 20:
            raise RangeError(f"minimumFractionDigits must be between 0 and 20, got {min_fraction}")

        # Validate maximumFractionDigits [0, 20]
        if not isinstance(max_fraction, int) or max_fraction < 0 or max_fraction > 20:
            raise RangeError(f"maximumFractionDigits must be between 0 and 20, got {max_fraction}")

        # Validate minimumSignificantDigits [1, 21] (if specified)
        if min_significant is not None:
            if not isinstance(min_significant, int) or min_significant < 1 or min_significant > 21:
                raise RangeError(f"minimumSignificantDigits must be between 1 and 21, got {min_significant}")

        # Validate maximumSignificantDigits [1, 21] (if specified)
        if max_significant is not None:
            if not isinstance(max_significant, int) or max_significant < 1 or max_significant > 21:
                raise RangeError(f"maximumSignificantDigits must be between 1 and 21, got {max_significant}")

        # Resolve locale
        self._locale = self._resolveLocale(locales, locale_matcher)

        # Store resolved options
        self._type = rule_type
        self._locale_matcher = locale_matcher
        self._minimum_integer_digits = min_integer
        self._minimum_fraction_digits = min_fraction
        self._maximum_fraction_digits = max_fraction
        self._minimum_significant_digits = min_significant
        self._maximum_significant_digits = max_significant

        # Initialize engine
        self._engine = PluralRulesEngine()
        self._provider = CLDRDataProvider()

    def select(self, number: Union[int, float]) -> str:
        """
        Select appropriate plural category for a number

        Args:
            number: Number to get plural category for (Number or BigInt)

        Returns:
            CLDR plural category: 'zero', 'one', 'two', 'few', 'many', or 'other'

        Performance: <100µs per call

        Implements FR-ES24-C-032: select() returns CLDR plural category
        Implements FR-ES24-C-034: Cardinal vs ordinal type support
        Implements FR-ES24-C-035: All CLDR plural categories
        """
        # Build number options for operand calculation
        number_options = {
            'minimumIntegerDigits': self._minimum_integer_digits,
            'minimumFractionDigits': self._minimum_fraction_digits,
            'maximumFractionDigits': self._maximum_fraction_digits,
            'minimumSignificantDigits': self._minimum_significant_digits,
            'maximumSignificantDigits': self._maximum_significant_digits,
        }

        # Evaluate using engine
        if self._type == 'cardinal':
            return self._engine.evaluateCardinalRule(self._locale, float(number), number_options)
        else:  # ordinal
            return self._engine.evaluateOrdinalRule(self._locale, float(number), number_options)

    def selectRange(self, start_range: Union[int, float], end_range: Union[int, float]) -> str:
        """
        Select plural category for a numeric range

        Args:
            start_range: Start of range
            end_range: End of range

        Returns:
            Plural category for the range

        Raises:
            RangeError: If startRange > endRange

        Performance: <200µs per call

        Implements FR-ES24-C-033: selectRange() for numeric ranges
        """
        # Validate range
        if start_range > end_range:
            raise RangeError(f"Invalid range: start ({start_range}) > end ({end_range})")

        # Get categories for start and end
        start_category = self.select(start_range)
        end_category = self.select(end_range)

        # Combine using range rules
        return self._engine.evaluateRangeRule(self._locale, start_category, end_category)

    def resolvedOptions(self) -> Dict[str, Any]:
        """
        Return resolved options and locale for this PluralRules instance

        Returns:
            Object with resolved locale and options:
            - locale: Resolved BCP 47 locale identifier
            - type: 'cardinal' or 'ordinal'
            - minimumIntegerDigits: Number
            - minimumFractionDigits: Number
            - maximumFractionDigits: Number
            - minimumSignificantDigits: Number or None
            - maximumSignificantDigits: Number or None
            - pluralCategories: List of available plural categories

        Implements FR-ES24-C-036: resolvedOptions() method
        """
        # Get plural categories for this locale and type
        categories = self._provider.getPluralCategories(self._locale, self._type)

        # Return resolved options (create new dict each time for immutability)
        return {
            'locale': self._locale,
            'type': self._type,
            'minimumIntegerDigits': self._minimum_integer_digits,
            'minimumFractionDigits': self._minimum_fraction_digits,
            'maximumFractionDigits': self._maximum_fraction_digits,
            'minimumSignificantDigits': self._minimum_significant_digits,
            'maximumSignificantDigits': self._maximum_significant_digits,
            'pluralCategories': categories.copy()  # Return copy for immutability
        }

    def _resolveLocale(
        self,
        locales: Optional[Union[str, List[str]]],
        locale_matcher: str
    ) -> str:
        """
        Resolve locale from input locales

        Args:
            locales: Locale(s) to resolve
            locale_matcher: 'lookup' or 'best fit'

        Returns:
            Resolved BCP 47 locale identifier
        """
        # Default locale
        if locales is None:
            return 'en-US'

        # Single locale string
        if isinstance(locales, str):
            return locales

        # Array of locales - use first one for simplicity
        # In production, would implement proper locale negotiation
        if isinstance(locales, list) and len(locales) > 0:
            return locales[0]

        # Fallback to default
        return 'en-US'
