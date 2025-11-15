"""
Async generator implementation for JavaScript runtime.

Implements async generator functions, async generator objects, and async iteration
per ECMAScript 2024 specification.

Implements FR-P3.5-014 through FR-P3.5-019:
- FR-P3.5-014: async function* syntax
- FR-P3.5-015: await in generators
- FR-P3.5-016: Symbol.asyncIterator
- FR-P3.5-018: AsyncGenerator object protocol

Public API:
    - AsyncGeneratorState: Enum of async generator states
    - AsyncIteratorResult: Result object from async next/return/throw
    - AsyncGenerator: Async generator object class
    - AsyncGeneratorFunction: Wrapper for async generator functions
"""

from enum import Enum, auto
from typing import Any, Callable, Optional
from dataclasses import dataclass
import asyncio
import inspect

from components.promise.src.js_promise import JSPromise


class AsyncGeneratorState(Enum):
    """
    Async generator execution states per ECMAScript spec.

    States:
        SUSPENDED_START: Generator created but not started
        SUSPENDED_YIELD: Generator suspended at yield
        EXECUTING: Generator currently running
        COMPLETED: Generator finished (done: true)
    """

    SUSPENDED_START = auto()
    SUSPENDED_YIELD = auto()
    EXECUTING = auto()
    COMPLETED = auto()


@dataclass
class AsyncIteratorResult:
    """
    Async iterator result object per ECMAScript async iterator protocol.

    Attributes:
        value: The yielded or returned value
        done: True if iterator is exhausted, False otherwise
    """

    value: Any
    done: bool


class AsyncExecutionContext:
    """
    Execution context for async generator state preservation.

    Stores local variables, instruction pointer, and call stack
    state for async generator suspension/resumption.
    """

    def __init__(self):
        """Initialize empty execution context."""
        self.locals = {}
        self.instruction_pointer = 0
        self.stack = []
        self.sent_value = None  # Value sent via next(value)


