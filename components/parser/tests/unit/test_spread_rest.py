"""
Tests for spread and rest operators in parser.

Tests spread/rest operators in arrays, objects, function parameters,
and destructuring patterns.
"""

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import (
    Program,
    ArrayExpression,
    ObjectExpression,
    SpreadElement,
    RestElement,
    FunctionDeclaration,
    ArrowFunctionExpression,
    VariableDeclaration,
    ArrayPattern,
    ObjectPattern,
    Identifier,
)


class TestArraySpread:
    """Test spread operator in array literals."""

    def test_array_spread_single_element(self):
        """
        Given an array literal with spread operator
        When parsing [...arr]
        Then array contains SpreadElement with arr as argument
        """
        # Given
        source = "[...arr]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        assert isinstance(ast, Program)
        assert len(ast.body) == 1
        expr_stmt = ast.body[0]
        array_expr = expr_stmt.expression
        assert isinstance(array_expr, ArrayExpression)
        assert len(array_expr.elements) == 1
        assert isinstance(array_expr.elements[0], SpreadElement)
        assert isinstance(array_expr.elements[0].argument, Identifier)
        assert array_expr.elements[0].argument.name == "arr"

    def test_array_spread_with_elements_before(self):
        """
        Given array with element before spread
        When parsing [1, ...arr]
        Then array contains literal and SpreadElement
        """
        # Given
        source = "[1, ...arr]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        assert len(array_expr.elements) == 2
        assert array_expr.elements[0].value == 1
        assert isinstance(array_expr.elements[1], SpreadElement)
        assert array_expr.elements[1].argument.name == "arr"

    def test_array_spread_with_elements_after(self):
        """
        Given array with element after spread
        When parsing [...arr, 2]
        Then array contains SpreadElement and literal
        """
        # Given
        source = "[...arr, 2]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        assert len(array_expr.elements) == 2
        assert isinstance(array_expr.elements[0], SpreadElement)
        assert array_expr.elements[1].value == 2

    def test_array_multiple_spreads(self):
        """
        Given array with multiple spread operators
        When parsing [...arr1, ...arr2]
        Then array contains two SpreadElements
        """
        # Given
        source = "[...arr1, ...arr2]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        assert len(array_expr.elements) == 2
        assert isinstance(array_expr.elements[0], SpreadElement)
        assert array_expr.elements[0].argument.name == "arr1"
        assert isinstance(array_expr.elements[1], SpreadElement)
        assert array_expr.elements[1].argument.name == "arr2"

    def test_array_spread_complex(self):
        """
        Given complex array with mixed elements and spreads
        When parsing [1, ...arr1, 2, ...arr2, 3]
        Then array elements are in correct order
        """
        # Given
        source = "[1, ...arr1, 2, ...arr2, 3]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        assert len(array_expr.elements) == 5
        assert array_expr.elements[0].value == 1
        assert isinstance(array_expr.elements[1], SpreadElement)
        assert array_expr.elements[2].value == 2
        assert isinstance(array_expr.elements[3], SpreadElement)
        assert array_expr.elements[4].value == 3

    def test_array_spread_empty_array(self):
        """
        Given array spreading empty array literal
        When parsing [...[]]
        Then SpreadElement contains empty array
        """
        # Given
        source = "[...[]]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        assert len(array_expr.elements) == 1
        spread_elem = array_expr.elements[0]
        assert isinstance(spread_elem, SpreadElement)
        assert isinstance(spread_elem.argument, ArrayExpression)
        assert len(spread_elem.argument.elements) == 0


