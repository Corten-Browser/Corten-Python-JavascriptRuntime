"""
Tests for bytecode compilation of spread/rest operators.

Tests spread in arrays, objects, function calls, and rest parameters/destructuring.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src import Parse
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode


def compile_source(source: str):
    """Helper to parse and compile source code."""
    ast = Parse(source, "test.js")
    compiler = BytecodeCompiler(ast)
    return compiler.compile()


class TestArraySpread:
    """Test bytecode compilation of array spread syntax."""

    def test_array_spread_single_element(self):
        """
        Given array with spread element
        When compiled to bytecode
        Then bytecode iterates source array and adds each element
        """
        # Given
        source = "const arr = [1, ...source, 2];"

        # When
        bytecode = compile_source(source)

        # Then - should create array and populate with elements
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have CREATE_ARRAY
        assert Opcode.CREATE_ARRAY in opcodes

        # Should load source array
        assert Opcode.LOAD_LOCAL in opcodes or Opcode.LOAD_GLOBAL in opcodes

        # Should use LOAD_ELEMENT to iterate spread source
        assert Opcode.LOAD_ELEMENT in opcodes

        # Should use STORE_ELEMENT to populate target array
        assert Opcode.STORE_ELEMENT in opcodes

    def test_array_spread_multiple_spreads(self):
        """
        Given array with multiple spread elements
        When compiled
        Then bytecode handles each spread separately
        """
        # Given
        source = "const arr = [...first, 5, ...second];"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create array
        assert Opcode.CREATE_ARRAY in opcodes

        # Should have element loads for spreads
        assert Opcode.LOAD_ELEMENT in opcodes

    def test_array_spread_only(self):
        """
        Given array with only spread element
        When compiled
        Then bytecode copies source array elements
        """
        # Given
        source = "const arr = [...source];"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create array and populate from source
        assert Opcode.CREATE_ARRAY in opcodes
        assert Opcode.LOAD_ELEMENT in opcodes

    def test_array_spread_with_literals(self):
        """
        Given array mixing literals and spread
        When compiled
        Then bytecode adds literals directly and iterates spread
        """
        # Given
        source = "const arr = [1, 2, ...middle, 3, 4];"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create array
        assert Opcode.CREATE_ARRAY in opcodes

        # Should have LOAD_CONSTANT for literals
        assert Opcode.LOAD_CONSTANT in opcodes

        # Should have LOAD_ELEMENT for spread
        assert Opcode.LOAD_ELEMENT in opcodes


class TestObjectSpread:
    """Test bytecode compilation of object spread syntax."""

    def test_object_spread_single_spread(self):
        """
        Given object with spread property
        When compiled to bytecode
        Then bytecode copies all properties from source
        """
        # Given
        source = "const obj = {x: 1, ...source};"

        # When
        bytecode = compile_source(source)

        # Then - should create object and copy properties
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create object
        assert Opcode.CREATE_OBJECT in opcodes

        # Should store regular property 'x'
        assert Opcode.STORE_PROPERTY in opcodes

        # Should load source object for spread
        assert Opcode.LOAD_LOCAL in opcodes or Opcode.LOAD_GLOBAL in opcodes

    def test_object_spread_multiple_spreads(self):
        """
        Given object with multiple spread properties
        When compiled
        Then bytecode handles each spread in order
        """
        # Given
        source = "const obj = {...first, x: 5, ...second};"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create object
        assert Opcode.CREATE_OBJECT in opcodes

        # Should have STORE_PROPERTY for regular property
        assert Opcode.STORE_PROPERTY in opcodes

    def test_object_spread_only(self):
        """
        Given object with only spread
        When compiled
        Then bytecode copies all properties from source
        """
        # Given
        source = "const obj = {...source};"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create object
        assert Opcode.CREATE_OBJECT in opcodes


class TestRestParameters:
    """Test bytecode compilation of rest parameters in functions."""

    def test_rest_parameter_only(self):
        """
        Given function with only rest parameter
        When compiled
        Then bytecode collects all arguments into array
        """
        # Given
        source = "function f(...args) { return args; }"

        # When
        bytecode = compile_source(source)

        # Then - function should be created with rest parameter handling
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create closure/function
        assert Opcode.CREATE_CLOSURE in opcodes

    def test_rest_parameter_with_regular_params(self):
        """
        Given function with regular and rest parameters
        When compiled
        Then bytecode assigns regular params and collects rest
        """
        # Given
        source = "function f(a, b, ...rest) { return rest; }"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create function
        assert Opcode.CREATE_CLOSURE in opcodes

    def test_arrow_function_with_rest_parameter(self):
        """
        Given arrow function with rest parameter
        When compiled
        Then bytecode handles rest like regular functions
        """
        # Given
        source = "const f = (...args) => args;"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create closure
        assert Opcode.CREATE_CLOSURE in opcodes


class TestRestInDestructuring:
    """Test bytecode compilation of rest in destructuring patterns."""

    def test_rest_in_array_destructuring(self):
        """
        Given array destructuring with rest element
        When compiled
        Then bytecode extracts named elements and collects rest
        """
        # Given
        source = "const [a, b, ...rest] = arr;"

        # When
        bytecode = compile_source(source)

        # Then - should extract elements 0, 1 and collect remaining
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have LOAD_ELEMENT for indexed access
        assert Opcode.LOAD_ELEMENT in opcodes

        # Should create array for rest elements
        assert Opcode.CREATE_ARRAY in opcodes

        # Should store to local variables
        assert Opcode.STORE_LOCAL in opcodes

    def test_rest_only_in_array_destructuring(self):
        """
        Given array destructuring with only rest element
        When compiled
        Then bytecode collects all elements
        """
        # Given
        source = "const [...rest] = arr;"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create array for rest
        assert Opcode.CREATE_ARRAY in opcodes

    def test_rest_in_object_destructuring(self):
        """
        Given object destructuring with rest element
        When compiled
        Then bytecode extracts named properties and collects rest
        """
        # Given
        source = "const {x, y, ...rest} = obj;"

        # When
        bytecode = compile_source(source)

        # Then - should extract x, y and collect remaining properties
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have LOAD_PROPERTY for named properties
        assert Opcode.LOAD_PROPERTY in opcodes

        # Should create object for rest properties
        assert Opcode.CREATE_OBJECT in opcodes

        # Should store to local variables
        assert Opcode.STORE_LOCAL in opcodes

    def test_rest_only_in_object_destructuring(self):
        """
        Given object destructuring with only rest element
        When compiled
        Then bytecode collects all properties
        """
        # Given
        source = "const {...rest} = obj;"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should create object for rest
        assert Opcode.CREATE_OBJECT in opcodes


class TestSpreadInFunctionCalls:
    """Test bytecode compilation of spread in function calls."""

    @pytest.mark.skip(
        reason="Parser doesn't support spread in function call arguments yet"
    )
    def test_spread_in_function_call(self):
        """
        Given function call with spread argument
        When compiled
        Then bytecode unpacks array elements as arguments
        """
        # Given
        source = "func(...args);"

        # When
        bytecode = compile_source(source)

        # Then - should unpack args and call function
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should load function
        assert Opcode.LOAD_LOCAL in opcodes or Opcode.LOAD_GLOBAL in opcodes

        # Should load args array
        # Should unpack elements using LOAD_ELEMENT
        assert Opcode.LOAD_ELEMENT in opcodes

        # Should call function
        assert Opcode.CALL_FUNCTION in opcodes

    @pytest.mark.skip(
        reason="Parser doesn't support spread in function call arguments yet"
    )
    def test_spread_mixed_with_regular_args(self):
        """
        Given function call mixing regular and spread arguments
        When compiled
        Then bytecode handles both types correctly
        """
        # Given
        source = "func(1, ...middle, 2);"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have LOAD_CONSTANT for literals
        assert Opcode.LOAD_CONSTANT in opcodes

        # Should have LOAD_ELEMENT for spread
        assert Opcode.LOAD_ELEMENT in opcodes

        # Should call function
        assert Opcode.CALL_FUNCTION in opcodes
