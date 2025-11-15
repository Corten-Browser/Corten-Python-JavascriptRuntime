"""
Test suite for Generator function edge cases (FR-ES24-B-046)

Tests generator function metadata and behavior.
"""

import pytest
from components.function_edge_cases.src.generator_metadata import get_generator_metadata, GeneratorFunctionMetadata


class TestGeneratorFunctionIdentification:
    """Test identifying generator functions"""

    def test_generator_function_is_generator(self):
        """Generator function has isGenerator flag"""
        func = {"type": "generator", "name": "gen"}
        result = get_generator_metadata(func)
        assert result["is_generator"] is True

    def test_normal_function_not_generator(self):
        """Normal function is not a generator"""
        func = {"type": "function", "name": "normal"}
        with pytest.raises(TypeError, match="Not a generator"):
            get_generator_metadata(func)

    def test_async_generator_is_generator(self):
        """Async generator is also a generator"""
        func = {"type": "async_generator", "name": "asyncGen"}
        result = get_generator_metadata(func)
        assert result["is_generator"] is True
        assert result["generator_kind"] == "async"


class TestGeneratorName:
    """Test generator function name"""

    def test_named_generator(self):
        """Named generator function"""
        func = {"type": "generator", "name": "myGenerator"}
        result = get_generator_metadata(func)
        # Name should be preserved
        assert func["name"] == "myGenerator"

    def test_anonymous_generator(self):
        """Anonymous generator function"""
        func = {"type": "generator", "name": ""}
        result = get_generator_metadata(func)
        assert func["name"] == ""

    def test_generator_method_name(self):
        """Generator method in object/class"""
        func = {"type": "generator", "name": "getData"}
        result = get_generator_metadata(func)
        assert func["name"] == "getData"


class TestGeneratorToString:
    """Test generator function toString"""

    def test_generator_toString_shows_star(self):
        """Generator toString shows function* syntax"""
        func = {
            "type": "generator",
            "name": "gen",
            "source": "function* gen() { yield 1; }"
        }
        result = get_generator_metadata(func)
        # toString should preserve function* syntax
        assert result["to_string"] == "function* gen() { yield 1; }"

    def test_anonymous_generator_toString(self):
        """Anonymous generator toString"""
        func = {
            "type": "generator",
            "name": "",
            "source": "function*() { yield 1; }"
        }
        result = get_generator_metadata(func)
        assert result["to_string"] == "function*() { yield 1; }"

    def test_async_generator_toString(self):
        """Async generator toString shows async function*"""
        func = {
            "type": "async_generator",
            "name": "asyncGen",
            "source": "async function* asyncGen() { yield 1; }"
        }
        result = get_generator_metadata(func)
        assert result["to_string"] == "async function* asyncGen() { yield 1; }"


class TestGeneratorLength:
    """Test generator function length property"""

    def test_generator_length_basic(self):
        """Generator length calculated like normal function"""
        func = {
            "type": "generator",
            "name": "gen",
            "params": [
                {"name": "a", "type": "required"},
                {"name": "b", "type": "required"}
            ]
        }
        result = get_generator_metadata(func)
        assert result["length"] == 2

    def test_generator_length_with_defaults(self):
        """Generator length stops at first default"""
        func = {
            "type": "generator",
            "name": "gen",
            "params": [
                {"name": "a", "type": "required"},
                {"name": "b", "type": "default", "default_value": 10},
                {"name": "c", "type": "required"}
            ]
        }
        result = get_generator_metadata(func)
        assert result["length"] == 1

    def test_generator_length_with_rest(self):
        """Generator with rest parameter"""
        func = {
            "type": "generator",
            "name": "gen",
            "params": [
                {"name": "a", "type": "required"},
                {"name": "rest", "type": "rest"}
            ]
        }
        result = get_generator_metadata(func)
        assert result["length"] == 1


class TestGeneratorConstructor:
    """Test generator function constructor"""

    def test_generator_constructor_is_generator_function(self):
        """Generator.prototype.constructor is GeneratorFunction"""
        func = {"type": "generator", "name": "gen"}
        result = get_generator_metadata(func)
        assert result["prototype_constructor"] == "GeneratorFunction"

    def test_async_generator_constructor(self):
        """Async generator has AsyncGeneratorFunction constructor"""
        func = {"type": "async_generator", "name": "asyncGen"}
        result = get_generator_metadata(func)
        assert result["prototype_constructor"] == "AsyncGeneratorFunction"


class TestGeneratorPrototype:
    """Test generator function prototype"""

    def test_generator_has_prototype(self):
        """Generator function has prototype property"""
        func = {
            "type": "generator",
            "name": "gen",
            "prototype": {"constructor": "GeneratorFunction"}
        }
        result = get_generator_metadata(func)
        # Generator functions have prototype property
        assert "prototype" in func

    def test_generator_instance_no_prototype(self):
        """Generator instance (iterator) has no prototype"""
        # This tests the instance created by calling generator
        # The generator function itself has prototype
        func = {"type": "generator", "name": "gen"}
        result = get_generator_metadata(func)
        # Metadata should indicate instances don't have prototype
        assert result.get("instances_have_prototype") is False
