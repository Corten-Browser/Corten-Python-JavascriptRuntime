"""
Array Methods Component - ES2024 Array.prototype gaps.

Public API exports for array_methods component.
Implements ES2024 Array.prototype methods including:
- at(), flat(), flatMap(), includes()
- copyWithin(), fill()
- Array.from() improvements, Array.of()
- Stable sort guarantee

FR-ES24-026 through FR-ES24-035
"""

from .array_methods import ArrayMethods
from .array_constructor import ArrayConstructorMethods
from .array_sorting import ArraySorting

__all__ = [
    'ArrayMethods',
    'ArrayConstructorMethods',
    'ArraySorting',
]

__version__ = '0.1.0'
