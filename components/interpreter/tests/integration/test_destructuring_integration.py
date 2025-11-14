"""
Integration tests for destructuring.

Tests complete pipeline: parse -> compile -> execute for destructuring patterns.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src import Parse
from components.bytecode.src.compiler import BytecodeCompiler
from components.interpreter.src.interpreter import Interpreter
from components.value_system.src.value import JSValue


def execute(source: str):
    """Helper to parse, compile, and execute JavaScript code."""
    ast = Parse(source, "test.js")
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()
    interpreter = Interpreter(bytecode)
    result = interpreter.run()
    return result.value if result else None


class TestObjectDestructuringIntegration:
    """Integration tests for object destructuring."""

    def test_simple_object_destructuring(self):
        """
        Given object destructuring with simple properties
        When executed
        Then variables are assigned correctly
        """
        # Given
        source = """
        const obj = {x: 10, y: 20};
        const {x, y} = obj;
        x + y
        """

        # When
        result = execute(source)

        # Then
        assert result == 30

    def test_object_destructuring_with_renaming(self):
        """
        Given object destructuring with property renaming
        When executed
        Then renamed variables have correct values
        """
        # Given
        source = """
        const obj = {x: 5, y: 15};
        const {x: a, y: b} = obj;
        a * b
        """

        # When
        result = execute(source)

        # Then
        assert result == 75

    def test_object_destructuring_with_defaults(self):
        """
        Given object destructuring with default values
        When property is undefined
        Then default value is used
        """
        # Given
        source = """
        const obj = {x: 10};
        const {x, y = 20} = obj;
        x + y
        """

        # When
        result = execute(source)

        # Then
        assert result == 30


class TestArrayDestructuringIntegration:
    """Integration tests for array destructuring."""

    def test_simple_array_destructuring(self):
        """
        Given array destructuring with simple elements
        When executed
        Then variables are assigned correctly
        """
        # Given
        source = """
        const arr = [10, 20, 30];
        const [a, b, c] = arr;
        a + b + c
        """

        # When
        result = execute(source)

        # Then
        assert result == 60

    def test_array_destructuring_partial(self):
        """
        Given array destructuring with fewer variables than elements
        When executed
        Then only specified variables are assigned
        """
        # Given
        source = """
        const arr = [5, 10, 15, 20];
        const [a, b] = arr;
        a * b
        """

        # When
        result = execute(source)

        # Then
        assert result == 50

    def test_array_destructuring_with_defaults(self):
        """
        Given array destructuring with default values
        When element is undefined
        Then default value is used
        """
        # Given
        source = """
        const arr = [10];
        const [a, b = 5] = arr;
        a + b
        """

        # When
        result = execute(source)

        # Then
        assert result == 15


class TestNestedDestructuringIntegration:
    """Integration tests for nested destructuring."""

    def test_nested_object_destructuring(self):
        """
        Given nested object destructuring
        When executed
        Then nested properties are extracted correctly
        """
        # Given
        source = """
        const obj = {x: {y: 100}};
        const {x: {y}} = obj;
        y
        """

        # When
        result = execute(source)

        # Then
        assert result == 100

    def test_nested_array_destructuring(self):
        """
        Given nested array destructuring
        When executed
        Then nested elements are extracted correctly
        """
        # Given
        source = """
        const arr = [[1, 2], 3];
        const [[a, b], c] = arr;
        a + b + c
        """

        # When
        result = execute(source)

        # Then
        assert result == 6

    def test_mixed_nested_destructuring(self):
        """
        Given mixed object and array destructuring
        When executed
        Then all values are extracted correctly
        """
        # Given
        source = """
        const obj = {x: 5, y: [10, 15]};
        const {x, y: [a, b]} = obj;
        x + a + b
        """

        # When
        result = execute(source)

        # Then
        assert result == 30


class TestDestructuringUseCases:
    """Test practical use cases of destructuring."""

    def test_destructuring_function_return(self):
        """
        Given destructuring of function return value
        When executed
        Then return values are correctly extracted
        """
        # Given
        source = """
        function getPoint() {
            return {x: 10, y: 20};
        }
        const {x, y} = getPoint();
        x + y
        """

        # When
        result = execute(source)

        # Then
        assert result == 30

    def test_destructuring_multiple_declarations(self):
        """
        Given multiple destructuring declarations
        When executed
        Then all variables are assigned correctly
        """
        # Given
        source = """
        const obj1 = {a: 1};
        const obj2 = {b: 2};
        const {a} = obj1;
        const {b} = obj2;
        a + b
        """

        # When
        result = execute(source)

        # Then
        assert result == 3

    def test_destructuring_with_existing_properties(self):
        """
        Given destructuring with computed expressions
        When executed
        Then properties are extracted and used correctly
        """
        # Given
        source = """
        const obj = {value: 100};
        const {value} = obj;
        value * 2
        """

        # When
        result = execute(source)

        # Then
        assert result == 200
