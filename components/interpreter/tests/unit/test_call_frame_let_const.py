"""
Unit tests for CallFrame let/const variable kind support.

Tests the variable kind tracking and const enforcement in CallFrame.
"""

import pytest
from components.value_system.src import Value
from components.memory_gc.src import GarbageCollector
from components.bytecode.src import BytecodeArray
from components.interpreter.src.call_frame import CallFrame


def test_call_frame_set_variable_kind_valid():
    """
    Given a call frame with locals
    When setting variable kind to valid values
    Then variable kind should be set correctly
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 3
    frame = CallFrame(bytecode, 3, Value.from_smi(0))

    # When
    frame.set_variable_kind(0, "var")
    frame.set_variable_kind(1, "let")
    frame.set_variable_kind(2, "const")

    # Then
    assert frame.variable_kinds[0] == "var"
    assert frame.variable_kinds[1] == "let"
    assert frame.variable_kinds[2] == "const"


def test_call_frame_set_variable_kind_invalid():
    """
    Given a call frame with locals
    When setting variable kind to invalid value
    Then should raise ValueError
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 1
    frame = CallFrame(bytecode, 1, Value.from_smi(0))

    # When/Then
    with pytest.raises(ValueError) as exc_info:
        frame.set_variable_kind(0, "invalid")

    assert "Invalid variable kind" in str(exc_info.value)


def test_call_frame_set_variable_kind_out_of_bounds():
    """
    Given a call frame with locals
    When setting variable kind for out-of-bounds index
    Then should raise IndexError
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 2
    frame = CallFrame(bytecode, 2, Value.from_smi(0))

    # When/Then
    with pytest.raises(IndexError) as exc_info:
        frame.set_variable_kind(5, "var")

    assert "out of bounds" in str(exc_info.value)


def test_call_frame_is_const():
    """
    Given a call frame with const variable
    When checking if variable is const
    Then should return True for const, False for others
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 3
    frame = CallFrame(bytecode, 3, Value.from_smi(0))
    frame.set_variable_kind(0, "var")
    frame.set_variable_kind(1, "let")
    frame.set_variable_kind(2, "const")

    # When/Then
    assert frame.is_const(0) is False
    assert frame.is_const(1) is False
    assert frame.is_const(2) is True


def test_call_frame_is_initialized():
    """
    Given a call frame with variables
    When checking initialization status
    Then should return correct status
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 2
    frame = CallFrame(bytecode, 2, Value.from_smi(0))

    # When/Then
    assert frame.is_initialized(0) is False
    assert frame.is_initialized(1) is False

    frame.mark_initialized(0)

    assert frame.is_initialized(0) is True
    assert frame.is_initialized(1) is False


def test_call_frame_mark_initialized():
    """
    Given a call frame with uninitialized variable
    When marking it as initialized
    Then should be marked correctly
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 1
    frame = CallFrame(bytecode, 1, Value.from_smi(0))

    # When
    frame.mark_initialized(0)

    # Then
    assert frame.is_initialized(0) is True


def test_call_frame_defaults_to_var():
    """
    Given a newly created call frame
    When checking variable kinds
    Then all should default to 'var'
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 3
    frame = CallFrame(bytecode, 3, Value.from_smi(0))

    # When/Then
    assert frame.variable_kinds[0] == "var"
    assert frame.variable_kinds[1] == "var"
    assert frame.variable_kinds[2] == "var"


def test_call_frame_defaults_to_uninitialized():
    """
    Given a newly created call frame
    When checking initialization status
    Then all should default to uninitialized
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.local_count = 3
    frame = CallFrame(bytecode, 3, Value.from_smi(0))

    # When/Then
    assert frame.is_initialized(0) is False
    assert frame.is_initialized(1) is False
    assert frame.is_initialized(2) is False
