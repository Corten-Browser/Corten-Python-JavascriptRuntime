"""
Unit tests for TypedArray edge cases - ES2024 Wave D

Requirement: FR-ES24-D-011
Tests comprehensive TypedArray boundary conditions and edge cases
"""

import pytest
import math
from components.array_polish.src.typed_array import TypedArrayHandler


class TestTypedArrayBoundaries:
    """Test TypedArray boundary conditions"""

    def setup_method(self):
        """Setup test fixtures"""
        self.handler = TypedArrayHandler()

    # FR-ES24-D-011: Int8Array boundaries
    def test_int8_array_min_value(self):
        """Int8Array minimum value (-128)"""
        result = self.handler.validate_typed_array('Int8Array', [-128, 0, 127])
        assert result['valid'] is True
        assert result['min_value'] == -128
        assert result['max_value'] == 127

    def test_int8_array_max_value(self):
        """Int8Array maximum value (127)"""
        result = self.handler.validate_typed_array('Int8Array', [127])
        assert result['valid'] is True

    def test_int8_array_overflow(self):
        """Int8Array overflow wraps around"""
        result = self.handler.validate_typed_array('Int8Array', [128])
        # 128 wraps to -128 in Int8Array
        assert result['has_overflow'] is True

    # FR-ES24-D-011: Uint8Array boundaries
    def test_uint8_array_min_value(self):
        """Uint8Array minimum value (0)"""
        result = self.handler.validate_typed_array('Uint8Array', [0, 128, 255])
        assert result['valid'] is True
        assert result['min_value'] == 0
        assert result['max_value'] == 255

    def test_uint8_array_max_value(self):
        """Uint8Array maximum value (255)"""
        result = self.handler.validate_typed_array('Uint8Array', [255])
        assert result['valid'] is True

    def test_uint8_array_negative_wraps(self):
        """Uint8Array negative values wrap"""
        result = self.handler.validate_typed_array('Uint8Array', [-1])
        # -1 wraps to 255 in Uint8Array
        assert result['has_overflow'] is True

    # FR-ES24-D-011: Uint8ClampedArray special behavior
    def test_uint8_clamped_array_clamps_low(self):
        """Uint8ClampedArray clamps low values to 0"""
        result = self.handler.validate_typed_array('Uint8ClampedArray', [-10])
        assert result['clamped'] is True
        # Should clamp to 0, not wrap

    def test_uint8_clamped_array_clamps_high(self):
        """Uint8ClampedArray clamps high values to 255"""
        result = self.handler.validate_typed_array('Uint8ClampedArray', [300])
        assert result['clamped'] is True
        # Should clamp to 255, not wrap

    def test_uint8_clamped_array_within_range(self):
        """Uint8ClampedArray values within range"""
        result = self.handler.validate_typed_array('Uint8ClampedArray', [0, 128, 255])
        assert result['valid'] is True
        assert result.get('clamped') is False

    # FR-ES24-D-011: Int16Array boundaries
    def test_int16_array_boundaries(self):
        """Int16Array min/max values"""
        result = self.handler.validate_typed_array('Int16Array', [-32768, 0, 32767])
        assert result['valid'] is True
        assert result['min_value'] == -32768
        assert result['max_value'] == 32767

    # FR-ES24-D-011: Uint16Array boundaries
    def test_uint16_array_boundaries(self):
        """Uint16Array min/max values"""
        result = self.handler.validate_typed_array('Uint16Array', [0, 32768, 65535])
        assert result['valid'] is True
        assert result['min_value'] == 0
        assert result['max_value'] == 65535

    # FR-ES24-D-011: Int32Array boundaries
    def test_int32_array_boundaries(self):
        """Int32Array min/max values"""
        result = self.handler.validate_typed_array('Int32Array', [-2147483648, 0, 2147483647])
        assert result['valid'] is True
        assert result['min_value'] == -2147483648
        assert result['max_value'] == 2147483647

    # FR-ES24-D-011: Uint32Array boundaries
    def test_uint32_array_boundaries(self):
        """Uint32Array min/max values"""
        result = self.handler.validate_typed_array('Uint32Array', [0, 2147483648, 4294967295])
        assert result['valid'] is True
        assert result['max_value'] == 4294967295

    # FR-ES24-D-011: Float32Array special values
    def test_float32_array_nan(self):
        """Float32Array with NaN"""
        result = self.handler.validate_typed_array('Float32Array', [1.5, float('nan'), 3.14])
        assert result['valid'] is True
        assert result['has_nan'] is True

    def test_float32_array_infinity(self):
        """Float32Array with Infinity"""
        result = self.handler.validate_typed_array('Float32Array', [float('inf'), float('-inf')])
        assert result['valid'] is True
        assert result['has_infinity'] is True

    def test_float32_array_negative_zero(self):
        """Float32Array with -0"""
        result = self.handler.validate_typed_array('Float32Array', [-0.0, 1.5])
        assert result['valid'] is True
        assert result['has_negative_zero'] is True

    # FR-ES24-D-011: Float64Array special values
    def test_float64_array_special_values(self):
        """Float64Array with all special values"""
        result = self.handler.validate_typed_array(
            'Float64Array',
            [float('nan'), -0.0, float('inf'), float('-inf'), 1.5]
        )
        assert result['valid'] is True
        assert result['has_nan'] is True
        assert result['has_negative_zero'] is True
        assert result['has_infinity'] is True

    # FR-ES24-D-011: BigInt64Array
    def test_bigint64_array_boundaries(self):
        """BigInt64Array large values"""
        result = self.handler.validate_typed_array(
            'BigInt64Array',
            [-(2**63), 0, 2**63 - 1]
        )
        assert result['valid'] is True

    # FR-ES24-D-011: BigUint64Array
    def test_biguint64_array_boundaries(self):
        """BigUint64Array large values"""
        result = self.handler.validate_typed_array(
            'BigUint64Array',
            [0, 2**63, 2**64 - 1]
        )
        assert result['valid'] is True

    # FR-ES24-D-011: Out-of-bounds access
    def test_typed_array_at_out_of_bounds(self):
        """TypedArray out-of-bounds access returns undefined"""
        typed_arr = self.handler.create_typed_array('Int8Array', [1, 2, 3])
        result = self.handler.at(typed_arr, 5)
        assert result['is_undefined'] is True

    def test_typed_array_at_negative_out_of_bounds(self):
        """TypedArray negative out-of-bounds"""
        typed_arr = self.handler.create_typed_array('Int8Array', [1, 2, 3])
        result = self.handler.at(typed_arr, -5)
        assert result['is_undefined'] is True

    # FR-ES24-D-011: TypedArray with byte offset
    def test_typed_array_with_offset(self):
        """TypedArray with byte offset"""
        typed_arr = self.handler.create_typed_array(
            'Int32Array',
            [1, 2, 3, 4, 5],
            byte_offset=4  # Skip first element
        )
        assert typed_arr['length'] == 4  # 5 - 1
        result = self.handler.at(typed_arr, 0)
        assert result['value'] == 2  # First element after offset

    def test_typed_array_with_offset_and_length(self):
        """TypedArray with byte offset and limited length"""
        typed_arr = self.handler.create_typed_array(
            'Int32Array',
            [1, 2, 3, 4, 5],
            byte_offset=4,
            length=2
        )
        assert typed_arr['length'] == 2
        result = self.handler.at(typed_arr, 1)
        assert result['value'] == 3

    # Error handling
    def test_typed_array_invalid_type(self):
        """Invalid TypedArray type raises error"""
        with pytest.raises(ValueError, match="Invalid TypedArray type"):
            self.handler.validate_typed_array('InvalidArray', [1, 2, 3])

    def test_typed_array_bigint_with_float(self):
        """BigInt arrays cannot contain floats"""
        with pytest.raises(TypeError, match="BigInt arrays require integer values"):
            self.handler.validate_typed_array('BigInt64Array', [1.5, 2.5])


class TestTypedArrayIterationEdgeCases:
    """Test TypedArray iteration edge cases"""

    def setup_method(self):
        """Setup test fixtures"""
        self.handler = TypedArrayHandler()

    # FR-ES24-D-014: Empty TypedArray
    def test_find_last_empty_typed_array(self):
        """findLast on empty TypedArray"""
        typed_arr = self.handler.create_typed_array('Int8Array', [])
        result = self.handler.find_last(typed_arr, lambda x, i, a: True)
        assert result['found'] is False

    # FR-ES24-D-014: findLast with boundary values
    def test_find_last_typed_array_boundary_values(self):
        """findLast finds boundary values"""
        typed_arr = self.handler.create_typed_array('Int8Array', [-128, 0, 127])
        result = self.handler.find_last(typed_arr, lambda x, i, a: x == 127)
        assert result['found'] is True
        assert result['value'] == 127

    # FR-ES24-D-014: TypedArray cannot be sparse
    def test_typed_array_cannot_be_sparse(self):
        """TypedArray cannot have holes (always dense)"""
        typed_arr = self.handler.create_typed_array('Int8Array', [1, 2, 3])
        info = self.handler.detect_edge_cases(typed_arr)
        assert info['is_sparse'] is False  # TypedArrays are always dense
