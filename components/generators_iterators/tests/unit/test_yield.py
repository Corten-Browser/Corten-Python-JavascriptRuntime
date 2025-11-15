"""
Unit tests for yield expression functionality.

Tests basic yield behavior, value yielding, and yield expression evaluation.

Following TDD: These tests are written FIRST (RED phase).
"""

import pytest
from components.generators_iterators.src.generator import (
    Generator,
    GeneratorFunction,
    IteratorResult,
)


class TestBasicYield:
    """Test basic yield expression behavior."""

    def test_yield_suspends_generator_execution(self):
        """
        Given a generator with a yield statement
        When next() is called
        Then execution suspends at yield and returns the yielded value
        """
        # Given
        def simple_gen():
            yield 42

        gen = GeneratorFunction(simple_gen)()

        # When
        result = gen.next()

        # Then
        assert result.value == 42
        assert result.done is False

    def test_yield_returns_iterator_result_object(self):
        """
        Given a generator yields a value
        When next() is called
        Then an IteratorResult object is returned with value and done properties
        """
        # Given
        def simple_gen():
            yield "hello"

        gen = GeneratorFunction(simple_gen)()

        # When
        result = gen.next()

        # Then
        assert isinstance(result, IteratorResult)
        assert hasattr(result, 'value')
        assert hasattr(result, 'done')
        assert result.value == "hello"
        assert result.done is False

    def test_multiple_yields_return_in_sequence(self):
        """
        Given a generator with multiple yield statements
        When next() is called multiple times
        Then each yield value is returned in sequence
        """
        # Given
        def multi_yield():
            yield 1
            yield 2
            yield 3

        gen = GeneratorFunction(multi_yield)()

        # When / Then
        result1 = gen.next()
        assert result1.value == 1
        assert result1.done is False

        result2 = gen.next()
        assert result2.value == 2
        assert result2.done is False

        result3 = gen.next()
        assert result3.value == 3
        assert result3.done is False

    def test_yield_with_expression(self):
        """
        Given a generator that yields expressions
        When next() is called
        Then the expression is evaluated and its result is yielded
        """
        # Given
        def expr_gen():
            yield 2 + 2
            yield 10 * 5
            yield "hello" + " world"

        gen = GeneratorFunction(expr_gen)()

        # When / Then
        assert gen.next().value == 4
        assert gen.next().value == 50
        assert gen.next().value == "hello world"

    def test_yield_undefined_when_no_value_specified(self):
        """
        Given a yield with no value
        When next() is called
        Then undefined is yielded
        """
        # Given
        def undefined_yield():
            yield  # No value specified

        gen = GeneratorFunction(undefined_yield)()

        # When
        result = gen.next()

        # Then
        assert result.value is None  # Python None represents JS undefined
        assert result.done is False

    def test_generator_completion_returns_done_true(self):
        """
        Given a generator that has yielded all values
        When next() is called after the last yield
        Then IteratorResult has done: true
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # When
        gen.next()  # Get the yielded value
        result = gen.next()  # Generator completes

        # Then
        assert result.done is True
        assert result.value is None  # undefined by default

    def test_yield_inside_loop(self):
        """
        Given a generator with yield inside a loop
        When iterating with next()
        Then each loop iteration yields a value
        """
        # Given
        def loop_gen():
            for i in range(5):
                yield i

        gen = GeneratorFunction(loop_gen)()

        # When / Then
        for expected in range(5):
            result = gen.next()
            assert result.value == expected
            assert result.done is False

        # Final next() completes
        result = gen.next()
        assert result.done is True

    def test_yield_with_conditional(self):
        """
        Given a generator with conditional yields
        When next() is called
        Then only values meeting the condition are yielded
        """
        # Given
        def conditional_gen():
            for i in range(10):
                if i % 2 == 0:  # Only even numbers
                    yield i

        gen = GeneratorFunction(conditional_gen)()

        # When / Then
        expected_values = [0, 2, 4, 6, 8]
        for expected in expected_values:
            result = gen.next()
            assert result.value == expected
            assert result.done is False

    def test_yield_preserves_local_state(self):
        """
        Given a generator with local variables
        When suspended at yield and then resumed
        Then local variable values are preserved
        """
        # Given
        def stateful_gen():
            count = 0
            while count < 3:
                count += 1
                yield count

        gen = GeneratorFunction(stateful_gen)()

        # When / Then
        assert gen.next().value == 1
        assert gen.next().value == 2
        assert gen.next().value == 3

    def test_yield_with_try_finally(self):
        """
        Given a generator with yield in try block
        When the generator executes
        Then finally block executes after generator completes
        """
        # Given
        executed_finally = []

        def finally_gen():
            try:
                yield 1
                yield 2
            finally:
                executed_finally.append(True)

        gen = GeneratorFunction(finally_gen)()

        # When
        gen.next()  # yield 1
        gen.next()  # yield 2
        gen.next()  # complete generator

        # Then
        assert executed_finally == [True]


class TestYieldValue:
    """Test various types of values that can be yielded."""

    def test_yield_number(self):
        """Test yielding numeric values."""
        def num_gen():
            yield 42
            yield 3.14
            yield -17

        gen = GeneratorFunction(num_gen)()

        assert gen.next().value == 42
        assert gen.next().value == 3.14
        assert gen.next().value == -17

    def test_yield_string(self):
        """Test yielding string values."""
        def str_gen():
            yield "hello"
            yield "world"

        gen = GeneratorFunction(str_gen)()

        assert gen.next().value == "hello"
        assert gen.next().value == "world"

    def test_yield_boolean(self):
        """Test yielding boolean values."""
        def bool_gen():
            yield True
            yield False

        gen = GeneratorFunction(bool_gen)()

        assert gen.next().value is True
        assert gen.next().value is False

    def test_yield_null(self):
        """Test yielding null."""
        def null_gen():
            yield None

        gen = GeneratorFunction(null_gen)()

        assert gen.next().value is None

    def test_yield_object(self):
        """Test yielding object values."""
        def obj_gen():
            yield {"name": "Alice", "age": 30}
            yield {"x": 10, "y": 20}

        gen = GeneratorFunction(obj_gen)()

        result1 = gen.next().value
        assert result1 == {"name": "Alice", "age": 30}

        result2 = gen.next().value
        assert result2 == {"x": 10, "y": 20}

    def test_yield_array(self):
        """Test yielding array values."""
        def arr_gen():
            yield [1, 2, 3]
            yield ["a", "b", "c"]

        gen = GeneratorFunction(arr_gen)()

        assert gen.next().value == [1, 2, 3]
        assert gen.next().value == ["a", "b", "c"]

    def test_yield_function(self):
        """Test yielding function values."""
        def func_gen():
            def helper():
                return "helper"
            yield helper

        gen = GeneratorFunction(func_gen)()

        result = gen.next().value
        assert callable(result)
        assert result() == "helper"
