"""
Performance Optimization Component - ES2024 Wave D

Provides comprehensive performance benchmarking and optimization:
- FR-ES24-D-018: Iteration hot path optimization (20% improvement target)
- FR-ES24-D-019: String operation optimization (30% improvement target)
- FR-ES24-D-020: Array operation optimization (25% improvement target)
- FR-ES24-D-021: Memory allocation optimization (15% reduction target)

Version: 0.1.0
"""

from .benchmarks import BenchmarkRunner
from .iteration_opt import IterationOptimizer
from .string_opt import StringOptimizer
from .array_opt import ArrayOptimizer
from .memory_opt import MemoryOptimizer

__all__ = [
    "BenchmarkRunner",
    "IterationOptimizer",
    "StringOptimizer",
    "ArrayOptimizer",
    "MemoryOptimizer",
]

__version__ = "0.1.0"
