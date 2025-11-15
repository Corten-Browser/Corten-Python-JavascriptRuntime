"""
WeakSet implementation per ECMAScript 2024.

Requirements:
- FR-P3-042: WeakSet constructor and methods
- FR-P3-043: WeakSet garbage collection behavior (weak references)
- FR-P3-050: WeakSet object-only values

Features:
- Values must be objects (primitives throw TypeError)
- Not enumerable (no size, no iteration)
- Weak references (values GC'd when unreachable)

Note: Full weak reference support requires integration with memory_gc component.
This implementation provides the correct API and will be enhanced with true
weak references when the GC component is integrated.
"""


class WeakSet:
    """
    WeakSet collection of objects with weak references.

    WeakSet only accepts objects as values. Primitive values throw TypeError.
    WeakSet is not enumerable - no size, no iteration.
    Values are held as weak references and are garbage collected when no
    longer referenced elsewhere.

    Note: This implementation uses a simplified storage mechanism.
    True weak reference support requires memory_gc component integration.
    """

    def __init__(self, iterable=None):
        """
        Create a new WeakSet.

        Args:
            iterable: Optional iterable of values

        Raises:
            TypeError: If any value in iterable is not an object
        """
        # Use dict with id(value) as the key for now
        # TODO: Replace with weak reference implementation when memory_gc available
        self._storage = {}

        if iterable is not None:
            for value in iterable:
                self.add(value)

    def _validate_value(self, value):
        """
        Validate that value is an object.

        Args:
            value: The value to validate

        Raises:
            TypeError: If value is not an object
        """
        # In JavaScript, only objects can be WeakSet values
        # Primitives: number, string, boolean, null, undefined, symbol
        # Objects: dict, list, function, class instances, etc.

        if value is None:
            raise TypeError("Invalid value used in weak set")

        if isinstance(value, (int, float, str, bool)):
            raise TypeError("Invalid value used in weak set")

        # If we get here, it's an object (dict, list, function, etc.)

    def add(self, value):
        """
        Add a value to the WeakSet.

        Args:
            value: The value (must be an object)

        Returns:
            WeakSet: this (for chaining)

        Raises:
            TypeError: If value is not an object
        """
        self._validate_value(value)

        # Store using object identity
        # TODO: Replace with weak reference when memory_gc available
        value_id = id(value)
        self._storage[value_id] = value

        return self

    def has(self, value):
        """
        Check if a value exists in the WeakSet.

        Args:
            value: The value (must be an object)

        Returns:
            bool: True if value exists
        """
        # Don't validate for has - just return False if not an object
        if isinstance(value, (type(None), int, float, str, bool)):
            return False

        value_id = id(value)
        if value_id in self._storage:
            stored_value = self._storage[value_id]
            # Verify it's the same object (identity check)
            return stored_value is value

        return False

    def delete(self, value):
        """
        Remove a value from the WeakSet.

        Args:
            value: The value to remove (must be an object)

        Returns:
            bool: True if value existed and was removed
        """
        # Don't validate for delete - just return False if not an object
        if isinstance(value, (type(None), int, float, str, bool)):
            return False

        value_id = id(value)
        if value_id in self._storage:
            stored_value = self._storage[value_id]
            # Verify it's the same object (identity check)
            if stored_value is value:
                del self._storage[value_id]
                return True

        return False

    def __repr__(self):
        """String representation for debugging."""
        # WeakSet is not enumerable, so we can't show contents
        return "WeakSet()"

    # WeakSet intentionally does NOT have:
    # - size property
    # - keys(), values(), entries() methods
    # - forEach() method
    # - __iter__() method
    # This is by design - WeakSet is not enumerable
