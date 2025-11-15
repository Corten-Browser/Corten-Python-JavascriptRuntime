"""
Unit tests for ES2024 Object static methods.

Tests Object.groupBy() and Object.hasOwn() from ECMAScript 2024.

Requirements:
- FR-P3.5-032: Object.groupBy(items, callback)
- FR-P3.5-033: Object.hasOwn(obj, prop)
"""

import pytest
from components.object_runtime.src.object_constructor import ObjectConstructor, Object


class TestObjectGroupBy:
    """Test Object.groupBy() static method (FR-P3.5-032)."""

    def test_groupby_basic_string_keys(self):
        """
        Given an array of objects with type property
        When groupBy is called with callback returning type
        Then items are grouped by type into object with string keys
        """
        # Given
        items = [
            {'type': 'fruit', 'name': 'apple'},
            {'type': 'vegetable', 'name': 'carrot'},
            {'type': 'fruit', 'name': 'banana'},
            {'type': 'vegetable', 'name': 'broccoli'}
        ]

        # When
        result = ObjectConstructor.groupBy(items, lambda x, i: x['type'])

        # Then
        assert 'fruit' in result
        assert 'vegetable' in result
        assert len(result['fruit']) == 2
        assert len(result['vegetable']) == 2
        assert result['fruit'][0]['name'] == 'apple'
        assert result['fruit'][1]['name'] == 'banana'
        assert result['vegetable'][0]['name'] == 'carrot'

    def test_groupby_empty_array(self):
        """
        Given an empty array
        When groupBy is called
        Then an empty object is returned
        """
        # Given
        items = []

        # When
        result = ObjectConstructor.groupBy(items, lambda x, i: x)

        # Then
        assert result == {}
        assert len(result) == 0

    def test_groupby_numeric_keys_coerced_to_string(self):
        """
        Given an array of numbers
        When groupBy returns numeric keys
        Then numeric keys are coerced to strings
        """
        # Given
        numbers = [1, 2, 3, 4, 5, 6]

        # When
        result = ObjectConstructor.groupBy(numbers, lambda x, i: x % 2)

        # Then
        # Numeric keys coerced to strings
        assert '0' in result  # Even numbers (x % 2 == 0)
        assert '1' in result  # Odd numbers (x % 2 == 1)
        assert result['0'] == [2, 4, 6]
        assert result['1'] == [1, 3, 5]

    def test_groupby_uses_index_parameter(self):
        """
        Given an array
        When callback uses the index parameter
        Then grouping is based on index
        """
        # Given
        items = ['a', 'b', 'c', 'd', 'e']

        # When - group by first half vs second half
        result = ObjectConstructor.groupBy(items, lambda x, i: 'first' if i < 2 else 'second')

        # Then
        assert result['first'] == ['a', 'b']
        assert result['second'] == ['c', 'd', 'e']

    def test_groupby_single_group(self):
        """
        Given an array where all items return same key
        When groupBy is called
        Then all items are in single group
        """
        # Given
        items = [1, 2, 3, 4, 5]

        # When
        result = ObjectConstructor.groupBy(items, lambda x, i: 'all')

        # Then
        assert len(result) == 1
        assert 'all' in result
        assert result['all'] == [1, 2, 3, 4, 5]

    def test_groupby_boolean_keys_coerced_to_string(self):
        """
        Given an array of numbers
        When callback returns boolean values
        Then boolean keys are coerced to strings
        """
        # Given
        numbers = [1, 2, 3, 4, 5, 6]

        # When
        result = ObjectConstructor.groupBy(numbers, lambda x, i: x % 2 == 0)

        # Then
        assert 'True' in result
        assert 'False' in result
        assert result['True'] == [2, 4, 6]
        assert result['False'] == [1, 3, 5]

    def test_groupby_none_key_coerced_to_string(self):
        """
        Given callback that returns None for some items
        When groupBy is called
        Then None is coerced to string 'None'
        """
        # Given
        items = [1, None, 2, None, 3]

        # When
        result = ObjectConstructor.groupBy(items, lambda x, i: x)

        # Then
        assert 'None' in result
        assert 'None' in result
        assert result['None'] == [None, None]
        assert result['1'] == [1]

    def test_groupby_non_iterable_raises_error(self):
        """
        Given a non-iterable value
        When groupBy is called
        Then TypeError is raised
        """
        # Given
        non_iterable = 42

        # When / Then
        with pytest.raises(TypeError, match="must be iterable"):
            ObjectConstructor.groupBy(non_iterable, lambda x, i: x)

    def test_groupby_non_callable_raises_error(self):
        """
        Given a non-callable callback
        When groupBy is called
        Then TypeError is raised
        """
        # Given
        items = [1, 2, 3]
        non_callable = "not a function"

        # When / Then
        with pytest.raises(TypeError, match="must be callable"):
            ObjectConstructor.groupBy(items, non_callable)


