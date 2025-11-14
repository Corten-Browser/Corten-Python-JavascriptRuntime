"""Event Loop component for asynchronous task scheduling.

This component implements the JavaScript event loop model with proper
microtask and macrotask queue semantics. It provides the foundation
for Promise execution, setTimeout, and other asynchronous operations.

Public API:
    EventLoop: Main event loop coordinator
    Task: Macrotask representation
    Microtask: Microtask representation

Example:
    >>> from components.event_loop.src import EventLoop
    >>> loop = EventLoop()
    >>> loop.queue_microtask(lambda: print("High priority"))
    >>> loop.queue_task(lambda: print("Low priority"))
    >>> loop.run()
    High priority
    Low priority
"""

from .event_loop import EventLoop
from .task import Task
from .microtask import Microtask

__all__ = ['EventLoop', 'Task', 'Microtask']

__version__ = '0.1.0'
