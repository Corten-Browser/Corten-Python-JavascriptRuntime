"""
GarbageCollector - Mark-and-sweep garbage collection.

Implements a simple mark-and-sweep garbage collector for the JavaScript heap.
"""

import time
from typing import List, Set, Dict

try:
    from .heap_object import HeapObject
except ImportError:
    from heap_object import HeapObject


class GarbageCollector:
    """
    Simple mark-and-sweep garbage collector.

    The garbage collector manages a heap of objects and performs
    mark-and-sweep collection to reclaim memory from unreachable objects.

    Algorithm:
        1. Mark phase: Starting from roots, recursively mark all reachable objects
        2. Sweep phase: Remove all unmarked objects from heap

    Attributes:
        heap_size_bytes (int): Total heap size in bytes
        heap (Set[HeapObject]): Set of allocated objects
        roots (List[HeapObject]): List of GC roots (global variables, stack)
        used_bytes (int): Currently used heap memory in bytes

    Example:
        >>> gc = GarbageCollector(heap_size_mb=64)
        >>> obj = gc.allocate(100)
        >>> gc.add_root(obj)
        >>> stats = gc.collect()
        >>> print(f"Freed {stats['bytes_freed']} bytes")
    """

    def __init__(self, heap_size_mb: int = 64):
        """
        Initialize GarbageCollector.

        Args:
            heap_size_mb: Heap size in megabytes. Defaults to 64MB.

        Raises:
            ValueError: If heap_size_mb is not positive.
        """
        if heap_size_mb <= 0:
            raise ValueError(f"Heap size must be positive, got {heap_size_mb}")

        self.heap_size_bytes = heap_size_mb * 1024 * 1024
        self.heap: Set[HeapObject] = set()
        self.roots: List[HeapObject] = []
        self.used_bytes = 0

    def add_root(self, obj: HeapObject) -> None:
        """
        Add GC root.

        GC roots are objects that are always considered reachable,
        such as global variables and stack references.

        Args:
            obj: Object to add as root

        Example:
            >>> gc = GarbageCollector()
            >>> obj = gc.allocate(100)
            >>> gc.add_root(obj)
        """
        if obj not in self.roots:
            self.roots.append(obj)

    def remove_root(self, obj: HeapObject) -> None:
        """
        Remove GC root.

        Args:
            obj: Object to remove from roots

        Example:
            >>> gc = GarbageCollector()
            >>> obj = gc.allocate(100)
            >>> gc.add_root(obj)
            >>> gc.remove_root(obj)
        """
        if obj in self.roots:
            self.roots.remove(obj)

    def allocate(self, size: int) -> HeapObject:
        """
        Allocate object on heap.

        If allocation would exceed heap size, triggers garbage collection
        to try to free space. If GC cannot free enough space, raises MemoryError.

        Args:
            size: Size in bytes. Must be non-negative.

        Returns:
            Newly allocated HeapObject

        Raises:
            ValueError: If size is negative
            MemoryError: If allocation fails after GC

        Example:
            >>> gc = GarbageCollector()
            >>> obj = gc.allocate(100)
            >>> obj.size
            100
        """
        if size < 0:
            raise ValueError(f"Size must be non-negative, got {size}")

        # Check if we need to collect
        if self.used_bytes + size > self.heap_size_bytes:
            self.collect()

            # If still not enough space after GC
            if self.used_bytes + size > self.heap_size_bytes:
                raise MemoryError(
                    f"Cannot allocate {size} bytes. "
                    f"Heap: {self.used_bytes}/{self.heap_size_bytes} bytes used"
                )

        # Allocate object
        obj = HeapObject(size=size)
        self.heap.add(obj)
        self.used_bytes += size

        return obj

    def collect(self) -> Dict:
        """
        Perform mark-and-sweep garbage collection.

        Algorithm:
            1. Clear all mark bits
            2. Mark phase: Starting from roots, mark all reachable objects
            3. Sweep phase: Remove unmarked objects and free memory

        Returns:
            Dictionary with collection statistics:
                - objects_before (int): Object count before collection
                - objects_after (int): Object count after collection
                - bytes_freed (int): Bytes of memory freed
                - duration_ms (float): Collection duration in milliseconds

        Example:
            >>> gc = GarbageCollector()
            >>> obj = gc.allocate(100)
            >>> gc.add_root(obj)
            >>> stats = gc.collect()
            >>> stats['objects_after']
            1
        """
        start_time = time.perf_counter()

        objects_before = len(self.heap)
        bytes_before = self.used_bytes

        # Phase 1: Clear all mark bits
        for obj in self.heap:
            obj.marked = False

        # Phase 2: Mark reachable objects from roots
        for root in self.roots:
            self._mark(root)

        # Phase 3: Sweep unmarked objects
        to_remove = {obj for obj in self.heap if not obj.marked}
        bytes_freed = sum(obj.size for obj in to_remove)

        self.heap -= to_remove
        self.used_bytes -= bytes_freed

        objects_after = len(self.heap)
        duration_ms = (time.perf_counter() - start_time) * 1000

        return {
            "objects_before": objects_before,
            "objects_after": objects_after,
            "bytes_freed": bytes_freed,
            "duration_ms": duration_ms,
        }

    def _mark(self, obj: HeapObject) -> None:
        """
        Recursively mark object and all objects it references.

        This is the mark phase of mark-and-sweep. It traverses the object
        graph from the given object, marking all reachable objects.

        Args:
            obj: Object to mark

        Note:
            This is a recursive implementation. For very deep object graphs,
            an iterative implementation with explicit stack would be more robust.
        """
        # Already marked - avoid infinite recursion on cycles
        if obj.marked:
            return

        # Mark this object
        obj.marked = True

        # Recursively mark referenced objects
        for ref in obj.get_references():
            if ref in self.heap:  # Only mark if object is in our heap
                self._mark(ref)
