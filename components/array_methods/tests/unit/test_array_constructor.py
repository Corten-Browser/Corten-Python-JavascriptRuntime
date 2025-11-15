"""
Unit tests for Array constructor static methods (ES2024).

Tests:
- FR-ES24-030: Array.from() improvements (mapping, iterable)
- FR-ES24-031: Array.of()
- Array.isArray() helper
"""

import pytest
from components.array_methods.src.array_constructor import ArrayConstructorMethods


class TestArrayFrom:
    """Test Array.from() static method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_constructor = ArrayConstructorMethods()

    def test_from_iterable_list(self):
        """
        Given a list (iterable)
        When creating array from iterable
        Then returns new array with elements
        """
        # Given
        iterable = [1, 2, 3, 4, 5]

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert result == [1, 2, 3, 4, 5]
        assert result is not iterable  # New array

    def test_from_iterable_string(self):
        """
        Given a string (iterable)
        When creating array from string
        Then returns array of characters
        """
        # Given
        iterable = "hello"

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert result == ['h', 'e', 'l', 'l', 'o']

    def test_from_iterable_with_map_function(self):
        """
        Given an iterable and mapping function
        When creating array
        Then applies mapping function to each element
        """
        # Given
        iterable = [1, 2, 3, 4, 5]

        # When
        result = self.array_constructor.from_iterable(
            iterable, map_fn=lambda x: x * 2
        )

        # Then
        assert result == [2, 4, 6, 8, 10]

    def test_from_iterable_with_map_and_index(self):
        """
        Given an iterable and mapping function with index
        When creating array
        Then mapping function receives element and index
        """
        # Given
        iterable = [10, 20, 30]

        # When
        result = self.array_constructor.from_iterable(
            iterable, map_fn=lambda x, i: x + i
        )

        # Then
        assert result == [10, 21, 32]

    def test_from_iterable_generator(self):
        """
        Given a generator (iterable)
        When creating array
        Then consumes generator into array
        """
        # Given
        def gen():
            yield 1
            yield 2
            yield 3

        # When
        result = self.array_constructor.from_iterable(gen())

        # Then
        assert result == [1, 2, 3]

    def test_from_iterable_range(self):
        """
        Given a range (iterable)
        When creating array
        Then converts range to array
        """
        # Given
        iterable = range(5)

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert result == [0, 1, 2, 3, 4]

    def test_from_iterable_set(self):
        """
        Given a set (iterable)
        When creating array
        Then converts set to array
        """
        # Given
        iterable = {3, 1, 2}

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert sorted(result) == [1, 2, 3]

    def test_from_iterable_empty(self):
        """
        Given an empty iterable
        When creating array
        Then returns empty array
        """
        # Given
        iterable = []

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert result == []

    def test_from_iterable_dict_keys(self):
        """
        Given dictionary keys (iterable)
        When creating array
        Then converts keys to array
        """
        # Given
        iterable = {"a": 1, "b": 2, "c": 3}.keys()

        # When
        result = self.array_constructor.from_iterable(iterable)

        # Then
        assert sorted(result) == ["a", "b", "c"]


class TestArrayOf:
    """Test Array.of() static method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_constructor = ArrayConstructorMethods()

    def test_of_creates_array_from_arguments(self):
        """
        Given multiple arguments
        When creating array with Array.of()
        Then creates array with those elements
        """
        # Given/When
        result = self.array_constructor.of(1, 2, 3, 4, 5)

        # Then
        assert result == [1, 2, 3, 4, 5]

    def test_of_single_element(self):
        """
        Given single argument
        When creating array with Array.of()
        Then creates array with one element (not length)
        """
        # Given/When
        result = self.array_constructor.of(5)

        # Then
        # Unlike Array(5) which creates array of length 5
        # Array.of(5) creates [5]
        assert result == [5]

    def test_of_no_arguments(self):
        """
        Given no arguments
        When creating array with Array.of()
        Then creates empty array
        """
        # Given/When
        result = self.array_constructor.of()

        # Then
        assert result == []

    def test_of_mixed_types(self):
        """
        Given arguments of different types
        When creating array with Array.of()
        Then creates array with all types
        """
        # Given/When
        result = self.array_constructor.of(1, "hello", True, None, {"key": "value"})

        # Then
        assert result == [1, "hello", True, None, {"key": "value"}]

    def test_of_with_undefined(self):
        """
        Given None (undefined) arguments
        When creating array with Array.of()
        Then includes None in array
        """
        # Given/When
        result = self.array_constructor.of(1, None, 3)

        # Then
        assert result == [1, None, 3]


class TestArrayIsArray:
    """Test Array.isArray() static method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.array_constructor = ArrayConstructorMethods()

    def test_is_array_with_list(self):
        """
        Given a list
        When checking if it's an array
        Then returns True
        """
        # Given
        value = [1, 2, 3]

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is True

    def test_is_array_with_empty_list(self):
        """
        Given an empty list
        When checking if it's an array
        Then returns True
        """
        # Given
        value = []

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is True

    def test_is_array_with_string(self):
        """
        Given a string
        When checking if it's an array
        Then returns False
        """
        # Given
        value = "hello"

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is False

    def test_is_array_with_number(self):
        """
        Given a number
        When checking if it's an array
        Then returns False
        """
        # Given
        value = 42

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is False

    def test_is_array_with_object(self):
        """
        Given a plain object (dict)
        When checking if it's an array
        Then returns False
        """
        # Given
        value = {"key": "value"}

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is False

    def test_is_array_with_none(self):
        """
        Given None (null/undefined)
        When checking if it's an array
        Then returns False
        """
        # Given
        value = None

        # When
        result = self.array_constructor.is_array(value)

        # Then
        assert result is False

    def test_is_array_with_tuple(self):
        """
        Given a tuple (array-like but not array)
        When checking if it's an array
        Then returns False (strict check)
        """
        # Given
        value = (1, 2, 3)

        # When
        result = self.array_constructor.is_array(value)

        # Then
        # Only list is considered array in Python
        assert result is False
