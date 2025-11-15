"""
PluralRulesEngine and CLDRDataProvider

Internal engine for evaluating CLDR plural rules
"""
import re
from decimal import Decimal
from typing import Dict, List, Callable, Any


class CLDRDataProvider:
    """
    Provider for CLDR plural rule data

    Implements lazy loading of locale-specific plural rules from CLDR data.
    """

    def __init__(self):
        """Initialize CLDR data provider with lazy loading cache"""
        self._cardinal_rules_cache: Dict[str, Dict[str, Callable]] = {}
        self._ordinal_rules_cache: Dict[str, Dict[str, Callable]] = {}
        self._range_rules_cache: Dict[str, Dict[tuple, str]] = {}
        self._categories_cache: Dict[tuple, List[str]] = {}

    def getCardinalRules(self, locale: str) -> Dict[str, Callable]:
        """
        Get cardinal plural rules for locale from CLDR

        Args:
            locale: BCP 47 locale identifier

        Returns:
            Dictionary mapping category names to rule functions
        """
        # Normalize locale
        locale = self._normalizeLocale(locale)

        # Check cache
        if locale in self._cardinal_rules_cache:
            return self._cardinal_rules_cache[locale]

        # Load rules for this locale
        rules = self._loadCardinalRules(locale)
        self._cardinal_rules_cache[locale] = rules
        return rules

    def getOrdinalRules(self, locale: str) -> Dict[str, Callable]:
        """
        Get ordinal plural rules for locale from CLDR

        Args:
            locale: BCP 47 locale identifier

        Returns:
            Dictionary mapping category names to rule functions
        """
        locale = self._normalizeLocale(locale)

        if locale in self._ordinal_rules_cache:
            return self._ordinal_rules_cache[locale]

        rules = self._loadOrdinalRules(locale)
        self._ordinal_rules_cache[locale] = rules
        return rules

    def getRangeRules(self, locale: str) -> Dict[tuple, str]:
        """
        Get range resolution rules for locale

        Args:
            locale: BCP 47 locale identifier

        Returns:
            Dictionary mapping (start_category, end_category) to result category
        """
        locale = self._normalizeLocale(locale)

        if locale in self._range_rules_cache:
            return self._range_rules_cache[locale]

        rules = self._loadRangeRules(locale)
        self._range_rules_cache[locale] = rules
        return rules

    def getPluralCategories(self, locale: str, rule_type: str) -> List[str]:
        """
        Get list of plural categories used by locale

        Args:
            locale: BCP 47 locale identifier
            rule_type: 'cardinal' or 'ordinal'

        Returns:
            List of category names (e.g., ['one', 'other'])
        """
        locale = self._normalizeLocale(locale)
        cache_key = (locale, rule_type)

        if cache_key in self._categories_cache:
            return self._categories_cache[cache_key]

        if rule_type == 'cardinal':
            rules = self.getCardinalRules(locale)
        else:
            rules = self.getOrdinalRules(locale)

        categories = list(rules.keys())
        self._categories_cache[cache_key] = categories
        return categories

    def _normalizeLocale(self, locale: str) -> str:
        """Normalize locale identifier"""
        if locale is None:
            return 'en-US'  # Default locale

        # Handle locale fallback
        # For now, just use the locale as-is
        # In production, would implement proper fallback chain
        return locale

    def _loadCardinalRules(self, locale: str) -> Dict[str, Callable]:
        """Load cardinal plural rules for locale"""
        # CLDR plural rules implementation
        # This is a simplified version - production would load from CLDR JSON data

        base_locale = locale.split('-')[0]  # Get language code

        # English rules
        if base_locale == 'en':
            return {
                'one': lambda operands: operands['n'] == 1 and operands['v'] == 0,
                'other': lambda operands: True  # Default
            }

        # Arabic rules (all 6 categories)
        elif base_locale == 'ar':
            return {
                'zero': lambda operands: operands['n'] == 0,
                'one': lambda operands: operands['n'] == 1,
                'two': lambda operands: operands['n'] == 2,
                'few': lambda operands: operands['n'] % 100 >= 3 and operands['n'] % 100 <= 10,
                'many': lambda operands: operands['n'] % 100 >= 11 and operands['n'] % 100 <= 99,
                'other': lambda operands: True
            }

        # Polish rules
        elif base_locale == 'pl':
            return {
                'one': lambda operands: operands['n'] == 1 and operands['v'] == 0,
                'few': lambda operands: (
                    operands['v'] == 0 and
                    operands['n'] % 10 >= 2 and operands['n'] % 10 <= 4 and
                    not (operands['n'] % 100 >= 12 and operands['n'] % 100 <= 14)
                ),
                'many': lambda operands: (
                    operands['v'] == 0 and (
                        (operands['n'] != 1 and operands['n'] % 10 >= 0 and operands['n'] % 10 <= 1) or
                        (operands['n'] % 10 >= 5 and operands['n'] % 10 <= 9) or
                        (operands['n'] % 100 >= 12 and operands['n'] % 100 <= 14)
                    )
                ),
                'other': lambda operands: True
            }

        # Japanese, Chinese (minimal - other only)
        elif base_locale in ['ja', 'zh']:
            return {
                'other': lambda operands: True
            }

        # French
        elif base_locale == 'fr':
            return {
                'one': lambda operands: operands['n'] >= 0 and operands['n'] < 2,
                'other': lambda operands: True
            }

        # Russian
        elif base_locale == 'ru':
            return {
                'one': lambda operands: (
                    operands['v'] == 0 and
                    operands['n'] % 10 == 1 and
                    operands['n'] % 100 != 11
                ),
                'few': lambda operands: (
                    operands['v'] == 0 and
                    operands['n'] % 10 >= 2 and operands['n'] % 10 <= 4 and
                    not (operands['n'] % 100 >= 12 and operands['n'] % 100 <= 14)
                ),
                'many': lambda operands: (
                    operands['v'] == 0 and (
                        operands['n'] % 10 == 0 or
                        (operands['n'] % 10 >= 5 and operands['n'] % 10 <= 9) or
                        (operands['n'] % 100 >= 11 and operands['n'] % 100 <= 14)
                    )
                ),
                'other': lambda operands: True
            }

        # Welsh (cy)
        elif base_locale == 'cy':
            return {
                'zero': lambda operands: operands['n'] == 0,
                'one': lambda operands: operands['n'] == 1,
                'two': lambda operands: operands['n'] == 2,
                'few': lambda operands: operands['n'] == 3,
                'many': lambda operands: operands['n'] == 6,
                'other': lambda operands: True
            }

        # Default (English-like)
        else:
            return {
                'one': lambda operands: operands['n'] == 1 and operands['v'] == 0,
                'other': lambda operands: True
            }

    def _loadOrdinalRules(self, locale: str) -> Dict[str, Callable]:
        """Load ordinal plural rules for locale"""
        base_locale = locale.split('-')[0]

        # English ordinal rules (1st, 2nd, 3rd, 4th, etc.)
        if base_locale == 'en':
            return {
                'one': lambda operands: (
                    operands['n'] % 10 == 1 and
                    operands['n'] % 100 != 11
                ),
                'two': lambda operands: (
                    operands['n'] % 10 == 2 and
                    operands['n'] % 100 != 12
                ),
                'few': lambda operands: (
                    operands['n'] % 10 == 3 and
                    operands['n'] % 100 != 13
                ),
                'other': lambda operands: True
            }

        # Most other languages don't have complex ordinal rules
        else:
            return {
                'other': lambda operands: True
            }

    def _loadRangeRules(self, locale: str) -> Dict[tuple, str]:
        """Load range resolution rules for locale"""
        base_locale = locale.split('-')[0]

        # English range rules
        if base_locale == 'en':
            return {
                ('one', 'one'): 'one',
                ('one', 'other'): 'other',
                ('other', 'one'): 'other',
                ('other', 'other'): 'other',
            }

        # Polish range rules
        elif base_locale == 'pl':
            return {
                ('one', 'few'): 'few',
                ('one', 'many'): 'many',
                ('one', 'other'): 'other',
                ('few', 'few'): 'few',
                ('few', 'many'): 'many',
                ('few', 'other'): 'other',
                ('many', 'many'): 'many',
                ('many', 'other'): 'other',
                ('other', 'other'): 'other',
            }

        # Arabic range rules
        elif base_locale == 'ar':
            # Simplified - same category wins
            categories = ['zero', 'one', 'two', 'few', 'many', 'other']
            rules = {}
            for start in categories:
                for end in categories:
                    # If same, use that category
                    if start == end:
                        rules[(start, end)] = start
                    # If different, use 'other' (simplified)
                    else:
                        rules[(start, end)] = 'other'
            return rules

        # Default: use end category
        else:
            return {}


