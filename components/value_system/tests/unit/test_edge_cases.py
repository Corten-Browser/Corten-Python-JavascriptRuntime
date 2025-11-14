"""
Additional edge case tests to improve coverage.

This module tests edge cases and error conditions that weren't
covered in the main test files.
"""

import pytest


class TestValueEdgeCasesExtended:
    """Extended edge case tests for Value class."""

    def test_object_registry_cleanup(self):
        """
        Given multiple object values
        When creating and extracting objects
        Then the registry maintains references correctly
        """
        from components.value_system.src.value import Value, _object_registry

        # Store initial registry size
        initial_size = len(_object_registry)

        # Create multiple objects
        obj1 = {"test": 1}
        obj2 = [1, 2, 3]
        obj3 = "test string"

        v1 = Value.from_object(obj1)
        v2 = Value.from_object(obj2)
        v3 = Value.from_object(obj3)

        # Registry should have 3 more objects
        assert len(_object_registry) == initial_size + 3

        # All objects should be retrievable
        assert v1.to_object() is obj1
        assert v2.to_object() is obj2
        assert v3.to_object() is obj3


class TestConversionEdgeCases:
    """Extended edge case tests for conversion functions."""

    def test_to_number_with_null_sentinel(self):
        """
        Given a NULL_VALUE
        When calling ToNumber
        Then it returns 0.0 per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import NULL_VALUE
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object(NULL_VALUE)

        assert ToNumber(value) == 0.0

    def test_to_string_with_null_sentinel(self):
        """
        Given a NULL_VALUE
        When calling ToString
        Then it returns "null"
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import NULL_VALUE
        from components.value_system.src.conversions import ToString

        value = Value.from_object(NULL_VALUE)

        assert ToString(value) == "null"

    def test_to_boolean_with_null_sentinel(self):
        """
        Given a NULL_VALUE
        When calling ToBoolean
        Then it returns False per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import NULL_VALUE
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object(NULL_VALUE)

        assert ToBoolean(value) is False

    def test_to_number_with_list(self):
        """
        Given a list object
        When calling ToNumber
        Then it raises TypeError
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object([1, 2, 3])

        with pytest.raises(TypeError):
            ToNumber(value)


class TestTypeCheckingEdgeCases:
    """Extended edge case tests for type checking functions."""

    def test_is_number_with_undefined(self):
        """
        Given undefined (None)
        When calling IsNumber
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber

        value = Value.from_object(None)

        assert IsNumber(value) is False

    def test_is_string_with_undefined(self):
        """
        Given undefined (None)
        When calling IsString
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsString

        value = Value.from_object(None)

        assert IsString(value) is False

    def test_is_object_with_null_sentinel(self):
        """
        Given NULL_VALUE
        When calling IsObject
        Then it returns False (null is not an object in our type system)
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject, NULL_VALUE

        value = Value.from_object(NULL_VALUE)

        assert IsObject(value) is False

    def test_null_sentinel_representation(self):
        """
        Given NULL_VALUE
        When converting to string
        Then it returns "null"
        """
        from components.value_system.src.type_check import NULL_VALUE

        assert repr(NULL_VALUE) == "null"
