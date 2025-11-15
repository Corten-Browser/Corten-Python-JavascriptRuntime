"""
BigInt arithmetic operations.

Implements all BigInt arithmetic: +, -, *, /, %, **

Requirements:
- FR-P3-073: BigInt arithmetic operations
- FR-P3-076: BigInt/Number mixing restrictions
"""

from bigint_value import BigIntValue, RangeError


def _validate_bigint_operand(operand, operation_name):
    """
    Validate operand is BigIntValue.

    Args:
        operand: Value to check
        operation_name: Name of operation for error message

    Throws:
        TypeError: If operand is not BigIntValue
    """
    if not isinstance(operand, BigIntValue):
        raise TypeError(
            f"Cannot mix BigInt and other types in {operation_name}"
        )


def bigint_add(a, b):
    """
    BigInt addition: a + b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
    """
    _validate_bigint_operand(a, "addition")
    _validate_bigint_operand(b, "addition")

    return BigIntValue(a.value + b.value)


def bigint_subtract(a, b):
    """
    BigInt subtraction: a - b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
    """
    _validate_bigint_operand(a, "subtraction")
    _validate_bigint_operand(b, "subtraction")

    return BigIntValue(a.value - b.value)


def bigint_multiply(a, b):
    """
    BigInt multiplication: a * b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
    """
    _validate_bigint_operand(a, "multiplication")
    _validate_bigint_operand(b, "multiplication")

    return BigIntValue(a.value * b.value)


def bigint_divide(a, b):
    """
    BigInt division: a / b

    Truncates toward zero (not floor division).

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
        RangeError: If division by zero
    """
    _validate_bigint_operand(a, "division")
    _validate_bigint_operand(b, "division")

    if b.value == 0:
        raise RangeError("Division by zero")

    # Python's // does floor division, but BigInt needs truncation toward zero
    # For positive results, they're the same
    # For negative results, we need to adjust
    quotient = a.value // b.value

    # Check if we need to adjust for truncation toward zero
    # If signs differ and there's a remainder, floor division went one too far
    if (a.value < 0) != (b.value < 0) and a.value % b.value != 0:
        quotient += 1

    return BigIntValue(quotient)


def bigint_remainder(a, b):
    """
    BigInt remainder: a % b

    JavaScript remainder preserves sign of dividend (truncation-based).
    Python's % is modulo (floor-based), so we need to adjust.

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
        RangeError: If division by zero
    """
    _validate_bigint_operand(a, "remainder")
    _validate_bigint_operand(b, "remainder")

    if b.value == 0:
        raise RangeError("Division by zero")

    # JavaScript remainder: sign follows dividend
    # Use: a % b = a - (a / b) * b where / truncates toward zero
    quotient = bigint_divide(a, b)
    remainder = a.value - (quotient.value * b.value)

    return BigIntValue(remainder)


def bigint_exponentiate(base, exponent):
    """
    BigInt exponentiation: base ** exponent

    Args:
        base: BigIntValue
        exponent: BigIntValue

    Returns:
        BigIntValue

    Throws:
        TypeError: If mixing BigInt and Number
        RangeError: If exponent is negative
    """
    _validate_bigint_operand(base, "exponentiation")
    _validate_bigint_operand(exponent, "exponentiation")

    if exponent.value < 0:
        raise RangeError("Exponent must be non-negative for BigInt")

    return BigIntValue(base.value ** exponent.value)


def bigint_negate(a):
    """
    Unary negation: -a

    Args:
        a: BigIntValue

    Returns:
        BigIntValue
    """
    if not isinstance(a, BigIntValue):
        raise TypeError("Operand must be BigInt")

    return BigIntValue(-a.value)


def bigint_unary_plus(a):
    """
    Unary plus: +a

    BigInt does not support unary plus (throws TypeError).

    Args:
        a: BigIntValue

    Throws:
        TypeError: Always (BigInt doesn't support unary +)
    """
    raise TypeError("Cannot convert BigInt to number using unary +")
