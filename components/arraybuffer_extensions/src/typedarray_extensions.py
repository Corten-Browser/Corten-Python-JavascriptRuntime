"""
TypedArray Extensions for ES2024
Non-mutating toReversed() and toSorted() methods

Requirements: FR-ES24-007, FR-ES24-008
"""

from typing import Any, Callable, Optional
from copy import deepcopy


class TypedArrayExtensions:
    """
    TypedArray ES2024 method extensions for non-mutating operations
    """

    def to_reversed(self, typed_array: Any) -> Any:
        """
        Return reversed copy of TypedArray (non-mutating)

        Args:
            typed_array: Source TypedArray

        Returns:
            New TypedArray with reversed elements

        Requirement: FR-ES24-007
        """
        # Create deep copy to avoid mutating original
        reversed_array = deepcopy(typed_array)

        # Reverse the values
        if hasattr(reversed_array, 'values') and isinstance(reversed_array.values, list):
            reversed_array.values = reversed_array.values[::-1]

        return reversed_array

    def to_sorted(self, typed_array: Any, compare_fn: Optional[Callable[[Any, Any], int]] = None) -> Any:
        """
        Return sorted copy of TypedArray (non-mutating)

        Args:
            typed_array: Source TypedArray
            compare_fn: Optional comparison function (a, b) -> int
                       Returns: <0 if a<b, 0 if a==b, >0 if a>b

        Returns:
            New TypedArray with sorted elements

        Requirement: FR-ES24-008
        """
        # Create deep copy to avoid mutating original
        sorted_array = deepcopy(typed_array)

        # Sort the values
        if hasattr(sorted_array, 'values') and isinstance(sorted_array.values, list):
            if compare_fn is None:
                # Default numeric sort
                sorted_array.values = sorted(sorted_array.values)
            else:
                # Custom comparison function
                # Python's sorted() uses key function, but we need compare function
                # Convert compare_fn to key using functools.cmp_to_key
                from functools import cmp_to_key
                sorted_array.values = sorted(sorted_array.values, key=cmp_to_key(compare_fn))

        return sorted_array
