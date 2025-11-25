"""
Intl.RelativeTimeFormat implementation for ES2024 Wave C.

Provides locale-aware relative time formatting.
"""

try:
    from .relative_time_format import RelativeTimeFormat
    from .exceptions import RangeError, TypeError
except ImportError:
    from components.intl_relativetimeformat.src.relative_time_format import RelativeTimeFormat
    from components.intl_relativetimeformat.src.exceptions import RangeError, TypeError

__all__ = ['RelativeTimeFormat', 'RangeError', 'TypeError']
