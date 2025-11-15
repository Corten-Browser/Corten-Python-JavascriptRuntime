"""
Property Inline Caches for optimized property access.

Provides PropertyLoadIC and PropertyStoreIC for fast property get/set operations.

Performance targets:
- Monomorphic hit: <5ns overhead vs direct access
- Polymorphic hit: <15ns overhead
- Cache hit rate: >90% for typical workloads
"""
from typing import Any
from .inline_cache import InlineCache
from ._shape_placeholder import Shape


class PropertyLoadIC(InlineCache):
    """
    Inline cache for property loads (obj.prop).

    Optimizes property reads by caching shape-to-offset mappings.
    Fast path avoids hash table lookup on cache hit.

    Example:
        ic = PropertyLoadIC()
        value = ic.load(obj, "propertyName")
        # First access: slow path, initializes cache
        # Subsequent accesses with same shape: fast path
    """

    def __init__(self):
        """Initialize property load IC."""
        super().__init__("property_load")

        # Statistics
        self._hits = 0
        self._misses = 0

    def load(self, obj: Any, prop_name: str) -> Any:
        """
        Load property with IC optimization.

        Args:
            obj: JavaScript object to load from
            prop_name: Property name

        Returns:
            Property value

        Performance:
            - Monomorphic hit: O(1) - single shape check + array access
            - Polymorphic hit: O(n) - linear search (n ≤ 4) + array access
            - Miss: O(1) - fallback to hash table lookup
        """
        # Get object shape (will use real Shape from hidden_classes later)
        obj_shape = self._get_object_shape(obj)

        # Check cache
        if self.check(obj_shape):
            # Cache hit: fast path
            self._hits += 1
            offset = self.get_cached_offset(obj_shape)
            return self._fast_load(obj, offset)
        else:
            # Cache miss: slow path
            self._misses += 1
            value, offset = self._slow_load(obj, prop_name)

            # Update cache with new shape/offset
            if offset is not None:
                self.update(obj_shape, offset)

            return value

    def _get_object_shape(self, obj: Any) -> Shape:
        """
        Get object's shape (hidden class).

        For now, creates a simple shape based on property keys.
        Will use real Shape from hidden_classes component later.

        Args:
            obj: JavaScript object

        Returns:
            Object's shape
        """
        # Cache shape on object for stability
        if hasattr(obj, '_cached_shape'):
            # Check if shape is still valid (same keys)
            if hasattr(obj, '_properties'):
                current_keys = frozenset(obj._properties.keys())
                if hasattr(obj, '_shape_keys') and obj._shape_keys == current_keys:
                    return obj._cached_shape

        # Create new shape
        if hasattr(obj, '_properties'):
            # Use sorted keys for consistent shape IDs
            sorted_keys = tuple(sorted(obj._properties.keys()))
            props = {key: i for i, key in enumerate(sorted_keys)}
            shape = Shape(props)

            # Cache shape on object
            obj._cached_shape = shape
            obj._shape_keys = frozenset(obj._properties.keys())
            return shape

        return Shape()

    def _fast_load(self, obj: Any, offset: int) -> Any:
        """
        Fast path: load property by offset.

        Args:
            obj: JavaScript object
            offset: Property offset in storage array

        Returns:
            Property value
        """
        # Fast access by offset (array indexing)
        # In future, will use obj.get_property_by_offset(offset)
        if hasattr(obj, '_properties'):
            # Use sorted keys to match shape offset
            sorted_keys = sorted(obj._properties.keys())
            if 0 <= offset < len(sorted_keys):
                key = sorted_keys[offset]
                return obj._properties[key]

        # Fallback - return undefined (will use real UNDEFINED_VALUE from object_runtime later)
        return obj.get_property("")  # Returns undefined for missing property

    def _slow_load(self, obj: Any, prop_name: str) -> tuple:
        """
        Slow path: load property by name (hash lookup).

        Args:
            obj: JavaScript object
            prop_name: Property name

        Returns:
            Tuple of (value, offset) where offset is None if property doesn't exist
        """
        # Slow hash table lookup
        value = obj.get_property(prop_name)

        # Get offset for caching (use sorted keys to match shape)
        if hasattr(obj, '_properties') and prop_name in obj._properties:
            sorted_keys = sorted(obj._properties.keys())
            offset = sorted_keys.index(prop_name)
        else:
            offset = None

        return value, offset

    def get_statistics(self) -> dict:
        """
        Get IC statistics.

        Returns:
            Dict with hits, misses, hit_rate, and state
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            'hits': self._hits,
            'misses': self._misses,
            'total': total,
            'hit_rate': hit_rate,
            'state': str(self.get_state())
        }


class PropertyStoreIC(InlineCache):
    """
    Inline cache for property stores (obj.prop = value).

    Optimizes property writes by caching shape-to-offset mappings.

    Example:
        ic = PropertyStoreIC()
        ic.store(obj, "propertyName", value)
        # First access: slow path, initializes cache
        # Subsequent accesses with same shape: fast path
    """

    def __init__(self):
        """Initialize property store IC."""
        super().__init__("property_store")

        # Statistics
        self._hits = 0
        self._misses = 0

    def store(self, obj: Any, prop_name: str, value: Any) -> None:
        """
        Store property with IC optimization.

        Args:
            obj: JavaScript object to store to
            prop_name: Property name
            value: Value to store

        Performance:
            - Monomorphic hit: O(1) - single shape check + array write
            - Polymorphic hit: O(n) - linear search (n ≤ 4) + array write
            - Miss: O(1) - fallback to hash table insert
        """
        # Get object shape
        obj_shape = self._get_object_shape(obj)

        # Check cache
        if self.check(obj_shape):
            # Cache hit: fast path
            self._hits += 1
            offset = self.get_cached_offset(obj_shape)
            self._fast_store(obj, offset, value)
        else:
            # Cache miss: slow path
            self._misses += 1
            offset = self._slow_store(obj, prop_name, value)

            # Update cache with new shape/offset
            if offset is not None:
                # Re-get shape after store (might have changed)
                obj_shape = self._get_object_shape(obj)
                self.update(obj_shape, offset)

    def _get_object_shape(self, obj: Any) -> Shape:
        """
        Get object's shape (hidden class).

        Args:
            obj: JavaScript object

        Returns:
            Object's shape
        """
        # Cache shape on object for stability
        if hasattr(obj, '_cached_shape'):
            # Check if shape is still valid (same keys)
            if hasattr(obj, '_properties'):
                current_keys = frozenset(obj._properties.keys())
                if hasattr(obj, '_shape_keys') and obj._shape_keys == current_keys:
                    return obj._cached_shape

        # Create new shape
        if hasattr(obj, '_properties'):
            # Use sorted keys for consistent shape IDs
            sorted_keys = tuple(sorted(obj._properties.keys()))
            props = {key: i for i, key in enumerate(sorted_keys)}
            shape = Shape(props)

            # Cache shape on object
            obj._cached_shape = shape
            obj._shape_keys = frozenset(obj._properties.keys())
            return shape

        return Shape()

    def _fast_store(self, obj: Any, offset: int, value: Any) -> None:
        """
        Fast path: store property by offset.

        Args:
            obj: JavaScript object
            offset: Property offset in storage array
            value: Value to store
        """
        # Fast access by offset (array indexing)
        if hasattr(obj, '_properties'):
            # Use sorted keys to match shape offset
            sorted_keys = sorted(obj._properties.keys())
            if 0 <= offset < len(sorted_keys):
                key = sorted_keys[offset]
                obj._properties[key] = value

    def _slow_store(self, obj: Any, prop_name: str, value: Any) -> int:
        """
        Slow path: store property by name (hash insert).

        Args:
            obj: JavaScript object
            prop_name: Property name
            value: Value to store

        Returns:
            Offset of stored property
        """
        # Slow hash table insert
        obj.set_property(prop_name, value)

        # Get offset for caching (use sorted keys to match shape)
        if hasattr(obj, '_properties') and prop_name in obj._properties:
            sorted_keys = sorted(obj._properties.keys())
            offset = sorted_keys.index(prop_name)
        else:
            offset = None

        return offset

    def get_statistics(self) -> dict:
        """
        Get IC statistics.

        Returns:
            Dict with hits, misses, hit_rate, and state
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            'hits': self._hits,
            'misses': self._misses,
            'total': total,
            'hit_rate': hit_rate,
            'state': str(self.get_state())
        }
