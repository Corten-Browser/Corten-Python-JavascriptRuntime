"""
Test suite for Function.prototype.toString() (FR-ES24-B-040)

Tests function source code revelation and formatting.
"""

import pytest
from components.function_edge_cases.src.tostring import function_to_string, ToStringOptions


class TestToStringNormalFunctions:
    """Test toString for normal functions"""

    def test_named_function(self):
        """Normal function shows source"""
        func = {
            "type": "function",
            "name": "foo",
            "source": "function foo(a, b) { return a + b; }"
        }
        result = function_to_string(func)
        assert result == "function foo(a, b) { return a + b; }"

    def test_anonymous_function(self):
        """Anonymous function shows source"""
        func = {
            "type": "function",
            "name": "",
            "source": "function(x) { return x * 2; }"
        }
        result = function_to_string(func)
        assert result == "function(x) { return x * 2; }"

    def test_function_with_body(self):
        """Function with multiline body"""
        func = {
            "type": "function",
            "name": "multi",
            "source": "function multi() {\n  return 1;\n}"
        }
        result = function_to_string(func)
        assert result == "function multi() {\n  return 1;\n}"


class TestToStringArrowFunctions:
    """Test toString for arrow functions"""

    def test_arrow_function_single_param(self):
        """Arrow function with single parameter"""
        func = {
            "type": "arrow",
            "source": "(x) => x * 2"
        }
        result = function_to_string(func)
        assert result == "(x) => x * 2"

    def test_arrow_function_no_params(self):
        """Arrow function with no parameters"""
        func = {
            "type": "arrow",
            "source": "() => 42"
        }
        result = function_to_string(func)
        assert result == "() => 42"

    def test_arrow_function_with_block(self):
        """Arrow function with block body"""
        func = {
            "type": "arrow",
            "source": "(a, b) => { return a + b; }"
        }
        result = function_to_string(func)
        assert result == "(a, b) => { return a + b; }"


class TestToStringBoundFunctions:
    """Test toString for bound functions"""

    def test_bound_function(self):
        """Bound function shows [native code]"""
        func = {
            "type": "bound",
            "name": "bound foo",
            "target_function": {"name": "foo"}
        }
        result = function_to_string(func)
        assert result == "function () { [native code] }"

    def test_bound_function_custom_placeholder(self):
        """Bound function with custom placeholder"""
        func = {
            "type": "bound",
            "name": "bound bar"
        }
        options = ToStringOptions(native_code_placeholder="[native code]")
        result = function_to_string(func, options)
        assert "[native code]" in result


class TestToStringNativeFunctions:
    """Test toString for native/built-in functions"""

    def test_native_function(self):
        """Native function shows [native code]"""
        func = {
            "type": "function",
            "name": "map",
            "is_native": True
        }
        result = function_to_string(func)
        assert result == "function map() { [native code] }"

    def test_native_constructor(self):
        """Native constructor shows [native code]"""
        func = {
            "type": "constructor",
            "name": "Array",
            "is_native": True
        }
        result = function_to_string(func)
        assert result == "function Array() { [native code] }"


class TestToStringGeneratorFunctions:
    """Test toString for generator functions"""

    def test_generator_function(self):
        """Generator function shows function* syntax"""
        func = {
            "type": "generator",
            "name": "gen",
            "source": "function* gen() { yield 1; }"
        }
        result = function_to_string(func)
        assert result == "function* gen() { yield 1; }"

    def test_anonymous_generator(self):
        """Anonymous generator function"""
        func = {
            "type": "generator",
            "name": "",
            "source": "function*() { yield 1; }"
        }
        result = function_to_string(func)
        assert result == "function*() { yield 1; }"


class TestToStringAsyncFunctions:
    """Test toString for async functions"""

    def test_async_function(self):
        """Async function shows async keyword"""
        func = {
            "type": "async",
            "name": "fetchData",
            "source": "async function fetchData() { return data; }"
        }
        result = function_to_string(func)
        assert result == "async function fetchData() { return data; }"

    def test_async_arrow(self):
        """Async arrow function"""
        func = {
            "type": "async",
            "is_arrow": True,
            "source": "async () => data"
        }
        result = function_to_string(func)
        assert result == "async () => data"


class TestToStringOptions:
    """Test toString with different options"""

    def test_synthetic_function(self):
        """Function without original source"""
        func = {
            "type": "function",
            "name": "synthetic",
            "params": ["a", "b"],
            "body": "return a + b;"
        }
        result = function_to_string(func)
        assert "function synthetic(a, b)" in result
        assert "return a + b;" in result

    def test_exclude_source(self):
        """Option to not include source"""
        func = {
            "type": "function",
            "name": "foo",
            "source": "function foo() { secret(); }"
        }
        options = ToStringOptions(include_source=False)
        result = function_to_string(func, options)
        assert result == "function foo() { [native code] }"
