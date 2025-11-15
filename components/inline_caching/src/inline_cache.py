"""
Base Inline Cache implementation.

Provides core inline caching functionality with state machine:
- Monomorphic IC: Single shape (fast path)
- Polymorphic IC: 2-4 shapes (medium path)
- Megamorphic IC: >4 shapes (fallback to slow path)

Performance targets:
- Monomorphic hit rate: >90%
- Cache check latency: <10ns
- Memory overhead: <100 bytes per IC
"""
from typing import Optional
from .ic_state import ICState
from ._shape_placeholder import Shape


# Polymorphic cache limit (transition to megamorphic after this many shapes)
POLYMORPHIC_LIMIT = 4


class InlineCache:
    """
    Base inline cache for property and call site optimization.

    State machine transitions:
    UNINITIALIZED → MONOMORPHIC → POLYMORPHIC → MEGAMORPHIC

    Attributes:
        cache_type: Type of cache (property_load, property_store, call)
        _state: Current IC state
        _mono_shape: Cached shape for monomorphic case
        _mono_offset: Cached offset for monomorphic case
        _poly_cache: List of (shape, offset) tuples for polymorphic case
    """

    def __init__(self, cache_type: str):
        """
        Initialize inline cache.

        Args:
            cache_type: Type of cache (property_load, property_store, call)
        """
        self.cache_type = cache_type
        self._state = ICState.UNINITIALIZED

        # Monomorphic cache (single shape)
        self._mono_shape: Optional[Shape] = None
        self._mono_offset: Optional[int] = None

        # Polymorphic cache (2-4 shapes)
        self._poly_cache: list = []

    def get_state(self) -> ICState:
        """
        Get current cache state.

        Returns:
            Current ICState
        """
        return self._state

    def check(self, shape: Shape) -> bool:
        """
        Check if cache is valid for given shape.

        Args:
            shape: Object shape to check

        Returns:
            True if cache hit, False if cache miss

        Performance:
            - Monomorphic: O(1) single comparison
            - Polymorphic: O(n) linear search (n ≤ 4)
            - Megamorphic: Always returns False (use slow path)
        """
        if self._state == ICState.UNINITIALIZED:
            return False

        elif self._state == ICState.MONOMORPHIC:
            return self._mono_shape == shape

        elif self._state == ICState.POLYMORPHIC:
            # Linear search through polymorphic cache
            for cached_shape, _ in self._poly_cache:
                if cached_shape == shape:
                    return True
            return False

        else:  # MEGAMORPHIC
            # Always miss in megamorphic state (fallback to dict lookup)
            return False

    def update(self, shape: Shape, offset: int) -> None:
        """
        Update cache with new shape/offset.

        Handles state transitions:
        - First shape: UNINITIALIZED → MONOMORPHIC
        - Second shape: MONOMORPHIC → POLYMORPHIC
        - Fifth shape: POLYMORPHIC → MEGAMORPHIC

        Args:
            shape: Object shape
            offset: Property offset in object

        Performance:
            - Monomorphic: O(1)
            - Polymorphic: O(n) to check for duplicates
            - Megamorphic: O(1) (no-op)
        """
        if self._state == ICState.UNINITIALIZED:
            # Transition to monomorphic
            self._mono_shape = shape
            self._mono_offset = offset
            self._state = ICState.MONOMORPHIC

        elif self._state == ICState.MONOMORPHIC:
            # Check if same shape (update offset)
            if self._mono_shape == shape:
                self._mono_offset = offset
                return

            # Different shape: transition to polymorphic
            # Move monomorphic entry to polymorphic cache
            self._poly_cache = [
                (self._mono_shape, self._mono_offset),
                (shape, offset)
            ]
            self._mono_shape = None
            self._mono_offset = None
            self._state = ICState.POLYMORPHIC

        elif self._state == ICState.POLYMORPHIC:
            # Check if shape already in cache
            for i, (cached_shape, _) in enumerate(self._poly_cache):
                if cached_shape == shape:
                    # Update existing entry
                    self._poly_cache[i] = (shape, offset)
                    return

            # New shape: add to polymorphic cache
            self._poly_cache.append((shape, offset))

            # Check if exceeded polymorphic limit
            if len(self._poly_cache) > POLYMORPHIC_LIMIT:
                # Transition to megamorphic
                self._poly_cache = []
                self._state = ICState.MEGAMORPHIC

        else:  # MEGAMORPHIC
            # No caching in megamorphic state
            pass

    def invalidate(self) -> None:
        """
        Invalidate cache (transition to next state or reset).

        Resets cache to UNINITIALIZED state and clears all cached data.
        """
        self._state = ICState.UNINITIALIZED
        self._mono_shape = None
        self._mono_offset = None
        self._poly_cache = []

    def get_cached_offset(self, shape: Optional[Shape] = None) -> Optional[int]:
        """
        Get cached offset for a shape.

        Args:
            shape: Shape to look up (required for polymorphic, optional for monomorphic)

        Returns:
            Cached offset or None if not found
        """
        if self._state == ICState.UNINITIALIZED:
            return None

        elif self._state == ICState.MONOMORPHIC:
            if shape is None or self._mono_shape == shape:
                return self._mono_offset
            return None

        elif self._state == ICState.POLYMORPHIC:
            if shape is None:
                return None
            # Search polymorphic cache
            for cached_shape, offset in self._poly_cache:
                if cached_shape == shape:
                    return offset
            return None

        else:  # MEGAMORPHIC
            return None

    def __repr__(self):
        """String representation for debugging."""
        return f"InlineCache(type={self.cache_type}, state={self._state})"
