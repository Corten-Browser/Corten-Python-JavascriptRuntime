# Deoptimization Component

**Type:** Feature
**Version:** 0.1.0
**Dependencies:** optimizing_jit, interpreter, bytecode, object_runtime, hidden_classes

## Purpose

Provides safe fallback from optimized JIT code to interpreter when speculation fails. This component ensures correctness when optimizations assumptions are violated by reconstructing interpreter state from JIT execution state.

## Key Features

- **Frame Reconstruction**: Convert JIT stack frames to interpreter frames
- **State Materialization**: Recreate JSValues from JIT registers/stack
- **Lazy Deoptimization**: Defer deopt to safe points (loop back-edge, function exit)
- **Eager Deoptimization**: Immediate bailout for critical failures
- **Deopt Triggers**: Handle guard failures, type mismatches, overflows
- **Profiling**: Track deopt patterns for optimization feedback

## Requirements

Implements 8 functional requirements:
- FR-P4-068: Deoptimization metadata generation
- FR-P4-069: Frame reconstruction (JIT → interpreter)
- FR-P4-070: Deopt triggers (failed guards, type mismatches)
- FR-P4-071: Lazy deoptimization
- FR-P4-072: Eager deoptimization
- FR-P4-073: Deopt bailout points
- FR-P4-074: State materialization (recreate interpreter state)
- FR-P4-075: Deopt statistics and profiling

## Architecture

```
DeoptimizationManager
├── FrameReconstructor
│   └── StateMaterializer
├── DeoptTriggerHandler
├── LazyDeoptimizer
├── EagerDeoptimizer
└── DeoptProfiler
```

## Usage

```python
from components.deoptimization import DeoptimizationManager, DeoptMode

# Initialize manager
manager = DeoptimizationManager()

# Register optimized function
manager.register_optimized_function(func_id, optimized_code)

# Deoptimize when guard fails
interpreter_state = manager.deoptimize(
    function_id=func_id,
    deopt_point=42,
    reason=DeoptReason.GUARD_FAILURE,
    mode=DeoptMode.EAGER
)

# Get statistics
stats = manager.get_stats()
print(f"Total deopts: {stats.total_deopts}")
```

## Testing

- ≥40 unit tests
- ≥85% coverage target
- Integration tests with optimizing_jit
- Correctness verification tests

## Performance

- Deoptimization overhead: <1ms
- State reconstruction accuracy: 100%
