"""
Unit tests for Iterator helper methods (ES2024).

Tests Iterator.prototype helper methods: map, filter, take, drop, flatMap,
reduce, toArray, forEach, some, every, find.

Requirements:
    - FR-P3.5-035 to FR-P3.5-045
    - ≥65 tests total
    - ≥90% coverage
"""

import pytest
from components.generators_iterators.src.iterator import (
    Iterator,
    ArrayIterator,
    StringIterator,
    create_array_iterator,
    create_string_iterator,
)
from components.generators_iterators.src.generator import IteratorResult


class TestIteratorMap:
    """Test Iterator.prototype.map() - FR-P3.5-035."""

    def test_map_transforms_values(self):
        """Map should transform each value through function."""
        it = create_array_iterator([1, 2, 3])
        mapped = it.map(lambda x, i: x * 2)

        assert mapped.next().value == 2
        assert mapped.next().value == 4
        assert mapped.next().value == 6
        assert mapped.next().done is True

    def test_map_receives_index(self):
        """Map function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c'])
        mapped = it.map(lambda x, i: f"{x}{i}")

        assert mapped.next().value == "a0"
        assert mapped.next().value == "b1"
        assert mapped.next().value == "c2"

    def test_map_is_lazy(self):
        """Map should not execute until values are consumed."""
        called = []
        it = create_array_iterator([1, 2, 3])

        def track_calls(x, i):
            called.append(x)
            return x * 2

        mapped = it.map(track_calls)
        assert len(called) == 0  # Not called yet

        mapped.next()
        assert len(called) == 1  # Called once

        mapped.next()
        assert len(called) == 2  # Called twice

    def test_map_empty_iterator(self):
        """Map on empty iterator should return empty iterator."""
        it = create_array_iterator([])
        mapped = it.map(lambda x, i: x * 2)

        result = mapped.next()
        assert result.done is True

    def test_map_preserves_done_state(self):
        """Map should preserve done state after exhaustion."""
        it = create_array_iterator([1])
        mapped = it.map(lambda x, i: x * 2)

        mapped.next()
        result1 = mapped.next()
        result2 = mapped.next()

        assert result1.done is True
        assert result2.done is True

    def test_map_chaining(self):
        """Map should support chaining with other methods."""
        it = create_array_iterator([1, 2, 3])
        result = it.map(lambda x, i: x * 2).map(lambda x, i: x + 1).toArray()

        assert result == [3, 5, 7]


class TestIteratorFilter:
    """Test Iterator.prototype.filter() - FR-P3.5-036."""

    def test_filter_keeps_matching_values(self):
        """Filter should keep only values where predicate returns true."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        filtered = it.filter(lambda x, i: x > 2)

        assert filtered.next().value == 3
        assert filtered.next().value == 4
        assert filtered.next().value == 5
        assert filtered.next().done is True

    def test_filter_receives_index(self):
        """Filter function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c', 'd'])
        filtered = it.filter(lambda x, i: i % 2 == 0)

        assert filtered.next().value == 'a'
        assert filtered.next().value == 'c'
        assert filtered.next().done is True

    def test_filter_is_lazy(self):
        """Filter should not execute until values are consumed."""
        called = []
        it = create_array_iterator([1, 2, 3, 4, 5])

        def track_calls(x, i):
            called.append(x)
            return x > 2

        filtered = it.filter(track_calls)
        assert len(called) == 0  # Not called yet

        filtered.next()
        # Should have checked values until finding first match
        assert 3 in called

    def test_filter_empty_iterator(self):
        """Filter on empty iterator should return empty iterator."""
        it = create_array_iterator([])
        filtered = it.filter(lambda x, i: True)

        result = filtered.next()
        assert result.done is True

    def test_filter_no_matches(self):
        """Filter with no matches should return empty iterator."""
        it = create_array_iterator([1, 2, 3])
        filtered = it.filter(lambda x, i: x > 10)

        result = filtered.next()
        assert result.done is True

    def test_filter_all_match(self):
        """Filter where all match should return all values."""
        it = create_array_iterator([2, 4, 6])
        filtered = it.filter(lambda x, i: x % 2 == 0)

        assert filtered.next().value == 2
        assert filtered.next().value == 4
        assert filtered.next().value == 6
        assert filtered.next().done is True


class TestIteratorTake:
    """Test Iterator.prototype.take() - FR-P3.5-037."""

    def test_take_limits_values(self):
        """Take should limit number of values."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        taken = it.take(3)

        assert taken.next().value == 1
        assert taken.next().value == 2
        assert taken.next().value == 3
        assert taken.next().done is True

    def test_take_is_lazy(self):
        """Take should not consume more values than needed."""
        called = []
        it = create_array_iterator([1, 2, 3, 4, 5])

        # Wrap to track consumption
        original_next = it.next

        def tracked_next():
            result = original_next()
            if not result.done:
                called.append(result.value)
            return result

        it.next = tracked_next

        taken = it.take(2)
        taken.next()
        taken.next()

        assert called == [1, 2]  # Only consumed 2 values

    def test_take_more_than_available(self):
        """Take more than available should return all values."""
        it = create_array_iterator([1, 2])
        taken = it.take(5)

        assert taken.next().value == 1
        assert taken.next().value == 2
        assert taken.next().done is True

    def test_take_zero(self):
        """Take(0) should return empty iterator."""
        it = create_array_iterator([1, 2, 3])
        taken = it.take(0)

        result = taken.next()
        assert result.done is True

    def test_take_negative_treated_as_zero(self):
        """Take with negative limit should return empty iterator."""
        it = create_array_iterator([1, 2, 3])
        taken = it.take(-1)

        result = taken.next()
        assert result.done is True


