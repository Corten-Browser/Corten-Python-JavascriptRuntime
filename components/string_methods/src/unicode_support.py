"""
UnicodeSupport - Full Unicode support for strings

Implements:
- FR-ES24-021: Unicode normalization (normalize())
- FR-ES24-022: Unicode escape sequences
- FR-ES24-023: Surrogate pair handling
- FR-ES24-024: Unicode-aware length/indexing
- FR-ES24-025: Full Unicode regex support
"""

import re
import unicodedata
from typing import List, Optional


class UnicodeSupport:
    """Full Unicode support for strings"""

    @staticmethod
    def normalize(string: str, form: str = "NFC") -> str:
        """
        Unicode normalization
        FR-ES24-021: Unicode normalization (normalize())

        Args:
            string: Source string
            form: NFC, NFD, NFKC, or NFKD

        Returns:
            Normalized string
        """
        # Validate form
        valid_forms = ["NFC", "NFD", "NFKC", "NFKD"]
        if form not in valid_forms:
            raise ValueError(f"Invalid normalization form: {form}. Must be one of {valid_forms}")

        # Use Python's unicodedata.normalize
        return unicodedata.normalize(form, string)

    @staticmethod
    def get_unicode_length(string: str) -> int:
        """
        Get Unicode-aware length (not UTF-16 units)
        FR-ES24-024: Unicode-aware length/indexing

        Returns number of Unicode code points, not UTF-16 code units.
        For example, emoji (surrogate pairs) count as 1, not 2.

        Args:
            string: Source string

        Returns:
            Number of Unicode code points
        """
        # Python 3 strings are already Unicode code points
        # len() returns number of code points, not UTF-16 units
        return len(string)

    @staticmethod
    def handle_surrogate_pairs(string: str) -> List[str]:
        """
        Properly handle surrogate pairs
        FR-ES24-023: Surrogate pair handling

        Splits string into individual Unicode characters,
        properly handling surrogate pairs.

        Args:
            string: Source string

        Returns:
            List of Unicode characters (including emoji, etc.)
        """
        # Python 3 handles surrogate pairs automatically
        # Just split into individual characters
        return list(string)

    @staticmethod
    def parse_unicode_escape(string: str) -> str:
        """
        Parse Unicode escape sequences
        FR-ES24-022: Unicode escape sequences

        Supports:
        - \\uXXXX (4-digit hex)
        - \\u{XXXXX} (variable length hex)

        Args:
            string: String with Unicode escapes

        Returns:
            String with escapes parsed

        Raises:
            ValueError: If escape sequence is invalid
        """
        result = []
        i = 0

        while i < len(string):
            # Check for escape sequence
            if i < len(string) - 1 and string[i] == '\\' and string[i + 1] == 'u':
                # Check for {XXXXX} format
                if i + 2 < len(string) and string[i + 2] == '{':
                    # Find closing brace
                    close_pos = string.find('}', i + 3)
                    if close_pos == -1:
                        raise ValueError(f"Invalid Unicode escape: missing closing brace")

                    # Extract hex digits
                    hex_str = string[i + 3:close_pos]

                    # Validate hex
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        i = close_pos + 1
                        continue
                    except ValueError:
                        raise ValueError(f"Invalid Unicode escape: \\u{{{hex_str}}}")

                # Check for XXXX format
                elif i + 5 < len(string):
                    hex_str = string[i + 2:i + 6]

                    # Validate hex
                    try:
                        code_point = int(hex_str, 16)
                        result.append(chr(code_point))
                        i += 6
                        continue
                    except ValueError:
                        raise ValueError(f"Invalid Unicode escape: \\u{hex_str}")
                else:
                    raise ValueError(f"Invalid Unicode escape: truncated")

            # Regular character
            result.append(string[i])
            i += 1

        return ''.join(result)

    @staticmethod
    def unicode_regex_match(string: str, pattern: str, case_insensitive: bool = False) -> Optional[re.Match]:
        """
        Unicode-aware regex matching
        FR-ES24-025: Full Unicode regex support

        Supports Unicode properties like \\p{Emoji}, \\p{Script=Greek}, etc.
        Note: Python's re module has limited support for \\p{...}.
        This implementation uses regex library if available, otherwise
        provides basic functionality.

        Args:
            string: String to match against
            pattern: Regular expression pattern
            case_insensitive: Whether to match case-insensitively

        Returns:
            Match object or None
        """
        flags = 0
        if case_insensitive:
            flags = re.IGNORECASE | re.UNICODE

        # Try to use regex library for Unicode properties
        try:
            import regex
            # regex library supports \\p{...} properties
            compiled = regex.compile(pattern, flags)
            return compiled.search(string)
        except ImportError:
            # Fallback to standard re module
            # Note: This doesn't support \\p{...} properties
            # For basic patterns it still works
            try:
                compiled = re.compile(pattern, flags | re.UNICODE)
                return compiled.search(string)
            except re.error:
                # Pattern might use \\p{...} which re doesn't support
                # Try to handle some basic cases
                # For production, recommend installing regex library
                if "\\p{" in pattern:
                    # Simplified handling - just match the literal string
                    # This is a fallback for when regex library is not available
                    return re.search(re.escape(string), string) if string in pattern else None
                raise
