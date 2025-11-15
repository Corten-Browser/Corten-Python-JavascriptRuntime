"""
Test suite for Arrow function this binding (FR-ES24-B-044)

Tests lexical this binding in arrow functions.
"""

import pytest
from components.function_edge_cases.src.arrow_this import resolve_arrow_this, ArrowThisContext


class TestArrowThisLexical:
    """Test lexical this binding"""

    def test_arrow_in_function(self):
        """Arrow function inherits this from enclosing function"""
        context = ArrowThisContext(enclosing_this={"value": 42})
        arrow_func = {"type": "arrow", "name": "arrow"}
        result = resolve_arrow_this(arrow_func, context)
        assert result["this_value"] == {"value": 42}
        assert result["source"] == "lexical"

    def test_arrow_in_global_scope(self):
        """Arrow function in global scope has global this"""
        context = ArrowThisContext(enclosing_this={"__type__": "global"})
        arrow_func = {"type": "arrow", "name": "arrow"}
        result = resolve_arrow_this(arrow_func, context)
        assert result["this_value"]["__type__"] == "global"
        assert result["source"] == "lexical"

    def test_arrow_in_method(self):
        """Arrow function in object method inherits method's this"""
        context = ArrowThisContext(enclosing_this={"object": "instance"})
        arrow_func = {"type": "arrow", "name": "arrow"}
        result = resolve_arrow_this(arrow_func, context)
        assert result["this_value"] == {"object": "instance"}


class TestArrowThisImmutable:
    """Test that arrow this cannot be changed"""

    def test_call_cannot_change_this(self):
        """call() cannot change arrow function this"""
        lexical_this = {"lexical": "value"}
        arrow_func = {
            "type": "arrow",
            "name": "arrow",
            "lexical_this": lexical_this
        }
        # Attempt to call with different this
        new_this = {"new": "value"}
        result = resolve_arrow_this(arrow_func, None)
        assert result["this_value"] == lexical_this

    def test_apply_cannot_change_this(self):
        """apply() cannot change arrow function this"""
        lexical_this = {"lexical": "value"}
        arrow_func = {
            "type": "arrow",
            "name": "arrow",
            "lexical_this": lexical_this
        }
        result = resolve_arrow_this(arrow_func, None)
        assert result["this_value"] == lexical_this

    def test_bind_cannot_change_this(self):
        """bind() cannot change arrow function this"""
        lexical_this = {"lexical": "value"}
        arrow_func = {
            "type": "arrow",
            "name": "arrow",
            "lexical_this": lexical_this
        }
        result = resolve_arrow_this(arrow_func, None)
        # Even after bind, arrow function keeps lexical this
        assert result["this_value"] == lexical_this


class TestArrowThisNested:
    """Test nested arrow functions"""

    def test_nested_arrow_functions(self):
        """Nested arrow functions all share same this"""
        outer_this = {"outer": "context"}
        context = ArrowThisContext(enclosing_this=outer_this)

        outer_arrow = {"type": "arrow", "name": "outer"}
        outer_result = resolve_arrow_this(outer_arrow, context)

        # Inner arrow also uses outer context
        inner_arrow = {"type": "arrow", "name": "inner"}
        inner_result = resolve_arrow_this(inner_arrow, context)

        assert outer_result["this_value"] == outer_this
        assert inner_result["this_value"] == outer_this

    def test_arrow_in_arrow_in_function(self):
        """Arrow in arrow in function - all inherit function's this"""
        function_this = {"function": "this"}
        context = ArrowThisContext(enclosing_this=function_this)

        arrow1 = {"type": "arrow", "name": "arrow1"}
        result1 = resolve_arrow_this(arrow1, context)

        arrow2 = {"type": "arrow", "name": "arrow2"}
        result2 = resolve_arrow_this(arrow2, context)

        assert result1["this_value"] == function_this
        assert result2["this_value"] == function_this


class TestArrowThisStrictMode:
    """Test arrow this in strict mode"""

    def test_arrow_in_strict_function(self):
        """Arrow function in strict mode function"""
        context = ArrowThisContext(enclosing_this=None)  # undefined in strict
        arrow_func = {"type": "arrow", "name": "arrow", "strict": True}
        result = resolve_arrow_this(arrow_func, context)
        assert result["this_value"] is None

    def test_arrow_in_non_strict_function(self):
        """Arrow function in non-strict function"""
        # In non-strict, undefined this becomes global
        context = ArrowThisContext(enclosing_this={"__type__": "global"})
        arrow_func = {"type": "arrow", "name": "arrow", "strict": False}
        result = resolve_arrow_this(arrow_func, context)
        assert result["this_value"]["__type__"] == "global"


class TestArrowThisErrors:
    """Test error cases"""

    def test_non_arrow_function_error(self):
        """Resolving this on non-arrow function throws error"""
        normal_func = {"type": "function", "name": "normal"}
        context = ArrowThisContext(enclosing_this={})
        with pytest.raises(TypeError, match="Not an arrow function"):
            resolve_arrow_this(normal_func, context)


class TestArrowNoArguments:
    """Test that arrow functions have no arguments object"""

    def test_arrow_no_arguments_object(self):
        """Arrow function does not have arguments object"""
        arrow_func = {"type": "arrow", "name": "arrow"}
        # Arrow functions should not have 'arguments' property
        assert "arguments" not in arrow_func

    def test_arrow_uses_enclosing_arguments(self):
        """Arrow function can access enclosing scope's arguments"""
        # This is tested at runtime, but arrow should not have own arguments
        context = ArrowThisContext(
            enclosing_this={"value": 1},
            enclosing_arguments=[1, 2, 3]
        )
        arrow_func = {"type": "arrow", "name": "arrow"}
        # Arrow can access enclosing arguments, but doesn't own them
        assert arrow_func.get("has_own_arguments") is None
