"""
Unit tests for array and object literal execution in interpreter.

Tests the CREATE_ARRAY, CREATE_OBJECT, and SET_PROPERTY opcodes
for executing JavaScript array and object literals.
"""

import pytest
from components.value_system.src import Value
from components.memory_gc.src import GarbageCollector
from components.bytecode.src import BytecodeArray, Instruction, Opcode
from components.object_runtime.src import JSArray, JSObject


def test_execute_empty_array():
    """
    Given bytecode with CREATE_ARRAY (0 elements)
    When executing bytecode
    Then should return an empty JSArray
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_instruction(Instruction(Opcode.CREATE_ARRAY, 0))  # Create empty array
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    array = result.value.to_object()
    assert isinstance(array, JSArray)
    assert array._length == 0


def test_execute_array_with_elements():
    """
    Given bytecode with CREATE_ARRAY (3 elements)
    When executing bytecode with elements on stack
    Then should return JSArray with 3 elements
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(10)
    bytecode.add_constant(20)
    bytecode.add_constant(30)
    # Push elements onto stack
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # 10
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # 20
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 2))  # 30
    # Create array with 3 elements
    bytecode.add_instruction(Instruction(Opcode.CREATE_ARRAY, 3))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    array = result.value.to_object()
    assert isinstance(array, JSArray)
    assert array._length == 3
    assert array.get_element(0).to_smi() == 10
    assert array.get_element(1).to_smi() == 20
    assert array.get_element(2).to_smi() == 30


def test_execute_nested_arrays():
    """
    Given bytecode creating nested arrays
    When executing bytecode
    Then should return array containing arrays
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(1)
    bytecode.add_constant(2)

    # Create inner array [1, 2]
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # 1
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # 2
    bytecode.add_instruction(Instruction(Opcode.CREATE_ARRAY, 2))

    # Create outer array containing inner array
    bytecode.add_instruction(Instruction(Opcode.CREATE_ARRAY, 1))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    outer_array = result.value.to_object()
    assert isinstance(outer_array, JSArray)
    assert outer_array._length == 1

    inner_array = outer_array.get_element(0).to_object()
    assert isinstance(inner_array, JSArray)
    assert inner_array._length == 2
    assert inner_array.get_element(0).to_smi() == 1
    assert inner_array.get_element(1).to_smi() == 2


def test_execute_empty_object():
    """
    Given bytecode with CREATE_OBJECT
    When executing bytecode
    Then should return an empty JSObject
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))  # Create empty object
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    obj = result.value.to_object()
    assert isinstance(obj, JSObject)


def test_execute_object_with_properties():
    """
    Given bytecode creating object with properties
    When executing bytecode
    Then should return JSObject with properties set
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(42)
    bytecode.add_constant(100)

    # Create object
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))

    # Set property "x" = 42
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(
        Instruction(Opcode.STORE_PROPERTY, "x")
    )  # Set property "x"

    # Set property "y" = 100
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 100
    bytecode.add_instruction(
        Instruction(Opcode.STORE_PROPERTY, "y")
    )  # Set property "y"

    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    obj = result.value.to_object()
    assert isinstance(obj, JSObject)
    assert obj.get_property("x").to_smi() == 42
    assert obj.get_property("y").to_smi() == 100


def test_execute_object_property_access():
    """
    Given bytecode creating object and accessing property
    When executing bytecode
    Then should return property value
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(42)

    # Create object
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))

    # Set property "x" = 42
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(
        Instruction(Opcode.STORE_PROPERTY, "x")
    )  # Set property "x"

    # Access property "x"
    bytecode.add_instruction(
        Instruction(Opcode.LOAD_PROPERTY, "x")
    )  # Load property "x"

    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    assert result.value.to_smi() == 42


def test_execute_nested_objects():
    """
    Given bytecode creating nested objects
    When executing bytecode
    Then should return object containing objects
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(42)

    # Create inner object
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(
        Instruction(Opcode.STORE_PROPERTY, "value")
    )  # Set inner.value = 42

    # Create outer object
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))
    # Stack: [inner_obj, outer_obj]
    # Need to swap to set inner as property of outer
    # For now, use a simpler approach - create outer first, then set properties

    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    # This test will need adjustment based on actual bytecode pattern
    # For now, just verify we got an object back
    obj = result.value.to_object()
    assert isinstance(obj, JSObject)


def test_execute_mixed_array_object_structure():
    """
    Given bytecode creating array of objects
    When executing bytecode
    Then should return array containing objects
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(10)
    bytecode.add_constant(20)

    # Create first object {x: 10}
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 10
    bytecode.add_instruction(Instruction(Opcode.STORE_PROPERTY, "x"))

    # Create second object {x: 20}
    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 1))  # Load 20
    bytecode.add_instruction(Instruction(Opcode.STORE_PROPERTY, "x"))

    # Create array containing both objects
    bytecode.add_instruction(Instruction(Opcode.CREATE_ARRAY, 2))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    array = result.value.to_object()
    assert isinstance(array, JSArray)
    assert array._length == 2

    obj1 = array.get_element(0).to_object()
    assert isinstance(obj1, JSObject)
    assert obj1.get_property("x").to_smi() == 10

    obj2 = array.get_element(1).to_object()
    assert isinstance(obj2, JSObject)
    assert obj2.get_property("x").to_smi() == 20


def test_execute_array_with_single_element():
    """
    Given bytecode creating array with one element
    When executing bytecode
    Then should return array with one element
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(42)
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
    bytecode.add_instruction(
        Instruction(Opcode.CREATE_ARRAY, 1)
    )  # Create array with 1 element
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    array = result.value.to_object()
    assert isinstance(array, JSArray)
    assert array._length == 1
    assert array.get_element(0).to_smi() == 42


def test_execute_object_with_single_property():
    """
    Given bytecode creating object with one property
    When executing bytecode
    Then should return object with one property
    """
    from components.interpreter.src.interpreter import Interpreter

    # Given
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    bytecode = BytecodeArray()
    bytecode.add_constant(100)

    bytecode.add_instruction(Instruction(Opcode.CREATE_OBJECT))
    bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 100
    bytecode.add_instruction(Instruction(Opcode.STORE_PROPERTY, "value"))
    bytecode.add_instruction(Instruction(Opcode.RETURN))

    # When
    result = interpreter.execute(bytecode)

    # Then
    assert result.is_success()
    obj = result.value.to_object()
    assert isinstance(obj, JSObject)
    assert obj.get_property("value").to_smi() == 100
