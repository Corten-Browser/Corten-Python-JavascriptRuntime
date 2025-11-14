"""
Tests for compiling new expressions to bytecode.

Tests the compilation of 'new Constructor(args)' expressions.
"""

import pytest
from components.bytecode.src import Compile
from components.bytecode.src.opcode import Opcode
from components.parser.src import Parse


class TestNewExpressionCompilation:
    """Test compilation of new expressions."""

    def test_compile_new_no_args(self):
        """
        Given a new expression with no arguments
        When compiling 'new Promise()'
        Then bytecode should have LOAD_GLOBAL and NEW opcodes
        And NEW opcode should have operand1 = 0 (zero arguments)
        """
        # Given
        source = "new Promise()"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.LOAD_GLOBAL in opcodes, "Should load Promise constructor"
        assert Opcode.NEW in opcodes, "Should have NEW opcode"

        # Find NEW instruction and check argument count
        new_instr = [
            instr for instr in bytecode.instructions if instr.opcode == Opcode.NEW
        ][0]
        assert new_instr.operand1 == 0, "NEW should have 0 arguments"

    def test_compile_new_with_one_arg(self):
        """
        Given a new expression with one argument
        When compiling 'new Promise(executor)'
        Then bytecode should load constructor, load argument, then NEW with count 1
        """
        # Given
        source = "new Promise(executor)"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.LOAD_GLOBAL in opcodes, "Should load Promise constructor"
        assert Opcode.NEW in opcodes, "Should have NEW opcode"

        # Find NEW instruction and check argument count
        new_instr = [
            instr for instr in bytecode.instructions if instr.opcode == Opcode.NEW
        ][0]
        assert new_instr.operand1 == 1, "NEW should have 1 argument"

    def test_compile_new_with_arrow_function(self):
        """
        Given a new expression with arrow function argument
        When compiling 'new Promise((resolve, reject) => {})'
        Then bytecode should create closure and pass to NEW
        """
        # Given
        source = "new Promise((resolve, reject) => {})"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.LOAD_GLOBAL in opcodes, "Should load Promise constructor"
        assert (
            Opcode.CREATE_CLOSURE in opcodes
        ), "Should create closure for arrow function"
        assert Opcode.NEW in opcodes, "Should have NEW opcode"

        # NEW should follow CREATE_CLOSURE
        new_instr = [
            instr for instr in bytecode.instructions if instr.opcode == Opcode.NEW
        ][0]
        assert new_instr.operand1 == 1, "NEW should have 1 argument (the closure)"

    def test_compile_new_with_multiple_args(self):
        """
        Given a new expression with multiple arguments
        When compiling 'new Array(1, 2, 3)'
        Then NEW opcode should have operand1 = 3
        """
        # Given
        source = "new Array(1, 2, 3)"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.LOAD_GLOBAL in opcodes, "Should load Array constructor"
        assert Opcode.NEW in opcodes, "Should have NEW opcode"

        # Check we load 3 constants
        load_constant_count = sum(
            1 for instr in bytecode.instructions if instr.opcode == Opcode.LOAD_CONSTANT
        )
        assert load_constant_count >= 3, "Should load 3 literal arguments"

        # Find NEW instruction and check argument count
        new_instr = [
            instr for instr in bytecode.instructions if instr.opcode == Opcode.NEW
        ][0]
        assert new_instr.operand1 == 3, "NEW should have 3 arguments"

    def test_compile_new_in_assignment(self):
        """
        Given a variable declaration with new expression
        When compiling 'const p = new Promise(executor)'
        Then bytecode should compile new expression and store result
        """
        # Given
        source = "const p = new Promise(executor)"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.NEW in opcodes, "Should have NEW opcode"
        assert (
            Opcode.STORE_LOCAL in opcodes or Opcode.STORE_GLOBAL in opcodes
        ), "Should store result of new expression"

    def test_compile_new_bytecode_order(self):
        """
        Given a new expression with arguments
        When compiling to bytecode
        Then instructions should be in correct order:
            1. Load constructor
            2. Load all arguments (in order)
            3. NEW with argument count
        """
        # Given
        source = "new Promise(executor)"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        instructions = bytecode.instructions

        # Find indices of key opcodes
        load_global_idx = None
        new_idx = None

        for i, instr in enumerate(instructions):
            if instr.opcode == Opcode.LOAD_GLOBAL and load_global_idx is None:
                load_global_idx = i
            elif instr.opcode == Opcode.NEW:
                new_idx = i

        assert load_global_idx is not None, "Should have LOAD_GLOBAL"
        assert new_idx is not None, "Should have NEW"
        assert load_global_idx < new_idx, "LOAD_GLOBAL should come before NEW"

    def test_compile_new_with_call_expression_arg(self):
        """
        Given a new expression with call expression as argument
        When compiling 'new Promise(getExecutor())'
        Then bytecode should compile the call expression before NEW
        """
        # Given
        source = "new Promise(getExecutor())"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.LOAD_GLOBAL in opcodes, "Should load Promise constructor"
        assert Opcode.CALL_FUNCTION in opcodes, "Should call getExecutor()"
        assert Opcode.NEW in opcodes, "Should have NEW opcode"

        # NEW should have 1 argument (result of getExecutor())
        new_instr = [
            instr for instr in bytecode.instructions if instr.opcode == Opcode.NEW
        ][0]
        assert new_instr.operand1 == 1, "NEW should have 1 argument"

    def test_new_expression_integrated_with_parser(self):
        """
        Integration test: verify parser and compiler work together
        When parsing and compiling 'new Promise(executor)'
        Then should produce valid bytecode without errors
        """
        # Given
        source = "new Promise(executor)"

        # When
        ast = Parse(source)
        bytecode = Compile(ast)

        # Then
        assert bytecode is not None
        assert len(bytecode.instructions) > 0
        assert Opcode.NEW in [instr.opcode for instr in bytecode.instructions]
