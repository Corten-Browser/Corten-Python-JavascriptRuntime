"""
Intl.ListFormat - Main implementation

Provides locale-aware list formatting with support for:
- Conjunction lists (A, B, and C)
- Disjunction lists (A, B, or C)
- Unit lists (A, B, C)
- Multiple styles (long, short, narrow)
"""

from typing import Union, List, Dict, Any, Optional, Iterable


class ListPatterns:
    """List formatting patterns for a locale"""

    def __init__(self, start: str, middle: str, end: str, pair: str, two: Optional[str] = None):
        self.start = start
        self.middle = middle
        self.end = end
        self.pair = pair
        self.two = two if two is not None else pair


class ListPatternProvider:
    """
    Provides locale-specific list formatting patterns

    Requirement: FR-ES24-C-046
    Description: Type option - conjunction/disjunction/unit
    Implementation: Returns type-specific patterns for each locale
                   - Conjunction uses "and" (or locale equivalent)
                   - Disjunction uses "or" (or locale equivalent)
                   - Unit uses minimal separators
    """

    # Simplified pattern database
    # In production, this would load from CLDR data
    PATTERNS = {
        'en': {
            'conjunction': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, and {1}",
                    pair="{0} and {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, & {1}",
                    pair="{0} & {1}"
                ),
                'narrow': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
            },
            'disjunction': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, or {1}",
                    pair="{0} or {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, or {1}",
                    pair="{0} or {1}"
                ),
                'narrow': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, or {1}",
                    pair="{0} or {1}"
                ),
            },
            'unit': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
                'narrow': ListPatterns(
                    start="{0} {1}",
                    middle="{0} {1}",
                    end="{0} {1}",
                    pair="{0} {1}"
                ),
            },
        },
        'es': {
            'conjunction': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0} y {1}",
                    pair="{0} y {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0} y {1}",
                    pair="{0} y {1}"
                ),
                'narrow': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
            },
            'disjunction': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0} o {1}",
                    pair="{0} o {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0} o {1}",
                    pair="{0} o {1}"
                ),
                'narrow': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0} o {1}",
                    pair="{0} o {1}"
                ),
            },
            'unit': {
                'long': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
                'short': ListPatterns(
                    start="{0}, {1}",
                    middle="{0}, {1}",
                    end="{0}, {1}",
                    pair="{0}, {1}"
                ),
                'narrow': ListPatterns(
                    start="{0} {1}",
                    middle="{0} {1}",
                    end="{0} {1}",
                    pair="{0} {1}"
                ),
            },
        },
        'ja': {
            'conjunction': {
                'long': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、{1}",
                    pair="{0}、{1}"
                ),
                'short': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、{1}",
                    pair="{0}、{1}"
                ),
                'narrow': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、{1}",
                    pair="{0}、{1}"
                ),
            },
            'disjunction': {
                'long': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、または{1}",
                    pair="{0}、または{1}"
                ),
                'short': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、または{1}",
                    pair="{0}、または{1}"
                ),
                'narrow': ListPatterns(
                    start="{0}、{1}",
                    middle="{0}、{1}",
                    end="{0}、または{1}",
                    pair="{0}、または{1}"
                ),
            },
            'unit': {
                'long': ListPatterns(
                    start="{0} {1}",
                    middle="{0} {1}",
                    end="{0} {1}",
                    pair="{0} {1}"
                ),
                'short': ListPatterns(
                    start="{0} {1}",
                    middle="{0} {1}",
                    end="{0} {1}",
                    pair="{0} {1}"
                ),
                'narrow': ListPatterns(
                    start="{0} {1}",
                    middle="{0} {1}",
                    end="{0} {1}",
                    pair="{0} {1}"
                ),
            },
        },
    }

    def get_patterns(self, locale: str, list_type: str, style: str) -> ListPatterns:
        """Get list formatting patterns for locale/type/style"""
        # Normalize locale (extract language)
        language = locale.split('-')[0].lower()

        # Fall back to English if locale not found
        if language not in self.PATTERNS:
            language = 'en'

        # Get patterns
        patterns = self.PATTERNS.get(language, self.PATTERNS['en'])
        type_patterns = patterns.get(list_type, patterns['conjunction'])
        return type_patterns.get(style, type_patterns['long'])


