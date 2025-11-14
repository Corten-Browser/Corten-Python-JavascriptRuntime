"""
Unit tests for type checking functions.

This module tests the JavaScript value type checking functions
that determine the type of a Value object.
"""

import pytest


class TestIsNumber:
    """Test IsNumber type checking function."""

    def test_is_number_returns_true_for_smi(self):
        """
        Given an SMI value
        When calling IsNumber
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber

        value = Value.from_smi(42)

        assert IsNumber(value) is True

    def test_is_number_returns_false_for_string(self):
        """
        Given a string value
        When calling IsNumber
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber

        value = Value.from_object("123")

        assert IsNumber(value) is False

    def test_is_number_returns_false_for_object(self):
        """
        Given an object value
        When calling IsNumber
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber

        value = Value.from_object({"key": "value"})

        assert IsNumber(value) is False


class TestIsString:
    """Test IsString type checking function."""

    def test_is_string_returns_true_for_string(self):
        """
        Given a string object value
        When calling IsString
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsString

        value = Value.from_object("Hello")

        assert IsString(value) is True

    def test_is_string_returns_false_for_smi(self):
        """
        Given an SMI value
        When calling IsString
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsString

        value = Value.from_smi(123)

        assert IsString(value) is False

    def test_is_string_returns_false_for_non_string_object(self):
        """
        Given a non-string object
        When calling IsString
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsString

        value = Value.from_object([1, 2, 3])

        assert IsString(value) is False

    def test_is_string_returns_true_for_empty_string(self):
        """
        Given an empty string
        When calling IsString
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsString

        value = Value.from_object("")

        assert IsString(value) is True


class TestIsObject:
    """Test IsObject type checking function."""

    def test_is_object_returns_true_for_dict(self):
        """
        Given a dictionary object
        When calling IsObject
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject

        value = Value.from_object({"key": "value"})

        assert IsObject(value) is True

    def test_is_object_returns_true_for_list(self):
        """
        Given a list object
        When calling IsObject
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject

        value = Value.from_object([1, 2, 3])

        assert IsObject(value) is True

    def test_is_object_returns_false_for_smi(self):
        """
        Given an SMI value
        When calling IsObject
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject

        value = Value.from_smi(42)

        assert IsObject(value) is False

    def test_is_object_returns_false_for_string(self):
        """
        Given a string value
        When calling IsObject
        Then it returns False (strings are primitive in JS)
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject

        value = Value.from_object("test")

        # In JavaScript, strings are primitives, not objects
        assert IsObject(value) is False


class TestIsUndefined:
    """Test IsUndefined type checking function."""

    def test_is_undefined_returns_true_for_none(self):
        """
        Given a None object (representing undefined)
        When calling IsUndefined
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsUndefined

        value = Value.from_object(None)

        assert IsUndefined(value) is True

    def test_is_undefined_returns_false_for_smi(self):
        """
        Given an SMI value
        When calling IsUndefined
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsUndefined

        value = Value.from_smi(0)

        assert IsUndefined(value) is False

    def test_is_undefined_returns_false_for_string(self):
        """
        Given a string value
        When calling IsUndefined
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsUndefined

        value = Value.from_object("undefined")

        assert IsUndefined(value) is False


class TestIsNull:
    """Test IsNull type checking function."""

    def test_is_null_returns_true_for_null_sentinel(self):
        """
        Given a null sentinel value
        When calling IsNull
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNull, NULL_VALUE

        value = Value.from_object(NULL_VALUE)

        assert IsNull(value) is True

    def test_is_null_returns_false_for_none(self):
        """
        Given None (undefined, not null)
        When calling IsNull
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNull

        value = Value.from_object(None)

        assert IsNull(value) is False

    def test_is_null_returns_false_for_smi(self):
        """
        Given an SMI value
        When calling IsNull
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNull

        value = Value.from_smi(0)

        assert IsNull(value) is False

    def test_is_null_returns_false_for_string(self):
        """
        Given a string value
        When calling IsNull
        Then it returns False
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNull

        value = Value.from_object("null")

        assert IsNull(value) is False
