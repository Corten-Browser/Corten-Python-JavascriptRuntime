"""
Unit tests for SharedArrayBuffer integration.

Tests FR-ES24-010: SharedArrayBuffer integration
"""

import pytest
import sys
from pathlib import Path

# Add typed_arrays src to path
typed_arrays_src = Path(__file__).parent.parent.parent.parent / 'typed_arrays' / 'src'
if str(typed_arrays_src) not in sys.path:
    sys.path.insert(0, str(typed_arrays_src))

from array_buffer import ArrayBuffer
from exceptions import RangeError


class TestSharedArrayBufferIntegration:
    """Test SharedArrayBuffer integration with Atomics."""

    def test_create_shared_buffer_returns_shared_array_buffer(self):
        """
        Given a byte length
        When create_shared_buffer is called
        Then it returns a SharedArrayBuffer with that length
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()
        buffer = sab_integration.create_shared_buffer(256)

        assert buffer is not None
        assert buffer.byteLength == 256
        assert hasattr(buffer, '_shared')
        assert buffer._shared is True

    def test_create_shared_buffer_zero_length(self):
        """
        Given a byte length of 0
        When create_shared_buffer is called
        Then it returns a SharedArrayBuffer with length 0
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()
        buffer = sab_integration.create_shared_buffer(0)

        assert buffer.byteLength == 0
        assert buffer._shared is True

    def test_create_shared_buffer_large_size(self):
        """
        Given a large byte length
        When create_shared_buffer is called
        Then it returns a SharedArrayBuffer with that length
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()
        large_size = 1024 * 1024 * 10  # 10MB

        buffer = sab_integration.create_shared_buffer(large_size)

        assert buffer.byteLength == large_size
        assert buffer._shared is True

    def test_create_shared_buffer_negative_length_throws(self):
        """
        Given a negative byte length
        When create_shared_buffer is called
        Then it raises RangeError
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()

        with pytest.raises(RangeError):
            sab_integration.create_shared_buffer(-10)

    def test_is_shared_array_buffer_returns_true_for_shared(self):
        """
        Given a SharedArrayBuffer
        When is_shared_array_buffer is called
        Then it returns True
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()
        shared_buffer = sab_integration.create_shared_buffer(128)

        result = sab_integration.is_shared_array_buffer(shared_buffer)

        assert result is True

    def test_is_shared_array_buffer_returns_false_for_non_shared(self):
        """
        Given a regular ArrayBuffer
        When is_shared_array_buffer is called
        Then it returns False
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()
        regular_buffer = ArrayBuffer(128)

        result = sab_integration.is_shared_array_buffer(regular_buffer)

        assert result is False

    def test_is_shared_array_buffer_returns_false_for_non_buffer(self):
        """
        Given a non-buffer object
        When is_shared_array_buffer is called
        Then it returns False
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab_integration = SharedArrayBufferIntegration()

        assert sab_integration.is_shared_array_buffer(None) is False
        assert sab_integration.is_shared_array_buffer("string") is False
        assert sab_integration.is_shared_array_buffer(123) is False
        assert sab_integration.is_shared_array_buffer([1, 2, 3]) is False

    def test_shared_buffer_can_be_used_with_typed_array(self):
        """
        Given a SharedArrayBuffer
        When a TypedArray is created from it
        Then the TypedArray works correctly with the shared buffer
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration
        from components.typed_arrays.src.typed_array import Int32Array

        sab_integration = SharedArrayBufferIntegration()
        shared_buffer = sab_integration.create_shared_buffer(64)

        # Create Int32Array view
        int32_array = Int32Array(shared_buffer)

        assert int32_array.length == 16  # 64 bytes / 4 bytes per int32
        assert int32_array.buffer is shared_buffer

        # Can read and write
        int32_array[0] = 42
        assert int32_array[0] == 42

    def test_shared_buffer_concurrent_access(self):
        """
        Given a SharedArrayBuffer
        When multiple TypedArray views are created
        Then they share the same underlying memory
        """
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration
        from components.typed_arrays.src.typed_array import Int32Array

        sab_integration = SharedArrayBufferIntegration()
        shared_buffer = sab_integration.create_shared_buffer(64)

        # Create two views
        view1 = Int32Array(shared_buffer)
        view2 = Int32Array(shared_buffer)

        # Modification through view1 visible in view2
        view1[0] = 123
        assert view2[0] == 123

        view2[1] = 456
        assert view1[1] == 456
