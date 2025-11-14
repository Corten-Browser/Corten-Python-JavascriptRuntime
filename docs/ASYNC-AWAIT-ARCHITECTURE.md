# Async/Await Architecture Design

**Date:** 2025-11-14
**Version:** 1.0
**Status:** Design Phase
**Depends On:** Phase 2.5 (Promises)

---

## Overview

This document outlines the architectural design for implementing JavaScript async/await in the Corten JavaScript Runtime. Async/await provides syntactic sugar over Promises, making asynchronous code look and behave more like synchronous code.

---

## Current State

**Implemented:**
- ✅ Promises (Phase 2.5)
- ✅ Event loop with microtask queue
- ✅ Promise.resolve/reject
- ✅ Promise.then/catch/finally

**Not Implemented:**
- ❌ Async functions
- ❌ Await expressions
- ❌ Coroutine suspension/resumption

---

## Target State

**Goal:** Enable JavaScript code like this to work:

```javascript
async function fetchUser(id) {
    const response = await fetch(id);
    const user = await response.json();
    return user;
}

const user = await fetchUser(42);
console.log(user);

// Arrow functions
const getUser = async (id) => {
    return await Promise.resolve({ id, name: "Alice" });
};

// Error handling
async function safeOp() {
    try {
        await Promise.reject("error");
    } catch (err) {
        console.log("Caught:", err);
    }
}
```

---

## Design Approach: State Machine Transformation

### Why State Machine (Not Generator-Based)?

**Options considered:**

1. **Generator-based desugaring** (Babel approach):
   - Transform `async function` → generator function
   - Transform `await expr` → `yield expr`
   - Pros: Simpler if generators exist
   - ❌ Cons: We haven't implemented generators yet

2. **State machine transformation** (V8 approach):
   - Compile async function to explicit state machine
   - Each await point = state transition
   - ✅ Pros: More efficient, no generator dependency, fits our bytecode model
   - Cons: Complex bytecode transformation

3. **CPS transformation**:
   - Rewrite function in continuation-passing style
   - ❌ Cons: Complex compilation, stack explosion risk

**Decision:** State machine transformation (V8 style)

---

## Architecture Components

### 1. Parser Changes

**Add Tokens:**
```python
class TokenType(Enum):
    ASYNC = auto()
    AWAIT = auto()
```

**Add Keywords:**
```python
KEYWORDS = {
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
}
```

**Add AST Nodes:**
```python
@dataclass
class AsyncFunctionDeclaration:
    """async function name(params) { body }"""
    id: Identifier
    params: List[Identifier]
    body: BlockStatement

@dataclass
class AsyncFunctionExpression:
    """async function(params) { body }"""
    id: Optional[Identifier]
    params: List[Identifier]
    body: BlockStatement

@dataclass
class AsyncArrowFunctionExpression:
    """async (params) => body"""
    params: List[Identifier]
    body: Any  # Expression or BlockStatement

@dataclass
class AwaitExpression:
    """await expression"""
    argument: Any  # Expression to await
```

**Parsing Logic:**
```python
def _parse_function_declaration(self):
    is_async = self._match(TokenType.ASYNC)
    self._consume(TokenType.FUNCTION)
    # ... parse name, params, body ...

    if is_async:
        return AsyncFunctionDeclaration(id, params, body)
    else:
        return FunctionDeclaration(id, params, body)

def _parse_arrow_function(self):
    is_async = self.previous_token.type == TokenType.ASYNC
    # ... parse params, body ...

    if is_async:
        return AsyncArrowFunctionExpression(params, body)
    else:
        return ArrowFunctionExpression(params, body)

def _parse_unary_expression(self):
    if self._match(TokenType.AWAIT):
        argument = self._parse_unary_expression()
        return AwaitExpression(argument)
    # ... rest of unary parsing ...
```

---

### 2. Bytecode Transformation

**Key Insight:** Async function transforms to:
1. A Promise-returning wrapper
2. State machine that can suspend at await points
3. Continuation management for resumption

**Example Transformation:**

**Input JavaScript:**
```javascript
async function foo(x) {
    const a = await Promise.resolve(1);
    const b = await Promise.resolve(2);
    return a + b + x;
}
```

**Conceptual State Machine:**
```javascript
function foo(x) {
    return new Promise((resolve, reject) => {
        let state = 0;
        let a, b;

        function resume(value) {
            try {
                switch (state) {
                    case 0:  // Initial
                        state = 1;
                        Promise.resolve(1).then(resume, reject);
                        return;

                    case 1:  // After first await
                        a = value;
                        state = 2;
                        Promise.resolve(2).then(resume, reject);
                        return;

                    case 2:  // After second await
                        b = value;
                        resolve(a + b + x);
                        return;
                }
            } catch (e) {
                reject(e);
            }
        }

        resume();  // Start state machine
    });
}
```

