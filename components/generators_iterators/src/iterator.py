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
