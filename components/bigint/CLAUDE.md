# Component: bigint

**Version:** 0.3.0
**Type:** base
**Tech Stack:** Python
**Project Root:** /home/user/Corten-JavascriptRuntime

## Responsibility

Implement BigInt arbitrary-precision integers per ECMAScript 2024 specification.

## Contract

**READ FIRST:** `/home/user/Corten-JavascriptRuntime/contracts/bigint.yaml`

## Requirements

Implement FR-P3-071 through FR-P3-080 from `/home/user/Corten-JavascriptRuntime/docs/phase3-requirements.md`

## Implementation Tasks

### 1. BigInt Value Type

**File:** `components/bigint/src/bigint_value.py`

- BigInt internal representation (arbitrary precision integer)
- Small BigInt optimization (fit in pointer if ≤64 bits)
- BigInt(value) constructor function
- TypeError if used with `new`

### 2. BigInt Literals (parser integration)

**File:** `components/bigint/src/bigint_parser.py`

Parse BigInt literals:
- Decimal: `123n`
- Hexadecimal: `0xFFn`
- Octal: `0o77n`
- Binary: `0b1010n`

### 3. BigInt Arithmetic

**File:** `components/bigint/src/bigint_arithmetic.py`

Implement all arithmetic operations:
- Addition: `a + b`
- Subtraction: `a - b`
- Multiplication: `a * b`
- Division: `a / b` (truncates toward zero)
- Remainder: `a % b`
- Exponentiation: `a ** b`
- Unary minus: `-a`
- Unary plus: `+a` (TypeError)

Type mixing check: `BigInt + Number` → TypeError

### 4. BigInt Bitwise Operations

**File:** `components/bigint/src/bigint_bitwise.py`

- AND: `a & b`
- OR: `a | b`
- XOR: `a ^ b`
- NOT: `~a`
- Left shift: `a << b`
- Signed right shift: `a >> b`
- Unsigned right shift: `a >>> b` (TypeError - not supported)

### 5. BigInt Comparison

**File:** `components/bigint/src/bigint_comparison.py`

- Strict equality: `a === b` (value comparison)
- Abstract equality: `a == b` (mathematical value)
- Relational: `<`, `<=`, `>`, `>=`
- Cross-type comparison: `bigint < number` (compare mathematical values)

### 6. BigInt Methods

**File:** `components/bigint/src/bigint_methods.py`

- `toString(radix)`: Convert to string (default radix 10)
- `valueOf()`: Return BigInt primitive
- `BigInt.asIntN(bits, bigint)`: Wrap to N-bit signed
- `BigInt.asUintN(bits, bigint)`: Wrap to N-bit unsigned

### 7. Bytecode Integration

**File:** `components/bigint/src/bigint_bytecode.py`

- BIGINT_ADD, BIGINT_SUB, BIGINT_MUL, BIGINT_DIV, BIGINT_MOD opcodes
- BIGINT_AND, BIGINT_OR, BIGINT_XOR, BIGINT_NOT opcodes
- BIGINT_SHL, BIGINT_SHR opcodes
- Type check before mixed operations

### 8. Tests

**Required Coverage:** ≥90%

**Files:**
- `tests/unit/test_bigint_creation.py` (≥10 tests)
- `tests/unit/test_bigint_literals.py` (≥5 tests)
- `tests/unit/test_bigint_arithmetic.py` (≥15 tests)
- `tests/unit/test_bigint_bitwise.py` (≥10 tests)
- `tests/unit/test_bigint_comparison.py` (≥10 tests)
- `tests/unit/test_bigint_coercion.py` (≥5 tests)
- `tests/unit/test_bigint_edge_cases.py` (≥10 tests - very large numbers)
- `tests/integration/test_bigint_integration.py` (≥10 tests)

## Dependencies

**This component has NO dependencies - implement FIRST**

## TDD Workflow

1. **RED:** Write tests for BigInt(value) creation
2. **GREEN:** Implement BigInt value type
3. **REFACTOR:** Optimize small BigInt
4. **RED:** Write tests for arithmetic operations
5. **GREEN:** Implement arithmetic
6. **REFACTOR:** Use efficient algorithms (Karatsuba for large multiplications)
7. **RED:** Write tests for bitwise operations
8. **GREEN:** Implement bitwise
9. **RED:** Write tests for type mixing errors
10. **GREEN:** Add type checks, throw TypeError

## Success Criteria

- ✅ BigInt literals parse correctly
- ✅ All arithmetic operations work
- ✅ All bitwise operations work
- ✅ Comparison operators correct
- ✅ typeof bigint === "bigint"
- ✅ Type mixing throws TypeError
- ✅ Very large numbers (>2^64) work
- ✅ ≥90% test coverage
- ✅ 100% test pass rate
- ✅ All 12-check verification passing

## Integration Points

1. **value_system:** Add BigInt to tagged pointer scheme
2. **parser:** Parse BigInt literals (123n, 0xFFn, etc.)
3. **bytecode:** BIGINT_* opcodes
4. **interpreter:** Execute BigInt operations
5. **typed_arrays:** BigInt64Array, BigUint64Array (Phase 3)

## Implementation Notes

- Use Python's built-in arbitrary precision integers as backing
- Small optimization: BigInt ≤64 bits fits in tagged pointer
- For very large numbers, use heap-allocated bignum
- Division truncates toward zero (not floor division)
- No mixing with Number in arithmetic (strict separation)

**IMPORTANT:** Follow TDD strictly. Write tests first, then implement.