**Bytecode Opcodes Needed:**

```python
class Opcode(Enum):
    # Existing opcodes...

    # Async/Await opcodes
    CREATE_ASYNC_FUNCTION = auto()  # Create async function (returns Promise)
    AWAIT = auto()                   # Suspend at await point
    RESUME = auto()                  # Resume from await
    SET_STATE = auto()               # Set state machine state
```

**Compilation Strategy:**

For each async function:
1. Identify all await expressions
2. Number them sequentially (states)
3. Generate state machine bytecode:
   - State 0: Function entry
   - State N: After Nth await
   - Final state: Return value

**Compiler Method:**
```python
def _compile_async_function(self, node: AsyncFunctionDeclaration):
    # Find all await expressions
    await_points = self._find_await_expressions(node.body)
    num_states = len(await_points) + 1

    # Create state machine bytecode
    state_machine_bytecode = BytecodeArray()

    # State 0: Entry point
    state_machine_bytecode.add_instruction(
        Instruction(opcode=Opcode.SET_STATE, operand1=0)
    )

    # Compile body with state transitions at each await
    for i, stmt in enumerate(node.body.body):
        if has_await(stmt):
            # Compile expression before await
            self._compile_expression_before_await(stmt)

            # AWAIT opcode suspends execution
            state_machine_bytecode.add_instruction(
                Instruction(opcode=Opcode.AWAIT)
            )

            # After resumption, we're in next state
            state_machine_bytecode.add_instruction(
                Instruction(opcode=Opcode.SET_STATE, operand1=i+1)
            )
        else:
            self._compile_statement(stmt)

    # Wrap in Promise executor
    self.bytecode.add_instruction(
        Instruction(
            opcode=Opcode.CREATE_ASYNC_FUNCTION,
            operand2=state_machine_bytecode
        )
    )
```

---

### 3. Interpreter Execution

**AsyncFunctionState Class:**
```python
@dataclass
class AsyncFunctionState:
    """State for suspended async function."""
    state: int  # Current state number
    locals: Dict[str, Value]  # Local variables
    bytecode: BytecodeArray  # Function bytecode
    promise: JSPromise  # Promise to resolve
```

**Interpreter Changes:**

```python
class Interpreter:
    def __init__(self, gc, event_loop=None):
        self.gc = gc
        self.event_loop = event_loop or EventLoop()
        self.suspended_async_functions = {}  # Track suspended functions
        # ... rest of init ...

    def execute(self, bytecode, *args):
        # ... existing execute code ...

        elif opcode == Opcode.CREATE_ASYNC_FUNCTION:
            # Create async function that returns Promise
            state_machine_bytecode = instruction.operand2

            def async_function(*args):
                # Create Promise
                promise = JSPromise(
                    lambda resolve, reject: self._start_async_function(
                        state_machine_bytecode, args, resolve, reject
                    ),
                    self.event_loop
                )
                return promise

            frame.push(Value.from_object(async_function))

        elif opcode == Opcode.AWAIT:
            # Suspend execution, wait for Promise
            awaited_value = frame.pop()

            if isinstance(awaited_value, JSPromise):
                promise = awaited_value
            else:
                # Wrap in Promise
                promise = JSPromise.resolve(awaited_value, self.event_loop)

            # Save current state
            state = AsyncFunctionState(
                state=frame.locals.get('__state__', 0),
                locals=frame.locals.copy(),
                bytecode=bytecode,
                promise=current_async_promise
            )

            # Register continuation
            promise.then(
                lambda value: self._resume_async_function(state, value),
                lambda err: self._reject_async_function(state, err)
            )

            # Suspend (return from execute)
            return EvaluationResult(value=Value.from_undefined())

        elif opcode == Opcode.SET_STATE:
            state_num = instruction.operand1
            frame.locals['__state__'] = state_num

    def _start_async_function(self, bytecode, args, resolve, reject):
        """Start async function execution."""
        # Create execution context
        # Start at state 0
        # Run until first await or completion
        pass

    def _resume_async_function(self, state: AsyncFunctionState, value):
        """Resume async function after await resolves."""
        # Restore state
        # Push awaited value onto stack
        # Continue execution from next instruction
        # Run until next await or completion
        pass

    def _reject_async_function(self, state: AsyncFunctionState, error):
        """Handle async function error."""
        # Reject the function's Promise
        state.promise._reject(error)
```

