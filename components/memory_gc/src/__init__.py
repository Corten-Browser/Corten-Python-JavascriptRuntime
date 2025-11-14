"""
Memory GC component - Memory allocation and garbage collection.

This component provides a simple mark-and-sweep garbage collector
for the JavaScript runtime engine.

Public API:
    - HeapObject: Base class for heap-allocated objects
    - GarbageCollector: Mark-and-sweep garbage collector
    - AllocateObject: Allocate JavaScript object
    - AllocateArray: Allocate JavaScript array
    - AllocateString: Allocate JavaScript string
"""

from .heap_object import HeapObject
from .garbage_collector import GarbageCollector
from .allocators import AllocateObject, AllocateArray, AllocateString

__all__ = [
    "HeapObject",
    "GarbageCollector",
    "AllocateObject",
    "AllocateArray",
    "AllocateString",
]
