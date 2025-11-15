"""
Set implementation per ECMAScript 2024.

Requirements:
- FR-P3-038: Set constructor and basic methods
- FR-P3-039: Set value equality (SameValueZero)
- FR-P3-045: Set iteration (keys, values, entries, forEach)
- FR-P3-046: Insertion order preservation
- FR-P3-048: Set.prototype.size property
- FR-P3-049: Map/Set clear method

Features:
- Values can be any type (primitives, objects, functions, etc.)
- SameValueZero equality for values (+0 === -0, NaN === NaN)
- Insertion order preserved
- Efficient O(1) average-case operations
"""

from .hash_table import HashTable


class Set:
    """
    Set collection of unique values.

    Set stores unique values of any type.
    Values are compared using SameValueZero equality.
    Iteration order is insertion order.

    Attributes:
        size: Number of values in the Set
    """

    def __init__(self, iterable=None):
        """
        Create a new Set.

        Args:
            iterable: Optional iterable of values
        """
        self._table = HashTable()

        if iterable is not None:
            for value in iterable:
                self.add(value)

    @property
    def size(self):
        """
        Get the number of values in the Set.

        Returns:
            int: Number of values
        """
        return self._table.size

    def add(self, value):
        """
        Add a value to the Set.

        If the value already exists, the Set is not modified.

        Args:
            value: The value to add

        Returns:
            Set: this (for chaining)
        """
        # Use value as both key and value in hash table
        self._table.set(value, value)
        return self

    def has(self, value):
        """
        Check if a value exists in the Set.

        Args:
            value: The value to check

        Returns:
            bool: True if value exists
        """
        return self._table.has(value)

    def delete(self, value):
        """
        Remove a value from the Set.

        Args:
            value: The value to remove

        Returns:
            bool: True if value existed and was removed
        """
        return self._table.delete(value)

    def clear(self):
        """
        Remove all values from the Set.

        Returns:
            None (undefined)
        """
        self._table.clear()

    def keys(self):
        """
        Get an iterator over values (same as values() for Set).

        In JavaScript Set, keys() and values() return the same thing.

        Yields:
            Values in insertion order
        """
        return self._table.keys()

    def values(self):
        """
        Get an iterator over values in insertion order.

        Yields:
            Values in insertion order
        """
        return self._table.values()

    def entries(self):
        """
        Get an iterator over [value, value] pairs.

        For consistency with Map, Set.entries() returns [value, value] pairs.

        Yields:
            (value, value) tuples in insertion order
        """
        for value in self._table.keys():
            yield (value, value)

    def forEach(self, callback, this_arg=None):
        """
        Execute a callback for each value.

        The callback is called with (value, value, set) for each entry.
        Note: value appears twice for consistency with Map.

        Args:
            callback: Function to call for each value
                      Signature: callback(value, value, set)
            this_arg: Value to use as 'this' in callback (optional, Python doesn't use)

        Returns:
            None (undefined)
        """
        for value in self._table.keys():
            callback(value, value, self)

    def __iter__(self):
        """
        Make Set iterable. Returns values iterator.

        This allows using Set in for loops:
            for value in set:
                ...

        Yields:
            Values in insertion order
        """
        return self.values()

    def __repr__(self):
        """String representation for debugging."""
        values = list(self.values())
        return f"Set({values})"
