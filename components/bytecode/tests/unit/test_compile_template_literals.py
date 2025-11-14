"""
Unit tests for template literal compilation.

Tests bytecode compilation of template literals, ensuring they are
compiled to efficient string concatenation operations.
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
from components.bytecode.src.opcode import Opcode


class TestTemplateLiteralCompilation:
    """Test bytecode generation for template literals."""

    def test_compile_simple_template_literal(self):
        """
        Given a simple template literal with only static text
        When compiled to bytecode
        Then it generates a LOAD_CONSTANT instruction
        """
        # Given
        source = "`Hello World`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()

        # When
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # Then - should load the constant string
        instructions = bytecode.instructions
        assert len(instructions) >= 1
        assert instructions[0].opcode == Opcode.LOAD_CONSTANT
        # Check constant pool index and value
        const_index = instructions[0].operand1
        assert const_index is not None
        assert bytecode.constant_pool[const_index] == "Hello World"

    def test_compile_template_with_single_expression(self):
        """
        Given a template literal with one expression
        When compiled to bytecode
        Then it generates LOAD_CONSTANT for static parts and ADD for concatenation
        """
        # Given
        source = "`Value: ${x}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()

        # When
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # Then - should have loads and adds
        instructions = bytecode.instructions
        opcodes = [instr.opcode for instr in instructions]

        # Should contain LOAD_CONSTANT for "Value: ", LOAD_GLOBAL for x, ADD
        assert Opcode.LOAD_CONSTANT in opcodes  # "Value: "
        assert Opcode.LOAD_GLOBAL in opcodes  # x
        assert Opcode.ADD in opcodes  # concatenation

    def test_compile_template_with_multiple_expressions(self):
        """
        Given a template literal with multiple expressions
        When compiled to bytecode
        Then it generates sequential concatenation operations
        """
        # Given
        source = "`${a} + ${b} = ${a + b}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()

        # When
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # Then - should have multiple ADDs for concatenation
        instructions = bytecode.instructions
        opcodes = [instr.opcode for instr in instructions]

        # Count ADDs - should have at least 3 for concatenating 4 parts
        add_count = opcodes.count(Opcode.ADD)
        assert add_count >= 3

    def test_compile_template_with_expression_operators(self):
        """
        Given a template with complex expressions
        When compiled to bytecode
        Then expressions are compiled correctly before concatenation
        """
        # Given
        source = "`Sum: ${x + 1}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()

        # When
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # Then - should compile the expression and concatenate
        instructions = bytecode.instructions
        opcodes = [instr.opcode for instr in instructions]

        # Should have LOAD for x, LOAD for 1, ADD for x+1, then ADD for concatenation
        assert opcodes.count(Opcode.ADD) >= 2  # At least one for expr, one for concat

    def test_compile_empty_template_literal(self):
        """
        Given an empty template literal
        When compiled to bytecode
        Then it generates LOAD_CONSTANT with empty string
        """
        # Given
        source = "``"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)
        ast = parser.parse()

        # When
        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        # Then - should load empty string
        instructions = bytecode.instructions
        assert len(instructions) >= 1
        assert instructions[0].opcode == Opcode.LOAD_CONSTANT
        # Check constant pool index and value
        const_index = instructions[0].operand1
        assert const_index is not None
        assert bytecode.constant_pool[const_index] == ""
