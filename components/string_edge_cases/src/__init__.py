"""
String Edge Cases Component - ES2024 Wave D

Provides complete String.prototype edge case handling including:
- String.prototype.at() with negative indices
- Code point handling for surrogate pairs
- String iteration by code points
- Unicode property escapes in RegExp
"""

from .edge_cases import StringEdgeCases

__all__ = ['StringEdgeCases']
