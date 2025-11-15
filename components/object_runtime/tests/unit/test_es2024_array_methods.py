"""
Unit tests for ES2024 Array methods.

Tests the new ES2024 array methods:
- toReversed() - Non-mutating reverse
- toSorted() - Non-mutating sort
- toSpliced() - Non-mutating splice
- with() - Non-mutating element replace
- findLast() - Find from end
- findLastIndex() - Find index from end
- fromAsync() - Static async array creation
"""

import pytest
import asyncio


class TestArrayToReversed:
    """Test Array.prototype.toReversed() - FR-P3.5-023."""

    def test_toreversed_returns_new_reversed_array(self):
        """
        Given an array with elements [1, 2, 3]
        When toReversed is called
        Then a new reversed array [3, 2, 1] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        reversed_arr = arr.to_reversed()

        assert reversed_arr.get_element(0).to_smi() == 3
        assert reversed_arr.get_element(1).to_smi() == 2
        assert reversed_arr.get_element(2).to_smi() == 1

    def test_toreversed_does_not_mutate_original(self):
        """
        Given an array with elements [1, 2, 3]
        When toReversed is called
        Then the original array remains unchanged
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        arr.to_reversed()

        # Original array unchanged
        assert arr.get_element(0).to_smi() == 1
        assert arr.get_element(1).to_smi() == 2
        assert arr.get_element(2).to_smi() == 3

    def test_toreversed_empty_array(self):
        """
        Given an empty array
        When toReversed is called
        Then an empty array is returned
        """
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        reversed_arr = arr.to_reversed()

        assert reversed_arr.get_property("length").to_smi() == 0

    def test_toreversed_single_element(self):
        """
        Given an array with single element [42]
        When toReversed is called
        Then a new array with same element [42] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(42))

        reversed_arr = arr.to_reversed()

        assert reversed_arr.get_element(0).to_smi() == 42
        assert reversed_arr.get_property("length").to_smi() == 1

    def test_toreversed_returns_new_instance(self):
        """
        Given an array
        When toReversed is called
        Then the returned array is a different instance
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))

        reversed_arr = arr.to_reversed()

        assert reversed_arr is not arr


