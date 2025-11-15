r"""ES2024 Advanced RegExp Features

This module implements advanced RegExp features for ES2024:
- Named capture groups (?<name>...)
- Unicode property escapes \p{...} and \P{...}
- Lookbehind assertions (?<=...) and (?<!...)
- dotAll flag (s) - . matches newlines
- Indices flag (d) - Match indices in results
- Set notation in /v flag
- String properties in /v
- RegExp.prototype.flags getter
- Unicode mode (/u) edge cases
- RegExp.prototype[@@match/@@matchAll]
"""

from .types import (
    CaptureGroup,
    UnicodePropertySet,
    LookbehindAssertion,
    RegExpFlags,
    MatchResult,
    MatchResultWithIndices,
    MatchIndices,
    CharacterSet,
    StringPropertySet,
)

from .parser import RegExpParser
from .executor import RegExpExecutor
from .prototype import RegExpPrototype
from .unicode_db import UnicodePropertyDatabase
from .set_notation import SetNotationProcessor

__all__ = [
    'CaptureGroup',
    'UnicodePropertySet',
    'LookbehindAssertion',
    'RegExpFlags',
    'MatchResult',
    'MatchResultWithIndices',
    'MatchIndices',
    'CharacterSet',
    'StringPropertySet',
    'RegExpParser',
    'RegExpExecutor',
    'RegExpPrototype',
    'UnicodePropertyDatabase',
    'SetNotationProcessor',
]
