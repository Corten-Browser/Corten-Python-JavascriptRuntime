"""
Complete DataView implementation for ES2024 compliance.
Implements FR-ES24-B-020 through FR-ES24-B-027.

DataView provides low-level interface for reading/writing multiple number types
in a binary ArrayBuffer with explicit endianness control.
"""

import struct
from typing import Optional


class DataView:
    """
    Low-level interface for reading and writing multiple number types in an ArrayBuffer.

    Supports all numeric types (Int8, Uint8, Int16, Uint16, Int32, Uint32, Float32, Float64)
    with configurable endianness (big-endian or little-endian).

    ES2024 Specification Compliance:
    - FR-ES24-B-020: DataView constructor
    - FR-ES24-B-021: All 8 get methods
    - FR-ES24-B-022: All 8 set methods
    - FR-ES24-B-023: Endianness support
    - FR-ES24-B-024: Boundary checking
    - FR-ES24-B-025: Partial buffer views
    - FR-ES24-B-026: Detached buffer handling
    - FR-ES24-B-027: Properties (buffer, byteOffset, byteLength)
    """

    def __init__(self, buffer, byteOffset: int = 0, byteLength: Optional[int] = None):
        """
        Create a DataView for an ArrayBuffer.

        Args:
            buffer: ArrayBuffer to create view of
            byteOffset: Offset in bytes from start of buffer (default 0)
            byteLength: Length of view in bytes (default: remaining buffer)

        Raises:
            TypeError: If buffer is not an ArrayBuffer
            RangeError: If byteOffset or byteLength is invalid
        """
        # Import here to avoid circular dependency issues
        # Check for ArrayBuffer from typed_arrays module
        from array_buffer import ArrayBuffer

        if not isinstance(buffer, ArrayBuffer):
            from exceptions import TypeError as JSTypeError
            raise JSTypeError("First argument to DataView constructor must be an ArrayBuffer")

        # Convert byteOffset to integer
        byteOffset = int(byteOffset)

        # Validate byteOffset
        if byteOffset < 0 or byteOffset > buffer.byteLength:
            from exceptions import RangeError
            raise RangeError("Start offset is outside the bounds of the buffer")

        # Calculate byteLength
        if byteLength is None:
            byteLength = buffer.byteLength - byteOffset
        else:
            byteLength = int(byteLength)

        # Validate byteLength
        if byteLength < 0:
            from exceptions import RangeError
            raise RangeError("Invalid DataView length")

        if byteOffset + byteLength > buffer.byteLength:
            from exceptions import RangeError
            raise RangeError("Invalid DataView length")

        # Store properties (cached at construction - won't change even if buffer detaches)
        self._buffer = buffer
        self._byteOffset = byteOffset
        self._byteLength = byteLength

    @property
    def buffer(self):
        """
        The ArrayBuffer referenced by this view.
        Read-only property that returns cached value even if buffer is detached.
        """
        return self._buffer

    @property
    def byteOffset(self):
        """
        The offset (in bytes) of this view from the start of its ArrayBuffer.
        Read-only property that returns cached value even if buffer is detached.
        """
        return self._byteOffset

    @property
    def byteLength(self):
        """
        The length (in bytes) of this view.
        Read-only property that returns cached value even if buffer is detached.
        """
        return self._byteLength

    def _check_bounds(self, byteOffset: int, size: int, operation: str) -> int:
        """
        Check if read/write operation is within bounds.

        Args:
            byteOffset: Offset within the view
            size: Number of bytes to access
            operation: Name of operation (for error messages)

        Returns:
            Integer byte offset

        Raises:
            TypeError: If buffer is detached
            RangeError: If access would be out of bounds
        """
        from exceptions import TypeError as JSTypeError, RangeError

        # Check if buffer is detached
        if self._buffer.detached:
            raise JSTypeError(f"Cannot perform {operation} on a detached ArrayBuffer")

        # Convert to integer
        byteOffset = int(byteOffset)

        # Check bounds
        if byteOffset < 0 or byteOffset + size > self._byteLength:
            raise RangeError("Offset is outside the bounds of the DataView")

        return byteOffset

    # ========== GETTER METHODS (8 total) ==========

    def getInt8(self, byteOffset: int) -> int:
        """
        Get signed 8-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view

        Returns:
            Signed 8-bit integer (-128 to 127)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 1, "getInt8")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 1)
        return struct.unpack('b', raw_bytes)[0]

    def getUint8(self, byteOffset: int) -> int:
        """
        Get unsigned 8-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view

        Returns:
            Unsigned 8-bit integer (0 to 255)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 1, "getUint8")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 1)
        return struct.unpack('B', raw_bytes)[0]

    def getInt16(self, byteOffset: int, littleEndian: bool = False) -> int:
        """
        Get signed 16-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            Signed 16-bit integer (-32768 to 32767)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+1 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 2, "getInt16")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 2)

        fmt = '<h' if littleEndian else '>h'
        return struct.unpack(fmt, raw_bytes)[0]

    def getUint16(self, byteOffset: int, littleEndian: bool = False) -> int:
        """
        Get unsigned 16-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            Unsigned 16-bit integer (0 to 65535)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+1 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 2, "getUint16")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 2)

        fmt = '<H' if littleEndian else '>H'
        return struct.unpack(fmt, raw_bytes)[0]

    def getInt32(self, byteOffset: int, littleEndian: bool = False) -> int:
        """
        Get signed 32-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            Signed 32-bit integer (-2147483648 to 2147483647)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "getInt32")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<i' if littleEndian else '>i'
        return struct.unpack(fmt, raw_bytes)[0]

    def getUint32(self, byteOffset: int, littleEndian: bool = False) -> int:
        """
        Get unsigned 32-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            Unsigned 32-bit integer (0 to 4294967295)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "getUint32")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<I' if littleEndian else '>I'
        return struct.unpack(fmt, raw_bytes)[0]

    def getFloat32(self, byteOffset: int, littleEndian: bool = False) -> float:
        """
        Get 32-bit floating point number at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            32-bit floating point number (IEEE-754 single precision)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "getFloat32")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<f' if littleEndian else '>f'
        return struct.unpack(fmt, raw_bytes)[0]

    def getFloat64(self, byteOffset: int, littleEndian: bool = False) -> float:
        """
        Get 64-bit floating point number at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            littleEndian: If True, read as little-endian; if False, read as big-endian (default)

        Returns:
            64-bit floating point number (IEEE-754 double precision)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+7 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 8, "getFloat64")
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 8)

        fmt = '<d' if littleEndian else '>d'
        return struct.unpack(fmt, raw_bytes)[0]

    # ========== SETTER METHODS (8 total) ==========

    def setInt8(self, byteOffset: int, value) -> None:
        """
        Set signed 8-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to signed 8-bit integer)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 1, "setInt8")
        value = int(value)

        # Wrap to -128..127 (ToInt8 conversion)
        value = value % 256
        if value >= 128:
            value -= 256

        encoded = struct.pack('b', value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setUint8(self, byteOffset: int, value) -> None:
        """
        Set unsigned 8-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to unsigned 8-bit integer)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 1, "setUint8")
        value = int(value)

        # Wrap to 0..255 (ToUint8 conversion)
        value = value % 256

        encoded = struct.pack('B', value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setInt16(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set signed 16-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to signed 16-bit integer)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+1 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 2, "setInt16")
        value = int(value)

        # Wrap to -32768..32767 (ToInt16 conversion)
        value = value % 65536
        if value >= 32768:
            value -= 65536

        fmt = '<h' if littleEndian else '>h'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setUint16(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set unsigned 16-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to unsigned 16-bit integer)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+1 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 2, "setUint16")
        value = int(value)

        # Wrap to 0..65535 (ToUint16 conversion)
        value = value % 65536

        fmt = '<H' if littleEndian else '>H'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setInt32(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set signed 32-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to signed 32-bit integer)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "setInt32")
        value = int(value)

        # Wrap to -2147483648..2147483647 (ToInt32 conversion)
        value = value % 4294967296
        if value >= 2147483648:
            value -= 4294967296

        fmt = '<i' if littleEndian else '>i'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setUint32(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set unsigned 32-bit integer at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to unsigned 32-bit integer)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "setUint32")
        value = int(value)

        # Wrap to 0..4294967295 (ToUint32 conversion)
        value = value % 4294967296

        fmt = '<I' if littleEndian else '>I'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setFloat32(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set 32-bit floating point number at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to 32-bit float)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+3 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 4, "setFloat32")
        value = float(value)

        fmt = '<f' if littleEndian else '>f'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    def setFloat64(self, byteOffset: int, value, littleEndian: bool = False) -> None:
        """
        Set 64-bit floating point number at specified byte offset.

        Args:
            byteOffset: Byte offset from start of view
            value: Value to set (converted to 64-bit float)
            littleEndian: If True, write as little-endian; if False, write as big-endian (default)

        Raises:
            TypeError: If buffer is detached
            RangeError: If byteOffset+7 is out of bounds
        """
        byteOffset = self._check_bounds(byteOffset, 8, "setFloat64")
        value = float(value)

        fmt = '<d' if littleEndian else '>d'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)
