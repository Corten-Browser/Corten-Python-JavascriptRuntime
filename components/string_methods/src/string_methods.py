"""
StringMethods - ES2024 String.prototype method implementations

Implements:
- FR-ES24-011: String.prototype.at()
- FR-ES24-012: String.prototype.replaceAll()
- FR-ES24-013: String.prototype.matchAll()
- FR-ES24-014: String.prototype.trimStart()
- FR-ES24-015: String.prototype.trimEnd()
- FR-ES24-016: String.prototype.padStart()
- FR-ES24-017: String.prototype.padEnd()
- FR-ES24-018: String.prototype.codePointAt()
- FR-ES24-019: String.fromCodePoint()
- FR-ES24-020: String.raw()
"""

import re
from typing import List, Any, Optional, Iterator, Tuple


class StringMethods:
    """ES2024 String.prototype method implementations"""

    @staticmethod
    def at(string: str, index: int) -> Optional[str]:
        """
        Get character at index (supports negative indices)
        FR-ES24-011: String.prototype.at()

        Args:
            string: Source string
            index: Index (negative from end)

        Returns:
            Character at index or None (undefined in JS)
        """
        length = len(string)

        # Handle empty string
        if length == 0:
            return None

        # Convert negative index
        if index < 0:
            index = length + index

        # Check bounds
        if index < 0 or index >= length:
            return None

        return string[index]

    @staticmethod
    def trim_start(string: str) -> str:
        """
        Remove leading whitespace
        FR-ES24-014: String.prototype.trimStart()

        Args:
            string: Source string

        Returns:
            String with leading whitespace removed
        """
        return string.lstrip()

    @staticmethod
    def trim_end(string: str) -> str:
        """
        Remove trailing whitespace
        FR-ES24-015: String.prototype.trimEnd()

        Args:
            string: Source string

        Returns:
            String with trailing whitespace removed
        """
        return string.rstrip()

    @staticmethod
    def pad_start(string: str, target_length: int, pad_string: str = " ") -> str:
        """
        Pad string from start to target length
        FR-ES24-016: String.prototype.padStart()

        Args:
            string: Source string
            target_length: Target length
            pad_string: Padding string (default: space)

        Returns:
            Padded string
        """
        current_length = len(string)

        # No padding needed
        if current_length >= target_length:
            return string

        # Calculate padding needed
        padding_length = target_length - current_length

        # Handle empty pad_string
        if not pad_string:
            return string

        # Repeat pad_string to fill padding
        full_pad = pad_string * ((padding_length // len(pad_string)) + 1)

        # Truncate to exact padding length needed
        return full_pad[:padding_length] + string

    @staticmethod
    def pad_end(string: str, target_length: int, pad_string: str = " ") -> str:
        """
        Pad string from end to target length
        FR-ES24-017: String.prototype.padEnd()

        Args:
            string: Source string
            target_length: Target length
            pad_string: Padding string (default: space)

        Returns:
            Padded string
        """
        current_length = len(string)

        # No padding needed
        if current_length >= target_length:
            return string

        # Calculate padding needed
        padding_length = target_length - current_length

        # Handle empty pad_string
        if not pad_string:
            return string

        # Repeat pad_string to fill padding
        full_pad = pad_string * ((padding_length // len(pad_string)) + 1)

        # Truncate to exact padding length needed
        return string + full_pad[:padding_length]

    @staticmethod
    def replace_all(string: str, search: str, replace: str) -> str:
        """
        Replace all occurrences (not just first)
        FR-ES24-012: String.prototype.replaceAll()

        Args:
            string: Source string
            search: String to search
            replace: Replacement string

        Returns:
            String with all occurrences replaced
        """
        # Use str.replace which replaces all occurrences in Python
        return string.replace(search, replace)

    @staticmethod
    def match_all(string: str, regexp: str) -> Iterator[Tuple]:
        """
        Return iterator of all matches
        FR-ES24-013: String.prototype.matchAll()

        Args:
            string: Source string
            regexp: Regular expression pattern

        Returns:
            Iterator of match objects (tuples of groups)
        """
        # Compile pattern
        pattern = re.compile(regexp)

        # Find all matches
        for match in pattern.finditer(string):
            # Return full match + captured groups
            # match.group(0) is full match, match.groups() are captured groups
            if match.groups():
                yield (match.group(0),) + match.groups()
            else:
                yield (match.group(0),)

    @staticmethod
    def code_point_at(string: str, index: int) -> Optional[int]:
        """
        Get Unicode code point at index
        FR-ES24-018: String.prototype.codePointAt()

        Args:
            string: Source string
            index: Index

        Returns:
            Unicode code point or None
        """
        # Check bounds
        if index < 0 or index >= len(string):
            return None

        # Get character and convert to code point
        char = string[index]
        return ord(char)

    @staticmethod
    def from_code_point(code_points: List[int]) -> str:
        """
        Create string from Unicode code points
        FR-ES24-019: String.fromCodePoint()

        Args:
            code_points: Unicode code points

        Returns:
            String from code points
        """
        # Convert each code point to character
        return ''.join(chr(cp) for cp in code_points)

    @staticmethod
    def raw(template: List[str], substitutions: List[Any]) -> str:
        """
        Get raw string (no escape processing)
        FR-ES24-020: String.raw()

        Args:
            template: Template literal strings
            substitutions: Substitution values

        Returns:
            Raw string with substitutions
        """
        # Interleave template strings and substitutions
        result = []

        for i, part in enumerate(template):
            result.append(part)

            # Add substitution if available
            if i < len(substitutions):
                result.append(str(substitutions[i]))

        return ''.join(result)
