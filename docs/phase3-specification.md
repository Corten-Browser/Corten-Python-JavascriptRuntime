# Phase 3: Advanced ECMAScript Features - Implementation Specification

**Version:** 0.3.0
**Target Compliance:** ECMAScript 2024 (ES15)
**Estimated Effort:** 80-120 hours
**Timeline:** 3-6 months

---

## Executive Summary

Phase 3 implements advanced ECMAScript features that are essential for modern JavaScript compatibility. This phase closes the 60% ES2024 feature gap identified in the compliance report, bringing the runtime from 40% to ~85% ES2024 compliance.

### Features to Implement

1. **Generators and Iterators** (FR-P3-001 to FR-P3-010)
2. **Symbols and Well-Known Symbols** (FR-P3-011 to FR-P3-020)
3. **Proxies and Reflect API** (FR-P3-021 to FR-P3-035)
4. **Collections** (Map, Set, WeakMap, WeakSet) (FR-P3-036 to FR-P3-050)
5. **TypedArrays and ArrayBuffer** (FR-P3-051 to FR-P3-070)
6. **BigInt** (FR-P3-071 to FR-P3-080)
7. **Timer APIs** (setTimeout, setInterval) (FR-P3-081 to FR-P3-090)

---

## 1. Generators and Iterators

### 1.1 Functional Requirements

**FR-P3-001: Generator Function Syntax**
- Support `function*` syntax for generator declarations
- Support `function*` for generator expressions
- Support generator methods in classes and objects

**FR-P3-002: Yield Expression**
- Implement `yield` expression for producing values
- Implement `yield*` for delegating to another generator/iterable
- Support bidirectional communication (next(value))

**FR-P3-003: Generator Object Protocol**
- Generator objects implement Iterator protocol
- Methods: next(), return(), throw()
- State management: suspended-start, suspended-yield, completed

**FR-P3-004: Iterator Protocol**
- Support Symbol.iterator well-known symbol
- Iterator objects with next() method
- Result objects: {value, done}

**FR-P3-005: Iterable Protocol**
- Objects implementing [Symbol.iterator]() are iterable
- for-of loop consumes iterables
- Spread operator works with iterables

**FR-P3-006: Built-in Iterables**
- Array, String, Map, Set are iterable
- Array.prototype.entries(), keys(), values() return iterators
- String iteration yields code points (not code units)

**FR-P3-007: Generator Completion**
- Early return via return() method
- Exception handling via throw() method
- Proper cleanup (try/finally in generators)

**FR-P3-008: Async Generators** (DEFERRED - requires async iterator protocol)
- Note: Defer to future phase if time-constrained

### 1.2 Implementation Details

**Bytecode Support:**
- `YIELD` opcode: Suspend generator, save state, return value
- `YIELD_STAR` opcode: Delegate to iterable
- `GENERATOR_CREATE` opcode: Create generator object
- Generator state storage: saved registers, instruction pointer

**Parser Changes:**
- Recognize `function*` syntax
- Parse `yield` expressions (only in generator context)
- Error on `yield` outside generator functions

