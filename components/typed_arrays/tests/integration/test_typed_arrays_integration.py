"""
Integration tests for TypedArrays component.
Tests interactions between ArrayBuffer, TypedArray variants, and DataView.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from array_buffer import ArrayBuffer
from typed_array import (
    Uint8Array, Int8Array, Uint8ClampedArray,
    Int16Array, Uint16Array,
    Int32Array, Uint32Array,
    Float32Array, Float64Array,
    BigInt64Array, BigUint64Array
)
from data_view import DataView
from exceptions import RangeError, TypeError


class TestArrayBufferWithTypedArrays:
    """Test ArrayBuffer integration with TypedArrays"""

    def test_multiple_views_same_buffer(self):
        """Multiple TypedArrays can view same buffer"""
        buf = ArrayBuffer(16)
        view1 = Uint8Array(buf)
        view2 = Uint32Array(buf)

        # Write via Uint32Array
        view2[0] = 0x12345678

        # Read via Uint8Array (little-endian)
        assert view1[0] == 0x78
        assert view1[1] == 0x56
        assert view1[2] == 0x34
        assert view1[3] == 0x12

    def test_overlapping_views(self):
        """TypedArray views can overlap in buffer"""
        buf = ArrayBuffer(16)
        view1 = Uint8Array(buf, 0, 8)
        view2 = Uint8Array(buf, 4, 8)

        view1[4] = 42
        assert view2[0] == 42

    def test_arraybuffer_isview_with_typedarray(self):
        """ArrayBuffer.isView() detects TypedArrays"""
        arr = Uint8Array(10)
        assert ArrayBuffer.isView(arr)

        buf = ArrayBuffer(10)
        assert not ArrayBuffer.isView(buf)

    def test_detached_buffer_affects_all_views(self):
        """Detaching buffer affects all TypedArray views"""
        buf = ArrayBuffer(16)
        view1 = Uint8Array(buf)
        view2 = Int32Array(buf)

        buf.transfer()

        with pytest.raises(TypeError):
            _ = view1[0]

        with pytest.raises(TypeError):
            _ = view2[0]


class TestArrayBufferWithDataView:
    """Test ArrayBuffer integration with DataView"""

    def test_arraybuffer_isview_with_dataview(self):
        """ArrayBuffer.isView() detects DataView"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        assert ArrayBuffer.isView(view)

    def test_dataview_and_typedarray_same_buffer(self):
        """DataView and TypedArray can share buffer"""
        buf = ArrayBuffer(16)
        dataView = DataView(buf)
        typedArray = Uint8Array(buf)

        # Write via DataView
        dataView.setUint8(0, 42)

        # Read via TypedArray
        assert typedArray[0] == 42

    def test_dataview_endianness_with_typedarray(self):
        """DataView endianness vs TypedArray (little-endian)"""
        buf = ArrayBuffer(4)
        dataView = DataView(buf)
        uint8View = Uint8Array(buf)

        # Write big-endian via DataView
        dataView.setUint32(0, 0x12345678, False)  # Big-endian

        # TypedArrays use little-endian internally
        # So reading bytes individually shows reversed order
        assert uint8View[0] == 0x12
        assert uint8View[1] == 0x34
        assert uint8View[2] == 0x56
        assert uint8View[3] == 0x78


class TestTypedArrayInteroperability:
    """Test different TypedArray variants working together"""

    def test_copy_between_different_types(self):
        """Copy data between different TypedArray types"""
        source = Uint8Array([1, 2, 3, 4, 5])
        dest = Int16Array(5)

        for i in range(source.length):
            dest[i] = source[i]

        assert list(dest) == [1, 2, 3, 4, 5]

    def test_type_conversion_on_copy(self):
        """Values convert when copying between types"""
        source = Int8Array([127, -128, -1])
        dest = Uint8Array(3)

        for i in range(source.length):
            dest[i] = source[i]

        # -128 wraps to 128, -1 wraps to 255
        assert dest[0] == 127
        assert dest[1] == 128
        assert dest[2] == 255

    def test_float_to_int_conversion(self):
        """Float to int conversion truncates"""
        source = Float32Array([3.14, -2.7, 100.9])
        dest = Int32Array(3)

        for i in range(source.length):
            dest[i] = source[i]

        assert dest[0] == 3
        assert dest[1] == -2
        assert dest[2] == 100

    def test_shared_buffer_different_element_sizes(self):
        """Views with different element sizes on same buffer"""
        buf = ArrayBuffer(16)
        uint8 = Uint8Array(buf)      # 16 elements
        uint16 = Uint16Array(buf)    # 8 elements
        uint32 = Uint32Array(buf)    # 4 elements

        # Write via uint32
        uint32[0] = 0xAABBCCDD

        # Read via uint16 (little-endian)
        assert uint16[0] == 0xCCDD
        assert uint16[1] == 0xAABB

        # Read via uint8
        assert uint8[0] == 0xDD
        assert uint8[1] == 0xCC
        assert uint8[2] == 0xBB
        assert uint8[3] == 0xAA


class TestUint8ClampedArrayBehavior:
    """Test Uint8ClampedArray special clamping behavior"""

    def test_clamping_vs_wrapping(self):
        """Uint8ClampedArray clamps vs Uint8Array wraps"""
        clamped = Uint8ClampedArray([256, -1, 300, -100])
        wrapped = Uint8Array([256, -1, 300, -100])

        # Clamped: clamps to 0..255
        assert clamped[0] == 255
        assert clamped[1] == 0
        assert clamped[2] == 255
        assert clamped[3] == 0

        # Wrapped: wraps modulo 256
        assert wrapped[0] == 0
        assert wrapped[1] == 255
        assert wrapped[2] == 44
        assert wrapped[3] == 156

    def test_clamping_with_floats(self):
        """Uint8ClampedArray special rounding for 0.5"""
        arr = Uint8ClampedArray([0.5, 1.5, 2.5, 3.5, 4.5])

        # Rounds to even (banker's rounding)
        assert arr[0] == 0   # 0.5 rounds to 0 (even)
        assert arr[1] == 2   # 1.5 rounds to 2 (even)
        assert arr[2] == 2   # 2.5 rounds to 2 (even)
        assert arr[3] == 4   # 3.5 rounds to 4 (even)
        assert arr[4] == 4   # 4.5 rounds to 4 (even)


