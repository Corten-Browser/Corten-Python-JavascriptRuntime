"""
ArrayBuffer Extensions for ES2024
Implements transfer, transferToFixedLength, detached getter, maxByteLength getter

Requirements: FR-ES24-001, FR-ES24-002, FR-ES24-003, FR-ES24-004
"""

from typing import Optional, Any


class ArrayBufferExtensions:
    """
    Manages ArrayBuffer ES2024 extensions including transfer operations
    and buffer status queries.
    """

    def transfer(self, buffer: Any, new_byte_length: Optional[int] = None) -> Any:
        """
        Transfer ArrayBuffer to new instance (ES2024)

        Args:
            buffer: Source ArrayBuffer to transfer
            new_byte_length: Optional new length for transferred buffer

        Returns:
            New ArrayBuffer with transferred data

        Raises:
            TypeError: If buffer is already detached
            ValueError: If new_byte_length is invalid

        Requirement: FR-ES24-001
        """
        # Check if buffer is detached
        if getattr(buffer, 'detached', False):
            raise TypeError("Cannot transfer detached ArrayBuffer")

        # Validate new_byte_length if provided
        if new_byte_length is not None:
            if new_byte_length < 0:
                raise ValueError("new_byte_length must be non-negative")

        # Get original length
        original_length = getattr(buffer, 'byte_length', 0)
        target_length = new_byte_length if new_byte_length is not None else original_length

        # Create new buffer (mock implementation)
        class TransferredBuffer:
            def __init__(self, byte_length):
                self.byte_length = byte_length
                self.detached = False
                self.data = bytearray(byte_length)

        new_buffer = TransferredBuffer(target_length)

        # Copy data if possible (up to min of original and new length)
        copy_length = min(original_length, target_length)
        if hasattr(buffer, 'data'):
            new_buffer.data[:copy_length] = buffer.data[:copy_length]

        # Mark original buffer as detached
        buffer.detached = True

        return new_buffer

    def transfer_to_fixed_length(self, buffer: Any, new_byte_length: int) -> Any:
        """
        Transfer ArrayBuffer to new fixed-length instance (ES2024)

        Args:
            buffer: Source ArrayBuffer
            new_byte_length: New fixed length

        Returns:
            New fixed-length ArrayBuffer

        Raises:
            TypeError: If buffer is already detached
            ValueError: If new_byte_length is invalid

        Requirement: FR-ES24-002
        """
        # Check if buffer is detached
        if getattr(buffer, 'detached', False):
            raise TypeError("Cannot transfer detached ArrayBuffer")

        # Validate new_byte_length
        if new_byte_length < 0:
            raise ValueError("new_byte_length must be non-negative")

        # Get original length
        original_length = getattr(buffer, 'byte_length', 0)

        # Create new fixed-length buffer
        class FixedLengthBuffer:
            def __init__(self, byte_length):
                self.byte_length = byte_length
                self.detached = False
                self.resizable = False
                self.data = bytearray(byte_length)

        new_buffer = FixedLengthBuffer(new_byte_length)

        # Copy data
        copy_length = min(original_length, new_byte_length)
        if hasattr(buffer, 'data'):
            new_buffer.data[:copy_length] = buffer.data[:copy_length]

        # Mark original buffer as detached
        buffer.detached = True

        return new_buffer

    def is_detached(self, buffer: Any) -> bool:
        """
        Check if ArrayBuffer is detached (ES2024)

        Args:
            buffer: ArrayBuffer to check

        Returns:
            True if buffer is detached, False otherwise

        Requirement: FR-ES24-003
        """
        return getattr(buffer, 'detached', False)

    def get_max_byte_length(self, buffer: Any) -> int:
        """
        Get maximum byte length for ArrayBuffer (ES2024)

        For fixed buffers, returns byte_length.
        For resizable buffers, returns max_byte_length.

        Args:
            buffer: ArrayBuffer to query

        Returns:
            Maximum byte length

        Requirement: FR-ES24-004
        """
        is_resizable = getattr(buffer, 'resizable', False)

        if is_resizable:
            return getattr(buffer, 'max_byte_length', 0)
        else:
            return getattr(buffer, 'byte_length', 0)
