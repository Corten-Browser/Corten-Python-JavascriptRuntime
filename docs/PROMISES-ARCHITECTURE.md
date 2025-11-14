# Promises Architecture Design

**Date:** 2025-11-14
**Version:** 1.0
**Status:** Design Phase

---

## Overview

This document outlines the architectural design for implementing JavaScript Promises in the Corten JavaScript Runtime. Promises require fundamental changes to the execution model, introducing asynchronous task scheduling via an event loop and microtask queue.

---

## Current State

**Execution Model:** Synchronous only
- Parser → Bytecode → Interpreter executes linearly
- No task scheduling
- No concept of "later" execution
- Functions run to completion immediately

---

## Target State

**Execution Model:** Asynchronous-capable
- Event loop coordinates task execution
- Microtask queue for Promise reactions
- Macrotask queue for timers (future: setTimeout/setInterval)
- Functions can suspend and resume (Phase 2.6: async/await)

---

## Architectural Components

### 1. Event Loop

**Location:** `components/event_loop/`

**Responsibility:** Coordinate execution of all tasks

**Key Classes:**
- `EventLoop` - Main coordinator
- `Task` - Represents unit of work (macrotask)
- `Microtask` - Represents Promise reaction

**Algorithm:**
```python
class EventLoop:
    def __init__(self):
        self.macrotask_queue = deque()  # setTimeout, I/O, user events
        self.microtask_queue = deque()  # Promise reactions
        self.running = False

    def run(self):
        """Run until all queues empty."""
        self.running = True

        while self.running and (self.macrotask_queue or self.microtask_queue):
            # Step 1: Execute one macrotask (if any)
            if self.macrotask_queue:
                task = self.macrotask_queue.popleft()
                task.execute()

            # Step 2: Execute ALL microtasks
            while self.microtask_queue:
                microtask = self.microtask_queue.popleft()
                microtask.execute()

            # Step 3: Check if more work
            if not self.macrotask_queue and not self.microtask_queue:
                break

        self.running = False

    def queue_microtask(self, callback):
        """Queue a Promise reaction."""
        microtask = Microtask(callback)
        self.microtask_queue.append(microtask)

    def queue_task(self, callback):
        """Queue a macrotask (setTimeout, I/O)."""
        task = Task(callback)
        self.macrotask_queue.append(task)
```

**Integration Point:**
`components/runtime_cli/src/repl.py` and `Execute()` function

---

### 2. Microtask Queue

**Location:** Part of `EventLoop`

**Responsibility:** Execute Promise reactions with priority

**Key Properties:**
- FIFO (First-In-First-Out)
- Higher priority than macrotasks
- ALL microtasks execute before next macrotask
- New microtasks queued during execution run in same batch

**Example:**
```javascript
Promise.resolve().then(() => {
    console.log('Microtask 1');
    Promise.resolve().then(() => console.log('Microtask 2'));
});
console.log('Synchronous');

// Output:
// Synchronous
// Microtask 1
// Microtask 2
```

---

### 3. Promise Implementation

**Location:** `components/promise/`

**Key Classes:**

