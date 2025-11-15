"""
JSON Extensions - ES2024 Wave B

Enhanced JSON.parse and JSON.stringify with:
- Reviver improvements (proper this binding, property order, source access)
- Replacer improvements (function/array replacer, context)
- Well-formed Unicode (proper surrogate handling)
- Space parameter (indentation)
- Edge cases (circular refs, BigInt, symbols, functions, toJSON)
"""

from .json_parser import JSONParser, JSONReviverContext
from .json_stringifier import JSONStringifier, JSONReplacerContext
from .json_unicode import JSONUnicode
from .json_edge_cases import (
    JSONEdgeCases,
    BigInt,
    Symbol,
    Undefined
)

__all__ = [
    # Parser
    'JSONParser',
    'JSONReviverContext',

    # Stringifier
    'JSONStringifier',
    'JSONReplacerContext',

    # Unicode
    'JSONUnicode',

    # Edge cases
    'JSONEdgeCases',
    'BigInt',
    'Symbol',
    'Undefined',
]

__version__ = '0.1.0'
