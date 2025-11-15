"""RegExp execution engine with advanced features

Executes RegExp patterns with advanced features:
- Named capture group extraction
- Unicode property matching
- Lookbehind assertion execution
- dotAll (s) flag support
- Indices (d) flag support
"""

import re
from typing import Optional
from .types import (
    MatchResult,
    MatchResultWithIndices,
    MatchIndices,
    LookbehindAssertion,
    UnicodePropertySet,
    RegExpFlags
)
from .parser import RegExpParser


class RegExpExecutor:
    """RegExp execution engine with advanced features"""

    def __init__(self):
        self.parser = RegExpParser()

    def execute(self, pattern: str, input_str: str, flags: str = "") -> MatchResult:
        """Execute RegExp pattern against input string

        Args:
            pattern: RegExp pattern (may contain advanced features)
            input_str: String to match against
            flags: Flag string (e.g., "gi")

        Returns:
            MatchResult with groups and captures

        Raises:
            SyntaxError: If pattern or flags are invalid
        """
        # Parse flags
        flag_config = self.parser.parse_flags(flags) if flags else RegExpFlags()

        # Parse named groups from pattern
        named_groups = self.parser.parse_pattern_for_named_groups(pattern)

        # Convert our pattern to Python regex
        # This is a simplified conversion - full implementation would handle all features
        python_pattern = self._convert_to_python_regex(pattern, flag_config)

        # Build Python regex flags
        python_flags = self._build_python_flags(flag_config)

        try:
            # Execute regex
            regex = re.compile(python_pattern, python_flags)
            match = regex.search(input_str)

            if not match:
                return MatchResult(matched=False)

            # Extract captures
            captures = list(match.groups())

            # Extract named groups
            groups = {}
            for group in named_groups:
                try:
                    value = match.group(group.name)
                    if value is not None:
                        groups[group.name] = value
                except (IndexError, KeyError):
                    pass  # Group didn't participate

            return MatchResult(
                matched=True,
                match_text=match.group(0),
                groups=groups,
                captures=captures
            )

        except re.error as e:
            raise SyntaxError(f"Invalid pattern: {e}")

    def execute_with_dotall(self, pattern: str, input_str: str) -> MatchResult:
        """Execute pattern with dotAll (s flag) - . matches newlines

        Args:
            pattern: RegExp pattern
            input_str: Input string

        Returns:
            Match result with . matching newlines
        """
        return self.execute(pattern, input_str, flags="s")

    def execute_with_indices(self, pattern: str, input_str: str, flags: str = "d") -> MatchResultWithIndices:
        """Execute pattern with indices flag - return match indices

        Args:
            pattern: RegExp pattern
            input_str: Input string
            flags: Flags (must include 'd')

        Returns:
            Match result with indices information
        """
        # Ensure d flag is present
        if 'd' not in flags:
            flags += 'd'

        # Parse flags
        flag_config = self.parser.parse_flags(flags)

        # Parse named groups
        named_groups = self.parser.parse_pattern_for_named_groups(pattern)

        # Convert and execute
        python_pattern = self._convert_to_python_regex(pattern, flag_config)
        python_flags = self._build_python_flags(flag_config)

        try:
            regex = re.compile(python_pattern, python_flags)
            match = regex.search(input_str)

            if not match:
                return MatchResultWithIndices(matched=False)

            # Extract captures and groups
            captures = list(match.groups())
            groups = {}
            for group in named_groups:
                try:
                    value = match.group(group.name)
                    if value is not None:
                        groups[group.name] = value
                except (IndexError, KeyError):
                    pass

            # Build indices information
            indices = MatchIndices(
                start=match.start(),
                end=match.end(),
                groups={},
                captures=[]
            )

            # Add group indices
            for group in named_groups:
                try:
                    start = match.start(group.name)
                    end = match.end(group.name)
                    if start != -1:
                        indices.groups[group.name] = (start, end)
                except (IndexError, KeyError):
                    pass

            # Add capture indices
            for i in range(len(captures)):
                try:
                    start = match.start(i + 1)
                    end = match.end(i + 1)
                    if start != -1:
                        indices.captures.append((start, end))
                except IndexError:
                    pass

            return MatchResultWithIndices(
                matched=True,
                match_text=match.group(0),
                groups=groups,
                captures=captures,
                indices=indices
            )

        except re.error as e:
            raise SyntaxError(f"Invalid pattern: {e}")

    def execute_lookbehind(self, assertion: LookbehindAssertion, position: int, input_str: str) -> bool:
        """Execute lookbehind assertion at given position

        Args:
            assertion: Lookbehind assertion to test
            position: Current position in string
            input_str: Input string

        Returns:
            True if assertion matches
        """
        # Can't lookbehind from start of string
        if position == 0:
            return not assertion.positive  # Negative lookbehind succeeds, positive fails

        # Get the substring to test (everything before position)
        # Look back up to max_length characters
        lookback_start = max(0, position - assertion.max_length)
        lookback_str = input_str[lookback_start:position]

        # Check if pattern matches at the end of the lookback string
        try:
            # Try to match at end of string
            match = re.search(assertion.pattern + r'$', lookback_str)
            matched = match is not None and match.end() == len(lookback_str)

            # For positive lookbehind, return if matched
            # For negative lookbehind, return opposite
            return matched if assertion.positive else not matched

        except re.error:
            return False

    def match_unicode_property(self, code_point: int, property_set: UnicodePropertySet) -> bool:
        """Test if code point matches unicode property

        Args:
            code_point: Unicode code point to test
            property_set: Property set to test against

        Returns:
            True if code point has property
        """
        # Check if code point is in the set
        has_property = code_point in property_set.code_points

        # For negated properties, invert the result
        return not has_property if property_set.negated else has_property

    def _convert_to_python_regex(self, pattern: str, flags: RegExpFlags) -> str:
        """Convert JavaScript RegExp pattern to Python regex

        Args:
            pattern: JavaScript RegExp pattern
            flags: Flag configuration

        Returns:
            Python regex pattern
        """
        # Convert JavaScript named groups to Python named groups
        # JavaScript: (?<name>...) -> Python: (?P<name>...)
        result = pattern

        # Convert named groups
        result = re.sub(r'\(\?<([^>]+)>', r'(?P<\1>', result)

        # Handle backreferences: \k<name> -> (?P=name)
        result = re.sub(r'\\k<([^>]+)>', r'(?P=\1)', result)

        return result

    def _build_python_flags(self, flags: RegExpFlags) -> int:
        """Build Python regex flags from RegExpFlags

        Args:
            flags: Flag configuration

        Returns:
            Python re module flags
        """
        python_flags = 0

        if flags.ignore_case:
            python_flags |= re.IGNORECASE

        if flags.multiline:
            python_flags |= re.MULTILINE

        if flags.dotall:
            python_flags |= re.DOTALL

        if flags.unicode or flags.unicode_sets:
            python_flags |= re.UNICODE

        return python_flags
