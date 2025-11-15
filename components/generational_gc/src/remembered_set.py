"""
RememberedSet - Track cross-generational pointers (old→young).

The remembered set tracks pointers from old generation objects to
young generation objects. This allows minor GC to avoid scanning
the entire old generation by only checking remembered pointers.
"""

from typing import Iterator, Set


class RememberedSet:
    """
    Set of cross-generational pointers (old generation → young generation).

    The remembered set is populated by write barriers when an old generation
    object is modified to point to a young generation object. During minor GC,
    the remembered set is used as additional roots to trace young objects
    referenced from old generation.

    Attributes:
        _pointers (Set[int]): Set of pointer values

    Example:
        >>> rs = RememberedSet()
        >>> rs.add(12345)  # Record old→young pointer
        >>> rs.contains(12345)
        True
        >>> list(rs.iterate())
        [12345]
        >>> rs.clear()  # Clear after minor GC
        >>> len(rs)
        0
    """

    def __init__(self) -> None:
        """
        Initialize empty remembered set.

        The set starts empty and is populated by write barriers
        during program execution.
        """
        self._pointers: Set[int] = set()

    def add(self, ptr: int) -> None:
        """
        Add pointer to remembered set.

        This is called by the write barrier when an old generation object
        is modified to reference a young generation object.

        Args:
            ptr: Pointer value to add (address of old gen object)

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.add(200)
            >>> len(rs)
            2
        """
        self._pointers.add(ptr)

    def remove(self, ptr: int) -> None:
        """
        Remove pointer from remembered set.

        This is called when a pointer is no longer valid (e.g., object
        was promoted to old generation or garbage collected).

        Args:
            ptr: Pointer value to remove

        Note:
            Removing a non-existent pointer does not raise an error.

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.remove(100)
            >>> len(rs)
            0
        """
        self._pointers.discard(ptr)

    def clear(self) -> None:
        """
        Clear all pointers from remembered set.

        This is typically called after a minor GC completes, as all
        cross-generational pointers will be re-recorded by write barriers
        if they still exist.

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.add(200)
            >>> rs.clear()
            >>> len(rs)
            0
        """
        self._pointers.clear()

    def contains(self, ptr: int) -> bool:
        """
        Check if pointer is in remembered set.

        Args:
            ptr: Pointer value to check

        Returns:
            True if pointer is in the set, False otherwise

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.contains(100)
            True
            >>> rs.contains(200)
            False
        """
        return ptr in self._pointers

    def iterate(self) -> Iterator[int]:
        """
        Iterate over all pointers in remembered set.

        Yields pointers in arbitrary order. The set can be modified
        during iteration, but this may affect which pointers are yielded.

        Yields:
            Pointer values in the set

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.add(200)
            >>> sorted(rs.iterate())
            [100, 200]
        """
        # Create a copy to allow safe iteration
        for ptr in list(self._pointers):
            yield ptr

    def __len__(self) -> int:
        """
        Get number of pointers in remembered set.

        Returns:
            Number of unique pointers

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> rs.add(200)
            >>> len(rs)
            2
        """
        return len(self._pointers)

    def __repr__(self) -> str:
        """
        Get string representation of remembered set.

        Returns:
            String showing number of pointers

        Example:
            >>> rs = RememberedSet()
            >>> rs.add(100)
            >>> repr(rs)
            'RememberedSet(size=1)'
        """
        return f"RememberedSet(size={len(self._pointers)})"
