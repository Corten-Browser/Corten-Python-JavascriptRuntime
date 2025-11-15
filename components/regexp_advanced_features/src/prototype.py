"""RegExp.prototype methods for advanced features"""

from .types import RegExpFlags, MatchResult
from .parser import RegExpParser
from typing import Iterator, Optional


class RegExpPrototype:
    """Enhanced RegExp.prototype methods"""

    def __init__(self):
        self.parser = RegExpParser()

    def flags_getter(self, regexp: 'RegExp') -> str:
        """Get RegExp.prototype.flags property

        Args:
            regexp: RegExp instance

        Returns:
            Flag string (e.g., "gimsduv")

        Requirement: FR-ES24-B-008
        """
        # This would access internal RegExp flags in real implementation
        # For now, return empty string as placeholder
        return ""

    def symbol_match(self, regexp: 'RegExp', string: str) -> Optional[MatchResult]:
        """Implement RegExp.prototype[@@match]

        Args:
            regexp: RegExp instance
            string: String to match

        Returns:
            Match result or None

        Requirement: FR-ES24-B-010
        """
        # Placeholder implementation
        return None

    def symbol_match_all(self, regexp: 'RegExp', string: str) -> Iterator[MatchResult]:
        """Implement RegExp.prototype[@@matchAll]

        Args:
            regexp: RegExp instance (must have g flag)
            string: String to match

        Returns:
            Iterator of all matches

        Raises:
            TypeError: If global flag not set

        Requirement: FR-ES24-B-010
        """
        # Placeholder - would yield match results
        return iter([])
