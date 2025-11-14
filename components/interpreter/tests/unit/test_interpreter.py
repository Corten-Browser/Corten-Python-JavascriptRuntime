"""
Unit tests for Interpreter class.

Tests the bytecode interpreter including opcode dispatch, global variables,
and function call handling.
"""

import pytest
from components.value_system.src import Value
from components.memory_gc.src import GarbageCollector
from components.bytecode.src import BytecodeArray, Instruction, Opcode


def test_interpreter_creation():
    """
    Given a garbage collector
    When creating an Interpreter
    Then interpreter should be initialized with GC reference
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()

    # When
    interpreter = Interpreter(gc)

    # Then
    assert interpreter.gc == gc


def test_interpreter_execute_simple_return():
    """
    Given bytecode with LOAD_CONSTANT and RETURN
    When executing bytecode
    Then should return the constant value
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(42)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 0
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_interpreter_set_and_get_global():
    """
    Given an interpreter
    When setting and getting global variables
    Then globals should be accessible
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    value = Value.from_smi(100)

    # When
    interpreter.set_global("x", value)
    retrieved = interpreter.get_global("x")

    # Then
    assert retrieved == value


def test_interpreter_get_undefined_global():
    """
    Given an interpreter
    When getting an undefined global variable
    Then should raise ReferenceError
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # When / Then
    with pytest.raises(Exception):  # Will be ReferenceError in implementation
        interpreter.get_global("undefined_var")


def test_interpreter_execute_with_arguments():
    """
    Given bytecode and arguments
    When executing with arguments
    Then arguments should be available as locals
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 2
    bytecode.parameter_count = 2
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load local 0
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    arg1 = Value.from_smi(10)
    arg2 = Value.from_smi(20)

    # When
    result = interpreter.execute(bytecode, arguments=[arg1, arg2])

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 10


def test_interpreter_execute_arithmetic():
    """
    Given bytecode with arithmetic operations
    When executing
    Then should perform arithmetic correctly
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(10)
    bytecode.add_constant(20)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.ADD))  # 10 + 20
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 30


def test_interpreter_execute_with_exception():
    """
    Given bytecode that throws an exception
    When executing
    Then should return EvaluationResult with exception
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    # Try to load undefined global - should raise exception
    bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))  # undefined
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant("undefined_var")

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_exception()
    assert result.exception is not None
