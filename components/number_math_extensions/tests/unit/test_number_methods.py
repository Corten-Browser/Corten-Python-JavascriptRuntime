"""
Unit tests for Number methods (ES2024 compliance)

Requirements:
- FR-ES24-044: Number.isFinite()
- FR-ES24-045: Number.isInteger()
- FR-ES24-046: Number.isNaN()
- FR-ES24-047: Number.isSafeInteger()
- FR-ES24-051: Number.parseFloat()
- FR-ES24-052: Number.parseInt()
"""
import math
import pytest
from components.number_math_extensions.src.number_methods import NumberMethods


class TestNumberIsFinite:
    """Test Number.isFinite() - FR-ES24-044"""

    def test_finite_numbers(self):
        """Finite numbers should return True"""
        assert NumberMethods.is_finite(0) is True
        assert NumberMethods.is_finite(1) is True
        assert NumberMethods.is_finite(-1) is True
        assert NumberMethods.is_finite(42.5) is True
        assert NumberMethods.is_finite(-273.15) is True
        assert NumberMethods.is_finite(1e10) is True
        assert NumberMethods.is_finite(-1e-10) is True

    def test_infinity_returns_false(self):
        """Infinity should return False"""
        assert NumberMethods.is_finite(float('inf')) is False
        assert NumberMethods.is_finite(float('-inf')) is False
        assert NumberMethods.is_finite(math.inf) is False
        assert NumberMethods.is_finite(-math.inf) is False

    def test_nan_returns_false(self):
        """NaN should return False"""
        assert NumberMethods.is_finite(float('nan')) is False
        assert NumberMethods.is_finite(math.nan) is False

    def test_non_numbers_return_false(self):
        """Non-numbers should return False (not coerced)"""
        assert NumberMethods.is_finite("123") is False
        assert NumberMethods.is_finite(None) is False
        assert NumberMethods.is_finite(True) is False
        assert NumberMethods.is_finite([]) is False
        assert NumberMethods.is_finite({}) is False


class TestNumberIsInteger:
    """Test Number.isInteger() - FR-ES24-045"""

    def test_integers_return_true(self):
        """Integers should return True"""
        assert NumberMethods.is_integer(0) is True
        assert NumberMethods.is_integer(1) is True
        assert NumberMethods.is_integer(-1) is True
        assert NumberMethods.is_integer(42) is True
        assert NumberMethods.is_integer(-273) is True
        assert NumberMethods.is_integer(1000000) is True

    def test_floats_as_integers_return_true(self):
        """Floats with integer values should return True"""
        assert NumberMethods.is_integer(1.0) is True
        assert NumberMethods.is_integer(-1.0) is True
        assert NumberMethods.is_integer(0.0) is True
        assert NumberMethods.is_integer(42.0) is True

    def test_non_integers_return_false(self):
        """Non-integer numbers should return False"""
        assert NumberMethods.is_integer(0.5) is False
        assert NumberMethods.is_integer(1.1) is False
        assert NumberMethods.is_integer(-0.1) is False
        assert NumberMethods.is_integer(math.pi) is False

    def test_infinity_and_nan_return_false(self):
        """Infinity and NaN should return False"""
        assert NumberMethods.is_integer(float('inf')) is False
        assert NumberMethods.is_integer(float('-inf')) is False
        assert NumberMethods.is_integer(float('nan')) is False

    def test_non_numbers_return_false(self):
        """Non-numbers should return False"""
        assert NumberMethods.is_integer("123") is False
        assert NumberMethods.is_integer(None) is False
        assert NumberMethods.is_integer(True) is False


class TestNumberIsNaN:
    """Test Number.isNaN() - FR-ES24-046"""

    def test_nan_returns_true(self):
        """NaN should return True"""
        assert NumberMethods.is_nan(float('nan')) is True
        assert NumberMethods.is_nan(math.nan) is True
        # In Python, 0.0/0.0 raises ZeroDivisionError, use float('nan') instead
        nan_value = float('nan')
        assert NumberMethods.is_nan(nan_value) is True

    def test_numbers_return_false(self):
        """Regular numbers should return False"""
        assert NumberMethods.is_nan(0) is False
        assert NumberMethods.is_nan(1) is False
        assert NumberMethods.is_nan(-1) is False
        assert NumberMethods.is_nan(42.5) is False
        assert NumberMethods.is_nan(float('inf')) is False
        assert NumberMethods.is_nan(float('-inf')) is False

    def test_non_numbers_return_false(self):
        """Non-numbers should return False (stricter than global isNaN)"""
        assert NumberMethods.is_nan("NaN") is False
        assert NumberMethods.is_nan("123") is False
        assert NumberMethods.is_nan(None) is False
        assert NumberMethods.is_nan(True) is False
        assert NumberMethods.is_nan(undefined) is False if 'undefined' in dir() else True