#### `JSPromise` - Core Promise object
```python
class JSPromise(JSObject):
    """JavaScript Promise implementation."""

    def __init__(self, executor_function, event_loop):
        super().__init__()
        self.state = PromiseState.PENDING  # PENDING, FULFILLED, REJECTED
        self.value = None  # Fulfillment value or rejection reason
        self.fulfillment_reactions = []  # .then() handlers
        self.rejection_reactions = []    # .catch() handlers
        self.event_loop = event_loop

        # Execute executor immediately
        try:
            resolve = self._create_resolve_function()
            reject = self._create_reject_function()
            executor_function(resolve, reject)
        except Exception as e:
            self._reject(e)

    def _create_resolve_function(self):
        """Create resolve() function passed to executor."""
        def resolve(value):
            if self.state != PromiseState.PENDING:
                return  # Promise already settled

            # Handle Promise resolution
            if isinstance(value, JSPromise):
                # If value is Promise, adopt its state
                value.then(resolve, self._reject)
            else:
                self._fulfill(value)

        return resolve

    def _create_reject_function(self):
        """Create reject() function passed to executor."""
        def reject(reason):
            if self.state != PromiseState.PENDING:
                return  # Promise already settled
            self._reject(reason)

        return reject

    def _fulfill(self, value):
        """Transition to FULFILLED state."""
        self.state = PromiseState.FULFILLED
        self.value = value

        # Queue all fulfillment reactions as microtasks
        for reaction in self.fulfillment_reactions:
            self.event_loop.queue_microtask(lambda: reaction(value))

        # Clear reactions
        self.fulfillment_reactions = []
        self.rejection_reactions = []

    def _reject(self, reason):
        """Transition to REJECTED state."""
        self.state = PromiseState.REJECTED
        self.value = reason

        # Queue all rejection reactions as microtasks
        for reaction in self.rejection_reactions:
            self.event_loop.queue_microtask(lambda: reaction(reason))

        # Clear reactions
        self.fulfillment_reactions = []
        self.rejection_reactions = []

    def then(self, on_fulfilled=None, on_rejected=None):
        """Register fulfillment/rejection handlers."""
        # Create new Promise for chaining
        result_promise = JSPromise(lambda resolve, reject: None, self.event_loop)

        def handle_fulfillment(value):
            try:
                if on_fulfilled:
                    new_value = on_fulfilled(value)
                    result_promise._resolve(new_value)
                else:
                    result_promise._fulfill(value)
            except Exception as e:
                result_promise._reject(e)

        def handle_rejection(reason):
            try:
                if on_rejected:
                    new_value = on_rejected(reason)
                    result_promise._resolve(new_value)
                else:
                    result_promise._reject(reason)
            except Exception as e:
                result_promise._reject(e)

        if self.state == PromiseState.PENDING:
            # Promise not settled yet, register reactions
            self.fulfillment_reactions.append(handle_fulfillment)
            self.rejection_reactions.append(handle_rejection)
        elif self.state == PromiseState.FULFILLED:
            # Promise already fulfilled, queue reaction as microtask
            self.event_loop.queue_microtask(lambda: handle_fulfillment(self.value))
        else:  # REJECTED
            # Promise already rejected, queue reaction as microtask
            self.event_loop.queue_microtask(lambda: handle_rejection(self.value))

        return result_promise

    def catch(self, on_rejected):
        """Shorthand for .then(None, on_rejected)."""
        return self.then(None, on_rejected)

    def finally_handler(self, on_finally):
        """Run callback regardless of fulfillment or rejection."""
        def handler(value):
            on_finally()
            return value

        return self.then(handler, handler)
```

#### `PromiseState` - Enum for Promise states
```python
from enum import Enum, auto

class PromiseState(Enum):
    PENDING = auto()
    FULFILLED = auto()
    REJECTED = auto()
```

---

### 4. Promise Static Methods

