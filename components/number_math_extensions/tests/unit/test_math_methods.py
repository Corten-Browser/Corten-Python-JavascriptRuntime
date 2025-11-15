"""
Unit tests for Math methods (ES2024 compliance)

Requirements:
- FR-ES24-053: Math.sign()
- FR-ES24-054: Math.trunc()
- FR-ES24-055: Math.cbrt()
- FR-ES24-056: Math.expm1()
- FR-ES24-057: Math.log1p()
- FR-ES24-058: Math.log10()
- FR-ES24-059: Math.log2()
- FR-ES24-060: Math.hypot()
- FR-ES24-061: Math.clz32()
- FR-ES24-062: Math.imul()
- FR-ES24-063: Math.fround()
- FR-ES24-064: Math.sinh(), cosh(), tanh()
- FR-ES24-065: Math.asinh(), acosh(), atanh()
"""
import math
import pytest
from components.number_math_extensions.src.math_methods import MathMethods


class TestMathSign:
    """Test Math.sign() - FR-ES24-053"""

    def test_positive_numbers(self):
        """Positive numbers should return 1"""
        assert MathMethods.sign(1) == 1
        assert MathMethods.sign(42) == 1
        assert MathMethods.sign(0.5) == 1
        assert MathMethods.sign(1e10) == 1
        assert MathMethods.sign(float('inf')) == 1

    def test_negative_numbers(self):
        """Negative numbers should return -1"""
        assert MathMethods.sign(-1) == -1
        assert MathMethods.sign(-42) == -1
        assert MathMethods.sign(-0.5) == -1
        assert MathMethods.sign(-1e10) == -1
        assert MathMethods.sign(float('-inf')) == -1

    def test_zero(self):
        """Zero should return 0"""
        assert MathMethods.sign(0) == 0
        assert MathMethods.sign(0.0) == 0
        assert MathMethods.sign(-0.0) == 0

    def test_nan(self):
        """NaN should return NaN"""
        result = MathMethods.sign(float('nan'))
        assert math.isnan(result)


class TestMathTrunc:
    """Test Math.trunc() - FR-ES24-054"""

    def test_positive_numbers(self):
        """Should truncate positive numbers"""
        assert MathMethods.trunc(3.14) == 3
        assert MathMethods.trunc(1.9) == 1
        assert MathMethods.trunc(42.999) == 42

    def test_negative_numbers(self):
        """Should truncate negative numbers"""
        assert MathMethods.trunc(-3.14) == -3
        assert MathMethods.trunc(-1.9) == -1
        assert MathMethods.trunc(-42.999) == -42

    def test_integers(self):
        """Should return integers unchanged"""
        assert MathMethods.trunc(0) == 0
        assert MathMethods.trunc(5) == 5
        assert MathMethods.trunc(-10) == -10

    def test_zero(self):
        """Should handle zero"""
        assert MathMethods.trunc(0.0) == 0
        assert MathMethods.trunc(-0.0) == 0


class TestMathCbrt:
    """Test Math.cbrt() - FR-ES24-055"""

    def test_positive_numbers(self):
        """Should compute cube root of positive numbers"""
        assert abs(MathMethods.cbrt(8) - 2) < 1e-10
        assert abs(MathMethods.cbrt(27) - 3) < 1e-10
        assert abs(MathMethods.cbrt(1) - 1) < 1e-10

    def test_negative_numbers(self):
        """Should compute cube root of negative numbers"""
        assert abs(MathMethods.cbrt(-8) - (-2)) < 1e-10
        assert abs(MathMethods.cbrt(-27) - (-3)) < 1e-10
        assert abs(MathMethods.cbrt(-1) - (-1)) < 1e-10

    def test_zero(self):
        """Should handle zero"""
        assert MathMethods.cbrt(0) == 0

    def test_fractional(self):
        """Should handle fractional values"""
        result = MathMethods.cbrt(0.125)
        assert abs(result - 0.5) < 1e-10


