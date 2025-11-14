# Event Loop Component

**Version**: 0.1.0
**Status**: ✅ Complete
**Phase**: 2.5.1 (Promises - Event Loop Foundation)

## Overview

The Event Loop component implements the JavaScript event loop model with proper microtask and macrotask queue semantics. This is the foundation for asynchronous operations including Promises, setTimeout, and other async features.

## Architecture

### Key Classes

- **`EventLoop`**: Main coordinator that manages task execution
- **`Task`**: Represents a macrotask (setTimeout, I/O, user events)
- **`Microtask`**: Represents a microtask (Promise reactions, queueMicrotask)

### Event Loop Algorithm

The event loop follows the JavaScript specification:

1. **Execute ALL pending microtasks** (including ones queued during execution)
2. **Execute ONE macrotask** (if available)
3. **Repeat** until both queues are empty

This ensures:
- ✅ Microtasks (Promise reactions) have priority over macrotasks
- ✅ All microtasks run before the next macrotask
- ✅ New microtasks queued during execution run in the same batch
- ✅ FIFO (First-In-First-Out) ordering within each queue

## Usage

### Basic Example

```python
from components.event_loop.src import EventLoop

# Create event loop
loop = EventLoop()

# Queue some work
loop.queue_microtask(lambda: print("Microtask 1"))
loop.queue_task(lambda: print("Macrotask 1"))
loop.queue_microtask(lambda: print("Microtask 2"))

# Run the loop
loop.run()

# Output:
# Microtask 1
# Microtask 2
# Macrotask 1
```

### Promise Simulation

```python
loop = EventLoop()

# Simulate: Promise.resolve().then(...).then(...)
def promise_start():
    print("Promise created")
    loop.queue_microtask(then_handler1)

def then_handler1():
    print("First then()")
    loop.queue_microtask(then_handler2)

def then_handler2():
    print("Second then()")

# Synchronous code
print("Start")
loop.queue_microtask(promise_start)
print("End")

# Run event loop
loop.run()

# Output:
# Start
# End
# Promise created
# First then()
# Second then()
```

### Stop Loop Early

```python
loop = EventLoop()

def stop_after_first():
    print("Executed first task")
    loop.stop()

loop.queue_microtask(stop_after_first)
loop.queue_microtask(lambda: print("Won't execute"))

loop.run()
# Output: Executed first task
```

## Testing

### Run Tests

```bash
# All tests
pytest components/event_loop/tests/ -v

# Unit tests only
pytest components/event_loop/tests/unit/ -v

# Integration tests only
pytest components/event_loop/tests/integration/ -v

# With coverage
pytest components/event_loop/tests/ --cov=components/event_loop/src --cov-report=term-missing
```

### Test Coverage

- **Total Tests**: 19 (12 unit + 7 integration)
- **Coverage**: 100% (43/43 statements)
- **Status**: ✅ All tests passing

#### Test Categories

**Unit Tests (12)**:
- Event loop creation and basic operations
- Single and multiple microtask/macrotask execution
- FIFO ordering guarantees
- Microtask priority over macrotasks
- Exception handling
- Loop stop functionality
- Loop reusability

**Integration Tests (7)**:
- Interleaved tasks and microtasks
- Many microtasks (100+) handling
- Macrotasks queuing microtasks
- Deeply nested microtask chains
- Alternating patterns
- Empty and refill scenarios
- Realistic Promise simulation

## API Reference

### EventLoop

#### `__init__()`
Initialize a new event loop with empty queues.

#### `run()`
Run the event loop until all queues are empty. Can be stopped early with `stop()`.

#### `queue_microtask(callback)`
Queue a high-priority microtask.
- **Parameters**: `callback` - Function to execute
- **Use for**: Promise reactions, queueMicrotask(), MutationObserver

#### `queue_task(callback)`
Queue a lower-priority macrotask.
- **Parameters**: `callback` - Function to execute
- **Use for**: setTimeout/setInterval, I/O, user events

#### `stop()`
Stop the event loop after the current task completes.

### Task

Represents a macrotask with lower execution priority.

#### `__init__(callback)`
Create a new macrotask.

#### `execute()`
Execute the task callback.

### Microtask

Represents a microtask with higher execution priority.

#### `__init__(callback)`
Create a new microtask.

#### `execute()`
Execute the microtask callback.

## Integration Points

This component will be integrated with:

- **`components/promise/`**: Promise implementation (Phase 2.5.2)
- **`components/runtime_cli/`**: REPL integration for async execution
- **Future components**: setTimeout, async/await, fetch, etc.

## Implementation Details

### Queue Semantics

- **Microtask Queue**: `collections.deque` for O(1) append/popleft
- **Macrotask Queue**: `collections.deque` for O(1) append/popleft

### Execution Order

```
Loop Iteration:
1. Process all microtasks (with newly queued ones)
   └─ If microtask queues another microtask, it runs in same batch
2. Process one macrotask
   └─ If macrotask queues microtasks, they run before next macrotask
3. Repeat until both queues empty
```

### Example Execution Flow

```python
loop.queue_task('T1')       # Macrotask queue: [T1]
loop.queue_microtask('M1')  # Microtask queue: [M1]
loop.queue_task('T2')       # Macrotask queue: [T1, T2]
loop.queue_microtask('M2')  # Microtask queue: [M1, M2]

loop.run()

# Execution order:
# 1. M1 (all microtasks first)
# 2. M2 (all microtasks first)
# 3. T1 (one macrotask)
# 4. T2 (one macrotask)
```

## Design Decisions

### Why Microtasks Execute Before Macrotasks

This follows the JavaScript specification to ensure:
- Promise handlers execute as soon as possible
- Microtasks don't starve (all execute before next macrotask)
- Predictable execution order for async code

### Why Only One Macrotask Per Iteration

This prevents long-running macrotask sequences from blocking the event loop. Each macrotask gets a chance to queue microtasks that execute before the next macrotask.

### Why Check `running` Flag in Microtask Loop

Allows `stop()` to halt the loop even during microtask batch processing, preventing infinite loops if microtasks keep queueing more microtasks.

## Next Steps

- **Phase 2.5.2**: Implement Promise class using this event loop
- **Phase 2.5.3**: Integrate Promise with bytecode compilation
- **Phase 2.5.4**: Add runtime APIs (Promise.all, Promise.race, etc.)
- **Phase 2.6**: Implement async/await on top of Promises

## References

- Architecture: `/docs/PROMISES-ARCHITECTURE.md`
- JavaScript Event Loop Spec: HTML Standard (WHATWG)
- Related Components: `components/promise/` (coming next)

---

**Implemented by**: Claude (Sonnet 4.5)
**Date**: 2025-11-14
**TDD**: ✅ Tests written first, 100% coverage
