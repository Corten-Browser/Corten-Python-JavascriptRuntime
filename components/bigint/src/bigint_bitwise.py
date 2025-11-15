"""
BigInt bitwise operations.

Implements all BigInt bitwise operations: &, |, ^, ~, <<, >>

Requirements:
- FR-P3-074: BigInt bitwise operations
"""

from bigint_value import BigIntValue


def _validate_bigint_operand(operand, operation_name):
    """Validate operand is BigIntValue."""
    if not isinstance(operand, BigIntValue):
        raise TypeError(
            f"Cannot use {operation_name} with non-BigInt operand"
        )


def bigint_and(a, b):
    """
    Bitwise AND: a & b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "bitwise AND")
    _validate_bigint_operand(b, "bitwise AND")

    return BigIntValue(a.value & b.value)


def bigint_or(a, b):
    """
    Bitwise OR: a | b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "bitwise OR")
    _validate_bigint_operand(b, "bitwise OR")

    return BigIntValue(a.value | b.value)


def bigint_xor(a, b):
    """
    Bitwise XOR: a ^ b

    Args:
        a: BigIntValue
        b: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "bitwise XOR")
    _validate_bigint_operand(b, "bitwise XOR")

    return BigIntValue(a.value ^ b.value)


def bigint_not(a):
    """
    Bitwise NOT: ~a

    Implements two's complement: ~x = -(x + 1)

    Args:
        a: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "bitwise NOT")

    # Python's ~ operator works correctly for arbitrary precision
    return BigIntValue(~a.value)


def bigint_left_shift(a, shift_amount):
    """
    Left shift: a << b

    Args:
        a: BigIntValue
        shift_amount: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "left shift")
    _validate_bigint_operand(shift_amount, "left shift")

    # If shift amount is negative, shift right instead
    if shift_amount.value < 0:
        return bigint_signed_right_shift(a, BigIntValue(-shift_amount.value))

    # Python handles arbitrary precision left shift
    return BigIntValue(a.value << shift_amount.value)


def bigint_signed_right_shift(a, shift_amount):
    """
    Signed right shift: a >> b

    Preserves sign (arithmetic shift).

    Args:
        a: BigIntValue
        shift_amount: BigIntValue

    Returns:
        BigIntValue
    """
    _validate_bigint_operand(a, "right shift")
    _validate_bigint_operand(shift_amount, "right shift")

    # If shift amount is negative, shift left instead
    if shift_amount.value < 0:
        return bigint_left_shift(a, BigIntValue(-shift_amount.value))

    # Python's >> preserves sign for negative numbers
    return BigIntValue(a.value >> shift_amount.value)


def bigint_unsigned_right_shift(a, b):
    """
    Unsigned right shift: a >>> b

    BigInt does NOT support unsigned right shift.
    This always throws TypeError.

    Args:
        a: BigIntValue
        b: BigIntValue

    Throws:
        TypeError: Always (BigInt doesn't support >>>)
    """
    raise TypeError("BigInts have no unsigned right shift, use >> instead")
