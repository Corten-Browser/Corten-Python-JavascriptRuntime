"""
Test suite for Function length property (FR-ES24-B-043)

Tests correct parameter counting with various parameter types.
"""

import pytest
from components.function_edge_cases.src.length import calculate_length, LengthCalculation


class TestLengthBasicParameters:
    """Test length with basic parameter lists"""

    def test_no_parameters(self):
        """Function with no parameters has length 0"""
        func = {"params": []}
        result = calculate_length(func)
        assert result["length"] == 0

    def test_one_parameter(self):
        """Function with one parameter has length 1"""
        func = {"params": [{"name": "a", "type": "required"}]}
        result = calculate_length(func)
        assert result["length"] == 1

    def test_multiple_parameters(self):
        """Function with multiple parameters"""
        func = {"params": [
            {"name": "a", "type": "required"},
            {"name": "b", "type": "required"},
            {"name": "c", "type": "required"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 3


class TestLengthDefaultParameters:
    """Test length with default parameters"""

    def test_stop_at_first_default(self):
        """Length stops at first default parameter"""
        func = {"params": [
            {"name": "a", "type": "required"},
            {"name": "b", "type": "default", "default_value": 1},
            {"name": "c", "type": "required"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 1

    def test_all_default_parameters(self):
        """All parameters have defaults"""
        func = {"params": [
            {"name": "a", "type": "default", "default_value": 1},
            {"name": "b", "type": "default", "default_value": 2}
        ]}
        result = calculate_length(func)
        assert result["length"] == 0

    def test_defaults_at_end(self):
        """Default parameters at end"""
        func = {"params": [
            {"name": "a", "type": "required"},
            {"name": "b", "type": "required"},
            {"name": "c", "type": "default", "default_value": 3}
        ]}
        result = calculate_length(func)
        assert result["length"] == 2


class TestLengthRestParameters:
    """Test length with rest parameters"""

    def test_rest_parameter_excluded(self):
        """Rest parameter not counted in length"""
        func = {"params": [
            {"name": "a", "type": "required"},
            {"name": "rest", "type": "rest"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 1

    def test_only_rest_parameter(self):
        """Function with only rest parameter"""
        func = {"params": [
            {"name": "args", "type": "rest"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 0

    def test_required_and_rest(self):
        """Required parameters before rest"""
        func = {"params": [
            {"name": "a", "type": "required"},
            {"name": "b", "type": "required"},
            {"name": "rest", "type": "rest"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 2


class TestLengthDestructuredParameters:
    """Test length with destructured parameters"""

    def test_object_destructuring_counts_as_one(self):
        """Object destructuring counts as one parameter"""
        func = {"params": [
            {"name": "{a, b}", "type": "destructured"},
            {"name": "c", "type": "required"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 2

    def test_array_destructuring_counts_as_one(self):
        """Array destructuring counts as one parameter"""
        func = {"params": [
            {"name": "[x, y]", "type": "destructured"},
            {"name": "z", "type": "required"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 2

    def test_nested_destructuring(self):
        """Nested destructuring counts as one parameter"""
        func = {"params": [
            {"name": "{a: {b, c}}", "type": "destructured"}
        ]}
        result = calculate_length(func)
        assert result["length"] == 1


class TestLengthBoundFunctions:
    """Test length for bound functions"""

    def test_bound_function_reduces_length(self):
        """Bound function length = max(0, original.length - boundArgs.length)"""
        original_func = {"length": 3}
        bound_func = {
            "type": "bound",
            "target_function": original_func,
            "bound_args": [1]
        }
        result = calculate_length(bound_func)
        assert result["length"] == 2  # 3 - 1

    def test_bound_function_length_minimum_zero(self):
        """Bound function length never negative"""
        original_func = {"length": 2}
        bound_func = {
            "type": "bound",
            "target_function": original_func,
            "bound_args": [1, 2, 3, 4]
        }
        result = calculate_length(bound_func)
        assert result["length"] == 0  # max(0, 2 - 4)

    def test_double_bound_function_length(self):
        """Double bound function calculates length correctly"""
        original_func = {"length": 5}
        bound1 = {
            "type": "bound",
            "target_function": original_func,
            "bound_args": [1, 2]
        }
        bound2 = {
            "type": "bound",
            "target_function": bound1,
            "bound_args": [3]
        }
        # Should be max(0, original - total_bound_args)
        # or step by step: 5 -> 3 -> 2
        result = calculate_length(bound2)
        assert result["length"] == 2  # (5 - 2) - 1


class TestLengthEdgeCases:
    """Test edge cases for length calculation"""

    def test_arrow_function_length(self):
        """Arrow function length calculated same as normal"""
        func = {
            "type": "arrow",
            "params": [{"name": "x", "type": "required"}]
        }
        result = calculate_length(func)
        assert result["length"] == 1

    def test_generator_function_length(self):
        """Generator function length calculated same as normal"""
        func = {
            "type": "generator",
            "params": [
                {"name": "a", "type": "required"},
                {"name": "b", "type": "default", "default_value": 1}
            ]
        }
        result = calculate_length(func)
        assert result["length"] == 1  # Stops at default

    def test_async_function_length(self):
        """Async function length calculated same as normal"""
        func = {
            "type": "async",
            "params": [
                {"name": "x", "type": "required"},
                {"name": "y", "type": "required"}
            ]
        }
        result = calculate_length(func)
        assert result["length"] == 2
