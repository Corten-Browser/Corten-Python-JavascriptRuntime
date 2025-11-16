"""
String Edge Cases Implementation - ES2024 Wave D

Implements complete String.prototype edge case handling:
- FR-ES24-D-006: String.prototype methods with surrogate pairs
- FR-ES24-D-007: String.prototype.at() edge cases
- FR-ES24-D-008: String iterator edge cases
- FR-ES24-D-009: Unicode property escapes in RegExp

Performance targets: All operations <500µs
"""

from typing import Optional, List, Dict, Any
import regex  # For Unicode property support (not standard re)


class StringEdgeCases:
    """
    Complete String edge case handling for ES2024 Wave D.

    Handles surrogate pairs, negative indices, Unicode code points,
    and Unicode property escapes correctly.
    """

    # Unicode property pattern cache for performance
    _property_cache: Dict[str, Any] = {}

    @staticmethod
    def at(string: str, index: int) -> Dict[str, Optional[Any]]:
        """
        Get character at index (supports negative indices).

        Implements String.prototype.at() with full edge case handling:
        - Negative indices count from end
        - Out-of-bounds indices return None
        - Surrogate pairs handled correctly (returns full code point)

        Requirement: FR-ES24-D-007

        Args:
            string: Input string
            index: Character index (negative indices count from end)

        Returns:
            Dictionary with 'result' (character or None) and 'code_point' (int or None)

        Raises:
            TypeError: If string is not a str or index is not an int

        Examples:
            >>> StringEdgeCases.at("hello", 1)
            {'result': 'e', 'code_point': 101}
            >>> StringEdgeCases.at("hello", -1)
            {'result': 'o', 'code_point': 111}
            >>> StringEdgeCases.at("hello", 100)
            {'result': None, 'code_point': None}
            >>> StringEdgeCases.at("😀", 0)
            {'result': '😀', 'code_point': 128512}
        """
        # Validate inputs
        if not isinstance(string, str):
            raise TypeError("First argument must be a string")
        if not isinstance(index, int):
            raise TypeError("Second argument must be an integer")

        # Handle empty string
        if len(string) == 0:
            return {"result": None, "code_point": None}

        # Convert negative index to positive
        # Python's negative indexing works on code points, which is what we want
        actual_index = index
        if index < 0:
            actual_index = len(string) + index

        # Check bounds
        if actual_index < 0 or actual_index >= len(string):
            return {"result": None, "code_point": None}

        # Get character at index
        # Python strings are already code-point based, so this handles surrogate pairs correctly
        char = string[actual_index]
        code_point = ord(char)

        return {
            "result": char,
            "code_point": code_point
        }

    @staticmethod
    def code_point_at(string: str, index: int) -> Dict[str, Any]:
        """
        Get Unicode code point at index.

        Returns the Unicode code point value at the given index.
        Handles surrogate pairs correctly by returning the full code point.

        Requirement: FR-ES24-D-006

        Args:
            string: Input string
            index: Character index (must be non-negative)

        Returns:
            Dictionary with 'code_point' (int or None) and 'is_surrogate_pair' (bool)

        Raises:
            TypeError: If string is not a str or index is not an int
            ValueError: If index is negative

        Examples:
            >>> StringEdgeCases.code_point_at("hello", 0)
            {'code_point': 104, 'is_surrogate_pair': False}
            >>> StringEdgeCases.code_point_at("😀", 0)
            {'code_point': 128512, 'is_surrogate_pair': True}
        """
        # Validate inputs
        if not isinstance(string, str):
            raise TypeError("First argument must be a string")
        if not isinstance(index, int):
            raise TypeError("Second argument must be an integer")
        if index < 0:
            raise ValueError("Index must be non-negative")

        # Handle empty string or out of bounds
        if index >= len(string):
            return {"code_point": None, "is_surrogate_pair": False}

        # Get character at index
        char = string[index]
        code_point = ord(char)

        # Determine if this is a surrogate pair
        # In UTF-16, surrogate pairs represent code points >= 0x10000
        # Python represents these as single characters with code point > 0xFFFF
        # However, unpaired surrogates (0xD800-0xDFFF) are NOT proper pairs
        is_surrogate_pair = code_point >= 0x10000

        # Check for unpaired surrogates (malformed)
        # These are in the range 0xD800-0xDFFF and should NOT be marked as pairs
        if 0xD800 <= code_point <= 0xDFFF:
            is_surrogate_pair = False

        return {
            "code_point": code_point,
            "is_surrogate_pair": is_surrogate_pair
        }

    @staticmethod
    def iterate_code_points(string: str) -> Dict[str, Any]:
        """
        Iterate over string as Unicode code points.

        Returns an iterator that yields Unicode code points (characters).
        Correctly handles surrogate pairs, yielding complete emoji/symbols.

        Requirement: FR-ES24-D-008

        Args:
            string: String to iterate over

        Returns:
            Dictionary with 'code_points' (list of characters), 'count' (int),
            and 'has_surrogate_pairs' (bool)

        Raises:
            TypeError: If string is not a str

        Examples:
            >>> StringEdgeCases.iterate_code_points("hello")
            {'code_points': ['h', 'e', 'l', 'l', 'o'], 'count': 5, 'has_surrogate_pairs': False}
            >>> StringEdgeCases.iterate_code_points("😀😁")
            {'code_points': ['😀', '😁'], 'count': 2, 'has_surrogate_pairs': True}
        """
        # Validate input
        if not isinstance(string, str):
            raise TypeError("First argument must be a string")

        # Python strings are already code-point based
        # Iteration naturally yields complete code points
        code_points = list(string)
        count = len(code_points)

        # Detect if any character is a surrogate pair (code point >= 0x10000)
        has_surrogate_pairs = any(ord(char) >= 0x10000 for char in code_points)

        return {
            "code_points": code_points,
            "count": count,
            "has_surrogate_pairs": has_surrogate_pairs
        }

    @staticmethod
    def match_unicode_property(text: str, property: str) -> Dict[str, Any]:
        """
        Match text against Unicode property escape.

        Matches text using Unicode property escapes in RegExp patterns.
        Supports properties like Emoji, Letter, Script=Greek, etc.

        Requirement: FR-ES24-D-009

        Args:
            text: Text to search
            property: Unicode property name (e.g., "Emoji", "Letter", "Script=Greek")

        Returns:
            Dictionary with 'matches' (list of characters), 'count' (int),
            and 'property' (str)

        Raises:
            TypeError: If text or property is not a str
            ValueError: If property is invalid

        Examples:
            >>> StringEdgeCases.match_unicode_property("Hello 😀", "Emoji")
            {'matches': ['😀'], 'count': 1, 'property': 'Emoji'}
            >>> StringEdgeCases.match_unicode_property("Hello123", "Letter")
            {'matches': ['H', 'e', 'l', 'l', 'o'], 'count': 5, 'property': 'Letter'}
        """
        # Validate inputs
        if not isinstance(text, str):
            raise TypeError("First argument must be a string")
        if not isinstance(property, str):
            raise TypeError("Second argument must be a string")

        # Get or compile regex pattern for this property
        pattern = StringEdgeCases._get_property_pattern(property)

        # Find all matches
        try:
            matches = pattern.findall(text)
        except Exception as e:
            raise ValueError(f"Invalid Unicode property: {property}") from e

        return {
            "matches": matches,
            "count": len(matches),
            "property": property
        }

    @staticmethod
    def _get_property_pattern(property: str) -> Any:
        """
        Get or compile a regex pattern for a Unicode property.

        Caches compiled patterns for performance.

        Args:
            property: Unicode property name

        Returns:
            Compiled regex pattern object

        Raises:
            ValueError: If property name is invalid
        """
        # Check cache first
        if property in StringEdgeCases._property_cache:
            return StringEdgeCases._property_cache[property]

        # Build regex pattern
        # Unicode property escapes use \p{PropertyName} syntax in regex module
        try:
            # Handle different property formats
            if "=" in property:
                # Script property: "Script=Greek" -> \p{Script=Greek}
                pattern_str = rf"\p{{{property}}}"
            else:
                # Simple property: "Letter" -> \p{Letter}
                # Map common property names to their Unicode equivalents
                property_map = {
                    "Emoji": "Emoji",
                    "Emoji_Presentation": "Emoji_Presentation",
                    "Letter": "L",  # Unicode General Category: Letter
                    "Lowercase_Letter": "Ll",
                    "Uppercase_Letter": "Lu",
                    "Number": "N",  # Unicode General Category: Number
                    "Decimal_Number": "Nd",
                    "Punctuation": "P",  # Unicode General Category: Punctuation
                    "Symbol": "S",  # Unicode General Category: Symbol
                }

                # Get the Unicode property name
                unicode_property = property_map.get(property, property)
                pattern_str = rf"\p{{{unicode_property}}}"

            # Compile pattern
            pattern = regex.compile(pattern_str)

            # Cache it
            StringEdgeCases._property_cache[property] = pattern

            return pattern

        except Exception as e:
            raise ValueError(f"Invalid Unicode property: {property}") from e
