"""
Iterator protocol implementation for JavaScript runtime.

Implements the iterator protocol (next() method returning {value, done})
and provides iterator implementations for built-in types (Array, String, etc).

Public API:
    - Iterator: Base iterator class
    - Iterable: Protocol for iterable objects
    - create_array_iterator: Create iterator for arrays
    - create_string_iterator: Create iterator for strings
"""

from typing import Any, List, Protocol
from components.generators_iterators.src.generator import IteratorResult


class Iterator:
    """
    Base iterator class implementing iterator protocol.

    Per ECMAScript spec, iterators have a next() method that returns
    IteratorResult {value, done}.
    """

    def next(self) -> IteratorResult:
        """
        Get next value from iterator.

        Returns:
            IteratorResult with {value, done}

        Raises:
            NotImplementedError: Subclasses must implement
        """
        raise NotImplementedError("Subclasses must implement next()")

    def __iter__(self):
        """
        Iterators are iterable (return self for Symbol.iterator).

        Returns:
            self
        """
        return self

    def __next__(self):
        """
        Python iterator protocol support.

        Returns:
            Next value

        Raises:
            StopIteration: When iterator is exhausted
        """
        result = self.next()
        if result.done:
            raise StopIteration
        return result.value

    # ES2024 Iterator Helper Methods

    def map(self, fn):
        """
        Lazily map values through a function.

        Returns a new iterator that yields values transformed by fn.
        This is a lazy operation - fn is called only when values are consumed.

        Args:
            fn: Function to transform values (value, index) -> transformed_value

        Returns:
            MappedIterator yielding mapped values
        """
        return MappedIterator(self, fn)

    def filter(self, fn):
        """
        Lazily filter values by predicate.

        Returns a new iterator that yields only values where fn returns truthy.
        This is a lazy operation - fn is called only when values are consumed.

        Args:
            fn: Predicate function (value, index) -> boolean

        Returns:
            FilteredIterator yielding only matching values
        """
        return FilteredIterator(self, fn)

    def take(self, limit):
        """
        Take first N values from iterator.

        Returns a new iterator that yields at most N values.
        This is a lazy operation.

        Args:
            limit: Maximum number of values to take

        Returns:
            TakeIterator yielding at most limit values
        """
        return TakeIterator(self, limit)

    def drop(self, limit):
        """
        Skip first N values from iterator.

        Returns a new iterator that skips the first N values.
        This is a lazy operation.

        Args:
            limit: Number of values to skip

        Returns:
            DropIterator yielding values after skipping limit
        """
        return DropIterator(self, limit)

    def flatMap(self, fn):
        """
        Map and flatten in one step.

        Returns a new iterator that maps values through fn and flattens
        the results. If fn returns an iterable, it's flattened.
        This is a lazy operation.

        Args:
            fn: Function returning values or iterables (value, index) -> value|iterable

        Returns:
            FlatMapIterator yielding flattened mapped values
        """
        return FlatMapIterator(self, fn)

    def reduce(self, fn, initial=None):
        """
        Reduce iterator to single value.

        This is an EAGER operation - consumes entire iterator immediately.

        Args:
            fn: Reducer function (accumulator, value, index) -> new_accumulator
            initial: Initial accumulator value (optional)

        Returns:
            Final accumulated value

        Raises:
            TypeError: If iterator is empty and no initial value provided
        """
        has_initial = initial is not None
        accumulator = initial
        index = 0

        for value in self:
            if not has_initial:
                accumulator = value
                has_initial = True
            else:
                accumulator = fn(accumulator, value, index)
            index += 1

        if not has_initial:
            raise TypeError("Reduce of empty iterator with no initial value")

        return accumulator

    def toArray(self):
        """
        Collect all iterator values into array.

        This is an EAGER operation - consumes entire iterator immediately.

        Returns:
            List containing all values from iterator
        """
        return list(self)

    def forEach(self, fn):
        """
        Execute function for each value.

        This is an EAGER operation - consumes entire iterator immediately.

        Args:
            fn: Function to execute (value, index) -> void

        Returns:
            None
        """
        for index, value in enumerate(self):
            fn(value, index)

    def some(self, fn):
        """
        Test if ANY value matches predicate.

        Short-circuits on first match.
        This is an EAGER operation but may not consume entire iterator.

        Args:
            fn: Predicate function (value, index) -> boolean

        Returns:
            True if any value matches, False otherwise
        """
        for index, value in enumerate(self):
            if fn(value, index):
                return True
        return False

    def every(self, fn):
        """
        Test if ALL values match predicate.

        Short-circuits on first non-match.
        This is an EAGER operation but may not consume entire iterator.

        Args:
            fn: Predicate function (value, index) -> boolean

        Returns:
            True if all values match, False otherwise
        """
        for index, value in enumerate(self):
            if not fn(value, index):
                return False
        return True

    def find(self, fn):
        """
        Find first matching value.

        Short-circuits on first match.
        This is an EAGER operation but may not consume entire iterator.

        Args:
            fn: Predicate function (value, index) -> boolean

        Returns:
            First matching value or None
        """
        for index, value in enumerate(self):
            if fn(value, index):
                return value
        return None


