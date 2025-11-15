"""
Test suite for Function.prototype.name edge cases (FR-ES24-B-039)

Tests name inference for all function types and contexts.
"""

import pytest
from components.function_edge_cases.src.name_inference import infer_function_name, NameInferenceContext


class TestNameInferenceAssignment:
    """Test name inference from assignment expressions"""

    def test_const_assignment(self):
        """Name inferred from const assignment"""
        context = NameInferenceContext(assignment_target="foo")
        result = infer_function_name(None, context)
        assert result == "foo"

    def test_let_assignment(self):
        """Name inferred from let assignment"""
        context = NameInferenceContext(assignment_target="bar")
        result = infer_function_name(None, context)
        assert result == "bar"

    def test_var_assignment(self):
        """Name inferred from var assignment"""
        context = NameInferenceContext(assignment_target="baz")
        result = infer_function_name(None, context)
        assert result == "baz"


class TestNameInferenceObjectLiteral:
    """Test name inference from object literals"""

    def test_object_literal_method(self):
        """Name inferred from object literal key"""
        context = NameInferenceContext(object_literal_key="method")
        result = infer_function_name(None, context)
        assert result == "method"

    def test_object_literal_arrow(self):
        """Name inferred from object literal arrow function"""
        context = NameInferenceContext(object_literal_key="arrowMethod")
        result = infer_function_name(None, context)
        assert result == "arrowMethod"

    def test_computed_property_literal(self):
        """Name inferred from computed property with literal"""
        context = NameInferenceContext(object_literal_key="computedKey")
        result = infer_function_name(None, context)
        assert result == "computedKey"

    def test_computed_property_symbol(self):
        """Computed property with symbol has empty name"""
        context = NameInferenceContext(object_literal_key="[Symbol.iterator]")
        result = infer_function_name(None, context)
        assert result == ""


class TestNameInferenceClass:
    """Test name inference from class methods"""

    def test_class_method(self):
        """Name inferred from class method name"""
        context = NameInferenceContext(class_method_name="render")
        result = infer_function_name(None, context)
        assert result == "render"

    def test_class_static_method(self):
        """Name inferred from static method name"""
        context = NameInferenceContext(class_method_name="create")
        result = infer_function_name(None, context)
        assert result == "create"

    def test_class_getter(self):
        """Name inferred from getter name with 'get ' prefix"""
        context = NameInferenceContext(class_method_name="get name")
        result = infer_function_name(None, context)
        assert result == "get name"

    def test_class_setter(self):
        """Name inferred from setter name with 'set ' prefix"""
        context = NameInferenceContext(class_method_name="set name")
        result = infer_function_name(None, context)
        assert result == "set name"


class TestNameInferenceSpecialCases:
    """Test special name inference cases"""

    def test_anonymous_function(self):
        """Anonymous function has empty string name"""
        context = NameInferenceContext(default_name="")
        result = infer_function_name(None, context)
        assert result == ""

    def test_named_function_expression(self):
        """Named function expression uses explicit name"""
        # Function already has explicit name "namedFn"
        result = infer_function_name({"name": "namedFn"}, None)
        assert result == "namedFn"

    def test_default_export(self):
        """Default export function gets 'default' name"""
        context = NameInferenceContext(assignment_target="default")
        result = infer_function_name(None, context)
        assert result == "default"

    def test_property_assignment(self):
        """Name inferred from property assignment"""
        context = NameInferenceContext(assignment_target="method")
        result = infer_function_name(None, context)
        assert result == "method"

    def test_generator_in_object(self):
        """Generator method name inference"""
        context = NameInferenceContext(object_literal_key="gen")
        result = infer_function_name({"is_generator": True}, context)
        assert result == "gen"
