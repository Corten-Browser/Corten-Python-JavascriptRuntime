"""
Type tags and error types for JavaScript runtime.

This module defines the fundamental type system and error types
used throughout the JavaScript runtime engine.
"""

from enum import Enum, auto


class TypeTag(Enum):
    """
    JavaScript value type tags for tagged pointer representation.

    These tags are used to distinguish between different JavaScript
    value types in the runtime's tagged pointer system.
    """

    SMI = auto()  # Small integer (31-bit signed)
    OBJECT = auto()  # JavaScript object
    STRING = auto()  # String
    NUMBER = auto()  # Heap-allocated number (double)
    BOOLEAN = auto()  # Boolean (true/false)
    UNDEFINED = auto()  # Undefined value
    NULL = auto()  # Null value
    FUNCTION = auto()  # Function object
    ARRAY = auto()  # Array object


class ErrorType(Enum):
    """
    JavaScript error types per ECMAScript specification.

    These error types correspond to the standard JavaScript error
    constructors defined in the ECMAScript specification.
    """

    SYNTAX_ERROR = auto()  # SyntaxError
    TYPE_ERROR = auto()  # TypeError
    REFERENCE_ERROR = auto()  # ReferenceError
    RANGE_ERROR = auto()  # RangeError
    ERROR = auto()  # Generic Error
