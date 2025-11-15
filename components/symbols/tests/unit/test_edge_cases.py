"""
Additional edge case tests to achieve ≥90% coverage.

Tests edge cases and error conditions.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol, SymbolValue
from symbol_ops import symbol_typeof, symbol_to_string, symbol_to_number, symbol_to_boolean
from symbol_properties import (
    SymbolPropertyStore,
    set_symbol_property,
    get_symbol_property,
    has_symbol_property,
    delete_symbol_property,
)


class TestSymbolOpsEdgeCases:
    """Test edge cases in symbol operations."""

    def test_typeof_non_symbol_values(self):
        """Test typeof with various non-symbol values."""
        assert symbol_typeof(None) == "undefined"
        assert symbol_typeof(True) == "boolean"
        assert symbol_typeof(False) == "boolean"
        assert symbol_typeof(42) == "number"
        assert symbol_typeof(3.14) == "number"
        assert symbol_typeof("test") == "string"
        assert symbol_typeof({}) == "object"
        assert symbol_typeof([]) == "object"

    def test_to_string_non_symbol(self):
        """Test symbol_to_string with non-symbol should raise TypeError."""
        with pytest.raises(TypeError, match="Cannot convert"):
            symbol_to_string("not a symbol")

    def test_to_number_non_symbol(self):
        """Test symbol_to_number with non-symbol should raise TypeError."""
        with pytest.raises(TypeError, match="Cannot convert"):
            symbol_to_number("not a symbol")

    def test_to_boolean_non_symbol_values(self):
        """Test symbol_to_boolean with non-symbol values."""
        # Truthy values
        assert symbol_to_boolean(True) is True
        assert symbol_to_boolean(1) is True
        assert symbol_to_boolean("test") is True
        assert symbol_to_boolean([1]) is True

        # Falsy values
        assert symbol_to_boolean(False) is False
        assert symbol_to_boolean(0) is False
        assert symbol_to_boolean("") is False
        assert symbol_to_boolean(None) is False


class TestSymbolValueEdgeCases:
    """Test SymbolValue edge cases."""

    def test_symbol_hash_consistency(self):
        """Test that symbol hash is consistent."""
        sym = Symbol("test")
        hash1 = hash(sym)
        hash2 = hash(sym)
        assert hash1 == hash2

    def test_symbol_hash_unique(self):
        """Test that different symbols have different hashes."""
        sym1 = Symbol("test")
        sym2 = Symbol("test")
        # Different symbols should (likely) have different hashes
        # Note: hash collisions are possible but unlikely
        assert hash(sym1) != hash(sym2)

    def test_symbol_str_representation(self):
        """Test __str__ method."""
        sym = Symbol("test")
        assert str(sym) == "Symbol(test)"

    def test_symbol_repr_representation(self):
        """Test __repr__ method."""
        sym = Symbol("test")
        assert repr(sym) == "Symbol(test)"

        sym_no_desc = Symbol()
        assert repr(sym_no_desc) == "Symbol()"


class TestSymbolPropertyStoreEdgeCases:
    """Test SymbolPropertyStore edge cases."""

    def test_store_set_with_non_symbol(self):
        """Test that setting with non-symbol raises TypeError."""
        store = SymbolPropertyStore()
        with pytest.raises(TypeError, match="Property key must be symbol"):
            store.set("not a symbol", "value")

    def test_store_get_with_non_symbol(self):
        """Test that getting with non-symbol raises TypeError."""
        store = SymbolPropertyStore()
        with pytest.raises(TypeError, match="Property key must be symbol"):
            store.get("not a symbol")

    def test_store_has_with_non_symbol(self):
        """Test that has with non-symbol returns False."""
        store = SymbolPropertyStore()
        result = store.has("not a symbol")
        assert result is False

    def test_store_delete_with_non_symbol(self):
        """Test that delete with non-symbol returns False."""
        store = SymbolPropertyStore()
        result = store.delete("not a symbol")
        assert result is False

    def test_store_get_default_value(self):
        """Test getting non-existent property returns default."""
        store = SymbolPropertyStore()
        sym = Symbol("key")
        result = store.get(sym, "default")
        assert result == "default"

    def test_store_delete_non_existent(self):
        """Test deleting non-existent property returns False."""
        store = SymbolPropertyStore()
        sym = Symbol("key")
        result = store.delete(sym)
        assert result is False


class TestSymbolPropertyHelperEdgeCases:
    """Test symbol property helper function edge cases."""

    def test_get_symbol_property_from_empty_object(self):
        """Test getting symbol property from object without any."""
        obj = {}
        sym = Symbol("key")
        result = get_symbol_property(obj, sym, "default")
        assert result == "default"

    def test_has_symbol_property_on_empty_object(self):
        """Test has_symbol_property on object without symbol properties."""
        obj = {}
        sym = Symbol("key")
        result = has_symbol_property(obj, sym)
        assert result is False

    def test_delete_symbol_property_from_empty_object(self):
        """Test delete_symbol_property on object without symbol properties."""
        obj = {}
        sym = Symbol("key")
        result = delete_symbol_property(obj, sym)
        assert result is False


class TestSymbolDescriptionCoercion:
    """Test various description coercion scenarios."""

    def test_symbol_with_none_explicitly(self):
        """Test Symbol(None) creates symbol with None description."""
        sym = Symbol(None)
        assert sym.description is None

    def test_symbol_with_numeric_description(self):
        """Test Symbol with numeric description."""
        sym = Symbol(42)
        assert sym.description == "42"

    def test_symbol_with_float_description(self):
        """Test Symbol with float description."""
        sym = Symbol(3.14)
        assert sym.description == "3.14"

    def test_symbol_with_boolean_description(self):
        """Test Symbol with boolean description."""
        sym_true = Symbol(True)
        assert sym_true.description == "True"

        sym_false = Symbol(False)
        assert sym_false.description == "False"