---

### 4. Example Execution Flow

**JavaScript:**
```javascript
async function test() {
    const x = await Promise.resolve(10);
    const y = await Promise.resolve(20);
    return x + y;
}

test().then(result => console.log(result));
```

**Execution Steps:**

1. **Call `test()`**:
   - CREATE_ASYNC_FUNCTION creates wrapper
   - Wrapper creates Promise
   - Returns Promise immediately

2. **State 0 (Initial)**:
   - SET_STATE 0
   - LOAD_GLOBAL "Promise"
   - LOAD_PROPERTY "resolve"
   - LOAD_CONSTANT 10
   - CALL_FUNCTION (returns Promise)
   - **AWAIT** - Suspends here

3. **Promise.resolve(10) fulfills**:
   - Event loop runs microtask
   - Calls resume continuation
   - Pushes value 10 onto stack

4. **State 1 (After first await)**:
   - SET_STATE 1
   - Store 10 in local "x"
   - LOAD_GLOBAL "Promise"
   - LOAD_PROPERTY "resolve"
   - LOAD_CONSTANT 20
   - CALL_FUNCTION
   - **AWAIT** - Suspends again

5. **Promise.resolve(20) fulfills**:
   - Event loop runs microtask
   - Calls resume continuation
   - Pushes value 20 onto stack

6. **State 2 (After second await)**:
   - SET_STATE 2
   - Store 20 in local "y"
   - LOAD_LOCAL "x" (10)
   - LOAD_LOCAL "y" (20)
   - ADD (30)
   - **RETURN** - Resolves outer Promise with 30

7. **`.then()` handler executes**:
   - Event loop runs microtask
   - `console.log(30)`

---

## Implementation Phases

### Phase 2.6.1: Parser Support (3-4 hours)
- Add ASYNC and AWAIT tokens
- Add async function AST nodes
- Add await expression AST node
- Parse async functions (declaration, expression, arrow)
- Parse await expressions
- Unit tests for parser

### Phase 2.6.2: Simple Async Functions (4-5 hours)
- Compile async functions without await (just return Promise)
- CREATE_ASYNC_FUNCTION opcode
- Interpreter support for async functions
- Tests for async functions without await

### Phase 2.6.3: Await Expression Support (5-6 hours)
- AWAIT opcode
- State machine transformation in compiler
- Suspension/resumption in interpreter
- AsyncFunctionState management
- Tests for single await

### Phase 2.6.4: Multiple Awaits (2-3 hours)
- State transitions for multiple awaits
- Local variable preservation across states
- Tests for multiple awaits in sequence

### Phase 2.6.5: Error Handling (2-3 hours)
- Try/catch with async/await
- Promise rejection handling
- Error propagation
- Tests for error scenarios

**Total Estimated:** 16-21 hours

---

## Testing Strategy

### Unit Tests

**Parser:**
- async function declaration
- async function expression
- async arrow function
- await expression
- async function with multiple awaits

**Bytecode:**
- Async function compilation
- State machine generation
- Await opcode generation

**Interpreter:**
- Async function execution
- await suspension
- await resumption
- Multiple awaits
- Error handling

### Integration Tests

**End-to-End:**
```javascript
// Test 1: Simple async function
async function simple() {
    return 42;
}

// Test 2: Single await
async function singleAwait() {
    const x = await Promise.resolve(10);
    return x * 2;
}

// Test 3: Multiple awaits
async function multipleAwaits() {
    const a = await Promise.resolve(1);
    const b = await Promise.resolve(2);
    return a + b;
}

// Test 4: Error handling
async function errorHandling() {
    try {
        await Promise.reject("error");
    } catch (err) {
        return "caught";
    }
}

// Test 5: Chaining
async function chain() {
    return await Promise.resolve(10);
}
chain().then(x => console.log(x));
```

---

## Success Criteria

- [ ] async function declarations work
- [ ] async function expressions work
- [ ] async arrow functions work
- [ ] await expressions suspend execution
- [ ] await expressions resume with value
- [ ] Multiple awaits in sequence work
- [ ] Error handling with try/catch works
- [ ] Async functions return Promises
- [ ] Integration with existing Promise system
- [ ] 50+ tests passing
- [ ] No breaking changes to existing features

---

## Future Work (Phase 3+)

- **Top-level await:** In ES modules
- **for await...of:** Async iteration
- **Async generators:** Combined async + generator
- **AsyncFunction constructor:** `new AsyncFunction(...)`

---

**Document Status:** Ready for implementation
**Next Step:** Begin Phase 2.6.1 (Parser Support)
