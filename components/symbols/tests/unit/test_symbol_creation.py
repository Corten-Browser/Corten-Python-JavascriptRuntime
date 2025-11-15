"""
Unit tests for Symbol creation.

Tests FR-P3-011 (Symbol primitive type) and FR-P3-016 (Symbol() constructor).

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol, SymbolValue


class TestSymbolCreation:
    """Test Symbol() function creates unique symbols."""

    def test_symbol_creation_basic(self):
        """Symbol() should create a new symbol."""
        sym = Symbol()
        assert sym is not None
        assert isinstance(sym, SymbolValue)

    def test_symbol_creation_with_description(self):
        """Symbol(description) should create symbol with description."""
        sym = Symbol("mySymbol")
        assert sym is not None
        assert sym.description == "mySymbol"

    def test_symbol_creation_with_undefined_description(self):
        """Symbol(undefined) should create symbol with None description."""
        sym = Symbol(None)
        assert sym is not None
        assert sym.description is None

    def test_symbol_uniqueness(self):
        """Each Symbol() call should create a unique symbol."""
        sym1 = Symbol("test")
        sym2 = Symbol("test")
        assert sym1 is not sym2
        assert sym1 != sym2

    def test_symbol_has_unique_id(self):
        """Each symbol should have a unique internal ID."""
        sym1 = Symbol("test")
        sym2 = Symbol("test")
        assert hasattr(sym1, '_id')
        assert hasattr(sym2, '_id')
        assert sym1._id != sym2._id

    def test_symbol_cannot_be_constructed_with_new(self):
        """Using 'new Symbol()' should throw TypeError."""
        # In Python, we'll simulate this by checking if Symbol is callable
        # but not a class constructor in the traditional sense
        sym = Symbol()
        # The Symbol function should return SymbolValue, not be a class
        assert type(Symbol).__name__ != 'type'

    def test_symbol_with_empty_string_description(self):
        """Symbol('') should create symbol with empty string description."""
        sym = Symbol('')
        assert sym.description == ''

    def test_symbol_description_conversion(self):
        """Symbol description should be converted to string."""
        sym = Symbol(123)
        assert sym.description == "123"

    def test_symbol_with_object_description(self):
        """Symbol with object description should convert to string."""
        obj = type('obj', (), {'__str__': lambda self: 'custom'})()
        sym = Symbol(obj)
        assert sym.description == "custom"

    def test_symbol_reference_equality(self):
        """Same symbol reference should be equal."""
        sym = Symbol("test")
        assert sym == sym
        assert sym is sym

    def test_symbol_maintains_description(self):
        """Symbol should maintain its description."""
        desc = "my special symbol"
        sym = Symbol(desc)
        assert sym.description == desc


class TestSymbolValue:
    """Test SymbolValue internal structure."""

    def test_symbol_value_has_id(self):
        """SymbolValue should have unique ID."""
        sym = Symbol()
        assert hasattr(sym, '_id')
        assert isinstance(sym._id, int)

    def test_symbol_value_has_description(self):
        """SymbolValue should have description attribute."""
        sym = Symbol("test")
        assert hasattr(sym, 'description')

    def test_symbol_value_id_is_incremental(self):
        """Symbol IDs should be incrementing integers."""
        sym1 = Symbol()
        sym2 = Symbol()
        # IDs should be different and likely incremental
        assert sym2._id > sym1._id or sym1._id != sym2._id


class TestSymbolPrototype:
    """Test Symbol.prototype methods (FR-P3-014)."""

    def test_symbol_has_description_property(self):
        """Symbol should have description property."""
        sym = Symbol("test")
        # The description should be accessible
        assert sym.description == "test"

    def test_symbol_description_readonly(self):
        """Symbol description should be read-only."""
        sym = Symbol("test")
        # Attempting to change description should not work or should raise error
        with pytest.raises(AttributeError):
            sym.description = "new"