class TestNumberIsSafeInteger:
    """Test Number.isSafeInteger() - FR-ES24-047"""

    def test_safe_integers_return_true(self):
        """Safe integers should return True"""
        assert NumberMethods.is_safe_integer(0) is True
        assert NumberMethods.is_safe_integer(1) is True
        assert NumberMethods.is_safe_integer(-1) is True
        assert NumberMethods.is_safe_integer(42) is True
        assert NumberMethods.is_safe_integer(1000) is True

    def test_boundary_safe_integers(self):
        """Boundary safe integers should return True"""
        max_safe = 9007199254740991  # 2^53 - 1
        min_safe = -9007199254740991  # -(2^53 - 1)
        assert NumberMethods.is_safe_integer(max_safe) is True
        assert NumberMethods.is_safe_integer(min_safe) is True

    def test_unsafe_integers_return_false(self):
        """Unsafe integers (beyond 2^53-1) should return False"""
        max_safe = 9007199254740991
        min_safe = -9007199254740991
        assert NumberMethods.is_safe_integer(max_safe + 1) is False
        assert NumberMethods.is_safe_integer(min_safe - 1) is False
        assert NumberMethods.is_safe_integer(2**53) is False
        assert NumberMethods.is_safe_integer(-(2**53)) is False

    def test_non_integers_return_false(self):
        """Non-integers should return False"""
        assert NumberMethods.is_safe_integer(0.5) is False
        assert NumberMethods.is_safe_integer(1.1) is False
        assert NumberMethods.is_safe_integer(float('inf')) is False
        assert NumberMethods.is_safe_integer(float('nan')) is False

    def test_non_numbers_return_false(self):
        """Non-numbers should return False"""
        assert NumberMethods.is_safe_integer("123") is False
        assert NumberMethods.is_safe_integer(None) is False


class TestNumberParseFloat:
    """Test Number.parseFloat() - FR-ES24-051"""

    def test_parse_valid_floats(self):
        """Should parse valid float strings"""
        assert NumberMethods.parse_float("3.14") == 3.14
        assert NumberMethods.parse_float("0.5") == 0.5
        assert NumberMethods.parse_float("-273.15") == -273.15
        assert NumberMethods.parse_float("1e10") == 1e10
        assert NumberMethods.parse_float("1.5e-10") == 1.5e-10

    def test_parse_integers(self):
        """Should parse integer strings as floats"""
        assert NumberMethods.parse_float("42") == 42.0
        assert NumberMethods.parse_float("-10") == -10.0
        assert NumberMethods.parse_float("0") == 0.0

    def test_parse_with_leading_whitespace(self):
        """Should ignore leading whitespace"""
        assert NumberMethods.parse_float("  3.14") == 3.14
        assert NumberMethods.parse_float("\t42") == 42.0
        assert NumberMethods.parse_float("\n1.5") == 1.5

    def test_parse_stops_at_invalid_char(self):
        """Should parse up to first invalid character"""
        assert NumberMethods.parse_float("3.14abc") == 3.14
        assert NumberMethods.parse_float("42 is the answer") == 42.0

    def test_parse_invalid_returns_nan(self):
        """Should return NaN for invalid input"""
        result = NumberMethods.parse_float("abc")
        assert math.isnan(result)
        result = NumberMethods.parse_float("")
        assert math.isnan(result)


class TestNumberParseInt:
    """Test Number.parseInt() - FR-ES24-052"""

    def test_parse_decimal(self):
        """Should parse decimal integers"""
        assert NumberMethods.parse_int("42", 10) == 42
        assert NumberMethods.parse_int("-10", 10) == -10
        assert NumberMethods.parse_int("0", 10) == 0
        assert NumberMethods.parse_int("123", 10) == 123

    def test_parse_binary(self):
        """Should parse binary integers"""
        assert NumberMethods.parse_int("1010", 2) == 10
        assert NumberMethods.parse_int("11111111", 2) == 255

    def test_parse_octal(self):
        """Should parse octal integers"""
        assert NumberMethods.parse_int("777", 8) == 511
        assert NumberMethods.parse_int("100", 8) == 64

    def test_parse_hexadecimal(self):
        """Should parse hexadecimal integers"""
        assert NumberMethods.parse_int("FF", 16) == 255
        assert NumberMethods.parse_int("1A", 16) == 26
        assert NumberMethods.parse_int("DEADBEEF", 16) == 3735928559

    def test_parse_various_radixes(self):
        """Should parse various radixes (2-36)"""
        assert NumberMethods.parse_int("Z", 36) == 35
        assert NumberMethods.parse_int("10", 3) == 3
        assert NumberMethods.parse_int("10", 5) == 5

    def test_parse_with_leading_whitespace(self):
        """Should ignore leading whitespace"""
        assert NumberMethods.parse_int("  42", 10) == 42
        assert NumberMethods.parse_int("\t10", 16) == 16

    def test_parse_stops_at_invalid_digit(self):
        """Should parse up to first invalid digit for radix"""
        assert NumberMethods.parse_int("123abc", 10) == 123
        assert NumberMethods.parse_int("12", 2) == 1  # '2' invalid for binary

    def test_parse_invalid_returns_nan(self):
        """Should return NaN for invalid input"""
        result = NumberMethods.parse_int("abc", 10)
        assert math.isnan(result)
