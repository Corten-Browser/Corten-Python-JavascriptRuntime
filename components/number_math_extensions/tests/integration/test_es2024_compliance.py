"""
Integration tests for ES2024 Number and Math compliance

Tests integration between Number and Math methods, and validates
ES2024 specification compliance scenarios.
"""
import math
import pytest
from components.number_math_extensions.src.number_methods import NumberMethods
from components.number_math_extensions.src.number_constants import NumberConstants
from components.number_math_extensions.src.math_methods import MathMethods


class TestES2024NumberMathIntegration:
    """Integration tests for Number and Math methods"""

    def test_safe_integer_boundaries_with_math(self):
        """Verify safe integer boundaries work with Math operations"""
        max_safe = NumberConstants.MAX_SAFE_INTEGER

        # Safe integer should be detected
        assert NumberMethods.is_safe_integer(max_safe)

        # Math operations within safe range
        half = MathMethods.trunc(max_safe / 2)
        assert NumberMethods.is_safe_integer(half)

        # Beyond safe range
        beyond = max_safe + 1
        assert not NumberMethods.is_safe_integer(beyond)

    def test_number_parsing_with_math_operations(self):
        """Verify parsed numbers work with Math operations"""
        # Parse float and use in Math operations
        value = NumberMethods.parse_float("3.14159")
        truncated = MathMethods.trunc(value)
        assert truncated == 3

        # Parse int and use in Math operations
        binary_val = NumberMethods.parse_int("1010", 2)
        assert binary_val == 10
        sign = MathMethods.sign(binary_val)
        assert sign == 1

    def test_special_values_consistency(self):
        """Verify special value handling is consistent across methods"""
        # NaN handling
        nan = float('nan')
        assert NumberMethods.is_nan(nan)
        assert not NumberMethods.is_finite(nan)
        assert not NumberMethods.is_integer(nan)
        assert math.isnan(MathMethods.sign(nan))

        # Infinity handling
        inf = float('inf')
        assert NumberMethods.is_finite(inf) is False
        assert MathMethods.sign(inf) == 1
        assert MathMethods.sign(-inf) == -1

    def test_hyperbolic_function_chain(self):
        """Verify hyperbolic and inverse hyperbolic functions are inverses"""
        x = 1.5

        # sinh and asinh
        sinh_x = MathMethods.sinh(x)
        back_x = MathMethods.asinh(sinh_x)
        assert abs(back_x - x) < 1e-10

        # cosh and acosh
        cosh_x = MathMethods.cosh(x)
        back_x = MathMethods.acosh(cosh_x)
        assert abs(back_x - x) < 1e-10

        # tanh and atanh
        y = 0.5  # tanh range is (-1, 1)
        tanh_y = MathMethods.tanh(y)
        back_y = MathMethods.atanh(tanh_y)
        assert abs(back_y - y) < 1e-10

    def test_logarithm_consistency(self):
        """Verify logarithm methods are consistent"""
        x = 100

        # log10(100) should be 2
        assert abs(MathMethods.log10(x) - 2) < 1e-10

        # log2(8) should be 3
        assert abs(MathMethods.log2(8) - 3) < 1e-10

        # log1p for small values
        small = 1e-10
        log1p_val = MathMethods.log1p(small)
        assert abs(log1p_val - small) < 1e-15  # For small x, log(1+x) ≈ x

    def test_expm1_log1p_inverse(self):
        """Verify expm1 and log1p are approximate inverses"""
        x = 0.5

        # expm1(log1p(x)) should approximate x
        result = MathMethods.expm1(MathMethods.log1p(x))
        assert abs(result - x) < 1e-10

        # log1p(expm1(x)) should approximate x
        result = MathMethods.log1p(MathMethods.expm1(x))
        assert abs(result - x) < 1e-10

    def test_pythagorean_theorem_with_hypot(self):
        """Verify hypot implements Pythagorean theorem correctly"""
        # 3-4-5 triangle
        assert abs(MathMethods.hypot([3, 4]) - 5) < 1e-10

        # 5-12-13 triangle
        assert abs(MathMethods.hypot([5, 12]) - 13) < 1e-10

        # 3D case
        assert abs(MathMethods.hypot([2, 3, 6]) - 7) < 1e-10

    def test_32bit_operations_integration(self):
        """Verify 32-bit operations work together"""
        # imul produces 32-bit result
        result = MathMethods.imul(2, 3)
        assert result == 6

        # clz32 counts leading zeros
        zeros = MathMethods.clz32(result)
        assert zeros == 29  # 6 = 0b110

        # fround reduces to 32-bit float precision
        rounded = MathMethods.fround(3.14159265359)
        assert isinstance(rounded, float)

    def test_number_validation_workflow(self):
        """Verify typical number validation workflow"""
        def validate_number(value):
            """Typical validation pattern"""
            if NumberMethods.is_nan(value):
                return "NaN"
            if not NumberMethods.is_finite(value):
                return "Infinite"
            if NumberMethods.is_integer(value):
                if NumberMethods.is_safe_integer(value):
                    return "Safe Integer"
                return "Unsafe Integer"
            return "Float"

        assert validate_number(42) == "Safe Integer"
        assert validate_number(42.5) == "Float"
        assert validate_number(float('nan')) == "NaN"
        assert validate_number(float('inf')) == "Infinite"
        assert validate_number(2**53) == "Unsafe Integer"

    def test_precision_edge_cases(self):
        """Verify precision handling at edge cases"""
        # EPSILON should detect smallest differences
        epsilon = NumberConstants.EPSILON
        assert 1 + epsilon != 1
        assert 1 + (epsilon / 2) == 1

        # cbrt of perfect cubes
        assert abs(MathMethods.cbrt(8) - 2) < epsilon
        assert abs(MathMethods.cbrt(27) - 3) < epsilon

        # trunc should not introduce floating point errors
        assert MathMethods.trunc(42.999999999) == 42
        assert MathMethods.trunc(-42.999999999) == -42
