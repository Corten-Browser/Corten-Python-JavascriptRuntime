"""
Unit tests for DataView constructor.
Tests FR-ES24-B-020, FR-ES24-B-025, FR-ES24-B-027

Following TDD RED phase - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "typed_arrays" / "src"))

from array_buffer import ArrayBuffer
from dataview import DataView
from exceptions import RangeError, TypeError as JSTypeError


class TestDataViewConstructorBasic:
    """Test basic DataView construction (FR-ES24-B-020)"""

    def test_create_from_buffer_whole(self):
        """DataView(buffer) creates view of entire buffer"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        assert view.buffer is buf
        assert view.byteLength == 16
        assert view.byteOffset == 0

    def test_create_with_offset(self):
        """DataView(buffer, byteOffset) creates view from offset"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 8)

        assert view.buffer is buf
        assert view.byteLength == 8  # Remaining bytes
        assert view.byteOffset == 8

    def test_create_with_offset_and_length(self):
        """DataView(buffer, byteOffset, byteLength) creates partial view"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        assert view.buffer is buf
        assert view.byteLength == 8
        assert view.byteOffset == 4

    def test_create_zero_length_view(self):
        """DataView can have zero byteLength"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 16, 0)

        assert view.byteLength == 0
        assert view.byteOffset == 16

    def test_fractional_offset_converted_to_integer(self):
        """Fractional byteOffset is converted to integer"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4.7)

        assert view.byteOffset == 4

    def test_fractional_length_converted_to_integer(self):
        """Fractional byteLength is converted to integer"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 0, 8.9)

        assert view.byteLength == 8


class TestDataViewConstructorErrors:
    """Test DataView constructor error cases (FR-ES24-B-020)"""

    def test_non_arraybuffer_throws_typeerror(self):
        """First argument must be ArrayBuffer"""
        with pytest.raises(JSTypeError, match="First argument to DataView constructor must be an ArrayBuffer"):
            DataView({})

    def test_non_arraybuffer_array_throws_typeerror(self):
        """Array is not ArrayBuffer"""
        with pytest.raises(JSTypeError, match="First argument to DataView constructor must be an ArrayBuffer"):
            DataView([1, 2, 3])

    def test_non_arraybuffer_none_throws_typeerror(self):
        """None is not ArrayBuffer"""
        with pytest.raises(JSTypeError, match="First argument to DataView constructor must be an ArrayBuffer"):
            DataView(None)

    def test_negative_offset_throws_rangeerror(self):
        """Negative byteOffset throws RangeError"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Start offset is outside the bounds of the buffer"):
            DataView(buf, -1)

    def test_offset_equals_buffer_length_throws(self):
        """byteOffset == buffer.byteLength throws (would create view past end)"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Start offset is outside the bounds of the buffer"):
            DataView(buf, 17)

    def test_offset_beyond_buffer_throws(self):
        """byteOffset > buffer.byteLength throws"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Start offset is outside the bounds of the buffer"):
            DataView(buf, 100)

    def test_negative_length_throws_rangeerror(self):
        """Negative byteLength throws RangeError"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Invalid DataView length"):
            DataView(buf, 0, -1)

    def test_length_exceeds_remaining_throws(self):
        """byteOffset + byteLength > buffer.byteLength throws"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Invalid DataView length"):
            DataView(buf, 8, 10)  # 8 + 10 = 18 > 16

    def test_offset_plus_length_exceeds_buffer(self):
        """byteOffset + byteLength exactly exceeding buffer throws"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError, match="Invalid DataView length"):
            DataView(buf, 10, 7)  # 10 + 7 = 17 > 16


class TestDataViewProperties:
    """Test DataView properties (FR-ES24-B-027)"""

    def test_buffer_property_readonly(self):
        """buffer property returns the underlying ArrayBuffer"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        assert view.buffer is buf

    def test_byte_length_property(self):
        """byteLength property returns view length"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        assert view.byteLength == 8

    def test_byte_offset_property(self):
        """byteOffset property returns view offset"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        assert view.byteOffset == 4

    def test_properties_cached_on_construction(self):
        """Properties are cached at construction time"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        # Cache values before detachment
        cached_buffer = view.buffer
        cached_offset = view.byteOffset
        cached_length = view.byteLength

        # Detach buffer
        buf.transfer()

        # Properties should still return cached values (not 0)
        assert view.buffer is cached_buffer
        assert view.byteOffset == cached_offset
        assert view.byteLength == cached_length

    def test_buffer_property_not_writable(self):
        """buffer property should be read-only"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        # Attempt to set should not change the property
        try:
            view.buffer = ArrayBuffer(32)
        except AttributeError:
            pass  # Expected for read-only property

        assert view.buffer is buf
