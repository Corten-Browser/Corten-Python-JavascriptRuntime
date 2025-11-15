"""
Generator implementation for JavaScript runtime.

Implements generator functions, generator objects, yield expressions,
and generator state management per ECMAScript 2024 specification.

Public API:
    - GeneratorState: Enum of generator states
    - IteratorResult: Result object from next/return/throw
    - Generator: Generator object class
    - GeneratorFunction: Wrapper for generator functions
"""

from enum import Enum, auto
from typing import Any, Callable, Optional
from dataclasses import dataclass


class GeneratorState(Enum):
    """
    Generator execution states per ECMAScript spec.

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
class IteratorResult:
    """
    Iterator result object per ECMAScript iterator protocol.

    Attributes:
        value: The yielded or returned value
        done: True if iterator is exhausted, False otherwise
    """

    value: Any
    done: bool


class ExecutionContext:
    """
    Execution context for generator state preservation.

    Stores local variables, instruction pointer, and call stack
    state for generator suspension/resumption.
    """

    def __init__(self):
        """Initialize empty execution context."""
        self.locals = {}
        self.instruction_pointer = 0
        self.stack = []
        self.sent_value = None  # Value sent via next(value)


class Generator:
    """
    Generator object implementing iterator and iterable protocols.

    A generator is returned when calling a generator function. It implements
    the iterator protocol (next, return, throw) and is also iterable.

    Attributes:
        generator_function: The original generator function
        state: Current generator state
        execution_context: Preserved execution state
    """

    def __init__(self, generator_function: Callable):
        """
        Initialize generator object.

        Args:
            generator_function: The generator function to execute
        """
        self.generator_function = generator_function
        self.state = GeneratorState.SUSPENDED_START
        self.execution_context = ExecutionContext()
        self._iterator = None  # Internal iterator from generator function

    def next(self, value: Any = None) -> IteratorResult:
        """
        Resume generator execution and get next yielded value.

        Implements generator.next(value) per ECMAScript spec.
        On first call, starts generator execution.
        On subsequent calls, resumes at last yield with optional sent value.

        Args:
            value: Optional value to send into generator (becomes yield expression result)

        Returns:
            IteratorResult with {value, done}

        Raises:
            StopIteration: When generator completes naturally
        """
        # Check if already completed
        if self.state == GeneratorState.COMPLETED:
            raise StopIteration

        # Store sent value for yield expression
        self.execution_context.sent_value = value

        try:
            # Update state to executing
            self.state = GeneratorState.EXECUTING

            # Initialize iterator on first call
            if self._iterator is None:
                self._iterator = self.generator_function()
                # First call: use next() (sent value is ignored)
                yielded_value = next(self._iterator)
            else:
                # Subsequent calls: use send() to pass value into generator
                yielded_value = self._iterator.send(value)

            # Generator suspended at yield
            self.state = GeneratorState.SUSPENDED_YIELD
            return IteratorResult(value=yielded_value, done=False)

        except StopIteration as e:
            # Generator completed
            self.state = GeneratorState.COMPLETED
            # Return value from generator (if any)
            return_value = getattr(e, 'value', None)
            return IteratorResult(value=return_value, done=True)

    def return_value(self, value: Any = None) -> IteratorResult:
        """
        Complete generator early with return value.

        Implements generator.return(value) per ECMAScript spec.
        Executes finally blocks and completes generator.

        Args:
            value: Value to return (default: undefined/None)

        Returns:
            IteratorResult with {value: value, done: true}
        """
        # If already completed, return completion result
        if self.state == GeneratorState.COMPLETED:
            return IteratorResult(value=value, done=True)

        try:
            # Try to close the generator properly
            if self._iterator is not None:
                if hasattr(self._iterator, 'close'):
                    self._iterator.close()
        finally:
            # Mark as completed
            self.state = GeneratorState.COMPLETED

        return IteratorResult(value=value, done=True)

    def throw(self, exception: Exception) -> IteratorResult:
        """
        Throw exception into generator at current yield point.

        Implements generator.throw(exception) per ECMAScript spec.
        If generator hasn't started, raises exception immediately.
        If generator is suspended, throws at yield point.

        Args:
            exception: Exception to throw into generator

        Returns:
            IteratorResult if exception is caught and generator continues

        Raises:
            Exception: The thrown exception if not caught, or StopIteration on completion
        """
        # If not started, raise immediately
        if self.state == GeneratorState.SUSPENDED_START:
            self.state = GeneratorState.COMPLETED
            raise exception

        # If already completed, raise immediately
        if self.state == GeneratorState.COMPLETED:
            raise exception

        try:
            # Update state
            self.state = GeneratorState.EXECUTING

            # Throw into generator
            if self._iterator is not None and hasattr(self._iterator, 'throw'):
                yielded_value = self._iterator.throw(exception)
                self.state = GeneratorState.SUSPENDED_YIELD
                return IteratorResult(value=yielded_value, done=False)
            else:
                # No throw method, just raise
                raise exception

        except StopIteration as e:
            # Generator completed
            self.state = GeneratorState.COMPLETED
            return_value = getattr(e, 'value', None)
            return IteratorResult(value=return_value, done=True)

        except Exception:
            # Unhandled exception, generator is completed
            self.state = GeneratorState.COMPLETED
            raise

    def __iter__(self):
        """
        Implement iterable protocol (Symbol.iterator).

        Generators are their own iterators per ECMAScript spec.

        Returns:
            self
        """
        return self

    def __next__(self):
        """
        Python iterator protocol support.

        Allows using Python's built-in iteration (for loops, etc).

        Returns:
            Next yielded value

        Raises:
            StopIteration: When generator completes
        """
        result = self.next()
        if result.done:
            if result.value is not None:
                raise StopIteration(result.value)
            raise StopIteration
        return result.value


class GeneratorFunction:
    """
    Wrapper for generator functions.

    Creates Generator objects when called. Represents function* declarations
    and expressions.

    The wrapped function should be a Python generator (uses yield).
    """

    def __init__(self, func: Callable):
        """
        Initialize generator function wrapper.

        Args:
            func: Python generator function (uses yield)
        """
        self.func = func

    def __call__(self) -> Generator:
        """
        Call generator function to create generator object.

        Returns:
            New Generator instance
        """
        return Generator(self.func)