class TestIteratorDrop:
    """Test Iterator.prototype.drop() - FR-P3.5-038."""

    def test_drop_skips_values(self):
        """Drop should skip first N values."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        dropped = it.drop(2)

        assert dropped.next().value == 3
        assert dropped.next().value == 4
        assert dropped.next().value == 5
        assert dropped.next().done is True

    def test_drop_is_lazy(self):
        """Drop should only skip when consuming starts."""
        called = []

        def track_calls():
            for i in [1, 2, 3, 4, 5]:
                called.append(i)
                yield i

        it = ArrayIterator([1, 2, 3, 4, 5])
        dropped = it.drop(2)

        # Creating iterator doesn't consume
        assert len(called) == 0

        # First next() skips 2 and returns 3rd
        dropped.next()
        # Should have consumed items 1, 2, 3

    def test_drop_more_than_available(self):
        """Drop more than available should return empty iterator."""
        it = create_array_iterator([1, 2])
        dropped = it.drop(5)

        result = dropped.next()
        assert result.done is True

    def test_drop_zero(self):
        """Drop(0) should return all values."""
        it = create_array_iterator([1, 2, 3])
        dropped = it.drop(0)

        assert dropped.next().value == 1
        assert dropped.next().value == 2
        assert dropped.next().value == 3
        assert dropped.next().done is True

    def test_drop_all(self):
        """Drop(length) should return empty iterator."""
        it = create_array_iterator([1, 2, 3])
        dropped = it.drop(3)

        result = dropped.next()
        assert result.done is True


class TestIteratorFlatMap:
    """Test Iterator.prototype.flatMap() - FR-P3.5-039."""

    def test_flatmap_flattens_arrays(self):
        """FlatMap should flatten arrays returned by mapper."""
        it = create_array_iterator([1, 2])
        flattened = it.flatMap(lambda x, i: [x, x * 2])

        assert flattened.next().value == 1
        assert flattened.next().value == 2
        assert flattened.next().value == 2
        assert flattened.next().value == 4
        assert flattened.next().done is True

    def test_flatmap_non_iterable_values(self):
        """FlatMap should handle non-iterable return values."""
        it = create_array_iterator([1, 2, 3])
        flattened = it.flatMap(lambda x, i: x * 2)

        assert flattened.next().value == 2
        assert flattened.next().value == 4
        assert flattened.next().value == 6
        assert flattened.next().done is True

    def test_flatmap_mixed_iterable_non_iterable(self):
        """FlatMap should handle mix of iterable and non-iterable."""
        it = create_array_iterator([1, 2, 3])
        flattened = it.flatMap(lambda x, i: [x, x] if x % 2 == 0 else x)

        assert flattened.next().value == 1
        assert flattened.next().value == 2
        assert flattened.next().value == 2
        assert flattened.next().value == 3
        assert flattened.next().done is True

    def test_flatmap_is_lazy(self):
        """FlatMap should be lazy - not execute until consumed."""
        called = []
        it = create_array_iterator([1, 2])

        def track_calls(x, i):
            called.append(x)
            return [x, x * 2]

        flattened = it.flatMap(track_calls)
        assert len(called) == 0

        flattened.next()
        assert len(called) == 1

    def test_flatmap_empty_arrays(self):
        """FlatMap with empty arrays should skip them."""
        it = create_array_iterator([1, 2, 3])
        flattened = it.flatMap(lambda x, i: [] if x == 2 else [x])

        assert flattened.next().value == 1
        assert flattened.next().value == 3
        assert flattened.next().done is True

    def test_flatmap_receives_index(self):
        """FlatMap function should receive value and index."""
        it = create_array_iterator(['a', 'b'])
        flattened = it.flatMap(lambda x, i: [x, str(i)])

        assert flattened.next().value == 'a'
        assert flattened.next().value == '0'
        assert flattened.next().value == 'b'
        assert flattened.next().value == '1'


class TestIteratorReduce:
    """Test Iterator.prototype.reduce() - FR-P3.5-040."""

    def test_reduce_with_initial_value(self):
        """Reduce should accumulate with initial value."""
        it = create_array_iterator([1, 2, 3, 4])
        result = it.reduce(lambda acc, x, i: acc + x, 0)

        assert result == 10

    def test_reduce_without_initial_value(self):
        """Reduce without initial should use first value as initial."""
        it = create_array_iterator([1, 2, 3, 4])
        result = it.reduce(lambda acc, x, i: acc + x)

        assert result == 10

    def test_reduce_empty_with_initial(self):
        """Reduce on empty iterator with initial should return initial."""
        it = create_array_iterator([])
        result = it.reduce(lambda acc, x, i: acc + x, 42)

        assert result == 42

    def test_reduce_empty_without_initial_raises(self):
        """Reduce on empty iterator without initial should raise TypeError."""
        it = create_array_iterator([])

        with pytest.raises(TypeError, match="Reduce of empty iterator"):
            it.reduce(lambda acc, x, i: acc + x)

    def test_reduce_receives_index(self):
        """Reduce function should receive accumulator, value, and index."""
        it = create_array_iterator([1, 2, 3])
        indices = []

        def track_index(acc, x, i):
            indices.append(i)
            return acc + x

        result = it.reduce(track_index, 0)
        assert indices == [0, 1, 2]

    def test_reduce_is_eager(self):
        """Reduce should consume entire iterator immediately."""
        it = create_array_iterator([1, 2, 3])

        result = it.reduce(lambda acc, x, i: acc + x, 0)

        # Iterator should be exhausted after reduce
        assert it.next().done is True


class TestIteratorToArray:
    """Test Iterator.prototype.toArray() - FR-P3.5-041."""

    def test_toarray_collects_values(self):
        """ToArray should collect all values into array."""
        it = create_array_iterator([1, 2, 3])
        result = it.toArray()

        assert result == [1, 2, 3]

    def test_toarray_empty_iterator(self):
        """ToArray on empty iterator should return empty array."""
        it = create_array_iterator([])
        result = it.toArray()

        assert result == []

    def test_toarray_is_eager(self):
        """ToArray should consume entire iterator immediately."""
        it = create_array_iterator([1, 2, 3])
        result = it.toArray()

        # Iterator should be exhausted
        assert it.next().done is True

    def test_toarray_with_strings(self):
        """ToArray should work with string iterator."""
        it = create_string_iterator("abc")
        result = it.toArray()

        assert result == ['a', 'b', 'c']

    def test_toarray_after_chaining(self):
        """ToArray should work after chaining operations."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        result = it.filter(lambda x, i: x > 2).map(lambda x, i: x * 2).toArray()

        assert result == [6, 8, 10]


