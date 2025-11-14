"""
Unit tests for ECMAScript type conversion functions.

This module tests ToNumber, ToString, and ToBoolean conversion
functions per ECMAScript specification.
"""

import pytest
import math


class TestToNumber:
    """Test ToNumber conversion function (ECMAScript ToNumber)."""

    def test_to_number_converts_smi_to_float(self):
        """
        Given an SMI value
        When calling ToNumber
        Then it returns the number as float
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_smi(42)

        assert ToNumber(value) == 42.0
        assert isinstance(ToNumber(value), float)

    def test_to_number_converts_zero_smi(self):
        """
        Given an SMI value of zero
        When calling ToNumber
        Then it returns 0.0
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_smi(0)

        assert ToNumber(value) == 0.0

    def test_to_number_converts_negative_smi(self):
        """
        Given a negative SMI value
        When calling ToNumber
        Then it returns the negative number
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_smi(-100)

        assert ToNumber(value) == -100.0

    def test_to_number_converts_numeric_string(self):
        """
        Given a string containing a number
        When calling ToNumber
        Then it parses and returns the number
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object("123.45")

        assert ToNumber(value) == 123.45

    def test_to_number_converts_empty_string_to_zero(self):
        """
        Given an empty string
        When calling ToNumber
        Then it returns 0.0 per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object("")

        assert ToNumber(value) == 0.0

    def test_to_number_converts_whitespace_string_to_zero(self):
        """
        Given a whitespace-only string
        When calling ToNumber
        Then it returns 0.0 per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object("   ")

        assert ToNumber(value) == 0.0

    def test_to_number_invalid_string_raises_type_error(self):
        """
        Given a non-numeric string
        When calling ToNumber
        Then it raises TypeError
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object("not a number")

        with pytest.raises(TypeError):
            ToNumber(value)

    def test_to_number_on_undefined_returns_nan(self):
        """
        Given undefined (None)
        When calling ToNumber
        Then it returns NaN per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber

        value = Value.from_object(None)

        result = ToNumber(value)
        assert math.isnan(result)


class TestToString:
    """Test ToString conversion function (ECMAScript ToString)."""

    def test_to_string_converts_smi_to_string(self):
        """
        Given an SMI value
        When calling ToString
        Then it returns the string representation
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_smi(42)

        assert ToString(value) == "42"

    def test_to_string_converts_zero_smi(self):
        """
        Given an SMI value of zero
        When calling ToString
        Then it returns "0"
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_smi(0)

        assert ToString(value) == "0"

    def test_to_string_converts_negative_smi(self):
        """
        Given a negative SMI value
        When calling ToString
        Then it returns the negative number as string
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_smi(-100)

        assert ToString(value) == "-100"

    def test_to_string_returns_string_unchanged(self):
        """
        Given a string value
        When calling ToString
        Then it returns the string unchanged
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_object("Hello, World!")

        assert ToString(value) == "Hello, World!"

    def test_to_string_converts_empty_string(self):
        """
        Given an empty string
        When calling ToString
        Then it returns empty string
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_object("")

        assert ToString(value) == ""

    def test_to_string_on_undefined_returns_undefined(self):
        """
        Given undefined (None)
        When calling ToString
        Then it returns "undefined" per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_object(None)

        assert ToString(value) == "undefined"

    def test_to_string_on_object_returns_string_representation(self):
        """
        Given an object
        When calling ToString
        Then it returns a string representation
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToString

        value = Value.from_object({"key": "value"})

        result = ToString(value)
        assert isinstance(result, str)
        assert len(result) > 0


class TestToBoolean:
    """Test ToBoolean conversion function (ECMAScript ToBoolean)."""

    def test_to_boolean_zero_is_false(self):
        """
        Given an SMI value of zero
        When calling ToBoolean
        Then it returns False per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_smi(0)

        assert ToBoolean(value) is False

    def test_to_boolean_non_zero_smi_is_true(self):
        """
        Given a non-zero SMI value
        When calling ToBoolean
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_smi(42)

        assert ToBoolean(value) is True

    def test_to_boolean_negative_smi_is_true(self):
        """
        Given a negative SMI value
        When calling ToBoolean
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_smi(-1)

        assert ToBoolean(value) is True

    def test_to_boolean_empty_string_is_false(self):
        """
        Given an empty string
        When calling ToBoolean
        Then it returns False per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object("")

        assert ToBoolean(value) is False

    def test_to_boolean_non_empty_string_is_true(self):
        """
        Given a non-empty string
        When calling ToBoolean
        Then it returns True
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object("hello")

        assert ToBoolean(value) is True

    def test_to_boolean_whitespace_string_is_true(self):
        """
        Given a whitespace-only string
        When calling ToBoolean
        Then it returns True (non-empty string)
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object("   ")

        assert ToBoolean(value) is True

    def test_to_boolean_undefined_is_false(self):
        """
        Given undefined (None)
        When calling ToBoolean
        Then it returns False per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object(None)

        assert ToBoolean(value) is False

    def test_to_boolean_object_is_true(self):
        """
        Given an object
        When calling ToBoolean
        Then it returns True per ECMAScript spec
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object({"key": "value"})

        assert ToBoolean(value) is True

    def test_to_boolean_empty_list_is_true(self):
        """
        Given an empty list (object)
        When calling ToBoolean
        Then it returns True (objects are truthy)
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        value = Value.from_object([])

        assert ToBoolean(value) is True
