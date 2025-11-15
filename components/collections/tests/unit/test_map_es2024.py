"""
Unit tests for ES2024 Map.groupBy() static method.

Tests Map.groupBy() from ECMAScript 2024.

Requirements:
- FR-P3.5-034: Map.groupBy(items, callback)
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class TestMapGroupBy:
    """Test Map.groupBy() static method (FR-P3.5-034)."""

    def test_groupby_basic_string_keys(self):
        """
        Given an array of objects
        When Map.groupBy is called with string keys
        Then items are grouped into Map with string keys
        """
        from components.collections.src.map import Map

        # Given
        items = [
            {'type': 'fruit', 'name': 'apple'},
            {'type': 'vegetable', 'name': 'carrot'},
            {'type': 'fruit', 'name': 'banana'}
        ]

        # When
        result = Map.groupBy(items, lambda x, i: x['type'])

        # Then
        assert isinstance(result, Map)
        assert result.has('fruit') is True
        assert result.has('vegetable') is True
        fruit_group = result.get('fruit')
        assert len(fruit_group) == 2
        assert fruit_group[0]['name'] == 'apple'
        assert fruit_group[1]['name'] == 'banana'

    def test_groupby_boolean_keys(self):
        """
        Given an array of numbers
        When Map.groupBy uses boolean keys
        Then items are grouped by boolean values (not coerced to string)
        """
        from components.collections.src.map import Map

        # Given
        numbers = [1, 2, 3, 4, 5, 6]

        # When
        result = Map.groupBy(numbers, lambda x, i: x % 2 == 0)

        # Then
        assert result.has(True) is True
        assert result.has(False) is True
        assert result.get(True) == [2, 4, 6]
        assert result.get(False) == [1, 3, 5]

    def test_groupby_numeric_keys(self):
        """
        Given an array
        When Map.groupBy uses numeric keys
        Then items are grouped by actual numbers (not coerced to string)
        """
        from components.collections.src.map import Map

        # Given
        items = ['a', 'b', 'c', 'd', 'e', 'f']

        # When - group by remainder when dividing index by 3
        result = Map.groupBy(items, lambda x, i: i % 3)

        # Then
        assert result.has(0) is True
        assert result.has(1) is True
        assert result.has(2) is True
        assert result.get(0) == ['a', 'd']
        assert result.get(1) == ['b', 'e']
        assert result.get(2) == ['c', 'f']

    def test_groupby_object_keys(self):
        """
        Given an array
        When Map.groupBy uses object keys
        Then items can be grouped using objects as keys
        """
        from components.collections.src.map import Map

        # Given
        key1 = {'category': 'A'}
        key2 = {'category': 'B'}
        items = [1, 2, 3, 4, 5]

        # When
        result = Map.groupBy(items, lambda x, i: key1 if x <= 2 else key2)

        # Then
        assert result.has(key1) is True
        assert result.has(key2) is True
        assert result.get(key1) == [1, 2]
        assert result.get(key2) == [3, 4, 5]

    def test_groupby_empty_array(self):
        """
        Given an empty array
        When Map.groupBy is called
        Then an empty Map is returned
        """
        from components.collections.src.map import Map

        # Given
        items = []

        # When
        result = Map.groupBy(items, lambda x, i: x)

        # Then
        assert isinstance(result, Map)
        assert result.size == 0

    def test_groupby_single_group(self):
        """
        Given an array where all items map to same key
        When Map.groupBy is called
        Then all items are in single group
        """
        from components.collections.src.map import Map

        # Given
        items = [1, 2, 3, 4, 5]

        # When
        result = Map.groupBy(items, lambda x, i: 'all')

        # Then
        assert result.size == 1
        assert result.has('all') is True
        assert result.get('all') == [1, 2, 3, 4, 5]

    def test_groupby_preserves_insertion_order(self):
        """
        Given an array with multiple groups
        When Map.groupBy is called
        Then groups are added in order first encountered
        """
        from components.collections.src.map import Map

        # Given
        items = [
            {'category': 'B'},
            {'category': 'A'},
            {'category': 'C'},
            {'category': 'A'}
        ]

        # When
        result = Map.groupBy(items, lambda x, i: x['category'])

        # Then
        # Keys should be in order: B, A, C (first encountered order)
        keys = list(result.keys())
        assert keys == ['B', 'A', 'C']

    def test_groupby_uses_index_parameter(self):
        """
        Given an array
        When callback uses index parameter
        Then grouping is based on index
        """
        from components.collections.src.map import Map

        # Given
        items = ['a', 'b', 'c', 'd', 'e']

        # When
        result = Map.groupBy(items, lambda x, i: 'first_half' if i < 3 else 'second_half')

        # Then
        assert result.get('first_half') == ['a', 'b', 'c']
        assert result.get('second_half') == ['d', 'e']

    def test_groupby_non_iterable_raises_error(self):
        """
        Given a non-iterable value
        When Map.groupBy is called
        Then TypeError is raised
        """
        from components.collections.src.map import Map

        # Given
        non_iterable = 42

        # When / Then
        with pytest.raises(TypeError, match="must be iterable"):
            Map.groupBy(non_iterable, lambda x, i: x)

    def test_groupby_non_callable_raises_error(self):
        """
        Given a non-callable callback
        When Map.groupBy is called
        Then TypeError is raised
        """
        from components.collections.src.map import Map

        # Given
        items = [1, 2, 3]
        non_callable = "not a function"

        # When / Then
        with pytest.raises(TypeError, match="must be callable"):
            Map.groupBy(items, non_callable)

    def test_groupby_returns_new_map_instance(self):
        """
        Given an array
        When Map.groupBy is called
        Then a new Map instance is created (not modifying existing Map)
        """
        from components.collections.src.map import Map

        # Given
        items = [1, 2, 3]

        # When
        result = Map.groupBy(items, lambda x, i: x % 2)

        # Then
        assert isinstance(result, Map)
        # Verify it's independent
        result.set('new_key', [99])
        # Original groupBy result is unaffected
        assert result.has('new_key') is True


class TestMapGroupByVsObjectGroupBy:
    """Test differences between Map.groupBy and Object.groupBy."""

    def test_map_groupby_preserves_key_types(self):
        """
        Given numeric keys
        When Map.groupBy is used
        Then numeric keys are preserved (unlike Object.groupBy which coerces to string)
        """
        from components.collections.src.map import Map

        # Given
        items = [1, 2, 3, 4]

        # When
        result = Map.groupBy(items, lambda x, i: x % 2)

        # Then
        # Map preserves numeric keys
        assert result.has(0) is True
        assert result.has(1) is True
        # But NOT string keys
        assert result.has('0') is False
        assert result.has('1') is False

    def test_map_groupby_supports_object_keys(self):
        """
        Given object keys
        When Map.groupBy is used
        Then objects can be used as keys (Object.groupBy cannot do this)
        """
        from components.collections.src.map import Map

        # Given
        key_obj = {'id': 1}
        items = [10, 20, 30]

        # When
        result = Map.groupBy(items, lambda x, i: key_obj)

        # Then
        assert result.has(key_obj) is True
        assert result.get(key_obj) == [10, 20, 30]
