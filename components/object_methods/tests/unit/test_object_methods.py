"""
Unit tests for ObjectMethods - ES2024 Object static methods.

Tests cover all 8 requirements:
- FR-ES24-036: Object.fromEntries()
- FR-ES24-037: Object.entries()
- FR-ES24-038: Object.values()
- FR-ES24-039: Object.getOwnPropertyDescriptors()
- FR-ES24-040: Object.setPrototypeOf() edge cases
- FR-ES24-041: Object.is()
- FR-ES24-042: Object.assign() edge cases
- FR-ES24-043: Object[Symbol.iterator]
"""

import pytest
from components.object_methods.src.object_methods import ObjectMethods


class TestObjectFromEntries:
    """
    Test Object.fromEntries() - FR-ES24-036

    Given an iterable of [key, value] pairs
    When Object.fromEntries() is called
    Then a new object is created with those entries
    """

    def test_creates_object_from_array_of_pairs(self):
        """Test basic object creation from [key, value] pairs."""
        # Given
        entries = [["a", 1], ["b", 2], ["c", 3]]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result == {"a": 1, "b": 2, "c": 3}

    def test_creates_object_from_empty_array(self):
        """Test that empty array creates empty object."""
        # Given
        entries = []

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result == {}

    def test_handles_duplicate_keys(self):
        """Test that later entries overwrite earlier ones."""
        # Given
        entries = [["a", 1], ["a", 2], ["a", 3]]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result == {"a": 3}

    def test_handles_non_string_keys(self):
        """Test that non-string keys are converted to strings."""
        # Given
        entries = [[1, "one"], [2, "two"], [True, "yes"]]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result == {"1": "one", "2": "two", "True": "yes"}

    def test_handles_various_value_types(self):
        """Test that various value types are preserved."""
        # Given
        entries = [
            ["string", "hello"],
            ["number", 42],
            ["bool", True],
            ["none", None],
            ["list", [1, 2, 3]],
            ["dict", {"nested": "value"}]
        ]

        # When
        result = ObjectMethods.from_entries(entries)

        # Then
        assert result["string"] == "hello"
        assert result["number"] == 42
        assert result["bool"] is True
        assert result["none"] is None
        assert result["list"] == [1, 2, 3]
        assert result["dict"] == {"nested": "value"}

    def test_rejects_invalid_entries(self):
        """Test that non-iterable entries raise TypeError."""
        # Given
        entries = ["not", "pairs"]

        # When/Then
        with pytest.raises(TypeError):
            ObjectMethods.from_entries(entries)


class TestObjectEntries:
    """
    Test Object.entries() - FR-ES24-037

    Given an object
    When Object.entries() is called
    Then enumerable own properties are returned as [key, value] pairs
    """

    def test_returns_key_value_pairs(self):
        """Test basic key-value pair extraction."""
        # Given
        obj = {"a": 1, "b": 2, "c": 3}

        # When
        result = ObjectMethods.entries(obj)

        # Then
        assert sorted(result) == [["a", 1], ["b", 2], ["c", 3]]

    def test_returns_empty_array_for_empty_object(self):
        """Test that empty object returns empty array."""
        # Given
        obj = {}

        # When
        result = ObjectMethods.entries(obj)

        # Then
        assert result == []

    def test_preserves_insertion_order(self):
        """Test that entries maintain insertion order."""
        # Given
        obj = {"z": 26, "a": 1, "m": 13}

        # When
        result = ObjectMethods.entries(obj)

        # Then
        # Python 3.7+ dicts maintain insertion order
        assert result == [["z", 26], ["a", 1], ["m", 13]]

    def test_handles_various_value_types(self):
        """Test entries with different value types."""
        # Given
        obj = {
            "string": "hello",
            "number": 42,
            "bool": True,
            "none": None,
            "list": [1, 2, 3]
        }

        # When
        result = ObjectMethods.entries(obj)

        # Then
        assert ["string", "hello"] in result
        assert ["number", 42] in result
        assert ["bool", True] in result
        assert ["none", None] in result
        assert ["list", [1, 2, 3]] in result