class TestObjectHasOwn:
    """Test Object.hasOwn() static method (FR-P3.5-033)."""

    def test_hasown_own_property_exists(self):
        """
        Given an object with own property
        When hasOwn is called for that property
        Then True is returned
        """
        # Given
        obj = {'a': 1, 'b': 2}

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'a') is True
        assert ObjectConstructor.hasOwn(obj, 'b') is True

    def test_hasown_property_does_not_exist(self):
        """
        Given an object without specific property
        When hasOwn is called for that property
        Then False is returned
        """
        # Given
        obj = {'a': 1}

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'b') is False
        assert ObjectConstructor.hasOwn(obj, 'c') is False

    def test_hasown_inherited_property_returns_false(self):
        """
        Given an object with inherited property
        When hasOwn is called for inherited property
        Then False is returned (only own properties)
        """
        # Given
        class BaseClass:
            inherited_prop = 'inherited'

        class DerivedClass(BaseClass):
            def __init__(self):
                self.own_prop = 'own'

        obj = DerivedClass()

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'own_prop') is True
        assert ObjectConstructor.hasOwn(obj, 'inherited_prop') is False

    def test_hasown_overridden_hasownproperty(self):
        """
        Given an object where hasOwnProperty is overridden
        When hasOwn is called
        Then it still works correctly (doesn't use hasOwnProperty)
        """
        # Given
        obj = {
            'hasOwnProperty': 'not a function',
            'a': 1,
            'b': 2
        }

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'a') is True
        assert ObjectConstructor.hasOwn(obj, 'b') is True
        assert ObjectConstructor.hasOwn(obj, 'hasOwnProperty') is True
        assert ObjectConstructor.hasOwn(obj, 'c') is False

    def test_hasown_empty_object(self):
        """
        Given an empty object
        When hasOwn is called for any property
        Then False is returned
        """
        # Given
        obj = {}

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'a') is False
        assert ObjectConstructor.hasOwn(obj, 'toString') is False

    def test_hasown_null_raises_error(self):
        """
        Given None (null in JavaScript)
        When hasOwn is called
        Then TypeError is raised
        """
        # Given
        obj = None

        # When / Then
        with pytest.raises(TypeError, match="Cannot convert undefined or null to object"):
            ObjectConstructor.hasOwn(obj, 'a')

    def test_hasown_custom_object_with_dict(self):
        """
        Given a custom object with __dict__
        When hasOwn is called for properties
        Then own properties are correctly identified
        """
        # Given
        class CustomObject:
            def __init__(self):
                self.x = 10
                self.y = 20

        obj = CustomObject()

        # When / Then
        assert ObjectConstructor.hasOwn(obj, 'x') is True
        assert ObjectConstructor.hasOwn(obj, 'y') is True
        assert ObjectConstructor.hasOwn(obj, 'z') is False


class TestObjectAlias:
    """Test that Object is an alias for ObjectConstructor."""

    def test_object_alias_groupby(self):
        """
        Given Object alias
        When groupBy is called
        Then it works identically to ObjectConstructor.groupBy
        """
        # Given
        items = [1, 2, 3, 4]

        # When
        result = Object.groupBy(items, lambda x, i: x % 2)

        # Then
        assert '0' in result
        assert '1' in result

    def test_object_alias_hasown(self):
        """
        Given Object alias
        When hasOwn is called
        Then it works identically to ObjectConstructor.hasOwn
        """
        # Given
        obj = {'a': 1}

        # When / Then
        assert Object.hasOwn(obj, 'a') is True
        assert Object.hasOwn(obj, 'b') is False
