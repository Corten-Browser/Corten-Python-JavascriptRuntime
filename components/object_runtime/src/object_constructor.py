"""
Object constructor with ES2024 static methods.

This module provides the JavaScript Object constructor with static methods
like Object.groupBy() and Object.hasOwn() from ECMAScript 2024.

Requirements:
- FR-P3.5-032: Object.groupBy(items, callback)
- FR-P3.5-033: Object.hasOwn(obj, prop)
"""

from typing import Any, Callable, Dict, List, Optional


class ObjectConstructor:
    """
    JavaScript Object constructor with ES2024 static methods.

    This class provides static methods that operate on objects and arrays,
    following ECMAScript 2024 specification.
    """

    @staticmethod
    def groupBy(items: List[Any], callback: Callable[[Any, int], Any]) -> Dict[str, List[Any]]:
        """
        Group array elements by callback return value.

        Groups elements of an iterable according to the string values returned
        by a provided callback function. Returns a plain object with properties
        for each group, containing arrays of elements in each group.

        ES2024 Specification: Object.groupBy(items, callbackFn)

        Args:
            items: Array-like iterable to group
            callback: Function called for each element with (element, index)
                     Returns the key (will be coerced to string) to group element under

        Returns:
            Plain dictionary with string keys mapping to arrays of grouped elements

        Raises:
            TypeError: If items is not iterable
            TypeError: If callback is not callable

        Example:
            >>> items = [
            ...     {'type': 'fruit', 'name': 'apple'},
            ...     {'type': 'vegetable', 'name': 'carrot'},
            ...     {'type': 'fruit', 'name': 'banana'}
            ... ]
            >>> result = ObjectConstructor.groupBy(items, lambda x, i: x['type'])
            >>> result['fruit']
            [{'type': 'fruit', 'name': 'apple'}, {'type': 'fruit', 'name': 'banana'}]
            >>> result['vegetable']
            [{'type': 'vegetable', 'name': 'carrot'}]

        Example with numeric keys:
            >>> numbers = [1, 2, 3, 4, 5, 6]
            >>> result = ObjectConstructor.groupBy(numbers, lambda x, i: 'even' if x % 2 == 0 else 'odd')
            >>> result['even']
            [2, 4, 6]
            >>> result['odd']
            [1, 3, 5]
        """
        if not hasattr(items, '__iter__'):
            raise TypeError("items must be iterable")

        if not callable(callback):
            raise TypeError("callback must be callable")

        result: Dict[str, List[Any]] = {}

        for index, item in enumerate(items):
            # Call callback with element and index
            key = callback(item, index)

            # Coerce key to string (JavaScript behavior)
            key_str = str(key)

            # Initialize group if it doesn't exist
            if key_str not in result:
                result[key_str] = []

            # Add item to group
            result[key_str].append(item)

        return result

    @staticmethod
    def hasOwn(obj: Any, prop: str) -> bool:
        """
        Check if object has own property (not inherited).

        Reliable replacement for Object.prototype.hasOwnProperty.call(obj, prop).
        Works correctly even if obj has overridden hasOwnProperty or is null-prototype.

        ES2024 Specification: Object.hasOwn(obj, property)

        Args:
            obj: Object to check for property
            prop: Property name to check

        Returns:
            True if obj has prop as own property, False otherwise

        Raises:
            TypeError: If obj is None or not an object-like type

        Example:
            >>> obj = {'a': 1, 'b': 2}
            >>> ObjectConstructor.hasOwn(obj, 'a')
            True
            >>> ObjectConstructor.hasOwn(obj, 'c')
            False

        Example with null prototype (simulated):
            >>> class NullProto:
            ...     def __init__(self):
            ...         self.x = 10
            >>> obj = NullProto()
            >>> ObjectConstructor.hasOwn(obj, 'x')
            True

        Example where hasOwnProperty is overridden:
            >>> obj = {'hasOwnProperty': 'not a function', 'a': 1}
            >>> ObjectConstructor.hasOwn(obj, 'a')  # Still works!
            True
        """
        if obj is None:
            raise TypeError("Cannot convert undefined or null to object")

        # For dictionaries, use 'in' to check own properties
        if isinstance(obj, dict):
            return prop in obj

        # For objects with __dict__, check __dict__ directly (own properties)
        if hasattr(obj, '__dict__'):
            return prop in obj.__dict__

        # For other types, check if attribute exists and is not inherited
        # This handles cases where __dict__ might not be available
        if hasattr(obj, prop):
            # Check if it's truly an own property
            # by verifying it's in the object's namespace, not just inherited
            try:
                return prop in dir(obj) and not hasattr(type(obj), prop)
            except:
                # Fallback: if we can't determine, check with hasattr
                return hasattr(obj, prop)

        return False


# Alias for convenience (matches JavaScript naming)
Object = ObjectConstructor
