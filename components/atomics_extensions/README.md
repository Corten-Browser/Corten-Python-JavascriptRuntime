# Atomics Extensions

**Version:** 0.1.0
**Type:** feature
**Tech Stack:** Python 3.11+, threading, Promise integration

## Overview

ES2024 Atomics.waitAsync and SharedArrayBuffer integration for concurrent programming. Provides asynchronous waiting on shared memory locations with promise-based notification.

## Contract

READ: `/home/user/Corten-JavascriptRuntime/contracts/atomics_extensions.yaml`

## Features

### Atomics.waitAsync()
- Asynchronous wait on shared memory locations
- Promise-based notification mechanism
- Timeout support with <10ms notification latency
- Support for 1000+ concurrent waiters

### SharedArrayBuffer Integration
- Create shared buffers for concurrent access
- Identify SharedArrayBuffer instances
- Integration with TypedArray views

## Requirements

- **FR-ES24-009**: Atomics.waitAsync() implementation
- **FR-ES24-010**: SharedArrayBuffer integration

## Usage

### Basic Wait and Notify

```python
from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration
from components.typed_arrays.src.typed_array import Int32Array
from components.event_loop.src import EventLoop

# Create shared buffer
sab = SharedArrayBufferIntegration()
buffer = sab.create_shared_buffer(64)
int32_array = Int32Array(buffer)
int32_array[0] = 0

# Create event loop
loop = EventLoop()

# Wait asynchronously
atomics = AtomicsExtensions()
result = atomics.wait_async(int32_array, 0, 0, event_loop=loop)

if result.async_status:
    # Async wait - use promise
    result.promise.then(lambda v: print(f"Notified: {v}"))

    # In another thread/context: notify
    count = atomics.notify(int32_array, 0, 1)
    print(f"Woke {count} waiters")

    # Process event loop
    loop.run()
else:
    # Immediate return
    print(f"Status: {result.value}")  # "not-equal"
```

### With Timeout

```python
# Wait with 1000ms timeout
result = atomics.wait_async(
    int32_array,
    0,
    0,
    timeout=1000,
    event_loop=loop
)

result.promise.then(lambda v: print(f"Result: {v}"))  # "ok" or "timed-out"
```

### Multiple Waiters

```python
# Create multiple waiters
results = []
for i in range(10):
    result = atomics.wait_async(int32_array, 0, 0, event_loop=loop)
    result.promise.then(lambda v: print(f"Waiter {i}: {v}"))
    results.append(result)

# Notify some waiters
count = atomics.notify(int32_array, 0, 3)  # Wake 3 waiters

# Notify all remaining
count = atomics.notify(int32_array, 0, float('inf'))  # Wake all
```

## Architecture

### Components

- **AtomicsExtensions**: Main API for wait_async and notify operations
- **SharedArrayBufferIntegration**: SharedArrayBuffer creation and identification
- **AtomicsWaitAsyncResult**: Result data structure
- **Waiter**: Internal waiter queue management

### Threading Model

- Thread-safe waiter queue with locking
- Timeout handling with threading.Timer
- Promise resolution via event loop microtasks
- FIFO waiter notification order

### Performance

- Notification latency: <10ms for large waiter counts
- Concurrent waiters: Tested with 1000+ waiters
- Memory efficient waiter queue with cleanup

## Testing

### Unit Tests (23 tests)

```bash
cd /home/user/Corten-JavascriptRuntime/components/atomics_extensions
pytest tests/unit/ -v
```

### Integration Tests (7 tests)

```bash
pytest tests/integration/ -v
```

### Coverage

```bash
pytest tests/ --cov=src --cov-report=html --cov-fail-under=80
```

## API Reference

### AtomicsExtensions

#### wait_async(typed_array, index, value, timeout=None, event_loop=None)

Asynchronously wait on shared memory location.

**Parameters:**
- `typed_array` (Int32Array): Shared integer array
- `index` (int): Index to wait on
- `value` (int): Expected value
- `timeout` (float, optional): Timeout in milliseconds
- `event_loop` (EventLoop): Event loop for promise scheduling

**Returns:** `AtomicsWaitAsyncResult`

**Raises:**
- `TypeError`: If not SharedArrayBuffer
- `RangeError`: If index out of bounds

#### notify(typed_array, index, count)

Notify waiters on shared memory location.

**Parameters:**
- `typed_array` (Int32Array): Shared integer array
- `index` (int): Index to notify
- `count` (int): Number of waiters to wake (or float('inf') for all)

**Returns:** `int` - Number of waiters notified

### SharedArrayBufferIntegration

#### create_shared_buffer(byte_length)

Create SharedArrayBuffer for concurrent access.

**Parameters:**
- `byte_length` (int): Buffer size in bytes

**Returns:** `ArrayBuffer` (marked as shared)

**Raises:**
- `RangeError`: If byte_length < 0

#### is_shared_array_buffer(buffer)

Check if buffer is SharedArrayBuffer.

**Parameters:**
- `buffer` (Any): Buffer to check

**Returns:** `bool`

### AtomicsWaitAsyncResult

Result object from wait_async.

**Attributes:**
- `async_status` (bool): True if async, False if immediate
- `value` (str): "ok", "not-equal", or "timed-out"
- `promise` (JSPromise or None): Promise for async waits

## Development

### Run Tests

```bash
pytest tests/ -v
```

### Check Coverage

```bash
pytest tests/ --cov=src --cov-report=term-missing
```

### Linting

```bash
pylint src/ tests/
```

### Formatting

```bash
black .
```

## Success Criteria

- ✅ All 30+ tests passing (100% pass rate)
- ✅ Test coverage ≥80%
- ✅ Wait notification latency <10ms
- ✅ Support for 1000+ concurrent waiters
- ✅ Promise integration with event loop
- ✅ Timeout handling
- ✅ SharedArrayBuffer validation
- ✅ Thread-safe waiter queue

## Dependencies

- `components.promise` (JSPromise)
- `components.typed_arrays` (Int32Array, ArrayBuffer)
- `components.event_loop` (EventLoop)
- `threading` (standard library)
- `time` (standard library)
