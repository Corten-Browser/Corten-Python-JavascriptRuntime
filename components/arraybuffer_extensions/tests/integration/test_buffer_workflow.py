"""
Integration tests for ArrayBuffer extensions workflow
Tests cross-component interactions and real-world scenarios
"""

import pytest
from unittest.mock import Mock


class TestBufferWorkflow:
    """Integration tests for complete buffer workflows"""

    def test_transfer_and_resize_workflow(self):
        """Test transferring buffer with resize operation"""
        from src.arraybuffer_extensions import ArrayBufferExtensions
        from src.resizable_buffer import ResizableArrayBuffer

        # Create resizable buffer
        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=4096)
        buffer.resize(2048)

        # Transfer to new buffer
        ext = ArrayBufferExtensions()
        new_buffer = ext.transfer(buffer, new_byte_length=3072)

        assert new_buffer is not None
        assert buffer.detached is True

    def test_resizable_to_fixed_workflow(self):
        """Test converting resizable buffer to fixed-length"""
        from src.arraybuffer_extensions import ArrayBufferExtensions
        from src.resizable_buffer import ResizableArrayBuffer

        # Create resizable buffer
        buffer = ResizableArrayBuffer(byte_length=512, max_byte_length=2048)

        # Transfer to fixed-length
        ext = ArrayBufferExtensions()
        fixed_buffer = ext.transfer_to_fixed_length(buffer, new_byte_length=1024)

        assert fixed_buffer is not None
        assert buffer.detached is True

    def test_growable_shared_buffer_workflow(self):
        """Test GrowableSharedArrayBuffer growth workflow"""
        from src.growable_shared_buffer import GrowableSharedArrayBuffer

        buffer = GrowableSharedArrayBuffer(byte_length=512, max_byte_length=4096)

        # Grow in steps
        buffer.grow(1024)
        assert buffer.byte_length == 1024

        buffer.grow(2048)
        assert buffer.byte_length == 2048

        buffer.grow(4096)
        assert buffer.byte_length == 4096

    def test_typedarray_chaining(self):
        """Test chaining toReversed and toSorted operations"""
        from src.typedarray_extensions import TypedArrayExtensions

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [3, 1, 4, 1, 5, 9, 2, 6]
        array.length = 8

        # Chain operations
        reversed_array = ext.to_reversed(array)
        sorted_reversed = ext.to_sorted(reversed_array)

        assert reversed_array is not array
        assert sorted_reversed is not reversed_array
        assert sorted_reversed is not array

    def test_detached_buffer_detection(self):
        """Test detached buffer detection across operations"""
        from src.arraybuffer_extensions import ArrayBufferExtensions
        from src.resizable_buffer import ResizableArrayBuffer

        ext = ArrayBufferExtensions()
        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=2048)

        # Initially not detached
        assert ext.is_detached(buffer) is False

        # Transfer detaches original
        new_buffer = ext.transfer(buffer)
        assert ext.is_detached(buffer) is True

        # Cannot operate on detached buffer
        with pytest.raises(TypeError):
            buffer.resize(512)
