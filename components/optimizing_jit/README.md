# optimizing_jit Component

**Type**: Feature
**Version**: 0.1.0
**Tech Stack**: Python, IR-based compilation, SSA, Graph algorithms

## Responsibility

Advanced JIT compiler with aggressive optimizations for 20-50x speedup over interpreter. Implements high-level IR, SSA form, type specialization, inlining, loop optimizations, escape analysis, and more.

## Structure

```
optimizing_jit/
├── src/
│   ├── __init__.py                    # Public API exports
│   ├── ir_builder.py                  # IR construction from bytecode
│   ├── ssa_builder.py                 # SSA form conversion
│   ├── ir_nodes.py                    # IR node definitions
│   ├── dominator_tree.py              # Dominator tree for SSA
│   ├── optimizations/
│   │   ├── __init__.py
│   │   ├── type_specialization.py     # Type specialization (Smi, Float64, Object)
│   │   ├── inlining.py                # Function inlining
│   │   ├── loop_opts.py               # Loop optimizations (LICM, unrolling)
│   │   ├── dce.py                     # Dead code elimination
│   │   ├── constant_folding.py        # Constant folding
│   │   ├── escape_analysis.py         # Escape analysis & scalar replacement
│   │   └── bounds_check_elim.py       # Bounds check elimination
│   ├── speculation.py                 # Guards and deoptimization triggers
│   ├── register_allocator.py          # Graph coloring register allocation
│   ├── code_generator.py              # IR → machine code
│   └── tier_up.py                     # Baseline → optimizing tier-up
├── tests/
│   ├── unit/
│   │   ├── test_ir_builder.py
│   │   ├── test_ssa_builder.py
│   │   ├── test_type_specialization.py
│   │   ├── test_inlining.py
│   │   ├── test_loop_opts.py
│   │   ├── test_dce.py
│   │   ├── test_constant_folding.py
│   │   ├── test_escape_analysis.py
│   │   ├── test_bounds_check_elim.py
│   │   ├── test_speculation.py
│   │   ├── test_register_allocator.py
│   │   └── test_code_generator.py
│   └── integration/
│       └── test_optimizing_jit.py
├── CLAUDE.md                          # Component development notes
├── README.md                          # This file
└── component.yaml                     # Component metadata
```

## Usage

### Compile with Optimizing JIT

```python
from components.optimizing_jit.src import OptimizingJITCompiler
from components.bytecode.src import BytecodeArray

compiler = OptimizingJITCompiler()

# Compile with profiling data
profiling_data = get_profiling_data()  # From baseline JIT
optimized_code = compiler.compile_function(bytecode, profiling_data)

# Execute optimized code
result = optimized_code.execute()
```

### Tier-up Decision

```python
if compiler.should_optimize(function_id, call_count, baseline_time):
    # Hot function - optimize it
    optimized_code = compiler.compile_function(bytecode, profiling_data)
```

## Key Features

### IR Infrastructure
- **Sea-of-nodes IR**: High-level intermediate representation
- **SSA Form**: Static Single Assignment with phi nodes
- **Dominator Tree**: For efficient SSA construction

### Core Optimizations
- **Type Specialization**: Specialize to Smi, Float64, Object based on profiling
- **Function Inlining**: Inline hot function calls
- **Dead Code Elimination**: Remove unreachable code
- **Constant Folding**: Evaluate constant expressions at compile time

### Advanced Optimizations
- **Loop Optimizations**: LICM (loop-invariant code motion), loop unrolling
- **Escape Analysis**: Determine which objects escape
- **Scalar Replacement**: Replace non-escaping objects with scalars
- **Bounds Check Elimination**: Remove redundant array bounds checks

### Speculation & Codegen
- **Guards**: Insert type guards for speculative optimizations
- **Deoptimization Triggers**: Safe fallback to interpreter
- **Graph Coloring**: Advanced register allocation
- **Code Generation**: Optimized machine code generation

## Performance Targets

- **Speedup**: 20-50x over interpreter
- **Compilation Latency**: <500ms
- **Optimization Aggressiveness**: High (uses profiling data)

## Development

This component follows TDD methodology:
1. RED: Write failing tests
2. GREEN: Implement minimal code to pass
3. REFACTOR: Improve code quality

See CLAUDE.md for detailed development notes and git history for Red-Green-Refactor pattern.

## Dependencies

- **baseline_jit**: CodeGenerator, RegisterAllocator reference implementations
- **hidden_classes**: Shape for type specialization
- **inline_caching**: InlineCache for profiling data
- **bytecode**: BytecodeArray for compilation input
- **interpreter**: InterpreterState for deoptimization

## Testing

- **Unit Tests**: ≥90 tests
- **Coverage**: ≥80%
- **Integration Tests**: Cross-tier compilation (baseline → optimizing)
- **Performance Benchmarks**: Verify 20-50x speedup

## Future Work

- Platform-specific backends (x64, ARM64)
- More aggressive optimizations (strength reduction, range analysis)
- Profile-guided optimization tuning
- Deoptimization statistics and adaptive optimization
