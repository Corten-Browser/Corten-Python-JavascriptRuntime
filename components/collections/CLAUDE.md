# Component: collections

**Version:** 0.3.0  
**Type:** core  
**Dependencies:** symbols (Symbol.iterator), memory_gc (weak references)

## Contract
READ: `/home/user/Corten-JavascriptRuntime/contracts/collections.yaml`

## Requirements
FR-P3-036 to FR-P3-050 from `docs/phase3-requirements.md`

## Implement
1. **Map** (set, get, has, delete, clear, size, iterators)
2. **Set** (add, has, delete, clear, size, iterators)
3. **WeakMap** (set, get, has, delete - objects only, weak refs)
4. **WeakSet** (add, has, delete - objects only, weak refs)
5. **SameValueZero equality** (+0 === -0, NaN === NaN)
6. **Insertion order preservation**
7. **Hash table implementation** (separate chaining)
8. **Weak references** (ephemeron tables for GC)

## Files
- `src/map.py`, `src/set.py`, `src/weak_map.py`, `src/weak_set.py`
- `src/same_value_zero.py`, `src/hash_table.py`
- Tests: ≥80 unit, ≥15 integration

## Success: Map/Set work, insertion order preserved, WeakMap/WeakSet GC correctly, ≥90% coverage
