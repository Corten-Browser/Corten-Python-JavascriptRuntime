# generational_gc

**Type**: Core Component
**Version**: 0.1.0
**Tech Stack**: Python 3.11+, performance profiling with time.perf_counter

## Overview

High-performance generational garbage collector implementing a two-generation collection strategy (young/old) for improved throughput and reduced pause times compared to traditional mark-sweep collection.

## Responsibility

Provides efficient memory management through:
- Fast allocation in young generation (nursery)
- Frequent minor GC for short-lived objects
- Infrequent major GC for long-lived objects
- Write barriers and remembered sets for cross-generational references
- Large object space for objects >64KB
- Adaptive triggering heuristics

## Architecture

### Generational Hypothesis

The generational GC is based on the observation that most objects die young:
- **Young Generation (Nursery)**: Fast bump-pointer allocation, frequent collection
- **Old Generation (Tenured Space)**: Slower free-list allocation, infrequent collection
- **Large Object Space**: Separate space for objects >64KB

### Collection Strategy

**Minor GC (Scavenge)**:
- Triggered when young generation is full
- Copy live objects from young gen (semi-space copying)
- Promote objects that survive N collections to old gen
- Very fast (<5ms for 8MB)

**Major GC (Mark-Sweep)**:
- Triggered when old generation is >75% full
- Mark-sweep collection of old generation
- Slower but infrequent (<50ms for 64MB)

### Write Barriers

When an old generation object references a young generation object, the write barrier records this in the remembered set. This allows minor GC to trace these cross-generational pointers without scanning the entire old generation.

## Structure

```
components/generational_gc/
├── src/
│   ├── __init__.py                # Public API exports
│   ├── generational_gc.py         # Main GC coordinator
│   ├── young_generation.py        # Nursery space
│   ├── old_generation.py          # Tenured space
│   ├── write_barrier.py           # Cross-gen pointer tracking
│   ├── remembered_set.py          # Old→young pointer set
│   ├── large_object_space.py      # Large objects (>64KB)
│   └── gc_stats.py                # Statistics tracking
├── tests/
│   ├── unit/
│   │   ├── test_young_generation.py
│   │   ├── test_old_generation.py
│   │   ├── test_write_barrier.py
│   │   ├── test_remembered_set.py
│   │   ├── test_large_object_space.py
│   │   └── test_generational_gc.py
│   └── integration/
│       └── test_gc_integration.py
├── component.yaml              # Component metadata
├── CLAUDE.md                   # Development instructions
└── README.md                   # This file
```

## Usage

### Basic Usage

```python
from components.generational_gc import GenerationalGC

# Create generational GC (8MB young gen, 64MB old gen)
gc = GenerationalGC()

# Allocate objects (allocated in young generation)
obj1 = gc.allocate(100)
obj2 = gc.allocate(200)

# Add roots
gc.add_root(obj1)

# Automatic GC triggers when young gen is full
# Or manually trigger:
minor_stats = gc.minor_gc()  # Scavenge young generation
major_stats = gc.major_gc()  # Full collection

# Access statistics
stats = gc.get_stats()
print(f"Minor GCs: {stats.minor_collections}")
print(f"Major GCs: {stats.major_collections}")
print(f"Pause time: {stats.pause_time_ms}ms")
print(f"Throughput: {stats.throughput_percent}%")
```

### Custom Configuration

```python
# Custom generation sizes
gc = GenerationalGC(
    young_size=16 * 1024 * 1024,  # 16MB young gen
    old_size=128 * 1024 * 1024     # 128MB old gen
)

# Configure promotion threshold
gc.set_promotion_age(3)  # Promote after 3 minor GCs

# Manual trigger control
if gc.should_trigger_minor_gc():
    gc.minor_gc()
```

## Performance Characteristics

### Time Complexity
- **Allocation**: O(1) - bump-pointer in young gen
- **Minor GC**: O(live objects in young gen) - typically very fast
- **Major GC**: O(total live objects) - slower but infrequent

### Space Overhead
- Write barriers: O(cross-generational pointers)
- Remembered set: typically small (<1% of heap)
- Semi-space copying: 2x young generation size

### Performance Targets
- Minor GC pause: <5ms for 8MB young gen
- Major GC pause: <50ms for 64MB old gen
- Throughput improvement: 2-5x over mark-sweep
- Survival rate: <10% in young generation

## Testing

### Run Unit Tests
```bash
pytest tests/unit/ -v
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Run with Coverage
```bash
pytest tests/ --cov=src --cov-report=html --cov-fail-under=85
```

### Performance Benchmarks
```bash
python benchmarks/gc_performance.py
```

## Development

See [CLAUDE.md](CLAUDE.md) for detailed development instructions, quality standards, and TDD requirements.

## Dependencies

- **memory_gc**: Base GC infrastructure (HeapObject, GarbageCollector)
- **value_system**: Tagged value representation
- **object_runtime**: JavaScript object runtime

## Integration

The generational GC integrates with the existing runtime through:
- Allocation interface compatible with memory_gc
- Root scanning from interpreter stack and globals
- Object reference tracking from object_runtime
- Value system integration for type information

## References

- Phase 4 Implementation Plan: `/PHASE4-IMPLEMENTATION-PLAN.md`
- API Contract: `/contracts/generational_gc.yaml`
- Requirements: FR-P4-056 through FR-P4-067

---

**Status**: Implementation in progress
**Test Coverage**: Target ≥85%
**Requirements**: 12/12 identified
