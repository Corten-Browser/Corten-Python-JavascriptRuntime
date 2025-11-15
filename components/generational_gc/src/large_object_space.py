"""
LargeObjectSpace - Separate space for large objects (>64KB).

Large objects are allocated in a separate space and collected
using mark-sweep (not copied during scavenge).
"""

from typing import Dict, List


class LargeObjectSpace:
    """
    Space for large objects (>64KB).

    Large objects are expensive to copy, so they are allocated in
    a separate space and collected using mark-sweep instead of
    being included in generational collection.

    Attributes:
        used_bytes (int): Total bytes used
        _objects (Dict[int, Dict]): Object metadata
        _next_ptr (int): Next allocation pointer

    Example:
        >>> los = LargeObjectSpace()
        >>> ptr = los.allocate(size=100 * 1024)  # 100KB
        >>> los.contains_object(ptr)
        True
    """

    # Threshold for large objects (64KB)
    LARGE_OBJECT_THRESHOLD = 64 * 1024

    def __init__(self) -> None:
        """
        Initialize empty large object space.
        """
        self.used_bytes = 0
        # Track objects: ptr -> {size: int, marked: bool}
        self._objects: Dict[int, Dict] = {}
        self._next_ptr = 0

    @property
    def object_count(self) -> int:
        """
        Get number of large objects.

        Returns:
            Number of allocated large objects
        """
        return len(self._objects)

    def allocate(self, size: int) -> int:
        """
        Allocate large object.

        Args:
            size: Object size in bytes (should be >64KB)

        Returns:
            Pointer to allocated object

        Raises:
            ValueError: If size is not positive

        Example:
            >>> los = LargeObjectSpace()
            >>> ptr = los.allocate(size=100 * 1024)
            >>> los.used_bytes
            102400
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        ptr = self._next_ptr
        self._next_ptr += size
        self.used_bytes += size

        self._objects[ptr] = {
            'size': size,
            'marked': False
        }

        return ptr

    def mark_sweep(self, roots: List[int]) -> int:
        """
        Perform mark-sweep collection on large objects.

        Args:
            roots: List of root pointers (reachable large objects)

        Returns:
            Number of bytes freed

        Example:
            >>> los = LargeObjectSpace()
            >>> ptr1 = los.allocate(size=100 * 1024)
            >>> ptr2 = los.allocate(size=200 * 1024)
            >>> bytes_freed = los.mark_sweep(roots=[ptr1])
            >>> bytes_freed
            204800
        """
        # Phase 1: Clear all mark bits
        for obj_meta in self._objects.values():
            obj_meta['marked'] = False

        # Phase 2: Mark reachable objects
        for root_ptr in roots:
            if root_ptr in self._objects:
                self._objects[root_ptr]['marked'] = True

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

        return bytes_freed

    def contains_object(self, ptr: int) -> bool:
        """
        Check if object exists in large object space.

        Args:
            ptr: Pointer to check

        Returns:
            True if object exists, False otherwise

        Example:
            >>> los = LargeObjectSpace()
            >>> ptr = los.allocate(size=100 * 1024)
            >>> los.contains_object(ptr)
            True
            >>> los.contains_object(9999)
            False
        """
        return ptr in self._objects

    def get_object_size(self, ptr: int) -> int:
        """
        Get size of large object.

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
        Get statistics for large object space.

        Returns:
            Dictionary with statistics:
                - used_bytes (int): Total bytes used
                - object_count (int): Number of large objects

        Example:
            >>> los = LargeObjectSpace()
            >>> los.allocate(size=100 * 1024)
            100000
            >>> stats = los.get_stats()
            >>> stats['object_count']
            1
        """
        return {
            'used_bytes': self.used_bytes,
            'object_count': self.object_count
        }

    def __repr__(self) -> str:
        """
        Get string representation.

        Returns:
            String showing bytes used and object count
        """
        return f"LargeObjectSpace(used={self.used_bytes}, objects={self.object_count})"
