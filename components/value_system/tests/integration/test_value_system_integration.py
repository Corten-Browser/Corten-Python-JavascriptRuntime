"""
Integration tests for value_system component.

This module tests the value_system component as a whole, verifying
that all pieces work together correctly in realistic scenarios.
"""

import math


class TestValueSystemIntegration:
    """Integration tests for complete value system workflows."""

    def test_complete_value_workflow_with_smi(self):
        """
        Given the value system
        When creating, checking, and converting SMI values
        Then all operations work together correctly
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber, IsString
        from components.value_system.src.conversions import ToNumber, ToString, ToBoolean

        # Create SMI value
        value = Value.from_smi(42)

        # Type checking
        assert IsNumber(value) is True
        assert IsString(value) is False

        # Conversions
        assert ToNumber(value) == 42.0
        assert ToString(value) == "42"
        assert ToBoolean(value) is True

    def test_complete_value_workflow_with_string(self):
        """
        Given the value system
        When creating, checking, and converting string values
        Then all operations work together correctly
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNumber, IsString
        from components.value_system.src.conversions import ToNumber, ToString, ToBoolean

        # Create string value
        value = Value.from_object("123")

        # Type checking
        assert IsString(value) is True
        assert IsNumber(value) is False

        # Conversions
        assert ToNumber(value) == 123.0
        assert ToString(value) == "123"
        assert ToBoolean(value) is True

    def test_complete_value_workflow_with_falsy_values(self):
        """
        Given the value system
        When working with falsy values (0, empty string, undefined)
        Then ToBoolean correctly identifies them
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToBoolean

        # Zero is falsy
        zero = Value.from_smi(0)
        assert ToBoolean(zero) is False

        # Empty string is falsy
        empty = Value.from_object("")
        assert ToBoolean(empty) is False

        # Undefined is falsy
        undefined = Value.from_object(None)
        assert ToBoolean(undefined) is False

    def test_complete_value_workflow_with_objects(self):
        """
        Given the value system
        When working with object values
        Then type checking and conversions work correctly
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsObject, IsString
        from components.value_system.src.conversions import ToBoolean, ToString

        # Dictionary object
        obj = {"key": "value", "count": 42}
        value = Value.from_object(obj)

        # Type checking
        assert IsObject(value) is True
        assert IsString(value) is False

        # Conversions
        assert ToBoolean(value) is True  # Objects are truthy
        result = ToString(value)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_null_and_undefined_distinction(self):
        """
        Given the value system
        When using null and undefined
        Then they are properly distinguished
        """
        from components.value_system.src.value import Value
        from components.value_system.src.type_check import IsNull, IsUndefined, NULL_VALUE
        from components.value_system.src.conversions import ToNumber, ToString

        # Undefined
        undefined = Value.from_object(None)
        assert IsUndefined(undefined) is True
        assert IsNull(undefined) is False
        assert math.isnan(ToNumber(undefined))
        assert ToString(undefined) == "undefined"

        # Null
        null_val = Value.from_object(NULL_VALUE)
        assert IsNull(null_val) is True
        assert IsUndefined(null_val) is False
        assert ToNumber(null_val) == 0.0
        assert ToString(null_val) == "null"

    def test_mixed_value_operations(self):
        """
        Given multiple values of different types
        When performing operations on them
        Then each value maintains its type correctly
        """
        from components.value_system.src.value import Value
        from components.value_system.src.conversions import ToNumber, ToString

        # Create various values
        num = Value.from_smi(100)
        text = Value.from_object("200")
        obj = Value.from_object({"value": 300})

        # Convert to numbers where possible
        assert ToNumber(num) == 100.0
        assert ToNumber(text) == 200.0

        # Convert to strings
        assert ToString(num) == "100"
        assert ToString(text) == "200"
        assert isinstance(ToString(obj), str)

    def test_tagged_pointer_encoding_integration(self):
        """
        Given the value system's tagged pointer implementation
        When encoding and decoding values
        Then the tagging is transparent to the user
        """
        from components.value_system.src.value import Value

        # SMI encoding should be transparent
        smi = Value.from_smi(999)
        assert smi.is_smi()
        assert smi.to_smi() == 999

        # Object encoding should be transparent
        obj = [1, 2, 3]
        obj_val = Value.from_object(obj)
        assert obj_val.is_object()
        assert obj_val.to_object() is obj

        # Both values should coexist
        assert smi.is_smi() and not smi.is_object()
        assert obj_val.is_object() and not obj_val.is_smi()
