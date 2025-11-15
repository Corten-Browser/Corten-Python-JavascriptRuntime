"""
Deoptimization component.

Provides safe fallback from optimized JIT code to interpreter.
"""
from components.deoptimization.src.deopt_types import (
    DeoptReason,
    DeoptMode,
    DeoptInfo,
    ValueLocation,
    JITFrame,
    InterpreterFrame,
    JITState,
    DeoptStats,
    DeoptHotspot,
)

__all__ = [
    "DeoptReason",
    "DeoptMode",
    "DeoptInfo",
    "ValueLocation",
    "JITFrame",
    "InterpreterFrame",
    "JITState",
    "DeoptStats",
    "DeoptHotspot",
]