class AsyncGenerator:
    """
    Async generator object implementing async iterator and async iterable protocols.

    An async generator is returned when calling an async generator function. It implements
    the async iterator protocol (next, return, throw returning Promises) and is also
    async iterable (has Symbol.asyncIterator).

    Implements FR-P3.5-018: AsyncGenerator object protocol
    - next() returns Promise<{value, done}>
    - return(value) returns Promise<{value, done}>
    - throw(exception) returns Promise<{value, done}>

    Attributes:
        generator_function: The original async generator function
        state: Current async generator state
        execution_context: Preserved execution state
        event_loop: Event loop for promise resolution
    """

    def __init__(self, generator_function: Callable, event_loop):
        """
        Initialize async generator object.

        Args:
            generator_function: The async generator function to execute
            event_loop: EventLoop instance for promise handling
        """
        self.generator_function = generator_function
        self.state = AsyncGeneratorState.SUSPENDED_START
        self.execution_context = AsyncExecutionContext()
        self.event_loop = event_loop
        self._iterator = None  # Internal async iterator from generator function

    def next(self, value: Any = None) -> JSPromise:
        """
        Resume async generator execution and get next yielded value.

        Implements AsyncGenerator.next(value) per ECMAScript spec.
        Returns a Promise that resolves to {value, done}.

        FR-P3.5-018: AsyncGenerator.next() returns Promise<{value, done}>

        Args:
            value: Optional value to send into generator (becomes yield expression result)

        Returns:
            Promise resolving to AsyncIteratorResult with {value, done}
        """
        # Check if already completed
        if self.state == AsyncGeneratorState.COMPLETED:
            return JSPromise.resolve(
                AsyncIteratorResult(value=None, done=True),
                self.event_loop
            )

        # Store sent value for yield expression
        self.execution_context.sent_value = value

        def executor(resolve, reject):
            try:
                # Update state to executing
                self.state = AsyncGeneratorState.EXECUTING

                # Initialize iterator on first call
                if self._iterator is None:
                    self._iterator = self.generator_function()

                # Try to get next value
                if inspect.isasyncgen(self._iterator):
                    # Async generator - create a task to get next value
                    self._handle_async_next(value, resolve, reject)
                else:
                    # Regular generator
                    try:
                        if value is None or self.state == AsyncGeneratorState.SUSPENDED_START:
                            yielded_value = next(self._iterator)
                        else:
                            yielded_value = self._iterator.send(value)

                        self.state = AsyncGeneratorState.SUSPENDED_YIELD
                        resolve(AsyncIteratorResult(value=yielded_value, done=False))

                    except StopIteration as e:
                        self.state = AsyncGeneratorState.COMPLETED
                        return_value = getattr(e, 'value', None)
                        resolve(AsyncIteratorResult(value=return_value, done=True))

            except Exception as e:
                self.state = AsyncGeneratorState.COMPLETED
                reject(e)

        return JSPromise(executor, self.event_loop)

    def _handle_async_next(self, value, resolve, reject):
        """
        Handle async generator next() call.

        This schedules the async operation and resolves/rejects appropriately.
        Coordinates between asyncio event loop and JSPromise EventLoop.
        """
        async def execute_next():
            try:
                if value is None and self.state == AsyncGeneratorState.SUSPENDED_START:
                    yielded_value = await self._iterator.__anext__()
                else:
                    if hasattr(self._iterator, 'asend'):
                        yielded_value = await self._iterator.asend(value)
                    else:
                        yielded_value = await self._iterator.__anext__()

                self.state = AsyncGeneratorState.SUSPENDED_YIELD
                resolve(AsyncIteratorResult(value=yielded_value, done=False))

            except StopAsyncIteration as e:
                self.state = AsyncGeneratorState.COMPLETED
                return_value = getattr(e, 'value', None)
                resolve(AsyncIteratorResult(value=return_value, done=True))

            except Exception as e:
                self.state = AsyncGeneratorState.COMPLETED
                reject(e)

        # Get or create event loop (reuse existing if available)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Wrap execute_next to pump EventLoop while waiting
        async def execute_with_pump():
            # Create the execution task
            task = asyncio.create_task(execute_next())

            # Pump both loops until task completes
            while not task.done():
                # Let asyncio process one iteration
                await asyncio.sleep(0)
                # Pump JSPromise EventLoop
                self.event_loop.run()

            # Final pump after task completes
            self.event_loop.run()

            # Return task result or raise exception
            return await task

        # Run the pumping wrapper
        loop.run_until_complete(execute_with_pump())

    def return_value(self, value: Any = None) -> JSPromise:
        """
        Complete async generator early with return value.

        Implements AsyncGenerator.return(value) per ECMAScript spec.
        Returns a Promise that resolves to {value: value, done: true}.

        FR-P3.5-018: AsyncGenerator.return(value)

        Args:
            value: Value to return (default: undefined/None)

        Returns:
            Promise resolving to AsyncIteratorResult with {value: value, done: true}
        """
        # If already completed, return completion result
        if self.state == AsyncGeneratorState.COMPLETED:
            return JSPromise.resolve(
                AsyncIteratorResult(value=value, done=True),
                self.event_loop
            )

        def executor(resolve, reject):
            try:
                # Try to close the generator properly
                if self._iterator is not None:
                    if inspect.isasyncgen(self._iterator):
                        # Async generator - use aclose
                        async def execute_return():
                            try:
                                if hasattr(self._iterator, 'aclose'):
                                    await self._iterator.aclose()
                            finally:
                                self.state = AsyncGeneratorState.COMPLETED
                                resolve(AsyncIteratorResult(value=value, done=True))

                        # Get or create event loop (reuse existing if available)
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_closed():
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        # Wrap execute_return to pump EventLoop while waiting
                        async def execute_return_with_pump():
                            task = asyncio.create_task(execute_return())
                            while not task.done():
                                await asyncio.sleep(0)
                                self.event_loop.run()
                            self.event_loop.run()
                            return await task

                        loop.run_until_complete(execute_return_with_pump())
                    else:
                        # Regular generator
                        if hasattr(self._iterator, 'close'):
                            self._iterator.close()
                        self.state = AsyncGeneratorState.COMPLETED
                        resolve(AsyncIteratorResult(value=value, done=True))
                else:
                    self.state = AsyncGeneratorState.COMPLETED
                    resolve(AsyncIteratorResult(value=value, done=True))

            except Exception as e:
                self.state = AsyncGeneratorState.COMPLETED
                reject(e)

        return JSPromise(executor, self.event_loop)

    def throw(self, exception: Exception) -> JSPromise:
        """
        Throw exception into async generator at current yield point.

        Implements AsyncGenerator.throw(exception) per ECMAScript spec.
        Returns a Promise that resolves to next value or rejects with exception.

        FR-P3.5-018: AsyncGenerator.throw(exception)

        Args:
            exception: Exception to throw into generator

        Returns:
            Promise resolving to AsyncIteratorResult if exception is caught,
            or rejecting with exception if not caught
        """
        # If not started, reject immediately
        if self.state == AsyncGeneratorState.SUSPENDED_START:
            self.state = AsyncGeneratorState.COMPLETED
            return JSPromise.reject(exception, self.event_loop)

        # If already completed, reject immediately
        if self.state == AsyncGeneratorState.COMPLETED:
            return JSPromise.reject(exception, self.event_loop)

        def executor(resolve, reject):
            try:
                # Update state
                self.state = AsyncGeneratorState.EXECUTING

                # Throw into generator
                if self._iterator is not None:
                    if inspect.isasyncgen(self._iterator) and hasattr(self._iterator, 'athrow'):
                        # Async generator - use athrow
                        async def execute_throw():
                            try:
                                yielded_value = await self._iterator.athrow(exception)
                                self.state = AsyncGeneratorState.SUSPENDED_YIELD
                                resolve(AsyncIteratorResult(value=yielded_value, done=False))

                            except StopAsyncIteration as e:
                                self.state = AsyncGeneratorState.COMPLETED
                                return_value = getattr(e, 'value', None)
                                resolve(AsyncIteratorResult(value=return_value, done=True))

                            except Exception as e:
                                self.state = AsyncGeneratorState.COMPLETED
                                reject(e)

                        # Get or create event loop (reuse existing if available)
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_closed():
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                        except RuntimeError:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                        # Wrap execute_throw to pump EventLoop while waiting
                        async def execute_throw_with_pump():
                            task = asyncio.create_task(execute_throw())
                            while not task.done():
                                await asyncio.sleep(0)
                                self.event_loop.run()
                            self.event_loop.run()
                            return await task

                        loop.run_until_complete(execute_throw_with_pump())

                    elif hasattr(self._iterator, 'throw'):
                        # Regular generator
                        try:
                            yielded_value = self._iterator.throw(exception)
                            self.state = AsyncGeneratorState.SUSPENDED_YIELD
                            resolve(AsyncIteratorResult(value=yielded_value, done=False))
                        except StopIteration as e:
                            self.state = AsyncGeneratorState.COMPLETED
                            return_value = getattr(e, 'value', None)
                            resolve(AsyncIteratorResult(value=return_value, done=True))
                        except Exception as e:
                            self.state = AsyncGeneratorState.COMPLETED
                            reject(e)
                    else:
                        # No throw method, reject
                        self.state = AsyncGeneratorState.COMPLETED
                        reject(exception)
                else:
                    # No iterator, reject
                    self.state = AsyncGeneratorState.COMPLETED
                    reject(exception)

            except Exception as e:
                self.state = AsyncGeneratorState.COMPLETED
                reject(e)

        return JSPromise(executor, self.event_loop)

    def __aiter__(self):
        """
        Implement async iterable protocol (Symbol.asyncIterator).

        Async generators are their own async iterators per ECMAScript spec.

        FR-P3.5-016: Symbol.asyncIterator implementation

        Returns:
            self
        """
        return self

    def __anext__(self):
        """
        Python async iterator protocol support.

        Allows using Python's built-in async iteration (async for loops).

        Returns:
            Promise resolving to next yielded value

        Raises:
            StopAsyncIteration: When generator completes
        """
        async def get_next():
            result_promise = self.next()

            # Wait for promise to resolve
            # This is a simplified implementation
            result = await self._promise_to_awaitable(result_promise)

            if result.done:
                if result.value is not None:
                    raise StopAsyncIteration(result.value)
                raise StopAsyncIteration

            return result.value

        return get_next()

    async def _promise_to_awaitable(self, promise):
        """
        Convert JSPromise to Python awaitable.

        This is a helper method to bridge between JSPromise and Python async/await.

        Args:
            promise: JSPromise instance

        Returns:
            Resolved value of the promise
        """
        # Create a future to await
        future = asyncio.Future()

        # Attach handlers
        promise.then(
            lambda value: future.set_result(value) if not future.done() else None,
            lambda error: future.set_exception(error) if not future.done() else None
        )

        # Run event loop to process promise
        self.event_loop.run()

        return await future


class AsyncGeneratorFunction:
    """
    Wrapper for async generator functions.

    Creates AsyncGenerator objects when called. Represents async function*
    declarations and expressions.

    FR-P3.5-014: async function* syntax

    The wrapped function should be a Python async generator (async def with yield).

    Attributes:
        func: The Python async generator function
        event_loop: EventLoop instance for async operations
    """

    def __init__(self, func: Callable, event_loop):
        """
        Initialize async generator function wrapper.

        Args:
            func: Python async generator function (async def with yield)
            event_loop: EventLoop instance
        """
        self.func = func
        self.event_loop = event_loop

    def __call__(self, *args, **kwargs) -> AsyncGenerator:
        """
        Call async generator function to create async generator object.

        Returns:
            New AsyncGenerator instance
        """
        # Create a closure that captures args/kwargs
        def create_generator():
            return self.func(*args, **kwargs)

        return AsyncGenerator(create_generator, self.event_loop)