class TestArrayToSorted:
    """Test Array.prototype.toSorted() - FR-P3.5-024."""

    def test_tosorted_returns_new_sorted_array(self):
        """
        Given an array [3, 1, 2]
        When toSorted is called without compareFn
        Then a new sorted array [1, 2, 3] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(3))
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))

        sorted_arr = arr.to_sorted()

        assert sorted_arr.get_element(0).to_smi() == 1
        assert sorted_arr.get_element(1).to_smi() == 2
        assert sorted_arr.get_element(2).to_smi() == 3

    def test_tosorted_does_not_mutate_original(self):
        """
        Given an array [3, 1, 2]
        When toSorted is called
        Then the original array remains unchanged
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(3))
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))

        arr.to_sorted()

        # Original array unchanged
        assert arr.get_element(0).to_smi() == 3
        assert arr.get_element(1).to_smi() == 1
        assert arr.get_element(2).to_smi() == 2

    def test_tosorted_with_compare_function(self):
        """
        Given an array [1, 2, 3]
        When toSorted is called with descending compareFn
        Then a new sorted array [3, 2, 1] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        # Descending compareFn
        def compare_desc(a, b):
            a_val = a.to_smi()
            b_val = b.to_smi()
            if a_val < b_val:
                return 1
            elif a_val > b_val:
                return -1
            return 0

        sorted_arr = arr.to_sorted(compare_desc)

        assert sorted_arr.get_element(0).to_smi() == 3
        assert sorted_arr.get_element(1).to_smi() == 2
        assert sorted_arr.get_element(2).to_smi() == 1

    def test_tosorted_empty_array(self):
        """
        Given an empty array
        When toSorted is called
        Then an empty array is returned
        """
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        sorted_arr = arr.to_sorted()

        assert sorted_arr.get_property("length").to_smi() == 0

    def test_tosorted_single_element(self):
        """
        Given an array with single element [42]
        When toSorted is called
        Then a new array with same element [42] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(42))

        sorted_arr = arr.to_sorted()

        assert sorted_arr.get_element(0).to_smi() == 42
        assert sorted_arr.get_property("length").to_smi() == 1

    def test_tosorted_returns_new_instance(self):
        """
        Given an array
        When toSorted is called
        Then the returned array is a different instance
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))

        sorted_arr = arr.to_sorted()

        assert sorted_arr is not arr


class TestArrayToSpliced:
    """Test Array.prototype.toSpliced() - FR-P3.5-025."""

    def test_tospliced_removes_elements(self):
        """
        Given an array [1, 2, 3, 4]
        When toSpliced(1, 2) is called
        Then a new array [1, 4] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4]:
            arr.push(Value.from_smi(i))

        spliced_arr = arr.to_spliced(1, 2)

        assert spliced_arr.get_element(0).to_smi() == 1
        assert spliced_arr.get_element(1).to_smi() == 4
        assert spliced_arr.get_property("length").to_smi() == 2

    def test_tospliced_adds_elements(self):
        """
        Given an array [1, 2, 3, 4]
        When toSpliced(1, 2, 'a', 'b') is called
        Then a new array [1, 'a', 'b', 4] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4]:
            arr.push(Value.from_smi(i))

        spliced_arr = arr.to_spliced(1, 2, Value.from_smi(10), Value.from_smi(20))

        assert spliced_arr.get_element(0).to_smi() == 1
        assert spliced_arr.get_element(1).to_smi() == 10
        assert spliced_arr.get_element(2).to_smi() == 20
        assert spliced_arr.get_element(3).to_smi() == 4

    def test_tospliced_does_not_mutate_original(self):
        """
        Given an array [1, 2, 3, 4]
        When toSpliced is called
        Then the original array remains unchanged
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4]:
            arr.push(Value.from_smi(i))

        arr.to_spliced(1, 2)

        # Original array unchanged
        assert arr.get_element(0).to_smi() == 1
        assert arr.get_element(1).to_smi() == 2
        assert arr.get_element(2).to_smi() == 3
        assert arr.get_element(3).to_smi() == 4

    def test_tospliced_insert_at_beginning(self):
        """
        Given an array [1, 2, 3]
        When toSpliced(0, 0, 99) is called
        Then a new array [99, 1, 2, 3] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3]:
            arr.push(Value.from_smi(i))

        spliced_arr = arr.to_spliced(0, 0, Value.from_smi(99))

        assert spliced_arr.get_element(0).to_smi() == 99
        assert spliced_arr.get_element(1).to_smi() == 1
        assert spliced_arr.get_element(2).to_smi() == 2
        assert spliced_arr.get_element(3).to_smi() == 3

    def test_tospliced_remove_all_from_index(self):
        """
        Given an array [1, 2, 3, 4, 5]
        When toSpliced(2, 10) is called (deleteCount > remaining)
        Then a new array [1, 2] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4, 5]:
            arr.push(Value.from_smi(i))

        spliced_arr = arr.to_spliced(2, 10)

        assert spliced_arr.get_element(0).to_smi() == 1
        assert spliced_arr.get_element(1).to_smi() == 2
        assert spliced_arr.get_property("length").to_smi() == 2

    def test_tospliced_returns_new_instance(self):
        """
        Given an array
        When toSpliced is called
        Then the returned array is a different instance
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))

        spliced_arr = arr.to_spliced(0, 0)

        assert spliced_arr is not arr


class TestArrayWith:
    """Test Array.prototype.with() - FR-P3.5-026."""

    def test_with_replaces_element_at_index(self):
        """
        Given an array [1, 2, 3]
        When with(1, 'X') is called
        Then a new array [1, 'X', 3] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        new_arr = arr.with_element(1, Value.from_smi(99))

        assert new_arr.get_element(0).to_smi() == 1
        assert new_arr.get_element(1).to_smi() == 99
        assert new_arr.get_element(2).to_smi() == 3

    def test_with_does_not_mutate_original(self):
        """
        Given an array [1, 2, 3]
        When with is called
        Then the original array remains unchanged
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        arr.with_element(1, Value.from_smi(99))

        # Original array unchanged
        assert arr.get_element(0).to_smi() == 1
        assert arr.get_element(1).to_smi() == 2
        assert arr.get_element(2).to_smi() == 3

    def test_with_negative_index(self):
        """
        Given an array [1, 2, 3]
        When with(-1, 99) is called (negative index from end)
        Then a new array [1, 2, 99] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        new_arr = arr.with_element(-1, Value.from_smi(99))

        assert new_arr.get_element(0).to_smi() == 1
        assert new_arr.get_element(1).to_smi() == 2
        assert new_arr.get_element(2).to_smi() == 99

    def test_with_first_element(self):
        """
        Given an array [1, 2, 3]
        When with(0, 99) is called
        Then a new array [99, 2, 3] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        new_arr = arr.with_element(0, Value.from_smi(99))

        assert new_arr.get_element(0).to_smi() == 99
        assert new_arr.get_element(1).to_smi() == 2
        assert new_arr.get_element(2).to_smi() == 3

    def test_with_returns_new_instance(self):
        """
        Given an array
        When with is called
        Then the returned array is a different instance
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))

        new_arr = arr.with_element(0, Value.from_smi(99))

        assert new_arr is not arr


