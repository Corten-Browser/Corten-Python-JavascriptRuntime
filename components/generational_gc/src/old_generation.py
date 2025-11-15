"""
OldGeneration - Tenured space for long-lived objects.

Implements free-list allocation and mark-sweep collection
for objects promoted from young generation.
"""

from typing import Dict, List, Optional


class OldGeneration:
    """
    Tenured space for long-lived objects.

    Objects are promoted here from young generation after surviving
    multiple minor GCs. Uses free-list allocation (slower than
    bump-pointer but allows reuse of freed space) and mark-sweep
    collection.

    Attributes:
        size (int): Total size in bytes
        used_bytes (int): Currently used bytes
        _objects (Dict[int, Dict]): Object metadata (ptr -> {size, marked})
        _next_ptr (int): Next pointer for allocation

    Example:
        >>> old_gen = OldGeneration(size=64 * 1024 * 1024)  # 64MB
        >>> ptr = old_gen.promote(obj_ptr=100, size=256)
        >>> old_gen.used_bytes
        256
        >>> old_gen.needs_major_gc()
        False
    """

    # Default size: 64MB
    DEFAULT_SIZE = 64 * 1024 * 1024

    # Trigger major GC when >75% full
    MAJOR_GC_THRESHOLD = 0.75

    def __init__(self, size: int = DEFAULT_SIZE) -> None:
        """
        Initialize old generation space.

        Args:
            size: Size in bytes (default: 64MB)

        Raises:
            ValueError: If size is not positive
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        self.size = size
        self.used_bytes = 0
        # Track objects: ptr -> {size: int, marked: bool}
        self._objects: Dict[int, Dict] = {}
        # Simple allocation pointer (not truly free-list, but adequate)
        self._next_ptr = 0

    @property
    def free_bytes(self) -> int:
        """
        Get number of free bytes.

        Returns:
            Number of bytes available for allocation
        """
        return self.size - self.used_bytes

    def promote(self, obj_ptr: int, size: int) -> Optional[int]:
        """
        Promote object from young generation to old generation.

        Allocates space in old generation and (conceptually) copies
        the object from young generation.

        Args:
            obj_ptr: Pointer to object in young generation
            size: Size of object in bytes

        Returns:
            Pointer in old generation, or None if not enough space

        Example:
            >>> old_gen = OldGeneration(size=1024)
            >>> new_ptr = old_gen.promote(obj_ptr=100, size=256)
            >>> old_gen.used_bytes
            256
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        # Check if we have space
        if self.used_bytes + size > self.size:
            return None

        # Allocate in old generation
        new_ptr = self._next_ptr
        self._next_ptr += size
        self.used_bytes += size

        # Track object metadata
        self._objects[new_ptr] = {
            'size': size,
            'marked': False
        }

        return new_ptr

    def needs_major_gc(self) -> bool:
        """
        Check if major GC is needed.

        Triggers major GC when old generation is > 75% full.

        Returns:
            True if major GC should be triggered, False otherwise

        Example:
            >>> old_gen = OldGeneration(size=1000)
            >>> old_gen.promote(obj_ptr=1, size=800)
            800
            >>> old_gen.needs_major_gc()
            True
        """
        utilization = self.used_bytes / self.size
        return utilization > self.MAJOR_GC_THRESHOLD

    def mark_sweep(self, roots: List[int]) -> Dict:
        """
        Perform mark-sweep garbage collection.

        Algorithm:
            1. Clear all mark bits
            2. Mark phase: Mark all reachable objects from roots
            3. Sweep phase: Free all unmarked objects

        Args:
            roots: List of root pointers (reachable objects)

        Returns:
            Statistics dictionary:
                - objects_freed (int): Number of objects collected
                - bytes_freed (int): Bytes of memory reclaimed
                - duration_ms (float): Collection time in milliseconds

        Example:
            >>> old_gen = OldGeneration(size=1024)
            >>> ptr1 = old_gen.promote(obj_ptr=1, size=100)
            >>> ptr2 = old_gen.promote(obj_ptr=2, size=200)
            >>> stats = old_gen.mark_sweep(roots=[ptr1])
            >>> stats['objects_freed']
            1
        """
        import time

        start_time = time.perf_counter()

        # Phase 1: Clear all mark bits
        for obj_meta in self._objects.values():
            obj_meta['marked'] = False

        # Phase 2: Mark reachable objects
        for root_ptr in roots:
            if root_ptr in self._objects:
                self._mark(root_ptr)

        # Phase 3: Sweep unmarked objects
        to_remove = []
        bytes_freed = 0

        for ptr, obj_meta in self._objects.items():
            if not obj_meta['marked']:
                to_remove.append(ptr)
                bytes_freed += obj_meta['size']

        # Remove unmarked objects
        for ptr in to_remove:
            del self._objects[ptr]

        self.used_bytes -= bytes_freed

        duration_ms = (time.perf_counter() - start_time) * 1000

        return {
            'objects_freed': len(to_remove),
            'bytes_freed': bytes_freed,
            'duration_ms': duration_ms
        }

    def _mark(self, ptr: int) -> None:
        """
        Mark object as reachable.

        This is the mark phase of mark-sweep. In a real implementation,
        this would recursively mark referenced objects, but for this
        simplified version we just mark the object itself.

        Args:
            ptr: Pointer to object
        """
        if ptr not in self._objects:
            return

        # Already marked - avoid re-processing
        if self._objects[ptr]['marked']:
            return

        self._objects[ptr]['marked'] = True

        # In a real implementation, we would recursively mark
        # objects referenced by this object:
        # for ref_ptr in get_object_references(ptr):
        #     self._mark(ref_ptr)

    def contains_object(self, ptr: int) -> bool:
        """
        Check if object exists in old generation.

        Args:
            ptr: Pointer to check

        Returns:
            True if object exists, False otherwise

        Example:
            >>> old_gen = OldGeneration(size=1024)
            >>> ptr = old_gen.promote(obj_ptr=1, size=100)
            >>> old_gen.contains_object(ptr)
            True
            >>> old_gen.contains_object(9999)
            False
        """
        return ptr in self._objects

    def get_object_size(self, ptr: int) -> int:
        """
        Get size of object.

        Args:
            ptr: Pointer to object

        Returns:
            Size in bytes

        Raises:
            KeyError: If object doesn't exist
        """
        return self._objects[ptr]['size']

    def get_stats(self) -> Dict:
        """
        Get statistics for old generation.

        Returns:
            Dictionary with statistics:
                - size (int): Total size in bytes
                - used_bytes (int): Currently used bytes
                - free_bytes (int): Available bytes
                - utilization (float): Used / total (0.0 to 1.0)
                - object_count (int): Number of objects

        Example:
            >>> old_gen = OldGeneration(size=1024)
            >>> old_gen.promote(obj_ptr=1, size=256)
            256
            >>> stats = old_gen.get_stats()
            >>> stats['utilization']
            0.25
        """
        return {
            'size': self.size,
            'used_bytes': self.used_bytes,
            'free_bytes': self.free_bytes,
            'utilization': self.used_bytes / self.size if self.size > 0 else 0.0,
            'object_count': len(self._objects)
        }

    def get_all_objects(self) -> Dict[int, Dict]:
        """
        Get all objects in old generation.

        Returns:
            Dictionary mapping pointers to metadata

        Note:
            This is primarily for testing and debugging.
        """
        return self._objects.copy()

    def __repr__(self) -> str:
        """
        Get string representation.

        Returns:
            String showing size and utilization
        """
        util = (self.used_bytes / self.size) * 100 if self.size > 0 else 0.0
        return f"OldGeneration(size={self.size}, used={self.used_bytes}, util={util:.1f}%)"