class TestObjectSpread:
    """Test spread operator in object literals."""

    def test_object_spread_single(self):
        """
        Given object with spread operator
        When parsing {...obj}
        Then object contains SpreadElement
        """
        # Given
        source = "({...obj})"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        obj_expr = ast.body[0].expression
        assert isinstance(obj_expr, ObjectExpression)
        assert len(obj_expr.properties) == 1
        assert isinstance(obj_expr.properties[0], SpreadElement)
        assert obj_expr.properties[0].argument.name == "obj"

    def test_object_spread_with_property_before(self):
        """
        Given object with property before spread
        When parsing {x: 1, ...obj}
        Then object contains property and SpreadElement
        """
        # Given
        source = "({x: 1, ...obj})"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        obj_expr = ast.body[0].expression
        assert len(obj_expr.properties) == 2
        # First property is normal
        assert obj_expr.properties[0].key.name == "x"
        # Second is spread
        assert isinstance(obj_expr.properties[1], SpreadElement)

    def test_object_spread_with_property_after(self):
        """
        Given object with property after spread
        When parsing {...obj, y: 2}
        Then object contains SpreadElement and property
        """
        # Given
        source = "({...obj, y: 2})"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        obj_expr = ast.body[0].expression
        assert len(obj_expr.properties) == 2
        assert isinstance(obj_expr.properties[0], SpreadElement)
        assert obj_expr.properties[1].key.name == "y"

    def test_object_multiple_spreads(self):
        """
        Given object with multiple spreads
        When parsing {...obj1, ...obj2}
        Then object contains two SpreadElements
        """
        # Given
        source = "({...obj1, ...obj2})"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        obj_expr = ast.body[0].expression
        assert len(obj_expr.properties) == 2
        assert isinstance(obj_expr.properties[0], SpreadElement)
        assert obj_expr.properties[0].argument.name == "obj1"
        assert isinstance(obj_expr.properties[1], SpreadElement)
        assert obj_expr.properties[1].argument.name == "obj2"

    def test_object_spread_merging(self):
        """
        Given object with spread merging pattern
        When parsing {...obj1, ...obj2, y: 2}
        Then properties are in correct order
        """
        # Given
        source = "({...obj1, ...obj2, y: 2})"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        obj_expr = ast.body[0].expression
        assert len(obj_expr.properties) == 3
        assert isinstance(obj_expr.properties[0], SpreadElement)
        assert isinstance(obj_expr.properties[1], SpreadElement)
        assert obj_expr.properties[2].key.name == "y"


class TestRestParameters:
    """Test rest parameters in function declarations and arrow functions."""

    def test_rest_parameter_only(self):
        """
        Given function with only rest parameter
        When parsing function f(...args) {}
        Then function has rest parameter marked with "..."
        """
        # Given
        source = "function f(...args) {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        func_decl = ast.body[0]
        assert isinstance(func_decl, FunctionDeclaration)
        assert len(func_decl.parameters) == 1
        assert func_decl.parameters[0] == "...args"

    def test_rest_parameter_with_regular_params(self):
        """
        Given function with regular and rest parameters
        When parsing function f(a, b, ...rest) {}
        Then function has all parameters in order
        """
        # Given
        source = "function f(a, b, ...rest) {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        func_decl = ast.body[0]
        assert len(func_decl.parameters) == 3
        assert func_decl.parameters[0] == "a"
        assert func_decl.parameters[1] == "b"
        assert func_decl.parameters[2] == "...rest"

    def test_rest_parameter_not_last_error(self):
        """
        Given function with rest parameter not last
        When parsing function f(...rest, a) {}
        Then parser raises SyntaxError
        """
        # Given
        source = "function f(...rest, a) {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When/Then
        with pytest.raises(SyntaxError, match="Rest parameter must be last"):
            parser.parse()

    def test_arrow_function_rest_parameter(self):
        """
        Given arrow function with rest parameter
        When parsing (...args) => {}
        Then arrow function has RestElement parameter
        """
        # Given
        source = "(...args) => {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        arrow_func = ast.body[0].expression
        assert isinstance(arrow_func, ArrowFunctionExpression)
        assert len(arrow_func.params) == 1
        assert isinstance(arrow_func.params[0], RestElement)
        assert arrow_func.params[0].argument.name == "args"

    def test_arrow_function_rest_with_regular_params(self):
        """
        Given arrow function with regular and rest parameters
        When parsing (a, b, ...rest) => {}
        Then arrow function has all parameters
        """
        # Given
        source = "(a, b, ...rest) => {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        arrow_func = ast.body[0].expression
        assert len(arrow_func.params) == 3
        assert arrow_func.params[0].name == "a"
        assert arrow_func.params[1].name == "b"
        assert isinstance(arrow_func.params[2], RestElement)
        assert arrow_func.params[2].argument.name == "rest"

    def test_arrow_function_rest_not_last_error(self):
        """
        Given arrow function with rest parameter not last
        When parsing (...rest, a) => {}
        Then parser raises SyntaxError
        """
        # Given
        source = "(...rest, a) => {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When/Then
        with pytest.raises(SyntaxError, match="Rest parameter must be last"):
            parser.parse()


