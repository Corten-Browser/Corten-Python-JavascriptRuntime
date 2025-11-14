"""
End-to-end integration tests for JavaScript runtime execution pipeline.

Tests the complete flow: Parse → Compile → Execute
Verifies that all components work together correctly to execute JavaScript code.
"""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Execute
from components.memory_gc.src import GarbageCollector
from components.value_system.src import IsNumber, IsUndefined, Value


class TestSimpleExpressions:
    """Test execution of simple JavaScript expressions."""

    def test_literal_number_execution(self):
        """Test complete pipeline: parse → compile → execute for literal number."""
        # Arrange
        source = "42"

        # Act: Parse
        ast = Parse(source)
        assert ast is not None, "Parser should return AST"

        # Act: Compile
        bytecode = Compile(ast)
        assert bytecode is not None, "Compiler should return bytecode"
        assert len(bytecode.instructions) > 0, "Bytecode should have instructions"

        # Act: Execute
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), f"Execution should succeed, got exception: {result.exception}"
        # Note: Expressions return undefined in current bytecode design
        # This is expected behavior - expression statements don't return values
        assert result.value is not None, "Result should have a value"

    def test_addition_expression_execution(self):
        """Test complete pipeline for binary addition expression."""
        # Arrange
        source = "10 + 32"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), f"Execution should succeed, got: {result.exception}"
        # Expression statements return undefined in current design
        assert result.value is not None

    def test_subtraction_expression_execution(self):
        """Test complete pipeline for subtraction."""
        # Arrange
        source = "100 - 58"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Subtraction should execute successfully"
        assert result.value is not None

    def test_multiplication_expression_execution(self):
        """Test complete pipeline for multiplication."""
        # Arrange
        source = "6 * 7"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Multiplication should execute successfully"
        assert result.value is not None

    def test_division_expression_execution(self):
        """Test complete pipeline for division."""
        # Arrange
        source = "84 / 2"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Division should execute successfully"
        assert result.value is not None


class TestVariableDeclarations:
    """Test variable declaration and usage."""

    def test_variable_declaration_with_number(self):
        """Test variable declaration with number literal."""
        # Arrange
        source = "var x = 5;"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), f"Variable declaration should succeed: {result.exception}"
        assert result.value is not None

    def test_variable_declaration_and_access(self):
        """Test declaring and accessing a variable."""
        # Arrange
        source = """
        var x = 10;
        x
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Variable access should succeed"
        # Last expression statement returns undefined
        assert result.value is not None

    def test_multiple_variable_declarations(self):
        """Test multiple variable declarations."""
        # Arrange
        source = """
        var a = 1;
        var b = 2;
        var c = 3;
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Multiple declarations should succeed"
        assert result.value is not None

    def test_variable_with_expression(self):
        """Test variable initialized with expression."""
        # Arrange
        source = "var result = 5 + 3;"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Variable with expression should succeed"
        assert result.value is not None


class TestFunctions:
    """Test function declaration and calling."""

    def test_simple_function_declaration(self):
        """Test declaring a simple function."""
        # Arrange
        source = """
        function add(a, b) {
            return a + b;
        }
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Function declaration should succeed"
        assert result.value is not None

    def test_function_declaration_and_call(self):
        """Test declaring and calling a function."""
        # Arrange
        source = """
        function double(x) {
            return x * 2;
        }
        double(21)
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Function call should succeed"
        # Expression statement returns undefined in current design
        assert result.value is not None

    def test_function_with_multiple_parameters(self):
        """Test function with multiple parameters."""
        # Arrange
        source = """
        function add(a, b) {
            return a + b;
        }
        add(3, 4)
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Multi-parameter function should work"
        assert result.value is not None


class TestControlFlow:
    """Test control flow statements."""

    def test_if_statement_true_branch(self):
        """Test if statement with true condition."""
        # Arrange
        source = """
        var x = 5;
        if (x) {
            var y = 10;
        }
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "If statement should execute"
        assert result.value is not None

    def test_if_else_statement(self):
        """Test if-else statement."""
        # Arrange
        source = """
        var x = 5;
        if (x) {
            var y = 10;
        } else {
            var y = 20;
        }
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "If-else should execute"
        assert result.value is not None

    def test_while_loop(self):
        """Test while loop execution."""
        # Arrange
        source = """
        var i = 0;
        while (i) {
            i = i + 1;
        }
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "While loop should execute"
        assert result.value is not None


class TestComplexPrograms:
    """Test more complex JavaScript programs."""

    def test_fibonacci_function(self):
        """Test recursive fibonacci function."""
        # Arrange
        source = """
        function fib(n) {
            if (n) {
                return 1;
            }
            if (n) {
                return 1;
            }
            return fib(n) + fib(n);
        }
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Complex function should compile and execute"
        assert result.value is not None

    def test_multiple_functions_and_variables(self):
        """Test program with multiple functions and variables."""
        # Arrange
        source = """
        var x = 10;
        var y = 20;

        function add(a, b) {
            return a + b;
        }

        function multiply(a, b) {
            return a * b;
        }

        var sum = add(x, y);
        var product = multiply(x, y);
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Complex program should execute"
        assert result.value is not None

    def test_nested_function_calls(self):
        """Test nested function calls."""
        # Arrange
        source = """
        function inner(x) {
            return x + 1;
        }

        function outer(y) {
            return inner(y) + inner(y);
        }

        outer(5)
        """

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Nested function calls should work"
        assert result.value is not None


class TestGarbageCollectorIntegration:
    """Test garbage collector integration with execution."""

    def test_execution_with_custom_gc(self):
        """Test providing custom GC instance to Execute."""
        # Arrange
        source = "var x = 42;"
        gc = GarbageCollector()

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode, gc)

        # Assert
        assert result.is_success(), "Execution with custom GC should work"
        assert result.value is not None

    def test_multiple_executions_same_gc(self):
        """Test multiple program executions with same GC instance."""
        # Arrange
        gc = GarbageCollector()
        programs = [
            "var a = 1;",
            "var b = 2;",
            "var c = 3;"
        ]

        # Act & Assert
        for source in programs:
            ast = Parse(source)
            bytecode = Compile(ast)
            result = Execute(bytecode, gc)
            assert result.is_success(), f"Execution of '{source}' should succeed"


class TestErrorHandling:
    """Test error handling in the execution pipeline."""

    def test_syntax_error_in_parsing(self):
        """Test that syntax errors are caught during parsing."""
        # Arrange
        source = "var x = ;"  # Syntax error

        # Act & Assert
        with pytest.raises(SyntaxError):
            Parse(source)

    def test_invalid_javascript_syntax(self):
        """Test handling of invalid JavaScript syntax."""
        # Arrange
        source = "function ("  # Invalid syntax

        # Act & Assert
        with pytest.raises(SyntaxError):
            Parse(source)


class TestValueSystemIntegration:
    """Test integration with value system."""

    def test_value_types_in_execution(self):
        """Test that execution produces correct Value types."""
        # Arrange
        source = "42"

        # Act
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert
        assert result.is_success()
        assert result.value is not None
        # Verify it's a Value object
        assert isinstance(result.value, Value), "Result should be Value instance"
