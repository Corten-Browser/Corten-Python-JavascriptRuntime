"""
Error Stack Polish Component

Complete Error.prototype.stack and error formatting implementation for ES2024 Wave D.

Provides:
- FR-ES24-D-015: Error.prototype.stack formatting
- FR-ES24-D-016: Error cause chain formatting
- FR-ES24-D-017: Source map support preparation
"""

from .stack_formatter import ErrorStackFormatter
from .cause_chain import CauseChainFormatter
from .source_map import SourceMapPreparer

__all__ = [
    "ErrorStackFormatter",
    "CauseChainFormatter",
    "SourceMapPreparer"
]

__version__ = "0.1.0"
