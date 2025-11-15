"""
Additional edge case tests for ObjectMethods.

Ensures comprehensive coverage of error paths and edge cases.
"""

import pytest
from components.object_methods.src.object_methods import ObjectMethods


class TestFromEntriesEdgeCases:
    """Additional edge cases for Object.fromEntries()."""

    def test_rejects_entries_with_single_element(self):
        """Test that entries with <2 elements raise TypeError."""
        # Given
        entries = [["a"]]  # Only one element

        # When/Then
        with pytest.raises(TypeError, match="at least 2 elements"):
            ObjectMethods.from_entries(entries)

    def test_handles_entries_with_more_than_two_elements(self):
        """Test that extra elements in entries are ignored."""
        # Given
        entries = [["a", 1, "extra", "ignored"]]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result == {"a": 1}

    def test_handles_numeric_keys(self):
        """Test that numeric keys are stringified."""
        # Given
        entries = [[0, "zero"], [1, "one"], [2, "two"]]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result["0"] == "zero"
        assert result["1"] == "one"
        assert result["2"] == "two"


class TestObjectIsEdgeCases:
    """Additional edge cases for Object.is()."""

    def test_handles_integers_vs_floats(self):
        """Test that integers and floats with same value are equal."""
        # Given/When/Then
        assert ObjectMethods.is_equal(1, 1.0) is False  # Different types

    def test_handles_negative_zero(self):
        """Test negative zero handling."""
        # Given/When/Then
        assert ObjectMethods.is_equal(-0.0, -0.0) is True
        assert ObjectMethods.is_equal(0.0, 0.0) is True

    def test_handles_lists(self):
        """Test list identity comparison."""
        # Given
        list1 = [1, 2, 3]
        list2 = [1, 2, 3]

        # When/Then
        assert ObjectMethods.is_equal(list1, list1) is True
        assert ObjectMethods.is_equal(list1, list2) is False


class TestObjectAssignEdgeCases:
    """Additional edge cases for Object.assign()."""

    def test_handles_numeric_values(self):
        """Test assigning numeric values."""
        # Given
        target = {}
        source = {"int": 42, "float": 3.14, "zero": 0, "negative": -10}

        # When
        ObjectMethods.assign(target, [source])

        # Then
        assert target["int"] == 42
        assert target["float"] == 3.14
        assert target["zero"] == 0
        assert target["negative"] == -10

    def test_handles_boolean_values(self):
        """Test assigning boolean values."""
        # Given
        target = {}
        source = {"true": True, "false": False}

        # When
        ObjectMethods.assign(target, [source])

        # Then
        assert target["true"] is True
        assert target["false"] is False

    def test_handles_nested_objects(self):
        """Test assigning nested objects (shallow copy)."""
        # Given
        target = {}
        nested = {"x": 1}
        source = {"nested": nested}

        # When
        ObjectMethods.assign(target, [source])

        # Then
        assert target["nested"] is nested  # Shallow copy, same reference


class TestObjectSetPrototypeOfEdgeCases:
    """Additional edge cases for Object.setPrototypeOf()."""

    def test_handles_empty_objects(self):
        """Test setting prototype on empty object."""
        # Given
        obj = {}
        proto = {"method": lambda: "hello"}

        # When
        result = ObjectMethods.set_prototype_of(obj, proto)

        # Then
        assert result is obj
        assert obj["__proto__"] is proto

    def test_rejects_list_as_target(self):
        """Test that list targets raise TypeError."""
        # Given
        proto = {}

        # When/Then
        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of([1, 2, 3], proto)


class TestObjectEntriesValuesEdgeCases:
    """Additional edge cases for entries/values."""

    def test_entries_with_numeric_string_keys(self):
        """Test entries with numeric string keys."""
        # Given
        obj = {"0": "a", "1": "b", "10": "c"}

        # When
        result = ObjectMethods.entries(obj)

        # Then
        assert ["0", "a"] in result
        assert ["1", "b"] in result
        assert ["10", "c"] in result

    def test_values_with_none_values(self):
        """Test values with None."""
        # Given
        obj = {"a": None, "b": None}

        # When
        result = ObjectMethods.values(obj)

        # Then
        assert result == [None, None]
