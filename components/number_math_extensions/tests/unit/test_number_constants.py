"""
Unit tests for Number constants (ES2024 compliance)

Requirements:
- FR-ES24-048: Number.EPSILON
- FR-ES24-049: Number.MAX_SAFE_INTEGER
- FR-ES24-050: Number.MIN_SAFE_INTEGER
"""
import pytest
from components.number_math_extensions.src.number_constants import NumberConstants


class TestNumberConstants:
    """Test Number constant properties"""

    def test_epsilon_value(self):
        """EPSILON should be 2.220446049250313e-16 - FR-ES24-048"""
        assert NumberConstants.EPSILON == 2.220446049250313e-16

    def test_epsilon_is_smallest_difference(self):
        """EPSILON should be smallest representable difference between 1 and next number"""
        # 1 + EPSILON should not equal 1
        assert 1 + NumberConstants.EPSILON != 1
        # 1 + (EPSILON / 2) should equal 1 (rounding)
        assert 1 + (NumberConstants.EPSILON / 2) == 1

    def test_max_safe_integer_value(self):
        """MAX_SAFE_INTEGER should be 9007199254740991 - FR-ES24-049"""
        assert NumberConstants.MAX_SAFE_INTEGER == 9007199254740991
        assert NumberConstants.MAX_SAFE_INTEGER == 2**53 - 1

    def test_max_safe_integer_accuracy(self):
        """MAX_SAFE_INTEGER should be largest integer representable accurately"""
        max_safe = NumberConstants.MAX_SAFE_INTEGER
        # max_safe should be exact
        assert float(max_safe) == max_safe
        # max_safe + 1 should be exact
        assert float(max_safe + 1) == max_safe + 1
        # max_safe + 2 may lose precision (depending on float implementation)
        # This is the boundary of safe integers

    def test_min_safe_integer_value(self):
        """MIN_SAFE_INTEGER should be -9007199254740991 - FR-ES24-050"""
        assert NumberConstants.MIN_SAFE_INTEGER == -9007199254740991
        assert NumberConstants.MIN_SAFE_INTEGER == -(2**53 - 1)

    def test_min_safe_integer_accuracy(self):
        """MIN_SAFE_INTEGER should be smallest integer representable accurately"""
        min_safe = NumberConstants.MIN_SAFE_INTEGER
        # min_safe should be exact
        assert float(min_safe) == min_safe
        # min_safe - 1 should be exact
        assert float(min_safe - 1) == min_safe - 1

    def test_safe_integer_symmetry(self):
        """MIN and MAX should be symmetric"""
        assert NumberConstants.MAX_SAFE_INTEGER == -NumberConstants.MIN_SAFE_INTEGER
