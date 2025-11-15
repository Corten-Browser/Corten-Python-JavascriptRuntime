"""
Unit tests for Symbol global registry.

Tests FR-P3-017 (Symbol.for/Symbol.keyFor global registry).

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol, symbol_for, symbol_key_for


class TestSymbolFor:
    """Test Symbol.for() global registry."""

    def test_symbol_for_creates_symbol(self):
        """Symbol.for(key) should create a symbol."""
        sym = symbol_for("test")
        assert sym is not None

    def test_symbol_for_returns_same_symbol(self):
        """Symbol.for(key) should return same symbol for same key."""
        sym1 = symbol_for("myKey")
        sym2 = symbol_for("myKey")
        assert sym1 is sym2
        assert sym1 == sym2

    def test_symbol_for_different_keys(self):
        """Symbol.for with different keys should return different symbols."""
        sym1 = symbol_for("key1")
        sym2 = symbol_for("key2")
        assert sym1 is not sym2
        assert sym1 != sym2

    def test_symbol_for_with_empty_string(self):
        """Symbol.for('') should work with empty string."""
        sym = symbol_for('')
        assert sym is not None

    def test_symbol_for_key_conversion(self):
        """Symbol.for should convert key to string."""
        sym1 = symbol_for("123")
        sym2 = symbol_for(123)
        # Should be same symbol because 123 converts to "123"
        assert sym1 is sym2


class TestSymbolKeyFor:
    """Test Symbol.keyFor() reverse lookup."""

    def test_symbol_key_for_returns_key(self):
        """Symbol.keyFor should return the key for registry symbols."""
        sym = symbol_for("myKey")
        key = symbol_key_for(sym)
        assert key == "myKey"

    def test_symbol_key_for_non_registry_symbol(self):
        """Symbol.keyFor should return None for non-registry symbols."""
        sym = Symbol("test")
        key = symbol_key_for(sym)
        assert key is None

    def test_symbol_key_for_undefined_for_local_symbols(self):
        """Symbol.keyFor should return None for locally created symbols."""
        sym = Symbol()
        result = symbol_key_for(sym)
        assert result is None

    def test_symbol_key_for_multiple_symbols(self):
        """Symbol.keyFor should work with multiple registry symbols."""
        sym1 = symbol_for("key1")
        sym2 = symbol_for("key2")
        assert symbol_key_for(sym1) == "key1"
        assert symbol_key_for(sym2) == "key2"

    def test_symbol_key_for_with_non_symbol(self):
        """Symbol.keyFor should raise TypeError for non-symbols."""
        with pytest.raises(TypeError):
            symbol_key_for("not a symbol")


class TestSymbolRegistry:
    """Test global symbol registry behavior."""

    def test_registry_persistence(self):
        """Registry should persist symbols across calls."""
        sym1 = symbol_for("persistent")
        # Simulate some other operations
        Symbol("other")
        sym2 = symbol_for("persistent")
        assert sym1 is sym2

    def test_registry_separate_from_local_symbols(self):
        """Registry symbols should be separate from Symbol() symbols."""
        local_sym = Symbol("test")
        registry_sym = symbol_for("test")
        assert local_sym is not registry_sym
        assert local_sym != registry_sym
