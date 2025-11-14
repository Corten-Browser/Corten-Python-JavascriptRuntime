"""Event Loop implementation for JavaScript runtime.

The Event Loop coordinates execution of all asynchronous tasks, implementing
the JavaScript event loop model with proper microtask and macrotask queues.
"""

from collections import deque
from .task import Task
from .microtask import Microtask


class EventLoop:
    """JavaScript event loop with macrotask and microtask queues.

    The event loop follows the JavaScript specification:
    1. Execute one macrotask (if any)
    2. Execute ALL microtasks (including ones queued during execution)
    3. Repeat until both queues are empty

    This ensures:
    - Microtasks (Promise reactions) have priority over macrotasks
    - All microtasks run before the next macrotask
    - New microtasks queued during execution run in the same batch

    Attributes:
        macrotask_queue: FIFO queue for macrotasks (setTimeout, I/O, events)
        microtask_queue: FIFO queue for microtasks (Promise reactions)
        running: Boolean flag indicating if loop is currently running
    """

    def __init__(self):
        """Initialize a new event loop with empty queues."""
        self.macrotask_queue = deque()
        self.microtask_queue = deque()
        self.running = False

    def run(self):
        """Run event loop until all queues are empty.

        The event loop will:
        1. Process ALL pending microtasks (including newly queued ones)
        2. Process one macrotask (if available)
        3. Repeat until both queues are empty

        The loop can be stopped early by calling stop().
        After completion, the loop can be reused by calling run() again.
        """
        self.running = True

        while self.running and (self.macrotask_queue or self.microtask_queue):
            # Step 1: Execute ALL microtasks FIRST
            # This includes any microtasks queued during microtask execution
            while self.running and self.microtask_queue:
                microtask = self.microtask_queue.popleft()
                microtask.execute()

            # Step 2: Execute one macrotask (if any)
            if self.running and self.macrotask_queue:
                task = self.macrotask_queue.popleft()
                task.execute()

            # Step 3: Check if more work exists
            if not self.macrotask_queue and not self.microtask_queue:
                break

        self.running = False

    def queue_microtask(self, callback):
        """Queue a microtask (higher priority).

        Microtasks execute before macrotasks and all microtasks in the queue
        (including ones added during execution) run before the next macrotask.

        Use for:
        - Promise reactions (then/catch/finally handlers)
        - queueMicrotask() calls
        - MutationObserver callbacks

        Args:
            callback: Function to execute as a microtask
        """
        microtask = Microtask(callback)
        self.microtask_queue.append(microtask)

    def queue_task(self, callback):
        """Queue a macrotask (lower priority).

        Macrotasks execute after all pending microtasks have been processed.
        Only one macrotask executes per loop iteration.

        Use for:
        - setTimeout/setInterval callbacks
        - I/O operations
        - User interaction events
        - Script execution

        Args:
            callback: Function to execute as a macrotask
        """
        task = Task(callback)
        self.macrotask_queue.append(task)

    def stop(self):
        """Stop the event loop.

        The loop will stop after completing the current task/microtask.
        Any remaining queued tasks will not execute.
        """
        self.running = False
