"""
Type checking functions for JavaScript values.

This module provides functions to check the type of JavaScript values
represented by the Value class. These functions implement JavaScript's
type checking semantics.
"""

from .value import Value


# Sentinel value for JavaScript null (distinct from Python None/undefined)
class _NullSentinel:
    """Sentinel class for JavaScript null value."""

    def __repr__(self) -> str:
        return "null"


NULL_VALUE = _NullSentinel()


def IsNumber(value: Value) -> bool:
    """
    Check if value is number (SMI or boxed double).

    In this implementation, we consider SMI values as numbers.
    Boxed doubles would also be numbers but are not yet implemented.

    Args:
        value: Value to check

    Returns:
        True if value is a number, False otherwise

    Example:
        >>> v = Value.from_smi(42)
        >>> IsNumber(v)
        True
    """
    # For now, only SMI values are numbers
    # Future: check for boxed double objects
    return value.is_smi()


def IsString(value: Value) -> bool:
    """
    Check if value is string.

    Args:
        value: Value to check

    Returns:
        True if value is a string, False otherwise

    Example:
        >>> v = Value.from_object("Hello")
        >>> IsString(v)
        True
    """
    if not value.is_object():
        return False

    # Extract object and check if it's a string
    try:
        obj = value.to_object()
        return isinstance(obj, str)
    except (TypeError, RuntimeError):
        return False


def IsObject(value: Value) -> bool:
    """
    Check if value is object (excluding strings and primitives).

    In JavaScript, strings are primitives, not objects. This function
    returns True for dictionaries, lists, and other object types, but
    False for strings and SMI values.

    Args:
        value: Value to check

    Returns:
        True if value is an object (not string/primitive), False otherwise

    Example:
        >>> v = Value.from_object({"key": "value"})
        >>> IsObject(v)
        True
        >>> v2 = Value.from_object("string")
        >>> IsObject(v2)
        False
    """
    if not value.is_object():
        return False

    # Extract object and check it's not a string or special value
    try:
        obj = value.to_object()
        # Strings are primitives in JavaScript, not objects
        if isinstance(obj, str):
            return False
        # None represents undefined, not an object
        if obj is None:
            return False
        # NULL_VALUE represents null, not an object in our type system
        if isinstance(obj, _NullSentinel):
            return False
        # Everything else is an object
        return True
    except (TypeError, RuntimeError):
        return False


def IsUndefined(value: Value) -> bool:
    """
    Check if value is undefined.

    We use Python's None to represent JavaScript's undefined value.

    Args:
        value: Value to check

    Returns:
        True if value is undefined, False otherwise

    Example:
        >>> v = Value.from_object(None)
        >>> IsUndefined(v)
        True
    """
    if not value.is_object():
        return False

    try:
        obj = value.to_object()
        return obj is None
    except (TypeError, RuntimeError):
        return False


def IsNull(value: Value) -> bool:
    """
    Check if value is null.

    We use a special NULL_VALUE sentinel to represent JavaScript's null
    value, which is distinct from undefined (represented by Python's None).

    Args:
        value: Value to check

    Returns:
        True if value is null, False otherwise

    Example:
        >>> v = Value.from_object(NULL_VALUE)
        >>> IsNull(v)
        True
    """
    if not value.is_object():
        return False

    try:
        obj = value.to_object()
        return isinstance(obj, _NullSentinel)
    except (TypeError, RuntimeError):
        return False
