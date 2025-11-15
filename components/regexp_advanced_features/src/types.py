"""Type definitions for advanced RegExp features"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional


@dataclass
class CaptureGroup:
    """Named capture group descriptor"""
    name: str
    pattern: str
    index: int


@dataclass
class UnicodePropertySet:
    r"""Unicode property set for \p{...} and \P{...}"""
    property_name: str
    property_value: Optional[str] = None
    code_points: Set[int] = field(default_factory=set)
    negated: bool = False


@dataclass
class LookbehindAssertion:
    """Lookbehind assertion descriptor"""
    pattern: str
    positive: bool  # True for (?<=...), False for (?<!...)
    max_length: int = 0


@dataclass
class RegExpFlags:
    """RegExp flags configuration"""
    global_flag: bool = False
    ignore_case: bool = False
    multiline: bool = False
    dotall: bool = False  # s flag
    unicode: bool = False  # u flag
    sticky: bool = False  # y flag
    indices: bool = False  # d flag
    unicode_sets: bool = False  # v flag

    def to_string(self) -> str:
        """Convert flags to string representation"""
        result = ""
        if self.indices: result += "d"
        if self.global_flag: result += "g"
        if self.ignore_case: result += "i"
        if self.multiline: result += "m"
        if self.dotall: result += "s"
        if self.unicode: result += "u"
        if self.unicode_sets: result += "v"
        if self.sticky: result += "y"
        return result


@dataclass
class MatchIndices:
    """Match indices information"""
    start: int
    end: int
    groups: Dict[str, Tuple[int, int]] = field(default_factory=dict)
    captures: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class MatchResult:
    """Basic match result"""
    matched: bool
    match_text: str = ""
    groups: Dict[str, str] = field(default_factory=dict)
    captures: List[str] = field(default_factory=list)


@dataclass
class MatchResultWithIndices:
    """Match result with indices (d flag)"""
    matched: bool
    match_text: str = ""
    groups: Dict[str, str] = field(default_factory=dict)
    captures: List[str] = field(default_factory=list)
    indices: Optional[MatchIndices] = None


@dataclass
class CharacterSet:
    """Character set for set notation"""
    code_points: Set[int] = field(default_factory=set)
    ranges: List[Tuple[int, int]] = field(default_factory=list)

    def contains(self, code_point: int) -> bool:
        """Check if code point is in the set"""
        if code_point in self.code_points:
            return True
        for start, end in self.ranges:
            if start <= code_point <= end:
                return True
        return False

    def add_code_point(self, code_point: int):
        """Add a code point to the set"""
        self.code_points.add(code_point)

    def add_range(self, start: int, end: int):
        """Add a range to the set"""
        self.ranges.append((start, end))


@dataclass
class StringPropertySet:
    """String property set for /v flag"""
    property_name: str
    strings: Set[str] = field(default_factory=set)
