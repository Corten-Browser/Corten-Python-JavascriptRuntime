"""
Shared types, enums, and utilities for JavaScript runtime.

This package provides common types, error enums, source location tracking,
and utility functions used across all components of the JavaScript runtime.

Public API:
    - TypeTag: Enum for JavaScript value type tags
    - ErrorType: Enum for JavaScript error types
    - SourceLocation: Dataclass for source code locations
    - assert_type: Type assertion utility
    - format_error: Error formatting utility
"""

from .types import TypeTag, ErrorType
from .location import SourceLocation
from .utils import assert_type, format_error

__all__ = [
    "TypeTag",
    "ErrorType",
    "SourceLocation",
    "assert_type",
    "format_error",
]

__version__ = "0.1.0"
