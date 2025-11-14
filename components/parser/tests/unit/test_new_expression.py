"""
Tests for parsing new expressions.

Tests the parsing of 'new Constructor(args)' expressions for creating instances.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import (
    NewExpression,
    Identifier,
    ExpressionStatement,
    ArrowFunctionExpression,
    BlockStatement,
    CallExpression,
    Literal,
    VariableDeclaration,
    MemberExpression,
)


class TestNewExpression:
    """Test parsing of new expressions."""

    def test_parse_new_with_identifier(self):
        """
        Given a new expression with simple identifier constructor
        When parsing 'new Promise()'
        Then should create NewExpression with Identifier callee and empty arguments
        """
        # Given
        source = "new Promise()"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, NewExpression)
        assert isinstance(stmt.expression.callee, Identifier)
        assert stmt.expression.callee.name == "Promise"
        assert len(stmt.expression.arguments) == 0

    def test_parse_new_with_single_argument(self):
        """
        Given a new expression with one argument
        When parsing 'new Promise(executor)'
        Then should create NewExpression with one argument
        """
        # Given
        source = "new Promise(executor)"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        stmt = ast.body[0]
        expr = stmt.expression
        assert isinstance(expr, NewExpression)
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], Identifier)
        assert expr.arguments[0].name == "executor"

    def test_parse_new_with_multiple_arguments(self):
        """
        Given a new expression with multiple arguments
        When parsing 'new Promise(resolve, reject)'
        Then should create NewExpression with two arguments
        """
        # Given
        source = "new Promise(resolve, reject)"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        expr = ast.body[0].expression
        assert isinstance(expr, NewExpression)
        assert len(expr.arguments) == 2
        assert isinstance(expr.arguments[0], Identifier)
        assert expr.arguments[0].name == "resolve"
        assert isinstance(expr.arguments[1], Identifier)
        assert expr.arguments[1].name == "reject"

    def test_parse_new_with_arrow_function_argument(self):
        """
        Given a new expression with arrow function as argument
        When parsing 'new Promise((resolve, reject) => { resolve(42); })'
        Then should create NewExpression with arrow function argument
        """
        # Given
        source = "new Promise((resolve, reject) => { resolve(42); })"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        expr = ast.body[0].expression
        assert isinstance(expr, NewExpression)
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], ArrowFunctionExpression)

        # Check arrow function has two parameters
        arrow_fn = expr.arguments[0]
        assert len(arrow_fn.params) == 2
        assert isinstance(arrow_fn.params[0], Identifier)
        assert arrow_fn.params[0].name == "resolve"
        assert isinstance(arrow_fn.params[1], Identifier)
        assert arrow_fn.params[1].name == "reject"

        # Check arrow function body is a block statement
        assert isinstance(arrow_fn.body, BlockStatement)

    def test_parse_new_with_literal_arguments(self):
        """
        Given a new expression with literal arguments
        When parsing 'new Array(1, 2, 3)'
        Then should create NewExpression with literal arguments
        """
        # Given
        source = "new Array(1, 2, 3)"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        expr = ast.body[0].expression
        assert isinstance(expr, NewExpression)
        assert len(expr.arguments) == 3
        assert isinstance(expr.arguments[0], Literal)
        assert expr.arguments[0].value == 1
        assert isinstance(expr.arguments[1], Literal)
        assert expr.arguments[1].value == 2
        assert isinstance(expr.arguments[2], Literal)
        assert expr.arguments[2].value == 3

    def test_parse_new_in_variable_declaration(self):
        """
        Given a variable declaration with new expression
        When parsing 'const p = new Promise(executor)'
        Then should create variable declaration with NewExpression initializer
        """
        # Given
        source = "const p = new Promise(executor)"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        stmt = ast.body[0]
        assert isinstance(stmt, VariableDeclaration)
        assert stmt.kind == "const"
        assert len(stmt.declarations) == 1
        decl = stmt.declarations[0]
        assert decl.id == "p"
        assert isinstance(decl.init, NewExpression)
        assert isinstance(decl.init.callee, Identifier)
        assert decl.init.callee.name == "Promise"

    def test_parse_new_followed_by_method_call(self):
        """
        Given a new expression followed by method call
        When parsing 'new Promise(executor).then(handler)'
        Then should create member expression on new expression
        """
        # Given
        source = "new Promise(executor).then(handler)"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        expr = ast.body[0].expression
        # The entire expression should be a CallExpression
        # .then() is called on the result of new Promise()
        assert isinstance(expr, CallExpression)

        # The callee should be a MemberExpression (new Promise(...).then)
        assert isinstance(expr.callee, MemberExpression)

        # The object of the MemberExpression should be the NewExpression
        assert isinstance(expr.callee.object, NewExpression)
        assert expr.callee.object.callee.name == "Promise"

        # The property should be 'then'
        assert isinstance(expr.callee.property, Identifier)
        assert expr.callee.property.name == "then"

    def test_parse_new_with_nested_call_expression(self):
        """
        Given a new expression with call expression as argument
        When parsing 'new Promise(getExecutor())'
        Then should create NewExpression with CallExpression argument
        """
        # Given
        source = "new Promise(getExecutor())"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        expr = ast.body[0].expression
        assert isinstance(expr, NewExpression)
        assert len(expr.arguments) == 1
        assert isinstance(expr.arguments[0], CallExpression)
        assert isinstance(expr.arguments[0].callee, Identifier)
        assert expr.arguments[0].callee.name == "getExecutor"
