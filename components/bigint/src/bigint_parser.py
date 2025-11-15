"""
BigInt literal parser.

Parses BigInt literals: 123n, 0xFFn, 0o77n, 0b1010n

Requirements:
- FR-P3-071: BigInt literals (123n, 0xFFn, etc.)
"""

from bigint_value import BigIntValue


def parse_bigint_literal(literal_str):
    """
    Parse BigInt literal string.

    Args:
        literal_str: String like '123n', '0xFFn', '0o77n', '0b1010n'

    Returns:
        BigIntValue if valid BigInt literal, None otherwise

    Throws:
        SyntaxError: If has 'n' suffix but invalid format
    """
    literal_str = literal_str.strip()

    # Check if it ends with 'n' (BigInt suffix)
    if not literal_str.endswith('n'):
        return None

    # Remove 'n' suffix
    num_str = literal_str[:-1]

    # Handle negative numbers
    is_negative = num_str.startswith('-')
    if is_negative:
        num_str = num_str[1:]

    try:
        # Parse based on prefix
        if num_str.startswith('0x') or num_str.startswith('0X'):
            # Hexadecimal
            value = int(num_str, 16)
        elif num_str.startswith('0o') or num_str.startswith('0O'):
            # Octal
            value = int(num_str, 8)
        elif num_str.startswith('0b') or num_str.startswith('0B'):
            # Binary
            value = int(num_str, 2)
        else:
            # Decimal
            value = int(num_str, 10)

        # Apply sign
        if is_negative:
            value = -value

        return BigIntValue(value)

    except ValueError as e:
        raise SyntaxError(f"Invalid BigInt literal: {literal_str}") from e
