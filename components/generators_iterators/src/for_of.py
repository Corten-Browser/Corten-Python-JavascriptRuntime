"""
for-of loop implementation for JavaScript runtime.

Implements for-of iteration using Symbol.iterator protocol per ECMAScript spec.

Public API:
    - execute_for_of_loop: Execute for-of loop over iterable
    - ForOfLoopContext: Context manager for for-of loops
"""

from typing import Any, Callable
from components.generators_iterators.src.iterator import get_iterator, is_iterable
from components.generators_iterators.src.generator import IteratorResult


class ForOfLoopContext:
    """
    Context manager for for-of loop execution.

    Manages iterator lifecycle, including proper cleanup on break/exception.
    """

    def __init__(self, iterable: Any):
        """
        Initialize for-of loop context.

        Args:
            iterable: Object to iterate over

        Raises:
            TypeError: If object is not iterable
        """
        if not is_iterable(iterable):
            raise TypeError(f"{type(iterable).__name__} is not iterable")

        self.iterable = iterable
        self.iterator = None

    def __enter__(self):
        """
        Enter context: get iterator.

        Returns:
            Iterator instance
        """
        self.iterator = get_iterator(self.iterable)
        return self.iterator

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: close iterator if it has return() method.

        Args:
            exc_type: Exception type (if any)
            exc_val: Exception value (if any)
            exc_tb: Exception traceback (if any)

        Returns:
            False to propagate exceptions
        """
        # Close iterator if it has return() method
        if self.iterator is not None and hasattr(self.iterator, 'return_value'):
            try:
                self.iterator.return_value()
            except Exception:
                pass  # Ignore errors during cleanup

        return False  # Don't suppress exceptions


def execute_for_of_loop(iterable: Any, body: Callable[[Any], None]) -> None:
    """
    Execute for-of loop over iterable.

    Implements for-of loop semantics:
    - Get iterator from iterable using Symbol.iterator
    - Call next() repeatedly until done: true
    - Execute body function for each value
    - Properly close iterator on break/exception

    Args:
        iterable: Object to iterate over
        body: Function to call for each value

    Raises:
        TypeError: If object is not iterable
        Exception: Any exception raised by body function
    """
    with ForOfLoopContext(iterable) as iterator:
        while True:
            try:
                # Get next value
                if hasattr(iterator, 'next'):
                    # Custom iterator with next() method
                    result = iterator.next()
                    if result.done:
                        break
                    value = result.value
                else:
                    # Python iterator
                    value = next(iterator)

                # Execute loop body
                body(value)

            except StopIteration:
                # Iterator exhausted
                break


def for_of_to_array(iterable: Any) -> list:
    """
    Collect all values from iterable into array.

    Helper for spread operator and array destructuring.

    Args:
        iterable: Iterable to collect values from

    Returns:
        List of all values from iterable

    Raises:
        TypeError: If object is not iterable
    """
    result = []
    execute_for_of_loop(iterable, lambda x: result.append(x))
    return result
