"""
Hidden Classes Component

Shape-based optimization for object property layout and fast property access.
"""

__version__ = "0.1.0"

# Core shape classes
from .shape import Shape, ElementKind, ArrayShape
from .shape_tree import ShapeTree
from .property_descriptor import PropertyAttributes

# Integration features (Phase 4)
from .shape_profiler import ShapeProfiler, ShapeStats, ShapeProfile
from .ic_integration import ICShapeIntegration
from .shape_deoptimization import ShapeDeoptimization, ShapeDeoptTrigger

__all__ = [
    # Core shape classes
    "Shape",
    "ElementKind",
    "ArrayShape",
    "ShapeTree",
    "PropertyAttributes",
    # Integration features
    "ShapeProfiler",
    "ShapeStats",
    "ShapeProfile",
    "ICShapeIntegration",
    "ShapeDeoptimization",
    "ShapeDeoptTrigger",
]
