# baseline_jit

**Type:** Feature
**Version:** 0.1.0

## Purpose

Fast baseline JIT compiler that compiles bytecode to machine code for 5-10x speedup over interpreter execution.

## Features

- **Bytecode → Machine Code Compilation:** Direct 1:1 translation with simple optimizations
- **Linear Scan Register Allocation:** Fast register allocation algorithm
- **IC Integration:** Inline caching integration for fast property access
- **OSR (On-Stack Replacement):** Tier-up from interpreter during hot loop execution
- **Code Cache:** LRU cache for compiled code (max 10MB)
- **x64 Backend:** Platform-specific machine code generation (ARM64 planned)
- **Tier-up Triggers:** Automatic compilation when functions are hot

## Requirements

Implements FR-P4-023 through FR-P4-037 (15 requirements):
- Bytecode compilation
- Register allocation
- Code generation
- Stack frame management
- IC integration
- OSR support
- Code caching

## Performance Targets

- **Speedup:** 5-10x over interpreter
- **Compilation Latency:** <100ms
- **Code Cache Size:** <10MB

## Dependencies

- `bytecode`: BytecodeArray, Opcode
- `interpreter`: InterpreterState, ExecutionContext
- `inline_caching`: InlineCache, ICState
- `hidden_classes`: Shape

## Usage

```python
from components.baseline_jit import BaselineJITCompiler

# Create compiler
compiler = BaselineJITCompiler(backend="x64")

# Compile bytecode
compiled_code = compiler.compile_function(bytecode_array)

# Execute compiled code
result = compiled_code.execute(args)
```

## Testing

- **Unit Tests:** ≥75 tests
- **Coverage:** ≥80%
- **Integration Tests:** Interpreter integration, tier-up scenarios
- **Performance Tests:** Benchmarks for speedup validation
