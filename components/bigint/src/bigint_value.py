"""
BigInt value type and constructor.

Implements BigInt arbitrary-precision integers using Python's built-in int.

Requirements:
- FR-P3-072: BigInt constructor from various types
- FR-P3-078: typeof bigint type checking
"""


class RangeError(Exception):
    """JavaScript RangeError equivalent."""
    pass


class BigIntValue:
    """
    BigInt internal representation.

    Uses Python's arbitrary-precision int as backing storage.
    """

    def __init__(self, value):
        """
        Create BigIntValue from Python integer.

        Args:
            value: Python int (arbitrary precision)
        """
        if not isinstance(value, int):
            raise TypeError(f"BigIntValue requires int, got {type(value).__name__}")
        self.value = value

    def typeof(self):
        """Return 'bigint' for typeof operator."""
        return "bigint"

    def value_of(self):
        """Return primitive BigInt value (self)."""
        return self

    def __repr__(self):
        """String representation for debugging."""
        return f"BigIntValue({self.value})"

    def __str__(self):
        """String conversion."""
        return str(self.value)


def BigInt(value):
    """
    BigInt constructor function.

    Converts value to BigInt. Cannot be called with 'new'.

    Args:
        value: number, string, boolean, or bigint

    Returns:
        BigIntValue

    Throws:
        TypeError: If called with 'new'
        RangeError: If number has fractional part, is Infinity, or NaN
        SyntaxError: If string is invalid
    """
    # Check if called with 'new' (would be set by runtime)
    if getattr(BigInt, '__new_target__', False):
        raise TypeError("BigInt is not a constructor")

    # Handle different input types
    if isinstance(value, BigIntValue):
        # BigInt(bigint) -> return equivalent BigInt
        return BigIntValue(value.value)

    elif isinstance(value, bool):
        # BigInt(true) -> 1n, BigInt(false) -> 0n
        return BigIntValue(1 if value else 0)

    elif isinstance(value, int):
        # BigInt(integer) -> direct conversion
        return BigIntValue(value)

    elif isinstance(value, float):
        # Check for special values
        if value != value:  # NaN check
            raise RangeError("Cannot convert NaN to BigInt")
        if value == float('inf') or value == float('-inf'):
            raise RangeError("Cannot convert infinity to BigInt")

        # Check for fractional part
        if value != int(value):
            raise RangeError("Cannot convert number with fractional part to BigInt")

        return BigIntValue(int(value))

    elif isinstance(value, str):
        # Parse string to BigInt
        value = value.strip()

        if not value:
            raise SyntaxError("Cannot convert empty string to BigInt")

        try:
            # Handle different bases
            if value.startswith('0x') or value.startswith('0X'):
                # Hexadecimal
                parsed = int(value, 16)
            elif value.startswith('0o') or value.startswith('0O'):
                # Octal
                parsed = int(value, 8)
            elif value.startswith('0b') or value.startswith('0B'):
                # Binary
                parsed = int(value, 2)
            else:
                # Decimal
                parsed = int(value, 10)

            return BigIntValue(parsed)

        except ValueError as e:
            raise SyntaxError(f"Invalid BigInt string: {value}") from e

    else:
        raise TypeError(f"Cannot convert {type(value).__name__} to BigInt")


# Flag to track if BigInt is called with 'new'
# In real implementation, this would be handled by the runtime
BigInt.__new_target__ = False
