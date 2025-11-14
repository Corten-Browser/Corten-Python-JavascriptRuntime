"""
Integration tests for complete JavaScript parsing workflows.

Tests verify that the parser can handle realistic JavaScript programs
end-to-end, from source code to complete AST trees.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src import (
    Parse,
    Program,
    VariableDeclaration,
    FunctionDeclaration,
    IfStatement,
    WhileStatement,
)


def test_parse_complete_function_with_logic():
    """
    Given a complete function with logic
    When parsing
    Then entire function structure should be in AST
    """
    source = """
        function factorial(n) {
            if (n == 0) {
                return 1;
            }
            return n * factorial(n - 1);
        }
    """

    ast = Parse(source, "factorial.js")

    assert isinstance(ast, Program)
    assert len(ast.body) == 1

    func = ast.body[0]
    assert isinstance(func, FunctionDeclaration)
    assert func.name == "factorial"
    assert func.parameters == ["n"]

    # Function body should have if statement
    assert len(func.body.body) == 2
    assert isinstance(func.body.body[0], IfStatement)


def test_parse_multiple_functions():
    """
    Given multiple function definitions
    When parsing
    Then all functions should be in AST
    """
    source = """
        function add(a, b) {
            return a + b;
        }

        function subtract(a, b) {
            return a - b;
        }

        function multiply(a, b) {
            return a * b;
        }
    """

    ast = Parse(source, "math.js")

    assert len(ast.body) == 3
    assert all(isinstance(f, FunctionDeclaration) for f in ast.body)
    assert ast.body[0].name == "add"
    assert ast.body[1].name == "subtract"
    assert ast.body[2].name == "multiply"


def test_parse_fibonacci_function():
    """
    Given fibonacci function implementation
    When parsing
    Then complete AST should be produced
    """
    source = """
        function fibonacci(n) {
            if (n < 2) {
                return n;
            }
            return fibonacci(n - 1) + fibonacci(n - 2);
        }
    """

    ast = Parse(source, "fib.js")

    func = ast.body[0]
    assert func.name == "fibonacci"
    assert len(func.body.body) == 2


def test_parse_calculator_program():
    """
    Given a simple calculator program
    When parsing
    Then complete program structure should be parsed
    """
    source = """
        var x = 10;
        var y = 5;

        function calculate() {
            var sum = x + y;
            var difference = x - y;
            var product = x * y;
            var quotient = x / y;

            return sum;
        }

        var result = calculate();
    """

    ast = Parse(source, "calculator.js")

    assert len(ast.body) == 4  # 2 vars, 1 function, 1 var

    # Variables
    assert isinstance(ast.body[0], VariableDeclaration)
    assert isinstance(ast.body[1], VariableDeclaration)

    # Function
    assert isinstance(ast.body[2], FunctionDeclaration)
    assert ast.body[2].name == "calculate"

    # Result variable
    assert isinstance(ast.body[3], VariableDeclaration)


def test_parse_counter_with_loop():
    """
    Given code with while loop
    When parsing
    Then loop structure should be in AST
    """
    source = """
        function count(n) {
            var i = 0;
            while (i < n) {
                i = i + 1;
            }
            return i;
        }
    """

    ast = Parse(source, "counter.js")

    func = ast.body[0]
    assert len(func.body.body) == 3  # var, while, return

    while_stmt = func.body.body[1]
    assert isinstance(while_stmt, WhileStatement)


def test_parse_nested_control_flow():
    """
    Given code with nested if/else
    When parsing
    Then nested structure should be preserved
    """
    source = """
        function classify(x) {
            if (x > 0) {
                if (x > 10) {
                    return "large";
                } else {
                    return "small";
                }
            } else {
                return "negative";
            }
        }
    """

    ast = Parse(source, "classify.js")

    func = ast.body[0]
    outer_if = func.body.body[0]

    assert isinstance(outer_if, IfStatement)
    assert isinstance(outer_if.consequent.body[0], IfStatement)


def test_parse_complex_expressions():
    """
    Given code with complex expressions
    When parsing
    Then expression structure should be correct
    """
    source = """
        var result = (a + b) * (c - d);
        var comparison = x > 5 == y < 10;
        var call_result = add(multiply(2, 3), subtract(8, 3));
    """

    ast = Parse(source, "complex.js")

    assert len(ast.body) == 3
    assert all(isinstance(stmt, VariableDeclaration) for stmt in ast.body)


def test_parse_object_property_access():
    """
    Given code with property access
    When parsing
    Then member expressions should be in AST
    """
    source = """
        var name = person.name;
        var value = obj.prop.nested;
        var item = array[0];
    """

    ast = Parse(source, "access.js")

    assert len(ast.body) == 3


def test_parse_function_calls():
    """
    Given code with various function calls
    When parsing
    Then call expressions should be in AST
    """
    source = """
        print("hello");
        var result = calculate(x, y);
        obj.method(arg1, arg2);
        func()();
    """

    ast = Parse(source, "calls.js")

    assert len(ast.body) == 4


def test_parse_realistic_program():
    """
    Given a realistic JavaScript program
    When parsing
    Then complete program should be parsed correctly
    """
    source = """
        // Greeting function
        function greet(name) {
            var message = "Hello, " + name;
            return message;
        }

        // Main program
        var userName = "World";
        var greeting = greet(userName);

        // Conditional logic
        if (greeting) {
            var result = greeting;
        } else {
            var result = "Error";
        }
    """

    ast = Parse(source, "greeting.js")

    assert isinstance(ast, Program)
    # Should have: function, 2 vars, if statement
    assert len(ast.body) == 4


def test_parse_preserves_source_locations():
    """
    Given JavaScript source with multiple lines
    When parsing
    Then source locations should be accurate
    """
    source = """var x = 5;
function test() {
    return x;
}"""

    ast = Parse(source, "locations.js")

    # First statement on line 1
    assert ast.body[0].location.line == 1

    # Second statement on line 2
    assert ast.body[1].location.line == 2


def test_parse_empty_function():
    """
    Given a function with empty body
    When parsing
    Then function should be parsed successfully
    """
    source = "function empty() { }"

    ast = Parse(source, "empty.js")

    func = ast.body[0]
    assert func.name == "empty"
    assert len(func.body.body) == 0


def test_parse_multiple_statements_in_block():
    """
    Given a block with multiple statements
    When parsing
    Then all statements should be in AST
    """
    source = """
        {
            var a = 1;
            var b = 2;
            var c = 3;
        }
    """

    ast = Parse(source, "block.js")

    block = ast.body[0]
    assert len(block.body) == 3
