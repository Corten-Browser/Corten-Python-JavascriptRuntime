"""
Intl.RelativeTimeFormat implementation for ES2024 Wave C.

Provides locale-aware relative time formatting.
"""

from .relative_time_format import RelativeTimeFormat
from .exceptions import RangeError, TypeError

__all__ = ['RelativeTimeFormat', 'RangeError', 'TypeError']
