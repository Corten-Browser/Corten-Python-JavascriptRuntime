"""
BigInt coercion and type checking.

Implements BigInt type coercion rules and validation.

Requirements:
- FR-P3-076: BigInt/Number mixing restrictions
- FR-P3-078: typeof bigint type checking
- FR-P3-079: BigInt coercion rules
"""

from bigint_value import BigIntValue


def bigint_typeof(value):
    """
    Get typeof for BigInt.

    Args:
        value: BigIntValue

    Returns:
        str: 'bigint'
    """
    if isinstance(value, BigIntValue):
        return 'bigint'
    else:
        # For other types, would need type system integration
        raise TypeError("Expected BigInt")


def bigint_to_boolean(bigint):
    """
    Convert BigInt to Boolean.

    Rules:
    - 0n → false
    - Any other BigInt → true

    Args:
        bigint: BigIntValue

    Returns:
        bool
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("Expected BigInt")

    return bigint.value != 0


def bigint_to_string_coerce(bigint):
    """
    Coerce BigInt to String.

    Args:
        bigint: BigIntValue

    Returns:
        str
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("Expected BigInt")

    return str(bigint.value)


def bigint_to_number_explicit(bigint):
    """
    Explicitly convert BigInt to Number.

    Note: May lose precision for large BigInts.

    Args:
        bigint: BigIntValue

    Returns:
        int or float
    """
    if not isinstance(bigint, BigIntValue):
        raise TypeError("Expected BigInt")

    # Convert to Python number (may lose precision)
    return bigint.value


def validate_bigint_only_operation(a, b):
    """
    Validate that both operands are BigInt.

    Used to enforce "no mixing BigInt and Number" rule.

    Args:
        a: Value to check
        b: Value to check

    Throws:
        TypeError: If either operand is not BigInt
    """
    if not isinstance(a, BigIntValue):
        raise TypeError(
            f"Cannot mix BigInt and other types in operation"
        )
    if not isinstance(b, BigIntValue):
        raise TypeError(
            f"Cannot mix BigInt and other types in operation"
        )
