"""
Array edge cases implementation - ES2024 Wave D

Implements:
- FR-ES24-D-010: Array method edge cases (empty, sparse)
- FR-ES24-D-012: Array.prototype.at() edge cases
- FR-ES24-D-013: Array.prototype.findLast/findLastIndex edge cases
- FR-ES24-D-014: Array iteration edge cases
"""

import math
from typing import List, Any, Callable, Dict, Optional


class ArrayEdgeCases:
    """
    Comprehensive array edge case handling for ES2024 compliance.

    Provides robust implementations of array methods with edge case coverage
    for empty arrays, sparse arrays, boundary conditions, and special values.
    """

    def at(
        self,
        array: List[Any],
        index: int,
        is_sparse: bool = False
    ) -> Dict[str, Any]:
        """
        Array.prototype.at() with comprehensive edge case handling.

        Supports negative indices, boundary conditions, empty arrays, sparse arrays.

        Args:
            array: Input array (may be empty or sparse)
            index: Index to access (supports negative indices)
            is_sparse: Whether array is sparse (holes vs undefined)

        Returns:
            Dict with 'value' and 'is_undefined' keys

        Raises:
            TypeError: If array is not a list or index is not an integer

        Requirements: FR-ES24-D-010, FR-ES24-D-012
        Performance: O(1)
        """
        # Input validation
        if not isinstance(array, list):
            raise TypeError("First argument must be an array")
        if not isinstance(index, int):
            raise TypeError("Index must be an integer")

        # Handle empty array
        if len(array) == 0:
            return {'value': None, 'is_undefined': True}

        # Convert negative index to positive
        actual_index = index if index >= 0 else len(array) + index

        # Check bounds
        if actual_index < 0 or actual_index >= len(array):
            return {'value': None, 'is_undefined': True}

        # Get value
        value = array[actual_index]

        # Handle sparse array hole
        if is_sparse and value is None:
            return {'value': None, 'is_undefined': True}

        # Return value
        return {'value': value, 'is_undefined': False}

    def find_last(
        self,
        array: List[Any],
        predicate: Callable[[Any, int, List[Any]], bool],
        is_sparse: bool = False
    ) -> Dict[str, Any]:
        """
        Array.prototype.findLast() with comprehensive edge case handling.

        Searches array from end to beginning, returns last element matching predicate.

        Args:
            array: Input array to search
            predicate: Function (element, index, array) -> bool
            is_sparse: Whether to skip holes

        Returns:
            Dict with 'value' and 'found' keys

        Raises:
            TypeError: If array is not a list or predicate is not callable

        Requirements: FR-ES24-D-010, FR-ES24-D-013, FR-ES24-D-014
        Performance: O(n)
        """
        # Input validation
        if not isinstance(array, list):
            raise TypeError("First argument must be an array")
        if not callable(predicate):
            raise TypeError("Predicate must be a callable")

        # Search from end to beginning
        for i in range(len(array) - 1, -1, -1):
            element = array[i]

            # Skip holes in sparse arrays
            if is_sparse and element is None:
                continue

            # Test predicate
            try:
                if predicate(element, i, array):
                    return {'value': element, 'found': True}
            except Exception as e:
                # Propagate predicate errors
                raise e

        # Not found
        return {'value': None, 'found': False}

    def find_last_index(
        self,
        array: List[Any],
        predicate: Callable[[Any, int, List[Any]], bool],
        is_sparse: bool = False
    ) -> Dict[str, Any]:
        """
        Array.prototype.findLastIndex() with comprehensive edge case handling.

        Searches array from end to beginning, returns index of last matching element.

        Args:
            array: Input array to search
            predicate: Function (element, index, array) -> bool
            is_sparse: Whether to skip holes

        Returns:
            Dict with 'index' and 'found' keys

        Raises:
            TypeError: If array is not a list or predicate is not callable

        Requirements: FR-ES24-D-010, FR-ES24-D-013, FR-ES24-D-014
        Performance: O(n)
        """
        # Input validation
        if not isinstance(array, list):
            raise TypeError("First argument must be an array")
        if not callable(predicate):
            raise TypeError("Predicate must be a callable")

        # Search from end to beginning
        for i in range(len(array) - 1, -1, -1):
            element = array[i]

            # Skip holes in sparse arrays
            if is_sparse and element is None:
                continue

            # Test predicate
            try:
                if predicate(element, i, array):
                    return {'index': i, 'found': True}
            except Exception as e:
                # Propagate predicate errors
                raise e

        # Not found
        return {'index': -1, 'found': False}

    def handle_sparse(
        self,
        array: List[Any],
        mode: str = 'remove_holes',
        is_sparse: bool = False,
        holes: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Handle sparse array edge cases with comprehensive normalization.

        Provides options for hole removal, hole preservation, or explicit undefined conversion.

        Args:
            array: Input array (may be sparse)
            mode: 'remove_holes', 'preserve_holes', or 'explicit_undefined'
            is_sparse: Whether array contains holes
            holes: List of indices that are holes (if known)

        Returns:
            Dict with 'normalized_array', 'holes_removed', 'original_holes'

        Raises:
            TypeError: If array is not a list or mode is not a string
            ValueError: If mode is not a valid option

        Requirements: FR-ES24-D-010, FR-ES24-D-014
        Performance: O(n)
        """
        # Input validation
        if not isinstance(array, list):
            raise TypeError("First argument must be an array")
        if not isinstance(mode, str):
            raise TypeError("Mode must be a string")
        if mode not in ('remove_holes', 'preserve_holes', 'explicit_undefined'):
            raise ValueError("Mode must be one of: remove_holes, preserve_holes, explicit_undefined")

        # Determine which indices are holes
        if holes is not None:
            hole_indices = set(holes)
        elif is_sparse:
            # In sparse arrays, None values at indices are holes
            hole_indices = {i for i, v in enumerate(array) if v is None}
        else:
            # Not sparse, no holes
            hole_indices = set()

        original_holes = sorted(list(hole_indices))

        # Handle based on mode
        if mode == 'preserve_holes':
            # Keep array as-is
            return {
                'normalized_array': array.copy(),
                'holes_removed': False,
                'original_holes': original_holes
            }

        elif mode == 'remove_holes':
            # Remove holes, compacting array
            normalized = [v for i, v in enumerate(array) if i not in hole_indices]
            return {
                'normalized_array': normalized,
                'holes_removed': len(hole_indices) > 0,
                'original_holes': original_holes
            }

        else:  # mode == 'explicit_undefined'
            # Convert holes to explicit undefined (keep None)
            normalized = array.copy()
            return {
                'normalized_array': normalized,
                'holes_removed': len(hole_indices) > 0,
                'original_holes': original_holes
            }

    def detect_edge_cases(
        self,
        array: List[Any],
        is_sparse: bool = False
    ) -> Dict[str, bool]:
        """
        Analyze array for common edge cases and special values.

        Returns comprehensive edge case information.

        Args:
            array: Array to analyze
            is_sparse: Whether array is sparse

        Returns:
            Dict with edge case flags (is_empty, is_sparse, has_nan, etc.)

        Raises:
            TypeError: If array is not a list

        Requirements: FR-ES24-D-010, FR-ES24-D-014
        Performance: O(n) - single pass through array

        Example:
            >>> ec = ArrayEdgeCases()
            >>> ec.detect_edge_cases([1, float('nan'), -0.0])
            {'is_empty': False, 'is_sparse': False, 'has_nan': True,
             'has_negative_zero': True, 'has_infinity': False, 'has_undefined': False}
        """
        # Input validation
        if not isinstance(array, list):
            raise TypeError("Argument must be an array")

        # Initialize flags
        info = {
            'is_empty': len(array) == 0,
            'is_sparse': is_sparse,
            'has_negative_zero': False,
            'has_nan': False,
            'has_infinity': False,
            'has_undefined': False
        }

        # Early exit for empty arrays
        if info['is_empty']:
            return info

        # Scan for special values (single pass optimization)
        for value in array:
            # Check for NaN
            if isinstance(value, float) and math.isnan(value):
                info['has_nan'] = True

            # Check for negative zero
            elif isinstance(value, (int, float)) and value == 0:
                if math.copysign(1, value) == -1:
                    info['has_negative_zero'] = True

            # Check for Infinity
            elif isinstance(value, float) and math.isinf(value):
                info['has_infinity'] = True

            # Check for explicit undefined (None in non-sparse array)
            elif value is None and not is_sparse:
                info['has_undefined'] = True

        return info
