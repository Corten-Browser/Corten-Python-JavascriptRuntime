"""
SharedArrayBuffer integration for ES2024.

Provides SharedArrayBuffer creation and identification.
"""

import sys
from pathlib import Path

# Add typed_arrays src to path for proper imports
typed_arrays_src = Path(__file__).parent.parent.parent / 'typed_arrays' / 'src'
if str(typed_arrays_src) not in sys.path:
    sys.path.insert(0, str(typed_arrays_src))

from array_buffer import ArrayBuffer
from exceptions import RangeError


class SharedArrayBufferIntegration:
    """SharedArrayBuffer integration with Atomics.

    Provides methods to create and identify SharedArrayBuffer instances
    that can be used with atomic operations.
    """

    def create_shared_buffer(self, byte_length):
        """Create SharedArrayBuffer for concurrent access.

        Creates a new SharedArrayBuffer with the specified byte length.
        The buffer can be shared across multiple threads/agents and used
        with atomic operations.

        Args:
            byte_length: Buffer size in bytes

        Returns:
            SharedArrayBuffer: New shared buffer

        Raises:
            RangeError: If byte_length is negative

        Example:
            >>> sab = SharedArrayBufferIntegration()
            >>> buffer = sab.create_shared_buffer(256)
            >>> buffer.byteLength
            256
            >>> sab.is_shared_array_buffer(buffer)
            True
        """
        byte_length = int(byte_length)

        if byte_length < 0:
            raise RangeError(f"Invalid byte length: {byte_length}")

        # Create ArrayBuffer and mark it as shared
        buffer = ArrayBuffer(byte_length)
        buffer._shared = True

        return buffer

    def is_shared_array_buffer(self, buffer):
        """Check if buffer is SharedArrayBuffer.

        Determines whether the given buffer is a SharedArrayBuffer
        that can be used with atomic operations.

        Args:
            buffer: Buffer to check

        Returns:
            bool: True if SharedArrayBuffer, False otherwise

        Example:
            >>> sab = SharedArrayBufferIntegration()
            >>> shared = sab.create_shared_buffer(128)
            >>> regular = ArrayBuffer(128)
            >>> sab.is_shared_array_buffer(shared)
            True
            >>> sab.is_shared_array_buffer(regular)
            False
        """
        if not isinstance(buffer, ArrayBuffer):
            return False

        return getattr(buffer, '_shared', False)
