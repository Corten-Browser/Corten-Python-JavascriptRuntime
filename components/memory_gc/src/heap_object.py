"""
HeapObject base class for heap-allocated objects.

This is the base class for all objects allocated on the JavaScript heap.
Each object tracks its size and mark bit for garbage collection.
"""

from typing import List


class HeapObject:
    """
    Base class for all heap-allocated objects.

    HeapObject represents a JavaScript value stored on the heap. It tracks
    the object's size in bytes and a mark bit used during garbage collection.

    Attributes:
        marked (bool): GC mark bit. True if object is reachable, False otherwise.
        size (int): Size of object in bytes.

    Example:
        >>> obj = HeapObject(size=100)
        >>> obj.size
        100
        >>> obj.marked
        False
        >>> obj.marked = True
        >>> obj.marked
        True
    """

    def __init__(self, size: int, marked: bool = False):
        """
        Initialize HeapObject.

        Args:
            size: Size of object in bytes. Must be non-negative.
            marked: Initial mark bit value. Defaults to False (unmarked).

        Raises:
            ValueError: If size is negative.
        """
        if size < 0:
            raise ValueError(f"Size must be non-negative, got {size}")

        self.size = size
        self.marked = marked

    def get_references(self) -> List["HeapObject"]:
        """
        Return list of objects referenced by this object.

        This method is called during the mark phase of garbage collection
        to find all objects reachable from this object. Subclasses should
        override this method to return their actual references.

        Returns:
            List of HeapObject instances referenced by this object.
            Base implementation returns empty list.

        Example:
            >>> obj = HeapObject(size=100)
            >>> obj.get_references()
            []
        """
        return []
