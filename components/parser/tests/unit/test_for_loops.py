"""
Tests for for loop parsing (traditional for, for-in, for-of).

Tests all three for loop types following TDD methodology.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src import Parse
from components.parser.src.ast_nodes import (
    ForStatement,
    ForInStatement,
    ForOfStatement,
    VariableDeclaration,
    Identifier,
    BinaryExpression,
    Literal,
    BlockStatement,
    ExpressionStatement,
    CallExpression,
)


class TestTraditionalForLoop:
    """Test traditional for loop parsing: for (init; test; update) { ... }"""

    def test_basic_for_loop(self):
        """
        Given a basic for loop with var initialization
        When parsing the source code
        Then it creates a ForStatement AST node with all components
        """
        source = "for (var i = 0; i < 10; i = i + 1) { }"

        ast = Parse(source)

        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert isinstance(stmt.init, VariableDeclaration)
        assert isinstance(stmt.test, BinaryExpression)
        assert stmt.test.operator == "<"
        assert stmt.update is not None  # i = i + 1
        assert isinstance(stmt.body, BlockStatement)

    def test_for_loop_with_expression_init(self):
        """
        Given a for loop with expression initialization (not var)
        When parsing the source code
        Then it creates a ForStatement with expression init
        """
        source = "for (i = 0; i < 10; i = i + 1) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        # init should be an expression, not VariableDeclaration
        assert not isinstance(stmt.init, VariableDeclaration)
        assert stmt.init is not None

    def test_for_loop_with_empty_init(self):
        """
        Given a for loop with no initialization
        When parsing the source code
        Then init should be None
        """
        source = "for (; i < 10; i = i + 1) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert stmt.init is None
        assert stmt.test is not None
        assert stmt.update is not None

    def test_for_loop_with_empty_test(self):
        """
        Given a for loop with no test condition (infinite loop)
        When parsing the source code
        Then test should be None
        """
        source = "for (var i = 0; ; i = i + 1) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert stmt.init is not None
        assert stmt.test is None
        assert stmt.update is not None

    def test_for_loop_with_empty_update(self):
        """
        Given a for loop with no update expression
        When parsing the source code
        Then update should be None
        """
        source = "for (var i = 0; i < 10; ) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert stmt.init is not None
        assert stmt.test is not None
        assert stmt.update is None

    def test_for_loop_all_empty(self):
        """
        Given a for loop with all parts empty (infinite loop)
        When parsing the source code
        Then all parts should be None
        """
        source = "for (;;) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert stmt.init is None
        assert stmt.test is None
        assert stmt.update is None

    def test_for_loop_with_body_statements(self):
        """
        Given a for loop with statements in the body
        When parsing the source code
        Then the body should contain all statements
        """
        source = """
        for (var i = 0; i < 10; i = i + 1) {
            var x = i;
        }
        """

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForStatement)
        assert isinstance(stmt.body, BlockStatement)
        assert len(stmt.body.body) == 1

    def test_nested_for_loops(self):
        """
        Given nested for loops
        When parsing the source code
        Then it creates nested ForStatement nodes
        """
        source = """
        for (var i = 0; i < 10; i = i + 1) {
            for (var j = 0; j < 10; j = j + 1) {
            }
        }
        """

        ast = Parse(source)

        outer = ast.body[0]
        assert isinstance(outer, ForStatement)
        assert isinstance(outer.body, BlockStatement)
        assert len(outer.body.body) == 1

        inner = outer.body.body[0]
        assert isinstance(inner, ForStatement)


class TestForInLoop:
    """Test for-in loop parsing: for (var key in obj) { ... }"""

    def test_basic_for_in_loop(self):
        """
        Given a basic for-in loop
        When parsing the source code
        Then it creates a ForInStatement AST node
        """
        source = "for (var key in obj) { }"

        ast = Parse(source)

        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ForInStatement)
        assert isinstance(stmt.left, VariableDeclaration)
        assert isinstance(stmt.right, Identifier)
        assert stmt.right.name == "obj"
        assert isinstance(stmt.body, BlockStatement)

    def test_for_in_without_var(self):
        """
        Given a for-in loop without var declaration
        When parsing the source code
        Then left should be an Identifier
        """
        source = "for (key in obj) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForInStatement)
        assert isinstance(stmt.left, Identifier)
        assert stmt.left.name == "key"

    def test_for_in_with_expression_right(self):
        """
        Given a for-in loop with expression on right side
        When parsing the source code
        Then right should be the expression
        """
        source = "for (var key in getObject()) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForInStatement)
        assert isinstance(stmt.right, CallExpression)

    def test_for_in_with_body(self):
        """
        Given a for-in loop with statements in body
        When parsing the source code
        Then the body should contain all statements
        """
        source = """
        for (var key in obj) {
            var val = obj[key];
        }
        """

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForInStatement)
        assert isinstance(stmt.body, BlockStatement)
        assert len(stmt.body.body) == 1


class TestForOfLoop:
    """Test for-of loop parsing: for (var value of array) { ... }"""

    def test_basic_for_of_loop(self):
        """
        Given a basic for-of loop
        When parsing the source code
        Then it creates a ForOfStatement AST node
        """
        source = "for (var value of array) { }"

        ast = Parse(source)

        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ForOfStatement)
        assert isinstance(stmt.left, VariableDeclaration)
        assert isinstance(stmt.right, Identifier)
        assert stmt.right.name == "array"
        assert isinstance(stmt.body, BlockStatement)

    def test_for_of_without_var(self):
        """
        Given a for-of loop without var declaration
        When parsing the source code
        Then left should be an Identifier
        """
        source = "for (value of array) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForOfStatement)
        assert isinstance(stmt.left, Identifier)
        assert stmt.left.name == "value"

    def test_for_of_with_expression_right(self):
        """
        Given a for-of loop with expression on right side
        When parsing the source code
        Then right should be the expression
        """
        source = "for (var value of getArray()) { }"

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForOfStatement)
        assert isinstance(stmt.right, CallExpression)

    def test_for_of_with_body(self):
        """
        Given a for-of loop with statements in body
        When parsing the source code
        Then the body should contain all statements
        """
        source = """
        for (var value of array) {
            var doubled = value * 2;
        }
        """

        ast = Parse(source)

        stmt = ast.body[0]
        assert isinstance(stmt, ForOfStatement)
        assert isinstance(stmt.body, BlockStatement)
        assert len(stmt.body.body) == 1


class TestForLoopErrorCases:
    """Test error handling in for loop parsing"""

    def test_for_loop_missing_parentheses(self):
        """
        Given a for loop without parentheses
        When parsing the source code
        Then it should raise SyntaxError
        """
        source = "for var i = 0; i < 10; i++ { }"

        with pytest.raises(SyntaxError):
            Parse(source)

    def test_for_loop_missing_semicolons(self):
        """
        Given a traditional for loop with missing semicolons
        When parsing the source code
        Then it should raise SyntaxError
        """
        source = "for (var i = 0 i < 10 i++) { }"

        with pytest.raises(SyntaxError):
            Parse(source)

    def test_multiple_for_loops(self):
        """
        Given multiple for loops in sequence
        When parsing the source code
        Then all for loops should be parsed correctly
        """
        source = """
        for (var i = 0; i < 5; i = i + 1) { }
        for (var j in obj) { }
        for (var k of arr) { }
        """

        ast = Parse(source)

        assert len(ast.body) == 3
        assert isinstance(ast.body[0], ForStatement)
        assert isinstance(ast.body[1], ForInStatement)
        assert isinstance(ast.body[2], ForOfStatement)
