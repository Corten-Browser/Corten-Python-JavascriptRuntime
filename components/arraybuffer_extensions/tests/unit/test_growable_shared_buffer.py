"""
Unit tests for GrowableSharedArrayBuffer (ES2024)
Requirement: FR-ES24-006
"""

import pytest


class TestGrowableSharedArrayBuffer:
    """Test GrowableSharedArrayBuffer for concurrent access"""

    def test_create_growable_buffer(self):
        """FR-ES24-006: Create GrowableSharedArrayBuffer"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)

        assert buffer.byte_length == 1024
        assert buffer.max_byte_length == 4096
        assert buffer.growable() is True

    def test_grow_buffer(self):
        """FR-ES24-006: Grow buffer to larger size"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.grow(2048)

        assert buffer.byte_length == 2048

    def test_grow_to_max(self):
        """FR-ES24-006: Grow to max_byte_length"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.grow(4096)

        assert buffer.byte_length == 4096

    def test_grow_same_size_allowed(self):
        """FR-ES24-006: Growing to same size is a no-op"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.grow(1024)

        assert buffer.byte_length == 1024

    def test_grow_smaller_raises(self):
        """FR-ES24-006: Growing to smaller size raises TypeError"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=2048, max_byte_length=4096)

        with pytest.raises(TypeError, match="smaller"):
            buffer.grow(1024)

    def test_grow_exceeds_max_raises(self):
        """FR-ES24-006: Growing beyond max_byte_length raises RangeError"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)

        with pytest.raises(ValueError, match="max_byte_length"):
            buffer.grow(8192)

    def test_grow_negative_raises(self):
        """FR-ES24-006: Negative grow raises error"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=4096)

        with pytest.raises(ValueError):
            buffer.grow(-1)

    def test_growable_property(self):
        """FR-ES24-006: growable property always returns True"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=512, max_byte_length=2048)

        assert buffer.growable() is True

    def test_initial_length_exceeds_max_raises(self):
        """FR-ES24-006: Initial length > max_byte_length raises"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        with pytest.raises(ValueError, match="byte_length.*max_byte_length"):
            GrowableSharedArrayBuffer(byte_length=4096, max_byte_length=1024)
