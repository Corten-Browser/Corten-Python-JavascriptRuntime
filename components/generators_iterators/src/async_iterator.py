"""
Async iterator protocol implementation for JavaScript runtime.

Implements the async iterator protocol (async next() method returning Promise<{value, done}>)
per ECMAScript 2024 specification.

Implements FR-P3.5-019: AsyncIterator protocol

Public API:
    - AsyncIterator: Base async iterator class
    - AsyncIterable: Protocol for async iterable objects
    - is_async_iterable: Check if object is async iterable
    - get_async_iterator: Get async iterator from async iterable
"""

from typing import Any, Protocol
from components.generators_iterators.src.async_generator import AsyncIteratorResult
from components.promise.src.js_promise import JSPromise


class AsyncIterator:
    """
    Base async iterator class implementing async iterator protocol.

    Per ECMAScript spec, async iterators have an async next() method that returns
    a Promise resolving to AsyncIteratorResult {value, done}.

    FR-P3.5-019: AsyncIterator protocol
    """

    def next(self) -> JSPromise:
        """
        Get next value from async iterator.

        Returns:
            Promise resolving to AsyncIteratorResult with {value, done}

        Raises:
            NotImplementedError: Subclasses must implement
        """
        raise NotImplementedError("Subclasses must implement async next()")

    def __aiter__(self):
        """
        Async iterators are async iterable (return self for Symbol.asyncIterator).

        Returns:
            self
        """
        return self

    async def __anext__(self):
        """
        Python async iterator protocol support.

        Returns:
            Next value (awaitable)

        Raises:
            StopAsyncIteration: When iterator is exhausted
        """
        result_promise = self.next()

        # This is a simplified implementation
        # In real implementation, we'd need to properly await the promise
        # For now, we'll raise NotImplementedError to indicate this needs
        # to be implemented by concrete classes
        raise NotImplementedError("Async iteration requires promise integration")


class AsyncIterable(Protocol):
    """
    Protocol for async iterable objects.

    Per ECMAScript spec, async iterables have Symbol.asyncIterator method.
    In Python, this is __aiter__.
    """

    def __aiter__(self) -> AsyncIterator:
        """
        Get async iterator for this async iterable.

        Returns:
            AsyncIterator instance
        """
        ...


def is_async_iterable(obj: Any) -> bool:
    """
    Check if object is async iterable (has Symbol.asyncIterator).

    Per ECMAScript spec, async iterable objects have a Symbol.asyncIterator
    method that returns an async iterator.

    Args:
        obj: Object to check

    Returns:
        True if async iterable, False otherwise

    Example:
        >>> async def gen():
        ...     yield 1
        >>> is_async_iterable(gen())
        True
        >>> is_async_iterable([1, 2, 3])
        False
    """
    # Check for Python's __aiter__ (Symbol.asyncIterator equivalent)
    return hasattr(obj, '__aiter__') and callable(getattr(obj, '__aiter__', None))


def get_async_iterator(async_iterable: Any) -> AsyncIterator:
    """
    Get async iterator from async iterable object.

    Calls obj[Symbol.asyncIterator]() (Python: __aiter__).

    Args:
        async_iterable: Async iterable object

    Returns:
        AsyncIterator instance

    Raises:
        TypeError: If object is not async iterable

    Example:
        >>> async def gen():
        ...     yield 1
        >>> async_gen = gen()
        >>> iterator = get_async_iterator(async_gen)
        >>> iterator is async_gen  # Generators are their own iterators
        True
    """
    if not is_async_iterable(async_iterable):
        raise TypeError(f"{type(async_iterable).__name__} is not async iterable")

    # Call __aiter__ to get the async iterator
    return async_iterable.__aiter__()


class AsyncArrayIterator(AsyncIterator):
    """
    Async iterator for arrays (yielding promises).

    This allows for-await-of to work with arrays of promises.

    Example:
        >>> loop = EventLoop()
        >>> promises = [
        ...     JSPromise.resolve(1, loop),
        ...     JSPromise.resolve(2, loop)
        ... ]
        >>> iterator = AsyncArrayIterator(promises, loop)
    """

    def __init__(self, array: list, event_loop):
        """
        Initialize async array iterator.

        Args:
            array: Array to iterate over (may contain promises)
            event_loop: EventLoop instance
        """
        self.array = array
        self.index = 0
        self.event_loop = event_loop

    def next(self) -> JSPromise:
        """
        Get next array element (wrapped in promise).

        If the element is already a promise, returns it.
        Otherwise, wraps it in a resolved promise.

        Returns:
            Promise resolving to AsyncIteratorResult
        """
        if self.index >= len(self.array):
            return JSPromise.resolve(
                AsyncIteratorResult(value=None, done=True),
                self.event_loop
            )

        value = self.array[self.index]
        self.index += 1

        # If value is a promise, wait for it
        if isinstance(value, JSPromise):
            def create_promise(resolve, reject):
                value.then(
                    lambda resolved_value: resolve(
                        AsyncIteratorResult(value=resolved_value, done=False)
                    ),
                    reject
                )

            return JSPromise(create_promise, self.event_loop)
        else:
            # Regular value, wrap in resolved promise
            return JSPromise.resolve(
                AsyncIteratorResult(value=value, done=False),
                self.event_loop
            )


def create_async_array_iterator(array: list, event_loop) -> AsyncArrayIterator:
    """
    Create async iterator for array.

    Allows arrays (especially arrays of promises) to be used with for-await-of.

    Args:
        array: Array to create async iterator for
        event_loop: EventLoop instance

    Returns:
        AsyncArrayIterator instance

    Example:
        >>> loop = EventLoop()
        >>> promises = [
        ...     JSPromise.resolve(1, loop),
        ...     JSPromise.resolve(2, loop)
        ... ]
        >>> iterator = create_async_array_iterator(promises, loop)
        >>> # Can now use with for-await-of
    """
    return AsyncArrayIterator(array, event_loop)
