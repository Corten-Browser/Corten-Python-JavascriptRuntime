"""
Generational GC - High-performance generational garbage collector.

Public API exports for generational garbage collection component.
"""

from .generational_gc import GenerationalGC
from .young_generation import YoungGeneration
from .old_generation import OldGeneration
from .write_barrier import WriteBarrier
from .remembered_set import RememberedSet
from .large_object_space import LargeObjectSpace
from .gc_stats import GCStats

__all__ = [
    'GenerationalGC',
    'YoungGeneration',
    'OldGeneration',
    'WriteBarrier',
    'RememberedSet',
    'LargeObjectSpace',
    'GCStats',
]

__version__ = '0.1.0'
