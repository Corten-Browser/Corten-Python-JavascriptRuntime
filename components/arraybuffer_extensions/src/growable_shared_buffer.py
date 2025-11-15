"""
GrowableSharedArrayBuffer implementation for ES2024
Thread-safe growable buffer for concurrent access

Requirement: FR-ES24-006
"""

import threading


class GrowableSharedArrayBuffer:
    """
    Growable SharedArrayBuffer implementation (ES2024)

    Provides thread-safe buffer that can only grow (not shrink),
    suitable for concurrent access patterns.
    """

    def __init__(self, byte_length: int, max_byte_length: int):
        """
        Create growable SharedArrayBuffer

        Args:
            byte_length: Initial buffer length
            max_byte_length: Maximum allowed length

        Raises:
            ValueError: If byte_length > max_byte_length or negative values

        Requirement: FR-ES24-006
        """
        if byte_length < 0:
            raise ValueError("byte_length must be non-negative")
        if max_byte_length < 0:
            raise ValueError("max_byte_length must be non-negative")
        if byte_length > max_byte_length:
            raise ValueError("byte_length cannot exceed max_byte_length")

        self._byte_length = byte_length
        self._max_byte_length = max_byte_length
        self.data = bytearray(max_byte_length)  # Pre-allocate max size
        self._lock = threading.Lock()  # Thread-safe operations

    @property
    def byte_length(self) -> int:
        """Current buffer length (thread-safe)"""
        with self._lock:
            return self._byte_length

    @property
    def max_byte_length(self) -> int:
        """Maximum buffer length"""
        return self._max_byte_length

    def grow(self, new_byte_length: int) -> None:
        """
        Grow buffer to new length

        Args:
            new_byte_length: New buffer length (must be >= current length)

        Raises:
            TypeError: If attempting to shrink buffer
            ValueError: If new_byte_length exceeds max or is negative

        Requirement: FR-ES24-006
        """
        if new_byte_length < 0:
            raise ValueError("new_byte_length must be non-negative")

        with self._lock:
            if new_byte_length < self._byte_length:
                raise TypeError("Cannot grow buffer to smaller size")

            if new_byte_length > self._max_byte_length:
                raise ValueError(f"new_byte_length ({new_byte_length}) exceeds max_byte_length ({self._max_byte_length})")

            # Update current length (can only increase)
            self._byte_length = new_byte_length

    def growable(self) -> bool:
        """
        Check if buffer is growable

        Returns:
            Always True for GrowableSharedArrayBuffer

        Requirement: FR-ES24-006
        """
        return True
