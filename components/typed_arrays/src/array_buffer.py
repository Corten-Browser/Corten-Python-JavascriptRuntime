"""
ArrayBuffer implementation following ECMAScript 2024 specification.
Fixed-length (or resizable) raw binary data buffer.
"""

import math
from exceptions import RangeError, TypeError as JSTypeError


class ArrayBuffer:
    """
    Fixed-length raw binary data buffer.
    ES2024 spec: supports resizable buffers and transfer/detach operations.
    """

    def __init__(self, byteLength, options=None):
        """
        Create new ArrayBuffer.

        Args:
            byteLength: Length in bytes (converted to integer)
            options: Optional dict with 'maxByteLength' for resizable buffers
        """
        # Convert byteLength to integer
        if isinstance(byteLength, float):
            if math.isnan(byteLength):
                raise RangeError("Invalid array buffer length: NaN")
            byteLength = int(byteLength)
        else:
            byteLength = int(byteLength)

        # Validate length
        if byteLength < 0:
            raise RangeError(f"Invalid array buffer length: {byteLength}")

        # Parse options
        options = options or {}
        maxByteLength = options.get('maxByteLength', None)

        if maxByteLength is not None:
            maxByteLength = int(maxByteLength)
            if maxByteLength < byteLength:
                raise RangeError(
                    f"maxByteLength ({maxByteLength}) must be >= byteLength ({byteLength})"
                )
            self._resizable = True
            self._maxByteLength = maxByteLength
        else:
            self._resizable = False
            self._maxByteLength = byteLength

        # Initialize buffer data
        self._data = bytearray(byteLength)
        self._byteLength = byteLength
        self._detached = False

    @property
    def byteLength(self):
        """Length in bytes (0 if detached)"""
        if self._detached:
            return 0
        return self._byteLength

    @property
    def detached(self):
        """Whether buffer has been detached (ES2024)"""
        return self._detached

    @property
    def resizable(self):
        """Whether buffer is resizable (ES2024)"""
        return self._resizable

    @property
    def maxByteLength(self):
        """Maximum byte length for resizable buffers"""
        if self._detached:
            return 0
        return self._maxByteLength

    def slice(self, begin=0, end=None):
        """
        Copy region to new ArrayBuffer.

        Args:
            begin: Start index (default 0)
            end: End index (default buffer length)

        Returns:
            New ArrayBuffer with copied data

        Raises:
            TypeError: If buffer is detached
        """
        if self._detached:
            raise JSTypeError("Cannot slice detached ArrayBuffer")

        # Handle negative indices
        length = self._byteLength
        if begin < 0:
            begin = max(0, length + begin)
        else:
            begin = min(begin, length)

        if end is None:
            end = length
        elif end < 0:
            end = max(0, length + end)
        else:
            end = min(end, length)

        # Ensure begin <= end
        if begin > end:
            begin = end

        # Calculate slice length
        sliceLength = end - begin

        # Create new buffer
        newBuffer = ArrayBuffer(sliceLength)

        # Copy data
        if sliceLength > 0:
            newBuffer._data[:] = self._data[begin:end]

        return newBuffer

    def transfer(self, newByteLength=None):
        """
        Transfer ArrayBuffer, detaching original (ES2024).

        Args:
            newByteLength: Optional new size for transferred buffer

        Returns:
            New ArrayBuffer with transferred data

        Raises:
            TypeError: If buffer is already detached
        """
        if self._detached:
            raise JSTypeError("Cannot transfer detached ArrayBuffer")

        # Default to current length
        if newByteLength is None:
            newByteLength = self._byteLength

        newByteLength = int(newByteLength)

        if newByteLength < 0:
            raise RangeError(f"Invalid array buffer length: {newByteLength}")

        # Create new buffer
        newBuffer = ArrayBuffer(newByteLength)

        # Copy existing data (truncate or zero-extend)
        copyLength = min(self._byteLength, newByteLength)
        if copyLength > 0:
            newBuffer._data[:copyLength] = self._data[:copyLength]

        # Detach this buffer
        self._detached = True
        self._data = bytearray(0)  # Clear data

        return newBuffer

    def resize(self, newByteLength):
        """
        Resize this buffer (only for resizable buffers).

        Args:
            newByteLength: New size in bytes

        Raises:
            TypeError: If buffer is not resizable or is detached
            RangeError: If newByteLength > maxByteLength
        """
        if not self._resizable:
            raise JSTypeError("Cannot resize non-resizable ArrayBuffer")

        if self._detached:
            raise JSTypeError("Cannot resize detached ArrayBuffer")

        newByteLength = int(newByteLength)

        if newByteLength < 0:
            raise RangeError(f"Invalid array buffer length: {newByteLength}")

        if newByteLength > self._maxByteLength:
            raise RangeError(
                f"Cannot resize beyond maxByteLength "
                f"({newByteLength} > {self._maxByteLength})"
            )

        # Resize the underlying buffer
        if newByteLength > self._byteLength:
            # Extend with zeros
            self._data.extend(bytearray(newByteLength - self._byteLength))
        elif newByteLength < self._byteLength:
            # Truncate
            self._data = self._data[:newByteLength]

        self._byteLength = newByteLength

    @staticmethod
    def isView(value):
        """
        Check if value is a TypedArray or DataView.

        Args:
            value: Value to check

        Returns:
            True if value is TypedArray or DataView, False otherwise
        """
        # Import here to avoid circular dependency
        from typed_array import TypedArray
        from data_view import DataView

        return isinstance(value, (TypedArray, DataView))

    # Internal methods for TypedArray/DataView access
    def _get_byte(self, index):
        """Get byte at index (internal use)"""
        if self._detached:
            raise JSTypeError("Cannot access detached ArrayBuffer")
        if index < 0 or index >= self._byteLength:
            raise RangeError(f"Byte index {index} out of range [0, {self._byteLength})")
        return self._data[index]

    def _set_byte(self, index, value):
        """Set byte at index (internal use)"""
        if self._detached:
            raise JSTypeError("Cannot modify detached ArrayBuffer")
        if index < 0 or index >= self._byteLength:
            raise RangeError(f"Byte index {index} out of range [0, {self._byteLength})")
        self._data[index] = value & 0xFF

    def _get_bytes(self, offset, count):
        """Get multiple bytes (internal use)"""
        if self._detached:
            raise JSTypeError("Cannot access detached ArrayBuffer")
        if offset < 0 or offset + count > self._byteLength:
            raise RangeError(f"Byte range [{offset}, {offset + count}) out of range")
        return bytes(self._data[offset:offset + count])

    def _set_bytes(self, offset, data):
        """Set multiple bytes (internal use)"""
        if self._detached:
            raise JSTypeError("Cannot modify detached ArrayBuffer")
        count = len(data)
        if offset < 0 or offset + count > self._byteLength:
            raise RangeError(f"Byte range [{offset}, {offset + count}) out of range")
        self._data[offset:offset + count] = data
