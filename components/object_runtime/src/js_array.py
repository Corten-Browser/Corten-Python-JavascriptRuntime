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

    # ES2024 Array Methods - "Change Array by Copy" proposal

    def to_reversed(self) -> 'JSArray':
        """
        Return new array with elements in reversed order (non-mutating).

        ES2024 feature: Array.prototype.toReversed()
        Returns a new array with elements reversed, without modifying original.

        Returns:
            New JSArray with elements in reversed order

        Example:
            >>> arr = JSArray(gc)
            >>> arr.push(Value.from_smi(1))
            >>> arr.push(Value.from_smi(2))
            >>> reversed_arr = arr.to_reversed()
            >>> reversed_arr.get_element(0).to_smi()
            2
            >>> arr.get_element(0).to_smi()  # Original unchanged
            1
        """
        # Create new array with same length
        new_arr = JSArray(self._gc, length=self._length)

        # Copy elements in reversed order
        for i in range(self._length):
            if i in self._elements:
                new_arr.set_element(self._length - 1 - i, self._elements[i])

        return new_arr

    def to_sorted(self, compare_fn=None) -> 'JSArray':
        """
        Return new sorted array (non-mutating).

        ES2024 feature: Array.prototype.toSorted()
        Returns a new sorted array without modifying original.

        Args:
            compare_fn: Optional comparison function (a, b) -> int
                       Returns: <0 if a<b, 0 if a==b, >0 if a>b
                       If None, uses default numeric sorting

        Returns:
            New JSArray with elements sorted

        Example:
            >>> arr = JSArray(gc)
            >>> arr.push(Value.from_smi(3))
            >>> arr.push(Value.from_smi(1))
            >>> sorted_arr = arr.to_sorted()
            >>> sorted_arr.get_element(0).to_smi()
            1
        """
        # Create new array
        new_arr = JSArray(self._gc, length=self._length)

        # Get all elements
        elements = []
        for i in range(self._length):
            if i in self._elements:
                elements.append(self._elements[i])
            else:
                elements.append(UNDEFINED_VALUE)

        # Sort elements
        if compare_fn is None:
            # Default sort: numeric comparison for SMI values
            def default_compare(a, b):
                if a.is_smi() and b.is_smi():
                    a_val = a.to_smi()
                    b_val = b.to_smi()
                    if a_val < b_val:
                        return -1
                    elif a_val > b_val:
                        return 1
                    return 0
                return 0
            elements.sort(key=lambda x: (x.is_smi(), x.to_smi() if x.is_smi() else 0))
        else:
            # Use custom compare function
            from functools import cmp_to_key
            elements.sort(key=cmp_to_key(compare_fn))

        # Copy sorted elements to new array
        for i, elem in enumerate(elements):
            new_arr.set_element(i, elem)

        return new_arr

    def to_spliced(self, start: int, delete_count: int, *items) -> 'JSArray':
        """
        Return new array with elements removed/added (non-mutating splice).

        ES2024 feature: Array.prototype.toSpliced()
        Like splice() but returns new array without modifying original.

        Args:
            start: Index at which to start changing the array
            delete_count: Number of elements to remove
            *items: Elements to add to the array

        Returns:
            New JSArray with specified changes

        Example:
            >>> arr = JSArray(gc)
            >>> for i in [1,2,3,4]: arr.push(Value.from_smi(i))
            >>> spliced = arr.to_spliced(1, 2, Value.from_smi(10))
            >>> spliced.get_element(1).to_smi()
            10
        """
        # Normalize start index
        if start < 0:
            start = max(0, self._length + start)
        else:
            start = min(start, self._length)

        # Normalize delete_count
        delete_count = max(0, min(delete_count, self._length - start))

        # Calculate new length
        new_length = self._length - delete_count + len(items)

        # Create new array
        new_arr = JSArray(self._gc)

        # Copy elements before start
        for i in range(start):
            if i in self._elements:
                new_arr.push(self._elements[i])
            else:
                new_arr.push(UNDEFINED_VALUE)

        # Add new items
        for item in items:
            new_arr.push(item)

        # Copy elements after deleted range
        for i in range(start + delete_count, self._length):
            if i in self._elements:
                new_arr.push(self._elements[i])
            else:
                new_arr.push(UNDEFINED_VALUE)

        return new_arr

    def with_element(self, index: int, value: Value) -> 'JSArray':
        """
        Return new array with one element replaced (non-mutating).

        ES2024 feature: Array.prototype.with()
        Returns a new array with element at index replaced by value.

        Args:
            index: Index of element to replace (supports negative indices)
            value: New value for the element

        Returns:
            New JSArray with element replaced

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> arr = JSArray(gc)
            >>> arr.push(Value.from_smi(1))
            >>> arr.push(Value.from_smi(2))
            >>> new_arr = arr.with_element(1, Value.from_smi(99))
            >>> new_arr.get_element(1).to_smi()
            99
            >>> arr.get_element(1).to_smi()  # Original unchanged
            2
        """
        # Normalize negative index
        if index < 0:
            index = self._length + index

        # Validate index
        if index < 0 or index >= self._length:
            raise IndexError(f"Index {index} out of bounds for array of length {self._length}")

        # Create new array
        new_arr = JSArray(self._gc, length=self._length)

        # Copy all elements
        for i in range(self._length):
            if i == index:
                new_arr.set_element(i, value)
            elif i in self._elements:
                new_arr.set_element(i, self._elements[i])
            else:
                new_arr.set_element(i, UNDEFINED_VALUE)

        return new_arr

    def find_last(self, predicate) -> Value:
        """
        Find last element matching predicate (search from end).

        ES2024 feature: Array.prototype.findLast()
        Searches array from end to beginning, returns first match found.

        Args:
            predicate: Function (value) -> bool to test each element

        Returns:
            Last matching element, or UNDEFINED_VALUE if not found

        Example:
            >>> arr = JSArray(gc)
            >>> for i in [1,2,3,4,5]: arr.push(Value.from_smi(i))
            >>> result = arr.find_last(lambda v: v.to_smi() > 3)
            >>> result.to_smi()
            5
        """
        # Search from end to beginning
        for i in range(self._length - 1, -1, -1):
            if i in self._elements:
                element = self._elements[i]
                if predicate(element):
                    return element

        return UNDEFINED_VALUE

    def find_last_index(self, predicate) -> int:
        """
        Find index of last element matching predicate (search from end).

        ES2024 feature: Array.prototype.findLastIndex()
        Searches array from end to beginning, returns index of first match.

        Args:
            predicate: Function (value) -> bool to test each element

        Returns:
            Index of last matching element, or -1 if not found

        Example:
            >>> arr = JSArray(gc)
            >>> for i in [1,2,3,4,5]: arr.push(Value.from_smi(i))
            >>> idx = arr.find_last_index(lambda v: v.to_smi() > 3)
            >>> idx
            4
        """
        # Search from end to beginning
        for i in range(self._length - 1, -1, -1):
            if i in self._elements:
                element = self._elements[i]
                if predicate(element):
                    return i

        return -1

    @staticmethod
    async def from_async(gc: GarbageCollector, async_iterable):
        """
        Create array from async iterable (static method).

        ES2024 feature: Array.fromAsync()
        Creates an array from an async iterable or async iterator.

        Args:
            gc: Garbage collector for array creation
            async_iterable: Async iterable or async iterator

        Returns:
            Promise<JSArray> - Array with all values from async iterable

        Example:
            >>> async def gen():
            ...     yield Value.from_smi(1)
            ...     yield Value.from_smi(2)
            >>> arr = await JSArray.from_async(gc, gen())
            >>> arr.get_element(0).to_smi()
            1
        """
        # Create new array
        result = JSArray(gc)

        # Iterate through async iterable
        async for item in async_iterable:
            result.push(item)

        return result
