"""
JSArray - JavaScript array implementation.

This module provides the JSArray class which extends JSObject
to implement JavaScript array semantics.
"""

from typing import Dict, List
from components.memory_gc.src import GarbageCollector, HeapObject
from components.value_system.src import Value
from js_object import JSObject, UNDEFINED_VALUE


class JSArray(JSObject):
    """
    JavaScript array extending JSObject.

    JSArray implements JavaScript array behavior with integer-indexed
    elements and a dynamic length property.

    Attributes:
        _elements (Dict[int, Value]): Element storage (index -> value)
        _length (int): Current array length

    Example:
        >>> gc = GarbageCollector()
        >>> arr = JSArray(gc)
        >>> arr.push(Value.from_smi(42))
        1
        >>> arr.get_element(0).to_smi()
        42
    """

    def __init__(self, gc: GarbageCollector, length: int = 0):
        """
        Initialize JSArray.

        Args:
            gc: Garbage collector managing this array
            length: Initial array length. Defaults to 0.

        Raises:
            ValueError: If length is negative
        """
        if length < 0:
            raise ValueError(f"Array length must be non-negative, got {length}")

        # Initialize parent JSObject
        super().__init__(gc)

        # Array-specific storage
        self._elements: Dict[int, Value] = {}
        self._length: int = length

        # Set length property
        self.set_property("length", Value.from_smi(length))

        # Update size estimate for array elements
        self.size = 100 + (length * 8)  # Base + 8 bytes per element
        gc.used_bytes += length * 8  # Add the extra array size

    def get_element(self, index: int) -> Value:
        """
        Get array element at index.

        Args:
            index: Array index (must be non-negative)

        Returns:
            Value at index, or undefined if out of bounds

        Example:
            >>> arr.set_element(5, Value.from_smi(100))
            >>> arr.get_element(5).to_smi()
            100
        """
        if index < 0 or index >= self._length:
            return UNDEFINED_VALUE

        if index in self._elements:
            return self._elements[index]

        return UNDEFINED_VALUE

    def set_element(self, index: int, value: Value) -> None:
        """
        Set array element at index.

        Automatically extends array length if index >= length.

        Args:
            index: Array index (must be non-negative)
            value: Value to store

        Raises:
            ValueError: If index is negative

        Example:
            >>> arr.set_element(0, Value.from_smi(42))
            >>> arr.get_element(0).to_smi()
            42
        """
        if index < 0:
            raise ValueError(f"Array index must be non-negative, got {index}")

        # Store element
        self._elements[index] = value

        # Update length if necessary
        if index >= self._length:
            old_length = self._length
            self._length = index + 1
            self.set_property("length", Value.from_smi(self._length))

            # Update size estimate
            added_size = (self._length - old_length) * 8
            self.size += added_size
            self._gc.used_bytes += added_size

    def push(self, value: Value) -> int:
        """
        Push element to end of array.

        Args:
            value: Value to push

        Returns:
            New array length

        Example:
            >>> arr = JSArray(gc)
            >>> arr.push(Value.from_smi(1))
            1
            >>> arr.push(Value.from_smi(2))
            2
        """
        self.set_element(self._length, value)
        return self._length

    def pop(self) -> Value:
        """
        Pop element from end of array.

        Returns:
            Popped value, or undefined if array is empty

        Example:
            >>> arr.push(Value.from_smi(42))
            1
            >>> arr.pop().to_smi()
            42
        """
        if self._length == 0:
            return UNDEFINED_VALUE

        # Get last element
        last_index = self._length - 1
        value = self.get_element(last_index)

        # Remove element
        if last_index in self._elements:
            del self._elements[last_index]

        # Update length
        self._length -= 1
        self.set_property("length", Value.from_smi(self._length))

        # Update size estimate
        self.size -= 8
        self._gc.used_bytes -= 8

        return value

    def get_references(self) -> List[HeapObject]:
        """
        Get list of heap objects referenced by this array.

        Returns:
            List containing prototype and any object-typed elements

        Example:
            >>> proto = JSObject(gc)
            >>> arr = JSArray(gc, prototype=proto)
            >>> proto in arr.get_references()
            True
        """
        refs = super().get_references()

        # Add object-typed array elements
        for value in self._elements.values():
            if value.is_object():
                obj = value.to_object()
                if isinstance(obj, HeapObject):
                    refs.append(obj)

        return refs
