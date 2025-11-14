"""
Tests for destructuring syntax parsing.

Tests object and array destructuring patterns in variable declarations.
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
    VariableDeclaration,
    VariableDeclarator,
    ObjectPattern,
    ArrayPattern,
    PropertyPattern,
    AssignmentPattern,
    Identifier,
    Literal,
)


def parse(source: str) -> Program:
    """Helper to parse source code."""
    lexer = Lexer(source, "test.js")
    parser = Parser(lexer)
    return parser.parse()


class TestObjectDestructuring:
    """Test object destructuring patterns."""

    def test_simple_object_destructuring(self):
        """
        Given source code with simple object destructuring
        When parsed
        Then AST contains ObjectPattern with correct properties
        """
        # Given
        source = "const {x, y} = obj;"

        # When
        ast = parse(source)

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, VariableDeclaration)
        assert stmt.kind == "const"
        assert len(stmt.declarations) == 1

        decl = stmt.declarations[0]
        assert isinstance(decl, VariableDeclarator)
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 2

        # Check first property: x
        prop1 = decl.id.properties[0]
        assert isinstance(prop1, PropertyPattern)
        assert isinstance(prop1.key, Identifier)
        assert prop1.key.name == "x"
        assert isinstance(prop1.value, Identifier)
        assert prop1.value.name == "x"
        assert prop1.computed is False

        # Check second property: y
        prop2 = decl.id.properties[1]
        assert isinstance(prop2, PropertyPattern)
        assert isinstance(prop2.key, Identifier)
        assert prop2.key.name == "y"
        assert isinstance(prop2.value, Identifier)
        assert prop2.value.name == "y"
        assert prop2.computed is False

        # Check initializer
        assert isinstance(decl.init, Identifier)
        assert decl.init.name == "obj"

    def test_object_destructuring_with_renaming(self):
        """
        Given object destructuring with property renaming
        When parsed
        Then AST contains PropertyPattern with different key and value
        """
        # Given
        source = "const {x: newX, y: newY} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 2

        # Check first property: x: newX
        prop1 = decl.id.properties[0]
        assert prop1.key.name == "x"
        assert prop1.value.name == "newX"

        # Check second property: y: newY
        prop2 = decl.id.properties[1]
        assert prop2.key.name == "y"
        assert prop2.value.name == "newY"

    def test_object_destructuring_with_single_property(self):
        """
        Given object destructuring with single property
        When parsed
        Then AST contains ObjectPattern with one property
        """
        # Given
        source = "let {x} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 1
        assert decl.id.properties[0].key.name == "x"
        assert decl.id.properties[0].value.name == "x"


class TestArrayDestructuring:
    """Test array destructuring patterns."""

    def test_simple_array_destructuring(self):
        """
        Given source code with simple array destructuring
        When parsed
        Then AST contains ArrayPattern with correct elements
        """
        # Given
        source = "const [a, b] = arr;"

        # When
        ast = parse(source)

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, VariableDeclaration)
        assert stmt.kind == "const"
        assert len(stmt.declarations) == 1

        decl = stmt.declarations[0]
        assert isinstance(decl, VariableDeclarator)
        assert isinstance(decl.id, ArrayPattern)
        assert len(decl.id.elements) == 2

        # Check first element
        elem1 = decl.id.elements[0]
        assert isinstance(elem1, Identifier)
        assert elem1.name == "a"

        # Check second element
        elem2 = decl.id.elements[1]
        assert isinstance(elem2, Identifier)
        assert elem2.name == "b"

        # Check initializer
        assert isinstance(decl.init, Identifier)
        assert decl.init.name == "arr"

    def test_array_destructuring_with_single_element(self):
        """
        Given array destructuring with single element
        When parsed
        Then AST contains ArrayPattern with one element
        """
        # Given
        source = "let [x] = arr;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ArrayPattern)
        assert len(decl.id.elements) == 1
        assert decl.id.elements[0].name == "x"

    def test_array_destructuring_with_three_elements(self):
        """
        Given array destructuring with three elements
        When parsed
        Then AST contains ArrayPattern with three elements
        """
        # Given
        source = "const [a, b, c] = arr;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ArrayPattern)
        assert len(decl.id.elements) == 3
        assert decl.id.elements[0].name == "a"
        assert decl.id.elements[1].name == "b"
        assert decl.id.elements[2].name == "c"


class TestNestedDestructuring:
    """Test nested destructuring patterns."""

    def test_nested_object_destructuring(self):
        """
        Given nested object destructuring
        When parsed
        Then AST contains ObjectPattern with nested ObjectPattern
        """
        # Given
        source = "const {x: {y}} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 1

        prop = decl.id.properties[0]
        assert prop.key.name == "x"
        assert isinstance(prop.value, ObjectPattern)
        assert len(prop.value.properties) == 1
        assert prop.value.properties[0].key.name == "y"
        assert prop.value.properties[0].value.name == "y"

    def test_nested_array_destructuring(self):
        """
        Given nested array destructuring
        When parsed
        Then AST contains ArrayPattern with nested ArrayPattern
        """
        # Given
        source = "const [[a, b], c] = arr;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ArrayPattern)
        assert len(decl.id.elements) == 2

        # First element is nested array
        nested = decl.id.elements[0]
        assert isinstance(nested, ArrayPattern)
        assert len(nested.elements) == 2
        assert nested.elements[0].name == "a"
        assert nested.elements[1].name == "b"

        # Second element is simple identifier
        assert decl.id.elements[1].name == "c"

    def test_mixed_nested_destructuring(self):
        """
        Given mixed object and array destructuring
        When parsed
        Then AST contains correct nested structure
        """
        # Given
        source = "const {x, y: [a, b]} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 2

        # First property: x (simple)
        prop1 = decl.id.properties[0]
        assert prop1.key.name == "x"
        assert prop1.value.name == "x"

        # Second property: y: [a, b] (nested array)
        prop2 = decl.id.properties[1]
        assert prop2.key.name == "y"
        assert isinstance(prop2.value, ArrayPattern)
        assert len(prop2.value.elements) == 2
        assert prop2.value.elements[0].name == "a"
        assert prop2.value.elements[1].name == "b"


class TestDefaultValues:
    """Test destructuring with default values."""

    def test_object_destructuring_with_defaults(self):
        """
        Given object destructuring with default values
        When parsed
        Then AST contains AssignmentPattern nodes
        """
        # Given
        source = "const {x = 10} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 1

        prop = decl.id.properties[0]
        assert prop.key.name == "x"
        assert isinstance(prop.value, AssignmentPattern)
        assert isinstance(prop.value.left, Identifier)
        assert prop.value.left.name == "x"
        assert isinstance(prop.value.right, Literal)
        assert prop.value.right.value == 10

    def test_array_destructuring_with_defaults(self):
        """
        Given array destructuring with default values
        When parsed
        Then AST contains AssignmentPattern nodes
        """
        # Given
        source = "const [a = 5, b = 10] = arr;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ArrayPattern)
        assert len(decl.id.elements) == 2

        # First element with default
        elem1 = decl.id.elements[0]
        assert isinstance(elem1, AssignmentPattern)
        assert elem1.left.name == "a"
        assert elem1.right.value == 5

        # Second element with default
        elem2 = decl.id.elements[1]
        assert isinstance(elem2, AssignmentPattern)
        assert elem2.left.name == "b"
        assert elem2.right.value == 10

    def test_object_destructuring_mixed_defaults(self):
        """
        Given object destructuring with some defaults
        When parsed
        Then AST has AssignmentPattern only for properties with defaults
        """
        # Given
        source = "const {x, y = 20} = obj;"

        # When
        ast = parse(source)

        # Then
        decl = ast.body[0].declarations[0]
        assert isinstance(decl.id, ObjectPattern)
        assert len(decl.id.properties) == 2

        # First property without default
        prop1 = decl.id.properties[0]
        assert prop1.key.name == "x"
        assert isinstance(prop1.value, Identifier)
        assert prop1.value.name == "x"

        # Second property with default
        prop2 = decl.id.properties[1]
        assert prop2.key.name == "y"
        assert isinstance(prop2.value, AssignmentPattern)
        assert prop2.value.left.name == "y"
        assert prop2.value.right.value == 20
