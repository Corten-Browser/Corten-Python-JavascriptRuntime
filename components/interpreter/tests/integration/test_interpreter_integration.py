"""
Integration tests for interpreter component.

Tests the complete interpreter workflow with real bytecode execution.
"""

import pytest
from components.interpreter.src import Execute, Interpreter
from components.bytecode.src import BytecodeArray, Instruction, Opcode
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value


def test_execute_function_simple_program():
    """
    Given simple bytecode program
    When executing via Execute function
    Then should return correct result
    """
    # Given
    bytecode = BytecodeArray()
    bytecode.add_constant(42)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = Execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_execute_with_provided_gc():
    """
    Given bytecode and garbage collector
    When executing with provided GC
    Then should use the provided GC instance
    """
    # Given
    gc = GarbageCollector()
    bytecode = BytecodeArray()
    bytecode.add_constant(100)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = Execute(bytecode, gc)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 100


def test_execute_arithmetic_expression():
    """
    Given bytecode for arithmetic expression (10 + 20) * 2
    When executing
    Then should compute correct result
    """
    # Given - compute (10 + 20) * 2 = 60
    bytecode = BytecodeArray()
    bytecode.add_constant(10)
    bytecode.add_constant(20)
    bytecode.add_constant(2)

    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.ADD))  # 10 + 20 = 30
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 2))  # Load 2
    bytecode.add_instruction(Instruction(Opcode.MULTIPLY))  # 30 * 2 = 60
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = Execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 60


def test_execute_with_local_variables():
    """
    Given bytecode that uses local variables
    When executing with arguments
    Then should handle locals correctly
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    bytecode = BytecodeArray()
    bytecode.local_count = 2
    bytecode.parameter_count = 2

    # Load local 0, load local 1, add, return
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 1))
    bytecode.add_instruction(Instruction(Opcode.ADD))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(
        bytecode, arguments=[Value.from_smi(15), Value.from_smi(25)]
    )

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 40


def test_execute_with_globals():
    """
    Given bytecode that uses global variables
    When executing
    Then should handle global scope correctly
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # Set global variable
    interpreter.set_global("x", Value.from_smi(50))

    # Create bytecode that loads global
    bytecode = BytecodeArray()
    bytecode.add_constant("x")
    bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 50


def test_execute_comparison_operations():
    """
    Given bytecode with comparison operations
    When executing
    Then should compute correct boolean results
    """
    # Given - compute 10 < 20
    bytecode = BytecodeArray()
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))
    bytecode.add_instruction(Instruction(Opcode.LESS_THAN))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = Execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 1  # True


def test_execute_conditional_jump():
    """
    Given bytecode with conditional jump
    When executing
    Then should follow correct branch
    """
    # Given - if (true) return 100 else return 200
    bytecode = BytecodeArray()
    bytecode.add_constant(100)
    bytecode.add_constant(200)

    bytecode.add_instruction(Instruction(Opcode.LOAD_TRUE))
    bytecode.add_instruction(Instruction(Opcode.JUMP_IF_FALSE, 5))  # Skip to else
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 100
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 200
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = Execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 100