class TestObjectValues:
    """
    Test Object.values() - FR-ES24-038

    Given an object
    When Object.values() is called
    Then enumerable own property values are returned as array
    """

    def test_returns_values_array(self):
        """Test basic value extraction."""
        # Given
        obj = {"a": 1, "b": 2, "c": 3}

        # When
        result = ObjectMethods.values(obj)

        # Then
        assert sorted(result) == [1, 2, 3]

    def test_returns_empty_array_for_empty_object(self):
        """Test that empty object returns empty array."""
        # Given
        obj = {}

        # When
        result = ObjectMethods.values(obj)

        # Then
        assert result == []

    def test_preserves_insertion_order(self):
        """Test that values maintain insertion order."""
        # Given
        obj = {"z": 26, "a": 1, "m": 13}

        # When
        result = ObjectMethods.values(obj)

        # Then
        assert result == [26, 1, 13]

    def test_handles_various_value_types(self):
        """Test values with different types."""
        # Given
        obj = {
            "string": "hello",
            "number": 42,
            "bool": True,
            "none": None,
            "list": [1, 2, 3]
        }

        # When
        result = ObjectMethods.values(obj)

        # Then
        assert "hello" in result
        assert 42 in result
        assert True in result
        assert None in result
        assert [1, 2, 3] in result


class TestObjectGetOwnPropertyDescriptors:
    """
    Test Object.getOwnPropertyDescriptors() - FR-ES24-039

    Given an object
    When Object.getOwnPropertyDescriptors() is called
    Then all own property descriptors are returned
    """

    def test_returns_descriptors_for_all_properties(self):
        """Test that all property descriptors are returned."""
        # Given
        obj = {"a": 1, "b": 2}

        # When
        result = ObjectMethods.get_own_property_descriptors(obj)

        # Then
        assert "a" in result
        assert "b" in result
        assert result["a"]["value"] == 1
        assert result["b"]["value"] == 2

    def test_descriptors_have_correct_attributes(self):
        """Test that descriptors have enumerable, writable, configurable."""
        # Given
        obj = {"x": 10}

        # When
        result = ObjectMethods.get_own_property_descriptors(obj)

        # Then
        desc = result["x"]
        assert desc["value"] == 10
        assert desc["writable"] is True
        assert desc["enumerable"] is True
        assert desc["configurable"] is True

    def test_returns_empty_for_empty_object(self):
        """Test that empty object returns empty descriptors."""
        # Given
        obj = {}

        # When
        result = ObjectMethods.get_own_property_descriptors(obj)

        # Then
        assert result == {}


class TestObjectSetPrototypeOf:
    """
    Test Object.setPrototypeOf() - FR-ES24-040

    Given an object and a prototype
    When Object.setPrototypeOf() is called
    Then the object's prototype is set
    """

    def test_sets_prototype_successfully(self):
        """Test basic prototype setting."""
        # Given
        obj = {"x": 1}
        proto = {"y": 2}

        # When
        result = ObjectMethods.set_prototype_of(obj, proto)

        # Then
        assert result is obj
        # Prototype should be set (in real JS, accessible via __proto__)

    def test_accepts_null_prototype(self):
        """Test that null prototype is allowed."""
        # Given
        obj = {"x": 1}

        # When
        result = ObjectMethods.set_prototype_of(obj, None)

        # Then
        assert result is obj

    def test_rejects_non_object_target(self):
        """Test that non-object targets raise TypeError."""
        # Given
        proto = {"x": 1}

        # When/Then
        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of(42, proto)

        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of("string", proto)

        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of(True, proto)

    def test_rejects_invalid_prototype(self):
        """Test that invalid prototypes raise TypeError."""
        # Given
        obj = {"x": 1}

        # When/Then
        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of(obj, 42)

        with pytest.raises(TypeError):
            ObjectMethods.set_prototype_of(obj, "string")


class TestObjectIs:
    """
    Test Object.is() - FR-ES24-041

    Given two values
    When Object.is() is called
    Then SameValue equality is determined
    """

    def test_same_value_for_identical_primitives(self):
        """Test that identical primitives are same value."""
        # Given/When/Then
        assert ObjectMethods.is_equal(42, 42) is True
        assert ObjectMethods.is_equal("hello", "hello") is True
        assert ObjectMethods.is_equal(True, True) is True
        assert ObjectMethods.is_equal(None, None) is True

    def test_different_values_are_not_equal(self):
        """Test that different values are not same value."""
        # Given/When/Then
        assert ObjectMethods.is_equal(1, 2) is False
        assert ObjectMethods.is_equal("a", "b") is False
        assert ObjectMethods.is_equal(True, False) is False

    def test_positive_zero_and_negative_zero(self):
        """Test that +0 and -0 are NOT same value (unlike ===)."""
        # Given/When/Then
        assert ObjectMethods.is_equal(+0.0, -0.0) is False
        assert ObjectMethods.is_equal(-0.0, +0.0) is False

    def test_nan_equals_nan(self):
        """Test that NaN equals NaN (unlike ===)."""
        # Given/When/Then
        assert ObjectMethods.is_equal(float('nan'), float('nan')) is True

    def test_different_types_are_not_equal(self):
        """Test that different types are not same value."""
        # Given/When/Then
        assert ObjectMethods.is_equal(1, "1") is False
        assert ObjectMethods.is_equal(True, 1) is False
        assert ObjectMethods.is_equal(None, 0) is False

    def test_object_identity(self):
        """Test that objects are compared by identity."""
        # Given
        obj1 = {"a": 1}
        obj2 = {"a": 1}

        # When/Then
        assert ObjectMethods.is_equal(obj1, obj1) is True
        assert ObjectMethods.is_equal(obj1, obj2) is False


