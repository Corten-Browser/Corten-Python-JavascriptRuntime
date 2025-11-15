"""
Array.prototype ES2024 method implementations.

Implements ES2024 Array.prototype method gaps:
- Array.prototype.at() - FR-ES24-026
- Array.prototype.flat() - FR-ES24-027
- Array.prototype.flatMap() - FR-ES24-028
- Array.prototype.includes() - FR-ES24-029
- Array.prototype.copyWithin() - FR-ES24-033
- Array.prototype.fill() - FR-ES24-034

Time Complexity:
- at(): O(1)
- flat(): O(n * d) where d is depth
- flatMap(): O(n)
- includes(): O(n)
- copyWithin(): O(k) where k is copy range
- fill(): O(k) where k is fill range
"""

from typing import Any, List, Callable, Optional
import math


class ArrayMethods:
    """
    ES2024 Array.prototype method implementations.

    Provides methods for array manipulation following ECMAScript 2024 spec.
    """

    def at(self, array: List[Any], index: int) -> Optional[Any]:
        """
        Get element at index (supports negative indices).

        Implements Array.prototype.at() per ES2024 spec.
        Negative indices count from end: -1 is last element.

        Time Complexity: O(1)
        Space Complexity: O(1)

        Args:
            array: Source array
            index: Index (negative from end)

        Returns:
            Element at index or None if out of bounds

        Example:
            >>> methods = ArrayMethods()
            >>> methods.at([1, 2, 3], -1)
            3
            >>> methods.at([1, 2, 3], 1)
            2
            >>> methods.at([1, 2, 3], 10)
            None
        """
        # Handle empty array
        if not array:
            return None

        # Convert negative index to positive
        if index < 0:
            index = len(array) + index

        # Check bounds
        if index < 0 or index >= len(array):
            return None

        return array[index]

    def flat(self, array: List[Any], depth: int = 1) -> List[Any]:
        """
        Flatten nested arrays to specified depth.

        Implements Array.prototype.flat() per ES2024 spec.
        Recursively flattens nested arrays up to specified depth.

        Time Complexity: O(n * d) where n is elements, d is depth
        Space Complexity: O(n * d) for result array

        Args:
            array: Source array (may contain nested arrays)
            depth: Flattening depth (default: 1, use float('inf') for complete)

        Returns:
            New flattened array

        Example:
            >>> methods = ArrayMethods()
            >>> methods.flat([1, [2, 3], [4, [5]]])
            [1, 2, 3, 4, [5]]
            >>> methods.flat([1, [2, [3, [4]]]], depth=2)
            [1, 2, 3, [4]]
            >>> methods.flat([1, [2, [3]]], depth=float('inf'))
            [1, 2, 3]
        """
        def flatten_recursive(arr: List[Any], current_depth: int) -> List[Any]:
            """Recursively flatten array to specified depth."""
            result = []

            for item in arr:
                # Skip None (empty slots in JavaScript)
                if item is None:
                    continue

                # If item is list and we have depth remaining, recurse
                if isinstance(item, list) and current_depth > 0:
                    result.extend(flatten_recursive(item, current_depth - 1))
                else:
                    result.append(item)

            return result

        return flatten_recursive(array, depth)

    def flat_map(
        self,
        array: List[Any],
        callback: Callable,
        this_arg: Any = None
    ) -> List[Any]:
        """
        Map and flatten (depth 1) in single operation.

        Implements Array.prototype.flatMap() per ES2024 spec.
        Equivalent to map().flat() but more efficient.

        Time Complexity: O(n)
        Space Complexity: O(n)

        Args:
            array: Source array
            callback: Mapping function (element, index) -> value or array
            this_arg: Optional this binding for callback

        Returns:
            New mapped and flattened array

        Example:
            >>> methods = ArrayMethods()
            >>> methods.flat_map([1, 2, 3], lambda x: [x, x * 2])
            [1, 2, 2, 4, 3, 6]
            >>> methods.flat_map([1, 2], lambda x: [[x]])
            [[1], [2]]
        """
        result = []

        for index, element in enumerate(array):
            # Call callback with element and index
            try:
                # Try calling with both element and index
                mapped = callback(element, index)
            except TypeError:
                # Fallback to just element if callback doesn't accept index
                mapped = callback(element)

            # Flatten one level
            if isinstance(mapped, list):
                result.extend(mapped)
            else:
                # Non-array returns are treated as single element
                result.append(mapped)

        return result

    def includes(
        self,
        array: List[Any],
        search_element: Any,
        from_index: int = 0
    ) -> bool:
        """
        Check if array includes element (uses SameValueZero).

        Implements Array.prototype.includes() per ES2024 spec.
        Uses SameValueZero comparison (like === but NaN equals NaN).

        Time Complexity: O(n)
        Space Complexity: O(1)

        Args:
            array: Source array
            search_element: Element to search for
            from_index: Starting index (negative from end)

        Returns:
            True if element found, False otherwise

        Example:
            >>> methods = ArrayMethods()
            >>> methods.includes([1, 2, 3], 2)
            True
            >>> methods.includes([1, 2, 3], 4)
            False
            >>> methods.includes([1, 2, 3], 2, from_index=3)
            False
            >>> methods.includes([1, float('nan'), 3], float('nan'))
            True
        """
        # Handle empty array
        if not array:
            return False

        # Convert negative from_index to positive
        if from_index < 0:
            from_index = max(0, len(array) + from_index)

        # Search from from_index to end
        for i in range(from_index, len(array)):
            element = array[i]

            # SameValueZero comparison
            # Special case: NaN equals NaN
            if isinstance(search_element, float) and math.isnan(search_element):
                if isinstance(element, float) and math.isnan(element):
                    return True
            # Special case: +0 equals -0
            elif search_element == 0 and element == 0:
                return True
            # Standard equality
            elif element == search_element:
                return True

        return False

    def copy_within(
        self,
        array: List[Any],
        target: int,
        start: int,
        end: Optional[int] = None
    ) -> List[Any]:
        """
        Copy sequence within array (mutating).

        Implements Array.prototype.copyWithin() per ES2024 spec.
        Copies elements from [start, end) to position starting at target.
        Mutates array in place.

        Time Complexity: O(k) where k is copy range
        Space Complexity: O(k) for temporary copy

        Args:
            array: Target array (mutated in place)
            target: Target index
            start: Source start index
            end: Source end index (default: len(array))

        Returns:
            Mutated array (same reference)

        Example:
            >>> methods = ArrayMethods()
            >>> arr = [1, 2, 3, 4, 5]
            >>> methods.copy_within(arr, target=0, start=3, end=5)
            [4, 5, 3, 4, 5]
            >>> arr  # Mutated in place
            [4, 5, 3, 4, 5]
        """
        length = len(array)

        # Default end to array length
        if end is None:
            end = length

        # Normalize negative indices
        if target < 0:
            target = max(0, length + target)
        else:
            target = min(target, length)

        if start < 0:
            start = max(0, length + start)
        else:
            start = min(start, length)

        if end < 0:
            end = max(0, length + end)
        else:
            end = min(end, length)

        # Calculate copy count
        count = min(end - start, length - target)

        if count <= 0:
            return array

        # Copy elements (handle overlapping ranges correctly)
        # Need to copy to temp first to handle overlaps
        temp = array[start:start + count]

        # Write to target position
        for i, value in enumerate(temp):
            if target + i < length:
                array[target + i] = value

        return array

    def fill(
        self,
        array: List[Any],
        value: Any,
        start: int = 0,
        end: Optional[int] = None
    ) -> List[Any]:
        """
        Fill array with value (mutating).

        Implements Array.prototype.fill() per ES2024 spec.
        Fills elements in range [start, end) with static value.
        Mutates array in place.

        Time Complexity: O(k) where k is fill range
        Space Complexity: O(1)

        Args:
            array: Target array (mutated in place)
            value: Fill value
            start: Start index (default: 0)
            end: End index (default: len(array))

        Returns:
            Mutated array (same reference)

        Example:
            >>> methods = ArrayMethods()
            >>> arr = [1, 2, 3, 4, 5]
            >>> methods.fill(arr, value=0, start=2, end=4)
            [1, 2, 0, 0, 5]
            >>> arr  # Mutated in place
            [1, 2, 0, 0, 5]
        """
        length = len(array)

        # Default end to array length
        if end is None:
            end = length

        # Normalize negative indices
        if start < 0:
            start = max(0, length + start)
        else:
            start = min(start, length)

        if end < 0:
            end = max(0, length + end)
        else:
            end = min(end, length)

        # Fill range
        for i in range(start, end):
            array[i] = value

        return array
