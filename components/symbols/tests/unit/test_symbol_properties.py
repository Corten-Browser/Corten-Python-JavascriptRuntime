"""
Unit tests for symbols as property keys.

Tests FR-P3-012 (Symbol properties on objects).

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol
from symbol_properties import (
    SymbolPropertyStore,
    set_symbol_property,
    get_symbol_property,
    has_symbol_property,
    delete_symbol_property,
    get_own_property_symbols,
)


class TestSymbolAsPropertyKey:
    """Test using symbols as property keys."""

    def test_set_symbol_property(self):
        """Should be able to set property with symbol key."""
        obj = {}
        sym = Symbol("key")
        set_symbol_property(obj, sym, "value")
        assert get_symbol_property(obj, sym) == "value"

    def test_get_symbol_property(self):
        """Should be able to get property with symbol key."""
        obj = {}
        sym = Symbol("key")
        set_symbol_property(obj, sym, 123)
        result = get_symbol_property(obj, sym)
        assert result == 123

    def test_symbol_property_different_from_string(self):
        """Symbol property should be separate from string properties."""
        obj = {}
        sym = Symbol("prop")
        set_symbol_property(obj, sym, "symbol value")
        # Setting string property shouldn't affect symbol property
        obj["prop"] = "string value"
        assert get_symbol_property(obj, sym) == "symbol value"
        assert obj.get("prop") == "string value"

    def test_different_symbols_different_properties(self):
        """Different symbols should access different properties."""
        obj = {}
        sym1 = Symbol("key")
        sym2 = Symbol("key")
        set_symbol_property(obj, sym1, "value1")
        set_symbol_property(obj, sym2, "value2")
        assert get_symbol_property(obj, sym1) == "value1"
        assert get_symbol_property(obj, sym2) == "value2"

    def test_registry_symbol_as_property_key(self):
        """Registry symbols should work as property keys."""
        from symbol_value import symbol_for
        obj = {}
        sym = symbol_for("myKey")
        set_symbol_property(obj, sym, "test")
        assert get_symbol_property(obj, sym) == "test"


class TestSymbolPropertyEnumeration:
    """Test symbol property enumeration behavior."""

    def test_has_symbol_property(self):
        """has_symbol_property should detect symbol properties."""
        obj = {}
        sym = Symbol("key")
        assert has_symbol_property(obj, sym) is False
        set_symbol_property(obj, sym, "value")
        assert has_symbol_property(obj, sym) is True

    def test_delete_symbol_property(self):
        """Should be able to delete symbol properties."""
        obj = {}
        sym = Symbol("key")
        set_symbol_property(obj, sym, "value")
        assert has_symbol_property(obj, sym) is True
        result = delete_symbol_property(obj, sym)
        assert result is True
        assert has_symbol_property(obj, sym) is False

    def test_get_own_property_symbols(self):
        """Should be able to get all symbol properties."""
        obj = {}
        sym1 = Symbol("key1")
        sym2 = Symbol("key2")
        set_symbol_property(obj, sym1, "value1")
        set_symbol_property(obj, sym2, "value2")
        symbols = get_own_property_symbols(obj)
        assert len(symbols) == 2
        assert sym1 in symbols
        assert sym2 in symbols

    def test_symbol_properties_not_in_regular_keys(self):
        """Symbol properties should not appear in regular key enumeration."""
        obj = {"regular": "value"}
        sym = Symbol("key")
        set_symbol_property(obj, sym, "symbol value")
        # Regular keys should not include symbol
        assert "regular" in obj
        assert sym not in obj


class TestSymbolPropertyStore:
    """Test SymbolPropertyStore internal implementation."""

    def test_symbol_property_store_creation(self):
        """SymbolPropertyStore should be creatable."""
        store = SymbolPropertyStore()
        assert store is not None

    def test_symbol_property_store_set_get(self):
        """SymbolPropertyStore should store and retrieve values."""
        store = SymbolPropertyStore()
        sym = Symbol("key")
        store.set(sym, "value")
        assert store.get(sym) == "value"

    def test_symbol_property_store_has(self):
        """SymbolPropertyStore should detect presence of symbols."""
        store = SymbolPropertyStore()
        sym = Symbol("key")
        assert store.has(sym) is False
        store.set(sym, "value")
        assert store.has(sym) is True

    def test_symbol_property_store_delete(self):
        """SymbolPropertyStore should delete symbols."""
        store = SymbolPropertyStore()
        sym = Symbol("key")
        store.set(sym, "value")
        result = store.delete(sym)
        assert result is True
        assert store.has(sym) is False

    def test_symbol_property_store_get_symbols(self):
        """SymbolPropertyStore should return all stored symbols."""
        store = SymbolPropertyStore()
        sym1 = Symbol("key1")
        sym2 = Symbol("key2")
        store.set(sym1, "value1")
        store.set(sym2, "value2")
        symbols = store.get_symbols()
        assert len(symbols) == 2
        assert sym1 in symbols
        assert sym2 in symbols


class TestSymbolPropertyNonEnumerable:
    """Test that symbol properties are non-enumerable by default."""

    def test_symbol_property_not_in_keys(self):
        """Symbol properties should not appear in Object.keys()."""
        obj = {"regular": "value"}
        sym = Symbol("key")
        set_symbol_property(obj, sym, "symbol value")
        # Only regular keys should appear
        keys = list(obj.keys())
        assert "regular" in keys
        assert sym not in keys
        assert len(keys) == 1

    def test_symbol_property_excluded_from_for_in(self):
        """Symbol properties should be excluded from for-in loop."""
        # This is tested via get_own_property_symbols being separate
        obj = {}
        sym = Symbol("key")
        set_symbol_property(obj, sym, "value")
        # Regular iteration shouldn't include symbol
        regular_keys = [k for k in obj]
        assert sym not in regular_keys


class TestWellKnownSymbolsAsProperties:
    """Test using well-known symbols as property keys."""

    def test_symbol_iterator_as_property(self):
        """Should be able to use Symbol.iterator as property key."""
        from well_known_symbols import SYMBOL_ITERATOR
        obj = {}
        iterator_func = lambda: None
        set_symbol_property(obj, SYMBOL_ITERATOR, iterator_func)
        assert get_symbol_property(obj, SYMBOL_ITERATOR) is iterator_func

    def test_symbol_to_string_tag_as_property(self):
        """Should be able to use Symbol.toStringTag as property key."""
        from well_known_symbols import SYMBOL_TO_STRING_TAG
        obj = {}
        set_symbol_property(obj, SYMBOL_TO_STRING_TAG, "CustomClass")
        assert get_symbol_property(obj, SYMBOL_TO_STRING_TAG) == "CustomClass"
