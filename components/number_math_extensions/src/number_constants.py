"""
Number constant properties for ES2024 compliance

Requirements:
- FR-ES24-048: Number.EPSILON
- FR-ES24-049: Number.MAX_SAFE_INTEGER
- FR-ES24-050: Number.MIN_SAFE_INTEGER
"""
import sys


class NumberConstants:
    """Number constant properties per ES2024 specification"""

    # FR-ES24-048: Number.EPSILON
    # Smallest representable difference between 1 and the next representable number
    EPSILON = 2.220446049250313e-16

    # FR-ES24-049: Number.MAX_SAFE_INTEGER
    # Maximum safe integer value (2^53 - 1)
    # Integers beyond this may lose precision in IEEE 754 double precision
    MAX_SAFE_INTEGER = 9007199254740991  # 2^53 - 1

    # FR-ES24-050: Number.MIN_SAFE_INTEGER
    # Minimum safe integer value (-(2^53 - 1))
    MIN_SAFE_INTEGER = -9007199254740991  # -(2^53 - 1)
