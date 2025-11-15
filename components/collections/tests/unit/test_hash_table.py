"""
Unit tests for hash table implementation.

The hash table is used internally by Map and Set.
- Separate chaining for collision resolution
- Insertion order preservation
- SameValueZero equality for keys
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestHashTableBasics:
    """Test basic hash table operations."""

    def test_create_empty_hash_table(self):
        """Test creating an empty hash table."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        assert ht.size == 0

    def test_set_and_get_simple_value(self):
        """Test setting and getting a simple key-value pair."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")
        assert ht.get("key1") == "value1"
        assert ht.size == 1

    def test_set_multiple_values(self):
        """Test setting multiple key-value pairs."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")
        ht.set("key2", "value2")
        ht.set("key3", "value3")

        assert ht.get("key1") == "value1"
        assert ht.get("key2") == "value2"
        assert ht.get("key3") == "value3"
        assert ht.size == 3

    def test_update_existing_key(self):
        """Test updating an existing key's value."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")
        ht.set("key1", "value2")

        assert ht.get("key1") == "value2"
        assert ht.size == 1  # Size should not change

    def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        assert ht.get("nonexistent") is None

    def test_has_key(self):
        """Test checking if a key exists."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")

        assert ht.has("key1") is True
        assert ht.has("nonexistent") is False

    def test_delete_key(self):
        """Test deleting a key."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")
        ht.set("key2", "value2")

        assert ht.delete("key1") is True
        assert ht.has("key1") is False
        assert ht.get("key1") is None
        assert ht.size == 1

    def test_delete_nonexistent_key(self):
        """Test deleting a non-existent key returns False."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        assert ht.delete("nonexistent") is False

    def test_clear(self):
        """Test clearing all entries."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", "value1")
        ht.set("key2", "value2")
        ht.clear()

        assert ht.size == 0
        assert ht.has("key1") is False
        assert ht.has("key2") is False


class TestHashTableKeyTypes:
    """Test hash table with various key types."""

    def test_integer_keys(self):
        """Test using integers as keys."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set(1, "one")
        ht.set(2, "two")
        ht.set(3, "three")

        assert ht.get(1) == "one"
        assert ht.get(2) == "two"

    def test_float_keys(self):
        """Test using floats as keys."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set(1.5, "value1")
        ht.set(2.7, "value2")

        assert ht.get(1.5) == "value1"
        assert ht.get(2.7) == "value2"

    def test_object_keys(self):
        """Test using objects as keys (reference equality)."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        obj1 = {"a": 1}
        obj2 = {"a": 1}  # Same content, different reference

        ht.set(obj1, "value1")
        ht.set(obj2, "value2")

        assert ht.get(obj1) == "value1"
        assert ht.get(obj2) == "value2"
        assert ht.size == 2  # Different objects


class TestHashTableSameValueZero:
    """Test SameValueZero equality in hash table."""

    def test_nan_as_key(self):
        """Test that NaN equals NaN (SameValueZero rule)."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        nan1 = float('nan')
        nan2 = float('nan')

        ht.set(nan1, "value1")
        # Setting with another NaN should update the same entry
        ht.set(nan2, "value2")

        assert ht.size == 1
        assert ht.get(nan1) == "value2"
        assert ht.get(nan2) == "value2"

    def test_positive_and_negative_zero(self):
        """Test that +0 and -0 are equal (SameValueZero rule)."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set(0.0, "zero")
        ht.set(-0.0, "negative zero")

        # Should update the same entry
        assert ht.size == 1
        assert ht.get(0.0) == "negative zero"
        assert ht.get(-0.0) == "negative zero"


class TestHashTableInsertionOrder:
    """Test that insertion order is preserved."""

    def test_iteration_order(self):
        """Test that entries are returned in insertion order."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("a", 1)
        ht.set("b", 2)
        ht.set("c", 3)

        entries = list(ht.entries())
        assert entries == [("a", 1), ("b", 2), ("c", 3)]

    def test_keys_order(self):
        """Test that keys are returned in insertion order."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("first", 1)
        ht.set("second", 2)
        ht.set("third", 3)

        keys = list(ht.keys())
        assert keys == ["first", "second", "third"]

    def test_values_order(self):
        """Test that values are returned in insertion order."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("a", 100)
        ht.set("b", 200)
        ht.set("c", 300)

        values = list(ht.values())
        assert values == [100, 200, 300]

    def test_update_preserves_order(self):
        """Test that updating a key preserves its insertion order."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("a", 1)
        ht.set("b", 2)
        ht.set("c", 3)
        ht.set("b", 20)  # Update middle key

        entries = list(ht.entries())
        assert entries == [("a", 1), ("b", 20), ("c", 3)]

    def test_delete_and_add_changes_order(self):
        """Test that deleting and re-adding a key moves it to end."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("a", 1)
        ht.set("b", 2)
        ht.set("c", 3)
        ht.delete("b")
        ht.set("b", 20)  # Add back

        entries = list(ht.entries())
        assert entries == [("a", 1), ("c", 3), ("b", 20)]


class TestHashTableCollisions:
    """Test hash table collision handling."""

    def test_handles_many_entries(self):
        """Test that hash table handles many entries correctly."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        # Add many entries to force collisions
        for i in range(100):
            ht.set(f"key{i}", f"value{i}")

        assert ht.size == 100
        for i in range(100):
            assert ht.get(f"key{i}") == f"value{i}"

    def test_delete_with_collisions(self):
        """Test deleting entries when there are collisions."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        # Add many entries
        for i in range(50):
            ht.set(f"key{i}", f"value{i}")

        # Delete some
        for i in range(0, 50, 2):  # Delete even keys
            assert ht.delete(f"key{i}") is True

        assert ht.size == 25

        # Verify odd keys still exist
        for i in range(1, 50, 2):
            assert ht.get(f"key{i}") == f"value{i}"


class TestHashTableEdgeCases:
    """Test edge cases."""

    def test_none_as_key(self):
        """Test using None as a key."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set(None, "null value")
        assert ht.get(None) == "null value"

    def test_none_as_value(self):
        """Test storing None as a value."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("key1", None)
        assert ht.has("key1") is True
        assert ht.get("key1") is None

    def test_empty_string_as_key(self):
        """Test using empty string as a key."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set("", "empty key")
        assert ht.get("") == "empty key"

    def test_boolean_keys(self):
        """Test using booleans as keys."""
        from components.collections.src.hash_table import HashTable

        ht = HashTable()
        ht.set(True, "true value")
        ht.set(False, "false value")

        assert ht.get(True) == "true value"
        assert ht.get(False) == "false value"
        assert ht.size == 2
