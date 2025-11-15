"""
WriteBarrier - Track cross-generational pointers (old→young).

Executes on every pointer store from old generation objects to
record cross-generational references in the remembered set.
"""

from typing import Iterator

try:
    from .remembered_set import RememberedSet
except ImportError:
    from remembered_set import RememberedSet


class WriteBarrier:
    """
    Write barrier to track old generation → young generation pointers.

    The write barrier executes on every pointer store operation where
    an old generation object might reference a young generation object.
    It records these cross-generational pointers in the remembered set,
    which is used as additional roots during minor GC.

    Attributes:
        remembered_set (RememberedSet): Set of old→young pointers

    Example:
        >>> wb = WriteBarrier()
        >>> wb.record_pointer(from_ptr=1000, to_ptr=500)
        >>> wb.remembered_set.contains(1000)
        True
        >>> wb.clear()
        >>> len(wb.remembered_set)
        0
    """

    def __init__(self) -> None:
        """
        Initialize write barrier with empty remembered set.
        """
        self.remembered_set = RememberedSet()

    def record_pointer(self, from_ptr: int, to_ptr: int) -> None:
        """
        Record old→young pointer in remembered set.

        This is called by the write barrier when an old generation
        object is modified to reference a young generation object.

        Args:
            from_ptr: Pointer to old generation object
            to_ptr: Pointer to young generation object (not stored, just for documentation)

        Example:
            >>> wb = WriteBarrier()
            >>> wb.record_pointer(from_ptr=1000, to_ptr=500)
            >>> wb.remembered_set.contains(1000)
            True
        """
        self.remembered_set.add(from_ptr)

    def execute(self, obj_ptr: int, field_offset: int, value: int,
                is_old_gen: bool, is_value_young: bool) -> None:
        """
        Execute write barrier on pointer store.

        This is called BEFORE every pointer store operation. It checks
        if the store creates a cross-generational reference (old→young)
        and records it in the remembered set if so.

        Args:
            obj_ptr: Pointer to object being modified
            field_offset: Offset of field being stored to
            value: Value being stored (pointer)
            is_old_gen: True if obj_ptr is in old generation
            is_value_young: True if value points to young generation

        Example:
            >>> wb = WriteBarrier()
            >>> # Store young pointer into old object
            >>> wb.execute(obj_ptr=1000, field_offset=0, value=500,
            ...            is_old_gen=True, is_value_young=True)
            >>> wb.remembered_set.contains(1000)
            True
        """
        # Only record old→young pointers
        if is_old_gen and is_value_young:
            self.record_pointer(from_ptr=obj_ptr, to_ptr=value)

    def clear(self) -> None:
        """
        Clear remembered set after minor GC.

        This is called after minor GC completes. The remembered set
        will be repopulated by write barriers as cross-generational
        references are created.

        Example:
            >>> wb = WriteBarrier()
            >>> wb.record_pointer(from_ptr=1000, to_ptr=500)
            >>> wb.clear()
            >>> len(wb.remembered_set)
            0
        """
        self.remembered_set.clear()

    def get_remembered_pointers(self) -> Iterator[int]:
        """
        Get all pointers in remembered set.

        This is called during minor GC to get additional roots
        (old generation objects that reference young generation).

        Yields:
            Pointers to old generation objects with young references

        Example:
            >>> wb = WriteBarrier()
            >>> wb.record_pointer(from_ptr=1000, to_ptr=500)
            >>> wb.record_pointer(from_ptr=2000, to_ptr=600)
            >>> sorted(wb.get_remembered_pointers())
            [1000, 2000]
        """
        return self.remembered_set.iterate()

    def __repr__(self) -> str:
        """
        Get string representation.

        Returns:
            String showing remembered set size
        """
        return f"WriteBarrier(remembered_set_size={len(self.remembered_set)})"
