"""
Stable array sorting (ES2024).

Implements ES2024 Array.prototype.sort() stability requirement:
- Array.prototype.sort() must be stable - FR-ES24-032

Stable sort: equal elements maintain their relative order from input.

Time Complexity: O(n log n)
Space Complexity: O(n) for merge sort implementation
"""

from typing import Any, List, Callable, Optional
from functools import cmp_to_key


class ArraySorting:
    """
    ES2024 stable sorting implementation.

    Provides stable sort for arrays per ES2024 requirement.
    Python's built-in sort (Timsort) is already stable.
    """

    def sort_stable(
        self,
        array: List[Any],
        compare_fn: Optional[Callable[[Any, Any], int]] = None
    ) -> List[Any]:
        """
        Sort array with stability guarantee (mutating).

        Implements Array.prototype.sort() per ES2024 spec.
        ES2024 requires sort to be stable: equal elements maintain relative order.

        Uses Python's Timsort algorithm which is guaranteed stable.

        Time Complexity: O(n log n)
        Space Complexity: O(n)

        Args:
            array: Array to sort (mutated in place)
            compare_fn: Optional comparison function (a, b) -> int
                       Returns: <0 if a<b, 0 if a==b, >0 if a>b
                       If None, uses default numeric/lexicographic sorting

        Returns:
            Sorted array (same reference as input)

        Example:
            >>> sorting = ArraySorting()
            >>> arr = [3, 1, 4, 1, 5]
            >>> sorting.sort_stable(arr)
            [1, 1, 3, 4, 5]

            # Stability demonstration
            >>> arr = [
            ...     {"val": 2, "id": "a"},
            ...     {"val": 1, "id": "b"},
            ...     {"val": 2, "id": "c"},
            ... ]
            >>> sorting.sort_stable(arr, lambda a, b: a["val"] - b["val"])
            # Result: id order for val=2 is "a", "c" (original order preserved)
        """
        # Handle empty array or single element
        if len(array) <= 1:
            return array

        # If no compare function provided, use default sorting
        if compare_fn is None:
            # Default sort behavior
            try:
                # Try numeric sort if possible
                array.sort()
            except TypeError:
                # Fallback to string comparison if mixed types
                array.sort(key=lambda x: (str(type(x)), str(x)))
        else:
            # Use provided compare function
            # Convert compare function to key function for Python's sort
            array.sort(key=cmp_to_key(compare_fn))

        return array
