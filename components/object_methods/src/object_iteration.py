"""
ObjectIteration - Object iteration support for ES2024.

Implements Object[Symbol.iterator] to make objects iterable.

Requirement: FR-ES24-043
"""

from typing import Any, Dict
from components.generators_iterators.src.generator import IteratorResult
from components.generators_iterators.src.iterator import Iterator


class ObjectIterator(Iterator):
    """
    Iterator for JavaScript objects.

    Iterates over object entries as [key, value] pairs,
    implementing Object.prototype[Symbol.iterator].

    Per ES2024 spec, objects are iterable and yield [key, value] pairs
    for enumerable own properties.
    """

    def __init__(self, obj: Dict[str, Any]):
        """
        Initialize object iterator.

        Args:
            obj: Object to iterate over
        """
        self.obj = obj
        self.keys = list(obj.keys())
        self.index = 0

    def next(self) -> IteratorResult:
        """
        Get next [key, value] pair from object.

        Returns:
            IteratorResult with [key, value] pair or done: true

        Example:
            >>> obj = {"a": 1, "b": 2}
            >>> iterator = ObjectIterator(obj)
            >>> result = iterator.next()
            >>> result.value
            ['a', 1]
        """
        if self.index >= len(self.keys):
            return IteratorResult(value=None, done=True)

        key = self.keys[self.index]
        value = self.obj[key]
        self.index += 1

        # Return [key, value] pair
        return IteratorResult(value=[key, value], done=False)


class ObjectIteration:
    """
    Object iteration support.

    Provides methods to get iterators for objects,
    implementing Object[Symbol.iterator] behavior.
    """

    @staticmethod
    def get_iterator(obj: Dict[str, Any]) -> ObjectIterator:
        """
        Get iterator for object (Symbol.iterator).

        Implements Object.prototype[Symbol.iterator]() behavior.

        Args:
            obj: Object to create iterator for

        Returns:
            ObjectIterator yielding [key, value] pairs

        Example:
            >>> obj = {"x": 10, "y": 20}
            >>> iterator = ObjectIteration.get_iterator(obj)
            >>> list(iterator)
            [['x', 10], ['y', 20]]

        Note:
            In full ES2024 implementation, this would be accessed via
            obj[Symbol.iterator](), but for Python we provide a static method.
        """
        return ObjectIterator(obj)
