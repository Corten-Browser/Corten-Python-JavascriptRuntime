"""
Edge case tests for ArrayBuffer extensions
Tests boundary conditions and unusual scenarios
"""

import pytest
from src.arraybuffer_extensions import ArrayBufferExtensions
from src.resizable_buffer import ResizableArrayBuffer
from src.growable_shared_buffer import GrowableSharedArrayBuffer
from src.typedarray_extensions import TypedArrayExtensions
from unittest.mock import Mock


class TestEdgeCases:
    """Edge case and boundary condition tests"""

    def test_transfer_zero_length_buffer(self):
        """Transfer buffer with 0 byte length"""
        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 0
        buffer.detached = False
        buffer.data = bytearray(0)

        new_buffer = ext.transfer(buffer)
        assert new_buffer.byte_length == 0

    def test_transfer_to_zero_length(self):
        """Transfer buffer resizing to 0 bytes"""
        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False
        buffer.data = bytearray(1024)

        new_buffer = ext.transfer(buffer, new_byte_length=0)
        assert new_buffer.byte_length == 0

    def test_resizable_buffer_zero_initial(self):
        """Create resizable buffer with 0 initial size"""
        buffer = ResizableArrayBuffer(byte_length=0, max_byte_length=1024)
        assert buffer.byte_length == 0

    def test_resizable_buffer_same_initial_and_max(self):
        """Create resizable buffer where initial == max"""
        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=1024)
        assert buffer.byte_length == 1024
        assert buffer.max_byte_length == 1024

    def test_growable_buffer_zero_initial(self):
        """Create growable buffer with 0 initial size"""
        buffer = GrowableSharedArrayBuffer(byte_length=0, max_byte_length=1024)
        assert buffer.byte_length == 0

    def test_multiple_resize_operations(self):
        """Multiple resize operations should work correctly"""
        buffer = ResizableArrayBuffer(byte_length=512, max_byte_length=4096)

        buffer.resize(1024)
        assert buffer.byte_length == 1024

        buffer.resize(2048)
        assert buffer.byte_length == 2048

        buffer.resize(1024)  # Shrink
        assert buffer.byte_length == 1024

        buffer.resize(0)  # Shrink to zero
        assert buffer.byte_length == 0

    def test_multiple_grow_operations(self):
        """Multiple grow operations should work correctly"""
        buffer = GrowableSharedArrayBuffer(byte_length=512, max_byte_length=4096)

        buffer.grow(1024)
        assert buffer.byte_length == 1024

        buffer.grow(2048)
        assert buffer.byte_length == 2048

        buffer.grow(4096)
        assert buffer.byte_length == 4096

    def test_to_reversed_duplicate_elements(self):
        """toReversed with duplicate elements"""
        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [1, 2, 2, 3, 3, 3]
        array.length = 6

        reversed_array = ext.to_reversed(array)
        assert reversed_array.values == [3, 3, 3, 2, 2, 1]

    def test_to_sorted_all_same_elements(self):
        """toSorted with all identical elements"""
        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [5, 5, 5, 5, 5]
        array.length = 5

        sorted_array = ext.to_sorted(array)
        assert sorted_array.values == [5, 5, 5, 5, 5]

    def test_to_sorted_negative_numbers(self):
        """toSorted with negative numbers"""
        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [-5, 3, -1, 0, 2, -3]
        array.length = 6

        sorted_array = ext.to_sorted(array)
        assert sorted_array.values == [-5, -3, -1, 0, 2, 3]

    def test_transfer_exact_same_size(self):
        """Transfer with new_byte_length equal to original"""
        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = False
        buffer.data = bytearray(1024)

        new_buffer = ext.transfer(buffer, new_byte_length=1024)
        assert new_buffer.byte_length == 1024
        assert buffer.detached is True

    def test_get_max_byte_length_detached(self):
        """Get max byte length of detached buffer"""
        ext = ArrayBufferExtensions()
        buffer = Mock()
        buffer.byte_length = 1024
        buffer.detached = True
        buffer.resizable = False

        # Should still return byte_length even if detached
        assert ext.get_max_byte_length(buffer) == 1024