class PluralRulesEngine:
    """
    Internal engine for CLDR-based plural rule evaluation

    Evaluates plural rules using CLDR operands (n, i, v, w, f, t).
    """

    def __init__(self):
        """Initialize plural rules engine with CLDR data provider"""
        self._provider = CLDRDataProvider()

    def evaluateCardinalRule(self, locale: str, number: float, number_options: Dict[str, Any]) -> str:
        """
        Evaluate CLDR cardinal plural rules for locale

        Args:
            locale: BCP 47 locale identifier
            number: Number to evaluate
            number_options: Formatting options

        Returns:
            CLDR plural category ('zero', 'one', 'two', 'few', 'many', 'other')
        """
        # Get operands
        operands = self.getPluralOperands(number, number_options)

        # Get rules for locale
        rules = self._provider.getCardinalRules(locale)

        # Evaluate rules in order of specificity
        # Check specific categories first, 'other' last
        for category in ['zero', 'one', 'two', 'few', 'many', 'other']:
            if category in rules:
                if rules[category](operands):
                    return category

        # Default to 'other'
        return 'other'

    def evaluateOrdinalRule(self, locale: str, number: float, number_options: Dict[str, Any]) -> str:
        """
        Evaluate CLDR ordinal plural rules for locale

        Args:
            locale: BCP 47 locale identifier
            number: Number to evaluate
            number_options: Formatting options

        Returns:
            CLDR plural category
        """
        operands = self.getPluralOperands(number, number_options)
        rules = self._provider.getOrdinalRules(locale)

        for category in ['one', 'two', 'few', 'many', 'other']:
            if category in rules:
                if rules[category](operands):
                    return category

        return 'other'

    def evaluateRangeRule(self, locale: str, start_category: str, end_category: str) -> str:
        """
        Combine two plural categories into range category

        Args:
            locale: BCP 47 locale identifier
            start_category: Plural category for range start
            end_category: Plural category for range end

        Returns:
            Combined plural category for the range
        """
        range_rules = self._provider.getRangeRules(locale)

        # Look up rule for this combination
        key = (start_category, end_category)
        if key in range_rules:
            return range_rules[key]

        # Default: use end category
        return end_category

    def getPluralOperands(self, number: float, options: Dict[str, Any]) -> Dict[str, int]:
        """
        Extract CLDR plural operands from formatted number

        CLDR operands:
        - n: Absolute value of the source number
        - i: Integer digits of n
        - v: Number of visible fraction digits with trailing zeros
        - w: Number of visible fraction digits without trailing zeros
        - f: Visible fractional digits with trailing zeros (as integer)
        - t: Visible fractional digits without trailing zeros (as integer)

        Args:
            number: Input number
            options: Formatting options (minimumFractionDigits, etc.)

        Returns:
            Dictionary with operands n, i, v, w, f, t
        """
        # Use absolute value
        n = abs(number)

        # Get integer part
        i = int(n)

        # Format number according to options
        formatted = self._formatNumber(n, options)

        # Extract fraction part
        if '.' in formatted:
            fraction_str = formatted.split('.')[1]
            v = len(fraction_str)  # Visible fraction digits

            # Remove trailing zeros to get w and t
            fraction_no_zeros = fraction_str.rstrip('0')
            w = len(fraction_no_zeros)

            f = int(fraction_str) if fraction_str else 0
            t = int(fraction_no_zeros) if fraction_no_zeros else 0
        else:
            v = 0
            w = 0
            f = 0
            t = 0

        return {
            'n': n,
            'i': i,
            'v': v,
            'w': w,
            'f': f,
            't': t
        }

    def _formatNumber(self, number: float, options: Dict[str, Any]) -> str:
        """
        Format number according to options

        Args:
            number: Number to format
            options: Formatting options

        Returns:
            Formatted number string
        """
        min_fraction = options.get('minimumFractionDigits', 0)
        max_fraction = options.get('maximumFractionDigits', 3)
        min_significant = options.get('minimumSignificantDigits')
        max_significant = options.get('maximumSignificantDigits')

        # If significant digits are specified, they override fraction digits
        if min_significant is not None or max_significant is not None:
            # Use significant digits formatting
            # Simplified implementation
            if max_significant is not None:
                # Format with significant digits
                formatted = f"{number:.{max_significant}g}"
                # Ensure minimum significant digits
                if min_significant is not None:
                    # Pad if needed
                    pass
                return formatted

        # Use fraction digits formatting
        # Ensure we have at least min_fraction digits
        if min_fraction > 0:
            format_str = f"{{:.{min_fraction}f}}"
            formatted = format_str.format(number)

            # If we have more than max_fraction, truncate
            if '.' in formatted:
                int_part, frac_part = formatted.split('.')
                if len(frac_part) > max_fraction:
                    frac_part = frac_part[:max_fraction]
                formatted = f"{int_part}.{frac_part}"

            return formatted
        else:
            # No minimum fraction digits
            if number == int(number):
                return str(int(number))
            else:
                # Format with max_fraction digits
                formatted = f"{number:.{max_fraction}f}"
                # Remove trailing zeros if no minimum
                return formatted.rstrip('0').rstrip('.')
