"""
YoungGeneration - Nursery space for newly allocated objects.

Implements bump-pointer allocation for fast object creation and
semi-space copying collection for fast minor GC.
"""

from typing import Dict, Optional


class YoungGeneration:
    """
    Nursery space for newly allocated objects.

    Uses bump-pointer allocation for very fast allocation (O(1)).
    Objects are allocated sequentially in memory until the space
    is full, then a minor GC (scavenge) is triggered.

    Attributes:
        size (int): Total size in bytes
        used_bytes (int): Currently used bytes
        free_bytes (int): Available bytes
        _allocation_pointer (int): Current allocation pointer
        _objects (Dict[int, Dict]): Object metadata (ptr -> {size, age})

    Example:
        >>> young_gen = YoungGeneration(size=8 * 1024 * 1024)  # 8MB
        >>> ptr = young_gen.allocate(100)
        >>> young_gen.used_bytes
        100
        >>> young_gen.is_full()
        False
    """

    # Default size: 8MB
    DEFAULT_SIZE = 8 * 1024 * 1024

    # Trigger GC when >90% full
    FULL_THRESHOLD = 0.9

    def __init__(self, size: int = DEFAULT_SIZE) -> None:
        """
        Initialize young generation space.

        Args:
            size: Size in bytes (default: 8MB)

        Raises:
            ValueError: If size is not positive
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        self.size = size
        self.used_bytes = 0
        self._allocation_pointer = 0
        # Track objects: ptr -> {size: int, age: int}
        self._objects: Dict[int, Dict] = {}

    @property
    def free_bytes(self) -> int:
        """
        Get number of free bytes.

        Returns:
            Number of bytes available for allocation
        """
        return self.size - self.used_bytes

    def allocate(self, size: int) -> Optional[int]:
        """
        Allocate object using bump-pointer allocation.

        This is very fast (O(1)) - just increment the allocation pointer.

        Args:
            size: Object size in bytes

        Returns:
            Pointer to allocated object, or None if not enough space

        Raises:
            ValueError: If size is not positive

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> ptr1 = young_gen.allocate(100)
            >>> ptr2 = young_gen.allocate(200)
            >>> ptr2 > ptr1  # Sequential allocation
            True
        """
        if size <= 0:
            raise ValueError(f"size must be positive, got {size}")

        # Check if we have space
        if self.used_bytes + size > self.size:
            return None

        # Bump-pointer allocation (very fast!)
        ptr = self._allocation_pointer
        self._allocation_pointer += size
        self.used_bytes += size

        # Track object metadata
        self._objects[ptr] = {
            'size': size,
            'age': 0
        }

        return ptr

    def is_full(self) -> bool:
        """
        Check if young generation is full.

        Considered "full" when utilization exceeds FULL_THRESHOLD (90%).
        This triggers minor GC before actually running out of space.

        Returns:
            True if should trigger GC, False otherwise

        Example:
            >>> young_gen = YoungGeneration(size=1000)
            >>> young_gen.allocate(950)
            950
            >>> young_gen.is_full()
            True
        """
        utilization = self.used_bytes / self.size
        return utilization >= self.FULL_THRESHOLD

    def reset(self) -> None:
        """
        Reset young generation after scavenge.

        This is called after minor GC completes. All live objects
        have been copied out, so we can reset the allocation pointer
        and reclaim all space.

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> young_gen.allocate(500)
            500
            >>> young_gen.reset()
            >>> young_gen.used_bytes
            0
        """
        self._allocation_pointer = 0
        self.used_bytes = 0
        self._objects.clear()

    def contains_object(self, ptr: int) -> bool:
        """
        Check if object exists in young generation.

        Args:
            ptr: Pointer to check

        Returns:
            True if object exists, False otherwise

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> ptr = young_gen.allocate(100)
            >>> young_gen.contains_object(ptr)
            True
            >>> young_gen.contains_object(9999)
            False
        """
        return ptr in self._objects

    def get_object_age(self, ptr: int) -> int:
        """
        Get age of object (number of GCs survived).

        Args:
            ptr: Pointer to object

        Returns:
            Age of object (0 for newly allocated)

        Raises:
            KeyError: If object doesn't exist

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> ptr = young_gen.allocate(100)
            >>> young_gen.get_object_age(ptr)
            0
        """
        return self._objects[ptr]['age']

    def increment_object_age(self, ptr: int) -> None:
        """
        Increment age of object after it survives GC.

        This is called during scavenge for objects that are copied
        to the to-space instead of promoted.

        Args:
            ptr: Pointer to object

        Raises:
            KeyError: If object doesn't exist

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> ptr = young_gen.allocate(100)
            >>> young_gen.increment_object_age(ptr)
            >>> young_gen.get_object_age(ptr)
            1
        """
        self._objects[ptr]['age'] += 1

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
        Get statistics for young generation.

        Returns:
            Dictionary with statistics:
                - size (int): Total size in bytes
                - used_bytes (int): Currently used bytes
                - free_bytes (int): Available bytes
                - utilization (float): Used / total (0.0 to 1.0)
                - object_count (int): Number of allocated objects

        Example:
            >>> young_gen = YoungGeneration(size=1024)
            >>> young_gen.allocate(256)
            256
            >>> stats = young_gen.get_stats()
            >>> stats['utilization']
            0.25
        """
        return {
            'size': self.size,
            'used_bytes': self.used_bytes,
            'free_bytes': self.free_bytes,
            'utilization': self.used_bytes / self.size,
            'object_count': len(self._objects)
        }

    def get_all_objects(self) -> Dict[int, Dict]:
        """
        Get all objects in young generation.

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
        util = (self.used_bytes / self.size) * 100
        return f"YoungGeneration(size={self.size}, used={self.used_bytes}, util={util:.1f}%)"
