"""
Symbol primitive type implementation.

Implements FR-P3-011 (Symbol primitive type) and FR-P3-016 (Symbol() constructor).
"""

from typing import Optional


# Global symbol ID counter
_symbol_id_counter = 0

# Global symbol registry (for Symbol.for/Symbol.keyFor)
_global_symbol_registry: dict[str, 'SymbolValue'] = {}
_global_symbol_reverse_registry: dict[int, str] = {}


class SymbolValue:
    """
    Symbol primitive value.

    Internal structure: { description: string | None, id: unique_int }

    Symbols are unique primitives used as property keys.
    Each symbol has a unique internal ID and an optional description.
    """

    __slots__ = ('_id', '_description')

    def __init__(self, description: Optional[str] = None):
        """
        Create a new symbol with optional description.

        Args:
            description: Optional string description for the symbol
        """
        global _symbol_id_counter

        self._id = _symbol_id_counter
        _symbol_id_counter += 1

        # Store description (None if not provided)
        if description is None:
            self._description = None
        else:
            # Convert to string
            self._description = str(description)

    @property
    def description(self) -> Optional[str]:
        """
        Get the symbol's description.

        Returns:
            The symbol's description string, or None if no description.
        """
        return self._description

    @description.setter
    def description(self, value):
        """Description is read-only."""
        raise AttributeError("Cannot set attribute 'description'")

    def __repr__(self):
        """Python representation."""
        if self._description:
            return f"Symbol({self._description})"
        return "Symbol()"

    def __str__(self):
        """String representation (for debugging)."""
        return self.to_string()

    def __eq__(self, other):
        """
        Symbol equality (reference equality only).

        Two symbols are equal only if they are the same object.
        """
        return self is other

    def __hash__(self):
        """Hash based on unique ID."""
        return hash(self._id)

    def to_string(self) -> str:
        """
        Convert symbol to string representation.

        Returns:
            "Symbol(description)" or "Symbol()" if no description.
        """
        if self._description:
            return f"Symbol({self._description})"
        return "Symbol()"

    def value_of(self) -> 'SymbolValue':
        """
        Return the symbol itself (primitive value).

        Returns:
            The symbol itself.
        """
        return self


def Symbol(description: Optional[str] = None) -> SymbolValue:
    """
    Create a new unique symbol.

    This is a function, not a constructor. Using 'new Symbol()' is a TypeError
    in JavaScript. In Python, we just provide this as a function.

    Args:
        description: Optional description for the symbol

    Returns:
        A new unique SymbolValue

    Examples:
        >>> sym = Symbol("mySymbol")
        >>> sym.description
        'mySymbol'
        >>> Symbol() == Symbol()
        False
    """
    # Convert description to string if provided (and not None)
    if description is not None and description != '':
        description_str = str(description)
    elif description == '':
        description_str = ''
    else:
        description_str = None

    return SymbolValue(description_str)


def symbol_for(key: str) -> SymbolValue:
    """
    Get or create a symbol from the global symbol registry.

    Symbol.for() creates/retrieves a symbol from the global registry.
    Unlike Symbol(), symbols created with Symbol.for() are reused based on key.

    Args:
        key: String key for the symbol in the registry

    Returns:
        The symbol associated with the key (created if doesn't exist)

    Examples:
        >>> sym1 = symbol_for("myKey")
        >>> sym2 = symbol_for("myKey")
        >>> sym1 is sym2
        True
    """
    # Convert key to string
    key_str = str(key)

    # Check if symbol already exists in registry
    if key_str in _global_symbol_registry:
        return _global_symbol_registry[key_str]

    # Create new symbol with key as description
    sym = SymbolValue(f"Symbol.for({key_str})")

    # Store in registry
    _global_symbol_registry[key_str] = sym
    _global_symbol_reverse_registry[sym._id] = key_str

    return sym


def symbol_key_for(symbol: SymbolValue) -> Optional[str]:
    """
    Get the key for a symbol in the global registry.

    Symbol.keyFor() returns the key for a registry symbol, or None if the
    symbol was not created with Symbol.for().

    Args:
        symbol: The symbol to look up

    Returns:
        The key string if symbol is in registry, None otherwise

    Raises:
        TypeError: If argument is not a symbol

    Examples:
        >>> sym = symbol_for("myKey")
        >>> symbol_key_for(sym)
        'myKey'
        >>> local_sym = Symbol("test")
        >>> symbol_key_for(local_sym)
        None
    """
    # Validate that argument is a symbol
    if not isinstance(symbol, SymbolValue):
        raise TypeError(f"Symbol.keyFor requires a symbol, got {type(symbol).__name__}")

    # Look up in reverse registry
    return _global_symbol_reverse_registry.get(symbol._id)
