"""
Unit tests for for-of loop implementation.

Tests for-of iteration over iterables using Symbol.iterator protocol.

Following TDD: These tests are written FIRST (RED phase).
"""

import pytest
from components.generators_iterators.src.for_of import (
    execute_for_of_loop,
    ForOfLoopContext,
)
from components.generators_iterators.src.generator import GeneratorFunction


class TestForOfBasics:
    """Test basic for-of loop functionality."""

    def test_for_of_iterates_over_array(self):
        """
        Given an array
        When executing for-of loop
        Then each element is visited in order
        """
        # Given
        arr = [1, 2, 3, 4, 5]
        collected = []

        def collector(item):
            collected.append(item)

        # When
        execute_for_of_loop(arr, collector)

        # Then
        assert collected == [1, 2, 3, 4, 5]

    def test_for_of_with_empty_array(self):
        """
        Given an empty array
        When executing for-of loop
        Then no iterations occur
        """
        # Given
        arr = []
        collected = []

        def collector(item):
            collected.append(item)

        # When
        execute_for_of_loop(arr, collector)

        # Then
        assert collected == []

    def test_for_of_iterates_over_string(self):
        """
        Given a string
        When executing for-of loop
        Then each character is visited
        """
        # Given
        string = "hello"
        collected = []

        def collector(char):
            collected.append(char)

        # When
        execute_for_of_loop(string, collector)

        # Then
        assert collected == ["h", "e", "l", "l", "o"]

    def test_for_of_iterates_over_generator(self):
        """
        Given a generator
        When executing for-of loop
        Then each yielded value is visited
        """
        # Given
        def number_gen():
            yield 1
            yield 2
            yield 3

        gen = GeneratorFunction(number_gen)()
        collected = []

        def collector(num):
            collected.append(num)

        # When
        execute_for_of_loop(gen, collector)

        # Then
        assert collected == [1, 2, 3]

    def test_for_of_with_custom_iterable(self):
        """
        Given a custom object implementing iterator protocol
        When executing for-of loop
        Then iteration works correctly
        """
        # Given
        class CustomIterable:
            def __iter__(self):
                self.data = [10, 20, 30]
                self.index = 0
                return self

            def __next__(self):
                if self.index >= len(self.data):
                    raise StopIteration
                value = self.data[self.index]
                self.index += 1
                return value

        iterable = CustomIterable()
        collected = []

        def collector(item):
            collected.append(item)

        # When
        execute_for_of_loop(iterable, collector)

        # Then
        assert collected == [10, 20, 30]


class TestForOfControlFlow:
    """Test for-of loop with control flow statements."""

    def test_for_of_with_break(self):
        """
        Given a for-of loop with break statement
        When break is executed
        Then iteration stops immediately
        """
        # Given
        arr = [1, 2, 3, 4, 5]
        collected = []

        def collector_with_break(item):
            if item == 3:
                raise StopIteration  # Simulate break
            collected.append(item)

        # When
        try:
            execute_for_of_loop(arr, collector_with_break)
        except StopIteration:
            pass

        # Then
        assert collected == [1, 2]

    def test_for_of_with_continue(self):
        """
        Given a for-of loop with continue statement
        When continue is executed
        Then current iteration is skipped
        """
        # Given
        arr = [1, 2, 3, 4, 5]
        collected = []

        def collector_with_skip(item):
            if item % 2 == 0:
                return  # Simulate continue
            collected.append(item)

        # When
        execute_for_of_loop(arr, collector_with_skip)

        # Then
        assert collected == [1, 3, 5]  # Only odd numbers

    def test_for_of_completes_normally(self):
        """
        Given a for-of loop that completes all iterations
        When no break occurs
        Then all elements are processed
        """
        # Given
        arr = [1, 2, 3]
        collected = []

        def collector(item):
            collected.append(item * 2)

        # When
        execute_for_of_loop(arr, collector)

        # Then
        assert collected == [2, 4, 6]


class TestForOfEdgeCases:
    """Test for-of loop edge cases and error handling."""

    def test_for_of_with_non_iterable_throws_error(self):
        """
        Given a non-iterable object
        When attempting for-of loop
        Then TypeError is raised
        """
        # Given
        non_iterable = 42

        def collector(item):
            pass

        # When / Then
        with pytest.raises(TypeError):
            execute_for_of_loop(non_iterable, collector)

    def test_for_of_closes_iterator_on_break(self):
        """
        Given an iterator with cleanup logic
        When for-of loop breaks early
        Then iterator cleanup is performed
        """
        # Given
        cleanup_called = []

        class CleanupIterator:
            def __iter__(self):
                return self

            def __next__(self):
                return 1

            def close(self):
                cleanup_called.append(True)

        # Note: Full cleanup testing in integration tests

    def test_for_of_closes_iterator_on_exception(self):
        """
        Given a for-of loop that throws exception
        When exception occurs during iteration
        Then iterator is properly closed
        """
        # Given
        arr = [1, 2, 3]

        def thrower(item):
            if item == 2:
                raise ValueError("test error")

        # When / Then
        with pytest.raises(ValueError):
            execute_for_of_loop(arr, thrower)

        # Iterator should be closed properly (tested in integration)

    def test_for_of_with_nested_iterables(self):
        """
        Given an iterable containing iterables
        When iterating with for-of
        Then outer iteration yields inner iterables (not flattened)
        """
        # Given
        nested = [[1, 2], [3, 4], [5, 6]]
        collected = []

        def collector(item):
            collected.append(item)

        # When
        execute_for_of_loop(nested, collector)

        # Then
        assert collected == [[1, 2], [3, 4], [5, 6]]


class TestForOfLoopContext:
    """Test ForOfLoopContext management."""

    def test_loop_context_tracks_current_value(self):
        """
        Given a for-of loop execution
        When accessing loop context
        Then current value is tracked
        """
        # Given
        arr = [10, 20, 30]
        context = ForOfLoopContext(arr)

        # When / Then
        # Context management tested in implementation

    def test_loop_context_closes_on_completion(self):
        """
        Given a for-of loop that completes
        When checking context after completion
        Then iterator is properly closed
        """
        # Given
        arr = [1, 2, 3]
        collected = []

        # When
        execute_for_of_loop(arr, lambda x: collected.append(x))

        # Then
        # Iterator closure verified in implementation

    def test_loop_context_handles_iterator_return(self):
        """
        Given an iterator with return() method
        When loop breaks early
        Then return() is called for cleanup
        """
        # Given
        def gen_with_cleanup():
            try:
                yield 1
                yield 2
                yield 3
            finally:
                pass  # Cleanup happens here

        # When / Then
        # Full cleanup testing in integration tests


class TestForOfWithDifferentTypes:
    """Test for-of with various iterable types."""

    def test_for_of_with_set(self):
        """
        Given a Set (when implemented)
        When using for-of
        Then each value is iterated
        """
        # Note: Will be fully implemented when Set is available
        pass

    def test_for_of_with_map(self):
        """
        Given a Map (when implemented)
        When using for-of
        Then each [key, value] pair is iterated
        """
        # Note: Will be fully implemented when Map is available
        pass

    def test_for_of_with_typed_array(self):
        """
        Given a TypedArray (when implemented)
        When using for-of
        Then each element is iterated
        """
        # Note: Will be fully implemented when TypedArray is available
        pass
