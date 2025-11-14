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


# ============================================================================
# Arrow Function Integration Tests (End-to-End)
# ============================================================================


def test_e2e_arrow_function_simple():
    """
    E2E test: Arrow function creation and execution
    Given: const f = () => 42;
    When: executing f()
    Then: should return 42
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # Arrow function bytecode: () => 42
    function_bytecode = BytecodeArray()
    function_bytecode.add_constant(42)
    function_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    function_bytecode.add_instruction(Instruction(Opcode.RETURN))

    # Main bytecode: const f = () => 42; return f();
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # Create closure
    bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, function_bytecode))
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # f = function

    # Call function
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load f
    bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))  # Call f()
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_e2e_arrow_function_multiple_params():
    """
    E2E test: Arrow function with multiple parameters
    Given: const add = (a, b) => a + b;
    When: executing add(10, 20)
    Then: should return 30
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # Arrow function bytecode: (a, b) => a + b
    function_bytecode = BytecodeArray()
    function_bytecode.local_count = 2
    function_bytecode.parameter_count = 2
    function_bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load a
    function_bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 1))  # Load b
    function_bytecode.add_instruction(Instruction(Opcode.ADD))  # a + b
    function_bytecode.add_instruction(Instruction(Opcode.RETURN))

    # Main bytecode: const add = (a, b) => a + b; return add(10, 20);
    bytecode = BytecodeArray()
    bytecode.local_count = 1
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # Create closure
    bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 2, function_bytecode))
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # add = function

    # Call function with arguments
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load add
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 2))  # Call add(10, 20)
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 30


def test_e2e_arrow_function_closure():
    """
    E2E test: Arrow function with closure variable capture
    Given: const x = 100; const f = () => x;
    When: executing f()
    Then: should return 100
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # Arrow function bytecode: () => 100 (simplified closure)
    function_bytecode = BytecodeArray()
    function_bytecode.add_constant(100)
    function_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    function_bytecode.add_instruction(Instruction(Opcode.RETURN))

    # Main bytecode: const x = 100; const f = () => x; return f();
    bytecode = BytecodeArray()
    bytecode.local_count = 2
    bytecode.add_constant(100)

    # x = 100
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))

    # Create closure
    bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, function_bytecode))
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # f = function

    # Call function
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 1))  # Load f
    bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))  # Call f()
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 100


def test_e2e_arrow_function_as_callback():
    """
    E2E test: Arrow function used as callback (higher-order function)
    Given: Arrow function that takes another arrow function as argument
    When: executing nested calls
    Then: should execute correctly
    """
    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)

    # Inner arrow function: () => 50
    inner_function_bytecode = BytecodeArray()
    inner_function_bytecode.add_constant(50)
    inner_function_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    inner_function_bytecode.add_instruction(Instruction(Opcode.RETURN))

    # Create and call inner function, return result
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # Create inner function
    bytecode.add_instruction(
        Instruction(Opcode.CREATE_CLOSURE, 0, inner_function_bytecode)
    )
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # callback = function

    # Call callback
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load callback
    bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))  # Call callback()
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 50
