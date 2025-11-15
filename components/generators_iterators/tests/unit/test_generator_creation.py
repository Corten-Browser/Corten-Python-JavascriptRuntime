"""
Unit tests for Generator object creation and basic properties.

Tests generator function declaration, generator object instantiation,
and basic generator state management.

Following TDD: These tests are written FIRST (RED phase).
"""

import pytest
from components.generators_iterators.src.generator import (
    Generator,
    GeneratorState,
    GeneratorFunction,
)


class TestGeneratorCreation:
    """Test generator object creation and initialization."""

    def test_generator_function_creates_generator_object(self):
        """
        Given a generator function is defined
        When the generator function is called
        Then a Generator object is returned
        """
        # Given
        def sample_generator_func():
            """Sample generator function for testing."""
            yield 1
            yield 2

        gen_func = GeneratorFunction(sample_generator_func)

        # When
        gen = gen_func()

        # Then
        assert isinstance(gen, Generator)

    def test_new_generator_has_suspended_start_state(self):
        """
        Given a generator is created
        When checking its initial state
        Then the state is SUSPENDED_START
        """
        # Given / When
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        assert gen.state == GeneratorState.SUSPENDED_START

    def test_generator_has_next_method(self):
        """
        Given a generator object
        When checking for next method
        Then next method exists and is callable
        """
        # Given
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        assert hasattr(gen, 'next')
        assert callable(gen.next)

    def test_generator_has_return_method(self):
        """
        Given a generator object
        When checking for return method
        Then return method exists and is callable
        """
        # Given
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        assert hasattr(gen, 'return_value')
        assert callable(gen.return_value)

    def test_generator_has_throw_method(self):
        """
        Given a generator object
        When checking for throw method
        Then throw method exists and is callable
        """
        # Given
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        assert hasattr(gen, 'throw')
        assert callable(gen.throw)

    def test_generator_stores_generator_function_reference(self):
        """
        Given a generator is created from a generator function
        When checking the generator's function reference
        Then it references the original generator function
        """
        # Given
        def sample_gen():
            yield 1

        gen_func = GeneratorFunction(sample_gen)

        # When
        gen = gen_func()

        # Then
        assert gen.generator_function is sample_gen

    def test_each_generator_call_creates_independent_instance(self):
        """
        Given a generator function
        When called multiple times
        Then each call creates a separate independent generator instance
        """
        # Given
        def counter_gen():
            count = 0
            while True:
                yield count
                count += 1

        gen_func = GeneratorFunction(counter_gen)

        # When
        gen1 = gen_func()
        gen2 = gen_func()

        # Then
        assert gen1 is not gen2
        assert gen1.state == GeneratorState.SUSPENDED_START
        assert gen2.state == GeneratorState.SUSPENDED_START

    def test_generator_starts_with_empty_execution_context(self):
        """
        Given a new generator
        When checking its execution context
        Then the context is initialized but not started
        """
        # Given / When
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        assert gen.execution_context is not None
        assert gen.state == GeneratorState.SUSPENDED_START

    def test_generator_has_symbol_iterator_property(self):
        """
        Given a generator object
        When checking for Symbol.iterator
        Then the property exists (generators are iterable)
        """
        # Given
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # Then
        # Note: Symbol.iterator will be implemented via symbols component
        # For now, we test that the generator has the iterator protocol
        assert hasattr(gen, '__iter__')

    def test_generator_iterator_returns_self(self):
        """
        Given a generator object
        When calling its iterator method
        Then it returns itself (generators are their own iterators)
        """
        # Given
        def sample_gen():
            yield 1

        gen = GeneratorFunction(sample_gen)()

        # When
        iterator = iter(gen)

        # Then
        assert iterator is gen


class TestGeneratorStates:
    """Test generator state transitions."""

    def test_generator_state_enum_has_all_states(self):
        """
        Given the GeneratorState enum
        When checking available states
        Then all four required states exist
        """
        # Then
        assert hasattr(GeneratorState, 'SUSPENDED_START')
        assert hasattr(GeneratorState, 'SUSPENDED_YIELD')
        assert hasattr(GeneratorState, 'EXECUTING')
        assert hasattr(GeneratorState, 'COMPLETED')

    def test_completed_generator_cannot_be_resumed(self):
        """
        Given a generator in COMPLETED state
        When attempting to call next()
        Then it raises StopIteration
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()
        # Consume the generator
        next(gen)  # Gets value 1

        # When / Then
        with pytest.raises(StopIteration):
            next(gen)  # Generator is now completed

    def test_generator_state_transitions_correctly(self):
        """
        Given a generator with multiple yields
        When iterating through values
        Then state transitions follow the correct sequence
        """
        # Given
        def multi_yield_gen():
            yield 1
            yield 2
            yield 3

        gen = GeneratorFunction(multi_yield_gen)()

        # Then - initial state
        assert gen.state == GeneratorState.SUSPENDED_START

        # When - first next()
        next(gen)
        # Then - after first yield
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # When - second next()
        next(gen)
        # Then - after second yield
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # When - third next()
        next(gen)
        # Then - after third yield
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # When - final next() exhausts generator
        with pytest.raises(StopIteration):
            next(gen)
        # Then - generator is completed
        assert gen.state == GeneratorState.COMPLETED
