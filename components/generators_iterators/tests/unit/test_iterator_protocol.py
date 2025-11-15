"""
Unit tests for Iterator protocol implementation.

Tests Symbol.iterator, iterator interface, and iterable objects.

Following TDD: These tests are written FIRST (RED phase).
"""

import pytest
from components.generators_iterators.src.iterator import (
    Iterator,
    Iterable,
    create_array_iterator,
    create_string_iterator,
)
from components.generators_iterators.src.generator import (
    Generator,
    GeneratorFunction,
)


class TestIteratorInterface:
    """Test Iterator interface requirements."""

    def test_iterator_has_next_method(self):
        """
        Given an Iterator object
        When checking its interface
        Then it has a next() method
        """
        # Given
        iterator = create_array_iterator([1, 2, 3])

        # Then
        assert hasattr(iterator, 'next')
        assert callable(iterator.next)

    def test_iterator_next_returns_iterator_result(self):
        """
        Given an Iterator
        When next() is called
        Then it returns IteratorResult {value, done}
        """
        # Given
        iterator = create_array_iterator([1])

        # When
        result = iterator.next()

        # Then
        assert hasattr(result, 'value')
        assert hasattr(result, 'done')
        assert result.value == 1
        assert result.done is False

    def test_iterator_done_true_when_exhausted(self):
        """
        Given an exhausted Iterator
        When next() is called
        Then done is True
        """
        # Given
        iterator = create_array_iterator([1])
        iterator.next()  # Consume the element

        # When
        result = iterator.next()

        # Then
        assert result.done is True


class TestIterableInterface:
    """Test Iterable interface (objects with Symbol.iterator)."""

    def test_iterable_has_symbol_iterator(self):
        """
        Given an Iterable object
        When checking for Symbol.iterator
        Then the property exists
        """
        # Given
        iterable = [1, 2, 3]  # Arrays are iterable

        # Then
        # In Python, this is __iter__
        assert hasattr(iterable, '__iter__')

    def test_symbol_iterator_returns_iterator(self):
        """
        Given an Iterable
        When calling Symbol.iterator method
        Then it returns an Iterator
        """
        # Given
        iterable = [1, 2, 3]

        # When
        iterator = iter(iterable)  # Python's __iter__

        # Then
        assert hasattr(iterator, '__next__')

    def test_generator_is_iterable(self):
        """
        Given a Generator object
        When checking if it's iterable
        Then it implements the Iterable interface
        """
        # Given
        def simple_gen():
            yield 1

        gen = GeneratorFunction(simple_gen)()

        # Then
        assert hasattr(gen, '__iter__')
        assert iter(gen) is gen  # Generators are their own iterators


class TestArrayIterator:
    """Test Array iterator implementation."""

    def test_array_iterator_yields_all_elements(self):
        """
        Given an array
        When iterating with its iterator
        Then all elements are yielded in order
        """
        # Given
        arr = [1, 2, 3, 4, 5]
        iterator = create_array_iterator(arr)

        # When / Then
        for expected in arr:
            result = iterator.next()
            assert result.value == expected
            assert result.done is False

        # Final next() is done
        result = iterator.next()
        assert result.done is True

    def test_array_iterator_with_empty_array(self):
        """
        Given an empty array
        When getting its iterator
        Then first next() returns done: true
        """
        # Given
        iterator = create_array_iterator([])

        # When
        result = iterator.next()

        # Then
        assert result.done is True

    def test_array_iterator_does_not_modify_array(self):
        """
        Given an array
        When iterating with iterator
        Then the original array is not modified
        """
        # Given
        arr = [1, 2, 3]
        iterator = create_array_iterator(arr)

        # When
        iterator.next()
        iterator.next()

        # Then
        assert arr == [1, 2, 3]

    def test_array_iterator_independent_instances(self):
        """
        Given an array
        When creating multiple iterators
        Then each iterator maintains independent state
        """
        # Given
        arr = [1, 2, 3]
        iter1 = create_array_iterator(arr)
        iter2 = create_array_iterator(arr)

        # When
        iter1.next()  # Advance iter1
        iter1.next()

        # Then
        assert iter1.next().value == 3
        assert iter2.next().value == 1  # iter2 starts from beginning


class TestStringIterator:
    """Test String iterator implementation."""

    def test_string_iterator_yields_characters(self):
        """
        Given a string
        When iterating with its iterator
        Then each character is yielded
        """
        # Given
        string = "abc"
        iterator = create_string_iterator(string)

        # When / Then
        assert iterator.next().value == "a"
        assert iterator.next().value == "b"
        assert iterator.next().value == "c"
        assert iterator.next().done is True

    def test_string_iterator_with_empty_string(self):
        """
        Given an empty string
        When getting its iterator
        Then first next() returns done: true
        """
        # Given
        iterator = create_string_iterator("")

        # When
        result = iterator.next()

        # Then
        assert result.done is True

    def test_string_iterator_handles_unicode(self):
        """
        Given a string with Unicode characters
        When iterating
        Then each code point is yielded correctly
        """
        # Given
        string = "🔥🎉"
        iterator = create_string_iterator(string)

        # When / Then
        assert iterator.next().value == "🔥"
        assert iterator.next().value == "🎉"
        assert iterator.next().done is True

    def test_string_iterator_whitespace_and_special(self):
        """
        Given a string with whitespace and special characters
        When iterating
        Then all characters including whitespace are yielded
        """
        # Given
        string = "a b\tc"
        iterator = create_string_iterator(string)

        # When / Then
        assert iterator.next().value == "a"
        assert iterator.next().value == " "
        assert iterator.next().value == "b"
        assert iterator.next().value == "\t"
        assert iterator.next().value == "c"


class TestIteratorConsumption:
    """Test iterator consumption patterns."""

    def test_iterator_can_be_consumed_once(self):
        """
        Given an iterator
        When fully consumed
        Then subsequent next() calls return done: true
        """
        # Given
        iterator = create_array_iterator([1, 2])

        # When
        iterator.next()
        iterator.next()
        result1 = iterator.next()  # Exhausted

        # Then
        assert result1.done is True

        # Multiple calls still done
        result2 = iterator.next()
        assert result2.done is True

    def test_iterable_can_create_multiple_iterators(self):
        """
        Given an iterable object
        When creating multiple iterators from it
        Then each can be consumed independently
        """
        # Given
        arr = [1, 2, 3]

        # When
        iter1 = create_array_iterator(arr)
        iter2 = create_array_iterator(arr)

        # Consume iter1 completely
        iter1.next()
        iter1.next()
        iter1.next()

        # Then iter2 is still fresh
        assert iter2.next().value == 1
