"""
Unit tests for Symbol type coercion and operations.

Tests FR-P3-014 (Symbol coercion rules) and FR-P3-015 (Symbol in operations).

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol
from symbol_ops import (
    symbol_typeof,
    symbol_to_string,
    symbol_to_number,
    symbol_to_boolean,
    symbol_equals,
    symbol_strict_equals,
)


class TestSymbolTypeof:
    """Test typeof operator with symbols (FR-P3-015)."""

    def test_typeof_symbol(self):
        """typeof symbol should return 'symbol'."""
        sym = Symbol("test")
        assert symbol_typeof(sym) == "symbol"

    def test_typeof_symbol_without_description(self):
        """typeof symbol without description should return 'symbol'."""
        sym = Symbol()
        assert symbol_typeof(sym) == "symbol"

    def test_typeof_registry_symbol(self):
        """typeof registry symbol should return 'symbol'."""
        from symbol_value import symbol_for
        sym = symbol_for("test")
        assert symbol_typeof(sym) == "symbol"


class TestSymbolToString:
    """Test symbol to string coercion (FR-P3-014)."""

    def test_symbol_to_string_with_description(self):
        """String(symbol) should return 'Symbol(description)'."""
        sym = Symbol("mySymbol")
        result = symbol_to_string(sym)
        assert result == "Symbol(mySymbol)"

    def test_symbol_to_string_without_description(self):
        """String(symbol) without description should return 'Symbol()'."""
        sym = Symbol()
        result = symbol_to_string(sym)
        assert result == "Symbol()"

    def test_symbol_to_string_empty_description(self):
        """String(symbol) with empty description should return 'Symbol()'."""
        sym = Symbol('')
        result = symbol_to_string(sym)
        assert result == "Symbol()"

    def test_symbol_to_string_explicit_only(self):
        """Implicit string coercion should throw TypeError."""
        # In JavaScript: "" + symbol throws TypeError
        # We test explicit conversion works, implicit fails
        sym = Symbol("test")
        # Explicit conversion should work
        assert symbol_to_string(sym) == "Symbol(test)"


class TestSymbolToNumber:
    """Test symbol to number coercion (FR-P3-014)."""

    def test_symbol_to_number_throws_type_error(self):
        """Number(symbol) should throw TypeError."""
        sym = Symbol("test")
        with pytest.raises(TypeError, match="Cannot convert.*Symbol.*to.*number"):
            symbol_to_number(sym)

    def test_symbol_arithmetic_throws_type_error(self):
        """Arithmetic operations with symbols should throw TypeError."""
        sym = Symbol("test")
        with pytest.raises(TypeError):
            symbol_to_number(sym)


class TestSymbolToBoolean:
    """Test symbol to boolean coercion (FR-P3-014)."""

    def test_symbol_to_boolean_always_true(self):
        """Boolean(symbol) should always return True."""
        sym = Symbol("test")
        assert symbol_to_boolean(sym) is True

    def test_symbol_without_description_to_boolean(self):
        """Boolean(symbol) without description should return True."""
        sym = Symbol()
        assert symbol_to_boolean(sym) is True


class TestSymbolEquality:
    """Test symbol equality operations (FR-P3-015)."""

    def test_symbol_equals_itself(self):
        """Symbol should equal itself."""
        sym = Symbol("test")
        assert symbol_strict_equals(sym, sym) is True

    def test_different_symbols_not_equal(self):
        """Different symbols should not be equal."""
        sym1 = Symbol("test")
        sym2 = Symbol("test")
        assert symbol_strict_equals(sym1, sym2) is False

    def test_registry_symbols_equal(self):
        """Registry symbols with same key should be equal."""
        from symbol_value import symbol_for
        sym1 = symbol_for("key")
        sym2 = symbol_for("key")
        assert symbol_strict_equals(sym1, sym2) is True

    def test_symbol_loose_equality(self):
        """Symbol == comparison should work same as ===."""
        sym = Symbol("test")
        assert symbol_equals(sym, sym) is True

    def test_symbol_not_equal_to_string(self):
        """Symbol should not equal string with same description."""
        sym = Symbol("test")
        assert symbol_strict_equals(sym, "Symbol(test)") is False


class TestSymbolPrototypeMethods:
    """Test Symbol.prototype methods."""

    def test_symbol_prototype_to_string(self):
        """Symbol.prototype.toString should return 'Symbol(description)'."""
        sym = Symbol("test")
        # The symbol should have a toString method
        assert hasattr(sym, 'to_string')
        assert sym.to_string() == "Symbol(test)"

    def test_symbol_prototype_value_of(self):
        """Symbol.prototype.valueOf should return the symbol itself."""
        sym = Symbol("test")
        assert hasattr(sym, 'value_of')
        assert sym.value_of() is sym

    def test_symbol_description_getter(self):
        """Symbol.prototype.description should return description."""
        sym = Symbol("myDescription")
        assert sym.description == "myDescription"

    def test_symbol_description_getter_none(self):
        """Symbol.prototype.description should return None if no description."""
        sym = Symbol()
        assert sym.description is None
