"""
Unit tests for ResizableArrayBuffer (ES2024)
Requirement: FR-ES24-005
"""

import pytest


class TestResizableArrayBuffer:
    """Test ResizableArrayBuffer implementation"""

    def test_create_resizable_buffer(self):
        """FR-ES24-005: Create ResizableArrayBuffer with initial and max lengths"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)

        assert buffer.byte_length == 1024
        assert buffer.max_byte_length == 4096
        assert buffer.resizable() is True

    def test_resize_within_max(self):
        """FR-ES24-005: Resize buffer within max_byte_length"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.resize(2048)

        assert buffer.byte_length == 2048

    def test_resize_to_zero(self):
        """FR-ES24-005: Resize to zero is allowed"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.resize(0)

        assert buffer.byte_length == 0

    def test_resize_exceeds_max_raises(self):
        """FR-ES24-005: Resize beyond max_byte_length raises RangeError"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)

        with pytest.raises(ValueError, match="max_byte_length"):
            buffer.resize(8192)

    def test_resize_negative_raises(self):
        """FR-ES24-005: Negative resize raises error"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)

        with pytest.raises(ValueError):
            buffer.resize(-1)

    def test_resize_detached_raises(self):
        """FR-ES24-005: Resizing detached buffer raises TypeError"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.detached = True

        with pytest.raises(TypeError, match="detached"):
            buffer.resize(2048)

    def test_initial_length_exceeds_max_raises(self):
        """FR-ES24-005: Initial length > max_byte_length raises"""
        from src.resizable_buffer import ResizableArrayBuffer

        with pytest.raises(ValueError, match="byte_length.*max_byte_length"):
            ResizableArrayBuffer(byte_length=4096, max_byte_length=1024)

    def test_resizable_property(self):
        """FR-ES24-005: resizable property always returns True"""
        from src.resizable_buffer import ResizableArrayBuffer

        buffer = ResizableArrayBuffer(byte_length=512, max_byte_length=2048)

        assert buffer.resizable() is True
