"""
Unit tests for async/await bytecode compilation.

This module tests the bytecode compilation of async functions and await expressions.
Follows TDD approach: tests written first, then implementation.
"""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.bytecode.src.opcode import Opcode


class TestAsyncFunctionDeclarationCompilation:
    """Test compilation of async function declarations."""

    def test_compile_simple_async_function(self):
        """
        Given an async function declaration with no parameters
        When the function is compiled
        Then CREATE_ASYNC_FUNCTION and STORE_GLOBAL opcodes are generated
        """
        # Given
        source = "async function foo() {}"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes
        assert Opcode.STORE_GLOBAL in opcodes

    def test_compile_async_function_with_params(self):
        """
        Given an async function with parameters
        When the function is compiled
        Then CREATE_ASYNC_FUNCTION includes function bytecode with correct parameter count
        """
        # Given
        source = "async function add(a, b) { return a + b; }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

        # Find CREATE_ASYNC_FUNCTION instruction
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]

        # Check function bytecode
        func_bytecode = async_instr.operand2
        assert func_bytecode is not None
        assert func_bytecode.parameter_count == 2

    def test_compile_async_function_with_return(self):
        """
        Given an async function with a return statement
        When the function is compiled
        Then the function bytecode contains LOAD_CONSTANT and RETURN opcodes
        """
        # Given
        source = "async function foo() { return 42; }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2

        # Should have LOAD_CONSTANT, RETURN
        func_opcodes = [instr.opcode for instr in func_bytecode.instructions]
        assert Opcode.LOAD_CONSTANT in func_opcodes
        assert Opcode.RETURN in func_opcodes

    def test_compile_async_function_with_body(self):
        """
        Given an async function with multiple statements in body
        When the function is compiled
        Then all statements are compiled in the function bytecode
        """
        # Given
        source = """
        async function test() {
            const x = 10;
            const y = 20;
            return x + y;
        }
        """
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2

        # Should have variable declarations and return
        func_opcodes = [instr.opcode for instr in func_bytecode.instructions]
        assert Opcode.STORE_LOCAL in func_opcodes  # Variable declarations
        assert Opcode.RETURN in func_opcodes


class TestAsyncFunctionExpressionCompilation:
    """Test compilation of async function expressions."""

    def test_compile_async_function_expression(self):
        """
        Given an async function expression
        When the expression is compiled
        Then CREATE_ASYNC_FUNCTION opcode is generated
        """
        # Given
        source = "const f = async function() {}"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

    def test_compile_async_function_expression_with_name(self):
        """
        Given a named async function expression
        When the expression is compiled
        Then CREATE_ASYNC_FUNCTION opcode is generated
        """
        # Given
        source = "const f = async function foo() {}"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

    def test_compile_async_function_expression_with_params(self):
        """
        Given an async function expression with parameters
        When the expression is compiled
        Then function bytecode has correct parameter count
        """
        # Given
        source = "const f = async function(x, y) { return x + y; }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2
        assert func_bytecode.parameter_count == 2


class TestAsyncArrowFunctionCompilation:
    """Test compilation of async arrow functions."""

    def test_compile_async_arrow_no_params(self):
        """
        Given an async arrow function with no parameters
        When the function is compiled
        Then CREATE_ASYNC_FUNCTION opcode is generated
        """
        # Given
        source = "const f = async () => 42"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

    def test_compile_async_arrow_with_param(self):
        """
        Given an async arrow function with a parameter
        When the function is compiled
        Then CREATE_ASYNC_FUNCTION opcode is generated with correct parameter count
        """
        # Given
        source = "const f = async x => x * 2"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2
        assert func_bytecode.parameter_count == 1

    def test_compile_async_arrow_block_body(self):
        """
        Given an async arrow function with block body
        When the function is compiled
        Then function bytecode contains block statements
        """
        # Given
        source = "const f = async (x) => { return x * 2; }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2
        func_opcodes = [instr.opcode for instr in func_bytecode.instructions]
        assert Opcode.RETURN in func_opcodes

    def test_compile_async_arrow_expression_body(self):
        """
        Given an async arrow function with expression body
        When the function is compiled
        Then function bytecode contains implicit return
        """
        # Given
        source = "const f = async x => x * 2"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        func_bytecode = async_instr.operand2
        func_opcodes = [instr.opcode for instr in func_bytecode.instructions]

        # Expression body should have implicit return
        assert Opcode.RETURN in func_opcodes


class TestAwaitExpressionCompilation:
    """Test compilation of await expressions (basic support)."""

    def test_compile_simple_await(self):
        """
        Given an async function with a simple await expression
        When the function is compiled
        Then the bytecode compiles without errors
        """
        # Given
        source = "async function f() { await Promise.resolve(42); }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then - Should compile without errors (even if await not fully implemented yet)
        assert bytecode is not None
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

    def test_compile_await_in_variable(self):
        """
        Given an async function with await in variable assignment
        When the function is compiled
        Then the bytecode compiles without errors
        """
        # Given
        source = "async function f() { const x = await Promise.resolve(1); }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        assert bytecode is not None
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes

    def test_compile_await_in_return(self):
        """
        Given an async function with await in return statement
        When the function is compiled
        Then the bytecode compiles without errors
        """
        # Given
        source = "async function f() { return await Promise.resolve(42); }"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        assert bytecode is not None
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_ASYNC_FUNCTION in opcodes


class TestAsyncFunctionParameterCount:
    """Test that async functions preserve parameter information."""

    def test_async_function_zero_params(self):
        """
        Given an async function with zero parameters
        When compiled
        Then parameter_count is 0
        """
        # Given
        source = "async function f() {}"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        assert async_instr.operand2.parameter_count == 0

    def test_async_function_multiple_params(self):
        """
        Given an async function with multiple parameters
        When compiled
        Then parameter_count matches the number of parameters
        """
        # Given
        source = "async function f(a, b, c) {}"
        ast = Parse(source)

        # When
        bytecode = Compile(ast)

        # Then
        async_instr = [
            instr
            for instr in bytecode.instructions
            if instr.opcode == Opcode.CREATE_ASYNC_FUNCTION
        ][0]
        assert async_instr.operand2.parameter_count == 3