class Iterable(Protocol):
    """
    Protocol for iterable objects.

    Per ECMAScript spec, iterables have Symbol.iterator method.
    In Python, this is __iter__.
    """

    def __iter__(self) -> Iterator:
        """
        Get iterator for this iterable.

        Returns:
            Iterator instance
        """
        ...


class ArrayIterator(Iterator):
    """
    Iterator for JavaScript arrays.

    Iterates over array elements in index order.
    """

    def __init__(self, array: List[Any]):
        """
        Initialize array iterator.

        Args:
            array: Array to iterate over
        """
        self.array = array
        self.index = 0

    def next(self) -> IteratorResult:
        """
        Get next array element.

        Returns:
            IteratorResult with next element or done: true
        """
        if self.index >= len(self.array):
            return IteratorResult(value=None, done=True)

        value = self.array[self.index]
        self.index += 1
        return IteratorResult(value=value, done=False)


class StringIterator(Iterator):
    """
    Iterator for JavaScript strings.

    Iterates over string characters (code points).
    """

    def __init__(self, string: str):
        """
        Initialize string iterator.

        Args:
            string: String to iterate over
        """
        self.string = string
        self.index = 0

    def next(self) -> IteratorResult:
        """
        Get next character from string.

        Returns:
            IteratorResult with next character or done: true
        """
        if self.index >= len(self.string):
            return IteratorResult(value=None, done=True)

        value = self.string[self.index]
        self.index += 1
        return IteratorResult(value=value, done=False)


def create_array_iterator(array: List[Any]) -> ArrayIterator:
    """
    Create iterator for array.

    Implements Array.prototype[Symbol.iterator]() behavior.

    Args:
        array: Array to create iterator for

    Returns:
        ArrayIterator instance
    """
    return ArrayIterator(array)


def create_string_iterator(string: str) -> StringIterator:
    """
    Create iterator for string.

    Implements String.prototype[Symbol.iterator]() behavior.

    Args:
        string: String to create iterator for

    Returns:
        StringIterator instance
    """
    return StringIterator(string)


def is_iterable(obj: Any) -> bool:
    """
    Check if object is iterable (has Symbol.iterator).

    Args:
        obj: Object to check

    Returns:
        True if iterable, False otherwise
    """
    return hasattr(obj, '__iter__')


def get_iterator(iterable: Any) -> Iterator:
    """
    Get iterator from iterable object.

    Calls obj[Symbol.iterator]() (Python: __iter__).

    Args:
        iterable: Iterable object

    Returns:
        Iterator instance

    Raises:
        TypeError: If object is not iterable
    """
    if not is_iterable(iterable):
        raise TypeError(f"{type(iterable).__name__} is not iterable")

    return iter(iterable)


# Helper iterator classes for lazy operations

class PythonIteratorAdapter(Iterator):
    """
    Adapter to wrap Python iterators into Iterator protocol.

    Converts Python iterator (with __next__) to Iterator (with next()).
    """

    def __init__(self, python_iter):
        """
        Initialize adapter.

        Args:
            python_iter: Python iterator (has __next__)
        """
        self.python_iter = python_iter

    def next(self) -> IteratorResult:
        """
        Get next value from Python iterator.

        Returns:
            IteratorResult with next value or done: true
        """
        try:
            value = next(self.python_iter)
            return IteratorResult(value=value, done=False)
        except StopIteration:
            return IteratorResult(value=None, done=True)