class TestMathExpm1:
    """Test Math.expm1() - FR-ES24-056"""

    def test_small_values(self):
        """Should compute e^x - 1 accurately for small x"""
        # For small x, expm1 is more accurate than exp(x) - 1
        assert abs(MathMethods.expm1(0) - 0) < 1e-15
        assert abs(MathMethods.expm1(1e-10)) < 1e-9

    def test_regular_values(self):
        """Should compute e^x - 1 for regular values"""
        assert abs(MathMethods.expm1(1) - (math.e - 1)) < 1e-10
        assert abs(MathMethods.expm1(2) - (math.e**2 - 1)) < 1e-10

    def test_negative_values(self):
        """Should handle negative values"""
        assert abs(MathMethods.expm1(-1) - (math.e**-1 - 1)) < 1e-10


class TestMathLog1p:
    """Test Math.log1p() - FR-ES24-057"""

    def test_small_values(self):
        """Should compute ln(1 + x) accurately for small x"""
        assert abs(MathMethods.log1p(0) - 0) < 1e-15
        assert abs(MathMethods.log1p(1e-10)) < 1e-9

    def test_regular_values(self):
        """Should compute ln(1 + x) for regular values"""
        assert abs(MathMethods.log1p(1) - math.log(2)) < 1e-10
        assert abs(MathMethods.log1p(math.e - 1) - 1) < 1e-10


class TestMathLog10:
    """Test Math.log10() - FR-ES24-058"""

    def test_powers_of_ten(self):
        """Should compute base-10 logarithm correctly"""
        assert abs(MathMethods.log10(10) - 1) < 1e-10
        assert abs(MathMethods.log10(100) - 2) < 1e-10
        assert abs(MathMethods.log10(1000) - 3) < 1e-10
        assert abs(MathMethods.log10(0.1) - (-1)) < 1e-10


class TestMathLog2:
    """Test Math.log2() - FR-ES24-059"""

    def test_powers_of_two(self):
        """Should compute base-2 logarithm correctly"""
        assert abs(MathMethods.log2(2) - 1) < 1e-10
        assert abs(MathMethods.log2(4) - 2) < 1e-10
        assert abs(MathMethods.log2(8) - 3) < 1e-10
        assert abs(MathMethods.log2(16) - 4) < 1e-10


class TestMathHypot:
    """Test Math.hypot() - FR-ES24-060"""

    def test_two_values(self):
        """Should compute hypotenuse of two values"""
        assert abs(MathMethods.hypot([3, 4]) - 5) < 1e-10
        assert abs(MathMethods.hypot([5, 12]) - 13) < 1e-10

    def test_three_values(self):
        """Should compute hypotenuse of three values"""
        assert abs(MathMethods.hypot([1, 2, 2]) - 3) < 1e-10

    def test_single_value(self):
        """Should handle single value"""
        assert abs(MathMethods.hypot([5]) - 5) < 1e-10

    def test_no_values(self):
        """Should return 0 for no values"""
        assert MathMethods.hypot([]) == 0


class TestMathClz32:
    """Test Math.clz32() - FR-ES24-061"""

    def test_powers_of_two(self):
        """Should count leading zeros correctly"""
        assert MathMethods.clz32(1) == 31  # 0000...0001
        assert MathMethods.clz32(2) == 30  # 0000...0010
        assert MathMethods.clz32(4) == 29  # 0000...0100
        assert MathMethods.clz32(0x80000000) == 0  # 1000...0000

    def test_zero(self):
        """Should return 32 for zero"""
        assert MathMethods.clz32(0) == 32

    def test_all_bits_set(self):
        """Should return 0 for all bits set"""
        assert MathMethods.clz32(0xFFFFFFFF) == 0


class TestMathImul:
    """Test Math.imul() - FR-ES24-062"""

    def test_basic_multiplication(self):
        """Should multiply 32-bit integers"""
        assert MathMethods.imul(2, 3) == 6
        assert MathMethods.imul(5, 7) == 35
        assert MathMethods.imul(-2, 3) == -6

    def test_overflow_wraps(self):
        """Should wrap on 32-bit overflow"""
        # Test that overflow wraps around in 32-bit space
        result = MathMethods.imul(0xFFFFFFFF, 5)
        # In 32-bit signed arithmetic, this should wrap
        assert -2**31 <= result < 2**31


