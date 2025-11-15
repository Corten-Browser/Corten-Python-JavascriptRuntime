"""
Test suite for Function.prototype.bind() edge cases (FR-ES24-B-041)

Tests bound function creation and behavior.
"""

import pytest
from components.function_edge_cases.src.bind import bind_function, BindOptions


class TestBindThisValue:
    """Test binding this value"""

    def test_bind_object_this(self):
        """Bind with object this"""
        func = {"type": "function", "name": "test", "length": 2}
        options = BindOptions(this_arg={"value": 42})
        bound = bind_function(func, options)
        assert bound["bound_this"] == {"value": 42}

    def test_bind_primitive_this(self):
        """Bind with primitive this value"""
        func = {"type": "function", "name": "test", "length": 2}
        options = BindOptions(this_arg=42)
        bound = bind_function(func, options)
        assert bound["bound_this"] == 42

    def test_bind_null_this(self):
        """Bind with null this"""
        func = {"type": "function", "name": "test", "length": 2}
        options = BindOptions(this_arg=None)
        bound = bind_function(func, options)
        assert bound["bound_this"] is None


class TestBindArguments:
    """Test binding arguments"""

    def test_bind_with_one_argument(self):
        """Bind with single argument"""
        func = {"type": "function", "name": "add", "length": 2}
        options = BindOptions(this_arg=None, args=[1])
        bound = bind_function(func, options)
        assert bound["bound_args"] == [1]
        assert bound["length"] == 1  # 2 - 1

    def test_bind_with_multiple_arguments(self):
        """Bind with multiple arguments"""
        func = {"type": "function", "name": "sum", "length": 3}
        options = BindOptions(this_arg=None, args=[1, 2])
        bound = bind_function(func, options)
        assert bound["bound_args"] == [1, 2]
        assert bound["length"] == 1  # 3 - 2

    def test_bind_with_more_args_than_params(self):
        """Bind with more args than parameters"""
        func = {"type": "function", "name": "test", "length": 1}
        options = BindOptions(this_arg=None, args=[1, 2, 3])
        bound = bind_function(func, options)
        assert bound["bound_args"] == [1, 2, 3]
        assert bound["length"] == 0  # max(0, 1 - 3)

    def test_bind_no_arguments(self):
        """Bind without arguments"""
        func = {"type": "function", "name": "test", "length": 2}
        options = BindOptions(this_arg={"x": 1}, args=[])
        bound = bind_function(func, options)
        assert bound["bound_args"] == []
        assert bound["length"] == 2


class TestBindName:
    """Test bound function name"""

    def test_bound_function_name(self):
        """Bound function has 'bound ' prefix"""
        func = {"type": "function", "name": "foo", "length": 1}
        options = BindOptions(this_arg=None)
        bound = bind_function(func, options)
        assert bound["name"] == "bound foo"

    def test_bound_anonymous_function(self):
        """Bound anonymous function"""
        func = {"type": "function", "name": "", "length": 1}
        options = BindOptions(this_arg=None)
        bound = bind_function(func, options)
        assert bound["name"] == "bound "

    def test_preserve_name_option(self):
        """Option to preserve original name"""
        func = {"type": "function", "name": "bar", "length": 1}
        options = BindOptions(this_arg=None, preserve_name=False)
        bound = bind_function(func, options)
        # When not preserving, still add "bound " prefix per spec
        assert bound["name"] == "bound bar"


class TestBindLength:
    """Test bound function length calculation"""

    def test_length_with_zero_bound_args(self):
        """Length unchanged with no bound args"""
        func = {"type": "function", "name": "test", "length": 3}
        options = BindOptions(this_arg=None, args=[])
        bound = bind_function(func, options)
        assert bound["length"] == 3

    def test_length_reduced_by_bound_args(self):
        """Length reduced by number of bound args"""
        func = {"type": "function", "name": "test", "length": 5}
        options = BindOptions(this_arg=None, args=[1, 2, 3])
        bound = bind_function(func, options)
        assert bound["length"] == 2  # 5 - 3

    def test_length_minimum_zero(self):
        """Length never goes negative"""
        func = {"type": "function", "name": "test", "length": 1}
        options = BindOptions(this_arg=None, args=[1, 2, 3, 4, 5])
        bound = bind_function(func, options)
        assert bound["length"] == 0  # max(0, 1 - 5)


class TestBindPrototype:
    """Test bound function prototype handling"""

    def test_bound_function_no_prototype(self):
        """Bound function has no prototype property"""
        func = {"type": "function", "name": "test", "length": 1, "prototype": {}}
        options = BindOptions(this_arg=None)
        bound = bind_function(func, options)
        assert "prototype" not in bound or bound.get("prototype") is None


class TestBindDouble:
    """Test binding already bound functions"""

    def test_double_bind(self):
        """Binding a bound function creates a chain"""
        func = {"type": "function", "name": "original", "length": 2}
        options1 = BindOptions(this_arg={"first": 1}, args=[1])
        bound1 = bind_function(func, options1)

        options2 = BindOptions(this_arg={"second": 2}, args=[2])
        bound2 = bind_function(bound1, options2)

        # First bind's this should be preserved
        assert bound2["bound_this"] == {"first": 1}
        assert bound2["bound_args"] == [1, 2]
        assert bound2["name"] == "bound bound original"

    def test_triple_bind(self):
        """Multiple binds create longer chain"""
        func = {"type": "function", "name": "test", "length": 3}
        bound1 = bind_function(func, BindOptions(this_arg=1, args=[1]))
        bound2 = bind_function(bound1, BindOptions(this_arg=2, args=[2]))
        bound3 = bind_function(bound2, BindOptions(this_arg=3, args=[3]))

        assert bound3["bound_this"] == 1  # First bind wins
        assert bound3["bound_args"] == [1, 2, 3]


class TestBindArrowFunction:
    """Test binding arrow functions"""

    def test_bind_arrow_function(self):
        """Binding arrow function preserves lexical this"""
        func = {
            "type": "arrow",
            "name": "arrow",
            "length": 1,
            "lexical_this": {"original": "context"}
        }
        options = BindOptions(this_arg={"new": "context"})
        bound = bind_function(func, options)

        # Arrow function should keep lexical this
        assert bound["type"] == "bound"
        assert bound["target_function"]["lexical_this"] == {"original": "context"}
