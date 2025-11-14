"""
Utility functions for type assertions and error formatting.

This module provides utility functions for runtime type checking
and formatting error messages with source location information.
"""

from typing import Any, Optional
from .types import TypeTag, ErrorType
from .location import SourceLocation


def assert_type(
    value: Any, expected_tag: TypeTag, message: Optional[str] = None
) -> None:
    """
    Assert that a value has the expected type tag.

    This function checks if a value has a 'tag' attribute matching
    the expected TypeTag. If not, it raises a TypeError with an
    appropriate error message.

    Args:
        value: Value to check (must have a 'tag' attribute)
        expected_tag: Expected TypeTag value
        message: Optional custom error message

    Raises:
        TypeError: If value doesn't have expected tag
        AttributeError: If value doesn't have a 'tag' attribute

    Example:
        >>> from types import TypeTag
        >>> class Value:
        ...     def __init__(self, tag):
        ...         self.tag = tag
        >>> value = Value(TypeTag.STRING)
        >>> assert_type(value, TypeTag.STRING)  # OK
        >>> assert_type(value, TypeTag.NUMBER)  # Raises TypeError
    """
    if not hasattr(value, "tag"):
        raise AttributeError(f"Value has no 'tag' attribute: {type(value).__name__}")

    if value.tag != expected_tag:
        if message:
            raise TypeError(message)
        raise TypeError(
            f"Type mismatch: expected {expected_tag.name}, got {value.tag.name}"
        )


def format_error(
    error_type: ErrorType, message: str, location: Optional[SourceLocation] = None
) -> str:
    """
    Format an error message with source location information.

    This function formats an error message in a JavaScript-style format,
    optionally including source location information (filename, line, column).

    Args:
        error_type: Type of error (from ErrorType enum)
        message: Error message
        location: Optional source location where error occurred

    Returns:
        Formatted error string

    Example:
        >>> from types import ErrorType
        >>> from location import SourceLocation
        >>> format_error(ErrorType.SYNTAX_ERROR, "Unexpected token")
        'SyntaxError: Unexpected token'
        >>> loc = SourceLocation("test.js", 10, 5, 128)
        >>> format_error(ErrorType.SYNTAX_ERROR, "Unexpected token", loc)
        'SyntaxError: Unexpected token at test.js:10:5'
    """
    # Map ErrorType to JavaScript error name
    error_names = {
        ErrorType.SYNTAX_ERROR: "SyntaxError",
        ErrorType.TYPE_ERROR: "TypeError",
        ErrorType.REFERENCE_ERROR: "ReferenceError",
        ErrorType.RANGE_ERROR: "RangeError",
        ErrorType.ERROR: "Error",
    }

    error_name = error_names.get(error_type, "Error")

    if location:
        return f"{error_name}: {message} at {location.filename}:{location.line}:{location.column}"
    return f"{error_name}: {message}"
