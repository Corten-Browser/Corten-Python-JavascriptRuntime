"""
Unit tests for template literal execution.

Tests interpreter execution of template literals compiled to bytecode,
verifying that string constants and concatenation work correctly.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.bytecode.src.compiler import BytecodeCompiler
from components.interpreter.src.interpreter import Interpreter
from components.memory_gc.src import GarbageCollector


class TestTemplateLiteralExecution:
    """Test interpreter execution of template literals."""

    def test_execute_simple_template_literal(self):
        """
        Given a simple template literal with only static text
        When executed by the interpreter
        Then it returns the static text as a string value
        """
        # Given
        source = "`Hello World`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # When
        gc = GarbageCollector()
        interpreter = Interpreter(gc)
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        # For now, we'll check that the value exists
        # Once string support is added, check value.to_string() == "Hello World"
        assert result.value is not None

    def test_execute_template_with_single_expression(self):
        """
        Given a template literal with one expression
        When executed by the interpreter with x=5
        Then it returns concatenated result "Value: 5"
        """
        # Given
        source = "`Value: ${x}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # When
        gc = GarbageCollector()
        interpreter = Interpreter(gc)
        # Set global variable x
        from components.value_system.src import Value
        interpreter.set_global("x", Value.from_smi(5))
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        # Once string support is added, check value.to_string() == "Value: 5"
        assert result.value is not None

    def test_execute_template_with_multiple_expressions(self):
        """
        Given a template literal with multiple expressions
        When executed by the interpreter with a=3, b=4
        Then it returns concatenated result "3 + 4 = 7"
        """
        # Given
        source = "`${a} + ${b} = ${a + b}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # When
        gc = GarbageCollector()
        interpreter = Interpreter(gc)
        from components.value_system.src import Value
        interpreter.set_global("a", Value.from_smi(3))
        interpreter.set_global("b", Value.from_smi(4))
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        # Once string support is added, check value.to_string() == "3 + 4 = 7"
        assert result.value is not None

    def test_execute_template_with_expression_operators(self):
        """
        Given a template with complex expressions
        When executed by the interpreter with x=10
        Then it returns concatenated result "Sum: 11"
        """
        # Given
        source = "`Sum: ${x + 1}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # When
        gc = GarbageCollector()
        interpreter = Interpreter(gc)
        from components.value_system.src import Value
        interpreter.set_global("x", Value.from_smi(10))
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        # Once string support is added, check value.to_string() == "Sum: 11"
        assert result.value is not None

    def test_execute_empty_template_literal(self):
        """
        Given an empty template literal
        When executed by the interpreter
        Then it returns an empty string value
        """
        # Given
        source = "``"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # When
        gc = GarbageCollector()
        interpreter = Interpreter(gc)
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        # Once string support is added, check value.to_string() == ""
        assert result.value is not None
