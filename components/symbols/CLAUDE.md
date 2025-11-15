# Component: symbols

**Version:** 0.3.0
**Type:** base
**Tech Stack:** Python
**Project Root:** /home/user/Corten-JavascriptRuntime

## Responsibility

Implement Symbol primitive type and well-known symbols per ECMAScript 2024 specification.

## Contract

**READ FIRST:** `/home/user/Corten-JavascriptRuntime/contracts/symbols.yaml`

## Requirements

Implement FR-P3-011 through FR-P3-020 from `/home/user/Corten-JavascriptRuntime/docs/phase3-requirements.md`

## Implementation Tasks

### 1. Symbol Value Type (value_system integration)

**File:** `components/symbols/src/symbol_value.py`

- Add Symbol to tagged pointer scheme
- Symbol internal structure: `{ description: string | None, id: unique_int }`
- Global symbol registry: `Map<string, Symbol>`
- Symbol() function (not constructor - TypeError if used with new)
- Symbol.for(key) / Symbol.keyFor(symbol)

### 2. Well-Known Symbols

**File:** `components/symbols/src/well_known_symbols.py`

Create all well-known symbols as module-level constants:
- Symbol.iterator
- Symbol.toStringTag
- Symbol.hasInstance
- Symbol.toPrimitive
- Symbol.species
- Symbol.isConcatSpreadable
- Symbol.unscopables
- Symbol.match, Symbol.replace, Symbol.search, Symbol.split

### 3. Symbol Operations

**File:** `components/symbols/src/symbol_ops.py`

- `typeof symbol` → "symbol"
- Symbol equality (reference equality only)
- Symbol coercion:
  - To number: TypeError
  - To string: String(symbol) → "Symbol(description)"
  - To boolean: always true
- Symbol.prototype.toString()
- Symbol.prototype.valueOf()
- Symbol.prototype.description getter

### 4. Integration with object_runtime

**File:** `components/symbols/src/symbol_properties.py`

- Symbols as property keys (separate storage from string keys)
- Object.getOwnPropertySymbols()
- Symbol properties non-enumerable by default
- Exclude symbols from for-in, Object.keys(), JSON.stringify

### 5. Tests

**Required Coverage:** ≥90%

**Files:**
- `tests/unit/test_symbol_creation.py` (≥10 tests)
- `tests/unit/test_symbol_registry.py` (≥5 tests)
- `tests/unit/test_symbol_properties.py` (≥15 tests)
- `tests/unit/test_well_known_symbols.py` (≥15 tests)
- `tests/unit/test_symbol_coercion.py` (≥5 tests)
- `tests/integration/test_symbol_integration.py` (≥10 tests)

## Dependencies

**This component has NO dependencies - implement FIRST**

## TDD Workflow

1. **RED:** Write failing tests for Symbol() creation
2. **GREEN:** Implement Symbol value type
3. **REFACTOR:** Optimize tagged pointer integration
4. **RED:** Write failing tests for well-known symbols
5. **GREEN:** Implement well-known symbols
6. **REFACTOR:** Ensure all symbols are unique
7. **RED:** Write tests for symbol as property keys
8. **GREEN:** Integrate with object_runtime
9. **REFACTOR:** Optimize property lookup

## Success Criteria

- ✅ Symbol() creates unique symbols
- ✅ Symbol.for/keyFor global registry works
- ✅ All 11 well-known symbols accessible
- ✅ Symbols work as property keys
- ✅ typeof symbol === "symbol"
- ✅ Type coercion follows spec (TypeError for number)
- ✅ ≥90% test coverage
- ✅ 100% test pass rate
- ✅ All 12-check verification passing

## Integration Points

1. **value_system:** Add Symbol to tagged pointer scheme
2. **object_runtime:** Support symbol property keys
3. **parser:** Recognize Symbol.* references
4. **bytecode:** LOAD_SYMBOL opcode for well-known symbols

## Notes

- Symbols are primitives, not objects (typeof "symbol")
- Each Symbol() call creates a unique symbol
- Global registry (Symbol.for) allows symbol reuse by key
- Symbol properties are excluded from normal enumeration
- Well-known symbols enable protocol customization (e.g., Symbol.iterator)

**IMPORTANT:** Follow TDD strictly. Write tests first, then implement. Commit after each Red-Green-Refactor cycle.