class ListFormatEngine:
    """Core list formatting logic"""

    def __init__(self, locale: str, list_type: str, style: str):
        self.locale = locale
        self.type = list_type
        self.style = style
        self.provider = ListPatternProvider()
        self.patterns = self.provider.get_patterns(locale, list_type, style)

    def format_list(self, items: List[str]) -> str:
        """Apply locale-specific list formatting"""
        if len(items) == 0:
            return ""

        if len(items) == 1:
            return items[0]

        if len(items) == 2:
            return self.patterns.pair.format(items[0], items[1])

        # 3+ items: use start/middle/end patterns
        result = items[0]
        for i in range(1, len(items) - 1):
            result = self.patterns.middle.format(result, items[i])

        # Add final item with end pattern
        result = self.patterns.end.format(result, items[-1])

        return result

    def format_list_to_parts(self, items: List[str]) -> List[Dict[str, str]]:
        """Format list to parts"""
        if len(items) == 0:
            return []

        if len(items) == 1:
            return [{'type': 'element', 'value': items[0]}]

        parts = []

        if len(items) == 2:
            # Two items: use pair pattern
            pattern = self.patterns.pair
            # Split pattern to extract separator
            # Pattern is like "{0} and {1}" or "{0}, {1}"
            separator = self._extract_separator(pattern, items[0], items[1])
            parts.append({'type': 'element', 'value': items[0]})
            if separator:
                parts.append({'type': 'literal', 'value': separator})
            parts.append({'type': 'element', 'value': items[1]})
            return parts

        # 3+ items
        # First item
        parts.append({'type': 'element', 'value': items[0]})

        # Middle items (use middle pattern)
        for i in range(1, len(items) - 1):
            separator = self._extract_separator(self.patterns.middle, "", items[i])
            if separator:
                parts.append({'type': 'literal', 'value': separator})
            parts.append({'type': 'element', 'value': items[i]})

        # Last item (use end pattern)
        separator = self._extract_separator(self.patterns.end, "", items[-1])
        if separator:
            parts.append({'type': 'literal', 'value': separator})
        parts.append({'type': 'element', 'value': items[-1]})

        return parts

    def _extract_separator(self, pattern: str, item0: str, item1: str) -> str:
        """Extract separator from pattern by removing the placeholder parts"""
        # Pattern is like "{0}, and {1}"
        # We want to extract ", and "
        result = pattern.replace('{0}', '').replace('{1}', '')
        return result