**Runtime Support:**
- Generator objects (subclass of Iterator)
- Generator execution context (suspended state)
- Integration with event loop (generators don't create microtasks)

### 1.3 Test Requirements

- Generator creation and basic iteration (10+ tests)
- Yield and yield* delegation (5+ tests)
- Bidirectional communication (5+ tests)
- Error handling (throw/return) (5+ tests)
- for-of loop integration (5+ tests)
- Edge cases (empty generators, early return) (5+ tests)

**Test Coverage Target:** ≥90%

---

## 2. Symbols and Well-Known Symbols

### 2.1 Functional Requirements

**FR-P3-011: Symbol Primitive Type**
- New primitive type (7th type: undefined, null, boolean, number, string, symbol, object)
- Symbol() creates unique symbol
- Symbol.for(key) creates/retrieves global symbols
- Symbol.keyFor(symbol) retrieves key for global symbol

**FR-P3-012: Symbol Properties**
- Symbols can be object property keys
- Symbol properties non-enumerable by default
- Object.getOwnPropertySymbols() retrieves symbol properties
- Symbols survive JSON.stringify (omitted from output)

**FR-P3-013: Well-Known Symbols**
Implement these well-known symbols:
- `Symbol.iterator` - Default iterator method
- `Symbol.toStringTag` - Object.prototype.toString() customization
- `Symbol.hasInstance` - instanceof behavior customization
- `Symbol.toPrimitive` - Type conversion customization
- `Symbol.species` - Constructor for derived objects
- `Symbol.asyncIterator` - Async iterator (DEFERRED)
- `Symbol.match`, `Symbol.replace`, `Symbol.search`, `Symbol.split` - RegExp methods
- `Symbol.isConcatSpreadable` - Array.prototype.concat behavior
- `Symbol.unscopables` - with statement binding exclusion

**FR-P3-014: Symbol Coercion**
- Cannot be coerced to number (throw TypeError)
- Can be coerced to boolean (always true)
- String(symbol) returns "Symbol(description)"
- symbol.toString() returns "Symbol(description)"
- symbol.description property returns description string

**FR-P3-015: Symbol in Operations**
- typeof symbol === "symbol"
- Symbols never equal each other (except same reference)
- Symbol keys preserved in Object.assign()
- Symbol keys excluded from for-in, Object.keys(), JSON

### 2.2 Implementation Details

**Value System:**
- Add Symbol type to tagged pointer scheme
- Symbol internal structure: description (string or undefined), hash (unique ID)
- Global symbol registry (Map<string, Symbol>)

**Object Runtime:**
- Dual property storage: string keys + symbol keys
- Hidden class transitions for symbol properties
- Property enumeration excludes symbols

**Parser:**
- Recognize Symbol.iterator, Symbol.for, etc.
- No new syntax (Symbol is runtime API)

### 2.3 Test Requirements

- Symbol creation and uniqueness (5+ tests)
- Global symbol registry (3+ tests)
- Symbol as property keys (10+ tests)
- Well-known symbol behaviors (15+ tests per symbol)
- Type coercion and operations (5+ tests)

**Test Coverage Target:** ≥90%

---

## 3. Proxies and Reflect API

### 3.1 Functional Requirements

**FR-P3-021: Proxy Object Creation**
- new Proxy(target, handler)
- Target must be object (or function)
- Handler is object with traps

**FR-P3-022: Proxy Traps (13 traps)**

**Fundamental Traps:**
- `get(target, property, receiver)` - Property read
- `set(target, property, value, receiver)` - Property write
- `has(target, property)` - in operator
- `deleteProperty(target, property)` - delete operator

**Object Shape Traps:**
- `getOwnPropertyDescriptor(target, property)` - Property descriptor
- `defineProperty(target, property, descriptor)` - Define property
- `ownKeys(target)` - Object.keys(), for-in, etc.
- `getPrototypeOf(target)` - [[GetPrototypeOf]]
- `setPrototypeOf(target, prototype)` - [[SetPrototypeOf]]
- `isExtensible(target)` - Object.isExtensible()
- `preventExtensions(target)` - Object.preventExtensions()

**Function Traps:**
- `apply(target, thisArg, args)` - Function call
- `construct(target, args, newTarget)` - new operator

**FR-P3-023: Proxy Invariants**
Enforce proxy invariants per ECMAScript spec:
- Non-configurable property cannot be reported as non-existent
- Non-extensible target cannot report new properties
- Non-writable, non-configurable property cannot change value
- If target is non-extensible, cannot report more keys than target has

**FR-P3-024: Revocable Proxies**
- Proxy.revocable(target, handler) returns {proxy, revoke}
- Calling revoke() makes proxy throw TypeError on all operations

**FR-P3-025: Reflect API**
Mirror of proxy traps as static methods:
- Reflect.get(target, property, receiver)
- Reflect.set(target, property, value, receiver)
- Reflect.has(target, property)
- Reflect.deleteProperty(target, property)
- Reflect.getOwnPropertyDescriptor(target, property)
- Reflect.defineProperty(target, property, descriptor)
- Reflect.ownKeys(target)
- Reflect.getPrototypeOf(target)
- Reflect.setPrototypeOf(target, prototype)
- Reflect.isExtensible(target)
- Reflect.preventExtensions(target)
- Reflect.apply(target, thisArg, args)
- Reflect.construct(target, args, newTarget)

**FR-P3-026: Proxy-Aware Operations**
All object operations must check for proxies:
- Property access via get trap
- Property assignment via set trap
- Property deletion via deleteProperty trap
- Object.keys() via ownKeys trap

### 3.2 Implementation Details

**Object Runtime:**
- Proxy objects as special object type
- Handler storage and trap dispatch
- Invariant validation after trap execution
- Revocation state tracking

**Bytecode:**
- Proxy-aware property access opcodes
- Trap dispatch mechanism
- Fallback to default behavior if trap absent

**Performance:**
- Inline cache invalidation for proxies
- Proxy detection in hot paths
- Optimization: direct access if no relevant traps

### 3.3 Test Requirements

- Proxy creation and basic traps (10+ tests)
- All 13 traps individually (5+ tests each = 65+ tests)
- Proxy invariants enforcement (10+ tests)
- Revocable proxies (5+ tests)
- Reflect API (13 methods × 3 tests = 39+ tests)
- Edge cases (nested proxies, proxy of proxy) (10+ tests)

**Test Coverage Target:** ≥85%

---

## 4. Collections (Map, Set, WeakMap, WeakSet)

### 4.1 Functional Requirements

**FR-P3-036: Map**
- new Map(iterable) constructor
- map.set(key, value) - Add/update entry
- map.get(key) - Retrieve value
- map.has(key) - Check existence
- map.delete(key) - Remove entry
- map.clear() - Remove all entries
- map.size property
- map.keys(), map.values(), map.entries() - Iterators
- map.forEach(callback, thisArg) - Iteration
- Maps are iterable (yield [key, value])

**FR-P3-037: Map Key Equality**
- SameValueZero comparison (0 === -0, NaN === NaN)
- Object keys by reference equality
- Preserves insertion order

**FR-P3-038: Set**
- new Set(iterable) constructor
- set.add(value) - Add value
- set.has(value) - Check membership
- set.delete(value) - Remove value
- set.clear() - Remove all values
- set.size property
- set.keys(), set.values(), set.entries() - Iterators (keys=values for Sets)
- set.forEach(callback, thisArg) - Iteration
- Sets are iterable (yield value)

**FR-P3-039: Set Value Equality**
- SameValueZero comparison
- Preserves insertion order

**FR-P3-040: WeakMap**
- new WeakMap(iterable) constructor
- Keys must be objects (no primitives)
- weakMap.set(key, value)
- weakMap.get(key)
- weakMap.has(key)
- weakMap.delete(key)
- No size property
- No iteration methods
- Not enumerable

**FR-P3-041: WeakMap Garbage Collection**
- Weak references to keys
- If key becomes unreachable, entry removed automatically
- Enables object metadata without memory leaks

**FR-P3-042: WeakSet**
- new WeakSet(iterable) constructor
- Values must be objects
- weakSet.add(value)
- weakSet.has(value)
- weakSet.delete(value)
- No size, no iteration
- Weak references

### 4.2 Implementation Details

**Map/Set Data Structure:**
- Hash table with separate chaining
- SameValueZero equality implementation
- Insertion order preservation (linked list or index tracking)
- Efficient resize/rehash strategy

**WeakMap/WeakSet:**
- Weak reference support in GC
- Ephemeron tables (key reachability determines entry liveness)
- Integration with mark-and-sweep collector

**Memory Management:**
- Map/Set use strong references
- WeakMap/WeakSet use weak references
- GC cleans up unreachable weak entries

### 4.3 Test Requirements

- Map: create, set, get, has, delete, clear (10+ tests)
- Map: iteration and ordering (5+ tests)
- Map: key equality (5+ tests)
- Set: create, add, has, delete, clear (10+ tests)
- Set: iteration and ordering (5+ tests)
- WeakMap: basic operations (5+ tests)
- WeakMap: GC behavior (3+ tests - may be flaky)
- WeakSet: basic operations (5+ tests)
- WeakSet: GC behavior (3+ tests)

**Test Coverage Target:** ≥90%

---

## 5. TypedArrays and ArrayBuffer

### 5.1 Functional Requirements

**FR-P3-051: ArrayBuffer**
- new ArrayBuffer(length) - Allocate byte buffer
- arrayBuffer.byteLength property
- arrayBuffer.slice(begin, end) - Copy region
- ArrayBuffer.isView(value) - Check if TypedArray or DataView

**FR-P3-052: TypedArray Variants**
Implement all TypedArray types:
- Int8Array, Uint8Array, Uint8ClampedArray
- Int16Array, Uint16Array
- Int32Array, Uint32Array
- Float32Array, Float64Array
- BigInt64Array, BigUint64Array (requires BigInt)

**FR-P3-053: TypedArray Construction**
- new TypedArray(length)
- new TypedArray(typedArray)
- new TypedArray(arrayLike)
- new TypedArray(buffer, byteOffset, length)

**FR-P3-054: TypedArray Properties**
- typedArray.buffer - Underlying ArrayBuffer
- typedArray.byteLength - Length in bytes
- typedArray.byteOffset - Offset in buffer
- typedArray.length - Number of elements
- TypedArray.BYTES_PER_ELEMENT

**FR-P3-055: TypedArray Methods**
Array-like methods:
- Indexing: array[index], array[index] = value
- forEach, map, filter, reduce, reduceRight
- every, some, find, findIndex
- indexOf, lastIndexOf, includes
- slice, subarray
- sort, reverse
- set(array, offset), copyWithin

TypedArray-specific:
- TypedArray.from(source)
- TypedArray.of(...values)

**FR-P3-056: DataView**
- new DataView(buffer, byteOffset, byteLength)
- getInt8/setInt8, getUint8/setUint8
- getInt16/setInt16, getUint16/setUint16
- getInt32/setInt32, getUint32/setUint32
- getFloat32/setFloat32, getFloat64/setFloat64
- Endianness control (littleEndian parameter)

**FR-P3-057: ArrayBuffer Transfer/Detach** (ES2024)
- arrayBuffer.transfer(newByteLength) - Transfer with optional resize
- arrayBuffer.detached property
- Detached buffers throw on access

**FR-P3-058: Resizable ArrayBuffer** (ES2024)
- new ArrayBuffer(length, {maxByteLength})
- arrayBuffer.resize(newByteLength)
- arrayBuffer.resizable property

### 5.2 Implementation Details

**Memory Management:**
- Contiguous byte buffer allocation
- Alignment requirements for typed views
- Detachment mechanism (zero-out buffer, mark detached)

**Type Conversions:**
- Int8: wrap to -128..127
- Uint8: wrap to 0..255
- Uint8Clamped: clamp to 0..255
- Float32: round to single precision
- BigInt64/BigUint64: BigInt coercion

**Object Runtime:**
- TypedArray exotic objects (indexed properties)
- Shared prototype chain: TypedArray.prototype → Array.prototype
- Fast path for numeric indexing

### 5.3 Test Requirements

- ArrayBuffer: create, slice, detach (10+ tests)
- Each TypedArray type: create, access, methods (10+ tests × 10 types = 100+ tests)
- DataView: create, all getter/setter methods (20+ tests)
- Endianness handling (5+ tests)
- Resizable ArrayBuffer (5+ tests)
- Edge cases: detached buffers, out of bounds (10+ tests)

**Test Coverage Target:** ≥85%

---

## 6. BigInt

### 6.1 Functional Requirements

**FR-P3-071: BigInt Literals**
- Numeric literals with 'n' suffix: 123n, 0xFFn, 0o77n, 0b1010n
- Arbitrary precision integers

**FR-P3-072: BigInt Construction**
- BigInt(value) - Coerce to BigInt
- BigInt from string: BigInt("12345678901234567890")
- BigInt from number (must be integer, no fractional part)

**FR-P3-073: BigInt Arithmetic**
- Addition: a + b
- Subtraction: a - b
- Multiplication: a * b
- Division: a / b (truncates toward zero)
- Remainder: a % b
- Exponentiation: a ** b
- Unary minus: -a
- Unary plus: +a (TypeError - no coercion)

**FR-P3-074: BigInt Bitwise Operations**
- AND: a & b
- OR: a | b
- XOR: a ^ b
- NOT: ~a
- Left shift: a << b
- Signed right shift: a >> b
- Unsigned right shift: TypeError (no unsigned BigInt)

**FR-P3-075: BigInt Comparison**
- Equality: a === b, a !== b
- Relational: a < b, a <= b, a > b, a >= b
- BigInt compared to Number (use mathematical value, not ===)

**FR-P3-076: BigInt Restrictions**
- Cannot mix BigInt and Number in arithmetic (TypeError)
- Cannot use Math.* functions with BigInt (use BigInt equivalents)
- No implicit coercion to Number

**FR-P3-077: BigInt Methods**
- bigint.toString(radix) - Convert to string
- BigInt.asIntN(bits, bigint) - Wrap to N-bit signed
- BigInt.asUintN(bits, bigint) - Wrap to N-bit unsigned

**FR-P3-078: BigInt Type Checking**
- typeof bigint === "bigint"

### 6.2 Implementation Details

**Value System:**
- BigInt as heap-allocated arbitrary-precision integer
- Small BigInt optimization (fit in pointer if ≤ 64 bits)
- Tagged pointer scheme: BigInt tag

**Arithmetic:**
- GMP library or custom bignum implementation
- Efficient multiplication (Karatsuba, Toom-Cook for large numbers)
- Division algorithms

**Parser:**
- Recognize 'n' suffix on numeric literals
- Parse binary, octal, hex BigInt literals

**Bytecode:**
- BIGINT_ADD, BIGINT_SUB, BIGINT_MUL, BIGINT_DIV opcodes
- Type checks before mixed-type operations

### 6.3 Test Requirements

- BigInt literals (5+ tests)
- BigInt construction from various types (5+ tests)
- Arithmetic operations (10+ tests)
- Bitwise operations (10+ tests)
- Comparison operators (10+ tests)
- Type mixing errors (5+ tests)
- Edge cases: very large numbers, negative, zero (10+ tests)

**Test Coverage Target:** ≥90%

---

## 7. Timer APIs

### 7.1 Functional Requirements

**FR-P3-081: setTimeout**
- setTimeout(callback, delay, ...args)
- Returns timer ID (number)
- Minimum delay: 0ms (actual execution deferred to next event loop iteration)
- Nested timeout clamping: ≥4ms after 5 levels

**FR-P3-082: clearTimeout**
- clearTimeout(timerID)
- Cancel pending timeout
- No-op if timer already fired or invalid ID

**FR-P3-083: setInterval**
- setInterval(callback, delay, ...args)
- Returns interval ID (number)
- Repeats every delay milliseconds
- Same clamping rules as setTimeout

**FR-P3-084: clearInterval**
- clearInterval(intervalID)
- Stop repeating interval
- No-op if already cleared or invalid ID

**FR-P3-085: Timer Execution**
- Timers execute as macrotasks in event loop
- Callback receives scheduled time (not actual time)
- this binding: globalThis (or undefined in strict mode)

**FR-P3-086: Timer Ordering**
- Timers fire in order of expiration time
- Timers with same expiration fire in creation order

**FR-P3-087: Timer Arguments**
- Additional arguments passed to callback
- setTimeout(fn, delay, arg1, arg2) → fn(arg1, arg2)

### 7.2 Implementation Details

**Event Loop Integration:**
- Timer queue (priority queue by expiration time)
- Event loop checks timer queue each iteration
- Execute all expired timers before next task

**Timer Storage:**
- Map<timerID, TimerInfo>
- TimerInfo: {callback, args, expiration, repeat, interval}

**Timer ID Generation:**
- Incrementing counter (or random if security-sensitive)
- Avoid ID reuse for active timers

**Nested Timeout Clamping:**
- Track nesting level per timer chain
- If level ≥ 5, clamp delay to max(delay, 4ms)

### 7.3 Test Requirements

- setTimeout: basic execution (5+ tests)
- setTimeout: delay accuracy (3+ tests - may be flaky)
- setTimeout: argument passing (3+ tests)
- clearTimeout: cancellation (3+ tests)
- setInterval: repeated execution (5+ tests)
- clearInterval: stopping interval (3+ tests)
- Nested timeout clamping (3+ tests)
- Edge cases: zero delay, negative delay, very large delay (5+ tests)

**Test Coverage Target:** ≥85%

---

## Implementation Strategy

### Component Mapping

Phase 3 features will be implemented across these components:

1. **generators_iterators** (NEW)
   - Generator runtime
   - Iterator protocol
   - Yield bytecode execution

2. **symbols** (NEW)
   - Symbol value type
   - Well-known symbols
   - Global symbol registry

3. **proxies_reflect** (NEW)
   - Proxy object implementation
   - Trap dispatch
   - Reflect API
   - Invariant enforcement

4. **collections** (NEW)
   - Map and Set
   - WeakMap and WeakSet
   - Hash table implementation

5. **typed_arrays** (NEW)
   - ArrayBuffer
   - All TypedArray variants
   - DataView

6. **bigint** (NEW)
   - BigInt value type
   - Arbitrary-precision arithmetic
   - BigInt literals parsing

7. **timers** (EXTENDS event_loop)
   - Timer queue
   - setTimeout/setInterval/clear*
   - Event loop integration

### Modification to Existing Components

- **parser**: Add generator syntax, BigInt literals, Symbol.* recognition
- **bytecode**: Add YIELD, YIELD_STAR, BIGINT_* opcodes
- **interpreter**: Add bytecode handlers for new opcodes
- **value_system**: Add Symbol and BigInt types to tagged pointer scheme
- **object_runtime**: Add proxy-aware operations, symbol properties
- **event_loop**: Add timer queue and timer task execution
- **memory_gc**: Add weak reference support for WeakMap/WeakSet

---

## Dependencies

### Cross-Component Dependencies

```
generators_iterators → symbols (Symbol.iterator)
symbols → object_runtime (symbol properties)
proxies_reflect → object_runtime (trap dispatch)
collections → memory_gc (weak references)
typed_arrays → memory_gc (buffer allocation)
bigint → value_system (BigInt type)
timers → event_loop (timer queue)
```

### Build Order (Topological Sort)

1. **symbols** (base, no dependencies)
2. **bigint** (base, no dependencies)
3. **generators_iterators** (depends on symbols)
4. **proxies_reflect** (depends on object_runtime)
5. **collections** (depends on symbols, memory_gc)
6. **typed_arrays** (depends on memory_gc)
7. **timers** (depends on event_loop)

---

## Quality Standards

All components must meet:

- ✅ 100% test pass rate (unit + integration)
- ✅ ≥80% test coverage (target ≥85% for Phase 3)
- ✅ TDD compliance (git history shows Red-Green-Refactor)
- ✅ 12-check verification passing
- ✅ Contract compliance
- ✅ Zero security vulnerabilities
- ✅ Proper error handling (no uncaught exceptions)

---

## Success Criteria

Phase 3 is complete when:

1. ✅ All 90 functional requirements implemented (FR-P3-001 to FR-P3-090)
2. ✅ All 7 new components created and verified
3. ✅ All existing components updated and verified
4. ✅ 100% integration test pass rate
5. ✅ System-wide validation passing
6. ✅ ECMAScript 2024 compliance: 40% → ~85%
7. ✅ All components pass 12-check verification
8. ✅ No critical pre-integration analysis failures

**Estimated Impact:**
- ES2024 compliance: **40% → 85%** (+45 percentage points)
- Feature completeness: **~50% → ~85%** of planned features
- Real-world JavaScript compatibility: **moderate → high**

---

## Exclusions (Deferred to Future Phases)

- Async generators (requires async iterator protocol)
- Symbol.asyncIterator (async-specific)
- Advanced RegExp features with symbols (Symbol.match, etc.) - basic support only
- Performance optimizations (inline caching for proxies, etc.)

---

**Document Version:** 1.0
**Created:** 2025-11-15
**Status:** APPROVED - Ready for implementation
