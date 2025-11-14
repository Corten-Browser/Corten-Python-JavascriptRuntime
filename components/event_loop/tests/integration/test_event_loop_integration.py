"""Integration tests for Event Loop with complex scenarios."""

import pytest
from components.event_loop.src import EventLoop


class TestComplexScenarios:
    """Complex scenarios with interleaved tasks and microtasks."""

    def test_interleaved_tasks_and_microtasks(self):
        """Complex scenario with interleaved tasks."""
        loop = EventLoop()
        executed = []

        # Initial setup
        loop.queue_task(lambda: executed.append('T1'))
        loop.queue_microtask(lambda: executed.append('M1'))

        # Task T1 queues more work
        def task1():
            executed.append('T2')
            loop.queue_microtask(lambda: executed.append('M2'))

        loop.queue_task(task1)

        loop.run()

        # Expected: M1, T1, T2, M2
        # (M1 executes first, then T1, then T2, then M2 from T2)
        assert executed[0] == 'M1'
        assert 'T1' in executed
        assert 'T2' in executed
        assert 'M2' in executed

    def test_many_microtasks(self):
        """Handle many microtasks efficiently."""
        loop = EventLoop()
        executed = []

        for i in range(100):
            loop.queue_microtask(lambda idx=i: executed.append(idx))

        loop.run()

        assert len(executed) == 100
        assert executed == list(range(100))

    def test_macrotask_queues_microtask_during_execution(self):
        """Macrotask can queue microtasks that run before next macrotask."""
        loop = EventLoop()
        executed = []

        def macro1():
            executed.append('macro1')
            loop.queue_microtask(lambda: executed.append('micro_from_macro1'))

        def macro2():
            executed.append('macro2')

        loop.queue_task(macro1)
        loop.queue_task(macro2)
        loop.run()

        # Expected: macro1, micro_from_macro1, macro2
        assert executed == ['macro1', 'micro_from_macro1', 'macro2']

    def test_deeply_nested_microtask_chains(self):
        """Handle chains of microtasks spawning more microtasks."""
        loop = EventLoop()
        executed = []

        def create_chain(depth, current=0):
            """Create a chain of microtasks."""
            executed.append(f'micro_{current}')
            if current < depth:
                loop.queue_microtask(lambda: create_chain(depth, current + 1))

        loop.queue_microtask(lambda: create_chain(5))
        loop.queue_task(lambda: executed.append('macro_after_chain'))
        loop.run()

        # All microtasks (6 total: 0-5) should execute before macro
        assert executed[:6] == [f'micro_{i}' for i in range(6)]
        assert executed[-1] == 'macro_after_chain'

    def test_alternating_tasks_and_microtasks(self):
        """Test alternating pattern of tasks and microtasks."""
        loop = EventLoop()
        executed = []

        for i in range(5):
            loop.queue_task(lambda idx=i: executed.append(f'T{idx}'))
            loop.queue_microtask(lambda idx=i: executed.append(f'M{idx}'))

        loop.run()

        # All microtasks first, then all tasks
        microtasks = [x for x in executed if x.startswith('M')]
        tasks = [x for x in executed if x.startswith('T')]

        assert len(microtasks) == 5
        assert len(tasks) == 5
        # All microtasks come before any task
        assert executed.index('M0') < executed.index('T0')

    def test_empty_and_refill_loop(self):
        """Test loop that becomes empty and gets refilled."""
        loop = EventLoop()
        executed = []

        # First batch
        loop.queue_microtask(lambda: executed.append('batch1'))
        loop.run()

        # Loop should be stopped now
        assert loop.running is False
        assert executed == ['batch1']

        # Refill and run again
        loop.queue_microtask(lambda: executed.append('batch2'))
        loop.run()

        assert executed == ['batch1', 'batch2']

    def test_realistic_promise_simulation(self):
        """Simulate realistic Promise-like behavior."""
        loop = EventLoop()
        executed = []

        # Simulate: Promise.resolve().then(...).then(...)
        def promise_chain_start():
            executed.append('promise_start')
            loop.queue_microtask(promise_chain_then1)

        def promise_chain_then1():
            executed.append('then1')
            loop.queue_microtask(promise_chain_then2)

        def promise_chain_then2():
            executed.append('then2')

        # Simulate: setTimeout(() => {...})
        def timer_callback():
            executed.append('timeout')
            loop.queue_microtask(lambda: executed.append('micro_in_timeout'))

        # Queue initial work
        executed.append('sync1')
        loop.queue_microtask(promise_chain_start)
        executed.append('sync2')
        loop.queue_task(timer_callback)

        # Run event loop
        loop.run()

        # Expected order:
        # sync1, sync2 (synchronous, before loop)
        # promise_start, then1, then2 (microtasks)
        # timeout, micro_in_timeout (macrotask + its microtask)
        assert executed == [
            'sync1', 'sync2',
            'promise_start', 'then1', 'then2',
            'timeout', 'micro_in_timeout'
        ]
