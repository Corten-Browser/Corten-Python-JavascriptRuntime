"""
WeakMap implementation per ECMAScript 2024.

Requirements:
- FR-P3-040: WeakMap constructor and methods
- FR-P3-041: WeakMap garbage collection behavior (weak references)
- FR-P3-050: WeakMap object-only keys

Features:
- Keys must be objects (primitives throw TypeError)
- Not enumerable (no size, no iteration)
- Weak references (entries GC'd when key unreachable)
- Values can be any type

Note: Full weak reference support requires integration with memory_gc component.
This implementation provides the correct API and will be enhanced with true
weak references when the GC component is integrated.
"""


class WeakMap:
    """
    WeakMap collection with object keys and weak references.

    WeakMap only accepts objects as keys. Primitive values throw TypeError.
    WeakMap is not enumerable - no size, no iteration.
    Keys are held as weak references and are garbage collected when no
    longer referenced elsewhere.

    Note: This implementation uses a simplified storage mechanism.
    True weak reference support requires memory_gc component integration.
    """

    def __init__(self, iterable=None):
        """
        Create a new WeakMap.

        Args:
            iterable: Optional iterable of [key, value] pairs

        Raises:
            TypeError: If any key in iterable is not an object
        """
        # Use dict with id(key) as the key for now
        # TODO: Replace with weak reference implementation when memory_gc available
        self._storage = {}

        if iterable is not None:
            for entry in iterable:
                if not isinstance(entry, (list, tuple)) or len(entry) != 2:
                    raise TypeError("Iterator value must be a key-value pair")
                key, value = entry
                self.set(key, value)

    def _validate_key(self, key):
        """
        Validate that key is an object.

        Args:
            key: The key to validate

        Raises:
            TypeError: If key is not an object
        """
        # In JavaScript, only objects can be WeakMap keys
        # Primitives: number, string, boolean, null, undefined, symbol
        # Objects: dict, list, function, class instances, etc.

        if key is None:
            raise TypeError("Invalid value used as weak map key")

        if isinstance(key, (int, float, str, bool)):
            raise TypeError("Invalid value used as weak map key")

        # If we get here, it's an object (dict, list, function, etc.)

    def set(self, key, value):
        """
        Add or update a key-value pair.

        Args:
            key: The key (must be an object)
            value: The value (any type)

        Returns:
            WeakMap: this (for chaining)

        Raises:
            TypeError: If key is not an object
        """
        self._validate_key(key)

        # Store using object identity
        # TODO: Replace with weak reference when memory_gc available
        key_id = id(key)
        self._storage[key_id] = (key, value)

        return self

    def get(self, key):
        """
        Get the value for a key.

        Args:
            key: The key (must be an object)

        Returns:
            The value if key exists, None (undefined) otherwise
        """
        # Don't validate for get - just return None if not an object
        if isinstance(key, (type(None), int, float, str, bool)):
            return None

        key_id = id(key)
        if key_id in self._storage:
            stored_key, value = self._storage[key_id]
            # Verify it's the same object (identity check)
            if stored_key is key:
                return value

        return None

    def has(self, key):
        """
        Check if a key exists in the WeakMap.

        Args:
            key: The key (must be an object)

        Returns:
            bool: True if key exists
        """
        # Don't validate for has - just return False if not an object
        if isinstance(key, (type(None), int, float, str, bool)):
            return False

        key_id = id(key)
        if key_id in self._storage:
            stored_key, _ = self._storage[key_id]
            # Verify it's the same object (identity check)
            return stored_key is key

        return False

    def delete(self, key):
        """
        Remove a key-value pair.

        Args:
            key: The key to remove (must be an object)

        Returns:
            bool: True if key existed and was removed
        """
        # Don't validate for delete - just return False if not an object
        if isinstance(key, (type(None), int, float, str, bool)):
            return False

        key_id = id(key)
        if key_id in self._storage:
            stored_key, _ = self._storage[key_id]
            # Verify it's the same object (identity check)
            if stored_key is key:
                del self._storage[key_id]
                return True

        return False

    def __repr__(self):
        """String representation for debugging."""
        # WeakMap is not enumerable, so we can't show contents
        return "WeakMap()"

    # WeakMap intentionally does NOT have:
    # - size property
    # - keys(), values(), entries() methods
    # - forEach() method
    # - __iter__() method
    # This is by design - WeakMap is not enumerable
