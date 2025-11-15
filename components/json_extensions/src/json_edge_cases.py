"""
JSON edge case handling (FR-ES24-B-038)

Handles:
- Circular references (TypeError)
- BigInt serialization (TypeError)
- Symbol/function/undefined handling
- toJSON() method support
"""

from typing import Any, Set, Optional
import json


class BigInt:
    """Marker class for BigInt values (JavaScript BigInt equivalent)"""
    def __init__(self, value: int):
        self.value = value


class Symbol:
    """Marker class for Symbol values (JavaScript Symbol equivalent)"""
    def __init__(self, description: str = ""):
        self.description = description


class Undefined:
    """Marker class for undefined values (JavaScript undefined)"""
    pass


class JSONEdgeCases:
    """JSON edge case handling"""

    def __init__(self):
        self._seen_objects: Set[int] = set()

    def handle_circular_reference(self, value: Any) -> None:
        """
        Detect and throw on circular references

        Args:
            value: Value with circular reference

        Raises:
            TypeError: Converting circular structure to JSON
        """
        raise TypeError("Converting circular structure to JSON")

    def handle_bigint(self, value: Any) -> None:
        """
        Reject BigInt serialization

        Args:
            value: BigInt value

        Raises:
            TypeError: Do not know how to serialize a BigInt
        """
        raise TypeError("Do not know how to serialize a BigInt")

    def handle_symbol(self, value: Any) -> None:
        """
        Skip symbols in JSON (return undefined)

        Args:
            value: Symbol value

        Returns:
            None (undefined)
        """
        return None

    def handle_function(self, value: Any) -> None:
        """
        Skip functions in JSON (return undefined)

        Args:
            value: Function value

        Returns:
            None (undefined)
        """
        return None

    def handle_undefined_in_array(self, array: list) -> str:
        """
        Convert undefined to null in arrays

        Args:
            array: Array with undefined elements

        Returns:
            JSON with null for undefined
        """
        # Convert undefined to null
        result = []
        for item in array:
            if isinstance(item, Undefined) or (callable(item) and not isinstance(item, type)):
                result.append(None)
            elif isinstance(item, Symbol):
                result.append(None)
            else:
                result.append(item)

        return json.dumps(result)

    def handle_toJSON(self, value: Any) -> Any:
        """
        Call toJSON() if present before stringification

        Args:
            value: Object with toJSON method

        Returns:
            Result of toJSON()
        """
        if hasattr(value, 'toJSON') and callable(value.toJSON):
            return value.toJSON()
        return value

    def detect_circular(self, obj: Any, seen: Optional[Set[int]] = None) -> bool:
        """
        Detect circular references in object graph

        Args:
            obj: Object to check
            seen: Set of already seen object IDs

        Returns:
            True if circular reference detected
        """
        if seen is None:
            seen = set()

        # Only objects and lists can be circular
        if not isinstance(obj, (dict, list)):
            return False

        obj_id = id(obj)

        if obj_id in seen:
            return True

        seen.add(obj_id)

        # Check nested values
        try:
            if isinstance(obj, dict):
                for value in obj.values():
                    if self.detect_circular(value, seen):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if self.detect_circular(item, seen):
                        return True
        finally:
            seen.remove(obj_id)

        return False

    def prepare_for_json(self, value: Any, seen: Optional[Set[int]] = None) -> Any:
        """
        Prepare value for JSON serialization (handle all edge cases)

        Args:
            value: Value to prepare
            seen: Set of seen objects (for circular detection)

        Returns:
            Value ready for JSON serialization

        Raises:
            TypeError: For circular references or BigInt
        """
        if seen is None:
            seen = set()

        # Handle toJSON() method first
        if hasattr(value, 'toJSON') and callable(value.toJSON):
            value = value.toJSON()

        # Check for BigInt (by class name or instance)
        if isinstance(value, BigInt) or value.__class__.__name__ == 'BigInt':
            self.handle_bigint(value)

        # Check for Symbol (by class name or instance)
        if isinstance(value, Symbol) or value.__class__.__name__ == 'Symbol':
            return None  # undefined

        # Check for functions (callable but not a class)
        if callable(value) and not isinstance(value, type):
            return None  # undefined

        # Check for Undefined (by class name or instance)
        if isinstance(value, Undefined) or value.__class__.__name__ == 'Undefined':
            return None  # Will be handled differently in objects vs arrays

        # Check for circular references in objects/arrays
        if isinstance(value, (dict, list)):
            obj_id = id(value)

            if obj_id in seen:
                self.handle_circular_reference(value)

            seen.add(obj_id)

            try:
                if isinstance(value, dict):
                    # Process object
                    result = {}
                    for k, v in value.items():
                        # Skip undefined/symbol/function properties in objects
                        if isinstance(v, (Undefined, Symbol)) or v.__class__.__name__ in ('Undefined', 'Symbol'):
                            continue  # Don't include in result
                        if callable(v) and not isinstance(v, type):
                            continue  # Don't include functions
                        # Otherwise, prepare and include
                        prepared = self.prepare_for_json(v, seen)
                        result[k] = prepared
                    return result

                elif isinstance(value, list):
                    # Process array
                    result = []
                    for item in value:
                        # In arrays, undefined/symbol/function becomes null
                        is_special = (isinstance(item, (Undefined, Symbol)) or
                                     item.__class__.__name__ in ('Undefined', 'Symbol') or
                                     (callable(item) and not isinstance(item, type)))
                        if is_special:
                            result.append(None)
                        else:
                            prepared = self.prepare_for_json(item, seen)
                            result.append(prepared)
                    return result

            finally:
                seen.remove(obj_id)

        # Primitive values pass through
        return value

    def stringify_with_edge_cases(self, value: Any) -> str:
        """
        Stringify value with all edge case handling

        Args:
            value: Value to stringify

        Returns:
            JSON string

        Raises:
            TypeError: For circular references or BigInt
        """
        prepared = self.prepare_for_json(value)
        return json.dumps(prepared)
