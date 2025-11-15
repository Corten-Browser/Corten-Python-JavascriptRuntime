# Component: typed_arrays

**Version:** 0.3.0  
**Type:** core  
**Dependencies:** memory_gc, symbols, bigint (for BigInt64Array)

## Contract
READ: `/home/user/Corten-JavascriptRuntime/contracts/typed_arrays.yaml`

## Requirements
FR-P3-051 to FR-P3-070 from `docs/phase3-requirements.md`

## Implement
1. **ArrayBuffer** (allocate, slice, transfer, detach)
2. **11 TypedArray types** (Int8Array, Uint8Array, Uint8ClampedArray, Int16Array, Uint16Array, Int32Array, Uint32Array, Float32Array, Float64Array, BigInt64Array, BigUint64Array)
3. **DataView** (all getter/setter methods with endianness)
4. **TypedArray methods** (map, filter, slice, set, etc.)
5. **Type conversions** (wrapping, clamping, precision)
6. **Resizable ArrayBuffer** (ES2024)

## Files
- `src/array_buffer.py`, `src/typed_array.py`, `src/data_view.py`
- `src/type_conversions.py`
- Tests: ≥150 unit, ≥20 integration

## Success: All 11 types work, DataView endianness correct, detached buffers throw, ≥85% coverage
