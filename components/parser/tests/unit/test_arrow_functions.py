"""
Unit tests for arrow function parsing.

Tests verify parsing of ES6 arrow function syntax including:
- Single parameter without parens: x => x * 2
- Single parameter with parens: (x) => x * 2
- Multiple parameters: (x, y) => x + y
- No parameters: () => 42
- Expression body (implicit return): x => x * 2
- Block body (explicit return): x => { return x * 2; }
- Nested arrow functions: x => y => x + y
- Arrow functions as callbacks: arr.map(x => x * 2)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import *


def parse(source: str) -> Program:
    """Helper to parse source code into AST."""
    lexer = Lexer(source, "test.js")
    parser = Parser(lexer)
    return parser.parse()


def test_parse_arrow_function_single_param_no_parens():
    """
    Given an arrow function with single parameter without parens
    When parsing 'x => x * 2'
    Then correct ArrowFunctionExpression AST should be produced
    """
    program = parse("x => x * 2;")

    assert isinstance(program, Program)
    assert len(program.body) == 1
    assert isinstance(program.body[0], ExpressionStatement)

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Check params: should have one Identifier param 'x'
    assert len(arrow.params) == 1
    assert isinstance(arrow.params[0], Identifier)
    assert arrow.params[0].name == "x"

    # Check body: should be BinaryExpression (x * 2) - expression body
    assert isinstance(arrow.body, BinaryExpression)
    assert arrow.body.operator == "*"
    assert isinstance(arrow.body.left, Identifier)
    assert arrow.body.left.name == "x"
    assert isinstance(arrow.body.right, Literal)
    assert arrow.body.right.value == 2

    # Check is_async
    assert arrow.is_async is False


def test_parse_arrow_function_single_param_with_parens():
    """
    Given an arrow function with single parameter with parens
    When parsing '(x) => x * 2'
    Then correct ArrowFunctionExpression AST should be produced
    """
    program = parse("(x) => x * 2;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Check params
    assert len(arrow.params) == 1
    assert arrow.params[0].name == "x"

    # Check body
    assert isinstance(arrow.body, BinaryExpression)
    assert arrow.body.operator == "*"


def test_parse_arrow_function_multiple_params():
    """
    Given an arrow function with multiple parameters
    When parsing '(x, y) => x + y'
    Then correct ArrowFunctionExpression with multiple params should be produced
    """
    program = parse("(x, y) => x + y;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Check params: should have two Identifier params
    assert len(arrow.params) == 2
    assert isinstance(arrow.params[0], Identifier)
    assert arrow.params[0].name == "x"
    assert isinstance(arrow.params[1], Identifier)
    assert arrow.params[1].name == "y"

    # Check body: should be BinaryExpression (x + y)
    assert isinstance(arrow.body, BinaryExpression)
    assert arrow.body.operator == "+"


def test_parse_arrow_function_no_params():
    """
    Given an arrow function with no parameters
    When parsing '() => 42'
    Then correct ArrowFunctionExpression with empty params should be produced
    """
    program = parse("() => 42;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Check params: should be empty list
    assert len(arrow.params) == 0

    # Check body: should be Literal 42
    assert isinstance(arrow.body, Literal)
    assert arrow.body.value == 42


def test_parse_arrow_function_expression_body():
    """
    Given an arrow function with expression body
    When parsing 'x => x * 2'
    Then body should be an Expression (implicit return)
    """
    program = parse("x => x * 2;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Expression body - should NOT be BlockStatement
    assert not isinstance(arrow.body, BlockStatement)
    assert isinstance(arrow.body, BinaryExpression)


def test_parse_arrow_function_block_body():
    """
    Given an arrow function with block body
    When parsing 'x => { return x * 2; }'
    Then body should be a BlockStatement (explicit return)
    """
    program = parse("x => { return x * 2; };")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Block body - should be BlockStatement
    assert isinstance(arrow.body, BlockStatement)
    assert len(arrow.body.body) == 1
    assert isinstance(arrow.body.body[0], ReturnStatement)
    assert isinstance(arrow.body.body[0].argument, BinaryExpression)


def test_parse_arrow_function_nested():
    """
    Given nested arrow functions (currying)
    When parsing 'x => y => x + y'
    Then outer arrow should have inner arrow as body
    """
    program = parse("x => y => x + y;")

    outer_arrow = program.body[0].expression
    assert isinstance(outer_arrow, ArrowFunctionExpression)
    assert len(outer_arrow.params) == 1
    assert outer_arrow.params[0].name == "x"

    # Body of outer arrow should be another arrow function
    inner_arrow = outer_arrow.body
    assert isinstance(inner_arrow, ArrowFunctionExpression)
    assert len(inner_arrow.params) == 1
    assert inner_arrow.params[0].name == "y"

    # Body of inner arrow should be x + y
    assert isinstance(inner_arrow.body, BinaryExpression)
    assert inner_arrow.body.operator == "+"


def test_parse_arrow_function_as_callback():
    """
    Given an arrow function used as callback
    When parsing 'arr.map(x => x * 2)'
    Then arrow function should be argument to map call
    """
    program = parse("arr.map(x => x * 2);")

    expr_stmt = program.body[0]
    assert isinstance(expr_stmt, ExpressionStatement)

    # Should be a call expression
    call = expr_stmt.expression
    assert isinstance(call, CallExpression)

    # Callee should be arr.map (MemberExpression)
    assert isinstance(call.callee, MemberExpression)

    # Argument should be arrow function
    assert len(call.arguments) == 1
    arrow = call.arguments[0]
    assert isinstance(arrow, ArrowFunctionExpression)
    assert len(arrow.params) == 1
    assert arrow.params[0].name == "x"


def test_parse_arrow_function_in_array():
    """
    Given an arrow function inside array literal
    When parsing '[x => x * 2, y => y + 1]'
    Then array should contain arrow function expressions
    """
    program = parse("[x => x * 2, y => y + 1];")

    expr_stmt = program.body[0]
    array = expr_stmt.expression
    assert isinstance(array, ArrayExpression)

    # Should have two arrow functions
    assert len(array.elements) == 2
    assert isinstance(array.elements[0], ArrowFunctionExpression)
    assert isinstance(array.elements[1], ArrowFunctionExpression)


def test_parse_arrow_function_vs_grouped_expression():
    """
    Given similar syntax that could be arrow function or grouped expression
    When parsing both '(x)' and '(x) => x'
    Then parser should correctly distinguish between them
    """
    # Grouped expression: (x) should parse as identifier in parens
    program1 = parse("(x);")
    assert isinstance(program1.body[0].expression, Identifier)
    assert program1.body[0].expression.name == "x"

    # Arrow function: (x) => x should parse as arrow function
    program2 = parse("(x) => x;")
    arrow = program2.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)
    assert len(arrow.params) == 1
    assert arrow.params[0].name == "x"


def test_parse_arrow_function_three_params():
    """
    Given an arrow function with three parameters
    When parsing '(a, b, c) => a + b + c'
    Then all three params should be in params list
    """
    program = parse("(a, b, c) => a + b + c;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)
    assert len(arrow.params) == 3
    assert arrow.params[0].name == "a"
    assert arrow.params[1].name == "b"
    assert arrow.params[2].name == "c"


def test_parse_arrow_function_complex_expression_body():
    """
    Given an arrow function with complex expression body
    When parsing 'x => x > 0 ? x : -x'
    Then expression should be preserved (will fail until ternary implemented)
    And for now test with 'x => x > 0'
    """
    # Simplified since ternary not implemented yet
    program = parse("x => x > 0;")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)
    assert isinstance(arrow.body, BinaryExpression)
    assert arrow.body.operator == ">"


def test_parse_arrow_function_in_var_assignment():
    """
    Given an arrow function assigned to variable
    When parsing 'var double = x => x * 2;'
    Then variable should be initialized with arrow function
    """
    program = parse("var double = x => x * 2;")

    var_decl = program.body[0]
    assert isinstance(var_decl, VariableDeclaration)

    # Init should be arrow function
    arrow = var_decl.declarations[0].init
    assert isinstance(arrow, ArrowFunctionExpression)
    assert len(arrow.params) == 1
    assert arrow.params[0].name == "x"


def test_parse_arrow_function_block_with_multiple_statements():
    """
    Given an arrow function with block body containing multiple statements
    When parsing 'x => { var y = x * 2; return y; }'
    Then block should contain both statements
    """
    program = parse("x => { var y = x * 2; return y; };")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)
    assert isinstance(arrow.body, BlockStatement)
    assert len(arrow.body.body) == 2
    assert isinstance(arrow.body.body[0], VariableDeclaration)
    assert isinstance(arrow.body.body[1], ReturnStatement)


def test_parse_arrow_function_empty_block_body():
    """
    Given an arrow function with empty block body
    When parsing '() => {}'
    Then block should be empty
    """
    program = parse("() => {};")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)
    assert isinstance(arrow.body, BlockStatement)
    assert len(arrow.body.body) == 0


def test_parse_arrow_function_object_literal_body():
    """
    Given an arrow function returning object literal
    When parsing 'x => ({value: x})'
    Then body should be object literal wrapped in parens
    """
    program = parse("x => ({value: x});")

    arrow = program.body[0].expression
    assert isinstance(arrow, ArrowFunctionExpression)

    # Body should be object literal (expression body)
    assert isinstance(arrow.body, ObjectExpression)
    assert len(arrow.body.properties) == 1
