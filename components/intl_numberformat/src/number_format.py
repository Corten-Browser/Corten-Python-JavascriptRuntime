"""
Intl.NumberFormat - Main implementation

Provides locale-aware number formatting with support for:
- Decimal, percent, currency, and unit styles
- Multiple notation types (standard, scientific, engineering, compact)
- Configurable rounding and grouping
- Range formatting
"""

from typing import Union, List, Dict, Any, Optional
import re
import math


class IntlNumberFormat:
    """
    Intl.NumberFormat implementation (FR-ES24-C-021 to FR-ES24-C-030)

    Provides locale-aware number formatting following ECMAScript Intl.NumberFormat API.
    """

    # ISO 4217 currency codes (subset for validation)
    VALID_CURRENCIES = {
        'USD', 'EUR', 'JPY', 'GBP', 'CHF', 'CNY', 'AUD', 'CAD',
        'NZD', 'SEK', 'NOK', 'DKK', 'PLN', 'CZK', 'HUF', 'INR',
        'BRL', 'MXN', 'ZAR', 'KRW', 'SGD', 'HKD', 'TWD', 'THB',
        'IDR', 'MYR', 'PHP', 'AED', 'SAR', 'ILS', 'RUB', 'TRY'
    }

    # Valid unit identifiers (subset)
    VALID_UNITS = {
        # Length
        'meter', 'kilometer', 'centimeter', 'millimeter', 'mile', 'yard', 'foot', 'inch',
        # Mass
        'kilogram', 'gram', 'milligram', 'pound', 'ounce',
        # Temperature
        'celsius', 'fahrenheit', 'kelvin',
        # Volume
        'liter', 'milliliter', 'gallon', 'quart', 'pint', 'cup',
        # Time
        'second', 'minute', 'hour', 'day', 'week', 'month', 'year',
        # Speed
        'meter-per-second', 'kilometer-per-hour', 'mile-per-hour',
        # Other
        'percent', 'bit', 'byte', 'kilobyte', 'megabyte', 'gigabyte'
    }

    def __init__(self, locales: Union[str, List[str], None] = None,
                 options: Optional[Dict[str, Any]] = None):
        """
        Initialize IntlNumberFormat (FR-ES24-C-021)

        Args:
            locales: BCP 47 language tag(s)
            options: Formatting options
        """
        if options is not None and not isinstance(options, dict):
            raise TypeError(f"Options must be a dictionary, not {type(options).__name__}")

        self._options = options or {}
        self._locale = self._resolve_locale(locales)
        self._resolved = self._resolve_options(self._locale, self._options)

    def _resolve_locale(self, locales: Union[str, List[str], None]) -> str:
        """Resolve locale from input."""
        if locales is None:
            return 'en-US'  # Default locale

        if isinstance(locales, str):
            locale_list = [locales]
        elif isinstance(locales, list):
            locale_list = locales
        else:
            raise TypeError("Locales must be string or list of strings")

        # Simple locale validation and canonicalization
        for locale in locale_list:
            if locale and self._is_valid_locale(locale):
                return self._canonicalize_locale(locale)

        # Fall back to default
        return 'en-US'

    def _is_valid_locale(self, locale: str) -> bool:
        """Basic locale validation."""
        if not isinstance(locale, str):
            return False

        # Basic BCP 47 pattern check
        pattern = r'^[a-zA-Z]{2,3}(-[a-zA-Z]{4})?(-[a-zA-Z]{2}|[0-9]{3})?(-u-.*)?$'
        return bool(re.match(pattern, locale))

    def _canonicalize_locale(self, locale: str) -> str:
        """Canonicalize locale to standard form."""
        parts = locale.split('-')
        if not parts:
            return 'en-US'

        # Language: lowercase
        canonical = [parts[0].lower()]

        # Script: titlecase (4 letters)
        # Region: uppercase (2 letters or 3 digits)
        for i, part in enumerate(parts[1:], 1):
            if i == 1 and len(part) == 4 and part.isalpha():
                # Script
                canonical.append(part.capitalize())
            elif len(part) == 2 and part.isalpha():
                # Region
                canonical.append(part.upper())
            elif len(part) == 3 and part.isdigit():
                # Numeric region
                canonical.append(part)
            else:
                # Keep as is (extensions, etc.)
                canonical.append(part)

        return'-'.join(canonical)

    def _resolve_options(self, locale: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve and validate options (FR-ES24-C-021)."""
        resolved = {}

        # Locale and numbering system
        resolved['locale'] = locale
        resolved['numberingSystem'] = options.get('numberingSystem', 'latn')

        # Style (FR-ES24-C-026)
        style = options.get('style', 'decimal')
        if style not in ('decimal', 'percent', 'currency', 'unit'):
            raise ValueError(f"Invalid style: {style}")
        resolved['style'] = style

        # Currency options (FR-ES24-C-027)
        if style == 'currency':
            currency = options.get('currency')
            if not currency:
                raise ValueError("Currency style requires currency option")
            if not isinstance(currency, str) or len(currency) != 3:
                raise ValueError(f"Invalid currency code: {currency}")
            if currency not in self.VALID_CURRENCIES:
                raise RangeError(f"Invalid ISO 4217 currency code: {currency}")

            resolved['currency'] = currency
            resolved['currencyDisplay'] = options.get('currencyDisplay', 'symbol')
            resolved['currencySign'] = options.get('currencySign', 'standard')

            # Currency-specific fraction defaults
            if currency == 'JPY':
                min_frac = options.get('minimumFractionDigits', 0)
                max_frac = options.get('maximumFractionDigits', 0)
            else:
                min_frac = options.get('minimumFractionDigits', 2)
                max_frac = options.get('maximumFractionDigits', 2)
        else:
            min_frac = options.get('minimumFractionDigits', 0)
            max_frac = options.get('maximumFractionDigits', 3)

        # Unit options (FR-ES24-C-028)
        if style == 'unit':
            unit = options.get('unit')
            if not unit:
                raise ValueError("Unit style requires unit option")
            if unit not in self.VALID_UNITS:
                raise RangeError(f"Invalid unit identifier: {unit}")

            resolved['unit'] = unit
            resolved['unitDisplay'] = options.get('unitDisplay', 'short')

        # Notation (FR-ES24-C-029)
        notation = options.get('notation', 'standard')
        if notation not in ('standard', 'scientific', 'engineering', 'compact'):
            raise ValueError(f"Invalid notation: {notation}")
        resolved['notation'] = notation

        if notation == 'compact':
            resolved['compactDisplay'] = options.get('compactDisplay', 'short')

        # Digit options
        resolved['minimumIntegerDigits'] = self._validate_int_range(
            options.get('minimumIntegerDigits', 1), 1, 21, 'minimumIntegerDigits')

        # Fraction digits
        resolved['minimumFractionDigits'] = self._validate_int_range(
            min_frac, 0, 20, 'minimumFractionDigits')
        resolved['maximumFractionDigits'] = self._validate_int_range(
            max_frac, 0, 20, 'maximumFractionDigits')

        if resolved['minimumFractionDigits'] > resolved['maximumFractionDigits']:
            raise RangeError(
                f"minimumFractionDigits ({resolved['minimumFractionDigits']}) "
                f"> maximumFractionDigits ({resolved['maximumFractionDigits']})")

        # Significant digits (optional)
        if 'minimumSignificantDigits' in options:
            resolved['minimumSignificantDigits'] = self._validate_int_range(
                options['minimumSignificantDigits'], 1, 21, 'minimumSignificantDigits')

        if 'maximumSignificantDigits' in options:
            resolved['maximumSignificantDigits'] = self._validate_int_range(
                options['maximumSignificantDigits'], 1, 21, 'maximumSignificantDigits')

        if ('minimumSignificantDigits' in resolved and
            'maximumSignificantDigits' in resolved):
            if resolved['minimumSignificantDigits'] > resolved['maximumSignificantDigits']:
                raise RangeError("minimumSignificantDigits > maximumSignificantDigits")

        # Other options
        use_grouping = options.get('useGrouping', 'auto')
        if isinstance(use_grouping, bool):
            resolved['useGrouping'] = use_grouping
        elif use_grouping in ('always', 'auto', 'min2'):
            resolved['useGrouping'] = use_grouping
        else:
            resolved['useGrouping'] = 'auto'

        resolved['signDisplay'] = options.get('signDisplay', 'auto')
        resolved['roundingMode'] = options.get('roundingMode', 'halfExpand')
        resolved['roundingPriority'] = options.get('roundingPriority', 'auto')
        resolved['roundingIncrement'] = options.get('roundingIncrement', 1)
        resolved['trailingZeroDisplay'] = options.get('trailingZeroDisplay', 'auto')

        return resolved

    def _validate_int_range(self, value: int, min_val: int, max_val: int, name: str) -> int:
        """Validate integer is in range."""
        if not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if value < min_val or value > max_val:
            raise RangeError(f"{name} must be between {min_val} and {max_val}")
        return value

    def format(self, value: Union[int, float]) -> str:
        """
        Format a number (FR-ES24-C-022)

        Args:
            value: Number to format

        Returns:
            Formatted number string
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"Value must be a number, not {type(value).__name__}")

        # Handle special values
        if math.isnan(value):
            return 'NaN'
        if math.isinf(value):
            return '-∞' if value < 0 else '∞'

        # Apply rounding
        rounded = self._apply_rounding(value)

        # Format based on style
        style = self._resolved['style']

        if style == 'percent':
            return self._format_percent(rounded)
        elif style == 'currency':
            return self._format_currency(rounded)
        elif style == 'unit':
            return self._format_unit(rounded)
        else:  # decimal
            return self._format_decimal(rounded)

    def _apply_rounding(self, value: float) -> float:
        """Apply rounding according to options."""
        mode = self._resolved.get('roundingMode', 'halfExpand')
        max_frac = self._resolved.get('maximumFractionDigits', 3)

        multiplier = 10 ** max_frac

        if mode == 'ceil':
            return math.ceil(value * multiplier) / multiplier
        elif mode == 'floor':
            return math.floor(value * multiplier) / multiplier
        elif mode == 'trunc':
            return math.trunc(value * multiplier) / multiplier
        elif mode == 'halfExpand':
            return round(value, max_frac)
        else:
            return round(value, max_frac)

    def _format_decimal(self, value: float) -> str:
        """Format as decimal number."""
        notation = self._resolved.get('notation', 'standard')

        if notation == 'scientific':
            return self._format_scientific(value)
        elif notation == 'engineering':
            return self._format_engineering(value)
        elif notation == 'compact':
            return self._format_compact(value)
        else:
            return self._format_standard(value)

    def _format_standard(self, value: float) -> str:
        """Format in standard notation."""
        sign = self._get_sign(value)
        abs_value = abs(value)

        # Format digits
        min_int = self._resolved.get('minimumIntegerDigits', 1)
        min_frac = self._resolved.get('minimumFractionDigits', 0)
        max_frac = self._resolved.get('maximumFractionDigits', 3)

        # Integer part
        int_part = int(abs_value)
        int_str = str(int_part).zfill(min_int)

        # Apply grouping
        if self._should_use_grouping():
            int_str = self._apply_grouping(int_str)

        # Fraction part
        frac = abs_value - int_part
        if max_frac > 0:
            frac_str = f"{frac:.{max_frac}f}".split('.')[1]
            # Ensure minimum fraction digits
            frac_str = frac_str.ljust(min_frac, '0')
            if frac_str and frac_str != '0' * len(frac_str):
                return f"{sign}{int_str}.{frac_str}"

        return f"{sign}{int_str}"

    def _get_sign(self, value: float) -> str:
        """Get sign prefix based on signDisplay option."""
        sign_display = self._resolved.get('signDisplay', 'auto')

        if value < 0:
            return '-'
        elif value == 0:
            if sign_display == 'exceptZero':
                return ''
            elif sign_display == 'always':
                return '+'
            else:
                return ''
        else:  # positive
            if sign_display in ('always', 'exceptZero'):
                return '+'
            else:
                return ''

    def _should_use_grouping(self) -> bool:
        """Check if grouping should be used."""
        use_grouping = self._resolved.get('useGrouping', 'auto')
        if isinstance(use_grouping, bool):
            return use_grouping
        return use_grouping in ('always', 'auto')

    def _apply_grouping(self, int_str: str) -> str:
        """Apply thousand grouping."""
        # US-style grouping: every 3 digits from right
        if len(int_str) <= 3:
            return int_str

        parts = []
        for i, digit in enumerate(reversed(int_str)):
            if i > 0 and i % 3 == 0:
                parts.append(',')
            parts.append(digit)

        return ''.join(reversed(parts))

    def _format_percent(self, value: float) -> str:
        """Format as percentage."""
        percent_value = value * 100
        formatted = self._format_standard(percent_value)
        return f"{formatted}%"

    def _format_currency(self, value: float) -> str:
        """Format as currency (FR-ES24-C-027)."""
        currency = self._resolved['currency']
        display = self._resolved.get('currencyDisplay', 'symbol')
        sign_type = self._resolved.get('currencySign', 'standard')

        # Get currency symbol
        symbols = {
            'USD': '$', 'EUR': '€', 'JPY': '¥', 'GBP': '£',
            'CHF': 'CHF', 'CNY': '¥', 'INR': '₹'
        }

        if display == 'code':
            symbol = currency
        elif display == 'name':
            names = {
                'USD': 'US dollars', 'EUR': 'euros', 'JPY': 'yen',
                'GBP': 'pounds', 'CHF': 'francs'
            }
            symbol = names.get(currency, currency)
        else:  # symbol or narrowSymbol
            symbol = symbols.get(currency, currency)

        # Format value
        formatted = self._format_standard(abs(value))

        # Handle negative with accounting format
        if value < 0 and sign_type == 'accounting':
            return f"({symbol}{formatted})"
        elif value < 0:
            return f"-{symbol}{formatted}"
        else:
            sign = self._get_sign(value)
            return f"{sign}{symbol}{formatted}"

    def _format_unit(self, value: float) -> str:
        """Format with unit (FR-ES24-C-028)."""
        unit = self._resolved['unit']
        display = self._resolved.get('unitDisplay', 'short')

        # Unit symbols/names
        units_short = {
            'meter': 'm', 'kilometer': 'km', 'centimeter': 'cm',
            'kilogram': 'kg', 'gram': 'g',
            'celsius': '°C', 'fahrenheit': '°F',
            'liter': 'L', 'milliliter': 'mL',
            'second': 's', 'minute': 'min', 'hour': 'hr'
        }

        units_long = {
            'meter': 'meters', 'kilometer': 'kilometers',
            'kilogram': 'kilograms', 'gram': 'grams',
            'celsius': 'degrees Celsius', 'fahrenheit': 'degrees Fahrenheit'
        }

        formatted = self._format_standard(value)

        if display == 'long':
            unit_str = units_long.get(unit, unit)
            return f"{formatted} {unit_str}"
        elif display == 'narrow':
            unit_str = units_short.get(unit, unit)[0] if units_short.get(unit) else unit[0]
            return f"{formatted}{unit_str}"
        else:  # short
            unit_str = units_short.get(unit, unit)
            return f"{formatted} {unit_str}"

    def _format_scientific(self, value: float) -> str:
        """Format in scientific notation."""
        if value == 0:
            return "0E0"

        exponent = int(math.floor(math.log10(abs(value))))
        mantissa = value / (10 ** exponent)

        min_frac = self._resolved.get('minimumFractionDigits', 0)
        max_frac = self._resolved.get('maximumFractionDigits', 3)

        mantissa_str = f"{mantissa:.{max_frac}f}"
        return f"{mantissa_str}E{exponent}"

    def _format_engineering(self, value: float) -> str:
        """Format in engineering notation (exponent multiple of 3)."""
        if value == 0:
            return "0E0"

        exponent = int(math.floor(math.log10(abs(value))))
        eng_exponent = (exponent // 3) * 3
        mantissa = value / (10 ** eng_exponent)

        max_frac = self._resolved.get('maximumFractionDigits', 3)
        mantissa_str = f"{mantissa:.{max_frac}f}"

        return f"{mantissa_str}E{eng_exponent}"

    def _format_compact(self, value: float) -> str:
        """Format in compact notation (FR-ES24-C-029)."""
        abs_value = abs(value)
        sign = '-' if value < 0 else ''

        if abs_value < 1000:
            return f"{sign}{abs_value:.0f}"
        elif abs_value < 1_000_000:
            return f"{sign}{abs_value/1000:.1f}K"
        elif abs_value < 1_000_000_000:
            return f"{sign}{abs_value/1_000_000:.1f}M"
        elif abs_value < 1_000_000_000_000:
            return f"{sign}{abs_value/1_000_000_000:.1f}B"
        else:
            return f"{sign}{abs_value/1_000_000_000_000:.1f}T"

    def formatToParts(self, value: Union[int, float]) -> List[Dict[str, str]]:
        """
        Format to parts (FR-ES24-C-023)

        Args:
            value: Number to format

        Returns:
            List of part objects with type and value
        """
        if not isinstance(value, (int, float)):
            raise TypeError(f"Value must be a number, not {type(value).__name__}")

        # Handle special values
        if math.isnan(value):
            return [{'type': 'nan', 'value': 'NaN'}]
        if math.isinf(value):
            parts = []
            if value < 0:
                parts.append({'type': 'minusSign', 'value': '-'})
            parts.append({'type': 'infinity', 'value': '∞'})
            return parts

        # Get formatted string and parse it
        formatted = self.format(value)
        return self._parse_to_parts(formatted, value)

    def _parse_to_parts(self, formatted: str, value: float) -> List[Dict[str, str]]:
        """Parse formatted string into parts."""
        parts = []
        style = self._resolved['style']

        # Simple parsing logic
        i = 0
        while i < len(formatted):
            char = formatted[i]

            if char in ('+', '-'):
                part_type = 'plusSign' if char == '+' else 'minusSign'
                parts.append({'type': part_type, 'value': char})
            elif char == '%':
                parts.append({'type': 'percentSign', 'value': char})
            elif char == ',':
                parts.append({'type': 'group', 'value': char})
            elif char == '.':
                parts.append({'type': 'decimal', 'value': char})
            elif char.isdigit():
                # Collect consecutive digits
                num = ''
                while i < len(formatted) and formatted[i].isdigit():
                    num += formatted[i]
                    i += 1
                i -= 1

                # Determine if integer or fraction
                has_decimal = any(p['type'] == 'decimal' for p in parts)
                part_type = 'fraction' if has_decimal else 'integer'
                parts.append({'type': part_type, 'value': num})
            elif style == 'currency' and char in ('$', '€', '¥', '£', '₹'):
                parts.append({'type': 'currency', 'value': char})
            elif style == 'currency':
                # Currency code or name
                code = ''
                while i < len(formatted) and formatted[i].isalpha():
                    code += formatted[i]
                    i += 1
                i -= 1
                if code:
                    parts.append({'type': 'currency', 'value': code})
            else:
                # Literal (spaces, unit symbols, etc.)
                literal = ''
                while i < len(formatted) and not formatted[i].isdigit():
                    if formatted[i] in ('+', '-', '%', ',', '.'):
                        break
                    if style == 'currency' and formatted[i] in ('$', '€', '¥', '£', '₹'):
                        break
                    literal += formatted[i]
                    i += 1
                i -= 1

                if literal.strip():
                    if style == 'unit':
                        parts.append({'type': 'unit', 'value': literal.strip()})
                    else:
                        parts.append({'type': 'literal', 'value': literal})

            i += 1

        return parts

    def formatRange(self, start: Union[int, float], end: Union[int, float]) -> str:
        """
        Format a number range (FR-ES24-C-024)

        Args:
            start: Start of range
            end: End of range

        Returns:
            Formatted range string
        """
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TypeError("Range values must be numbers")

        if start > end:
            raise RangeError("Start must be <= end")

        start_formatted = self.format(start)
        end_formatted = self.format(end)

        return f"{start_formatted} – {end_formatted}"

    def formatRangeToParts(self, start: Union[int, float],
                          end: Union[int, float]) -> List[Dict[str, str]]:
        """
        Format range to parts (FR-ES24-C-025)

        Args:
            start: Start of range
            end: End of range

        Returns:
            List of part objects with type, value, and source
        """
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
            raise TypeError("Range values must be numbers")

        if start > end:
            raise RangeError("Start must be <= end")

        start_parts = self.formatToParts(start)
        end_parts = self.formatToParts(end)

        # Add source attribute
        for part in start_parts:
            part['source'] = 'startRange'

        for part in end_parts:
            part['source'] = 'endRange'

        # Add separator
        separator = {'type': 'literal', 'value': ' – ', 'source': 'shared'}

        return start_parts + [separator] + end_parts

    def resolvedOptions(self) -> Dict[str, Any]:
        """
        Get resolved options (FR-ES24-C-030)

        Returns:
            Dictionary of resolved options
        """
        # Return a copy to prevent modification
        return self._resolved.copy()

    def __getattr__(self, name):
        """Prevent setting attributes after construction."""
        if name.startswith('_'):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
        raise AttributeError(f"can't set attribute '{name}'")

    def __setattr__(self, name, value):
        """Make formatter essentially immutable after construction."""
        if not hasattr(self, '_resolved'):
            # Allow setting during __init__
            super().__setattr__(name, value)
        elif name.startswith('_'):
            # Allow private attributes
            super().__setattr__(name, value)
        else:
            raise AttributeError(f"can't set attribute '{name}'")


class RangeError(Exception):
    """ECMAScript RangeError exception."""
    pass