class TestRestInDestructuring:
    """Test rest elements in destructuring patterns."""

    def test_array_destructuring_rest(self):
        """
        Given array destructuring with rest
        When parsing const [a, ...rest] = arr
        Then pattern contains elements and RestElement
        """
        # Given
        source = "const [a, ...rest] = arr"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        var_decl = ast.body[0]
        assert isinstance(var_decl, VariableDeclaration)
        pattern = var_decl.declarations[0].id
        assert isinstance(pattern, ArrayPattern)
        assert len(pattern.elements) == 2
        assert isinstance(pattern.elements[0], Identifier)
        assert pattern.elements[0].name == "a"
        assert isinstance(pattern.elements[1], RestElement)
        assert pattern.elements[1].argument.name == "rest"

    def test_array_destructuring_rest_only(self):
        """
        Given array destructuring with only rest
        When parsing const [...all] = arr
        Then pattern contains only RestElement
        """
        # Given
        source = "const [...all] = arr"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        pattern = ast.body[0].declarations[0].id
        assert isinstance(pattern, ArrayPattern)
        assert len(pattern.elements) == 1
        assert isinstance(pattern.elements[0], RestElement)
        assert pattern.elements[0].argument.name == "all"

    def test_array_destructuring_rest_not_last_error(self):
        """
        Given array destructuring with rest not last
        When parsing const [...rest, a] = arr
        Then parser raises SyntaxError
        """
        # Given
        source = "const [...rest, a] = arr"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When/Then
        with pytest.raises(SyntaxError, match="Rest element must be last"):
            parser.parse()

    def test_object_destructuring_rest(self):
        """
        Given object destructuring with rest
        When parsing const {x, ...rest} = obj
        Then pattern contains property and RestElement
        """
        # Given
        source = "const {x, ...rest} = obj"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        var_decl = ast.body[0]
        pattern = var_decl.declarations[0].id
        assert isinstance(pattern, ObjectPattern)
        assert len(pattern.properties) == 2
        # First is property pattern
        assert pattern.properties[0].key.name == "x"
        # Second is RestElement
        assert isinstance(pattern.properties[1], RestElement)
        assert pattern.properties[1].argument.name == "rest"

    def test_object_destructuring_rest_only(self):
        """
        Given object destructuring with only rest
        When parsing const {...all} = obj
        Then pattern contains only RestElement
        """
        # Given
        source = "const {...all} = obj"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        pattern = ast.body[0].declarations[0].id
        assert isinstance(pattern, ObjectPattern)
        assert len(pattern.properties) == 1
        assert isinstance(pattern.properties[0], RestElement)
        assert pattern.properties[0].argument.name == "all"

    def test_object_destructuring_rest_not_last_error(self):
        """
        Given object destructuring with rest not last
        When parsing const {...rest, x} = obj
        Then parser raises SyntaxError
        """
        # Given
        source = "const {...rest, x} = obj"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When/Then
        with pytest.raises(SyntaxError, match="Rest element must be last"):
            parser.parse()

    def test_object_destructuring_multiple_properties_with_rest(self):
        """
        Given object destructuring with multiple properties and rest
        When parsing const {x, y, z, ...rest} = obj
        Then all properties and rest are in pattern
        """
        # Given
        source = "const {x, y, z, ...rest} = obj"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        pattern = ast.body[0].declarations[0].id
        assert len(pattern.properties) == 4
        assert pattern.properties[0].key.name == "x"
        assert pattern.properties[1].key.name == "y"
        assert pattern.properties[2].key.name == "z"
        assert isinstance(pattern.properties[3], RestElement)
        assert pattern.properties[3].argument.name == "rest"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_spread_array(self):
        """
        Given array with spread of empty array
        When parsing [...[]]
        Then spread contains empty array expression
        """
        # Given
        source = "[...[]]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        array_expr = ast.body[0].expression
        spread = array_expr.elements[0]
        assert isinstance(spread, SpreadElement)
        assert isinstance(spread.argument, ArrayExpression)
        assert len(spread.argument.elements) == 0

    def test_nested_spread_in_array(self):
        """
        Given nested arrays with spread
        When parsing [[...arr]]
        Then outer array contains inner array with spread
        """
        # Given
        source = "[[...arr]]"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        outer_array = ast.body[0].expression
        inner_array = outer_array.elements[0]
        assert isinstance(inner_array, ArrayExpression)
        spread = inner_array.elements[0]
        assert isinstance(spread, SpreadElement)
        assert spread.argument.name == "arr"
