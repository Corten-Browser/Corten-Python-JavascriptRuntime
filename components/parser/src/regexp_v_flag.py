r"""
RegExp /v flag implementation with character class set operations.

Implements ES2024 RegExp /v flag support including:
- Flag parsing and validation
- Character class set operations (intersection &&, subtraction --)
- String properties in character classes (\p{property})

ES2024 Spec: https://tc39.es/ecma262/#sec-regexp-unicode-properties
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any


@dataclass
class RegExpFlags:
    """
    RegExp flags representation with validation.

    Attributes:
        g: Global flag
        i: Case-insensitive flag
        m: Multiline flag
        s: Dotall flag
        u: Unicode flag (mutually exclusive with v)
        v: Set notation flag (mutually exclusive with u)
        d: hasIndices flag
        y: Sticky flag

    Example:
        >>> flags = RegExpFlags.from_string("giv")
        >>> flags.g
        True
        >>> flags.v
        True
        >>> flags.u
        False
    """

    g: bool = False  # global
    i: bool = False  # case-insensitive
    m: bool = False  # multiline
    s: bool = False  # dotall
    u: bool = False  # unicode
    v: bool = False  # set notation (ES2024)
    d: bool = False  # hasIndices
    y: bool = False  # sticky

    @classmethod
    def from_string(cls, flags_str: str) -> "RegExpFlags":
        """
        Parse flags from string.

        Args:
            flags_str: String of flag characters (e.g., "giv")

        Returns:
            RegExpFlags: Parsed flags object

        Raises:
            ValueError: If flags are invalid or duplicate
            TypeError: If /u and /v flags are both present

        Example:
            >>> flags = RegExpFlags.from_string("giv")
            >>> flags.g and flags.i and flags.v
            True
        """
        flags = cls()
        seen = set()

        for char in flags_str:
            # Check for duplicates
            if char in seen:
                raise ValueError(f"duplicate flag: {char}")
            seen.add(char)

            # Validate and set flag
            if char == "g":
                flags.g = True
            elif char == "i":
                flags.i = True
            elif char == "m":
                flags.m = True
            elif char == "s":
                flags.s = True
            elif char == "u":
                flags.u = True
            elif char == "v":
                flags.v = True
            elif char == "d":
                flags.d = True
            elif char == "y":
                flags.y = True
            else:
                raise ValueError(f"Invalid flag: {char}")

        # Validate mutual exclusivity of u and v
        if flags.u and flags.v:
            raise TypeError("RegExp flags /u and /v are mutually exclusive")

        return flags

    def to_string(self) -> str:
        """
        Convert flags to string representation.

        Returns:
            str: Flag string (e.g., "giv")

        Example:
            >>> flags = RegExpFlags(g=True, i=True, v=True)
            >>> flags.to_string()
            'giv'
        """
        result = ""
        if self.g:
            result += "g"
        if self.i:
            result += "i"
        if self.m:
            result += "m"
        if self.s:
            result += "s"
        if self.u:
            result += "u"
        if self.v:
            result += "v"
        if self.d:
            result += "d"
        if self.y:
            result += "y"
        return result


class CharacterClassSetParser:
    """
    Parser for character class set operations.

    Parses character class set notation enabled by the /v flag:
    - Intersection: [a-z&&[aeiou]] (vowels)
    - Subtraction: [a-z--[aeiou]] (consonants)
    - Nested operations: [[[a-z]--[aeiou]]&&[b-y]]

    Example:
        >>> parser = CharacterClassSetParser()
        >>> result = parser.parse("[a-z&&[aeiou]]", has_v_flag=True)
        >>> result["type"]
        'intersection'
    """

    # Valid Unicode property names (subset for demonstration)
    VALID_PROPERTIES = {
        "RGI_Emoji",
        "ASCII",
        "Letter",
        "Number",
        "Digit",
        "Alphabetic",
        "Uppercase",
        "Lowercase",
        "White_Space",
        "Script",
        "General_Category",
    }

    def parse(self, char_class: str, has_v_flag: bool) -> Dict[str, Any]:
        """
        Parse character class with potential set operations.

        Args:
            char_class: Character class string (e.g., "[a-z&&[aeiou]]")
            has_v_flag: Whether the /v flag is enabled

        Returns:
            dict: Parsed structure with type and operands

        Raises:
            ValueError: If set operations used without /v flag
            ValueError: If invalid property name used

        Example:
            >>> parser = CharacterClassSetParser()
            >>> result = parser.parse("[a-z&&[aeiou]]", has_v_flag=True)
            >>> result["type"]
            'intersection'
        """
        # Strip outer brackets
        if char_class.startswith("[") and char_class.endswith("]"):
            char_class = char_class[1:-1]

        # Check for property notation
        if r"\p{" in char_class or r"\P{" in char_class:
            return self._parse_property(char_class, has_v_flag)

        # Check for set operations
        if "&&" in char_class:
            if not has_v_flag:
                raise ValueError("requires /v flag")
            return self._parse_intersection(char_class)

        if "--" in char_class:
            if not has_v_flag:
                raise ValueError("requires /v flag")
            return self._parse_subtraction(char_class)

        # Simple character class
        return {
            "type": "simple",
            "pattern": char_class,
            "negated": char_class.startswith("^"),
        }

    def _parse_property(self, pattern: str, has_v_flag: bool) -> Dict[str, Any]:
        r"""
        Parse Unicode property notation.

        Args:
            pattern: Pattern containing \p{} or \P{}
            has_v_flag: Whether /v flag is enabled

        Returns:
            dict: Property information

        Raises:
            ValueError: If property name is invalid
        """
        # Extract property name
        negated = r"\P{" in pattern

        if negated:
            start = pattern.find(r"\P{")
        else:
            start = pattern.find(r"\p{")

        if start == -1:
            return {"type": "simple", "pattern": pattern, "negated": False}

        end = pattern.find("}", start)
        if end == -1:
            raise ValueError("Unclosed property notation")

        property_name = pattern[start + 3 : end]

        # Validate property name
        if property_name not in self.VALID_PROPERTIES:
            raise ValueError(f"Invalid property: {property_name}")

        return {
            "type": "property",
            "property": property_name,
            "negated": negated,
            "string_property": has_v_flag,
        }

    def _parse_intersection(self, pattern: str) -> Dict[str, Any]:
        """
        Parse intersection operation (&&).

        Args:
            pattern: Pattern with && operator

        Returns:
            dict: Intersection operation structure
        """
        # Find the && operator (not inside nested brackets)
        parts = self._split_on_operator(pattern, "&&")

        if len(parts) < 2:
            return {"type": "simple", "pattern": pattern, "negated": False}

        # Parse left and right operands
        left = parts[0].strip()
        right = "&&".join(parts[1:]).strip()

        # Handle negation in right operand
        right_negated = False
        if right.startswith("[^") and right.endswith("]"):
            right_negated = True
            right = right[2:-1]
        elif right.startswith("[") and right.endswith("]"):
            right = right[1:-1]

        return {
            "type": "intersection",
            "left": left,
            "right": {"pattern": right, "negated": right_negated},
            "operations": ["&&"],
        }

    def _parse_subtraction(self, pattern: str) -> Dict[str, Any]:
        """
        Parse subtraction operation (--).

        Args:
            pattern: Pattern with -- operator

        Returns:
            dict: Subtraction operation structure
        """
        # Find the -- operator
        parts = self._split_on_operator(pattern, "--")

        if len(parts) < 2:
            return {"type": "simple", "pattern": pattern, "negated": False}

        left = parts[0].strip()
        right = "--".join(parts[1:]).strip()

        # Strip brackets from left operand if present
        if left.startswith("[") and left.endswith("]"):
            left = left[1:-1]

        # Strip brackets from right operand if present
        if right.startswith("[") and right.endswith("]"):
            right = right[1:-1]

        return {
            "type": "subtraction",
            "left": left,
            "right": right,
            "operations": ["--"],
        }

    def _split_on_operator(self, pattern: str, operator: str) -> List[str]:
        """
        Split pattern on operator, respecting nested brackets.

        Args:
            pattern: Pattern to split
            operator: Operator to split on

        Returns:
            list: Split parts
        """
        parts = []
        current = ""
        bracket_depth = 0
        i = 0

        while i < len(pattern):
            char = pattern[i]

            if char == "[":
                bracket_depth += 1
                current += char
                i += 1
            elif char == "]":
                bracket_depth -= 1
                current += char
                i += 1
            elif bracket_depth == 0 and pattern[i : i + len(operator)] == operator:
                parts.append(current)
                current = ""
                i += len(operator)
            else:
                current += char
                i += 1

        if current:
            parts.append(current)

        return parts


class RegExpVFlag:
    """
    Main interface for RegExp /v flag functionality.

    Provides methods to parse and validate RegExp patterns with /v flag,
    including set operations and string properties.

    Example:
        >>> regexp = RegExpVFlag("/[a-z&&[aeiou]]/v")
        >>> regexp.flags.v
        True
        >>> regexp.pattern
        '[a-z&&[aeiou]]'
    """

    def __init__(self, regexp_literal: str):
        """
        Initialize from RegExp literal string.

        Args:
            regexp_literal: Full RegExp literal (e.g., "/pattern/flags")

        Raises:
            ValueError: If literal format is invalid
            TypeError: If /u and /v flags are both present
        """
        if not regexp_literal.startswith("/"):
            raise ValueError("RegExp literal must start with /")

        # Find closing /
        close_index = regexp_literal.rfind("/")
        if close_index <= 0:
            raise ValueError("RegExp literal must have closing /")

        self.pattern = regexp_literal[1:close_index]
        flags_str = regexp_literal[close_index + 1 :]

        self.flags = RegExpFlags.from_string(flags_str)
        self.parser = CharacterClassSetParser()

    def parse_character_classes(self) -> List[Dict[str, Any]]:
        """
        Parse all character classes in the pattern.

        Returns:
            list: Parsed character class structures

        Example:
            >>> regexp = RegExpVFlag("/[a-z&&[aeiou]]/v")
            >>> classes = regexp.parse_character_classes()
            >>> len(classes)
            1
            >>> classes[0]["type"]
            'intersection'
        """
        results = []
        i = 0
        pattern = self.pattern

        while i < len(pattern):
            if pattern[i] == "[":
                # Find matching ]
                bracket_depth = 1
                j = i + 1

                while j < len(pattern) and bracket_depth > 0:
                    if pattern[j] == "[":
                        bracket_depth += 1
                    elif pattern[j] == "]":
                        bracket_depth -= 1
                    j += 1

                char_class = pattern[i:j]
                parsed = self.parser.parse(char_class, self.flags.v)
                results.append(parsed)

                i = j
            else:
                i += 1

        return results

    def validate(self) -> bool:
        """
        Validate the RegExp pattern.

        Returns:
            bool: True if pattern is valid

        Raises:
            ValueError: If pattern is invalid
        """
        # Parse all character classes
        self.parse_character_classes()
        return True
