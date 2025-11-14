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


# ============================================================================
# let/const Tests (Phase 1 - Basic Support)
# ============================================================================


def test_execute_let_declaration():
    """
    Given bytecode declaring a let variable with initialization
    When executing
    Then variable should be stored and retrievable
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # let x = 42;
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # Store to local 0
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load local 0
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(42)

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_execute_let_reassignment():
    """
    Given a let variable that is reassigned
    When executing reassignment
    Then new value should be stored successfully
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # let x = 10;
    # x = 20;
    # return x;
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # Store to local 0
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # Reassign local 0
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load local 0
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 20


def test_execute_const_declaration():
    """
    Given bytecode declaring a const variable with initialization
    When executing
    Then variable should be stored and retrievable
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # const x = 42;
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # Store to local 0
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load local 0
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(42)

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_execute_const_reassignment_error():
    """
    Given a const variable that is reassigned
    When attempting reassignment
    Then should raise TypeError for assignment to constant
    """
    from components.interpreter.src.interpreter import Interpreter
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # const x = 10;
    # x = 20;  // TypeError
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(
        Instruction(Opcode.STORE_LOCAL, 0)
    )  # Store to local 0 (const)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(
        Instruction(Opcode.STORE_LOCAL, 0)
    )  # Try to reassign const
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # Mark local 0 as const before execution
    # (In real implementation, DECLARE_VAR would do this)
    def mark_const_before_execution(frame: CallFrame):
        frame.set_variable_kind(0, "const")

    # Patch execute to mark variable as const
    original_execute_frame = interpreter._execute_frame

    def patched_execute_frame(frame):
        mark_const_before_execution(frame)
        return original_execute_frame(frame)

    interpreter._execute_frame = patched_execute_frame

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_exception()
    assert isinstance(result.exception, TypeError)
    assert "constant" in str(result.exception).lower()


def test_execute_const_immutability():
    """
    Given multiple const variable reassignment attempts
    When executing
    Then all reassignments should fail with TypeError
    """
    from components.interpreter.src.interpreter import Interpreter
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 2

    # const x = 10;
    # const y = 20;
    # y = 30;  // Should fail
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # x = 10 (const)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # y = 20 (const)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 2))  # Load 30
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # Try y = 30
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(10)
    bytecode.add_constant(20)
    bytecode.add_constant(30)

    # Mark locals as const
    def mark_const_before_execution(frame: CallFrame):
        frame.set_variable_kind(0, "const")
        frame.set_variable_kind(1, "const")

    original_execute_frame = interpreter._execute_frame

    def patched_execute_frame(frame):
        mark_const_before_execution(frame)
        return original_execute_frame(frame)

    interpreter._execute_frame = patched_execute_frame

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_exception()
    assert isinstance(result.exception, TypeError)


def test_execute_var_still_works():
    """
    Given var variables
    When executing with reassignments
    Then var should work as before (reassignment allowed)
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # var x = 10;
    # x = 20;
    # return x;
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # x = 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # x = 20 (allowed)
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load x
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 20


def test_execute_mixed_var_let_const():
    """
    Given bytecode with var, let, and const variables
    When executing
    Then var and let allow reassignment, const does not
    """
    from components.interpreter.src.interpreter import Interpreter
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 3

    # var v = 1;
    # let l = 2;
    # const c = 3;
    # v = 10;  // OK
    # l = 20;  // OK
    # c = 30;  // TypeError
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 1
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # v = 1
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 2
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # l = 2
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 2))  # Load 3
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 2))  # c = 3
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 3))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # v = 10 (OK)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 4))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # l = 20 (OK)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 5))  # Load 30
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 2))  # c = 30 (ERROR)
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(1)
    bytecode.add_constant(2)
    bytecode.add_constant(3)
    bytecode.add_constant(10)
    bytecode.add_constant(20)
    bytecode.add_constant(30)

    # Mark variable kinds
    def mark_kinds_before_execution(frame: CallFrame):
        frame.set_variable_kind(0, "var")  # v is var
        frame.set_variable_kind(1, "let")  # l is let
        frame.set_variable_kind(2, "const")  # c is const

    original_execute_frame = interpreter._execute_frame

    def patched_execute_frame(frame):
        mark_kinds_before_execution(frame)
        return original_execute_frame(frame)

    interpreter._execute_frame = patched_execute_frame

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_exception()
    assert isinstance(result.exception, TypeError)


def test_execute_let_with_expressions():
    """
    Given let variables used in expressions
    When executing arithmetic with let variables
    Then should work correctly
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 3

    # let x = 10;
    # let y = 20;
    # let z = x + y;
    # return z;
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # x = 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))  # y = 20
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load x
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 1))  # Load y
    bytecode.add_instruction(Instruction(Opcode.ADD))  # x + y
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 2))  # z = result
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 2))  # Load z
    bytecode.add_instruction(Instruction(Opcode.RETURN))
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 30


def test_execute_const_with_object_literal():
    """
    Given const variable with object value
    When storing and retrieving object
    Then should work correctly (Phase 1: const binding, not object immutability)
    """
    from components.interpreter.src.interpreter import Interpreter
    from components.interpreter.src.call_frame import CallFrame

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.local_count = 1

    # const obj = {};
    # return obj;
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))  # Create object
    bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))  # obj = {}
    bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))  # Load obj
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # Mark as const
    def mark_const_before_execution(frame: CallFrame):
        frame.set_variable_kind(0, "const")

    original_execute_frame = interpreter._execute_frame

    def patched_execute_frame(frame):
        mark_const_before_execution(frame)
        return original_execute_frame(frame)

    interpreter._execute_frame = patched_execute_frame

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_object() is not None
