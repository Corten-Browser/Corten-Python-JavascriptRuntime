"""
Source location information for error reporting and debugging.

This module provides the SourceLocation dataclass which represents
a position in source code with file, line, column, and byte offset.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SourceLocation:
    """
    Source code location for error reporting and debugging.

    This immutable dataclass represents a specific position in source code,
    including the filename, line number, column number, and byte offset.

    Attributes:
        filename: Source file name
        line: Line number (1-indexed)
        column: Column number (1-indexed)
        offset: Byte offset from start of file

    Example:
        >>> location = SourceLocation(filename="main.js", line=10, column=5, offset=256)
        >>> print(location)
        SourceLocation(filename='main.js', line=10, column=5, offset=256)
    """

    filename: str
    line: int
    column: int
    offset: int

    def __post_init__(self):
        """Validate that line and column are positive integers."""
        if self.line < 1:
            raise ValueError(f"Line must be >= 1, got {self.line}")
        if self.column < 1:
            raise ValueError(f"Column must be >= 1, got {self.column}")
        if self.offset < 0:
            raise ValueError(f"Offset must be >= 0, got {self.offset}")
