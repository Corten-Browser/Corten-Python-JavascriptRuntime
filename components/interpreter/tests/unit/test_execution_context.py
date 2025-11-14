"""
Unit tests for ExecutionContext class.

Tests the execution state manager that tracks global variables,
call stack, and garbage collector.
"""

import pytest
from components.value_system.src import Value
from components.memory_gc.src import GarbageCollector
from components.bytecode.src import BytecodeArray


def test_execution_context_creation():
    """
    Given a garbage collector
    When creating an ExecutionContext
    Then context should be initialized with empty global scope and call stack
    """
    from components.interpreter.src.execution_context import ExecutionContext

    # Given
    gc = GarbageCollector()

    # When
    context = ExecutionContext(gc)

    # Then
    assert context.gc == gc
    assert isinstance(context.global_scope, dict)
    assert len(context.global_scope) == 0
    assert isinstance(context.call_stack, list)
    assert len(context.call_stack) == 0


def test_execution_context_push_frame():
    """
    Given an execution context
    When pushing a call frame
    Then frame should be added to call stack
    """
    from components.interpreter.src.execution_context import ExecutionContext
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)
    bytecode = BytecodeArray()
    frame = CallFrame(bytecode, 0, Value.from_smi(0))

    # When
    context.push_frame(frame)

    # Then
    assert len(context.call_stack) == 1
    assert context.call_stack[0] == frame


def test_execution_context_push_multiple_frames():
    """
    Given an execution context
    When pushing multiple frames
    Then frames should be stacked in order
    """
    from components.interpreter.src.execution_context import ExecutionContext
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)
    bytecode1 = BytecodeArray()
    bytecode2 = BytecodeArray()
    bytecode3 = BytecodeArray()
    frame1 = CallFrame(bytecode1, 0, Value.from_smi(0))
    frame2 = CallFrame(bytecode2, 0, Value.from_smi(0))
    frame3 = CallFrame(bytecode3, 0, Value.from_smi(0))

    # When
    context.push_frame(frame1)
    context.push_frame(frame2)
    context.push_frame(frame3)

    # Then
    assert len(context.call_stack) == 3
    assert context.call_stack[0] == frame1
    assert context.call_stack[1] == frame2
    assert context.call_stack[2] == frame3


def test_execution_context_pop_frame():
    """
    Given an execution context with frames
    When popping a frame
    Then top frame should be removed and returned
    """
    from components.interpreter.src.execution_context import ExecutionContext
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)
    bytecode1 = BytecodeArray()
    bytecode2 = BytecodeArray()
    frame1 = CallFrame(bytecode1, 0, Value.from_smi(0))
    frame2 = CallFrame(bytecode2, 0, Value.from_smi(0))
    context.push_frame(frame1)
    context.push_frame(frame2)

    # When
    popped = context.pop_frame()

    # Then
    assert popped == frame2
    assert len(context.call_stack) == 1
    assert context.call_stack[0] == frame1


def test_execution_context_pop_from_empty_stack():
    """
    Given an empty execution context
    When attempting to pop frame
    Then should raise IndexError
    """
    from components.interpreter.src.execution_context import ExecutionContext

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)

    # When / Then
    with pytest.raises(IndexError):
        context.pop_frame()


def test_execution_context_current_frame():
    """
    Given an execution context with frames
    When getting current frame
    Then top frame should be returned without removing it
    """
    from components.interpreter.src.execution_context import ExecutionContext
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)
    bytecode1 = BytecodeArray()
    bytecode2 = BytecodeArray()
    frame1 = CallFrame(bytecode1, 0, Value.from_smi(0))
    frame2 = CallFrame(bytecode2, 0, Value.from_smi(0))
    context.push_frame(frame1)
    context.push_frame(frame2)

    # When
    current = context.current_frame()

    # Then
    assert current == frame2
    assert len(context.call_stack) == 2  # Stack unchanged


def test_execution_context_current_frame_empty_stack():
    """
    Given an empty execution context
    When attempting to get current frame
    Then should raise IndexError
    """
    from components.interpreter.src.execution_context import ExecutionContext

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)

    # When / Then
    with pytest.raises(IndexError):
        context.current_frame()


def test_execution_context_global_scope():
    """
    Given an execution context
    When setting and getting global variables
    Then global scope should store variables
    """
    from components.interpreter.src.execution_context import ExecutionContext

    # Given
    gc = GarbageCollector()
    context = ExecutionContext(gc)

    # When
    context.global_scope["x"] = Value.from_smi(10)
    context.global_scope["y"] = Value.from_smi(20)

    # Then
    assert context.global_scope["x"].to_smi() == 10
    assert context.global_scope["y"].to_smi() == 20
