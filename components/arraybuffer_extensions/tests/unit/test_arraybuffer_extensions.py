"""
Unit tests for ArrayBufferExtensions (ES2024)
Requirements: FR-ES24-001, FR-ES24-002, FR-ES24-003, FR-ES24-004
"""

import pytest
from unittest.mock import Mock, MagicMock


class TestArrayBufferExtensions:
    """Test ArrayBuffer.prototype extensions (transfer, detached, maxByteLength)"""

    def test_transfer_basic(self):
        """FR-ES24-001: Test basic transfer operation"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False
        buffer.data = bytearray(1024)

        new_buffer = ext.transfer(buffer)

        assert new_buffer is not None
        assert buffer.detached is True  # Original should be detached

    def test_transfer_with_resize(self):
        """FR-ES24-001: Test transfer with new byte length"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False
        buffer.data = bytearray(1024)

        new_buffer = ext.transfer(buffer, new_byte_length=2048)

        assert new_buffer is not None
        assert buffer.detached is True

    def test_transfer_detached_buffer_raises(self):
        """FR-ES24-001: Transferring detached buffer should raise TypeError"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.detached = True

        with pytest.raises(TypeError, match="detached"):
            ext.transfer(buffer)

    def test_transfer_invalid_length_raises(self):
        """FR-ES24-001: Invalid new_byte_length should raise RangeError"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False

        with pytest.raises(ValueError, match="byte_length"):
            ext.transfer(buffer, new_byte_length=-1)

    def test_transfer_to_fixed_length_basic(self):
        """FR-ES24-002: Test transferToFixedLength operation"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False
        buffer.data = bytearray(1024)

        new_buffer = ext.transfer_to_fixed_length(buffer, new_byte_length=512)

        assert new_buffer is not None
        assert buffer.detached is True

    def test_transfer_to_fixed_length_detached_raises(self):
        """FR-ES24-002: Transferring detached buffer should raise"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.detached = True

        with pytest.raises(TypeError):
            ext.transfer_to_fixed_length(buffer, new_byte_length=512)

    def test_is_detached_true(self):
        """FR-ES24-003: Test detached getter returns True"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.detached = True

        assert ext.is_detached(buffer) is True

    def test_is_detached_false(self):
        """FR-ES24-003: Test detached getter returns False"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.detached = False

        assert ext.is_detached(buffer) is False

    def test_get_max_byte_length_fixed(self):
        """FR-ES24-004: Fixed buffers return byte_length"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.resizable = False

        assert ext.get_max_byte_length(buffer) == 1024

    def test_get_max_byte_length_resizable(self):
        """FR-ES24-004: Resizable buffers return max_byte_length"""
        from src.arraybuffer_extensions import ArrayBufferExtensions

        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 512
        buffer.max_byte_length = 2048
        buffer.resizable = True

        assert ext.get_max_byte_length(buffer) == 2048
