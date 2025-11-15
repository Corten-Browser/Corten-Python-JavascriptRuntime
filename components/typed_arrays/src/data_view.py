"""
DataView implementation following ECMAScript 2024 specification.
Low-level interface for reading/writing binary data with endianness control.
"""

import struct
from array_buffer import ArrayBuffer
from exceptions import RangeError, TypeError as JSTypeError


class DataView:
    """
    Low-level interface for reading/writing binary data.
    Supports all numeric types with configurable endianness.
    """

    def __init__(self, buffer, byteOffset=0, byteLength=None):
        """
        Create DataView for ArrayBuffer.

        Args:
            buffer: ArrayBuffer to view
            byteOffset: Offset in bytes (default 0)
            byteLength: Length in bytes (default remaining buffer)
        """
        if not isinstance(buffer, ArrayBuffer):
            raise JSTypeError("DataView requires ArrayBuffer")

        byteOffset = int(byteOffset)
        if byteOffset < 0 or byteOffset > buffer.byteLength:
            raise RangeError(f"Byte offset {byteOffset} out of range")

        if byteLength is None:
            byteLength = buffer.byteLength - byteOffset
        else:
            byteLength = int(byteLength)
            if byteLength < 0:
                raise RangeError(f"Invalid byte length: {byteLength}")

        if byteOffset + byteLength > buffer.byteLength:
            raise RangeError(
                f"DataView extends beyond buffer "
                f"({byteOffset + byteLength} > {buffer.byteLength})"
            )

        self._buffer = buffer
        self._byteOffset = byteOffset
        self._byteLength = byteLength

    @property
    def buffer(self):
        """Underlying ArrayBuffer"""
        return self._buffer

    @property
    def byteLength(self):
        """Length in bytes"""
        if self._buffer.detached:
            return 0
        return self._byteLength

    @property
    def byteOffset(self):
        """Offset in buffer (bytes)"""
        if self._buffer.detached:
            return 0
        return self._byteOffset

    def _check_bounds(self, byteOffset, size):
        """Validate byte offset is within view bounds"""
        if self._buffer.detached:
            raise JSTypeError("Cannot access detached ArrayBuffer")

        byteOffset = int(byteOffset)
        if byteOffset < 0 or byteOffset + size > self._byteLength:
            raise RangeError(
                f"Byte offset {byteOffset} + size {size} exceeds view bounds {self._byteLength}"
            )

        return byteOffset

    # Int8 getters/setters
    def getInt8(self, byteOffset):
        """Get signed 8-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 1)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 1)
        return struct.unpack('b', raw_bytes)[0]

    def setInt8(self, byteOffset, value):
        """Set signed 8-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 1)
        value = int(value)
        # Wrap to -128..127
        value = (value % 256)
        if value >= 128:
            value -= 256
        encoded = struct.pack('b', value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Uint8 getters/setters
    def getUint8(self, byteOffset):
        """Get unsigned 8-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 1)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 1)
        return struct.unpack('B', raw_bytes)[0]

    def setUint8(self, byteOffset, value):
        """Set unsigned 8-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 1)
        value = int(value) % 256  # Wrap to 0..255
        encoded = struct.pack('B', value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Int16 getters/setters
    def getInt16(self, byteOffset, littleEndian=False):
        """Get signed 16-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 2)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 2)

        fmt = '<h' if littleEndian else '>h'
        return struct.unpack(fmt, raw_bytes)[0]

    def setInt16(self, byteOffset, value, littleEndian=False):
        """Set signed 16-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 2)
        value = int(value)

        # Wrap to -32768..32767
        value = value % 65536
        if value >= 32768:
            value -= 65536

        fmt = '<h' if littleEndian else '>h'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Uint16 getters/setters
    def getUint16(self, byteOffset, littleEndian=False):
        """Get unsigned 16-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 2)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 2)

        fmt = '<H' if littleEndian else '>H'
        return struct.unpack(fmt, raw_bytes)[0]

    def setUint16(self, byteOffset, value, littleEndian=False):
        """Set unsigned 16-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 2)
        value = int(value) % 65536  # Wrap to 0..65535

        fmt = '<H' if littleEndian else '>H'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Int32 getters/setters
    def getInt32(self, byteOffset, littleEndian=False):
        """Get signed 32-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 4)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<i' if littleEndian else '>i'
        return struct.unpack(fmt, raw_bytes)[0]

    def setInt32(self, byteOffset, value, littleEndian=False):
        """Set signed 32-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 4)
        value = int(value)

        # Wrap to -2147483648..2147483647
        value = value % 4294967296
        if value >= 2147483648:
            value -= 4294967296

        fmt = '<i' if littleEndian else '>i'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Uint32 getters/setters
    def getUint32(self, byteOffset, littleEndian=False):
        """Get unsigned 32-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 4)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<I' if littleEndian else '>I'
        return struct.unpack(fmt, raw_bytes)[0]

    def setUint32(self, byteOffset, value, littleEndian=False):
        """Set unsigned 32-bit integer"""
        byteOffset = self._check_bounds(byteOffset, 4)
        value = int(value) % 4294967296  # Wrap to 0..4294967295

        fmt = '<I' if littleEndian else '>I'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Float32 getters/setters
    def getFloat32(self, byteOffset, littleEndian=False):
        """Get 32-bit floating point"""
        byteOffset = self._check_bounds(byteOffset, 4)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 4)

        fmt = '<f' if littleEndian else '>f'
        return struct.unpack(fmt, raw_bytes)[0]

    def setFloat32(self, byteOffset, value, littleEndian=False):
        """Set 32-bit floating point"""
        byteOffset = self._check_bounds(byteOffset, 4)
        value = float(value)

        fmt = '<f' if littleEndian else '>f'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # Float64 getters/setters
    def getFloat64(self, byteOffset, littleEndian=False):
        """Get 64-bit floating point"""
        byteOffset = self._check_bounds(byteOffset, 8)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 8)

        fmt = '<d' if littleEndian else '>d'
        return struct.unpack(fmt, raw_bytes)[0]

    def setFloat64(self, byteOffset, value, littleEndian=False):
        """Set 64-bit floating point"""
        byteOffset = self._check_bounds(byteOffset, 8)
        value = float(value)

        fmt = '<d' if littleEndian else '>d'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # BigInt64 getters/setters
    def getBigInt64(self, byteOffset, littleEndian=False):
        """Get signed 64-bit BigInt"""
        byteOffset = self._check_bounds(byteOffset, 8)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 8)

        fmt = '<q' if littleEndian else '>q'
        return struct.unpack(fmt, raw_bytes)[0]

    def setBigInt64(self, byteOffset, value, littleEndian=False):
        """Set signed 64-bit BigInt"""
        byteOffset = self._check_bounds(byteOffset, 8)
        value = int(value)

        # Wrap to -2^63..2^63-1
        value = value % (2**64)
        if value >= 2**63:
            value -= 2**64

        fmt = '<q' if littleEndian else '>q'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)

    # BigUint64 getters/setters
    def getBigUint64(self, byteOffset, littleEndian=False):
        """Get unsigned 64-bit BigInt"""
        byteOffset = self._check_bounds(byteOffset, 8)
        raw_bytes = self._buffer._get_bytes(self._byteOffset + byteOffset, 8)

        fmt = '<Q' if littleEndian else '>Q'
        return struct.unpack(fmt, raw_bytes)[0]

    def setBigUint64(self, byteOffset, value, littleEndian=False):
        """Set unsigned 64-bit BigInt"""
        byteOffset = self._check_bounds(byteOffset, 8)
        value = int(value) % (2**64)  # Wrap to 0..2^64-1

        fmt = '<Q' if littleEndian else '>Q'
        encoded = struct.pack(fmt, value)
        self._buffer._set_bytes(self._byteOffset + byteOffset, encoded)
