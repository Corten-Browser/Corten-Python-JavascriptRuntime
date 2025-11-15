"""
BigInt comparison operations.

Implements all BigInt comparison: ===, ==, <, <=, >, >=

Requirements:
- FR-P3-075: BigInt comparison operators
"""

from bigint_value import BigIntValue


def _get_numeric_value(value):
    """
    Get numeric value for comparison.

    Args:
        value: BigIntValue, int, float, or str

    Returns:
        Numeric value for comparison
    """
    if isinstance(value, BigIntValue):
        return value.value
    elif isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        # Try to parse as number
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return None
    return None


def bigint_strict_equal(a, b):
    """
    Strict equality: a === b

    Only true if both are BigInt with same value.

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        bool
    """
    if not isinstance(a, BigIntValue) or not isinstance(b, BigIntValue):
        return False

    return a.value == b.value


def bigint_equal(a, b):
    """
    Abstract equality: a == b

    Compares mathematical values (can compare BigInt to Number).

    Args:
        a: BigIntValue or other type
        b: Any type

    Returns:
        bool
    """
    a_val = _get_numeric_value(a)
    b_val = _get_numeric_value(b)

    if a_val is None or b_val is None:
        return False

    return a_val == b_val


def bigint_less_than(a, b):
    """
    Less than: a < b

    Args:
        a: BigIntValue or other type
        b: Any type

    Returns:
        bool
    """
    a_val = _get_numeric_value(a)
    b_val = _get_numeric_value(b)

    if a_val is None or b_val is None:
        return False

    return a_val < b_val


def bigint_less_than_or_equal(a, b):
    """
    Less than or equal: a <= b

    Args:
        a: BigIntValue or other type
        b: Any type

    Returns:
        bool
    """
    a_val = _get_numeric_value(a)
    b_val = _get_numeric_value(b)

    if a_val is None or b_val is None:
        return False

    return a_val <= b_val


def bigint_greater_than(a, b):
    """
    Greater than: a > b

    Args:
        a: BigIntValue or other type
        b: Any type

    Returns:
        bool
    """
    a_val = _get_numeric_value(a)
    b_val = _get_numeric_value(b)

    if a_val is None or b_val is None:
        return False

    return a_val > b_val


def bigint_greater_than_or_equal(a, b):
    """
    Greater than or equal: a >= b

    Args:
        a: BigIntValue or other type
        b: Any type

    Returns:
        bool
    """
    a_val = _get_numeric_value(a)
    b_val = _get_numeric_value(b)

    if a_val is None or b_val is None:
        return False

    return a_val >= b_val