class TestObjectAssign:
    """
    Test Object.assign() - FR-ES24-042

    Given a target and source objects
    When Object.assign() is called
    Then enumerable own properties are copied to target
    """

    def test_copies_properties_to_target(self):
        """Test basic property copying."""
        # Given
        target = {"a": 1}
        source = {"b": 2, "c": 3}

        # When
        result = ObjectMethods.assign(target, [source])

        # Then
        assert result is target
        assert target == {"a": 1, "b": 2, "c": 3}

    def test_handles_multiple_sources(self):
        """Test copying from multiple sources."""
        # Given
        target = {"a": 1}
        source1 = {"b": 2}
        source2 = {"c": 3}
        source3 = {"d": 4}

        # When
        result = ObjectMethods.assign(target, [source1, source2, source3])

        # Then
        assert target == {"a": 1, "b": 2, "c": 3, "d": 4}

    def test_overwrites_existing_properties(self):
        """Test that source properties overwrite target properties."""
        # Given
        target = {"a": 1, "b": 2}
        source = {"b": 20, "c": 30}

        # When
        ObjectMethods.assign(target, [source])

        # Then
        assert target == {"a": 1, "b": 20, "c": 30}

    def test_later_sources_overwrite_earlier(self):
        """Test that later sources take precedence."""
        # Given
        target = {}
        source1 = {"a": 1}
        source2 = {"a": 2}
        source3 = {"a": 3}

        # When
        ObjectMethods.assign(target, [source1, source2, source3])

        # Then
        assert target["a"] == 3

    def test_handles_empty_sources(self):
        """Test that empty sources don't affect target."""
        # Given
        target = {"a": 1}

        # When
        ObjectMethods.assign(target, [{}])

        # Then
        assert target == {"a": 1}

    def test_skips_none_sources(self):
        """Test that None/null sources are skipped."""
        # Given
        target = {"a": 1}
        source = {"b": 2}

        # When
        ObjectMethods.assign(target, [None, source, None])

        # Then
        assert target == {"a": 1, "b": 2}

    def test_rejects_non_object_target(self):
        """Test that non-object targets raise TypeError."""
        # Given
        source = {"a": 1}

        # When/Then
        with pytest.raises(TypeError):
            ObjectMethods.assign(42, [source])

        with pytest.raises(TypeError):
            ObjectMethods.assign("string", [source])


class TestObjectIterator:
    """
    Test Object[Symbol.iterator] - FR-ES24-043

    Given an object
    When getting its iterator
    Then it yields [key, value] pairs
    """

    def test_object_is_iterable(self):
        """Test that objects can produce iterators."""
        # Given
        from components.object_methods.src.object_iteration import ObjectIteration
        obj = {"a": 1, "b": 2, "c": 3}

        # When
        iterator = ObjectIteration.get_iterator(obj)

        # Then
        assert iterator is not None

    def test_iterator_yields_entries(self):
        """Test that iterator yields [key, value] pairs."""
        # Given
        from components.object_methods.src.object_iteration import ObjectIteration
        obj = {"x": 10, "y": 20}

        # When
        iterator = ObjectIteration.get_iterator(obj)
        entries = list(iterator)

        # Then
        assert ["x", 10] in entries
        assert ["y", 20] in entries

    def test_iterator_follows_protocol(self):
        """Test that iterator follows Iterator protocol."""
        # Given
        from components.object_methods.src.object_iteration import ObjectIteration
        obj = {"a": 1}

        # When
        iterator = ObjectIteration.get_iterator(obj)

        # Then
        assert hasattr(iterator, 'next')
        result = iterator.next()
        assert hasattr(result, 'value')
        assert hasattr(result, 'done')
