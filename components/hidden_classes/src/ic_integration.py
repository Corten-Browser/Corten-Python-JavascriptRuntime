"""
IC-Shape Integration - Bridge between inline caching and shapes

Provides shape information to inline caches for fast property access.
Validates IC cache entries using shape information.

FR-P4-021: Integration with inline caching
"""

from typing import Optional
from .shape import Shape
from .shape_tree import ShapeTree
from .shape_profiler import ShapeProfiler


class ICShapeIntegration:
    """
    Integration layer between inline caches and shapes

    Inline caches (ICs) use shapes to validate cached property offsets:
    1. IC stores: (shape, property_offset)
    2. On property access:
       - Get object's current shape
       - Check if shape matches cached shape
       - If match: Use cached offset (fast path)
       - If mismatch: Slow path + update cache

    This class provides:
    - Shape extraction from objects
    - IC entry validation
    - Property offset lookup
    - Profiling integration (IC hits/misses)

    Example:
        ic_integration = ICShapeIntegration(shape_tree, profiler)

        # IC fast path
        current_shape = ic_integration.get_shape_for_ic(obj)
        if ic_integration.validate_ic_entry(current_shape, cached_shape, cached_offset):
            # HIT - use fast path
            offset = ic_integration.get_property_offset_for_ic(current_shape, "x")
            value = load_at_offset(obj, offset)
            ic_integration.record_ic_hit(current_shape, "x")
        else:
            # MISS - slow path
            value = slow_property_load(obj, "x")
            ic_integration.record_ic_miss(current_shape, "x")
    """

    def __init__(self, shape_tree: ShapeTree, profiler: ShapeProfiler):
        """
        Create IC-shape integration

        Args:
            shape_tree: Shape tree for shape management
            profiler: Shape profiler for tracking IC hits/misses
        """
        self.shape_tree = shape_tree
        self.profiler = profiler

    def get_shape_for_ic(self, obj) -> Shape:
        """
        Get object's shape for IC validation

        Args:
            obj: JavaScript object (must have .shape attribute)

        Returns:
            Object's current shape
        """
        return obj.shape

    def validate_ic_entry(
        self,
        current_shape: Shape,
        cached_shape: Shape,
        cached_offset: int
    ) -> bool:
        """
        Validate IC cache entry is still valid

        An IC entry is valid if:
        1. Shape matches exactly (same shape object), OR
        2. Shape changed but property offset is same (rare optimization)

        Args:
            current_shape: Object's current shape
            cached_shape: Cached shape from IC
            cached_offset: Cached property offset from IC

        Returns:
            True if IC entry is valid (can use fast path)
        """
        # Fast path: Same shape object
        if current_shape is cached_shape:
            return True

        # Slow path check: Different shape but compatible offset
        # This handles cases where shape transitioned but property offset unchanged
        # (e.g., adding a different property doesn't affect existing offsets)
        # For now, we only validate exact shape matches
        # More sophisticated implementations could check offset compatibility
        return False

    def has_same_offset(
        self,
        shape1: Shape,
        shape2: Shape,
        offset: int
    ) -> bool:
        """
        Check if two shapes have same property at given offset

        This is a potential optimization for IC validation.
        Even if shape changed, if the property offset is the same,
        the IC entry might still be usable.

        Args:
            shape1: First shape
            shape2: Second shape
            offset: Property offset to check

        Returns:
            True if both shapes have same property at offset
        """
        # Build property maps for both shapes
        shape1._build_property_maps()
        shape2._build_property_maps()

        # Get properties at this offset
        prop1 = None
        prop2 = None

        for name, off in shape1._property_map.items():
            if off == offset:
                prop1 = name
                break

        for name, off in shape2._property_map.items():
            if off == offset:
                prop2 = name
                break

        # Same property at same offset?
        return prop1 is not None and prop1 == prop2

    def get_property_offset_for_ic(
        self,
        shape: Shape,
        property_name: str
    ) -> Optional[int]:
        """
        Get property offset for IC fast path

        Args:
            shape: Object's shape
            property_name: Property being accessed

        Returns:
            Property offset (for O(1) access) or None if not found
        """
        return shape.get_property_offset(property_name)

    def record_ic_hit(self, shape: Shape, property_name: str):
        """
        Record IC hit for profiling

        An IC hit means:
        - Shape matched
        - Cached offset was valid
        - Fast path was used

        Args:
            shape: Shape that was accessed
            property_name: Property that was accessed
        """
        self.profiler.record_access(shape, property_name)

    def record_ic_miss(self, shape: Shape, property_name: str):
        """
        Record IC miss (shape changed)

        An IC miss means:
        - Shape did not match cached shape
        - Slow path was used
        - IC cache needs updating

        Args:
            shape: Shape that was accessed
            property_name: Property that was accessed
        """
        # Record as access (even though it was a miss)
        # This helps profiling understand access patterns
        self.profiler.record_access(shape, property_name)
        # Could track IC miss rate separately if needed
