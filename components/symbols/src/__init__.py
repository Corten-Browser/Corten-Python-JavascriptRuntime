"""
Symbol component - ECMAScript Symbol primitive type.

This component implements the Symbol primitive type and all well-known symbols
per ECMAScript 2024 specification.
"""

from .symbol_value import Symbol, SymbolValue, symbol_for, symbol_key_for
from .well_known_symbols import (
    SYMBOL_ITERATOR,
    SYMBOL_TO_STRING_TAG,
    SYMBOL_HAS_INSTANCE,
    SYMBOL_TO_PRIMITIVE,
    SYMBOL_SPECIES,
    SYMBOL_IS_CONCAT_SPREADABLE,
    SYMBOL_UNSCOPABLES,
    SYMBOL_MATCH,
    SYMBOL_REPLACE,
    SYMBOL_SEARCH,
    SYMBOL_SPLIT,
)
from .symbol_ops import (
    symbol_typeof,
    symbol_to_string,
    symbol_to_number,
    symbol_to_boolean,
    symbol_equals,
    symbol_strict_equals,
)
from .symbol_properties import (
    SymbolPropertyStore,
    set_symbol_property,
    get_symbol_property,
    has_symbol_property,
    delete_symbol_property,
    get_own_property_symbols,
)

__all__ = [
    # Symbol creation
    'Symbol',
    'SymbolValue',
    'symbol_for',
    'symbol_key_for',
    # Well-known symbols
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
    # Operations
    'symbol_typeof',
    'symbol_to_string',
    'symbol_to_number',
    'symbol_to_boolean',
    'symbol_equals',
    'symbol_strict_equals',
    # Properties
    'SymbolPropertyStore',
    'set_symbol_property',
    'get_symbol_property',
    'has_symbol_property',
    'delete_symbol_property',
    'get_own_property_symbols',
]

__version__ = '0.3.0'
