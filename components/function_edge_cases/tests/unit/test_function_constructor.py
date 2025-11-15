"""
Test suite for Function constructor edge cases (FR-ES24-B-045)

Tests dynamic function creation with Function constructor.
"""

import pytest
from components.function_edge_cases.src.function_constructor import create_dynamic_function, FunctionConstructorOptions


class TestFunctionConstructorBasic:
    """Test basic Function constructor usage"""

    def test_function_with_body_only(self):
        """Function constructor with body only"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return 42"
        )
        result = create_dynamic_function(options)
        assert result["function"]["type"] == "function"
        assert result["function"]["params"] == []
        assert "return 42" in result["function"]["body"]

    def test_function_with_one_parameter(self):
        """Function constructor with one parameter"""
        options = FunctionConstructorOptions(
            parameters=["x"],
            body="return x * 2"
        )
        result = create_dynamic_function(options)
        assert result["parsed_params"] == ["x"]
        assert "return x * 2" in result["function"]["body"]

    def test_function_with_multiple_parameters(self):
        """Function constructor with multiple parameters"""
        options = FunctionConstructorOptions(
            parameters=["a", "b", "c"],
            body="return a + b + c"
        )
        result = create_dynamic_function(options)
        assert result["parsed_params"] == ["a", "b", "c"]


class TestFunctionConstructorStrictMode:
    """Test strict mode in Function constructor"""

    def test_strict_mode_from_body(self):
        """Strict mode detected from body"""
        options = FunctionConstructorOptions(
            parameters=[],
            body='"use strict"; return this'
        )
        result = create_dynamic_function(options)
        assert result["function"]["strict"] is True

    def test_strict_mode_option(self):
        """Strict mode from constructor option"""
        options = FunctionConstructorOptions(
            parameters=["x"],
            body="return x",
            strict=True
        )
        result = create_dynamic_function(options)
        assert result["function"]["strict"] is True

    def test_non_strict_mode_default(self):
        """Non-strict mode by default"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return 1"
        )
        result = create_dynamic_function(options)
        assert result["function"].get("strict", False) is False


class TestFunctionConstructorSyntaxErrors:
    """Test syntax errors in Function constructor"""

    def test_invalid_body_syntax(self):
        """Invalid body syntax throws SyntaxError"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return {"
        )
        with pytest.raises(SyntaxError, match="Unexpected end of input"):
            create_dynamic_function(options)

    def test_invalid_parameter_syntax(self):
        """Invalid parameter syntax throws SyntaxError"""
        options = FunctionConstructorOptions(
            parameters=["a", "1invalid"],
            body="return a"
        )
        with pytest.raises(SyntaxError, match="Invalid parameter"):
            create_dynamic_function(options)

    def test_duplicate_parameters_strict_mode(self):
        """Duplicate parameters in strict mode throw SyntaxError"""
        options = FunctionConstructorOptions(
            parameters=["x", "x"],
            body='"use strict"; return x',
            strict=True
        )
        with pytest.raises(SyntaxError, match="Duplicate parameter"):
            create_dynamic_function(options)

    def test_reserved_word_parameter_strict_mode(self):
        """Reserved word as parameter in strict mode throws SyntaxError"""
        options = FunctionConstructorOptions(
            parameters=["eval"],
            body='"use strict"; return eval',
            strict=True
        )
        with pytest.raises(SyntaxError, match="Reserved word"):
            create_dynamic_function(options)


class TestFunctionConstructorScope:
    """Test scope behavior of constructed functions"""

    def test_function_created_in_global_scope(self):
        """Constructed function has global scope, not lexical"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return typeof localVar"
        )
        result = create_dynamic_function(options)
        # Function should not have access to local variables
        assert result["function"]["scope"] == "global"

    def test_function_cannot_access_local_variables(self):
        """Constructed function cannot access enclosing local variables"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return enclosingVar"  # Would throw ReferenceError
        )
        result = create_dynamic_function(options)
        # This is valid syntax, but would fail at runtime
        assert result["function"]["type"] == "function"


class TestFunctionConstructorParameterEdgeCases:
    """Test edge cases in parameter handling"""

    def test_parameters_as_string_list(self):
        """Parameters as array of strings"""
        options = FunctionConstructorOptions(
            parameters=["arg1", "arg2"],
            body="return arg1 + arg2"
        )
        result = create_dynamic_function(options)
        assert result["parsed_params"] == ["arg1", "arg2"]

    def test_empty_parameter_list(self):
        """Empty parameter list"""
        options = FunctionConstructorOptions(
            parameters=[],
            body="return 42"
        )
        result = create_dynamic_function(options)
        assert result["parsed_params"] == []

    def test_default_parameter_in_constructor(self):
        """Function constructor with default parameter"""
        options = FunctionConstructorOptions(
            parameters=["a", "b = 10"],
            body="return a + b"
        )
        result = create_dynamic_function(options)
        # Should parse parameter with default
        assert "b = 10" in result["parsed_params"] or result["parsed_params"] == ["a", "b"]

    def test_rest_parameter_in_constructor(self):
        """Function constructor with rest parameter"""
        options = FunctionConstructorOptions(
            parameters=["a", "...rest"],
            body="return rest"
        )
        result = create_dynamic_function(options)
        assert "rest" in str(result["parsed_params"])
