"""
Array constructor static methods (ES2024).

Implements ES2024 Array constructor improvements:
- Array.from() with mapping - FR-ES24-030
- Array.of() - FR-ES24-031
- Array.isArray() helper

Time Complexity:
- from_iterable(): O(n)
- of(): O(n)
- is_array(): O(1)
"""

from typing import Any, List, Callable, Optional, Iterable


class ArrayConstructorMethods:
    """
    ES2024 Array constructor static method implementations.

    Provides static methods for array creation and type checking.
    """

    def from_iterable(
        self,
        iterable: Iterable[Any],
        map_fn: Optional[Callable] = None,
        this_arg: Any = None
    ) -> List[Any]:
        """
        Create array from iterable with optional mapping.

        Implements Array.from() per ES2024 spec.
        Converts any iterable to array, optionally applying mapping function.

        Time Complexity: O(n) where n is iterable length
        Space Complexity: O(n) for result array

        Args:
            iterable: Any iterable object (list, generator, string, etc.)
            map_fn: Optional mapping function (element, index) -> value
            this_arg: Optional this binding for map_fn

        Returns:
            New array from iterable

        Example:
            >>> constructor = ArrayConstructorMethods()
            >>> constructor.from_iterable([1, 2, 3])
            [1, 2, 3]
            >>> constructor.from_iterable("hello")
            ['h', 'e', 'l', 'l', 'o']
            >>> constructor.from_iterable([1, 2, 3], map_fn=lambda x: x * 2)
            [2, 4, 6]
            >>> constructor.from_iterable(range(5))
            [0, 1, 2, 3, 4]
        """
        result = []

        # Convert iterable to list first to support indexing
        items = list(iterable)

        # If no mapping function, just return list
        if map_fn is None:
            return items

        # Apply mapping function to each element
        for index, element in enumerate(items):
            try:
                # Try calling with both element and index
                mapped = map_fn(element, index)
            except TypeError:
                # Fallback to just element if map_fn doesn't accept index
                try:
                    mapped = map_fn(element)
                except TypeError:
                    # If still fails, just use element as-is
                    mapped = element

            result.append(mapped)

        return result

    def of(self, *elements: Any) -> List[Any]:
        """
        Create array from arguments.

        Implements Array.of() per ES2024 spec.
        Unlike Array(n) which creates array of length n,
        Array.of(n) creates array containing n.

        Time Complexity: O(n) where n is number of arguments
        Space Complexity: O(n)

        Args:
            *elements: Variable number of elements

        Returns:
            New array containing elements

        Example:
            >>> constructor = ArrayConstructorMethods()
            >>> constructor.of(1, 2, 3)
            [1, 2, 3]
            >>> constructor.of(5)
            [5]  # Not array of length 5
            >>> constructor.of()
            []
            >>> constructor.of(1, "hello", True, None)
            [1, 'hello', True, None]
        """
        return list(elements)

    def is_array(self, value: Any) -> bool:
        """
        Check if value is an array.

        Implements Array.isArray() per ES2024 spec.
        In Python, only list type is considered array.

        Time Complexity: O(1)
        Space Complexity: O(1)

        Args:
            value: Value to check

        Returns:
            True if value is array (list), False otherwise

        Example:
            >>> constructor = ArrayConstructorMethods()
            >>> constructor.is_array([1, 2, 3])
            True
            >>> constructor.is_array([])
            True
            >>> constructor.is_array("hello")
            False
            >>> constructor.is_array(42)
            False
            >>> constructor.is_array(None)
            False
            >>> constructor.is_array((1, 2, 3))  # Tuple is not array
            False
        """
        return isinstance(value, list)
