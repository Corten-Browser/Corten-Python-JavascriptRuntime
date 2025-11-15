"""
weakref_finalization component - ES2021 WeakRef and FinalizationRegistry.
"""

from .src import (
    WeakRef,
    FinalizationRegistry,
    on_object_collected,
    schedule_cleanup_microtask,
)

__all__ = [
    'WeakRef',
    'FinalizationRegistry',
    'on_object_collected',
    'schedule_cleanup_microtask',
]
