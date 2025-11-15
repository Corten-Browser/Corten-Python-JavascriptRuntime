# inline_caching Component

**Version:** 0.1.0
**Type:** Core
**Purpose:** Inline caching infrastructure for fast property access and call site optimization

## Overview

The inline_caching component provides high-performance inline caching for JavaScript runtime optimization. It implements monomorphic, polymorphic, and megamorphic inline caches for property access, function calls, and global variables.

### Key Features

- **IC State Machine**: UNINITIALIZED → MONOMORPHIC → POLYMORPHIC → MEGAMORPHIC
- **Property Load IC**: Fast property reads (obj.prop)
- **Property Store IC**: Fast property writes (obj.prop = value)
- **Call IC**: Function call site optimization
- **Global IC**: Global variable access optimization
- **Statistics Tracking**: Hit/miss rates and performance metrics

## Performance Targets

- **Cache Hit Rate**: >90% for monomorphic access
- **Cache Check Latency**: <10ns
- **Memory Overhead**: <100 bytes per IC
- **Monomorphic Speedup**: 5-10x vs hash table lookup
- **Polymorphic Speedup**: 2-5x vs hash table lookup

## Installation

This component is part of the Corten JavaScript Runtime. No separate installation required.

## Usage

### Property Load IC

```python
from components.inline_caching.src import PropertyLoadIC

ic = PropertyLoadIC()

# First access: slow path, initializes cache
value = ic.load(obj, "propertyName")

# Subsequent accesses: fast path (cache hit)
value = ic.load(obj, "propertyName")

# Check statistics
stats = ic.get_statistics()
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

### Property Store IC

```python
from components.inline_caching.src import PropertyStoreIC

ic = PropertyStoreIC()

# Store with caching
ic.store(obj, "propertyName", value)
```

### Call IC

```python
from components.inline_caching.src import CallIC

ic = CallIC()

# Call with caching
result = ic.call(function, [arg1, arg2])
```

### Global IC

```python
from components.inline_caching.src import GlobalIC

ic = GlobalIC()

# Store global
ic.store_global("globalVar", value)

# Load global (cached)
value = ic.load_global("globalVar")
```

## IC State Machine

```
UNINITIALIZED (no shapes cached)
     ↓
MONOMORPHIC (single shape, fastest)
     ↓
POLYMORPHIC (2-4 shapes, fast)
     ↓
MEGAMORPHIC (>4 shapes, fallback to slow path)
```

## Architecture

### Components

- **ic_state.py**: IC state enumeration
- **inline_cache.py**: Base IC class with state machine
- **property_ic.py**: PropertyLoadIC and PropertyStoreIC
- **call_ic.py**: CallIC for function calls
- **global_ic.py**: GlobalIC for globals

### Dependencies

- **object_runtime** (for JSObject integration)
- **value_system** (for tagged values)
- **hidden_classes** (for Shape integration, to be integrated)

## Development

### Running Tests

```bash
# All tests
pytest components/inline_caching/tests/unit/ -v

# With coverage
pytest components/inline_caching/tests/unit/ --cov=components/inline_caching/src --cov-report=html

# Single test file
pytest components/inline_caching/tests/unit/test_inline_cache.py -v
```

### Test Results

- **Total Tests**: 46
- **Coverage**: 91% (exceeds 85% target)
- **Pass Rate**: 100%

### Code Quality

- **TDD**: Red-Green-Refactor pattern followed
- **BDD**: Given-When-Then test structure
- **Linting**: PEP 8 compliant
- **Complexity**: All functions ≤10 cyclomatic complexity

## Requirements Implemented

All 10 Phase 4 requirements implemented:

- ✅ FR-P4-001: Monomorphic inline cache
- ✅ FR-P4-002: Polymorphic inline cache
- ✅ FR-P4-003: Megamorphic cache
- ✅ FR-P4-004: Property load IC
- ✅ FR-P4-005: Property store IC
- ✅ FR-P4-006: IC invalidation
- ✅ FR-P4-007: IC statistics and profiling
- ✅ FR-P4-008: Global variable IC
- ✅ FR-P4-009: Function call IC
- ✅ FR-P4-010: IC integration (ready for interpreter)

## Performance Characteristics

### Monomorphic IC (Single Shape)

- **Cache check**: O(1) - single comparison
- **Fast path**: O(1) - direct array access
- **Expected hit rate**: >95%

### Polymorphic IC (2-4 Shapes)

- **Cache check**: O(n) where n ≤ 4
- **Fast path**: O(1) after shape match
- **Expected hit rate**: >85%

### Megamorphic IC (>4 Shapes)

- **Always misses**: Falls back to hash table lookup
- **No caching overhead**: Minimal memory usage
- **Behavior**: Same as uncached access

## Integration Notes

### Placeholder Shape Class

Currently uses a placeholder Shape class (`_shape_placeholder.py`). This will be replaced with the real Shape implementation from the `hidden_classes` component once available.

### Future Enhancements

- Integration with real hidden classes
- IC feedback for JIT compilation
- Specialized ICs for arrays and functions
- IC chain optimization
- Deoptimization support

## License

Part of Corten JavaScript Runtime
Version: 0.1.0
Status: Pre-release
