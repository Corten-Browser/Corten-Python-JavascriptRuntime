"""
Intl.Collator - Locale-sensitive string comparison and sorting.

Implements ES2024 Wave C Internationalization APIs.
FR-ES24-C-001 to FR-ES24-C-008
"""

from .collator import IntlCollator, RangeError

__all__ = ['IntlCollator', 'RangeError']
