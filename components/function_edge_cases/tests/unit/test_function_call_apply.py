"""
Test suite for Function.prototype.call/apply edge cases (FR-ES24-B-042)

Tests explicit this binding and argument handling.
"""

import pytest
from components.function_edge_cases.src.call_apply import call_function, apply_function, CallApplyOptions


class TestCallThisBinding:
    """Test call() with different this values"""

    def test_call_with_object_this(self):
        """Call with object this value"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg={"x": 1})
        result = call_function(func, options, args=[])
        assert result["this_value"] == {"x": 1}

    def test_call_with_primitive_this_non_strict(self):
        """Call with primitive this in non-strict mode (boxed)"""
        func = {"type": "function", "name": "test", "strict": False}
        options = CallApplyOptions(this_arg=42)
        result = call_function(func, options, args=[])
        # Primitive should be boxed to Number object
        assert result["this_value"] == {"__primitive__": 42, "__type__": "Number"}

    def test_call_with_primitive_this_strict(self):
        """Call with primitive this in strict mode (not boxed)"""
        func = {"type": "function", "name": "test", "strict": True}
        options = CallApplyOptions(this_arg=42)
        result = call_function(func, options, args=[])
        assert result["this_value"] == 42

    def test_call_with_undefined_this_non_strict(self):
        """Call with undefined this in non-strict mode (global)"""
        func = {"type": "function", "name": "test", "strict": False}
        options = CallApplyOptions(this_arg=None)
        result = call_function(func, options, args=[])
        assert result["this_value"]["__type__"] == "global"

    def test_call_with_undefined_this_strict(self):
        """Call with undefined this in strict mode (undefined)"""
        func = {"type": "function", "name": "test", "strict": True}
        options = CallApplyOptions(this_arg=None)
        result = call_function(func, options, args=[])
        assert result["this_value"] is None


class TestCallArrowFunction:
    """Test call() on arrow functions"""

    def test_call_arrow_ignores_this(self):
        """Arrow function ignores this from call()"""
        func = {
            "type": "arrow",
            "name": "arrow",
            "lexical_this": {"original": "context"}
        }
        options = CallApplyOptions(this_arg={"new": "context"})
        result = call_function(func, options, args=[])
        # Arrow function uses lexical this, not call's this
        assert result["this_value"] == {"original": "context"}

    def test_call_arrow_in_strict_mode(self):
        """Arrow function in strict mode still uses lexical this"""
        func = {
            "type": "arrow",
            "name": "arrow",
            "strict": True,
            "lexical_this": {"lexical": True}
        }
        options = CallApplyOptions(this_arg=42)
        result = call_function(func, options, args=[])
        assert result["this_value"] == {"lexical": True}


class TestCallBoundFunction:
    """Test call() on bound functions"""

    def test_call_bound_ignores_this(self):
        """Bound function ignores this from call()"""
        func = {
            "type": "bound",
            "name": "bound foo",
            "bound_this": {"bound": "value"},
            "target_function": {"type": "function", "name": "foo"}
        }
        options = CallApplyOptions(this_arg={"new": "value"})
        result = call_function(func, options, args=[])
        # Bound function uses bound this, not call's this
        assert result["this_value"] == {"bound": "value"}


class TestApplyWithArrays:
    """Test apply() with argument arrays"""

    def test_apply_with_array(self):
        """Apply with array of arguments"""
        func = {"type": "function", "name": "sum"}
        options = CallApplyOptions(this_arg=None, args=[1, 2, 3])
        result = apply_function(func, options)
        assert result["args_used"] == [1, 2, 3]

    def test_apply_with_empty_array(self):
        """Apply with empty array"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg=None, args=[])
        result = apply_function(func, options)
        assert result["args_used"] == []

    def test_apply_with_null_args(self):
        """Apply with null args treated as empty array"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg=None, args=None)
        result = apply_function(func, options)
        assert result["args_used"] == []

    def test_apply_with_undefined_args(self):
        """Apply with undefined args treated as empty array"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg=None, args=None)
        result = apply_function(func, options)
        assert result["args_used"] == []


class TestApplyArrayLike:
    """Test apply() with array-like objects"""

    def test_apply_with_array_like(self):
        """Apply with array-like object"""
        func = {"type": "function", "name": "test"}
        args_like = {"0": "a", "1": "b", "length": 2}
        options = CallApplyOptions(this_arg=None, args=args_like)
        result = apply_function(func, options)
        assert result["args_used"] == ["a", "b"]

    def test_apply_with_non_array_like_error(self):
        """Apply with non-array-like throws TypeError"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg=None, args=42)
        with pytest.raises(TypeError, match="not array-like"):
            apply_function(func, options)


class TestCallApplyArguments:
    """Test call/apply argument handling"""

    def test_call_with_multiple_args(self):
        """Call with multiple arguments"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(this_arg=None)
        result = call_function(func, options, args=[1, "two", True])
        # Just verify call succeeds and returns result structure
        assert "result" in result

    def test_apply_preserves_arg_types(self):
        """Apply preserves argument types"""
        func = {"type": "function", "name": "test"}
        options = CallApplyOptions(
            this_arg=None,
            args=[1, "string", True, None, {"obj": "value"}]
        )
        result = apply_function(func, options)
        assert result["args_used"] == [1, "string", True, None, {"obj": "value"}]
