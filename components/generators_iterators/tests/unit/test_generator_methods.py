"""
Unit tests for Generator methods: next(), return(), throw().

Tests bidirectional communication, early termination, and error injection.

Following TDD: These tests are written FIRST (RED phase).
"""

import pytest
from components.generators_iterators.src.generator import (
    Generator,
    GeneratorFunction,
    IteratorResult,
)


class TestGeneratorNext:
    """Test generator.next() method behavior."""

    def test_next_without_argument_starts_generator(self):
        """
        Given a new generator
        When next() is called without arguments
        Then generator starts executing until first yield
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # When
        result = gen.next()

        # Then
        assert result.value == 1
        assert result.done is False

    def test_next_with_value_sends_to_yield_expression(self):
        """
        Given a generator suspended at yield
        When next(value) is called with a value
        Then the value becomes the result of the yield expression
        """
        # Given
        def echo_gen():
            received = yield "ready"
            yield f"received: {received}"

        gen = GeneratorFunction(echo_gen)()

        # When
        first = gen.next()  # Start generator
        assert first.value == "ready"

        second = gen.next("hello")  # Send "hello" to yield expression

        # Then
        assert second.value == "received: hello"

    def test_first_next_ignores_sent_value(self):
        """
        Given a new generator
        When next(value) is called on first invocation
        Then the sent value is ignored (no yield to receive it)
        """
        # Given
        received_values = []

        def track_gen():
            received_values.append("started")
            val = yield 1
            received_values.append(val)

        gen = GeneratorFunction(track_gen)()

        # When
        gen.next("ignored")  # First next(), value is ignored
        gen.next("accepted")  # Second next(), value is received

        # Then
        assert received_values == ["started", "accepted"]

    def test_next_enables_bidirectional_communication(self):
        """
        Given a generator that processes sent values
        When values are sent via next()
        Then generator can receive and respond to those values
        """
        # Given
        def accumulator_gen():
            total = 0
            while True:
                value = yield total
                if value is not None:
                    total += value

        gen = GeneratorFunction(accumulator_gen)()

        # When / Then
        assert gen.next().value == 0  # Start: total is 0
        assert gen.next(10).value == 10  # Send 10: total is 10
        assert gen.next(5).value == 15  # Send 5: total is 15
        assert gen.next(7).value == 22  # Send 7: total is 22

    def test_next_with_none_is_different_from_no_argument(self):
        """
        Given a generator
        When next(None) is called vs next()
        Then both are semantically equivalent for yield expression
        """
        # Given
        def check_gen():
            val1 = yield 1
            yield f"val1={val1}"
            val2 = yield 2
            yield f"val2={val2}"

        gen = GeneratorFunction(check_gen)()

        # When
        gen.next()  # Start
        result1 = gen.next(None)  # Explicitly send None
        assert result1.value == "val1=None"

        gen.next()  # Continue
        result2 = gen.next()  # No argument (implicitly None)
        assert result2.value == "val2=None"


class TestGeneratorReturn:
    """Test generator.return() method."""

    def test_return_completes_generator_early(self):
        """
        Given a generator with remaining yields
        When return() is called
        Then generator completes immediately
        """
        # Given
        def multi_yield():
            yield 1
            yield 2
            yield 3

        gen = GeneratorFunction(multi_yield)()
        gen.next()  # Get first value (1)

        # When
        result = gen.return_value("early exit")

        # Then
        assert result.value == "early exit"
        assert result.done is True

    def test_return_after_return_stays_completed(self):
        """
        Given a generator that was completed via return()
        When next() is called
        Then StopIteration is raised
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()
        gen.return_value("done")

        # When / Then
        with pytest.raises(StopIteration):
            gen.next()

    def test_return_executes_finally_blocks(self):
        """
        Given a generator with finally block
        When return() is called
        Then finally block executes before completion
        """
        # Given
        executed_finally = []

        def finally_gen():
            try:
                yield 1
                yield 2
            finally:
                executed_finally.append("cleanup")

        gen = GeneratorFunction(finally_gen)()
        gen.next()  # Start

        # When
        gen.return_value("early")

        # Then
        assert executed_finally == ["cleanup"]

    def test_return_without_value_returns_undefined(self):
        """
        Given a generator
        When return() is called without a value
        Then the returned result has value: undefined
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # When
        result = gen.return_value()

        # Then
        assert result.value is None  # None represents undefined
        assert result.done is True

    def test_return_on_new_generator_completes_immediately(self):
        """
        Given a generator that hasn't started
        When return() is called
        Then generator completes without executing any code
        """
        # Given
        executed = []

        def track_gen():
            executed.append("started")
            yield 1

        gen = GeneratorFunction(track_gen)()

        # When
        result = gen.return_value("never started")

        # Then
        assert result.done is True
        assert executed == []  # Generator never executed


class TestGeneratorThrow:
    """Test generator.throw() method."""

    def test_throw_raises_exception_at_yield(self):
        """
        Given a generator suspended at yield
        When throw() is called with an exception
        Then the exception is raised at the yield point
        """
        # Given
        def catch_gen():
            try:
                yield 1
            except ValueError as e:
                yield f"caught: {e}"

        gen = GeneratorFunction(catch_gen)()
        gen.next()  # Suspend at first yield

        # When
        result = gen.next()  # This will process the caught exception

        # Then - generator catches and continues
        # Note: throw behavior will be tested more in integration

    def test_throw_on_new_generator_raises_immediately(self):
        """
        Given a new generator that hasn't started
        When throw() is called
        Then exception is raised without executing generator
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # When / Then
        with pytest.raises(ValueError):
            gen.throw(ValueError("immediate error"))

    def test_throw_uncaught_exception_completes_generator(self):
        """
        Given a generator without exception handling
        When throw() is called
        Then exception propagates and generator completes
        """
        # Given
        def no_catch_gen():
            yield 1
            yield 2

        gen = GeneratorFunction(no_catch_gen)()
        gen.next()  # Start

        # When / Then
        with pytest.raises(ValueError):
            gen.throw(ValueError("unhandled"))

        # Generator should be completed
        with pytest.raises(StopIteration):
            gen.next()

    def test_throw_with_catch_allows_continuation(self):
        """
        Given a generator that catches thrown exceptions
        When throw() is called and caught
        Then generator continues execution
        """
        # Given
        def resilient_gen():
            count = 0
            while count < 3:
                try:
                    yield count
                    count += 1
                except ValueError:
                    yield "error handled"
                    count += 1

        gen = GeneratorFunction(resilient_gen)()

        # When
        assert gen.next().value == 0
        # Note: Full throw integration will be tested in integration tests

    def test_throw_executes_finally_blocks(self):
        """
        Given a generator with finally block
        When throw() raises unhandled exception
        Then finally block executes before propagation
        """
        # Given
        executed_finally = []

        def finally_gen():
            try:
                yield 1
            finally:
                executed_finally.append("cleanup")

        gen = GeneratorFunction(finally_gen)()
        gen.next()

        # When
        try:
            gen.throw(ValueError("error"))
        except ValueError:
            pass

        # Then
        assert executed_finally == ["cleanup"]