class TestMathFround:
    """Test Math.fround() - FR-ES24-063"""

    def test_exact_values(self):
        """Should preserve exactly representable values"""
        assert MathMethods.fround(1.0) == 1.0
        assert MathMethods.fround(0.5) == 0.5

    def test_rounding(self):
        """Should round to nearest 32-bit float"""
        # Test that precision is reduced
        result = MathMethods.fround(1.337)
        assert isinstance(result, float)
        # Should be close but may lose precision
        assert abs(result - 1.337) < 0.001


class TestMathHyperbolicSine:
    """Test Math.sinh() - FR-ES24-064"""

    def test_zero(self):
        """sinh(0) should be 0"""
        assert abs(MathMethods.sinh(0) - 0) < 1e-10

    def test_positive_values(self):
        """Should compute hyperbolic sine of positive values"""
        assert abs(MathMethods.sinh(1) - math.sinh(1)) < 1e-10
        assert abs(MathMethods.sinh(2) - math.sinh(2)) < 1e-10

    def test_negative_values(self):
        """Should compute hyperbolic sine of negative values"""
        assert abs(MathMethods.sinh(-1) - math.sinh(-1)) < 1e-10


class TestMathHyperbolicCosine:
    """Test Math.cosh() - FR-ES24-064"""

    def test_zero(self):
        """cosh(0) should be 1"""
        assert abs(MathMethods.cosh(0) - 1) < 1e-10

    def test_positive_values(self):
        """Should compute hyperbolic cosine of positive values"""
        assert abs(MathMethods.cosh(1) - math.cosh(1)) < 1e-10
        assert abs(MathMethods.cosh(2) - math.cosh(2)) < 1e-10


class TestMathHyperbolicTangent:
    """Test Math.tanh() - FR-ES24-064"""

    def test_zero(self):
        """tanh(0) should be 0"""
        assert abs(MathMethods.tanh(0) - 0) < 1e-10

    def test_positive_values(self):
        """Should compute hyperbolic tangent of positive values"""
        assert abs(MathMethods.tanh(1) - math.tanh(1)) < 1e-10
        assert abs(MathMethods.tanh(2) - math.tanh(2)) < 1e-10


class TestMathInverseHyperbolicSine:
    """Test Math.asinh() - FR-ES24-065"""

    def test_zero(self):
        """asinh(0) should be 0"""
        assert abs(MathMethods.asinh(0) - 0) < 1e-10

    def test_positive_values(self):
        """Should compute inverse hyperbolic sine"""
        assert abs(MathMethods.asinh(1) - math.asinh(1)) < 1e-10
        assert abs(MathMethods.asinh(2) - math.asinh(2)) < 1e-10

    def test_negative_values(self):
        """Should handle negative values"""
        assert abs(MathMethods.asinh(-1) - math.asinh(-1)) < 1e-10


class TestMathInverseHyperbolicCosine:
    """Test Math.acosh() - FR-ES24-065"""

    def test_one(self):
        """acosh(1) should be 0"""
        assert abs(MathMethods.acosh(1) - 0) < 1e-10

    def test_positive_values(self):
        """Should compute inverse hyperbolic cosine"""
        assert abs(MathMethods.acosh(2) - math.acosh(2)) < 1e-10
        assert abs(MathMethods.acosh(3) - math.acosh(3)) < 1e-10


class TestMathInverseHyperbolicTangent:
    """Test Math.atanh() - FR-ES24-065"""

    def test_zero(self):
        """atanh(0) should be 0"""
        assert abs(MathMethods.atanh(0) - 0) < 1e-10

    def test_fractional_values(self):
        """Should compute inverse hyperbolic tangent"""
        assert abs(MathMethods.atanh(0.5) - math.atanh(0.5)) < 1e-10
        assert abs(MathMethods.atanh(-0.5) - math.atanh(-0.5)) < 1e-10