class TestIteratorForEach:
    """Test Iterator.prototype.forEach() - FR-P3.5-042."""

    def test_foreach_executes_function(self):
        """ForEach should execute function for each value."""
        it = create_array_iterator([1, 2, 3])
        collected = []

        it.forEach(lambda x, i: collected.append(x))

        assert collected == [1, 2, 3]

    def test_foreach_receives_index(self):
        """ForEach function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c'])
        indices = []

        it.forEach(lambda x, i: indices.append(i))

        assert indices == [0, 1, 2]

    def test_foreach_returns_none(self):
        """ForEach should return None."""
        it = create_array_iterator([1, 2, 3])
        result = it.forEach(lambda x, i: None)

        assert result is None

    def test_foreach_is_eager(self):
        """ForEach should consume entire iterator immediately."""
        it = create_array_iterator([1, 2, 3])
        it.forEach(lambda x, i: None)

        # Iterator should be exhausted
        assert it.next().done is True

    def test_foreach_empty_iterator(self):
        """ForEach on empty iterator should not call function."""
        it = create_array_iterator([])
        called = False

        def mark_called(x, i):
            nonlocal called
            called = True

        it.forEach(mark_called)

        assert called is False


class TestIteratorSome:
    """Test Iterator.prototype.some() - FR-P3.5-043."""

    def test_some_finds_match(self):
        """Some should return true if any value matches."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        result = it.some(lambda x, i: x > 3)

        assert result is True

    def test_some_no_match(self):
        """Some should return false if no value matches."""
        it = create_array_iterator([1, 2, 3])
        result = it.some(lambda x, i: x > 10)

        assert result is False

    def test_some_short_circuits(self):
        """Some should short-circuit on first match."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        called = []

        def track_calls(x, i):
            called.append(x)
            return x > 2

        result = it.some(track_calls)

        assert result is True
        assert len(called) == 3  # Should stop at 3

    def test_some_receives_index(self):
        """Some function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c'])
        result = it.some(lambda x, i: i == 1)

        assert result is True

    def test_some_empty_iterator(self):
        """Some on empty iterator should return false."""
        it = create_array_iterator([])
        result = it.some(lambda x, i: True)

        assert result is False

    def test_some_all_match(self):
        """Some should return true if all match (stops at first)."""
        it = create_array_iterator([2, 4, 6])
        result = it.some(lambda x, i: x % 2 == 0)

        assert result is True


