"""Macrotask implementation for Event Loop.

Macrotasks represent units of work like setTimeout, I/O operations, and user events.
They have lower priority than microtasks.
"""


class Task:
    """Represents a macrotask (setTimeout, I/O, user events).

    Macrotasks are lower-priority work units that execute after
    all pending microtasks have been processed.

    Attributes:
        callback: The function to execute when this task runs.
    """

    def __init__(self, callback):
        """Initialize a new macrotask.

        Args:
            callback: Callable to execute when task runs.
        """
        self.callback = callback

    def execute(self):
        """Execute the task callback.

        Returns:
            The return value of the callback function.

        Raises:
            Any exception raised by the callback.
        """
        return self.callback()
