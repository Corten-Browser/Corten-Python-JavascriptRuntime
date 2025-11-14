"""
Unit tests for CallFrame class.

Tests the function call frame that manages local variables, operand stack,
and program counter for bytecode execution.
"""

import pytest
from components.value_system.src import Value
from components.bytecode.src import BytecodeArray, Instruction, Opcode


def test_call_frame_creation():
    """
    Given bytecode and local count
    When creating a CallFrame
    Then frame should be initialized with empty stack and locals
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    bytecode.local_count = 3
    local_count = 3
    this_value = Value.from_smi(42)

    # When
    frame = CallFrame(bytecode, local_count, this_value)

    # Then
    assert frame.bytecode == bytecode
    assert frame.pc == 0
    assert frame.this_value == this_value
    assert len(frame.locals) == local_count
    assert len(frame.stack) == 0


def test_call_frame_push_to_stack():
    """
    Given a call frame
    When pushing a value onto the stack
    Then value should be added to top of stack
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))
    value = Value.from_smi(100)

    # When
    frame.push(value)

    # Then
    assert len(frame.stack) == 1
    assert frame.stack[0] == value


def test_call_frame_push_multiple_values():
    """
    Given a call frame
    When pushing multiple values
    Then values should be stacked in order
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))
    value1 = Value.from_smi(1)
    value2 = Value.from_smi(2)
    value3 = Value.from_smi(3)

    # When
    frame.push(value1)
    frame.push(value2)
    frame.push(value3)

    # Then
    assert len(frame.stack) == 3
    assert frame.stack[0] == value1
    assert frame.stack[1] == value2
    assert frame.stack[2] == value3


def test_call_frame_pop_from_stack():
    """
    Given a call frame with values on stack
    When popping a value
    Then top value should be removed and returned
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))
    value1 = Value.from_smi(1)
    value2 = Value.from_smi(2)
    frame.push(value1)
    frame.push(value2)

    # When
    popped = frame.pop()

    # Then
    assert popped == value2
    assert len(frame.stack) == 1
    assert frame.stack[0] == value1


def test_call_frame_pop_multiple_values():
    """
    Given a call frame with multiple values
    When popping values
    Then values should be popped in LIFO order
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))
    value1 = Value.from_smi(1)
    value2 = Value.from_smi(2)
    value3 = Value.from_smi(3)
    frame.push(value1)
    frame.push(value2)
    frame.push(value3)

    # When
    popped3 = frame.pop()
    popped2 = frame.pop()
    popped1 = frame.pop()

    # Then
    assert popped3 == value3
    assert popped2 == value2
    assert popped1 == value1
    assert len(frame.stack) == 0


def test_call_frame_pop_from_empty_stack():
    """
    Given an empty call frame
    When attempting to pop
    Then should raise IndexError
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))

    # When / Then
    with pytest.raises(IndexError):
        frame.pop()


def test_call_frame_peek_at_stack_top():
    """
    Given a call frame with values on stack
    When peeking at top value
    Then top value should be returned without removing it
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))
    value1 = Value.from_smi(1)
    value2 = Value.from_smi(2)
    frame.push(value1)
    frame.push(value2)

    # When
    peeked = frame.peek()

    # Then
    assert peeked == value2
    assert len(frame.stack) == 2  # Stack unchanged


def test_call_frame_peek_empty_stack():
    """
    Given an empty call frame
    When attempting to peek
    Then should raise IndexError
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))

    # When / Then
    with pytest.raises(IndexError):
        frame.peek()


def test_call_frame_local_variables():
    """
    Given a call frame with locals
    When accessing local variables
    Then locals should be accessible by index
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 3, Value.from_smi(0))

    # When
    frame.locals[0] = Value.from_smi(10)
    frame.locals[1] = Value.from_smi(20)
    frame.locals[2] = Value.from_smi(30)

    # Then
    assert frame.locals[0].to_smi() == 10
    assert frame.locals[1].to_smi() == 20
    assert frame.locals[2].to_smi() == 30


def test_call_frame_program_counter():
    """
    Given a call frame
    When accessing program counter
    Then pc should start at 0 and be modifiable
    """
    from components.interpreter.src.call_frame import CallFrame

    # Given
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))

    # Then
    assert frame.pc == 0

    # When
    frame.pc = 5

    # Then
    assert frame.pc == 5
