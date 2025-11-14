"""
Tests for async/await parser support.

Tests async function declarations, expressions, arrow functions,
and await expressions following TDD methodology.
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
    Program,
    AsyncFunctionDeclaration,
    AsyncFunctionExpression,
    AsyncArrowFunctionExpression,
    AwaitExpression,
    Identifier,
    BlockStatement,
    VariableDeclaration,
    ReturnStatement,
    ExpressionStatement,
    CallExpression,
    Literal,
)


def parse(source: str) -> Program:
    """Helper to parse source code."""
    lexer = Lexer(source, "test.js")
    parser = Parser(lexer)
    return parser.parse()


class TestAsyncFunctionDeclaration:
    """Test parsing of async function declarations."""

    def test_parse_simple_async_function(self):
        """
        Given an async function with no parameters
        When parsing the source code
        Then it should create AsyncFunctionDeclaration node
        """
        source = "async function foo() {}"
        ast = parse(source)

        assert len(ast.body) == 1
        func = ast.body[0]
        assert isinstance(func, AsyncFunctionDeclaration)
        assert isinstance(func.id, Identifier)
        assert func.id.name == "foo"
        assert len(func.params) == 0
        assert isinstance(func.body, BlockStatement)

    def test_parse_async_function_with_params(self):
        """
        Given an async function with parameters
        When parsing the source code
        Then it should preserve parameter names
        """
        source = "async function add(a, b) { return a + b; }"
        ast = parse(source)

        func = ast.body[0]
        assert isinstance(func, AsyncFunctionDeclaration)
        assert func.id.name == "add"
        assert len(func.params) == 2
        assert func.params[0] == "a"
        assert func.params[1] == "b"

    def test_parse_async_function_with_await(self):
        """
        Given an async function containing await expression
        When parsing the source code
        Then the await expression should be parsed correctly
        """
        source = "async function foo() { await Promise.resolve(1); }"
        ast = parse(source)

        func = ast.body[0]
        assert isinstance(func, AsyncFunctionDeclaration)
        # Check body contains await expression
        stmt = func.body.body[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, AwaitExpression)

    def test_parse_async_function_with_multiple_statements(self):
        """
        Given an async function with multiple statements
        When parsing the source code
        Then all statements should be parsed
        """
        source = """
        async function foo() {
            const x = 1;
            const y = 2;
            return x + y;
        }
        """
        ast = parse(source)

        func = ast.body[0]
        assert isinstance(func, AsyncFunctionDeclaration)
        assert len(func.body.body) == 3


class TestAsyncFunctionExpression:
    """Test parsing of async function expressions."""

    def test_parse_async_function_expression_no_name(self):
        """
        Given an async function expression without name
        When parsing the source code
        Then it should have id=None
        """
        source = "const f = async function() {}"
        ast = parse(source)

        decl = ast.body[0]
        assert isinstance(decl, VariableDeclaration)
        init = decl.declarations[0].init
        assert isinstance(init, AsyncFunctionExpression)
        assert init.id is None
        assert len(init.params) == 0

    def test_parse_async_function_expression_with_name(self):
        """
        Given an async function expression with name
        When parsing the source code
        Then the name should be preserved
        """
        source = "const f = async function foo() {}"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncFunctionExpression)
        assert isinstance(init.id, Identifier)
        assert init.id.name == "foo"

    def test_parse_async_function_expression_with_params(self):
        """
        Given an async function expression with parameters
        When parsing the source code
        Then parameters should be preserved
        """
        source = "const f = async function(x, y) { return x + y; }"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncFunctionExpression)
        assert len(init.params) == 2
        assert init.params[0] == "x"
        assert init.params[1] == "y"


class TestAsyncArrowFunction:
    """Test parsing of async arrow functions."""

    def test_parse_async_arrow_no_params(self):
        """
        Given an async arrow function with no parameters
        When parsing the source code
        Then it should create AsyncArrowFunctionExpression
        """
        source = "const f = async () => 42"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncArrowFunctionExpression)
        assert len(init.params) == 0
        assert isinstance(init.body, Literal)
        assert init.body.value == 42

    def test_parse_async_arrow_single_param(self):
        """
        Given an async arrow function with single parameter (no parens)
        When parsing the source code
        Then parameter should be parsed correctly
        """
        source = "const f = async x => x * 2"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncArrowFunctionExpression)
        assert len(init.params) == 1
        assert isinstance(init.params[0], Identifier)
        assert init.params[0].name == "x"

    def test_parse_async_arrow_multiple_params(self):
        """
        Given an async arrow function with multiple parameters
        When parsing the source code
        Then all parameters should be parsed
        """
        source = "const f = async (x, y) => x + y"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncArrowFunctionExpression)
        assert len(init.params) == 2
        assert init.params[0].name == "x"
        assert init.params[1].name == "y"

    def test_parse_async_arrow_block_body(self):
        """
        Given an async arrow function with block body
        When parsing the source code
        Then body should be BlockStatement
        """
        source = "const f = async (x) => { return x * 2; }"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncArrowFunctionExpression)
        assert isinstance(init.body, BlockStatement)
        assert len(init.body.body) == 1
        assert isinstance(init.body.body[0], ReturnStatement)

    def test_parse_async_arrow_with_await(self):
        """
        Given an async arrow function with await expression
        When parsing the source code
        Then await should be parsed correctly
        """
        source = "const f = async () => await Promise.resolve(42)"
        ast = parse(source)

        decl = ast.body[0]
        init = decl.declarations[0].init
        assert isinstance(init, AsyncArrowFunctionExpression)
        assert isinstance(init.body, AwaitExpression)


class TestAwaitExpression:
    """Test parsing of await expressions."""

    def test_parse_await_simple(self):
        """
        Given an await expression with identifier
        When parsing the source code
        Then await argument should be identifier
        """
        source = "async function f() { await x; }"
        ast = parse(source)

        func = ast.body[0]
        stmt = func.body.body[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, AwaitExpression)
        assert isinstance(stmt.expression.argument, Identifier)
        assert stmt.expression.argument.name == "x"

    def test_parse_await_with_call(self):
        """
        Given an await expression with function call
        When parsing the source code
        Then await argument should be CallExpression
        """
        source = "async function f() { await fetch(); }"
        ast = parse(source)

        func = ast.body[0]
        stmt = func.body.body[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, AwaitExpression)
        assert isinstance(stmt.expression.argument, CallExpression)

    def test_parse_await_with_promise(self):
        """
        Given an await expression with Promise.resolve
        When parsing the source code
        Then await argument should be parsed correctly
        """
        source = "async function f() { await Promise.resolve(42); }"
        ast = parse(source)

        func = ast.body[0]
        stmt = func.body.body[0]
        assert isinstance(stmt, ExpressionStatement)
        assert isinstance(stmt.expression, AwaitExpression)
        assert isinstance(stmt.expression.argument, CallExpression)

    def test_parse_multiple_awaits(self):
        """
        Given an async function with multiple await expressions
        When parsing the source code
        Then all awaits should be parsed
        """
        source = """
        async function f() {
            await a();
            await b();
            await c();
        }
        """
        ast = parse(source)

        func = ast.body[0]
        stmts = func.body.body
        assert len(stmts) == 3
        for stmt in stmts:
            assert isinstance(stmt, ExpressionStatement)
            assert isinstance(stmt.expression, AwaitExpression)


class TestComplexAsyncAwait:
    """Test complex async/await scenarios."""

    def test_parse_async_with_variable_assignment(self):
        """
        Given an async function with await in variable assignment
        When parsing the source code
        Then variable should be assigned await expression
        """
        source = "async function f() { const x = await Promise.resolve(1); }"
        ast = parse(source)

        func = ast.body[0]
        decl = func.body.body[0]
        assert isinstance(decl, VariableDeclaration)
        init = decl.declarations[0].init
        assert isinstance(init, AwaitExpression)

    def test_parse_async_with_return_await(self):
        """
        Given an async function with return await
        When parsing the source code
        Then return argument should be AwaitExpression
        """
        source = "async function f() { return await Promise.resolve(42); }"
        ast = parse(source)

        func = ast.body[0]
        ret = func.body.body[0]
        assert isinstance(ret, ReturnStatement)
        assert isinstance(ret.argument, AwaitExpression)

    def test_parse_nested_async_functions(self):
        """
        Given nested async functions
        When parsing the source code
        Then both should be parsed correctly
        """
        source = """
        async function outer() {
            const inner = async function() {
                return await Promise.resolve(1);
            };
            return await inner();
        }
        """
        ast = parse(source)

        outer = ast.body[0]
        assert isinstance(outer, AsyncFunctionDeclaration)

        # Check inner async function
        inner_decl = outer.body.body[0]
        assert isinstance(inner_decl, VariableDeclaration)
        inner_func = inner_decl.declarations[0].init
        assert isinstance(inner_func, AsyncFunctionExpression)

    def test_parse_async_arrow_in_async_function(self):
        """
        Given an async arrow function inside async function
        When parsing the source code
        Then both should be parsed correctly
        """
        source = """
        async function f() {
            const g = async x => await Promise.resolve(x);
            return await g(42);
        }
        """
        ast = parse(source)

        func = ast.body[0]
        assert isinstance(func, AsyncFunctionDeclaration)

        # Check inner async arrow
        inner_decl = func.body.body[0]
        assert isinstance(inner_decl, VariableDeclaration)
        inner_arrow = inner_decl.declarations[0].init
        assert isinstance(inner_arrow, AsyncArrowFunctionExpression)


class TestAwaitPrecedence:
    """Test await expression precedence and error cases."""

    def test_await_has_unary_precedence(self):
        """
        Given an await expression with binary operation
        When parsing the source code
        Then await should bind to its immediate operand
        """
        source = "async function f() { const x = await Promise.resolve(1) + 2; }"
        ast = parse(source)

        func = ast.body[0]
        decl = func.body.body[0]
        init = decl.declarations[0].init

        # The await should bind to Promise.resolve(1), not the whole expression
        # So init should be BinaryExpression(AwaitExpression + 2)
        from components.parser.src.ast_nodes import BinaryExpression
        assert isinstance(init, BinaryExpression)
        assert init.operator == "+"
        assert isinstance(init.left, AwaitExpression)
        assert isinstance(init.right, Literal)
        assert init.right.value == 2