**Implementation:**
```python
class PromiseConstructor:
    """Promise constructor with static methods."""

    @staticmethod
    def resolve(value, event_loop):
        """Create immediately fulfilled Promise."""
        if isinstance(value, JSPromise):
            return value  # Already a Promise

        return JSPromise(lambda resolve, reject: resolve(value), event_loop)

    @staticmethod
    def reject(reason, event_loop):
        """Create immediately rejected Promise."""
        return JSPromise(lambda resolve, reject: reject(reason), event_loop)

    @staticmethod
    def all(promises, event_loop):
        """Fulfill when all Promises fulfill, reject if any rejects."""
        results = [None] * len(promises)
        remaining = len(promises)

        def on_fulfill(index, value):
            nonlocal remaining
            results[index] = value
            remaining -= 1
            if remaining == 0:
                resolve(results)

        def on_reject(reason):
            reject(reason)

        result_promise = JSPromise(lambda res, rej: None, event_loop)
        resolve = result_promise._create_resolve_function()
        reject = result_promise._create_reject_function()

        if len(promises) == 0:
            resolve([])
            return result_promise

        for i, promise in enumerate(promises):
            promise.then(
                lambda value, idx=i: on_fulfill(idx, value),
                on_reject
            )

        return result_promise

    @staticmethod
    def race(promises, event_loop):
        """Settle when first Promise settles."""
        result_promise = JSPromise(lambda res, rej: None, event_loop)
        resolve = result_promise._create_resolve_function()
        reject = result_promise._create_reject_function()

        for promise in promises:
            promise.then(resolve, reject)

        return result_promise

    @staticmethod
    def any(promises, event_loop):
        """Fulfill when first Promise fulfills, reject if all reject."""
        errors = []
        remaining = len(promises)

        def on_reject(reason):
            nonlocal remaining
            errors.append(reason)
            remaining -= 1
            if remaining == 0:
                reject(AggregateError(errors))

        result_promise = JSPromise(lambda res, rej: None, event_loop)
        resolve = result_promise._create_resolve_function()
        reject = result_promise._create_reject_function()

        if len(promises) == 0:
            reject(AggregateError([]))
            return result_promise

        for promise in promises:
            promise.then(resolve, on_reject)

        return result_promise

    @staticmethod
    def allSettled(promises, event_loop):
        """Wait for all Promises to settle (fulfill or reject)."""
        results = [None] * len(promises)
        remaining = len(promises)

        def on_settle(index, status, value):
            nonlocal remaining
            results[index] = {"status": status, "value": value}
            remaining -= 1
            if remaining == 0:
                resolve(results)

        result_promise = JSPromise(lambda res, rej: None, event_loop)
        resolve = result_promise._create_resolve_function()

        if len(promises) == 0:
            resolve([])
            return result_promise

        for i, promise in enumerate(promises):
            promise.then(
                lambda value, idx=i: on_settle(idx, "fulfilled", value),
                lambda reason, idx=i: on_settle(idx, "rejected", reason)
            )

        return result_promise
```

---

## Integration with Existing Components

### Parser Changes

**Add tokens:**
- `new` keyword (for `new Promise()`)

**Add AST nodes:**
- `NewExpression` - for `new Promise(...)`

**Example:**
```javascript
new Promise((resolve, reject) => {
    resolve(42);
})
```

Parser creates:
```python
NewExpression(
    callee=Identifier(name="Promise"),
    arguments=[
        ArrowFunctionExpression(
            params=[Identifier("resolve"), Identifier("reject")],
            body=BlockStatement(...)
        )
    ]
)
```

---

### Bytecode Changes

**Add opcodes:**
- `CREATE_PROMISE` - Create new Promise object
- `QUEUE_MICROTASK` - Queue microtask to event loop

**Example bytecode:**
```
// new Promise((resolve, reject) => { resolve(42); })

LOAD_GLOBAL "Promise"           // Load Promise constructor
LOAD_CONSTANT 0                 // Arrow function bytecode
CREATE_CLOSURE 0, <bytecode>    // Create executor function
CREATE_PROMISE                  // new Promise(executor)
```

---

### Interpreter Changes

**Add global object:**
```python
# In interpreter initialization
globals['Promise'] = PromiseConstructor
```

**Modify Execute() function:**
```python
def Execute(bytecode, gc=None):
    """Execute bytecode with event loop support."""
    gc = gc or GarbageCollector()
    event_loop = EventLoop()

    # Create interpreter with event loop
    interpreter = Interpreter(gc, event_loop)

    # Execute main script (synchronous code)
    result = interpreter.execute(bytecode)

    # Run event loop to process any Promises
    event_loop.run()

    return result
```

