"""
String Methods - ES2024 String.prototype method implementations

Provides ES2024-compliant String methods including:
- at(), replaceAll(), matchAll()
- trimStart(), trimEnd(), padStart(), padEnd()
- codePointAt(), fromCodePoint(), raw()
- Full Unicode support (normalization, surrogate pairs)
"""

from .string_methods import StringMethods
from .unicode_support import UnicodeSupport

__all__ = ['StringMethods', 'UnicodeSupport']