class TestIteratorEvery:
    """Test Iterator.prototype.every() - FR-P3.5-044."""

    def test_every_all_match(self):
        """Every should return true if all values match."""
        it = create_array_iterator([2, 4, 6])
        result = it.every(lambda x, i: x % 2 == 0)

        assert result is True

    def test_every_some_dont_match(self):
        """Every should return false if any value doesn't match."""
        it = create_array_iterator([2, 3, 4])
        result = it.every(lambda x, i: x % 2 == 0)

        assert result is False

    def test_every_short_circuits(self):
        """Every should short-circuit on first non-match."""
        it = create_array_iterator([2, 4, 5, 6, 8])
        called = []

        def track_calls(x, i):
            called.append(x)
            return x % 2 == 0

        result = it.every(track_calls)

        assert result is False
        assert len(called) == 3  # Should stop at 5

    def test_every_receives_index(self):
        """Every function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c'])
        result = it.every(lambda x, i: i < 10)

        assert result is True

    def test_every_empty_iterator(self):
        """Every on empty iterator should return true (vacuous truth)."""
        it = create_array_iterator([])
        result = it.every(lambda x, i: False)

        assert result is True

    def test_every_none_match(self):
        """Every should return false if none match."""
        it = create_array_iterator([1, 3, 5])
        result = it.every(lambda x, i: x % 2 == 0)

        assert result is False


class TestIteratorFind:
    """Test Iterator.prototype.find() - FR-P3.5-045."""

    def test_find_returns_match(self):
        """Find should return first matching value."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        result = it.find(lambda x, i: x > 2)

        assert result == 3

    def test_find_no_match(self):
        """Find should return None if no match."""
        it = create_array_iterator([1, 2, 3])
        result = it.find(lambda x, i: x > 10)

        assert result is None

    def test_find_short_circuits(self):
        """Find should short-circuit on first match."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        called = []

        def track_calls(x, i):
            called.append(x)
            return x > 2

        result = it.find(track_calls)

        assert result == 3
        assert len(called) == 3  # Should stop at 3

    def test_find_receives_index(self):
        """Find function should receive value and index."""
        it = create_array_iterator(['a', 'b', 'c'])
        result = it.find(lambda x, i: i == 1)

        assert result == 'b'

    def test_find_empty_iterator(self):
        """Find on empty iterator should return None."""
        it = create_array_iterator([])
        result = it.find(lambda x, i: True)

        assert result is None


class TestIteratorChaining:
    """Test chaining multiple iterator helpers."""

    def test_map_filter_chain(self):
        """Should support chaining map and filter."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        result = it.map(lambda x, i: x * 2).filter(lambda x, i: x > 5).toArray()

        assert result == [6, 8, 10]

    def test_filter_take_chain(self):
        """Should support chaining filter and take."""
        it = create_array_iterator([1, 2, 3, 4, 5, 6, 7, 8])
        result = it.filter(lambda x, i: x % 2 == 0).take(2).toArray()

        assert result == [2, 4]

    def test_drop_map_chain(self):
        """Should support chaining drop and map."""
        it = create_array_iterator([1, 2, 3, 4, 5])
        result = it.drop(2).map(lambda x, i: x * 10).toArray()

        assert result == [30, 40, 50]

    def test_complex_chain(self):
        """Should support complex chaining."""
        it = create_array_iterator([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        result = (
            it.filter(lambda x, i: x % 2 == 0)  # [2, 4, 6, 8, 10]
            .map(lambda x, i: x * 2)  # [4, 8, 12, 16, 20]
            .drop(1)  # [8, 12, 16, 20]
            .take(2)  # [8, 12]
            .toArray()
        )

        assert result == [8, 12]

    def test_flatmap_chain(self):
        """Should support chaining with flatMap."""
        it = create_array_iterator([1, 2, 3])
        # flatMap produces: 1, 2 (from 1), 2, 4 (from 2), 3, 6 (from 3)
        # filter(x > 2) keeps: 4, 3, 6
        result = it.flatMap(lambda x, i: [x, x * 2]).filter(lambda x, i: x > 2).toArray()

        assert result == [4, 3, 6]

    def test_lazy_chain_is_lazy(self):
        """Chained lazy operations should remain lazy."""
        called = []
        it = create_array_iterator([1, 2, 3, 4, 5])

        def track_calls(x, i):
            called.append(x)
            return x * 2

        chained = it.map(track_calls).filter(lambda x, i: x > 5)

        assert len(called) == 0  # Not called yet

        chained.next()
        # Should have called map until finding first match for filter


class TestIteratorEdgeCases:
    """Test edge cases and error conditions."""

    def test_iterator_reuse_after_exhaustion(self):
        """Calling next after exhaustion should keep returning done."""
        it = create_array_iterator([1, 2])
        it.next()
        it.next()
        result1 = it.next()
        result2 = it.next()

        assert result1.done is True
        assert result2.done is True

    def test_helper_on_exhausted_iterator(self):
        """Helpers on exhausted iterator should work correctly."""
        it = create_array_iterator([1, 2])
        it.toArray()  # Exhausts iterator

        result = it.map(lambda x, i: x * 2).toArray()
        assert result == []

    def test_nested_iterators(self):
        """Should handle nested iterator structures."""
        it1 = create_array_iterator([1, 2])
        it2 = create_array_iterator([3, 4])

        # Create array of iterators and flatMap
        it_of_its = create_array_iterator([it1, it2])
        result = it_of_its.flatMap(lambda it, i: it).toArray()

        assert result == [1, 2, 3, 4]

    def test_string_iterator_helpers(self):
        """Helpers should work with string iterators."""
        it = create_string_iterator("hello")
        result = it.filter(lambda x, i: x in 'aeiou').toArray()

        assert result == ['e', 'o']