**Handle opcodes:**
```python
elif opcode == Opcode.CREATE_PROMISE:
    executor = frame.pop()  # Function with (resolve, reject) params
    promise = JSPromise(executor, self.event_loop)
    frame.push(Value.from_object(promise))

elif opcode == Opcode.QUEUE_MICROTASK:
    callback = frame.pop()
    self.event_loop.queue_microtask(callback)
```

---

## Testing Strategy

### Unit Tests

**Event Loop:**
- Empty loop exits immediately
- Single microtask executes
- Multiple microtasks execute in order
- Microtasks have priority over macrotasks
- New microtasks queued during execution run in same batch

**Promise:**
- Constructor executes executor immediately
- resolve() fulfills Promise
- reject() rejects Promise
- State transitions are irreversible
- .then() registers reactions
- .catch() is shorthand for .then(null, onReject)
- .finally() runs regardless of outcome

**Promise Chaining:**
- Chained .then() creates new Promise
- Return value passes to next .then()
- Exceptions caught by next .catch()
- Returning Promise flattens chain

**Promise Static Methods:**
- Promise.resolve() creates fulfilled Promise
- Promise.reject() creates rejected Promise
- Promise.all() waits for all
- Promise.race() settles with first
- Promise.any() fulfills with first fulfillment
- Promise.allSettled() waits for all settlements

### Integration Tests

**End-to-End:**
```javascript
// Test: Promise chain
new Promise((resolve) => resolve(1))
    .then(x => x + 1)
    .then(x => x * 2)
    .then(x => console.log(x))  // Should print 4

// Test: Error handling
new Promise((resolve, reject) => reject("error"))
    .catch(err => console.log("Caught:", err))

// Test: Promise.all
Promise.all([
    Promise.resolve(1),
    Promise.resolve(2),
    Promise.resolve(3)
]).then(values => console.log(values))  // [1, 2, 3]
```

---

## Implementation Phases

### Phase 2.5.1: Event Loop Foundation (4-6 hours)
- Create `components/event_loop/` component
- Implement `EventLoop` class
- Implement `Task` and `Microtask` classes
- Unit tests for event loop
- Integration with `Execute()` function

### Phase 2.5.2: Promise Core (6-8 hours)
- Create `components/promise/` component
- Implement `JSPromise` class
- Implement Promise constructor
- Implement state transitions
- Implement .then()/.catch()/.finally()
- Unit tests for Promise

### Phase 2.5.3: Promise Chaining (2-3 hours)
- Implement Promise chaining logic
- Handle return values
- Handle returned Promises (flattening)
- Exception propagation
- Tests for chaining

### Phase 2.5.4: Static Methods (3-4 hours)
- Implement Promise.resolve/reject
- Implement Promise.all
- Implement Promise.race
- Implement Promise.any
- Implement Promise.allSettled
- Tests for each method

### Phase 2.5.5: Integration (2-3 hours)
- Parser: NEW keyword and NewExpression
- Bytecode: CREATE_PROMISE opcode
- Interpreter: Opcode handling
- Global Promise object
- End-to-end integration tests

**Total Estimated:** 17-24 hours

---

## Success Criteria

- [ ] Event loop runs to completion
- [ ] Microtasks execute with priority
- [ ] Promise constructor works
- [ ] Promise state machine correct
- [ ] .then()/.catch()/.finally() work
- [ ] Promise chaining works
- [ ] All static methods work
- [ ] 100+ tests passing
- [ ] Integration with existing runtime
- [ ] No breaking changes to Phase 1-2 features

---

## Future Work (Phase 2.6+)

- **Async/Await:** Requires this Promise implementation as foundation
- **Timers:** setTimeout/setInterval use macrotask queue
- **Fetch API:** Uses Promises for async I/O
- **Top-Level Await:** In ES modules (Phase 2.7)

---

**Document Status:** Ready for implementation
**Next Step:** Create `components/event_loop/` and begin Phase 2.5.1
