"""
Well-known symbols implementation.

Implements FR-P3-013 (Well-known symbols), FR-P3-018 (Symbol.iterator),
FR-P3-019 (Symbol.toStringTag), FR-P3-020 (Symbol.hasInstance).

Well-known symbols are used to customize language behavior and define protocols.
"""

from symbol_value import SymbolValue


# Well-known symbols are created once and reused throughout the runtime
# These are the built-in symbols defined by ECMAScript

# Symbol.iterator - Default iterator for objects
# Used by for-of loops and spread operator
SYMBOL_ITERATOR = SymbolValue("Symbol.iterator")

# Symbol.toStringTag - Custom string tag for Object.prototype.toString
# Allows customizing the [object Type] string
SYMBOL_TO_STRING_TAG = SymbolValue("Symbol.toStringTag")

# Symbol.hasInstance - Custom instanceof behavior
# Method to customize instanceof operator
SYMBOL_HAS_INSTANCE = SymbolValue("Symbol.hasInstance")

# Symbol.toPrimitive - Custom type conversion
# Method for converting object to primitive value
SYMBOL_TO_PRIMITIVE = SymbolValue("Symbol.toPrimitive")

# Symbol.species - Constructor for derived objects
# Specifies function-valued property for creating derived objects
SYMBOL_SPECIES = SymbolValue("Symbol.species")

# Symbol.isConcatSpreadable - Array.prototype.concat behavior
# Controls whether object should be flattened to array elements
SYMBOL_IS_CONCAT_SPREADABLE = SymbolValue("Symbol.isConcatSpreadable")

# Symbol.unscopables - with statement exclusions
# Object with properties that are excluded from with environment bindings
SYMBOL_UNSCOPABLES = SymbolValue("Symbol.unscopables")

# Symbol.match - String.prototype.match behavior
# Method for String.prototype.match
SYMBOL_MATCH = SymbolValue("Symbol.match")

# Symbol.replace - String.prototype.replace behavior
# Method for String.prototype.replace
SYMBOL_REPLACE = SymbolValue("Symbol.replace")

# Symbol.search - String.prototype.search behavior
# Method for String.prototype.search
SYMBOL_SEARCH = SymbolValue("Symbol.search")

# Symbol.split - String.prototype.split behavior
# Method for String.prototype.split
SYMBOL_SPLIT = SymbolValue("Symbol.split")


# Export all well-known symbols
__all__ = [
    'SYMBOL_ITERATOR',
    'SYMBOL_TO_STRING_TAG',
    'SYMBOL_HAS_INSTANCE',
    'SYMBOL_TO_PRIMITIVE',
    'SYMBOL_SPECIES',
    'SYMBOL_IS_CONCAT_SPREADABLE',
    'SYMBOL_UNSCOPABLES',
    'SYMBOL_MATCH',
    'SYMBOL_REPLACE',
    'SYMBOL_SEARCH',
    'SYMBOL_SPLIT',
]
