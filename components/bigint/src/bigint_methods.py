"""
BigInt methods.

Implements BigInt prototype methods and static methods:
- toString(radix)
- valueOf()
- BigInt.asIntN(bits, bigint)
- BigInt.asUintN(bits, bigint)

Requirements:
- FR-P3-077: BigInt methods (toString, asIntN, asUintN)
"""

from bigint_value import BigIntValue, RangeError


def bigint_to_string(bigint, radix=10):
    """
    Convert BigInt to string in given radix.

    Args:
        bigint: BigIntValue
        radix: int (2-36), default 10

    Returns:
        str

    Throws:
        RangeError: If radix out of range
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("First argument must be BigInt")

    if radix < 2 or radix > 36:
        raise RangeError(f"radix must be between 2 and 36, got {radix}")

    # Python's int conversion handles all radixes
    if radix == 10:
        return str(bigint.value)
    else:
        # For other radixes, use Python's formatting
        value = bigint.value
        is_negative = value < 0
        if is_negative:
            value = -value

        # Convert to string in given radix
        if radix == 2:
            result = bin(value)[2:]  # Remove '0b' prefix
        elif radix == 8:
            result = oct(value)[2:]  # Remove '0o' prefix
        elif radix == 16:
            result = hex(value)[2:]  # Remove '0x' prefix
        else:
            # General base conversion
            result = _to_base(value, radix)

        return ('-' + result) if is_negative else result


def _to_base(num, base):
    """
    Convert number to string in given base.

    Args:
        num: int (non-negative)
        base: int (2-36)

    Returns:
        str
    """
    if num == 0:
        return '0'

    digits = '0123456789abcdefghijklmnopqrstuvwxyz'
    result = []

    while num > 0:
        result.append(digits[num % base])
        num //= base

    return ''.join(reversed(result))


def bigint_as_int_n(bits, bigint):
    """
    Wrap BigInt to N-bit signed integer.

    BigInt.asIntN(bits, bigint) wraps bigint to signed N-bit integer range.

    Args:
        bits: int - number of bits
        bigint: BigIntValue

    Returns:
        BigIntValue - wrapped to N-bit signed range

    Example:
        BigInt.asIntN(8, 128n) → -128n
        BigInt.asIntN(8, 127n) → 127n
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("Second argument must be BigInt")

    if not isinstance(bits, int) or bits < 0:
        raise TypeError("First argument must be non-negative integer")

    # Calculate the modulus (2^bits)
    modulus = 2 ** bits

    # Wrap to unsigned range first
    wrapped = bigint.value % modulus

    # Convert to signed range
    # If wrapped >= 2^(bits-1), it represents a negative number
    if wrapped >= 2 ** (bits - 1):
        wrapped -= modulus

    return BigIntValue(wrapped)


def bigint_as_uint_n(bits, bigint):
    """
    Wrap BigInt to N-bit unsigned integer.

    BigInt.asUintN(bits, bigint) wraps bigint to unsigned N-bit integer range.

    Args:
        bits: int - number of bits
        bigint: BigIntValue

    Returns:
        BigIntValue - wrapped to N-bit unsigned range

    Example:
        BigInt.asUintN(8, 256n) → 0n
        BigInt.asUintN(8, -1n) → 255n
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("Second argument must be BigInt")

    if not isinstance(bits, int) or bits < 0:
        raise TypeError("First argument must be non-negative integer")

    # Calculate the modulus (2^bits)
    modulus = 2 ** bits

    # Wrap to unsigned range
    wrapped = bigint.value % modulus

    return BigIntValue(wrapped)