class MappedIterator(Iterator):
    """
    Iterator that lazily maps values through a function.

    Used by Iterator.prototype.map().
    """

    def __init__(self, source: Iterator, fn):
        """
        Initialize mapped iterator.

        Args:
            source: Source iterator
            fn: Mapping function (value, index) -> transformed_value
        """
        self.source = source
        self.fn = fn
        self.index = 0

    def next(self) -> IteratorResult:
        """
        Get next mapped value.

        Returns:
            IteratorResult with mapped value or done: true
        """
        result = self.source.next()
        if result.done:
            return result

        mapped_value = self.fn(result.value, self.index)
        self.index += 1
        return IteratorResult(value=mapped_value, done=False)


class FilteredIterator(Iterator):
    """
    Iterator that lazily filters values by predicate.

    Used by Iterator.prototype.filter().
    """

    def __init__(self, source: Iterator, fn):
        """
        Initialize filtered iterator.

        Args:
            source: Source iterator
            fn: Predicate function (value, index) -> boolean
        """
        self.source = source
        self.fn = fn
        self.index = 0

    def next(self) -> IteratorResult:
        """
        Get next filtered value.

        Returns:
            IteratorResult with next matching value or done: true
        """
        while True:
            result = self.source.next()
            if result.done:
                return result

            if self.fn(result.value, self.index):
                self.index += 1
                return result

            self.index += 1


class TakeIterator(Iterator):
    """
    Iterator that takes first N values.

    Used by Iterator.prototype.take().
    """

    def __init__(self, source: Iterator, limit: int):
        """
        Initialize take iterator.

        Args:
            source: Source iterator
            limit: Maximum number of values to take
        """
        self.source = source
        self.limit = limit
        self.count = 0

    def next(self) -> IteratorResult:
        """
        Get next value if under limit.

        Returns:
            IteratorResult with next value or done: true
        """
        if self.count >= self.limit:
            return IteratorResult(value=None, done=True)

        result = self.source.next()
        if result.done:
            return result

        self.count += 1
        return result


class DropIterator(Iterator):
    """
    Iterator that skips first N values.

    Used by Iterator.prototype.drop().
    """

    def __init__(self, source: Iterator, limit: int):
        """
        Initialize drop iterator.

        Args:
            source: Source iterator
            limit: Number of values to skip
        """
        self.source = source
        self.limit = limit
        self.skipped = 0

    def next(self) -> IteratorResult:
        """
        Get next value after skipping limit.

        Returns:
            IteratorResult with next value or done: true
        """
        # Skip initial values
        while self.skipped < self.limit:
            result = self.source.next()
            if result.done:
                return result
            self.skipped += 1

        # Return remaining values
        return self.source.next()


class FlatMapIterator(Iterator):
    """
    Iterator that maps and flattens in one step.

    Used by Iterator.prototype.flatMap().
    """

    def __init__(self, source: Iterator, fn):
        """
        Initialize flatMap iterator.

        Args:
            source: Source iterator
            fn: Mapping function (value, index) -> value|iterable
        """
        self.source = source
        self.fn = fn
        self.index = 0
        self.current_inner = None

    def next(self) -> IteratorResult:
        """
        Get next flattened value.

        Returns:
            IteratorResult with next value or done: true
        """
        while True:
            # If we have an inner iterator, try to get next value from it
            if self.current_inner is not None:
                try:
                    inner_result = self.current_inner.next()
                    if not inner_result.done:
                        return inner_result
                except (AttributeError, StopIteration):
                    pass

                # Inner iterator exhausted, clear it
                self.current_inner = None

            # Get next value from source
            result = self.source.next()
            if result.done:
                return result

            # Map the value
            mapped = self.fn(result.value, self.index)
            self.index += 1

            # Check if mapped value is iterable
            if is_iterable(mapped) and not isinstance(mapped, str):
                # Create iterator for it
                if isinstance(mapped, Iterator):
                    self.current_inner = mapped
                elif isinstance(mapped, list):
                    # Convert list to ArrayIterator
                    self.current_inner = ArrayIterator(mapped)
                else:
                    # Try to create iterator from iterable
                    try:
                        python_iter = iter(mapped)
                        # Wrap Python iterator in an adapter
                        self.current_inner = PythonIteratorAdapter(python_iter)
                    except TypeError:
                        # Not actually iterable, return as-is
                        return IteratorResult(value=mapped, done=False)
            else:
                # Not iterable, return directly
                return IteratorResult(value=mapped, done=False)
