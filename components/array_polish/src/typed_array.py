"""
TypedArray boundary handling - ES2024 Wave D

Requirement: FR-ES24-D-011
"""

import math
from typing import List, Any, Dict, Optional, Callable


class TypedArrayHandler:
    """
    TypedArray boundary condition and edge case handling.

    Supports all TypedArray types with comprehensive boundary checking,
    overflow/underflow handling, and special value support.
    """

    # TypedArray boundary values
    BOUNDARIES = {
        'Int8Array': {'min': -128, 'max': 127},
        'Uint8Array': {'min': 0, 'max': 255},
        'Uint8ClampedArray': {'min': 0, 'max': 255},
        'Int16Array': {'min': -32768, 'max': 32767},
        'Uint16Array': {'min': 0, 'max': 65535},
        'Int32Array': {'min': -2147483648, 'max': 2147483647},
        'Uint32Array': {'min': 0, 'max': 4294967295},
        'Float32Array': {'min': float('-inf'), 'max': float('inf')},
        'Float64Array': {'min': float('-inf'), 'max': float('inf')},
        'BigInt64Array': {'min': -(2**63), 'max': 2**63 - 1},
        'BigUint64Array': {'min': 0, 'max': 2**64 - 1},
    }

    def validate_typed_array(
        self,
        array_type: str,
        elements: List[Any]
    ) -> Dict[str, Any]:
        """
        Validate TypedArray elements against type boundaries.

        Args:
            array_type: TypedArray type name
            elements: Array elements

        Returns:
            Dict with validation results and edge case flags

        Raises:
            ValueError: If array_type is invalid
            TypeError: If elements are invalid for type

        Requirements: FR-ES24-D-011
        """
        # Validate array type
        if array_type not in self.BOUNDARIES:
            raise ValueError(f"Invalid TypedArray type: {array_type}")

        # Get boundaries
        bounds = self.BOUNDARIES[array_type]

        # Initialize result
        result = {
            'valid': True,
            'min_value': bounds['min'],
            'max_value': bounds['max'],
            'has_overflow': False,
            'clamped': False,
            'has_nan': False,
            'has_negative_zero': False,
            'has_infinity': False
        }

        # Check BigInt arrays
        is_bigint = 'BigInt' in array_type
        if is_bigint:
            for elem in elements:
                if isinstance(elem, float) and not elem.is_integer():
                    raise TypeError("BigInt arrays require integer values")

        # Check Float arrays for special values
        is_float = 'Float' in array_type
        for elem in elements:
            if isinstance(elem, float):
                if math.isnan(elem):
                    result['has_nan'] = True
                elif math.isinf(elem):
                    result['has_infinity'] = True
                elif elem == 0 and math.copysign(1, elem) == -1:
                    result['has_negative_zero'] = True

            # Check for overflow (values outside boundaries)
            if not is_float and isinstance(elem, (int, float)):
                if elem < bounds['min'] or elem > bounds['max']:
                    result['has_overflow'] = True
                    if array_type == 'Uint8ClampedArray':
                        result['clamped'] = True

        return result

    def create_typed_array(
        self,
        array_type: str,
        elements: List[Any],
        byte_offset: int = 0,
        length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a TypedArray representation with offset and length.

        Args:
            array_type: TypedArray type name
            elements: Array elements
            byte_offset: Byte offset in buffer
            length: Array length (None = all after offset)

        Returns:
            TypedArray representation dict

        Requirements: FR-ES24-D-011
        """
        # Validate type
        if array_type not in self.BOUNDARIES:
            raise ValueError(f"Invalid TypedArray type: {array_type}")

        # Calculate element size in bytes
        element_sizes = {
            'Int8Array': 1,
            'Uint8Array': 1,
            'Uint8ClampedArray': 1,
            'Int16Array': 2,
            'Uint16Array': 2,
            'Int32Array': 4,
            'Uint32Array': 4,
            'Float32Array': 4,
            'Float64Array': 8,
            'BigInt64Array': 8,
            'BigUint64Array': 8,
        }
        element_size = element_sizes[array_type]

        # Calculate offset in elements
        element_offset = byte_offset // element_size

        # Get effective elements after offset
        effective_elements = elements[element_offset:]

        # Apply length limit if specified
        if length is not None:
            effective_elements = effective_elements[:length]

        # Calculate byte length
        actual_length = len(effective_elements)
        byte_length = actual_length * element_size

        return {
            'type': array_type,
            'elements': effective_elements,
            'length': actual_length,
            'byte_length': byte_length,
            'byte_offset': byte_offset
        }

    def at(
        self,
        typed_array: Dict[str, Any],
        index: int
    ) -> Dict[str, Any]:
        """
        Access TypedArray element at index with edge case handling.

        Args:
            typed_array: TypedArray representation
            index: Index to access

        Returns:
            Dict with 'value' and 'is_undefined'

        Requirements: FR-ES24-D-011, FR-ES24-D-012
        """
        elements = typed_array['elements']
        length = typed_array['length']

        # Handle empty array
        if length == 0:
            return {'value': None, 'is_undefined': True}

        # Convert negative index
        actual_index = index if index >= 0 else length + index

        # Check bounds
        if actual_index < 0 or actual_index >= length:
            return {'value': None, 'is_undefined': True}

        # Return value
        return {'value': elements[actual_index], 'is_undefined': False}

    def find_last(
        self,
        typed_array: Dict[str, Any],
        predicate: Callable[[Any, int, List[Any]], bool]
    ) -> Dict[str, Any]:
        """
        Find last matching element in TypedArray.

        Args:
            typed_array: TypedArray representation
            predicate: Predicate function

        Returns:
            Dict with 'value' and 'found'

        Requirements: FR-ES24-D-011, FR-ES24-D-013
        """
        elements = typed_array['elements']

        # Search from end to beginning
        for i in range(len(elements) - 1, -1, -1):
            if predicate(elements[i], i, elements):
                return {'value': elements[i], 'found': True}

        return {'value': None, 'found': False}

    def detect_edge_cases(
        self,
        typed_array: Dict[str, Any]
    ) -> Dict[str, bool]:
        """
        Detect edge cases in TypedArray.

        Args:
            typed_array: TypedArray representation

        Returns:
            Dict with edge case flags

        Requirements: FR-ES24-D-011, FR-ES24-D-014
        """
        elements = typed_array['elements']

        info = {
            'is_empty': len(elements) == 0,
            'is_sparse': False,  # TypedArrays are always dense
            'has_negative_zero': False,
            'has_nan': False,
            'has_infinity': False,
            'has_undefined': False
        }

        # Check for special values
        for value in elements:
            if isinstance(value, float):
                if math.isnan(value):
                    info['has_nan'] = True
                elif math.isinf(value):
                    info['has_infinity'] = True
                elif value == 0 and math.copysign(1, value) == -1:
                    info['has_negative_zero'] = True

        return info
