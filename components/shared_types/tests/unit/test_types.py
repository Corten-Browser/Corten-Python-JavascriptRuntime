"""
Unit tests for TypeTag and ErrorType enums.

Following TDD: These tests are written FIRST before implementation.
"""

import pytest
from enum import Enum


def test_type_tag_enum_exists():
    """Test that TypeTag enum can be imported."""
    from src.types import TypeTag

    assert issubclass(TypeTag, Enum)


def test_type_tag_has_smi():
    """Test that TypeTag has SMI value for small integers."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "SMI")


def test_type_tag_has_object():
    """Test that TypeTag has OBJECT value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "OBJECT")


def test_type_tag_has_string():
    """Test that TypeTag has STRING value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "STRING")


def test_type_tag_has_number():
    """Test that TypeTag has NUMBER value for heap-allocated numbers."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "NUMBER")


def test_type_tag_has_boolean():
    """Test that TypeTag has BOOLEAN value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "BOOLEAN")


def test_type_tag_has_undefined():
    """Test that TypeTag has UNDEFINED value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "UNDEFINED")


def test_type_tag_has_null():
    """Test that TypeTag has NULL value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "NULL")


def test_type_tag_has_function():
    """Test that TypeTag has FUNCTION value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "FUNCTION")


def test_type_tag_has_array():
    """Test that TypeTag has ARRAY value."""
    from src.types import TypeTag

    assert hasattr(TypeTag, "ARRAY")


def test_type_tag_has_exactly_nine_values():
    """Test that TypeTag has exactly 9 values as per specification."""
    from src.types import TypeTag

    assert len(TypeTag) == 9


def test_error_type_enum_exists():
    """Test that ErrorType enum can be imported."""
    from src.types import ErrorType

    assert issubclass(ErrorType, Enum)


def test_error_type_has_syntax_error():
    """Test that ErrorType has SYNTAX_ERROR value."""
    from src.types import ErrorType

    assert hasattr(ErrorType, "SYNTAX_ERROR")


def test_error_type_has_type_error():
    """Test that ErrorType has TYPE_ERROR value."""
    from src.types import ErrorType

    assert hasattr(ErrorType, "TYPE_ERROR")


def test_error_type_has_reference_error():
    """Test that ErrorType has REFERENCE_ERROR value."""
    from src.types import ErrorType

    assert hasattr(ErrorType, "REFERENCE_ERROR")


def test_error_type_has_range_error():
    """Test that ErrorType has RANGE_ERROR value."""
    from src.types import ErrorType

    assert hasattr(ErrorType, "RANGE_ERROR")


def test_error_type_has_error():
    """Test that ErrorType has ERROR value for generic errors."""
    from src.types import ErrorType

    assert hasattr(ErrorType, "ERROR")


def test_error_type_has_exactly_five_values():
    """Test that ErrorType has exactly 5 values as per specification."""
    from src.types import ErrorType

    assert len(ErrorType) == 5


def test_type_tag_enum_values_are_unique():
    """Test that all TypeTag enum values are unique."""
    from src.types import TypeTag

    values = [tag.value for tag in TypeTag]
    assert len(values) == len(set(values))


def test_error_type_enum_values_are_unique():
    """Test that all ErrorType enum values are unique."""
    from src.types import ErrorType

    values = [error.value for error in ErrorType]
    assert len(values) == len(set(values))
