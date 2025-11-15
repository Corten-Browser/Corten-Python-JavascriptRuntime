r"""RegExp parser for advanced features

Parses advanced RegExp syntax including:
- Named capture groups (?<name>...)
- Unicode property escapes \p{...}
- Lookbehind assertions (?<=...) and (?<!...)
- Set notation in /v flag
"""

import re
from typing import List, Optional
from .types import CaptureGroup, UnicodePropertySet, LookbehindAssertion, RegExpFlags


class RegExpParser:
    """Enhanced RegExp parser for advanced syntax"""

    def __init__(self):
        self.named_groups: List[CaptureGroup] = []
        self.group_names: set = set()

    def parse_named_capture_group(self, pattern: str) -> Optional[CaptureGroup]:
        """Parse a single named capture group from pattern

        Args:
            pattern: Pattern containing (?<name>...) syntax

        Returns:
            CaptureGroup descriptor or None if not found

        Raises:
            SyntaxError: If group name is invalid or syntax is malformed
        """
        # Match named group pattern: (?<name>...)
        # Allow empty name to detect and report error
        match = re.match(r'\(\?<([^>]*)>(.+)\)$', pattern)
        if not match:
            return None

        name = match.group(1)
        group_pattern = match.group(2)

        # Check for empty name
        if not name:
            raise SyntaxError("Capture group name cannot be empty")

        # Validate group name (must be valid identifier)
        if not self._is_valid_identifier(name):
            raise SyntaxError(f"Invalid capture group name: {name}")

        # Create capture group
        index = len(self.named_groups)
        group = CaptureGroup(name=name, pattern=group_pattern, index=index)

        return group

    def parse_pattern_for_named_groups(self, pattern: str) -> List[CaptureGroup]:
        """Parse entire pattern and extract all named capture groups

        Args:
            pattern: Full RegExp pattern string

        Returns:
            List of all named capture groups found

        Raises:
            SyntaxError: If duplicate group names found
        """
        groups = []
        group_names = set()

        # Find all named groups: (?<name>...)
        # This regex finds named groups considering nesting
        pos = 0
        while pos < len(pattern):
            if pattern[pos:pos+3] == '(?<':
                # Find the end of the group name
                name_end = pattern.find('>', pos + 3)
                if name_end == -1:
                    raise SyntaxError("Unterminated named capture group")

                name = pattern[pos+3:name_end]

                # Check for empty name
                if not name:
                    raise SyntaxError("Capture group name cannot be empty")

                # Validate name
                if not self._is_valid_identifier(name):
                    raise SyntaxError(f"Invalid capture group name: {name}")

                # Check for duplicates
                if name in group_names:
                    raise SyntaxError(f"Duplicate capture group name: {name}")

                group_names.add(name)

                # Find the matching closing paren
                group_start = name_end + 1
                paren_count = 1
                group_end = group_start
                in_escape = False

                while group_end < len(pattern) and paren_count > 0:
                    if in_escape:
                        in_escape = False
                    elif pattern[group_end] == '\\':
                        in_escape = True
                    elif pattern[group_end] == '(':
                        paren_count += 1
                    elif pattern[group_end] == ')':
                        paren_count -= 1
                    group_end += 1

                if paren_count != 0:
                    raise SyntaxError("Unmatched parentheses in pattern")

                group_pattern = pattern[group_start:group_end-1]
                index = len(groups)

                group = CaptureGroup(name=name, pattern=group_pattern, index=index)
                groups.append(group)

                # Continue searching from where we left off
                # This allows finding nested groups
                pos = group_start
            else:
                pos += 1

        return groups

    def parse_unicode_property(self, property_expr: str, negated: bool = False) -> UnicodePropertySet:
        r"""Parse unicode property escape

        Args:
            property_expr: Property expression like "Script=Latin" or "Letter"
            negated: True for \P{...}, false for \p{...}

        Returns:
            UnicodePropertySet with matching code points

        Raises:
            SyntaxError: If property expression is invalid
        """
        # Parse property expression
        if '=' in property_expr:
            parts = property_expr.split('=', 1)
            property_name = parts[0].strip()
            property_value = parts[1].strip()
        else:
            property_name = property_expr.strip()
            property_value = None

        # For now, return empty set - will be populated by UnicodePropertyDatabase
        return UnicodePropertySet(
            property_name=property_name,
            property_value=property_value,
            code_points=set(),
            negated=negated
        )

    def parse_lookbehind(self, pattern: str, positive: bool = True) -> LookbehindAssertion:
        """Parse lookbehind assertion

        Args:
            pattern: Lookbehind pattern
            positive: True for (?<=...), false for (?<!...)

        Returns:
            LookbehindAssertion descriptor

        Raises:
            SyntaxError: If pattern contains unbounded quantifiers
        """
        # Check for unbounded quantifiers (not allowed in lookbehind)
        if re.search(r'[*+]\??(?!\})', pattern):
            raise SyntaxError("Unbounded quantifiers not allowed in lookbehind")

        # Estimate max length for lookbehind
        # This is a simplified version - full implementation would need proper analysis
        max_length = self._estimate_max_length(pattern)

        return LookbehindAssertion(
            pattern=pattern,
            positive=positive,
            max_length=max_length
        )

    def parse_flags(self, flags_str: str) -> RegExpFlags:
        """Parse RegExp flags string

        Args:
            flags_str: Flag string (e.g., "gimsduv")

        Returns:
            RegExpFlags configuration

        Raises:
            SyntaxError: If invalid flags or invalid combinations
        """
        flags = RegExpFlags()

        seen = set()
        for char in flags_str:
            # Check for duplicate flags
            if char in seen:
                raise SyntaxError(f"Duplicate flag: {char}")
            seen.add(char)

            # Parse individual flags
            if char == 'g':
                flags.global_flag = True
            elif char == 'i':
                flags.ignore_case = True
            elif char == 'm':
                flags.multiline = True
            elif char == 's':
                flags.dotall = True
            elif char == 'u':
                flags.unicode = True
            elif char == 'v':
                flags.unicode_sets = True
            elif char == 'y':
                flags.sticky = True
            elif char == 'd':
                flags.indices = True
            else:
                raise SyntaxError(f"Invalid flag: {char}")

        # Check for invalid combinations
        if flags.unicode and flags.unicode_sets:
            raise SyntaxError("Cannot use both 'u' and 'v' flags")

        return flags

    def _is_valid_identifier(self, name: str) -> bool:
        """Check if string is a valid JavaScript identifier

        Args:
            name: String to validate

        Returns:
            True if valid identifier
        """
        if not name:
            return False

        # JavaScript identifier rules:
        # - Must start with letter, _, or $
        # - Can contain letters, digits, _, $
        if not (name[0].isalpha() or name[0] in ('_', '$')):
            return False

        for char in name[1:]:
            if not (char.isalnum() or char in ('_', '$')):
                return False

        return True

    def _estimate_max_length(self, pattern: str) -> int:
        """Estimate maximum length for lookbehind pattern

        This is a simplified estimation. A full implementation would
        need to analyze the pattern structure completely.

        Args:
            pattern: Pattern to analyze

        Returns:
            Estimated maximum length
        """
        # Very simplified - just count characters as upper bound
        # Real implementation would parse quantifiers properly
        return len(pattern) * 10  # Conservative estimate
