"""
Shape Profiler - Statistics and profiling for shape usage

Tracks shape creation, transitions, accesses, and deprecation.
Provides profiling data for JIT optimizations.

FR-P4-020: Shape statistics and profiling
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from .shape import Shape


@dataclass
class ShapeStats:
    """
    Statistics for a single shape

    Tracks:
    - Creation count
    - Transition count (how many transitions from this shape)
    - Access count (property access frequency)
    - Deprecation count
    - Children (property_name -> child shape id)
    """

    shape_id: int
    creation_count: int = 0
    transition_count: int = 0
    access_count: int = 0
    deprecation_count: int = 0
    children: Dict[str, int] = field(default_factory=dict)


@dataclass
class ShapeProfile:
    """
    Complete shape profiling data

    Provides overview of all shapes in the system:
    - Total shapes created
    - Active vs deprecated shapes
    - Hot shapes (frequently used)
    - Transition frequencies
    """

    total_shapes: int
    active_shapes: int
    deprecated_shapes: int
    hot_shapes: List[int]  # Shape IDs of top 10 most-used shapes
    transition_frequencies: Dict[Tuple[int, str], int]  # (shape_id, property) -> count


class ShapeProfiler:
    """
    Shape profiler for tracking shape usage patterns

    Provides insights for JIT optimization:
    - Which shapes are hot (frequently used)?
    - Which transitions are common?
    - Which shapes are deprecated?

    This data helps the JIT:
    - Inline fast paths for hot shapes
    - Allocate inline caches for common transitions
    - Clean up deprecated shapes

    Example:
        profiler = ShapeProfiler()

        # Track shape lifecycle
        profiler.record_creation(shape)
        profiler.record_transition(parent, "x", child)
        profiler.record_access(shape, "x")
        profiler.record_deprecation(old_shape)

        # Get insights
        hot_shapes = profiler.get_hot_shapes(threshold=1000)
        profile = profiler.get_profile()
    """

    def __init__(self):
        """Create shape profiler"""
        self.stats: Dict[int, ShapeStats] = {}
        self._transition_frequencies: Dict[Tuple[int, str], int] = {}

    def record_creation(self, shape: Shape):
        """
        Record shape creation

        Args:
            shape: Shape being created
        """
        shape_id = id(shape)

        if shape_id not in self.stats:
            self.stats[shape_id] = ShapeStats(shape_id=shape_id)

        self.stats[shape_id].creation_count += 1

    def record_transition(self, from_shape: Shape, property_name: str, to_shape: Shape):
        """
        Record shape transition

        Tracks transitions in the shape tree (adding properties).

        Args:
            from_shape: Parent shape
            property_name: Property being added
            to_shape: Child shape (result of transition)
        """
        from_id = id(from_shape)
        to_id = id(to_shape)

        # Ensure from_shape is tracked
        if from_id not in self.stats:
            self.stats[from_id] = ShapeStats(shape_id=from_id)

        # Record transition
        self.stats[from_id].transition_count += 1
        self.stats[from_id].children[property_name] = to_id

        # Track transition frequency
        transition_key = (from_id, property_name)
        self._transition_frequencies[transition_key] = \
            self._transition_frequencies.get(transition_key, 0) + 1

    def record_access(self, shape: Shape, property_name: str):
        """
        Record property access

        Tracks how often properties are accessed on this shape.
        High access count indicates a hot shape.

        Args:
            shape: Shape being accessed
            property_name: Property being accessed
        """
        shape_id = id(shape)

        # Ensure shape is tracked
        if shape_id not in self.stats:
            self.stats[shape_id] = ShapeStats(shape_id=shape_id)

        self.stats[shape_id].access_count += 1

    def record_deprecation(self, shape: Shape):
        """
        Record shape deprecation

        Args:
            shape: Shape being deprecated
        """
        shape_id = id(shape)

        # Ensure shape is tracked
        if shape_id not in self.stats:
            self.stats[shape_id] = ShapeStats(shape_id=shape_id)

        self.stats[shape_id].deprecation_count += 1

    def get_hot_shapes(self, threshold: int = 1000) -> List[int]:
        """
        Get frequently-used shapes (hot shapes)

        Hot shapes are candidates for:
        - Inline cache allocation
        - JIT specialization
        - Memory optimization

        Args:
            threshold: Minimum access count to be considered hot

        Returns:
            List of shape IDs (sorted by access count, descending)
        """
        # Filter shapes by access count >= threshold
        hot = [
            (shape_id, stats.access_count)
            for shape_id, stats in self.stats.items()
            if stats.access_count >= threshold
        ]

        # Sort by access count (descending)
        hot.sort(key=lambda x: x[1], reverse=True)

        # Return top 10 shape IDs
        return [shape_id for shape_id, _ in hot[:10]]

    def get_profile(self) -> ShapeProfile:
        """
        Get complete profiling data

        Returns:
            ShapeProfile with all statistics
        """
        total_shapes = len(self.stats)

        # Count deprecated shapes (deprecation_count > 0)
        deprecated_shapes = sum(
            1 for stats in self.stats.values()
            if stats.deprecation_count > 0
        )

        active_shapes = total_shapes - deprecated_shapes

        # Get hot shapes (top 10 by access count)
        all_shapes = [
            (shape_id, stats.access_count)
            for shape_id, stats in self.stats.items()
        ]
        all_shapes.sort(key=lambda x: x[1], reverse=True)
        hot_shapes = [shape_id for shape_id, _ in all_shapes[:10]]

        return ShapeProfile(
            total_shapes=total_shapes,
            active_shapes=active_shapes,
            deprecated_shapes=deprecated_shapes,
            hot_shapes=hot_shapes,
            transition_frequencies=self._transition_frequencies.copy(),
        )
