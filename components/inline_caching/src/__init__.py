"""
Inline Caching - Fast property and call site optimization.

This module provides inline caching infrastructure for optimizing
property access, function calls, and global variable access in JavaScript.

Public API:
    Classes:
        - InlineCache: Base inline cache class
        - PropertyLoadIC: Inline cache for property loads (obj.prop)
        - PropertyStoreIC: Inline cache for property stores (obj.prop = value)
        - CallIC: Inline cache for function calls
        - GlobalIC: Inline cache for global variable access

    Enums:
        - ICState: Inline cache state machine states

Example:
    >>> from components.inline_caching.src import PropertyLoadIC, ICState
    >>> ic = PropertyLoadIC()
    >>> value = ic.load(obj, "propertyName")
    >>> ic.get_state()
    ICState.MONOMORPHIC
"""

# Export public classes
from .ic_state import ICState
from .inline_cache import InlineCache
from .property_ic import PropertyLoadIC, PropertyStoreIC
from .call_ic import CallIC
from .global_ic import GlobalIC

__all__ = [
    # Enums
    "ICState",
    # Classes
    "InlineCache",
    "PropertyLoadIC",
    "PropertyStoreIC",
    "CallIC",
    "GlobalIC",
]

__version__ = "0.1.0"
