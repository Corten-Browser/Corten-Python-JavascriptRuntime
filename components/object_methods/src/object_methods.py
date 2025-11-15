"""
ObjectMethods - ES2024 Object static method implementations.

Implements:
- Object.fromEntries() - Create object from [key, value] pairs
- Object.entries() - Get [key, value] pairs from object
- Object.values() - Get values from object
- Object.getOwnPropertyDescriptors() - Get all property descriptors
- Object.setPrototypeOf() - Set object prototype
- Object.is() - SameValue equality comparison
- Object.assign() - Copy properties from sources to target

Requirements:
- FR-ES24-036: Object.fromEntries()
- FR-ES24-037: Object.entries()
- FR-ES24-038: Object.values()
- FR-ES24-039: Object.getOwnPropertyDescriptors()
- FR-ES24-040: Object.setPrototypeOf() edge cases
- FR-ES24-041: Object.is()
- FR-ES24-042: Object.assign() edge cases
"""

import math
from typing import Any, Dict, List, Iterable, Optional


class ObjectMethods:
    """
    Object static method implementations for ES2024 compliance.

    All methods are static and follow ECMAScript semantics.
    """

    @staticmethod
    def from_entries(entries: Iterable) -> Dict[str, Any]:
        """
        Create object from [key, value] pairs.

        Implements Object.fromEntries() per ES2024 spec.

        Args:
            entries: Iterable of [key, value] pairs

        Returns:
            New object with entries as properties

        Raises:
            TypeError: If entries are not iterable pairs

        Example:
            >>> ObjectMethods.from_entries([["a", 1], ["b", 2]])
            {'a': 1, 'b': 2}

        Complexity: O(n) where n is number of entries
        """
        result = {}

        for entry in entries:
            # Reject strings as entries (they're iterable but not valid pairs)
            if isinstance(entry, str):
                raise TypeError("Iterator value must be array-like, not string")

            # Each entry must be iterable (array-like)
            try:
                # Convert to list to ensure it's a pair
                pair = list(entry)
                if len(pair) < 2:
                    raise TypeError("Iterator value must be array-like with at least 2 elements")

                key = pair[0]
                value = pair[1]

                # Convert key to string (JavaScript object keys are strings)
                key_str = str(key)
                result[key_str] = value

            except TypeError as e:
                raise TypeError(f"Iterator value must be array-like: {e}")

        return result

    @staticmethod
    def entries(obj: Dict[str, Any]) -> List[List[Any]]:
        """
        Get enumerable own property [key, value] pairs.

        Implements Object.entries() per ES2024 spec.

        Args:
            obj: Object to get entries from

        Returns:
            Array of [key, value] pairs

        Example:
            >>> ObjectMethods.entries({"a": 1, "b": 2})
            [['a', 1], ['b', 2]]

        Complexity: O(n) where n is number of properties
        """
        # Return entries in insertion order (Python 3.7+)
        return [[key, value] for key, value in obj.items()]

    @staticmethod
    def values(obj: Dict[str, Any]) -> List[Any]:
        """
        Get enumerable own property values.

        Implements Object.values() per ES2024 spec.

        Args:
            obj: Object to get values from

        Returns:
            Array of property values

        Example:
            >>> ObjectMethods.values({"a": 1, "b": 2})
            [1, 2]

        Complexity: O(n) where n is number of properties
        """
        # Return values in insertion order (Python 3.7+)
        return list(obj.values())

    @staticmethod
    def get_own_property_descriptors(obj: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        Get all own property descriptors.

        Implements Object.getOwnPropertyDescriptors() per ES2024 spec.

        Args:
            obj: Object to get descriptors from

        Returns:
            Object mapping property names to descriptors

        Example:
            >>> desc = ObjectMethods.get_own_property_descriptors({"x": 10})
            >>> desc["x"]["value"]
            10

        Note:
            In Python, all dict properties are enumerable, writable, and configurable.
            This is a simplified implementation for the runtime.
        """
        descriptors = {}

        for key, value in obj.items():
            # Create property descriptor per ES spec
            descriptors[key] = {
                "value": value,
                "writable": True,
                "enumerable": True,
                "configurable": True
            }

        return descriptors

    @staticmethod
    def set_prototype_of(obj: Any, prototype: Optional[Any]) -> Any:
        """
        Set object prototype with edge case handling.

        Implements Object.setPrototypeOf() per ES2024 spec.

        Args:
            obj: Target object (must be object type)
            prototype: New prototype (object or null)

        Returns:
            The target object

        Raises:
            TypeError: If obj is not an object
            TypeError: If prototype is not an object or null

        Example:
            >>> obj = {"x": 1}
            >>> proto = {"y": 2}
            >>> ObjectMethods.set_prototype_of(obj, proto)
            {'x': 1}

        Note:
            In Python, we store the prototype reference.
            Full prototype chain walking would integrate with JSObject.
        """
        # Type check: target must be object
        if not isinstance(obj, dict):
            raise TypeError(f"Object.setPrototypeOf called on non-object: {type(obj).__name__}")

        # Type check: prototype must be object or null
        if prototype is not None and not isinstance(prototype, dict):
            raise TypeError(f"Object prototype may only be an Object or null: {type(prototype).__name__}")

        # In a full implementation, this would set __proto__
        # For now, we just validate and return the object
        # The actual prototype chain would be managed by JSObject
        obj["__proto__"] = prototype

        return obj

    @staticmethod
    def is_equal(value1: Any, value2: Any) -> bool:
        """
        SameValue equality comparison.

        Implements Object.is() per ES2024 spec.

        Differences from === operator:
        - Object.is(+0, -0) === false (=== gives true)
        - Object.is(NaN, NaN) === true (=== gives false)

        Args:
            value1: First value
            value2: Second value

        Returns:
            True if values are the same, False otherwise

        Example:
            >>> ObjectMethods.is_equal(42, 42)
            True
            >>> ObjectMethods.is_equal(NaN, NaN)
            True
            >>> ObjectMethods.is_equal(+0, -0)
            False

        Spec Reference: ECMAScript 2024 Section 7.2.10 SameValue(x, y)
        """
        # Type check first: different types are never equal
        # In JavaScript, true !== 1 (different types)
        if type(value1) != type(value2):
            return False

        # Special case: NaN === NaN (different from JavaScript ===)
        if isinstance(value1, float) and isinstance(value2, float):
            if math.isnan(value1) and math.isnan(value2):
                return True

            # Special case: +0 !== -0 (different from JavaScript ===)
            if value1 == 0 and value2 == 0:
                # Check signs using copysign or division by zero
                # 1/+0 = +inf, 1/-0 = -inf
                try:
                    sign1 = math.copysign(1, value1)
                    sign2 = math.copysign(1, value2)
                    return sign1 == sign2
                except:
                    pass

        # For all other values, use Python's identity/equality
        # Objects (dicts, lists, etc.) are compared by identity (is)
        if isinstance(value1, (dict, list)) or isinstance(value2, (dict, list)):
            return value1 is value2

        # Primitives compared by value
        return value1 == value2

    @staticmethod
    def assign(target: Any, sources: List[Optional[Dict[str, Any]]]) -> Any:
        """
        Copy enumerable own properties from sources to target.

        Implements Object.assign() per ES2024 spec.

        Args:
            target: Target object (must be object type)
            sources: List of source objects (null/undefined are skipped)

        Returns:
            The target object (modified in place)

        Raises:
            TypeError: If target is not an object

        Example:
            >>> target = {"a": 1}
            >>> ObjectMethods.assign(target, [{"b": 2}, {"c": 3}])
            {'a': 1, 'b': 2, 'c': 3}

        Note:
            - Sources are processed left to right
            - Later sources overwrite earlier ones
            - null/undefined sources are skipped
            - Only enumerable own properties are copied

        Complexity: O(n*m) where n is number of sources, m is average properties per source
        """
        # Type check: target must be object
        if not isinstance(target, dict):
            raise TypeError(f"Cannot convert {type(target).__name__} to object")

        # Process each source
        for source in sources:
            # Skip null/undefined sources
            if source is None:
                continue

            # Source must be object-like
            if not isinstance(source, dict):
                # In JavaScript, primitives are skipped
                # For now, we only support dicts
                continue

            # Copy enumerable own properties
            for key, value in source.items():
                target[key] = value

        return target
