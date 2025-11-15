"""
weakref_finalization - ES2021 WeakRef and FinalizationRegistry.

This module provides weak references and finalization callbacks for ES2021.
"""

from .weakref import WeakRef
from .finalization_registry import (
    FinalizationRegistry,
    on_object_collected,
    schedule_cleanup_microtask
)

__all__ = [
    'WeakRef',
    'FinalizationRegistry',
    'on_object_collected',
    'schedule_cleanup_microtask',
]

__version__ = '0.1.0'
