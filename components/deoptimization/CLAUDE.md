# Deoptimization Component - Agent Instructions

**Component:** deoptimization
**Type:** Feature
**Version:** 0.1.0
**Project Root:** /home/user/Corten-JavascriptRuntime

## Your Mission

Implement safe fallback from optimized JIT code to interpreter when speculation fails. You are responsible for frame reconstruction, state materialization, and deoptimization profiling.

## Mandatory Operating Rules

1. **Work ONLY in** `components/deoptimization/` directory
2. **DO NOT access** other component directories (components/*/)
3. **Follow TDD strictly**: Red-Green-Refactor
4. **Test coverage**: ≥85%
5. **Git commits**: Show Red-Green-Refactor pattern

## Requirements (8 Total)

- FR-P4-068: Deoptimization metadata generation
- FR-P4-069: Frame reconstruction (JIT → interpreter)
- FR-P4-070: Deopt triggers (failed guards, type mismatches)
- FR-P4-071: Lazy deoptimization
- FR-P4-072: Eager deoptimization
- FR-P4-073: Deopt bailout points
- FR-P4-074: State materialization (recreate interpreter state)
- FR-P4-075: Deopt statistics and profiling

## Implementation Tasks

### Phase 1: Core Data Structures (RED)
**Tests First:**
1. Create `tests/unit/test_deopt_data_structures.py`
   - Test DeoptInfo creation
   - Test ValueLocation mapping
   - Test DeoptReason/DeoptMode enums
   - Test JITFrame/InterpreterFrame structures

**Implementation:**
2. Create `src/deopt_types.py`
   - DeoptReason enum
   - DeoptMode enum
   - DeoptInfo dataclass
   - ValueLocation dataclass
   - JITFrame dataclass
   - InterpreterFrame dataclass
   - JITState dataclass
   - DeoptStats dataclass
   - DeoptHotspot dataclass

### Phase 2: State Materialization (RED-GREEN-REFACTOR)
**Tests First:**
3. Create `tests/unit/test_state_materialization.py` (≥10 tests)
   - Test materialize() with register values
   - Test materialize() with stack values
   - Test materialize() with constants
   - Test materialize_object() for JSObject
   - Test handling of escaped allocations
   - Test type conversions (Smi, Float64, Object)

**Implementation:**
4. Create `src/state_materializer.py`
   - StateMaterializer class
   - materialize() method
   - materialize_object() method
   - Type conversion helpers

### Phase 3: Frame Reconstruction (RED-GREEN-REFACTOR)
**Tests First:**
5. Create `tests/unit/test_frame_reconstruction.py` (≥15 tests)
   - Test reconstruct_frame() basic case
   - Test materialize_values() from registers
   - Test materialize_values() from stack
   - Test materialize_values() from constants
   - Test nested frames (inlined functions)
   - Test handling of missing values
   - Test frame size validation

**Implementation:**
6. Create `src/frame_reconstructor.py`
   - FrameReconstructor class
   - reconstruct_frame() method
   - materialize_values() method
   - Nested frame handling

### Phase 4: Deoptimization Triggers (RED-GREEN-REFACTOR)
**Tests First:**
7. Create `tests/unit/test_deopt_triggers.py` (≥8 tests)
   - Test handle_guard_failure()
   - Test handle_type_mismatch()
   - Test different DeoptReasons
   - Test trigger to manager integration

**Implementation:**
8. Create `src/trigger_handler.py`
   - DeoptTriggerHandler class
   - handle_guard_failure() method
   - handle_type_mismatch() method
   - Reason categorization

### Phase 5: Lazy Deoptimization (RED-GREEN-REFACTOR)
**Tests First:**
9. Create `tests/unit/test_lazy_deopt.py` (≥6 tests)
   - Test schedule_deopt()
   - Test process_pending()
   - Test queue management
   - Test safe point processing

**Implementation:**
10. Create `src/lazy_deopt.py`
    - LazyDeoptimizer class
    - schedule_deopt() method
    - process_pending() method
    - Queue management

### Phase 6: Eager Deoptimization (RED-GREEN-REFACTOR)
**Tests First:**
11. Create `tests/unit/test_eager_deopt.py` (≥5 tests)
    - Test bailout() immediate return
    - Test critical failures
    - Test state reconstruction on bailout

**Implementation:**
12. Create `src/eager_deopt.py`
    - EagerDeoptimizer class
    - bailout() method
    - Critical failure handling

### Phase 7: Deoptimization Manager (RED-GREEN-REFACTOR)
**Tests First:**
13. Create `tests/unit/test_deopt_manager.py` (≥10 tests)
    - Test register_optimized_function()
    - Test deoptimize() eager mode
    - Test deoptimize() lazy mode
    - Test get_stats()
    - Test function registry

**Implementation:**
14. Create `src/deopt_manager.py`
    - DeoptimizationManager class
    - register_optimized_function() method
    - deoptimize() method
    - get_stats() method
    - Function registry

### Phase 8: Profiling (RED-GREEN-REFACTOR)
**Tests First:**
15. Create `tests/unit/test_deopt_profiler.py` (≥8 tests)
    - Test record_deopt()
    - Test get_stats()
    - Test get_hot_deopts()
    - Test reason counting
    - Test hotspot identification

**Implementation:**
16. Create `src/deopt_profiler.py`
    - DeoptProfiler class
    - record_deopt() method
    - get_stats() method
    - get_hot_deopts() method
    - Statistics tracking

### Phase 9: Integration Testing
17. Create `tests/integration/test_deoptimization.py` (≥10 tests)
    - Test full deopt flow (JIT → interpreter)
    - Test with actual OptimizedCode (placeholder)
    - Test lazy vs eager modes
    - Test profiling integration
    - Test correctness of reconstructed state

### Phase 10: Public API
18. Create `src/__init__.py`
    - Export all public classes
    - Export enums
    - Export dataclasses

## Dependencies

**Available for import:**
```python
# Placeholder types until actual integration
from typing import Any, Dict, List, Optional

# From optimizing_jit (use placeholders if needed)
# - OptimizedCode
# - GuardNode

# From interpreter (use placeholders if needed)
# - InterpreterState
# - ExecutionContext

# From bytecode
# - BytecodeArray

# From object_runtime
# - JSValue
# - JSObject

# From hidden_classes
# - Shape
```

**If actual types not available:** Use type hints and placeholders for now.

## Key Algorithms

### Frame Reconstruction
```python
def reconstruct_frame(jit_frame, deopt_info):
    # 1. Read value locations from deopt_info
    # 2. For each interpreter value:
    #    - Read from register/stack/constant
    #    - Materialize JSValue
    # 3. Create InterpreterFrame with:
    #    - bytecode_offset from deopt_info
    #    - locals and stack from materialized values
    # 4. Return InterpreterFrame
```

### State Materialization
```python
def materialize(jit_state, deopt_info):
    # 1. For each value in value_map:
    #    - Get location (register/stack/constant)
    #    - Read raw value from JIT state
    #    - Convert to JSValue based on type
    # 2. Recreate objects from escaped data
    # 3. Build complete InterpreterState
    # 4. Return InterpreterState
```

### Lazy Deoptimization
```python
def schedule_deopt(function_id, deopt_point, reason):
    # 1. Add to pending queue
    # 2. Mark function for deopt
    # 3. Continue JIT execution to safe point
    # At safe point:
    # 4. Process pending deopts
    # 5. Reconstruct interpreter state
    # 6. Return to interpreter
```

## Testing Strategy

1. **Unit tests** (≥40 total):
   - Each class thoroughly tested
   - Edge cases covered
   - Error conditions tested

2. **Integration tests** (≥10):
   - Full deoptimization flow
   - Correctness verification
   - Performance verification

3. **Test Quality**:
   - No over-mocking
   - Test actual behavior
   - Clear test names
   - Good assertions

## Success Criteria

- [ ] All 40+ tests passing
- [ ] ≥85% test coverage
- [ ] Correct state reconstruction (verified by tests)
- [ ] <1ms deoptimization overhead
- [ ] Clean git history showing TDD pattern
- [ ] All 8 requirements implemented

## Performance Targets

- Deoptimization overhead: <1ms
- State reconstruction accuracy: 100%
- Minimal runtime overhead for deopt metadata

## Git Workflow

```bash
# After writing tests (RED)
git add tests/
git commit -m "[deoptimization] test: Add tests for X (RED)"

# After implementation (GREEN)
git add src/
git commit -m "[deoptimization] feat: Implement X (GREEN)"

# After refactoring (REFACTOR)
git add src/ tests/
git commit -m "[deoptimization] refactor: Improve X (REFACTOR)"
```

## Notes

- **Correctness is critical**: Deopt must ALWAYS produce valid interpreter state
- **Test edge cases**: Nested frames, escaped objects, type conversions
- **Use placeholders**: If dependencies not fully available, use type hints
- **Focus on correctness first**: Performance optimization comes later
- **Document assumptions**: If using simplified implementations

## Questions?

If you encounter issues with dependencies or unclear requirements, document them and proceed with reasonable placeholder implementations.
