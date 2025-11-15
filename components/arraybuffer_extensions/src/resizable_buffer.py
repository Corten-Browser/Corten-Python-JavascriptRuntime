"""
ResizableArrayBuffer implementation for ES2024
Supports dynamic buffer sizing up to max_byte_length

Requirement: FR-ES24-005
"""


class ResizableArrayBuffer:
    """
    Resizable ArrayBuffer implementation (ES2024)

    Allows buffers to be resized up to a maximum length without
    creating a new buffer instance.
    """

    def __init__(self, byte_length: int, max_byte_length: int):
        """
        Create resizable ArrayBuffer

        Args:
            byte_length: Initial buffer length
            max_byte_length: Maximum allowed length

        Raises:
            ValueError: If byte_length > max_byte_length or negative values

        Requirement: FR-ES24-005
        """
        if byte_length < 0:
            raise ValueError("byte_length must be non-negative")
        if max_byte_length < 0:
            raise ValueError("max_byte_length must be non-negative")
        if byte_length > max_byte_length:
            raise ValueError("byte_length cannot exceed max_byte_length")

        self._byte_length = byte_length
        self._max_byte_length = max_byte_length
        self.detached = False
        self.data = bytearray(max_byte_length)  # Pre-allocate max size

    @property
    def byte_length(self) -> int:
        """Current buffer length"""
        return self._byte_length

    @property
    def max_byte_length(self) -> int:
        """Maximum buffer length"""
        return self._max_byte_length

    def resize(self, new_byte_length: int) -> None:
        """
        Resize buffer to new length

        Args:
            new_byte_length: New buffer length (0 to max_byte_length)

        Raises:
            TypeError: If buffer is detached
            ValueError: If new_byte_length is invalid

        Requirement: FR-ES24-005
        """
        if self.detached:
            raise TypeError("Cannot resize detached ArrayBuffer")

        if new_byte_length < 0:
            raise ValueError("new_byte_length must be non-negative")

        if new_byte_length > self._max_byte_length:
            raise ValueError(f"new_byte_length ({new_byte_length}) exceeds max_byte_length ({self._max_byte_length})")

        # Update current length
        # Data beyond new length becomes inaccessible (but preserved in case of re-expansion)
        self._byte_length = new_byte_length

    def resizable(self) -> bool:
        """
        Check if buffer is resizable

        Returns:
            Always True for ResizableArrayBuffer

        Requirement: FR-ES24-005
        """
        return True
