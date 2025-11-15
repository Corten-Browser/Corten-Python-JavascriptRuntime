"""
Optimizations Package

Exports all optimization passes for the optimizing JIT compiler.
"""

from .dce import DeadCodeEliminator
from .constant_folding import ConstantFolder
from .loop_optimizer import LoopOptimizer, LoopInfo
from .escape_analyzer import EscapeAnalyzer, EscapeInfo, EscapeStatus
from .scalar_replacement import ScalarReplacement

# Phase 4 Advanced Optimizations (newly implemented)
from .polymorphic_ic_handler import PolymorphicICHandler
from .code_motion import (
    CodeMotionOptimizer,
    InstructionScheduler,
    DependencyGraph
)
from .graph_coloring_allocator import (
    GraphColoringAllocator,
    InterferenceGraph,
    RegisterAllocation
)

# Future optimizations (not yet implemented)
# from .strength_reduction import StrengthReducer
# from .range_analysis import RangeAnalyzer, ValueRange
# from .bounds_check_elimination import BoundsCheckEliminator
# from .speculation_manager import (
#     SpeculationManager,
#     GuardNode,
#     GuardType,
#     DeoptTrigger,
#     DeoptReason
# )

__all__ = [
    # Core optimizations
    "DeadCodeEliminator",
    "ConstantFolder",
    "LoopOptimizer",
    "LoopInfo",
    "EscapeAnalyzer",
    "EscapeInfo",
    "EscapeStatus",
    "ScalarReplacement",
    # Phase 4 Advanced Optimizations
    "PolymorphicICHandler",
    "CodeMotionOptimizer",
    "InstructionScheduler",
    "DependencyGraph",
    "GraphColoringAllocator",
    "InterferenceGraph",
    "RegisterAllocation",
    # Future optimizations (commented out until implemented)
    # "StrengthReducer",
    # "RangeAnalyzer",
    # "ValueRange",
    # "BoundsCheckEliminator",
    # "SpeculationManager",
    # "GuardNode",
    # "GuardType",
    # "DeoptTrigger",
    # "DeoptReason",
]
