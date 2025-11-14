"""Microtask implementation for Event Loop.

Microtasks represent high-priority work like Promise reactions and queueMicrotask().
They execute before macrotasks and all microtasks execute before the next macrotask.
"""


class Microtask:
    """Represents a microtask (Promise reactions, queueMicrotask).

    Microtasks are high-priority work units that execute before any macrotask.
    When a microtask executes, any new microtasks queued during its execution
    will also run before the next macrotask.

    Attributes:
        callback: The function to execute when this microtask runs.
    """

    def __init__(self, callback):
        """Initialize a new microtask.

        Args:
            callback: Callable to execute when microtask runs.
        """
        self.callback = callback

    def execute(self):
        """Execute the microtask callback.

        Returns:
            The return value of the callback function.

        Raises:
            Any exception raised by the callback.
        """
        return self.callback()