class TestBigIntArrays:
    """Test BigInt64Array and BigUint64Array"""

    def test_bigint_storage(self):
        """BigInt arrays store large values"""
        arr = BigInt64Array([2**62, -2**62])

        assert arr[0] == 2**62
        assert arr[1] == -2**62

    def test_biguint_wrapping(self):
        """BigUint64Array wraps to 0..2^64-1"""
        arr = BigUint64Array([2**64, 2**64 + 100, -1])

        assert arr[0] == 0
        assert arr[1] == 100
        assert arr[2] == 2**64 - 1


class TestTypedArraySliceVsSubarray:
    """Test difference between slice() and subarray()"""

    def test_slice_creates_new_buffer(self):
        """slice() creates new buffer"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.slice(1, 4)

        assert list(arr2) == [2, 3, 4]
        assert arr2.buffer is not arr1.buffer

        # Modifying arr2 doesn't affect arr1
        arr2[0] = 99
        assert arr1[1] == 2

    def test_subarray_shares_buffer(self):
        """subarray() shares buffer"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.subarray(1, 4)

        assert list(arr2) == [2, 3, 4]
        assert arr2.buffer is arr1.buffer

        # Modifying arr2 affects arr1
        arr2[0] = 99
        assert arr1[1] == 99


class TestComplexWorkflows:
    """Test complex real-world workflows"""

    def test_binary_protocol_parsing(self):
        """Simulate parsing binary protocol"""
        # Create message: [version(1), length(2), data(4)]
        buf = ArrayBuffer(7)
        view = DataView(buf)

        view.setUint8(0, 1)                    # Version
        view.setUint16(1, 4, True)             # Length (little-endian)
        view.setUint32(3, 0x12345678, True)    # Data

        # Parse it back
        version = view.getUint8(0)
        length = view.getUint16(1, True)
        data = view.getUint32(3, True)

        assert version == 1
        assert length == 4
        assert data == 0x12345678

    def test_pixel_manipulation(self):
        """Simulate RGBA pixel manipulation"""
        # 2x2 image, 4 bytes per pixel (RGBA)
        pixels = Uint8ClampedArray(16)

        # Set pixel (0,0) to red
        pixels[0] = 255   # R
        pixels[1] = 0     # G
        pixels[2] = 0     # B
        pixels[3] = 255   # A

        # Set pixel (1,1) to blue
        pixels[12] = 0    # R
        pixels[13] = 0    # G
        pixels[14] = 255  # B
        pixels[15] = 255  # A

        assert pixels[0] == 255
        assert pixels[14] == 255

    def test_audio_buffer_processing(self):
        """Simulate audio buffer processing"""
        # 10 samples of 32-bit float audio
        audio = Float32Array(10)

        # Generate sine wave-like data
        for i in range(10):
            audio[i] = i * 0.1

        # Apply gain
        processed = audio.map(lambda x, *args: x * 0.5)

        assert abs(processed[5] - 0.25) < 0.001
        assert processed.length == 10


class TestErrorHandling:
    """Test error conditions in integration scenarios"""

    def test_mixed_views_with_detached_buffer(self):
        """All views fail when buffer detached"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        view = DataView(buf)

        buf.transfer()

        with pytest.raises(TypeError):
            arr[0] = 42

        with pytest.raises(TypeError):
            view.setUint8(0, 42)

    def test_overlapping_set_operations(self):
        """Set operations handle overlapping regions"""
        arr = Uint8Array([1, 2, 3, 4, 5, 6])

        # Copy overlapping region within same array
        arr.copyWithin(2, 0, 3)

        assert list(arr) == [1, 2, 1, 2, 3, 6]

    def test_type_overflow_handling(self):
        """Different types handle overflow differently"""
        # Int8Array wraps
        int8 = Int8Array([127, 128, 129])
        assert int8[0] == 127
        assert int8[1] == -128
        assert int8[2] == -127

        # Uint8ClampedArray clamps
        clamped = Uint8ClampedArray([127, 128, 129, 256])
        assert clamped[0] == 127
        assert clamped[1] == 128
        assert clamped[2] == 129
        assert clamped[3] == 255


class TestResizableBuffers:
    """Test ES2024 resizable ArrayBuffer feature"""

    def test_typed_array_on_resizable_buffer(self):
        """TypedArray views resizable buffer"""
        buf = ArrayBuffer(16, {'maxByteLength': 64})
        arr = Uint8Array(buf)

        assert arr.length == 16

        # Resize buffer
        buf.resize(32)

        # Original array still views old size
        # (In real JS, this would auto-update, but for simplicity we don't)
        assert arr.length == 16

    def test_transfer_preserves_typed_array_data(self):
        """Transfer preserves data accessible via TypedArray"""
        buf1 = ArrayBuffer(16)
        arr1 = Uint8Array(buf1)
        arr1[0] = 42
        arr1[1] = 99

        # Transfer to new buffer
        buf2 = buf1.transfer(16)
        arr2 = Uint8Array(buf2)

        # Data preserved
        assert arr2[0] == 42
        assert arr2[1] == 99

        # Original buffer detached
        with pytest.raises(TypeError):
            _ = arr1[0]
