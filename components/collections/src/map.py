"""
Map implementation per ECMAScript 2024.

Requirements:
- FR-P3-036: Map constructor and basic methods
- FR-P3-037: Map key equality (SameValueZero)
- FR-P3-044: Map iteration (keys, values, entries, forEach)
- FR-P3-046: Insertion order preservation
- FR-P3-047: Map.prototype.size property
- FR-P3-049: Map/Set clear method

Features:
- Keys can be any type (primitives, objects, functions, etc.)
- SameValueZero equality for keys (+0 === -0, NaN === NaN)
- Insertion order preserved
- Efficient O(1) average-case operations
"""

from .hash_table import HashTable


class Map:
    """
    Map collection with key-value pairs.

    Map allows any type of value as keys, including objects and functions.
    Keys are compared using SameValueZero equality.
    Iteration order is insertion order.

    Attributes:
        size: Number of key-value pairs in the Map
    """

    def __init__(self, iterable=None):
        """
        Create a new Map.

        Args:
            iterable: Optional iterable of [key, value] pairs
        """
        self._table = HashTable()

        if iterable is not None:
            for entry in iterable:
                if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                    raise TypeError("Iterator value must be a key-value pair")
                key, value = entry
                self.set(key, value)

    @property
    def size(self):
        """
        Get the number of key-value pairs in the Map.

        Returns:
            int: Number of entries
        """
        return self._table.size

    def set(self, key, value):
        """
        Add or update a key-value pair.

        Args:
            key: The key (any type)
            value: The value

        Returns:
            Map: this (for chaining)
        """
        self._table.set(key, value)
        return self

    def get(self, key):
        """
        Get the value for a key.

        Args:
            key: The key

        Returns:
            The value if key exists, None (undefined) otherwise
        """
        return self._table.get(key)

    def has(self, key):
        """
        Check if a key exists in the Map.

        Args:
            key: The key

        Returns:
            bool: True if key exists
        """
        return self._table.has(key)

    def delete(self, key):
        """
        Remove a key-value pair.

        Args:
            key: The key to remove

        Returns:
            bool: True if key existed and was removed
        """
        return self._table.delete(key)

    def clear(self):
        """
        Remove all key-value pairs from the Map.

        Returns:
            None (undefined)
        """
        self._table.clear()

    def keys(self):
        """
        Get an iterator over keys in insertion order.

        Yields:
            Keys in insertion order
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
        Get an iterator over [key, value] pairs in insertion order.

        Yields:
            (key, value) tuples in insertion order
        """
        return self._table.entries()

    def forEach(self, callback, this_arg=None):
        """
        Execute a callback for each key-value pair.

        The callback is called with (value, key, map) for each entry.
        Note: value comes before key (matches JavaScript Map.forEach).

        Args:
            callback: Function to call for each entry
                      Signature: callback(value, key, map)
            this_arg: Value to use as 'this' in callback (optional, Python doesn't use)

        Returns:
            None (undefined)
        """
        for key, value in self._table.entries():
            callback(value, key, self)

    def __iter__(self):
        """
        Make Map iterable. Returns entries iterator.

        This allows using Map in for loops:
            for key, value in map:
                ...

        Yields:
            (key, value) tuples in insertion order
        """
        return self.entries()

    def __repr__(self):
        """String representation for debugging."""
        entries = list(self.entries())
        return f"Map({entries})"
