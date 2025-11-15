"""
for await...of loop implementation for JavaScript runtime.

Implements for-await-of loop that consumes async iterables per ECMAScript 2024.

Implements FR-P3.5-017: for await...of loop

Public API:
    - for_await_of: Execute for-await-of loop
    - ForAwaitOfError: Exception for for-await-of errors
"""

from typing import Any, Callable, Awaitable
from components.generators_iterators.src.async_iterator import (
    is_async_iterable,
    get_async_iterator,
)
from components.promise.src.js_promise import JSPromise
import asyncio


class ForAwaitOfError(Exception):
    """Exception raised during for-await-of execution."""

    pass


async def for_await_of(
    async_iterable: Any,
    body: Callable[[Any], Awaitable[None]],
    event_loop,
) -> None:
    """
    Execute for await...of loop over async iterable.

    Implements: for await (const item of asyncIterable) { body(item) }

    This function:
    1. Gets async iterator from async iterable
    2. Calls next() on iterator (returns Promise)
    3. Awaits the Promise
    4. Calls body with the value
    5. Repeats until done: true

    FR-P3.5-017: for await...of loop implementation

    Args:
        async_iterable: Async iterable to consume
        body: Async function to call for each value
        event_loop: EventLoop instance

    Raises:
        TypeError: If object is not async iterable
        ForAwaitOfError: If error occurs during iteration

    Example:
        >>> async def gen():
        ...     yield 1
        ...     yield 2
        >>> async def print_value(value):
        ...     print(value)
        >>> await for_await_of(gen(), print_value, loop)
        1
        2
    """
    # Check if async iterable
    if not is_async_iterable(async_iterable):
        raise TypeError(f"{type(async_iterable).__name__} is not async iterable")

    # Get async iterator
    iterator = get_async_iterator(async_iterable)

    try:
        while True:
            # Get next promise
            result_promise = iterator.next()

            # Await the promise to get {value, done}
            result = await _await_promise(result_promise, event_loop)

            # Check if done
            if result.done:
                break

            # Call body with value
            try:
                await body(result.value)
            except BreakException:
                # break statement in body
                break
            except ContinueException:
                # continue statement in body
                continue

    finally:
        # Cleanup: try to close iterator
        if hasattr(iterator, 'return_value') and callable(iterator.return_value):
            # AsyncGenerator has return_value method
            try:
                iterator.return_value()
            except:
                pass  # Ignore errors during cleanup


async def _await_promise(promise: JSPromise, event_loop) -> Any:
    """
    Convert JSPromise to Python awaitable.

    This is a helper function to bridge between JSPromise and Python async/await.

    Args:
        promise: JSPromise instance
        event_loop: EventLoop instance

    Returns:
        Resolved value of the promise

    Raises:
        Exception: If promise rejects
    """
    # Create a future to await
    future = asyncio.Future()

    # Attach handlers
    promise.then(
        lambda value: future.set_result(value) if not future.done() else None,
        lambda error: future.set_exception(error) if not future.done() else None
    )

    # Process microtasks to resolve promise
    event_loop.run()

    # Await the future
    return await future


class BreakException(Exception):
    """
    Exception used to implement break statement in for-await-of.

    This is an internal exception used to break out of async loops.
    """

    pass


class ContinueException(Exception):
    """
    Exception used to implement continue statement in for-await-of.

    This is an internal exception used to continue to next iteration.
    """

    pass


def execute_for_await_of_sync(
    async_iterable: Any,
    body: Callable[[Any], None],
    event_loop,
) -> None:
    """
    Synchronous wrapper for for-await-of loop.

    This function allows calling for-await-of from synchronous code
    by running the async loop in the event loop.

    Args:
        async_iterable: Async iterable to consume
        body: Function to call for each value (will be wrapped to async)
        event_loop: EventLoop instance

    Example:
        >>> async def gen():
        ...     yield 1
        ...     yield 2
        >>> values = []
        >>> execute_for_await_of_sync(gen(), lambda v: values.append(v), loop)
        >>> print(values)
        [1, 2]
    """

    async def async_body(value):
        """Wrap synchronous body in async function."""
        return body(value)

    # Run the async for-await-of
    asyncio.run(for_await_of(async_iterable, async_body, event_loop))


class ForAwaitOfContext:
    """
    Context manager for for-await-of loop execution.

    This provides proper cleanup and error handling for for-await-of loops.

    Example:
        >>> async with ForAwaitOfContext(async_gen, event_loop) as iterator:
        ...     async for value in iterator:
        ...         print(value)
    """

    def __init__(self, async_iterable: Any, event_loop):
        """
        Initialize for-await-of context.

        Args:
            async_iterable: Async iterable to consume
            event_loop: EventLoop instance
        """
        self.async_iterable = async_iterable
        self.event_loop = event_loop
        self.iterator = None

    async def __aenter__(self):
        """
        Enter context and get async iterator.

        Returns:
            AsyncIterator instance
        """
        if not is_async_iterable(self.async_iterable):
            raise TypeError(
                f"{type(self.async_iterable).__name__} is not async iterable"
            )

        self.iterator = get_async_iterator(self.async_iterable)
        return self.iterator

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context and cleanup iterator.

        Args:
            exc_type: Exception type (if exception occurred)
            exc_val: Exception value
            exc_tb: Exception traceback

        Returns:
            False (don't suppress exceptions)
        """
        # Try to close iterator
        if self.iterator is not None:
            if hasattr(self.iterator, 'return_value') and callable(
                self.iterator.return_value
            ):
                try:
                    await self.iterator.return_value()
                except:
                    pass  # Ignore errors during cleanup

        return False  # Don't suppress exceptions