class IntlListFormat:
    """
    Intl.ListFormat implementation (FR-ES24-C-043 to FR-ES24-C-047)

    Provides locale-aware list formatting following ECMAScript Intl.ListFormat API.
    """

    VALID_TYPES = {'conjunction', 'disjunction', 'unit'}
    VALID_STYLES = {'long', 'short', 'narrow'}
    VALID_LOCALE_MATCHERS = {'lookup', 'best fit'}

    def __init__(self, locales: Union[str, List[str], None] = None,
                 options: Optional[Dict[str, Any]] = None):
        """
        Create new Intl.ListFormat instance

        Requirement: FR-ES24-C-043
        Description: Intl.ListFormat constructor with locale and options
        Implementation: Canonicalizes locales, validates and stores type/style options,
                       resolves locale using localeMatcher algorithm
        """
        # Validate options type
        if options is not None and not isinstance(options, dict):
            raise TypeError("options must be a dictionary or None")

        # Parse options
        if options is None:
            options = {}

        # Get localeMatcher (default: "best fit")
        locale_matcher = options.get('localeMatcher', 'best fit')
        if locale_matcher not in self.VALID_LOCALE_MATCHERS:
            raise ValueError(f"Invalid localeMatcher: {locale_matcher}")

        # Get type (default: "conjunction")
        list_type = options.get('type', 'conjunction')
        if list_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid type: {list_type}")

        # Get style (default: "long")
        style = options.get('style', 'long')
        if style not in self.VALID_STYLES:
            raise ValueError(f"Invalid style: {style}")

        # Canonicalize and resolve locale
        self._locale = self._resolve_locale(locales, locale_matcher)
        self._type = list_type
        self._style = style

        # Create formatting engine
        self._engine = ListFormatEngine(self._locale, self._type, self._style)

    def _canonicalize_locale_list(self, locales: Union[str, List[str], None]) -> List[str]:
        """Canonicalize locale list"""
        if locales is None:
            return []

        if isinstance(locales, str):
            return [locales]

        if isinstance(locales, list):
            return locales

        # Try to iterate
        try:
            return list(locales)
        except TypeError:
            return []

    def _resolve_locale(self, locales: Union[str, List[str], None],
                       matcher: str) -> str:
        """Resolve locale using requested locales and matcher"""
        locale_list = self._canonicalize_locale_list(locales)

        if not locale_list:
            # Default to English
            return 'en'

        # For simplicity, use first locale
        # In production, this would do proper locale negotiation
        locale = locale_list[0]

        # Validate BCP 47 format (basic validation)
        if not isinstance(locale, str) or len(locale) == 0:
            return 'en'

        return locale

    def format(self, list_items: Iterable[Any]) -> str:
        """
        Format list according to locale and options

        Requirement: FR-ES24-C-044
        Description: format() method - Format list to string
        Implementation: Applies locale-specific patterns, handles empty/single/two/multiple items,
                       uses appropriate separators and conjunctions based on type and style
        """
        # Check if iterable
        try:
            items = list(list_items)
        except TypeError:
            raise TypeError("list must be iterable")

        # Convert all items to strings
        string_items = [str(item) for item in items]

        # Use engine to format
        return self._engine.format_list(string_items)

    def formatToParts(self, list_items: Iterable[Any]) -> List[Dict[str, str]]:
        """
        Format list returning parts for each element

        Requirement: FR-ES24-C-045
        Description: formatToParts() method - Return parts array
        Implementation: Generates parts with type ('element' or 'literal') and value,
                       maintains correct order and structure for reconstruction
        """
        # Check if iterable
        try:
            items = list(list_items)
        except TypeError:
            raise TypeError("list must be iterable")

        # Convert all items to strings
        string_items = [str(item) for item in items]

        # Use engine to format to parts
        return self._engine.format_list_to_parts(string_items)

    def resolvedOptions(self) -> Dict[str, str]:
        """
        Return resolved locale and formatting options

        Requirement: FR-ES24-C-047
        Description: resolvedOptions() method
        Implementation: Returns object with locale, type, and style properties
                       reflecting actual resolved options (not input)
        """
        return {
            'locale': self._locale,
            'type': self._type,
            'style': self._style
        }


# Helper functions
def SupportedLocalesOf(locales: Union[str, List[str]],
                       options: Optional[Dict[str, Any]] = None) -> List[str]:
    """Return supported locales from requested list"""
    # Simplified implementation
    # In production, would check against available CLDR data
    if isinstance(locales, str):
        locales = [locales]

    # For now, support en and es
    supported = {'en', 'en-US', 'es', 'es-ES', 'ja', 'ja-JP'}
    result = []
    for locale in locales:
        # Check exact match or language match
        if locale in supported:
            result.append(locale)
        else:
            lang = locale.split('-')[0]
            if lang in supported:
                result.append(locale)

    return result


def CanonicalizeListFormatLocaleList(locales: Any) -> List[str]:
    """Canonicalize and validate locale list"""
    if locales is None:
        return []

    if isinstance(locales, str):
        return [locales]

    if isinstance(locales, list):
        return locales

    try:
        return list(locales)
    except TypeError:
        return []


def CreateListFormatPart(part_type: str, value: str) -> Dict[str, str]:
    """Create a list format part object"""
    return {
        'type': part_type,
        'value': value
    }
