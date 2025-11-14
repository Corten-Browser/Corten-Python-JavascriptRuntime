"""
Tests for Opcode enumeration.

These tests verify the opcode enum contains all required bytecode operations
for the JavaScript runtime engine.
"""

import pytest


def test_opcode_imports():
    """Test that Opcode enum can be imported."""
    from components.bytecode.src.opcode import Opcode

    assert Opcode is not None


def test_opcode_has_all_literal_opcodes():
    """Test that all literal loading opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Literal opcodes
    assert hasattr(Opcode, "LOAD_CONSTANT")
    assert hasattr(Opcode, "LOAD_UNDEFINED")
    assert hasattr(Opcode, "LOAD_NULL")
    assert hasattr(Opcode, "LOAD_TRUE")
    assert hasattr(Opcode, "LOAD_FALSE")


def test_opcode_has_all_variable_opcodes():
    """Test that all variable access opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Variable opcodes
    assert hasattr(Opcode, "LOAD_GLOBAL")
    assert hasattr(Opcode, "STORE_GLOBAL")
    assert hasattr(Opcode, "LOAD_LOCAL")
    assert hasattr(Opcode, "STORE_LOCAL")


def test_opcode_has_all_arithmetic_opcodes():
    """Test that all arithmetic operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Arithmetic opcodes
    assert hasattr(Opcode, "ADD")
    assert hasattr(Opcode, "SUBTRACT")
    assert hasattr(Opcode, "MULTIPLY")
    assert hasattr(Opcode, "DIVIDE")
    assert hasattr(Opcode, "MODULO")
    assert hasattr(Opcode, "NEGATE")


def test_opcode_has_all_comparison_opcodes():
    """Test that all comparison operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Comparison opcodes
    assert hasattr(Opcode, "EQUAL")
    assert hasattr(Opcode, "NOT_EQUAL")
    assert hasattr(Opcode, "LESS_THAN")
    assert hasattr(Opcode, "LESS_EQUAL")
    assert hasattr(Opcode, "GREATER_THAN")
    assert hasattr(Opcode, "GREATER_EQUAL")


def test_opcode_has_all_logical_opcodes():
    """Test that all logical operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Logical opcodes
    assert hasattr(Opcode, "LOGICAL_AND")
    assert hasattr(Opcode, "LOGICAL_OR")
    assert hasattr(Opcode, "LOGICAL_NOT")


def test_opcode_has_all_control_flow_opcodes():
    """Test that all control flow opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Control flow opcodes
    assert hasattr(Opcode, "JUMP")
    assert hasattr(Opcode, "JUMP_IF_TRUE")
    assert hasattr(Opcode, "JUMP_IF_FALSE")
    assert hasattr(Opcode, "RETURN")


def test_opcode_has_all_object_opcodes():
    """Test that all object operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Object opcodes
    assert hasattr(Opcode, "CREATE_OBJECT")
    assert hasattr(Opcode, "LOAD_PROPERTY")
    assert hasattr(Opcode, "STORE_PROPERTY")
    assert hasattr(Opcode, "DELETE_PROPERTY")


def test_opcode_has_all_array_opcodes():
    """Test that all array operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Array opcodes
    assert hasattr(Opcode, "CREATE_ARRAY")
    assert hasattr(Opcode, "LOAD_ELEMENT")
    assert hasattr(Opcode, "STORE_ELEMENT")


def test_opcode_has_all_function_opcodes():
    """Test that all function operation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Function opcodes
    assert hasattr(Opcode, "CREATE_CLOSURE")
    assert hasattr(Opcode, "CALL_FUNCTION")


def test_opcode_has_all_stack_opcodes():
    """Test that all stack manipulation opcodes are defined."""
    from components.bytecode.src.opcode import Opcode

    # Stack opcodes
    assert hasattr(Opcode, "POP")
    assert hasattr(Opcode, "DUP")


def test_opcode_enum_values_are_unique():
    """Test that all opcode enum values are unique."""
    from components.bytecode.src.opcode import Opcode

    # Get all opcode values
    values = [op.value for op in Opcode]

    # Check uniqueness
    assert len(values) == len(set(values)), "Opcode values must be unique"


def test_opcode_is_enum_type():
    """Test that Opcode is an Enum type."""
    from enum import Enum
    from components.bytecode.src.opcode import Opcode

    assert issubclass(Opcode, Enum)


def test_opcode_has_approximately_50_opcodes():
    """Test that we have approximately 50 opcodes as specified."""
    from components.bytecode.src.opcode import Opcode

    # Count should be around 50 (contract says ~50 opcodes)
    opcode_count = len(list(Opcode))
    assert 30 <= opcode_count <= 60, f"Expected ~50 opcodes, got {opcode_count}"