class TestArrayFindLast:
    """Test Array.prototype.findLast() - FR-P3.5-027."""

    def test_findlast_finds_element(self):
        """
        Given an array [1, 2, 3, 4, 5]
        When findLast is called with predicate (x > 3)
        Then element 5 is returned (last matching)
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4, 5]:
            arr.push(Value.from_smi(i))

        result = arr.find_last(lambda val: val.to_smi() > 3)

        assert result.to_smi() == 5

    def test_findlast_returns_undefined_when_not_found(self):
        """
        Given an array [1, 2, 3]
        When findLast is called with predicate that matches nothing
        Then undefined is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray
        from js_object import UNDEFINED_VALUE

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3]:
            arr.push(Value.from_smi(i))

        result = arr.find_last(lambda val: val.to_smi() > 10)

        assert result == UNDEFINED_VALUE

    def test_findlast_empty_array(self):
        """
        Given an empty array
        When findLast is called
        Then undefined is returned
        """
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray
        from js_object import UNDEFINED_VALUE

        gc = GarbageCollector()
        arr = JSArray(gc)

        result = arr.find_last(lambda val: True)

        assert result == UNDEFINED_VALUE

    def test_findlast_finds_last_not_first(self):
        """
        Given an array [2, 4, 6, 8]
        When findLast is called with predicate (x > 3)
        Then element 8 is returned (last, not first matching)
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [2, 4, 6, 8]:
            arr.push(Value.from_smi(i))

        result = arr.find_last(lambda val: val.to_smi() > 3)

        # Should be 8 (last), not 4 (first)
        assert result.to_smi() == 8

    def test_findlast_single_element_matching(self):
        """
        Given an array with single element [42]
        When findLast is called with predicate that matches
        Then the element is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(42))

        result = arr.find_last(lambda val: val.to_smi() == 42)

        assert result.to_smi() == 42


class TestArrayFindLastIndex:
    """Test Array.prototype.findLastIndex() - FR-P3.5-028."""

    def test_findlastindex_finds_index(self):
        """
        Given an array [1, 2, 3, 4, 5]
        When findLastIndex is called with predicate (x > 3)
        Then index 4 is returned (last matching element)
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4, 5]:
            arr.push(Value.from_smi(i))

        result = arr.find_last_index(lambda val: val.to_smi() > 3)

        assert result == 4

    def test_findlastindex_returns_minus_one_when_not_found(self):
        """
        Given an array [1, 2, 3]
        When findLastIndex is called with predicate that matches nothing
        Then -1 is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3]:
            arr.push(Value.from_smi(i))

        result = arr.find_last_index(lambda val: val.to_smi() > 10)

        assert result == -1

    def test_findlastindex_empty_array(self):
        """
        Given an empty array
        When findLastIndex is called
        Then -1 is returned
        """
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)

        result = arr.find_last_index(lambda val: True)

        assert result == -1

    def test_findlastindex_finds_last_not_first(self):
        """
        Given an array [2, 4, 6, 8]
        When findLastIndex is called with predicate (x > 3)
        Then index 3 is returned (last, not first matching)
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [2, 4, 6, 8]:
            arr.push(Value.from_smi(i))

        result = arr.find_last_index(lambda val: val.to_smi() > 3)

        # Should be index 3 (last), not index 1 (first)
        assert result == 3

    def test_findlastindex_single_element_matching(self):
        """
        Given an array with single element [42]
        When findLastIndex is called with predicate that matches
        Then index 0 is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(42))

        result = arr.find_last_index(lambda val: val.to_smi() == 42)

        assert result == 0


