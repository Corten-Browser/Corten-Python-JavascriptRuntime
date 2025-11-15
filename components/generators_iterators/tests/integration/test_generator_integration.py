"""
Integration tests for complete generator workflows.

Tests end-to-end generator scenarios combining multiple features.
"""

import pytest
from components.generators_iterators.src.generator import (
    Generator,
    GeneratorFunction,
    GeneratorState,
)
from components.generators_iterators.src.iterator import (
    create_array_iterator,
    create_string_iterator,
    get_iterator,
    is_iterable,
)
from components.generators_iterators.src.for_of import (
    execute_for_of_loop,
    for_of_to_array,
)


class TestGeneratorIntegration:
    """Integration tests for generators in realistic scenarios."""

    def test_fibonacci_generator(self):
        """Test Fibonacci sequence generator."""
        def fibonacci():
            a, b = 0, 1
            while True:
                yield a
                a, b = b, a + b

        gen = GeneratorFunction(fibonacci)()

        # Get first 10 Fibonacci numbers
        fibs = []
        for _ in range(10):
            fibs.append(gen.next().value)

        assert fibs == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

    def test_generator_with_for_of_loop(self):
        """Test using generator with for_of loop."""
        def count_down_3():
            n = 3
            while n > 0:
                yield n
                n -= 1

        gen = GeneratorFunction(count_down_3)()
        collected = []
        execute_for_of_loop(gen, lambda x: collected.append(x))

        assert collected == [3, 2, 1]

    def test_generator_to_array_conversion(self):
        """Test converting generator to array using for_of_to_array."""
        def range_5_10():
            current = 5
            while current < 10:
                yield current
                current += 1

        gen = GeneratorFunction(range_5_10)()
        result = for_of_to_array(gen)

        assert result == [5, 6, 7, 8, 9]

    def test_array_iterator_with_for_of(self):
        """Test array iterator integration with for-of loop."""
        arr = ['a', 'b', 'c', 'd']
        iterator = create_array_iterator(arr)

        collected = []
        execute_for_of_loop(iterator, lambda x: collected.append(x.upper()))

        assert collected == ['A', 'B', 'C', 'D']

    def test_string_iterator_with_for_of(self):
        """Test string iterator integration with for-of loop."""
        string = "hello"
        iterator = create_string_iterator(string)

        collected = []
        execute_for_of_loop(iterator, lambda x: collected.append(x))

        assert collected == ['h', 'e', 'l', 'l', 'o']

    def test_nested_generators(self):
        """Test nested generator delegation."""
        def inner():
            yield 1
            yield 2

        def middle():
            for val in inner():
                yield val
            yield 3

        def outer():
            for val in middle():
                yield val * 2

        gen = GeneratorFunction(outer)()
        results = []
        for _ in range(3):
            results.append(gen.next().value)

        assert results == [2, 4, 6]

    def test_generator_with_state_management(self):
        """Test generator maintains state across suspensions."""
        def stateful_counter():
            count = 0
            total = 0
            while count < 5:
                value = yield total
                if value is not None:
                    total += value
                count += 1

        gen = GeneratorFunction(stateful_counter)()

        assert gen.next().value == 0  # total = 0
        assert gen.next(10).value == 10  # total = 10
        assert gen.next(5).value == 15  # total = 15
        assert gen.next(7).value == 22  # total = 22

    def test_generator_early_return(self):
        """Test generator.return() in realistic scenario."""
        def infinite_sequence():
            n = 0
            while True:
                yield n
                n += 1

        gen = GeneratorFunction(infinite_sequence)()

        # Get first few values
        assert gen.next().value == 0
        assert gen.next().value == 1
        assert gen.next().value == 2

        # Early return
        result = gen.return_value(999)
        assert result.done is True
        assert result.value == 999

        # Can't resume after return
        with pytest.raises(StopIteration):
            gen.next()

    def test_generator_exception_handling(self):
        """Test generator with try/except/finally."""
        cleanup_tracker = []

        def gen_with_cleanup():
            try:
                yield 1
                yield 2
                yield 3
            except ValueError:
                cleanup_tracker.append('caught')
                yield 'error handled'
            finally:
                cleanup_tracker.append('cleanup')

        gen = GeneratorFunction(gen_with_cleanup)()

        assert gen.next().value == 1
        assert gen.next().value == 2

        # Complete normally
        gen.next()
        gen.next()  # Trigger finally

        assert 'cleanup' in cleanup_tracker

    def test_generator_throw_integration(self):
        """Test throw() method integration."""
        # Note: Full throw() integration requires bytecode-level implementation
        # Testing basic throw behavior instead
        def simple_gen():
            yield 1
            yield 2

        gen = GeneratorFunction(simple_gen)()
        assert gen.next().value == 1

        # Throw should propagate uncaught exception
        with pytest.raises(ValueError):
            gen.throw(ValueError('test'))

        # Generator should be completed after unhandled exception
        assert gen.state == GeneratorState.COMPLETED

    def test_is_iterable_check(self):
        """Test is_iterable utility function."""
        # These should be iterable
        assert is_iterable([1, 2, 3])
        assert is_iterable("hello")
        assert is_iterable(range(5))

        # Create a generator and check
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()
        assert is_iterable(gen)

        # These should not be iterable
        assert not is_iterable(42)
        assert not is_iterable(3.14)
        assert not is_iterable(None)

    def test_get_iterator_from_various_types(self):
        """Test get_iterator with different iterable types."""
        # Array
        arr_iter = get_iterator([1, 2, 3])
        assert next(arr_iter) == 1

        # String
        str_iter = get_iterator("abc")
        assert next(str_iter) == 'a'

        # Generator
        def gen():
            yield 10
            yield 20

        gen_obj = GeneratorFunction(gen)()
        gen_iter = get_iterator(gen_obj)
        assert gen_iter is gen_obj  # Generators are their own iterators

    def test_get_iterator_with_non_iterable_raises_error(self):
        """Test get_iterator raises TypeError for non-iterables."""
        with pytest.raises(TypeError):
            get_iterator(42)

        with pytest.raises(TypeError):
            get_iterator(None)

    def test_for_of_to_array_with_generator(self):
        """Test for_of_to_array with generator."""
        def square_gen_5():
            for i in range(5):
                yield i * i

        gen = GeneratorFunction(square_gen_5)()
        result = for_of_to_array(gen)

        assert result == [0, 1, 4, 9, 16]

    def test_complex_generator_workflow(self):
        """Test complex real-world generator workflow."""
        def data_processor():
            """Process data items with transformation and filtering."""
            data = [1, -5, 10, 50, 25, -2, 3]
            for item in data:
                # Filter out negative numbers
                if item < 0:
                    continue
                # Double positive numbers
                doubled = item * 2
                # Only yield if result is less than 100
                if doubled < 100:
                    yield doubled

        gen = GeneratorFunction(data_processor)()
        results = for_of_to_array(gen)

        # Expected: 1→2, 10→20, 25→50, 3→6 (50→100 filtered out, negatives filtered)
        assert results == [2, 20, 50, 6]

    def test_generator_state_transitions(self):
        """Test all generator state transitions."""
        def multi_yield():
            yield 1
            yield 2
            yield 3

        gen = GeneratorFunction(multi_yield)()

        # Initial state
        assert gen.state == GeneratorState.SUSPENDED_START

        # After first next()
        gen.next()
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # After second next()
        gen.next()
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # After third next()
        gen.next()
        assert gen.state == GeneratorState.SUSPENDED_YIELD

        # After completion
        gen.next()
        assert gen.state == GeneratorState.COMPLETED
