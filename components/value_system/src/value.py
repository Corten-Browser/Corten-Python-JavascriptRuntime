"""
Value class - tagged pointer representation for JavaScript values.

This module implements the Value class which uses tagged pointers
to efficiently represent JavaScript values with SMI (Small Integer)
optimization.

Tagged Pointer Encoding:
    - SMI: Tag in low 2 bits = 0b00, value in upper bits (30-bit signed)
    - Object: Tag in low 2 bits = 0b01, pointer/id in upper bits
"""

from typing import Any


# Tag masks and values
TAG_MASK = 0b11  # Mask for extracting tag from low 2 bits
SMI_TAG = 0b00  # Tag for Small Integer
OBJECT_TAG = 0b01  # Tag for heap object

# Bit positions
TAG_BITS = 2  # Number of bits used for tag


class Value:
    """
    Tagged value representation supporting SMI and pointer types.

    This class provides an efficient representation for JavaScript values
    using tagged pointers. Small integers (SMI) are stored directly in
    the tagged value, while objects are stored on the heap with a
    reference in the tagged value.

    Attributes:
        _raw (int): Raw tagged pointer value containing type tag and data
    """

    def __init__(self, raw: int) -> None:
        """
        Create Value from raw tagged pointer.

        Args:
            raw: Raw tagged integer value (includes tag in low 2 bits)
        """
        self._raw = raw

    @staticmethod
    def from_smi(value: int) -> "Value":
        """
        Create SMI value from integer.

        Encodes the integer as a Small Integer (SMI) with tag 0b00.
        The integer value is shifted left by 2 bits to make room for
        the tag.

        Args:
            value: Integer value to encode (-2^29 to 2^29-1)

        Returns:
            Value object with SMI encoding

        Example:
            >>> v = Value.from_smi(42)
            >>> v.is_smi()
            True
            >>> v.to_smi()
            42
        """
        # Shift value left by TAG_BITS and add SMI_TAG
        raw = (value << TAG_BITS) | SMI_TAG
        return Value(raw)

    @staticmethod
    def from_object(obj: Any) -> "Value":
        """
        Create object value from heap reference.

        Encodes a Python object reference as a tagged pointer with
        tag 0b01. Uses Python's id() to get a unique identifier for
        the object, which is stored alongside the object in a registry.

        Args:
            obj: Python object reference to wrap

        Returns:
            Value object with object tag

        Example:
            >>> obj = {"key": "value"}
            >>> v = Value.from_object(obj)
            >>> v.is_object()
            True
            >>> v.to_object() is obj
            True
        """
        # Store object in registry and get ID
        obj_id = id(obj)
        _object_registry[obj_id] = obj

        # Encode object ID with OBJECT_TAG
        raw = (obj_id << TAG_BITS) | OBJECT_TAG
        return Value(raw)

    def is_smi(self) -> bool:
        """
        Check if value is SMI (Small Integer).

        Returns:
            True if value is SMI, False otherwise
        """
        return (self._raw & TAG_MASK) == SMI_TAG

    def is_object(self) -> bool:
        """
        Check if value is heap object.

        Returns:
            True if value is heap object, False otherwise
        """
        return (self._raw & TAG_MASK) == OBJECT_TAG

    def to_smi(self) -> int:
        """
        Extract SMI integer value.

        Returns:
            Integer value stored in SMI

        Raises:
            TypeError: If value is not SMI
        """
        if not self.is_smi():
            raise TypeError("Value is not an SMI (Small Integer)")

        # Extract value by shifting right by TAG_BITS
        # Need to handle sign extension for negative numbers
        value = self._raw >> TAG_BITS

        # Python's right shift automatically handles sign extension
        # for negative numbers, but we need to ensure proper 30-bit
        # signed integer representation
        return value

    def to_object(self) -> Any:
        """
        Extract heap object reference.

        Returns:
            Python object reference

        Raises:
            TypeError: If value is not object
        """
        if not self.is_object():
            raise TypeError("Value is not an object")

        # Extract object ID
        obj_id = self._raw >> TAG_BITS

        # Retrieve object from registry
        if obj_id not in _object_registry:
            raise RuntimeError(f"Object ID {obj_id} not found in registry")

        return _object_registry[obj_id]


# Global object registry to maintain references
# Maps object ID (from Python's id()) to actual object
_object_registry: dict[int, Any] = {}