class TestArrayFromAsync:
    """Test Array.fromAsync() - FR-P3.5-029."""

    @pytest.mark.asyncio
    async def test_fromasync_creates_array_from_async_iterable(self):
        """
        Given an async iterable yielding [1, 2, 3]
        When Array.fromAsync is called
        Then a Promise resolving to array [1, 2, 3] is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def async_generator():
            for i in [1, 2, 3]:
                yield Value.from_smi(i)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, async_generator())

        assert isinstance(result_arr, JSArray)
        assert result_arr.get_element(0).to_smi() == 1
        assert result_arr.get_element(1).to_smi() == 2
        assert result_arr.get_element(2).to_smi() == 3

    @pytest.mark.asyncio
    async def test_fromasync_empty_async_iterable(self):
        """
        Given an empty async iterable
        When Array.fromAsync is called
        Then a Promise resolving to empty array is returned
        """
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray

        async def async_generator():
            return
            yield  # Never executed, makes it a generator

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, async_generator())

        assert isinstance(result_arr, JSArray)
        assert result_arr.get_property("length").to_smi() == 0

    @pytest.mark.asyncio
    async def test_fromasync_with_async_generator_function(self):
        """
        Given an async generator function
        When Array.fromAsync is called
        Then all yielded values are collected into array
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def count_to_five():
            for i in range(1, 6):
                await asyncio.sleep(0.001)  # Simulate async work
                yield Value.from_smi(i)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, count_to_five())

        assert result_arr.get_property("length").to_smi() == 5
        assert result_arr.get_element(0).to_smi() == 1
        assert result_arr.get_element(4).to_smi() == 5

    @pytest.mark.asyncio
    async def test_fromasync_with_single_element(self):
        """
        Given an async iterable with single element
        When Array.fromAsync is called
        Then array with that element is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def single_value():
            yield Value.from_smi(42)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, single_value())

        assert result_arr.get_property("length").to_smi() == 1
        assert result_arr.get_element(0).to_smi() == 42

    @pytest.mark.asyncio
    async def test_fromasync_preserves_order(self):
        """
        Given an async iterable yielding values in sequence
        When Array.fromAsync is called
        Then array preserves the original order
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def ordered_values():
            for i in [10, 20, 30, 40, 50]:
                yield Value.from_smi(i)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, ordered_values())

        assert result_arr.get_element(0).to_smi() == 10
        assert result_arr.get_element(1).to_smi() == 20
        assert result_arr.get_element(2).to_smi() == 30
        assert result_arr.get_element(3).to_smi() == 40
        assert result_arr.get_element(4).to_smi() == 50

    @pytest.mark.asyncio
    async def test_fromasync_handles_awaitable_values(self):
        """
        Given an async iterable with awaitable values
        When Array.fromAsync is called
        Then all values are properly awaited and collected
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def async_values():
            await asyncio.sleep(0.001)
            yield Value.from_smi(1)
            await asyncio.sleep(0.001)
            yield Value.from_smi(2)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, async_values())

        assert result_arr.get_element(0).to_smi() == 1
        assert result_arr.get_element(1).to_smi() == 2

    @pytest.mark.asyncio
    async def test_fromasync_with_large_async_iterable(self):
        """
        Given an async iterable with many elements
        When Array.fromAsync is called
        Then all elements are collected correctly
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def many_values():
            for i in range(100):
                yield Value.from_smi(i)

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, many_values())

        assert result_arr.get_property("length").to_smi() == 100
        assert result_arr.get_element(0).to_smi() == 0
        assert result_arr.get_element(50).to_smi() == 50
        assert result_arr.get_element(99).to_smi() == 99

    @pytest.mark.asyncio
    async def test_fromasync_is_static_method(self):
        """
        Given Array class
        When fromAsync is called as static method
        Then it works without instance
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def values():
            yield Value.from_smi(1)

        gc = GarbageCollector()
        # Call as static method
        result_arr = await JSArray.from_async(gc, values())

        assert isinstance(result_arr, JSArray)
        assert result_arr.get_element(0).to_smi() == 1

    @pytest.mark.asyncio
    async def test_fromasync_with_async_list(self):
        """
        Given a regular list converted to async iterable
        When Array.fromAsync is called
        Then array is created from the list
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def async_list_iterator():
            items = [Value.from_smi(i) for i in [5, 10, 15]]
            for item in items:
                yield item

        gc = GarbageCollector()
        result_arr = await JSArray.from_async(gc, async_list_iterator())

        assert result_arr.get_element(0).to_smi() == 5
        assert result_arr.get_element(1).to_smi() == 10
        assert result_arr.get_element(2).to_smi() == 15

    @pytest.mark.asyncio
    async def test_fromasync_completes_before_returning(self):
        """
        Given an async iterable
        When Array.fromAsync is awaited
        Then the result is a complete array (not a promise)
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        async def values():
            yield Value.from_smi(1)
            yield Value.from_smi(2)

        gc = GarbageCollector()
        result = await JSArray.from_async(gc, values())

        # Result should be JSArray, not a coroutine/promise
        assert isinstance(result, JSArray)
        assert result.get_property("length").to_smi() == 2


class TestArrayES2024EdgeCases:
    """Test edge cases for ES2024 Array methods to improve coverage."""

    def test_with_element_out_of_bounds_positive(self):
        """
        Given an array [1, 2, 3]
        When with(10, 99) is called (index out of bounds)
        Then IndexError is raised
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        with pytest.raises(IndexError):
            arr.with_element(10, Value.from_smi(99))

    def test_with_element_out_of_bounds_negative(self):
        """
        Given an array [1, 2, 3]
        When with(-10, 99) is called (negative index too large)
        Then IndexError is raised
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        arr.push(Value.from_smi(1))
        arr.push(Value.from_smi(2))
        arr.push(Value.from_smi(3))

        with pytest.raises(IndexError):
            arr.with_element(-10, Value.from_smi(99))

    def test_tospliced_with_negative_start(self):
        """
        Given an array [1, 2, 3, 4]
        When toSpliced(-2, 1) is called (negative start index)
        Then elements are removed from correct position
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc)
        for i in [1, 2, 3, 4]:
            arr.push(Value.from_smi(i))

        spliced = arr.to_spliced(-2, 1)

        # Should remove element at index 2 (value 3)
        assert spliced.get_element(0).to_smi() == 1
        assert spliced.get_element(1).to_smi() == 2
        assert spliced.get_element(2).to_smi() == 4
        assert spliced.get_property("length").to_smi() == 3

    def test_tospliced_with_sparse_array(self):
        """
        Given a sparse array (with gaps)
        When toSpliced is called
        Then undefined values are handled correctly
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray
        from js_object import UNDEFINED_VALUE

        gc = GarbageCollector()
        arr = JSArray(gc, length=5)
        arr.set_element(0, Value.from_smi(1))
        arr.set_element(4, Value.from_smi(5))
        # Elements 1, 2, 3 are undefined (sparse)

        spliced = arr.to_spliced(1, 2)

        # Should have elements [1, undefined, 5]
        assert spliced.get_element(0).to_smi() == 1
        assert spliced.get_element(1) == UNDEFINED_VALUE
        assert spliced.get_element(2).to_smi() == 5

    def test_tosorted_with_sparse_array(self):
        """
        Given a sparse array with undefined values
        When toSorted is called
        Then a sorted array is returned
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray

        gc = GarbageCollector()
        arr = JSArray(gc, length=4)
        arr.set_element(0, Value.from_smi(3))
        arr.set_element(2, Value.from_smi(1))
        # Elements 1 and 3 are undefined (sparse)

        sorted_arr = arr.to_sorted()

        # Should return a sorted array (implementation-specific ordering)
        assert sorted_arr.get_property("length").to_smi() == 4
        # Verify it's a new instance
        assert sorted_arr is not arr

    def test_with_element_on_sparse_array(self):
        """
        Given a sparse array with undefined values
        When with_element is called
        Then undefined values are preserved
        """
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_array import JSArray
        from js_object import UNDEFINED_VALUE

        gc = GarbageCollector()
        arr = JSArray(gc, length=4)
        arr.set_element(0, Value.from_smi(1))
        arr.set_element(3, Value.from_smi(4))
        # Elements 1 and 2 are undefined (sparse)

        new_arr = arr.with_element(2, Value.from_smi(99))

        # Should have [1, undefined, 99, 4]
        assert new_arr.get_element(0).to_smi() == 1
        assert new_arr.get_element(1) == UNDEFINED_VALUE
        assert new_arr.get_element(2).to_smi() == 99
        assert new_arr.get_element(3).to_smi() == 4
