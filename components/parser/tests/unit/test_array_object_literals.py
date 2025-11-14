"""
Unit tests for array and object literal parsing.

Tests verify that the parser correctly handles:
- Array literals: [1, 2, 3]
- Object literals: {key: value}
- Nested structures
- Edge cases (empty arrays/objects, trailing commas)
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


# ============================================================================
# ARRAY LITERAL TESTS
# ============================================================================


def test_parse_empty_array():
    """
    Given an empty array literal
    When parsing
    Then ArrayExpression with empty elements should be created
    """
    program = parse("[];")

    expr_stmt = program.body[0]
    assert isinstance(expr_stmt, ExpressionStatement)

    array_expr = expr_stmt.expression
    assert isinstance(array_expr, ArrayExpression)
    assert len(array_expr.elements) == 0


def test_parse_array_with_single_element():
    """
    Given an array with one element
    When parsing
    Then ArrayExpression with one element should be created
    """
    program = parse("[1];")

    array_expr = program.body[0].expression
    assert isinstance(array_expr, ArrayExpression)
    assert len(array_expr.elements) == 1
    assert isinstance(array_expr.elements[0], Literal)
    assert array_expr.elements[0].value == 1


def test_parse_array_with_multiple_elements():
    """
    Given an array with multiple elements
    When parsing
    Then all elements should be in the array
    """
    program = parse("[1, 2, 3];")

    array_expr = program.body[0].expression
    assert isinstance(array_expr, ArrayExpression)
    assert len(array_expr.elements) == 3
    assert array_expr.elements[0].value == 1
    assert array_expr.elements[1].value == 2
    assert array_expr.elements[2].value == 3


def test_parse_array_with_expressions():
    """
    Given an array with expression elements
    When parsing
    Then expressions should be evaluated as elements
    """
    program = parse("[x, y + 1, fn()];")

    array_expr = program.body[0].expression
    assert len(array_expr.elements) == 3

    # First element: identifier
    assert isinstance(array_expr.elements[0], Identifier)
    assert array_expr.elements[0].name == "x"

    # Second element: binary expression
    assert isinstance(array_expr.elements[1], BinaryExpression)
    assert array_expr.elements[1].operator == "+"

    # Third element: call expression
    assert isinstance(array_expr.elements[2], CallExpression)


def test_parse_nested_arrays():
    """
    Given nested array literals
    When parsing
    Then nested ArrayExpression nodes should be created
    """
    program = parse("[[1, 2], [3, 4]];")

    array_expr = program.body[0].expression
    assert isinstance(array_expr, ArrayExpression)
    assert len(array_expr.elements) == 2

    # First nested array
    inner1 = array_expr.elements[0]
    assert isinstance(inner1, ArrayExpression)
    assert len(inner1.elements) == 2
    assert inner1.elements[0].value == 1
    assert inner1.elements[1].value == 2

    # Second nested array
    inner2 = array_expr.elements[1]
    assert isinstance(inner2, ArrayExpression)
    assert len(inner2.elements) == 2
    assert inner2.elements[0].value == 3
    assert inner2.elements[1].value == 4


def test_parse_array_with_trailing_comma():
    """
    Given an array with trailing comma
    When parsing
    Then trailing comma should be ignored
    """
    program = parse("[1, 2, 3,];")

    array_expr = program.body[0].expression
    assert len(array_expr.elements) == 3


def test_parse_array_in_variable_declaration():
    """
    Given array literal in variable declaration
    When parsing
    Then array should be parsed as initializer
    """
    program = parse("var arr = [1, 2, 3];")

    var_decl = program.body[0]
    assert isinstance(var_decl, VariableDeclaration)

    init = var_decl.declarations[0].init
    assert isinstance(init, ArrayExpression)
    assert len(init.elements) == 3


# ============================================================================
# OBJECT LITERAL TESTS
# ============================================================================


def test_parse_empty_object():
    """
    Given an empty object literal
    When parsing
    Then ObjectExpression with empty properties should be created
    """
    # Use parentheses to force expression context
    program = parse("({});")

    expr_stmt = program.body[0]
    assert isinstance(expr_stmt, ExpressionStatement)

    obj_expr = expr_stmt.expression
    assert isinstance(obj_expr, ObjectExpression)
    assert len(obj_expr.properties) == 0


def test_parse_object_with_single_property():
    """
    Given an object with one property
    When parsing
    Then ObjectExpression with one property should be created
    """
    program = parse("({x: 1});")

    obj_expr = program.body[0].expression
    assert isinstance(obj_expr, ObjectExpression)
    assert len(obj_expr.properties) == 1

    prop = obj_expr.properties[0]
    assert isinstance(prop, Property)
    assert isinstance(prop.key, Identifier)
    assert prop.key.name == "x"
    assert isinstance(prop.value, Literal)
    assert prop.value.value == 1
    assert prop.kind == "init"
    assert prop.computed is False


def test_parse_object_with_multiple_properties():
    """
    Given an object with multiple properties
    When parsing
    Then all properties should be in the object
    """
    program = parse("({x: 1, y: 2, z: 3});")

    obj_expr = program.body[0].expression
    assert len(obj_expr.properties) == 3

    assert obj_expr.properties[0].key.name == "x"
    assert obj_expr.properties[0].value.value == 1

    assert obj_expr.properties[1].key.name == "y"
    assert obj_expr.properties[1].value.value == 2

    assert obj_expr.properties[2].key.name == "z"
    assert obj_expr.properties[2].value.value == 3


def test_parse_object_shorthand_properties():
    """
    Given an object with shorthand properties
    When parsing
    Then shorthand should expand to {x: x}
    """
    program = parse("({x, y});")

    obj_expr = program.body[0].expression
    assert len(obj_expr.properties) == 2

    # Shorthand x expands to x: x
    prop1 = obj_expr.properties[0]
    assert prop1.key.name == "x"
    assert isinstance(prop1.value, Identifier)
    assert prop1.value.name == "x"

    # Shorthand y expands to y: y
    prop2 = obj_expr.properties[1]
    assert prop2.key.name == "y"
    assert isinstance(prop2.value, Identifier)
    assert prop2.value.name == "y"


def test_parse_object_with_string_keys():
    """
    Given an object with string literal keys
    When parsing
    Then string keys should be allowed
    """
    program = parse('({"key": "value"});')

    obj_expr = program.body[0].expression
    prop = obj_expr.properties[0]
    assert isinstance(prop.key, Literal)
    assert prop.key.value == "key"
    assert isinstance(prop.value, Literal)
    assert prop.value.value == "value"


def test_parse_object_with_method():
    """
    Given an object with method definition
    When parsing
    Then method property should be created
    """
    program = parse("({greet() { return 'hi'; }});")

    obj_expr = program.body[0].expression
    assert len(obj_expr.properties) == 1

    prop = obj_expr.properties[0]
    assert prop.key.name == "greet"
    assert isinstance(prop.value, FunctionExpression)
    assert prop.kind == "method"
    assert prop.value.name is None  # Anonymous function
    assert len(prop.value.parameters) == 0


def test_parse_object_with_computed_property():
    """
    Given an object with computed property name
    When parsing
    Then computed property should be marked as computed
    """
    program = parse("({[expr]: value});")

    obj_expr = program.body[0].expression
    prop = obj_expr.properties[0]
    assert prop.computed is True
    assert isinstance(prop.key, Identifier)
    assert prop.key.name == "expr"


def test_parse_nested_objects():
    """
    Given nested object literals
    When parsing
    Then nested ObjectExpression nodes should be created
    """
    program = parse("({outer: {inner: 1}});")

    obj_expr = program.body[0].expression
    assert isinstance(obj_expr, ObjectExpression)

    outer_prop = obj_expr.properties[0]
    assert outer_prop.key.name == "outer"

    inner_obj = outer_prop.value
    assert isinstance(inner_obj, ObjectExpression)

    inner_prop = inner_obj.properties[0]
    assert inner_prop.key.name == "inner"
    assert inner_prop.value.value == 1


def test_parse_object_with_trailing_comma():
    """
    Given an object with trailing comma
    When parsing
    Then trailing comma should be ignored
    """
    program = parse("({a: 1, b: 2,});")

    obj_expr = program.body[0].expression
    assert len(obj_expr.properties) == 2


def test_parse_object_in_variable_declaration():
    """
    Given object literal in variable declaration
    When parsing
    Then object should be parsed as initializer
    """
    program = parse("var obj = {x: 1, y: 2};")

    var_decl = program.body[0]
    init = var_decl.declarations[0].init
    assert isinstance(init, ObjectExpression)
    assert len(init.properties) == 2


# ============================================================================
# COMPLEX NESTED STRUCTURES
# ============================================================================


def test_parse_complex_nested_structures():
    """
    Given complex nested arrays and objects
    When parsing
    Then correct nested structure should be created
    """
    program = parse("({arr: [1, 2], obj: {nested: true}});")

    obj_expr = program.body[0].expression
    assert len(obj_expr.properties) == 2

    # First property: arr with array value
    arr_prop = obj_expr.properties[0]
    assert arr_prop.key.name == "arr"
    assert isinstance(arr_prop.value, ArrayExpression)
    assert len(arr_prop.value.elements) == 2

    # Second property: obj with object value
    obj_prop = obj_expr.properties[1]
    assert obj_prop.key.name == "obj"
    assert isinstance(obj_prop.value, ObjectExpression)


def test_parse_array_of_objects():
    """
    Given array containing objects
    When parsing
    Then array should contain ObjectExpression elements
    """
    program = parse("[{a: 1}, {b: 2}];")

    array_expr = program.body[0].expression
    assert len(array_expr.elements) == 2

    assert isinstance(array_expr.elements[0], ObjectExpression)
    assert isinstance(array_expr.elements[1], ObjectExpression)


def test_parse_object_with_expression_values():
    """
    Given object with expression values
    When parsing
    Then expressions should be parsed correctly
    """
    program = parse("({sum: a + b, product: x * y});")

    obj_expr = program.body[0].expression

    # sum property
    sum_prop = obj_expr.properties[0]
    assert isinstance(sum_prop.value, BinaryExpression)
    assert sum_prop.value.operator == "+"

    # product property
    prod_prop = obj_expr.properties[1]
    assert isinstance(prod_prop.value, BinaryExpression)
    assert prod_prop.value.operator == "*"


# ============================================================================
# ERROR HANDLING
# ============================================================================


def test_parse_array_missing_closing_bracket():
    """
    Given array without closing bracket
    When parsing
    Then SyntaxError should be raised
    """
    with pytest.raises(SyntaxError):
        parse("[1, 2, 3")


def test_parse_object_missing_closing_brace():
    """
    Given object without closing brace
    When parsing
    Then SyntaxError should be raised
    """
    with pytest.raises(SyntaxError):
        parse("({x: 1")


def test_parse_object_missing_colon():
    """
    Given object property without colon (not shorthand)
    When parsing
    Then SyntaxError should be raised
    """
    # Note: This should fail because it's trying to parse 1 as if it's part of the property
    # After shorthand property 'x', we expect comma or closing brace, not a number
    with pytest.raises(SyntaxError):
        parse("({x 1})")


def test_parse_object_invalid_property_syntax():
    """
    Given object with invalid property syntax
    When parsing
    Then SyntaxError should be raised
    """
    with pytest.raises(SyntaxError):
        parse("({: value})")
