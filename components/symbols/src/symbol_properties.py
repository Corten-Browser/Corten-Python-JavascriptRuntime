"""
Symbol properties implementation.

Implements FR-P3-012 (Symbol properties on objects).

Symbols can be used as property keys, stored separately from string keys.
Symbol properties are non-enumerable by default and excluded from normal enumeration.
"""

from typing import Any, List, Dict
from symbol_value import SymbolValue


class SymbolPropertyStore:
    """
    Storage for symbol properties on objects.

    Symbol properties are stored separately from string properties to maintain
    proper enumeration behavior (symbols excluded from for-in, Object.keys, etc.).
    """

    def __init__(self):
        """Initialize empty symbol property store."""
        # Map from symbol ID to value
        self._properties: Dict[int, tuple[SymbolValue, Any]] = {}

    def set(self, symbol: SymbolValue, value: Any) -> None:
        """
        Set a property with symbol key.

        Args:
            symbol: The symbol key
            value: The property value
        """
        if not isinstance(symbol, SymbolValue):
            raise TypeError(f"Property key must be symbol, got {type(symbol).__name__}")

        # Store with symbol ID as key, but keep symbol reference for retrieval
        self._properties[symbol._id] = (symbol, value)

    def get(self, symbol: SymbolValue, default=None) -> Any:
        """
        Get a property value by symbol key.

        Args:
            symbol: The symbol key
            default: Default value if property doesn't exist

        Returns:
            The property value, or default if not found
        """
        if not isinstance(symbol, SymbolValue):
            raise TypeError(f"Property key must be symbol, got {type(symbol).__name__}")

        if symbol._id in self._properties:
            _, value = self._properties[symbol._id]
            return value
        return default

    def has(self, symbol: SymbolValue) -> bool:
        """
        Check if symbol property exists.

        Args:
            symbol: The symbol key

        Returns:
            True if property exists, False otherwise
        """
        if not isinstance(symbol, SymbolValue):
            return False

        return symbol._id in self._properties

    def delete(self, symbol: SymbolValue) -> bool:
        """
        Delete a symbol property.

        Args:
            symbol: The symbol key

        Returns:
            True if property was deleted, False if it didn't exist
        """
        if not isinstance(symbol, SymbolValue):
            return False

        if symbol._id in self._properties:
            del self._properties[symbol._id]
            return True
        return False

    def get_symbols(self) -> List[SymbolValue]:
        """
        Get all symbol keys.

        Returns:
            List of all symbol keys in this store
        """
        return [sym for sym, _ in self._properties.values()]


# Global WeakMap-like storage for object symbol properties
# In real implementation, this would be a WeakMap to avoid memory leaks
# For now, we use object id as key
_object_symbol_properties: Dict[int, SymbolPropertyStore] = {}


def _get_symbol_store(obj: Any) -> SymbolPropertyStore:
    """
    Get or create symbol property store for an object.

    Args:
        obj: The object

    Returns:
        SymbolPropertyStore for this object
    """
    obj_id = id(obj)
    if obj_id not in _object_symbol_properties:
        _object_symbol_properties[obj_id] = SymbolPropertyStore()
    return _object_symbol_properties[obj_id]


def set_symbol_property(obj: Any, symbol: SymbolValue, value: Any) -> None:
    """
    Set a property on an object using a symbol key.

    Args:
        obj: The object to set property on
        symbol: The symbol key
        value: The property value

    Examples:
        >>> obj = {}
        >>> sym = Symbol("key")
        >>> set_symbol_property(obj, sym, "value")
        >>> get_symbol_property(obj, sym)
        'value'
    """
    store = _get_symbol_store(obj)
    store.set(symbol, value)


def get_symbol_property(obj: Any, symbol: SymbolValue, default=None) -> Any:
    """
    Get a property from an object using a symbol key.

    Args:
        obj: The object to get property from
        symbol: The symbol key
        default: Default value if property doesn't exist

    Returns:
        The property value, or default if not found

    Examples:
        >>> obj = {}
        >>> sym = Symbol("key")
        >>> set_symbol_property(obj, sym, "value")
        >>> get_symbol_property(obj, sym)
        'value'
    """
    obj_id = id(obj)
    if obj_id not in _object_symbol_properties:
        return default

    store = _object_symbol_properties[obj_id]
    return store.get(symbol, default)


def has_symbol_property(obj: Any, symbol: SymbolValue) -> bool:
    """
    Check if an object has a property with symbol key.

    Args:
        obj: The object to check
        symbol: The symbol key

    Returns:
        True if property exists, False otherwise

    Examples:
        >>> obj = {}
        >>> sym = Symbol("key")
        >>> has_symbol_property(obj, sym)
        False
        >>> set_symbol_property(obj, sym, "value")
        >>> has_symbol_property(obj, sym)
        True
    """
    obj_id = id(obj)
    if obj_id not in _object_symbol_properties:
        return False

    store = _object_symbol_properties[obj_id]
    return store.has(symbol)


def delete_symbol_property(obj: Any, symbol: SymbolValue) -> bool:
    """
    Delete a property from an object using a symbol key.

    Args:
        obj: The object to delete property from
        symbol: The symbol key

    Returns:
        True if property was deleted, False if it didn't exist

    Examples:
        >>> obj = {}
        >>> sym = Symbol("key")
        >>> set_symbol_property(obj, sym, "value")
        >>> delete_symbol_property(obj, sym)
        True
        >>> has_symbol_property(obj, sym)
        False
    """
    obj_id = id(obj)
    if obj_id not in _object_symbol_properties:
        return False

    store = _object_symbol_properties[obj_id]
    return store.delete(symbol)


def get_own_property_symbols(obj: Any) -> List[SymbolValue]:
    """
    Get all symbol property keys from an object.

    This is the equivalent of Object.getOwnPropertySymbols() in JavaScript.

    Args:
        obj: The object to get symbol properties from

    Returns:
        List of all symbol keys on the object

    Examples:
        >>> obj = {}
        >>> sym1 = Symbol("key1")
        >>> sym2 = Symbol("key2")
        >>> set_symbol_property(obj, sym1, "value1")
        >>> set_symbol_property(obj, sym2, "value2")
        >>> symbols = get_own_property_symbols(obj)
        >>> len(symbols)
        2
        >>> sym1 in symbols and sym2 in symbols
        True
    """
    obj_id = id(obj)
    if obj_id not in _object_symbol_properties:
        return []

    store = _object_symbol_properties[obj_id]
    return store.get_symbols()
