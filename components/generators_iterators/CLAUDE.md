# Component: generators_iterators

**Version:** 0.3.0
**Type:** core
**Tech Stack:** Python
**Project Root:** /home/user/Corten-JavascriptRuntime

## Responsibility

Implement generator functions (`function*`), yield expressions, and iterator protocol per ECMAScript 2024.

## Contract

**READ FIRST:** `/home/user/Corten-JavascriptRuntime/contracts/generators_iterators.yaml`

## Requirements

Implement FR-P3-001 through FR-P3-010 from `/home/user/Corten-JavascriptRuntime/docs/phase3-requirements.md`

## Dependencies

**CRITICAL:** Depends on `symbols` component for Symbol.iterator

## Implementation Tasks

### 1. Generator Syntax (parser integration)

**File:** `components/generators_iterators/src/generator_parser.py`

- Parse `function*` syntax (declarations and expressions)
- Parse `yield` expression (only in generator context)
- Parse `yield*` delegation
- Error if `yield` outside generator

### 2. Generator Bytecode

**File:** `components/generators_iterators/src/generator_bytecode.py`

- `GENERATOR_CREATE` opcode: Create generator object
- `YIELD` opcode: Suspend and yield value
- `YIELD_STAR` opcode: Delegate to iterable
- `GENERATOR_RESUME` opcode: Resume from suspension

### 3. Generator Runtime

**File:** `components/generators_iterators/src/generator.py`

Generator object class:
- State: suspended-start | suspended-yield | executing | completed
- Methods: `next(value)`, `return(value)`, `throw(exception)`
- Implements Iterator protocol
- Implements Iterable protocol (has Symbol.iterator)

### 4. Iterator Protocol

**File:** `components/generators_iterators/src/iterator.py`

- Iterator interface: `{ next() → { value, done } }`
- Iterable interface: `{ [Symbol.iterator]() → Iterator }`
- IteratorResult: `{ value: any, done: boolean }`

### 5. Built-in Iterables

**File:** `components/generators_iterators/src/builtin_iterables.py`

Make these types iterable (integrate with existing components):
- Array.prototype[Symbol.iterator]
- String.prototype[Symbol.iterator] (code points)
- Map.prototype[Symbol.iterator] (when Map implemented)
- Set.prototype[Symbol.iterator] (when Set implemented)

### 6. for-of Loop

**File:** `components/generators_iterators/src/for_of.py`

- Implement for-of loop using Symbol.iterator
- Bytecode: FOR_OF_START, FOR_OF_NEXT, FOR_OF_CLOSE
- Proper cleanup (close iterator on break/exception)

### 7. Spread Operator for Iterables

**File:** `components/generators_iterators/src/spread.py`

- `[...iterable]` spreads iterable into array
- Uses Symbol.iterator protocol

### 8. Tests

**Required Coverage:** ≥90%

**Files:**
- `tests/unit/test_generator_creation.py` (≥10 tests)
- `tests/unit/test_yield.py` (≥10 tests)
- `tests/unit/test_yield_star.py` (≥5 tests)
- `tests/unit/test_generator_methods.py` (≥10 tests)
- `tests/unit/test_iterator_protocol.py` (≥5 tests)
- `tests/unit/test_for_of.py` (≥10 tests)
- `tests/unit/test_spread.py` (≥5 tests)
- `tests/integration/test_generator_integration.py` (≥15 tests)

## TDD Workflow

1. **RED:** Write tests for `function*` parsing
2. **GREEN:** Implement parser support for generators
3. **RED:** Write tests for simple `yield`
4. **GREEN:** Implement YIELD bytecode and generator state
5. **REFACTOR:** Optimize generator suspension/resumption
6. **RED:** Write tests for generator.next(value) bidirectional communication
7. **GREEN:** Implement value passing into generator
8. **RED:** Write tests for for-of loop
9. **GREEN:** Implement for-of using Symbol.iterator
10. **RED:** Write tests for yield* delegation
11. **GREEN:** Implement YIELD_STAR

## Success Criteria

- ✅ `function*` creates generator functions
- ✅ Generator functions return generator objects
- ✅ `yield` suspends execution and returns value
- ✅ `generator.next()` resumes execution
- ✅ `generator.next(value)` sends value into generator
- ✅ `generator.return(value)` completes generator early
- ✅ `generator.throw(error)` throws error into generator
- ✅ `yield*` delegates to another generator/iterable
- ✅ for-of loop works with iterables
- ✅ Spread operator works with iterables
- ✅ ≥90% test coverage
- ✅ All 12-check verification passing

## Integration Points

1. **symbols:** Use Symbol.iterator for protocol
2. **parser:** Parse function*, yield, yield*
3. **bytecode:** GENERATOR_CREATE, YIELD, YIELD_STAR opcodes
4. **interpreter:** Execute generator bytecode, manage state
5. **object_runtime:** Built-in types implement Symbol.iterator

**IMPORTANT:** Follow TDD. Generator state management is complex - test thoroughly!
