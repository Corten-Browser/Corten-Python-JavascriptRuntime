"""
JSObject - JavaScript object representation with property storage.

This module provides the JSObject class which represents a JavaScript
object with properties and prototype chain support.
"""

from typing import Optional, Dict, List
from components.memory_gc.src import HeapObject, GarbageCollector
from components.value_system.src import Value


# Sentinel value for undefined (matches LOAD_UNDEFINED opcode)
UNDEFINED_VALUE = Value.from_smi(0)  # Temporary representation


class JSObject(HeapObject):
    """
    JavaScript object with property storage and prototype chain.

    JSObject represents a JavaScript object with a dictionary-based
    property storage and support for prototype-based inheritance.

    Attributes:
        _gc (GarbageCollector): Garbage collector managing this object
        _properties (Dict[str, Value]): Property storage (name -> value)
        _prototype (Optional[JSObject]): Prototype object for inheritance

    Example:
        >>> gc = GarbageCollector()
        >>> obj = JSObject(gc)
        >>> obj.set_property("name", Value.from_smi(42))
        >>> obj.get_property("name").to_smi()
        42
    """

    def __init__(self, gc: GarbageCollector, prototype: Optional["JSObject"] = None):
        """
        Initialize JSObject.

        Args:
            gc: Garbage collector managing this object
            prototype: Prototype object for inheritance chain (optional)
        """
        # Estimate size: base object + properties dict + prototype ref
        # Simple estimate: 100 bytes base + 50 per property
        size = 100
        super().__init__(size=size)

        self._gc = gc
        self._properties: Dict[str, Value] = {}
        self._prototype: Optional[JSObject] = prototype

        # Register with GC manually (add to heap and update used bytes)
        gc.heap.add(self)
        gc.used_bytes += size

    def get_property(self, key: str) -> Value:
        """
        Get property value, searching prototype chain if needed.

        Searches for property in this object first, then walks up the
        prototype chain until found or chain ends.

        Args:
            key: Property name to retrieve

        Returns:
            Value stored at property, or undefined if not found

        Example:
            >>> obj.set_property("x", Value.from_smi(10))
            >>> obj.get_property("x").to_smi()
            10
        """
        # Check own properties first
        if key in self._properties:
            return self._properties[key]

        # Search prototype chain
        if self._prototype is not None:
            return self._prototype.get_property(key)

        # Property not found - return undefined
        return UNDEFINED_VALUE

    def set_property(self, key: str, value: Value) -> None:
        """
        Set property value on this object.

        Sets the property directly on this object (does not affect prototype).

        Args:
            key: Property name to set
            value: Value to store at property

        Example:
            >>> obj.set_property("name", Value.from_smi(42))
            >>> obj.get_property("name").to_smi()
            42
        """
        self._properties[key] = value

        # Update size estimate
        self.size = 100 + len(self._properties) * 50

    def has_property(self, key: str) -> bool:
        """
        Check if property exists (searches prototype chain).

        Args:
            key: Property name to check

        Returns:
            True if property exists in object or prototype chain, False otherwise

        Example:
            >>> obj.set_property("x", Value.from_smi(1))
            >>> obj.has_property("x")
            True
            >>> obj.has_property("y")
            False
        """
        # Check own properties
        if key in self._properties:
            return True

        # Check prototype chain
        if self._prototype is not None:
            return self._prototype.has_property(key)

        return False

    def delete_property(self, key: str) -> bool:
        """
        Delete property from this object.

        Only deletes own properties, not inherited ones.

        Args:
            key: Property name to delete

        Returns:
            True if property existed and was deleted, False otherwise

        Example:
            >>> obj.set_property("x", Value.from_smi(1))
            >>> obj.delete_property("x")
            True
            >>> obj.has_property("x")
            False
        """
        if key in self._properties:
            del self._properties[key]
            # Update size estimate
            self.size = 100 + len(self._properties) * 50
            return True

        return False

    def get_prototype(self) -> Optional["JSObject"]:
        """
        Get prototype object.

        Returns:
            Prototype object, or None if no prototype

        Example:
            >>> proto = JSObject(gc)
            >>> obj = JSObject(gc, prototype=proto)
            >>> obj.get_prototype() is proto
            True
        """
        return self._prototype

    def set_prototype(self, prototype: "JSObject") -> None:
        """
        Set prototype object.

        Args:
            prototype: New prototype object

        Example:
            >>> obj = JSObject(gc)
            >>> proto = JSObject(gc)
            >>> obj.set_prototype(proto)
            >>> obj.get_prototype() is proto
            True
        """
        self._prototype = prototype

    def get_references(self) -> List[HeapObject]:
        """
        Get list of heap objects referenced by this object.

        Used by garbage collector during mark phase to find reachable objects.

        Returns:
            List containing prototype (if exists) and any object-typed properties

        Example:
            >>> proto = JSObject(gc)
            >>> obj = JSObject(gc, prototype=proto)
            >>> proto in obj.get_references()
            True
        """
        refs: List[HeapObject] = []

        # Add prototype if exists
        if self._prototype is not None:
            refs.append(self._prototype)

        # Add object-typed property values
        for value in self._properties.values():
            if value.is_object():
                obj = value.to_object()
                if isinstance(obj, HeapObject):
                    refs.append(obj)

        return refs
