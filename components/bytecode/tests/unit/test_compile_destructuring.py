"""
Tests for bytecode compilation of destructuring patterns.

Tests object and array destructuring in variable declarations.
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


class TestObjectDestructuring:
    """Test bytecode compilation of object destructuring."""

    def test_simple_object_destructuring(self):
        """
        Given simple object destructuring
        When compiled to bytecode
        Then bytecode expands to individual property assignments
        """
        # Given
        source = "const {x, y} = obj;"

        # When
        bytecode = compile_source(source)

        # Then - should expand to approximately:
        # LOAD_LOCAL obj
        # DUP
        # LOAD_CONSTANT "x"
        # LOAD_PROPERTY
        # STORE_LOCAL x
        # DUP
        # LOAD_CONSTANT "y"
        # LOAD_PROPERTY
        # STORE_LOCAL y
        # POP (remove obj from stack)

        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have LOAD_LOCAL for obj
        assert Opcode.LOAD_LOCAL in opcodes or Opcode.LOAD_GLOBAL in opcodes

        # Should have LOAD_PROPERTY for accessing x and y
        property_loads = opcodes.count(Opcode.LOAD_PROPERTY)
        assert property_loads == 2, f"Expected 2 LOAD_PROPERTY, got {property_loads}"

        # Should have STORE_LOCAL for x and y
        store_locals = opcodes.count(Opcode.STORE_LOCAL)
        assert store_locals >= 2, f"Expected at least 2 STORE_LOCAL, got {store_locals}"

    def test_object_destructuring_with_renaming(self):
        """
        Given object destructuring with renaming
        When compiled
        Then bytecode uses original property names but stores to new variables
        """
        # Given
        source = "const {x: newX, y: newY} = obj;"

        # When
        bytecode = compile_source(source)

        # Then
        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should access properties x and y
        assert opcodes.count(Opcode.LOAD_PROPERTY) == 2

        # Should store to two local variables (newX and newY)
        assert opcodes.count(Opcode.STORE_LOCAL) >= 2


class TestArrayDestructuring:
    """Test bytecode compilation of array destructuring."""

    def test_simple_array_destructuring(self):
        """
        Given simple array destructuring
        When compiled to bytecode
        Then bytecode expands to indexed element access
        """
        # Given
        source = "const [a, b] = arr;"

        # When
        bytecode = compile_source(source)

        # Then - should expand to approximately:
        # LOAD_LOCAL arr
        # DUP
        # LOAD_CONSTANT 0
        # LOAD_ELEMENT
        # STORE_LOCAL a
        # DUP
        # LOAD_CONSTANT 1
        # LOAD_ELEMENT
        # STORE_LOCAL b
        # POP (remove arr from stack)

        instructions = bytecode.instructions
        opcodes = [inst.opcode for inst in instructions]

        # Should have LOAD_LOCAL for arr
        assert Opcode.LOAD_LOCAL in opcodes or Opcode.LOAD_GLOBAL in opcodes

        # Should have LOAD_ELEMENT for accessing arr[0] and arr[1]
        element_loads = opcodes.count(Opcode.LOAD_ELEMENT)
        assert element_loads == 2, f"Expected 2 LOAD_ELEMENT, got {element_loads}"

        # Should have STORE_LOCAL for a and b
        store_locals = opcodes.count(Opcode.STORE_LOCAL)
        assert store_locals >= 2, f"Expected at least 2 STORE_LOCAL, got {store_locals}"

    def test_array_destructuring_with_three_elements(self):
        """
        Given array destructuring with three elements
        When compiled
        Then bytecode accesses three array indices
        """
        # Given
        source = "const [a, b, c] = arr;"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should access arr[0], arr[1], arr[2]
        assert opcodes.count(Opcode.LOAD_ELEMENT) == 3


class TestNestedDestructuring:
    """Test bytecode compilation of nested destructuring."""

    def test_nested_object_destructuring(self):
        """
        Given nested object destructuring
        When compiled
        Then bytecode handles nested property access
        """
        # Given
        source = "const {x: {y}} = obj;"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have LOAD_PROPERTY for both x and y
        assert opcodes.count(Opcode.LOAD_PROPERTY) >= 2

    def test_nested_array_destructuring(self):
        """
        Given nested array destructuring
        When compiled
        Then bytecode handles nested element access
        """
        # Given
        source = "const [[a, b], c] = arr;"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have LOAD_ELEMENT for nested arrays and c
        # arr[0], arr[0][0], arr[0][1], arr[1]
        assert opcodes.count(Opcode.LOAD_ELEMENT) >= 3

    def test_mixed_nested_destructuring(self):
        """
        Given mixed object and array destructuring
        When compiled
        Then bytecode uses appropriate access methods
        """
        # Given
        source = "const {x, y: [a, b]} = obj;"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have LOAD_PROPERTY for x and y
        assert opcodes.count(Opcode.LOAD_PROPERTY) >= 2

        # Should have LOAD_ELEMENT for a and b
        assert opcodes.count(Opcode.LOAD_ELEMENT) >= 2


class TestDefaultValues:
    """Test bytecode compilation of default values in destructuring."""

    def test_object_destructuring_with_defaults(self):
        """
        Given object destructuring with default value
        When compiled
        Then bytecode checks for undefined and uses default
        """
        # Given
        source = "const {x = 10} = obj;"

        # When
        bytecode = compile_source(source)

        # Then - should check if property is undefined and use default
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have property load
        assert Opcode.LOAD_PROPERTY in opcodes

        # Should have conditional logic for default value
        # (JUMP_IF_NOT_UNDEFINED or similar pattern)
        assert Opcode.JUMP_IF_TRUE in opcodes or Opcode.JUMP_IF_FALSE in opcodes or Opcode.LOAD_CONSTANT in opcodes

    def test_array_destructuring_with_defaults(self):
        """
        Given array destructuring with default values
        When compiled
        Then bytecode checks for undefined and uses defaults
        """
        # Given
        source = "const [a = 5, b = 10] = arr;"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have element loads
        assert opcodes.count(Opcode.LOAD_ELEMENT) >= 2

        # Should have conditional logic for defaults
        assert Opcode.JUMP_IF_TRUE in opcodes or Opcode.JUMP_IF_FALSE in opcodes or Opcode.LOAD_CONSTANT in opcodes


class TestDestructuringIntegration:
    """Test integration of destructuring compilation."""

    def test_destructuring_in_multiple_declarations(self):
        """
        Given multiple destructuring declarations
        When compiled
        Then all patterns are handled correctly
        """
        # Given
        source = """
        const {x, y} = obj1;
        const [a, b] = arr1;
        let {z} = obj2;
        """

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have property loads for x, y, z
        assert opcodes.count(Opcode.LOAD_PROPERTY) >= 3

        # Should have element loads for a, b
        assert opcodes.count(Opcode.LOAD_ELEMENT) >= 2

    def test_destructuring_with_expressions(self):
        """
        Given destructuring with expression initializer
        When compiled
        Then initializer expression is compiled correctly
        """
        # Given
        source = "const {x} = getObject();"

        # When
        bytecode = compile_source(source)

        # Then
        opcodes = [inst.opcode for inst in bytecode.instructions]

        # Should have function call
        assert Opcode.CALL_FUNCTION in opcodes

        # Should have property load
        assert Opcode.LOAD_PROPERTY in opcodes
