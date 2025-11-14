"""
ECMAScript type conversion functions.

This module implements the ECMAScript abstract operations for type
conversion: ToNumber, ToString, and ToBoolean. These functions follow
the ECMAScript specification semantics.
"""

import math
from .value import Value
from .type_check import NULL_VALUE


def ToNumber(value: Value) -> float:
    """
    Convert value to number per ECMAScript ToNumber abstract operation.

    Conversion rules (ECMAScript spec):
    - SMI: Return the numeric value as float
    - String: Parse the string as number
        - Empty string or whitespace: 0
        - Valid number: parsed value
        - Invalid: raise TypeError
    - Undefined: NaN
    - Null: 0
    - Object: Attempt conversion (simplified)

    Args:
        value: Value to convert

    Returns:
        Float representation of the value

    Raises:
        TypeError: If conversion is not possible

    Example:
        >>> v = Value.from_smi(42)
        >>> ToNumber(v)
        42.0
        >>> v2 = Value.from_object("123.45")
        >>> ToNumber(v2)
        123.45
    """
    # SMI values convert directly to float
    if value.is_smi():
        return float(value.to_smi())

    # Object values need type-specific conversion
    if value.is_object():
        obj = value.to_object()

        # Undefined -> NaN
        if obj is None:
            return math.nan

        # Null -> 0
        if isinstance(obj, type(NULL_VALUE)):
            return 0.0

        # String conversion
        if isinstance(obj, str):
            # Empty string or whitespace -> 0
            stripped = obj.strip()
            if not stripped:
                return 0.0

            # Try to parse as number
            try:
                return float(stripped)
            except ValueError as exc:
                raise TypeError(f"Cannot convert string '{obj}' to number") from exc

        # Other objects: attempt to convert via Python's float()
        try:
            return float(obj)
        except (ValueError, TypeError) as exc:
            raise TypeError(f"Cannot convert object to number: {exc}") from exc

    # Shouldn't reach here, but handle gracefully
    raise TypeError("Cannot convert value to number")


def ToString(value: Value) -> str:
    """
    Convert value to string per ECMAScript ToString abstract operation.

    Conversion rules (ECMAScript spec):
    - SMI: String representation of the number
    - String: Return unchanged
    - Undefined: "undefined"
    - Null: "null"
    - Object: String representation (simplified)

    Args:
        value: Value to convert

    Returns:
        String representation of the value

    Example:
        >>> v = Value.from_smi(42)
        >>> ToString(v)
        '42'
        >>> v2 = Value.from_object("Hello")
        >>> ToString(v2)
        'Hello'
    """
    # SMI values convert to string representation
    if value.is_smi():
        return str(value.to_smi())

    # Object values need type-specific conversion
    if value.is_object():
        obj = value.to_object()

        # Undefined -> "undefined"
        if obj is None:
            return "undefined"

        # Null -> "null"
        if isinstance(obj, type(NULL_VALUE)):
            return "null"

        # String -> return unchanged
        if isinstance(obj, str):
            return obj

        # Other objects: use Python's str()
        return str(obj)

    # Shouldn't reach here
    return ""


def ToBoolean(value: Value) -> bool:
    """
    Convert value to boolean per ECMAScript ToBoolean abstract operation.

    Conversion rules (ECMAScript spec):
    - Falsy values: 0, "", undefined, null -> False
    - Everything else -> True

    Args:
        value: Value to convert

    Returns:
        Boolean representation of the value

    Example:
        >>> v = Value.from_smi(0)
        >>> ToBoolean(v)
        False
        >>> v2 = Value.from_smi(42)
        >>> ToBoolean(v2)
        True
        >>> v3 = Value.from_object("")
        >>> ToBoolean(v3)
        False
    """
    # SMI: 0 is falsy, everything else is truthy
    if value.is_smi():
        return value.to_smi() != 0

    # Object values need type-specific conversion
    if value.is_object():
        obj = value.to_object()

        # Undefined is falsy
        if obj is None:
            return False

        # Null is falsy
        if isinstance(obj, type(NULL_VALUE)):
            return False

        # Empty string is falsy
        if isinstance(obj, str):
            return len(obj) > 0

        # All other objects are truthy (including empty lists/dicts)
        # This matches JavaScript semantics where objects are always truthy
        return True

    # Shouldn't reach here, default to False
    return False
