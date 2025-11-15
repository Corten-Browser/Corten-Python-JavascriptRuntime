"""
Number static method implementations for ES2024 compliance

Requirements:
- FR-ES24-044: Number.isFinite()
- FR-ES24-045: Number.isInteger()
- FR-ES24-046: Number.isNaN()
- FR-ES24-047: Number.isSafeInteger()
- FR-ES24-051: Number.parseFloat()
- FR-ES24-052: Number.parseInt()
"""
import math
from typing import Any
from .number_constants import NumberConstants


class NumberMethods:
    """Number static method implementations per ES2024 specification"""

    @staticmethod
    def is_finite(value: Any) -> bool:
        """
        Check if value is a finite number (not Infinity or NaN)

        FR-ES24-044: Number.isFinite()

        Args:
            value: Value to check

        Returns:
            True if value is a finite number, False otherwise

        Unlike global isFinite(), does not coerce non-numbers to numbers.
        """
        # Must be numeric type (int or float), not bool
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False

        # Must not be infinity or NaN
        return not (math.isinf(value) or math.isnan(value))

    @staticmethod
    def is_integer(value: Any) -> bool:
        """
        Check if value is an integer

        FR-ES24-045: Number.isInteger()

        Args:
            value: Value to check

        Returns:
            True if value is an integer, False otherwise

        Unlike global isinstance(x, int), also accepts float values
        that are mathematically integers (e.g., 1.0).
        """
        # Must be numeric type (int or float), not bool
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False

        # Must be finite
        if math.isinf(value) or math.isnan(value):
            return False

        # Check if mathematically an integer
        return value == int(value)

    @staticmethod
    def is_nan(value: Any) -> bool:
        """
        Check if value is NaN (more reliable than global isNaN)

        FR-ES24-046: Number.isNaN()

        Args:
            value: Value to check

        Returns:
            True if value is NaN, False otherwise

        Unlike global isNaN(), does not coerce non-numbers to numbers.
        This makes it more reliable for strict NaN detection.
        """
        # Must be numeric type (int or float), not bool
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return False

        return math.isnan(value)

    @staticmethod
    def is_safe_integer(value: Any) -> bool:
        """
        Check if value is a safe integer

        FR-ES24-047: Number.isSafeInteger()

        Args:
            value: Value to check

        Returns:
            True if value is a safe integer, False otherwise

        Safe integers are integers between -(2^53 - 1) and 2^53 - 1 inclusive.
        These can be exactly represented in IEEE 754 double precision.
        """
        # Must be an integer
        if not NumberMethods.is_integer(value):
            return False

        # Must be within safe integer range
        return (NumberConstants.MIN_SAFE_INTEGER <= value <=
                NumberConstants.MAX_SAFE_INTEGER)

    @staticmethod
    def parse_float(string: str) -> float:
        """
        Parse float from string

        FR-ES24-051: Number.parseFloat()

        Args:
            string: String to parse

        Returns:
            Parsed float value, or NaN if parsing fails

        Parses the string and returns a floating point number.
        Leading whitespace is ignored. Parsing stops at the first
        character that cannot be part of a number.
        """
        if not isinstance(string, str):
            return float('nan')

        # Strip leading whitespace
        string = string.lstrip()

        if not string:
            return float('nan')

        # Try to parse as much as possible
        # Find the longest valid numeric prefix
        i = 0
        has_digit = False
        has_dot = False
        has_e = False

        # Handle sign
        if i < len(string) and string[i] in '+-':
            i += 1

        # Parse digits and decimal point
        while i < len(string):
            ch = string[i]
            if ch.isdigit():
                has_digit = True
                i += 1
            elif ch == '.' and not has_dot and not has_e:
                has_dot = True
                i += 1
            elif ch in 'eE' and not has_e and has_digit:
                has_e = True
                i += 1
                # Handle exponent sign
                if i < len(string) and string[i] in '+-':
                    i += 1
            else:
                break

        if not has_digit:
            return float('nan')

        try:
            return float(string[:i])
        except ValueError:
            return float('nan')

    @staticmethod
    def parse_int(string: str, radix: int) -> int:
        """
        Parse integer from string with specified radix

        FR-ES24-052: Number.parseInt()

        Args:
            string: String to parse
            radix: Number base (2-36)

        Returns:
            Parsed integer value, or NaN if parsing fails

        Parses the string as an integer in the specified base.
        Leading whitespace is ignored. Parsing stops at the first
        character that is not a valid digit in the specified base.
        """
        if not isinstance(string, str):
            return float('nan')

        # Validate radix
        if not isinstance(radix, int) or radix < 2 or radix > 36:
            return float('nan')

        # Strip leading whitespace
        string = string.lstrip()

        if not string:
            return float('nan')

        # Handle sign
        sign = 1
        i = 0
        if string[i] in '+-':
            if string[i] == '-':
                sign = -1
            i += 1

        if i >= len(string):
            return float('nan')

        # Valid digits for this radix
        valid_digits = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[:radix]

        # Parse digits
        result = 0
        found_digit = False

        while i < len(string):
            ch = string[i].upper()
            if ch in valid_digits:
                digit_value = valid_digits.index(ch)
                result = result * radix + digit_value
                found_digit = True
                i += 1
            else:
                break

        if not found_digit:
            return float('nan')

        return sign * result
