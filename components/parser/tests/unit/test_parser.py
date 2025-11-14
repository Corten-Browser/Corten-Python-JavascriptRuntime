"""
Unit tests for Parser class.

Tests verify recursive descent parsing of JavaScript source code
into Abstract Syntax Trees (AST), including expressions, statements,
and complete programs.
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


def test_parser_creation():
    """
    Given a lexer
    When creating a Parser
    Then it should initialize successfully
    """
    lexer = Lexer("var x = 5;", "test.js")
    parser = Parser(lexer)
    assert parser is not None


def test_parse_simple_var_declaration():
    """
    Given a simple var declaration
    When parsing
    Then correct AST should be produced
    """
    program = parse("var x = 5;")

    assert isinstance(program, Program)
    assert len(program.body) == 1
    assert isinstance(program.body[0], VariableDeclaration)

    var_decl = program.body[0]
    assert len(var_decl.declarations) == 1
    assert var_decl.declarations[0].name == "x"
    assert isinstance(var_decl.declarations[0].init, Literal)
    assert var_decl.declarations[0].init.value == 5


def test_parse_multiple_var_declarations():
    """
    Given multiple variable declarations
    When parsing
    Then all declarations should be in AST
    """
    program = parse("var x = 5, y = 10;")

    var_decl = program.body[0]
    assert len(var_decl.declarations) == 2
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init.value == 5
    assert var_decl.declarations[1].name == "y"
    assert var_decl.declarations[1].init.value == 10


def test_parse_var_without_initializer():
    """
    Given a var declaration without initializer
    When parsing
    Then init should be None
    """
    program = parse("var x;")

    var_decl = program.body[0]
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init is None


def test_parse_literal_expressions():
    """
    Given literal values
    When parsing
    Then correct literal nodes should be created
    """
    # Number
    program = parse("42;")
    assert isinstance(program.body[0], ExpressionStatement)
    assert isinstance(program.body[0].expression, Literal)
    assert program.body[0].expression.value == 42

    # String
    program = parse('"hello";')
    assert program.body[0].expression.value == "hello"

    # Boolean
    program = parse("true;")
    assert isinstance(program.body[0].expression, Literal)

    program = parse("false;")
    assert isinstance(program.body[0].expression, Literal)

    # Null
    program = parse("null;")
    assert isinstance(program.body[0].expression, Literal)

    # Undefined
    program = parse("undefined;")
    assert isinstance(program.body[0].expression, Literal)


def test_parse_identifier_expression():
    """
    Given an identifier
    When parsing
    Then an Identifier node should be created
    """
    program = parse("myVariable;")

    expr_stmt = program.body[0]
    assert isinstance(expr_stmt.expression, Identifier)
    assert expr_stmt.expression.name == "myVariable"


def test_parse_binary_expression():
    """
    Given a binary expression
    When parsing
    Then correct BinaryExpression should be created
    """
    program = parse("a + b;")

    expr = program.body[0].expression
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "+"
    assert isinstance(expr.left, Identifier)
    assert expr.left.name == "a"
    assert isinstance(expr.right, Identifier)
    assert expr.right.name == "b"


def test_parse_binary_expression_with_numbers():
    """
    Given arithmetic with numbers
    When parsing
    Then correct AST should be produced
    """
    program = parse("5 + 10;")

    expr = program.body[0].expression
    assert expr.operator == "+"
    assert expr.left.value == 5
    assert expr.right.value == 10


def test_parse_multiple_binary_operators():
    """
    Given expressions with multiple operators
    When parsing
    Then they should be parsed with left-to-right associativity
    """
    # a + b - c should parse as ((a + b) - c)
    program = parse("a + b - c;")

    expr = program.body[0].expression
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "-"
    assert isinstance(expr.left, BinaryExpression)
    assert expr.left.operator == "+"


def test_parse_call_expression():
    """
    Given a function call
    When parsing
    Then CallExpression should be created
    """
    program = parse("add(1, 2);")

    expr = program.body[0].expression
    assert isinstance(expr, CallExpression)
    assert isinstance(expr.callee, Identifier)
    assert expr.callee.name == "add"
    assert len(expr.arguments) == 2
    assert expr.arguments[0].value == 1
    assert expr.arguments[1].value == 2


def test_parse_call_expression_no_args():
    """
    Given a function call with no arguments
    When parsing
    Then empty arguments list should be created
    """
    program = parse("foo();")

    expr = program.body[0].expression
    assert isinstance(expr, CallExpression)
    assert len(expr.arguments) == 0


def test_parse_member_expression_dot():
    """
    Given dot notation property access
    When parsing
    Then MemberExpression with computed=False should be created
    """
    program = parse("obj.property;")

    expr = program.body[0].expression
    assert isinstance(expr, MemberExpression)
    assert isinstance(expr.object, Identifier)
    assert expr.object.name == "obj"
    assert isinstance(expr.property, Identifier)
    assert expr.property.name == "property"
    assert expr.computed is False


def test_parse_member_expression_bracket():
    """
    Given bracket notation property access
    When parsing
    Then MemberExpression with computed=True should be created
    """
    program = parse("obj[key];")

    expr = program.body[0].expression
    assert isinstance(expr, MemberExpression)
    assert expr.computed is True


def test_parse_function_declaration():
    """
    Given a function declaration
    When parsing
    Then FunctionDeclaration should be created
    """
    program = parse("function add(a, b) { return a + b; }")

    func_decl = program.body[0]
    assert isinstance(func_decl, FunctionDeclaration)
    assert func_decl.name == "add"
    assert func_decl.parameters == ["a", "b"]
    assert isinstance(func_decl.body, BlockStatement)
    assert len(func_decl.body.body) == 1


def test_parse_function_no_params():
    """
    Given a function with no parameters
    When parsing
    Then empty parameters list should be created
    """
    program = parse("function foo() { }")

    func_decl = program.body[0]
    assert func_decl.name == "foo"
    assert len(func_decl.parameters) == 0


def test_parse_return_statement():
    """
    Given a return statement
    When parsing
    Then ReturnStatement should be created
    """
    program = parse("function foo() { return 42; }")

    func_decl = program.body[0]
    return_stmt = func_decl.body.body[0]
    assert isinstance(return_stmt, ReturnStatement)
    assert isinstance(return_stmt.argument, Literal)
    assert return_stmt.argument.value == 42


def test_parse_bare_return():
    """
    Given a return with no value
    When parsing
    Then argument should be None
    """
    program = parse("function foo() { return; }")

    return_stmt = program.body[0].body.body[0]
    assert isinstance(return_stmt, ReturnStatement)
    assert return_stmt.argument is None


def test_parse_if_statement():
    """
    Given an if statement
    When parsing
    Then IfStatement should be created
    """
    program = parse("if (x > 0) { return x; }")

    if_stmt = program.body[0]
    assert isinstance(if_stmt, IfStatement)
    assert isinstance(if_stmt.test, BinaryExpression)
    assert isinstance(if_stmt.consequent, BlockStatement)
    assert if_stmt.alternate is None


def test_parse_if_else_statement():
    """
    Given an if/else statement
    When parsing
    Then both branches should be in AST
    """
    program = parse("if (x > 0) { return x; } else { return 0; }")

    if_stmt = program.body[0]
    assert isinstance(if_stmt.consequent, BlockStatement)
    assert isinstance(if_stmt.alternate, BlockStatement)


def test_parse_while_statement():
    """
    Given a while loop
    When parsing
    Then WhileStatement should be created
    """
    program = parse("while (i < 10) { i = i + 1; }")

    while_stmt = program.body[0]
    assert isinstance(while_stmt, WhileStatement)
    assert isinstance(while_stmt.test, BinaryExpression)
    assert isinstance(while_stmt.body, BlockStatement)


def test_parse_block_statement():
    """
    Given a block statement
    When parsing
    Then all statements in block should be parsed
    """
    program = parse("{ var x = 1; var y = 2; }")

    block = program.body[0]
    assert isinstance(block, BlockStatement)
    assert len(block.body) == 2
    assert isinstance(block.body[0], VariableDeclaration)
    assert isinstance(block.body[1], VariableDeclaration)


def test_parse_empty_program():
    """
    Given empty source
    When parsing
    Then empty Program should be created
    """
    program = parse("")

    assert isinstance(program, Program)
    assert len(program.body) == 0


def test_parse_multiple_statements():
    """
    Given multiple top-level statements
    When parsing
    Then all should be in Program body
    """
    source = """
        var x = 5;
        var y = 10;
        function add(a, b) { return a + b; }
    """
    program = parse(source)

    assert len(program.body) == 3
    assert isinstance(program.body[0], VariableDeclaration)
    assert isinstance(program.body[1], VariableDeclaration)
    assert isinstance(program.body[2], FunctionDeclaration)


def test_parse_comparison_operators():
    """
    Given comparison operators
    When parsing
    Then correct operators should be in AST
    """
    program = parse("a == b;")
    assert program.body[0].expression.operator == "=="

    program = parse("a != b;")
    assert program.body[0].expression.operator == "!="

    program = parse("a < b;")
    assert program.body[0].expression.operator == "<"

    program = parse("a > b;")
    assert program.body[0].expression.operator == ">"


def test_parse_assignment():
    """
    Given an assignment
    When parsing
    Then assignment should be in AST
    """
    program = parse("x = 5;")

    expr = program.body[0].expression
    assert isinstance(expr, BinaryExpression)
    assert expr.operator == "="


def test_parse_complex_expression():
    """
    Given a complex nested expression
    When parsing
    Then correct AST structure should be produced
    """
    program = parse("add(x + 1, y * 2);")

    call = program.body[0].expression
    assert isinstance(call, CallExpression)
    assert len(call.arguments) == 2

    # First argument: x + 1
    arg1 = call.arguments[0]
    assert isinstance(arg1, BinaryExpression)
    assert arg1.operator == "+"

    # Second argument: y * 2
    arg2 = call.arguments[1]
    assert isinstance(arg2, BinaryExpression)
    assert arg2.operator == "*"
