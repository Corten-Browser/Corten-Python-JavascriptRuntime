"""
Unit tests for Value class - tagged pointer representation.

This module tests the Value class which provides tagged pointer
representation for JavaScript values with SMI optimization.
"""

import pytest


class TestValueCreation:
    """Test Value object creation and initialization."""

    def test_value_from_smi_creates_smi_value(self):
        """
        Given an integer value
        When creating a Value from SMI
        Then the value is tagged as SMI
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(42)

        assert value.is_smi() is True
        assert value.is_object() is False

    def test_value_from_smi_stores_integer_correctly(self):
        """
        Given an integer value
        When creating a Value from SMI
        Then the integer can be extracted
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(42)

        assert value.to_smi() == 42

    def test_value_from_smi_negative_integer(self):
        """
        Given a negative integer
        When creating a Value from SMI
        Then the negative integer is stored correctly
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(-100)

        assert value.is_smi() is True
        assert value.to_smi() == -100

    def test_value_from_smi_zero(self):
        """
        Given zero
        When creating a Value from SMI
        Then zero is stored correctly
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(0)

        assert value.is_smi() is True
        assert value.to_smi() == 0

    def test_value_from_object_creates_object_value(self):
        """
        Given a Python object
        When creating a Value from object
        Then the value is tagged as object
        """
        from components.value_system.src.value import Value

        obj = {"key": "value"}
        value = Value.from_object(obj)

        assert value.is_object() is True
        assert value.is_smi() is False

    def test_value_from_object_stores_reference(self):
        """
        Given a Python object
        When creating a Value from object
        Then the object reference can be extracted
        """
        from components.value_system.src.value import Value

        obj = {"key": "value"}
        value = Value.from_object(obj)

        assert value.to_object() is obj

    def test_value_init_with_raw_tagged_value(self):
        """
        Given a raw tagged integer
        When creating a Value directly
        Then the Value is created successfully
        """
        from components.value_system.src.value import Value

        # Raw SMI value: 42 << 2 | 0b00
        raw = 42 << 2
        value = Value(raw)

        assert value.is_smi() is True
        assert value.to_smi() == 42


class TestValueTypeChecking:
    """Test Value type checking methods."""

    def test_is_smi_returns_true_for_smi(self):
        """
        Given an SMI value
        When checking is_smi
        Then it returns True
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(100)

        assert value.is_smi() is True

    def test_is_smi_returns_false_for_object(self):
        """
        Given an object value
        When checking is_smi
        Then it returns False
        """
        from components.value_system.src.value import Value

        value = Value.from_object("test")

        assert value.is_smi() is False

    def test_is_object_returns_true_for_object(self):
        """
        Given an object value
        When checking is_object
        Then it returns True
        """
        from components.value_system.src.value import Value

        value = Value.from_object([1, 2, 3])

        assert value.is_object() is True

    def test_is_object_returns_false_for_smi(self):
        """
        Given an SMI value
        When checking is_object
        Then it returns False
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(200)

        assert value.is_object() is False


class TestValueExtraction:
    """Test extracting values from Value objects."""

    def test_to_smi_extracts_integer(self):
        """
        Given an SMI value
        When calling to_smi
        Then the integer is extracted correctly
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(999)

        assert value.to_smi() == 999

    def test_to_smi_on_object_raises_type_error(self):
        """
        Given an object value
        When calling to_smi
        Then a TypeError is raised
        """
        from components.value_system.src.value import Value

        value = Value.from_object("not an integer")

        with pytest.raises(TypeError, match="not.*SMI"):
            value.to_smi()

    def test_to_object_extracts_reference(self):
        """
        Given an object value
        When calling to_object
        Then the object reference is extracted
        """
        from components.value_system.src.value import Value

        obj = [1, 2, 3]
        value = Value.from_object(obj)

        assert value.to_object() is obj

    def test_to_object_on_smi_raises_type_error(self):
        """
        Given an SMI value
        When calling to_object
        Then a TypeError is raised
        """
        from components.value_system.src.value import Value

        value = Value.from_smi(42)

        with pytest.raises(TypeError, match="not.*object"):
            value.to_object()


class TestValueEdgeCases:
    """Test edge cases for Value class."""

    def test_large_positive_smi(self):
        """
        Given a large positive integer
        When creating SMI value
        Then it's stored correctly
        """
        from components.value_system.src.value import Value

        large_num = 2**29 - 1  # Max 30-bit signed value
        value = Value.from_smi(large_num)

        assert value.to_smi() == large_num

    def test_large_negative_smi(self):
        """
        Given a large negative integer
        When creating SMI value
        Then it's stored correctly
        """
        from components.value_system.src.value import Value

        large_neg = -(2**29)  # Min 30-bit signed value
        value = Value.from_smi(large_neg)

        assert value.to_smi() == large_neg

    def test_none_as_object(self):
        """
        Given None
        When creating object value
        Then it's stored correctly
        """
        from components.value_system.src.value import Value

        value = Value.from_object(None)

        assert value.is_object() is True
        assert value.to_object() is None

    def test_string_as_object(self):
        """
        Given a string
        When creating object value
        Then it's stored correctly
        """
        from components.value_system.src.value import Value

        s = "Hello, World!"
        value = Value.from_object(s)

        assert value.to_object() == s
