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
from components.deoptimization.src.deopt_manager import DeoptimizationManager
from components.deoptimization.src.frame_reconstructor import FrameReconstructor
from components.deoptimization.src.state_materializer import StateMaterializer
from components.deoptimization.src.trigger_handler import DeoptTriggerHandler
from components.deoptimization.src.lazy_deopt import LazyDeoptimizer
from components.deoptimization.src.eager_deopt import EagerDeoptimizer
from components.deoptimization.src.deopt_profiler import DeoptProfiler

__all__ = [
    # Enums and types
    "DeoptReason",
    "DeoptMode",
    "DeoptInfo",
    "ValueLocation",
    "JITFrame",
    "InterpreterFrame",
    "JITState",
    "DeoptStats",
    "DeoptHotspot",
    # Main classes
    "DeoptimizationManager",
    "FrameReconstructor",
    "StateMaterializer",
    "DeoptTriggerHandler",
    "LazyDeoptimizer",
    "EagerDeoptimizer",
    "DeoptProfiler",
]