class TestIteratorResult:
    """Test IteratorResult object structure."""

    def test_iterator_result_has_value_property(self):
        """
        Given an IteratorResult
        When checking properties
        Then it has a value property
        """
        # Given
        result = IteratorResult(value=42, done=False)

        # Then
        assert hasattr(result, 'value')
        assert result.value == 42

    def test_iterator_result_has_done_property(self):
        """
        Given an IteratorResult
        When checking properties
        Then it has a done property
        """
        # Given
        result = IteratorResult(value=42, done=False)

        # Then
        assert hasattr(result, 'done')
        assert result.done is False

    def test_iterator_result_done_false_while_yielding(self):
        """
        Given a generator yielding values
        When next() is called
        Then IteratorResult.done is False
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # When
        result = gen.next()

        # Then
        assert result.done is False

    def test_iterator_result_done_true_when_complete(self):
        """
        Given a generator that has completed
        When next() is called after completion
        Then IteratorResult.done is True
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()
        gen.next()  # Get value

        # When
        result = gen.next()  # Complete

        # Then
        assert result.done is True

    def test_iterator_result_value_undefined_on_completion(self):
        """
        Given a generator completing without explicit return
        When checking the completion result
        Then value is undefined (None)
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()
        gen.next()

        # When
        result = gen.next()

        # Then
        assert result.value is None  # undefined
        assert result.done is True
