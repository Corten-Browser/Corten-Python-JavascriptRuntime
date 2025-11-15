"""
Symbol operations and type coercion.

Implements FR-P3-014 (Symbol coercion rules) and FR-P3-015 (Symbol in operations).
"""

from typing import Any
from symbol_value import SymbolValue


def symbol_typeof(value: Any) -> str:
    """
    Return the typeof string for a symbol.

    Args:
        value: The value to check

    Returns:
        "symbol" if value is a symbol, otherwise type-specific string

    Examples:
        >>> sym = Symbol("test")
        >>> symbol_typeof(sym)
        'symbol'
    """
    if isinstance(value, SymbolValue):
        return "symbol"
    # For non-symbols, return appropriate type
    if value is None:
        return "undefined"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "string"
    return "object"


def symbol_to_string(symbol: SymbolValue) -> str:
    """
    Convert symbol to string (explicit conversion only).

    In JavaScript:
    - String(symbol) works and returns "Symbol(description)"
    - Implicit conversion (symbol + "") throws TypeError

    Args:
        symbol: The symbol to convert

    Returns:
        String representation "Symbol(description)" or "Symbol()"

    Examples:
        >>> sym = Symbol("mySymbol")
        >>> symbol_to_string(sym)
        'Symbol(mySymbol)'
        >>> Symbol()
        >>> symbol_to_string(sym)
        'Symbol()'
    """
    if not isinstance(symbol, SymbolValue):
        raise TypeError(f"Cannot convert {type(symbol).__name__} to symbol string")

    # Use the symbol's to_string method
    return symbol.to_string()


def symbol_to_number(symbol: SymbolValue) -> float:
    """
    Attempt to convert symbol to number (always throws TypeError).

    Per ECMAScript spec, symbols cannot be converted to numbers.

    Args:
        symbol: The symbol to convert

    Raises:
        TypeError: Always raised - symbols cannot be converted to numbers

    Examples:
        >>> sym = Symbol("test")
        >>> symbol_to_number(sym)
        TypeError: Cannot convert Symbol to number
    """
    if isinstance(symbol, SymbolValue):
        raise TypeError("Cannot convert Symbol to number")
    raise TypeError(f"Cannot convert {type(symbol).__name__} to number")


def symbol_to_boolean(symbol: SymbolValue) -> bool:
    """
    Convert symbol to boolean (always True).

    All symbols are truthy in boolean context.

    Args:
        symbol: The symbol to convert

    Returns:
        True (always)

    Examples:
        >>> sym = Symbol("test")
        >>> symbol_to_boolean(sym)
        True
    """
    if isinstance(symbol, SymbolValue):
        return True
    # For non-symbols, use standard truthiness
    return bool(symbol)


def symbol_equals(left: Any, right: Any) -> bool:
    """
    Check loose equality (==) for symbols.

    For symbols, == behaves the same as ===.

    Args:
        left: Left operand
        right: Right operand

    Returns:
        True if both are the same symbol, False otherwise

    Examples:
        >>> sym = Symbol("test")
        >>> symbol_equals(sym, sym)
        True
        >>> symbol_equals(Symbol("test"), Symbol("test"))
        False
    """
    return symbol_strict_equals(left, right)


def symbol_strict_equals(left: Any, right: Any) -> bool:
    """
    Check strict equality (===) for symbols.

    Symbols use reference equality - two symbols are equal only if they
    are the exact same symbol (same reference).

    Args:
        left: Left operand
        right: Right operand

    Returns:
        True if both are the same symbol reference, False otherwise

    Examples:
        >>> sym = Symbol("test")
        >>> symbol_strict_equals(sym, sym)
        True
        >>> symbol_strict_equals(Symbol("test"), Symbol("test"))
        False
        >>> from symbol_value import symbol_for
        >>> symbol_strict_equals(symbol_for("key"), symbol_for("key"))
        True
    """
    # Both must be symbols
    if not isinstance(left, SymbolValue) or not isinstance(right, SymbolValue):
        return False

    # Reference equality
    return left is right
