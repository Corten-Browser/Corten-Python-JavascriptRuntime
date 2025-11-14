"""
Allocation functions for JavaScript types.

Provides high-level allocation functions for common JavaScript types:
objects, arrays, and strings.
"""

try:
    from .heap_object import HeapObject
    from .garbage_collector import GarbageCollector
except ImportError:
    from heap_object import HeapObject
    from garbage_collector import GarbageCollector


# Size estimates for JavaScript types (in bytes)
OBJECT_HEADER_SIZE = 32  # Base object overhead
PROPERTY_SIZE = 64  # Size per property (key + value pointer + metadata)
ARRAY_HEADER_SIZE = 48  # Array object overhead
ARRAY_ELEMENT_SIZE = 8  # Size per array element (pointer)
STRING_HEADER_SIZE = 24  # String object overhead
STRING_CHAR_SIZE = 2  # Size per character (UTF-16)


def AllocateObject(gc: GarbageCollector, property_count: int = 4) -> HeapObject:
    """
    Allocate JavaScript object.

    Allocates a heap object sized for a JavaScript object with the
    specified number of properties.

    Size calculation:
        - Base overhead: 32 bytes
        - Per property: 64 bytes (property name + value + metadata)
        - Total: 32 + (property_count * 64) bytes

    Args:
        gc: GarbageCollector to allocate from
        property_count: Estimated number of properties. Defaults to 4.

    Returns:
        Newly allocated HeapObject

    Raises:
        ValueError: If property_count is negative
        MemoryError: If allocation fails

    Example:
        >>> gc = GarbageCollector()
        >>> obj = AllocateObject(gc, property_count=5)
        >>> obj.size
        352
    """
    if property_count < 0:
        raise ValueError(f"Property count must be non-negative, got {property_count}")

    size = OBJECT_HEADER_SIZE + (property_count * PROPERTY_SIZE)
    return gc.allocate(size)


def AllocateArray(gc: GarbageCollector, length: int) -> HeapObject:
    """
    Allocate JavaScript array.

    Allocates a heap object sized for a JavaScript array with the
    specified length.

    Size calculation:
        - Base overhead: 48 bytes (array header)
        - Per element: 8 bytes (pointer to value)
        - Total: 48 + (length * 8) bytes

    Args:
        gc: GarbageCollector to allocate from
        length: Array length (number of elements)

    Returns:
        Newly allocated HeapObject

    Raises:
        ValueError: If length is negative
        MemoryError: If allocation fails

    Example:
        >>> gc = GarbageCollector()
        >>> arr = AllocateArray(gc, length=10)
        >>> arr.size
        128
    """
    if length < 0:
        raise ValueError(f"Array length must be non-negative, got {length}")

    size = ARRAY_HEADER_SIZE + (length * ARRAY_ELEMENT_SIZE)
    return gc.allocate(size)


def AllocateString(gc: GarbageCollector, value: str) -> HeapObject:
    """
    Allocate JavaScript string.

    Allocates a heap object sized for a JavaScript string with the
    specified value. Uses UTF-16 encoding (2 bytes per character).

    Size calculation:
        - Base overhead: 24 bytes (string header)
        - Per character: 2 bytes (UTF-16)
        - Total: 24 + (len(value) * 2) bytes

    Note: Some Unicode characters (outside BMP) may require surrogate
    pairs in UTF-16, taking 4 bytes. This is a simplified estimate.

    Args:
        gc: GarbageCollector to allocate from
        value: String value to allocate

    Returns:
        Newly allocated HeapObject

    Raises:
        MemoryError: If allocation fails

    Example:
        >>> gc = GarbageCollector()
        >>> s = AllocateString(gc, value="hello")
        >>> s.size
        34
    """
    # Calculate UTF-16 size (simplified - doesn't account for surrogate pairs)
    char_count = len(value)
    size = STRING_HEADER_SIZE + (char_count * STRING_CHAR_SIZE)
    return gc.allocate(size)
