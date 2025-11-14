# JavaScript Runtime Architecture

## Project Overview

This is a production-grade JavaScript runtime implementation targeting ECMAScript 2024 (ES15) compliance, designed for browser integration with multi-tier execution, garbage collection, and Web API support.

## Architectural Principles

1. **Multi-tier execution**: Interpreter → Baseline JIT → Optimizing JIT
2. **Register-based bytecode**: Architecture-independent intermediate representation
3. **Generational GC**: Fast young generation + efficient old generation
4. **Hidden classes**: Optimized object property access
5. **Modular design**: Clear component boundaries enabling parallel development

## Component Architecture - Phase 1 (Foundation)

This implementation follows a phased approach. Phase 1 focuses on the foundational components needed for basic JavaScript execution (ES5 core + Test262 validation).

### Dependency Hierarchy

Components are organized by dependency level:

**Level 0 (Base)** - No dependencies:
- `shared_types` - Common types, enums, utilities

**Level 1 (Core)** - Foundation runtime services:
- `value_system` - Value representation, tagging, boxing/unboxing
- `memory_gc` - Memory allocation and garbage collection
- `object_runtime` - Object model and built-in objects

**Level 2 (Feature)** - Core functionality:
- `parser` - Lexer, parser, AST generation, scope analysis
- `bytecode` - Bytecode format and compiler (AST → bytecode)

**Level 3 (Integration)** - Execution orchestration:
- `interpreter` - Bytecode interpreter and execution engine

**Level 4 (Application)** - Entry points:
- `runtime_cli` - Command-line interface and REPL

### Component Descriptions

#### 1. shared_types (Level 0, ~20k tokens)
**Responsibility**: Common types, enums, and utilities used across all components.

**Exports**:
- `TypeTag` enum (SMI, Object, String, Number, Boolean, Undefined, Null)
- `ErrorType` enum (SyntaxError, TypeError, ReferenceError, etc.)
- `SourceLocation` struct (file, line, column, offset)
- Utility functions (assertions, logging, error handling)

**Dependencies**: None

**Tech Stack**: Python 3.11+, dataclasses, enums

---

#### 2. value_system (Level 1, ~30k tokens)
**Responsibility**: Value representation using tagged pointers, SMI optimization, type checking.

**Exports**:
- `Value` class - Tagged value representation
- `BoxedValue` class - Heap-allocated values
- Type checking: `IsString()`, `IsNumber()`, `IsObject()`, `IsSMI()`, etc.
- Boxing/unboxing: `Box()`, `Unbox()`, `ToNumber()`, `ToString()`
- SMI encoding/decoding (32-bit signed integers in pointer)

**Dependencies**: shared_types

**Tech Stack**: Python 3.11+, ctypes for pointer manipulation

---

#### 3. memory_gc (Level 1, ~50k tokens)
**Responsibility**: Memory allocation and simple mark-and-sweep garbage collection.

**Exports**:
- `Allocator` - Memory allocation interface
- `GarbageCollector` - Mark-and-sweep GC implementation
- `HeapObject` - Base class for all heap-allocated objects
- Allocation functions: `AllocateObject()`, `AllocateArray()`, `AllocateString()`
- GC triggering: `MaybeCollect()`, `ForceCollect()`

**Dependencies**: shared_types, value_system

**Tech Stack**: Python 3.11+, memory profiling with tracemalloc

**Notes**: Simple mark-and-sweep for Phase 1. Generational GC in Phase 2.

---

#### 4. object_runtime (Level 1, ~70k tokens)
**Responsibility**: Object model, property storage, built-in objects (Object, Array, Function, String, Number).

**Exports**:
- `JSObject` - JavaScript object representation
- `JSArray` - Array implementation
- `JSFunction` - Function representation (bytecode + scope)
- `JSString` - String implementation
- `JSNumber` - Number implementation
- Property access: `GetProperty()`, `SetProperty()`, `HasProperty()`, `DeleteProperty()`
- Built-in constructors: `ObjectConstructor`, `ArrayConstructor`, `FunctionConstructor`
- Prototype chains: `GetPrototype()`, `SetPrototype()`

**Dependencies**: shared_types, value_system, memory_gc

**Tech Stack**: Python 3.11+, dict-based property storage (Phase 1)

**Notes**: Simple dict-based properties for Phase 1. Hidden classes in Phase 4.

---

#### 5. parser (Level 2, ~70k tokens)
**Responsibility**: Lexical analysis, syntax parsing, AST generation, scope analysis (ES5 core).

**Exports**:
- `Lexer` - Tokenization (source → tokens)
- `Token` - Token representation (type, value, location)
- `Parser` - Recursive descent parser (tokens → AST)
- AST nodes: `Expression`, `Statement`, `Declaration`, `Literal`, `Identifier`, etc.
- `ScopeAnalyzer` - Scope resolution, variable binding
- `Parse()` - Main entry point (source → AST)

**Dependencies**: shared_types, object_runtime

**Tech Stack**: Python 3.11+, recursive descent parsing

**Features** (Phase 1 - ES5 core):
- Variables: var
- Functions: function declarations, function expressions
- Objects: object literals, property access
- Arrays: array literals, indexing
- Operators: arithmetic, comparison, logical, assignment
- Control flow: if/else, while, for, switch, break, continue, return
- Scoping: function scope, closures

**Deferred to Phase 2**:
- let/const (block scope)
- Arrow functions
- Classes
- Destructuring, spread/rest
- Template literals
- ES modules

---

#### 6. bytecode (Level 2, ~60k tokens)
**Responsibility**: Register-based bytecode format and compiler (AST → bytecode).

**Exports**:
- `Opcode` enum (~50 opcodes for Phase 1)
- `Instruction` - Bytecode instruction representation
- `BytecodeArray` - Compiled bytecode container
- `BytecodeCompiler` - AST → bytecode compiler
- `Compile()` - Main entry point (AST → bytecode)

**Dependencies**: shared_types, object_runtime, parser

**Tech Stack**: Python 3.11+, struct for bytecode encoding

**Instruction Set** (Phase 1):
- **Literals**: LoadConstant, LoadUndefined, LoadNull, LoadTrue, LoadFalse
- **Variables**: LoadGlobal, StoreGlobal, LoadLocal, StoreLocal
- **Operators**: Add, Subtract, Multiply, Divide, Modulo, Equal, NotEqual, LessThan, etc.
- **Control flow**: Jump, JumpIfTrue, JumpIfFalse, Return
- **Objects**: CreateObject, LoadProperty, StoreProperty, DeleteProperty
- **Arrays**: CreateArray, LoadElement, StoreElement
- **Functions**: CreateClosure, CallFunction

**Register Allocation**: Simple stack-based allocation for Phase 1, optimized register allocation in Phase 2.

---

#### 7. interpreter (Level 3, ~70k tokens)
**Responsibility**: Bytecode interpreter, execution engine, runtime services.

**Exports**:
- `Interpreter` - Main interpreter class
- `ExecutionContext` - Execution state (scope, this, call stack)
- `CallFrame` - Function call frame
- `Execute()` - Bytecode execution (bytecode → result)
- `EvaluationResult` - Result wrapper (value or exception)

**Dependencies**: shared_types, value_system, memory_gc, object_runtime, bytecode

**Tech Stack**: Python 3.11+, match/case for opcode dispatch

**Features** (Phase 1):
- Bytecode dispatch loop
- Variable resolution (global + local scopes)
- Function calls (with arguments, return values)
- Object property access
- Array element access
- Exception handling (throw/catch)
- Basic profiling (instruction counter)

**Deferred to Phase 4**:
- Inline caching
- JIT compilation hints
- OSR (on-stack replacement)

---

#### 8. runtime_cli (Level 4, ~20k tokens)
**Responsibility**: Command-line interface, REPL, Test262 test runner.

**Exports**:
- `main()` - Entry point with argument parsing
- `REPL` - Interactive read-eval-print loop
- `Test262Runner` - Test262 conformance test executor
- `ExecuteFile()` - Execute JavaScript file
- `EvaluateExpression()` - Evaluate single expression

**Dependencies**: All components (orchestration layer)

**Tech Stack**: Python 3.11+, argparse for CLI, pytest for testing

**Features**:
- Execute JavaScript files: `runtime --file script.js`
- Interactive REPL: `runtime --repl`
- Run Test262 tests: `runtime --test262 test/language/expressions/`
- Verbose mode: `runtime --verbose --file script.js`
- Bytecode dump: `runtime --dump-bytecode --file script.js`

---

## Build Order (Dependency Topological Sort)

**Wave 1** (1 component, no dependencies):
1. shared_types

**Wave 2** (2 components in parallel):
2. value_system
3. memory_gc (can start together, both depend only on shared_types)

**Wave 3** (1 component):
4. object_runtime (depends on shared_types, value_system, memory_gc)

**Wave 4** (2 components in parallel):
5. parser (depends on shared_types, object_runtime)
6. bytecode (starts after parser completes - depends on parser)

Actually, let me correct Wave 4:

**Wave 4** (1 component):
5. parser (depends on shared_types, object_runtime)

**Wave 5** (1 component):
6. bytecode (depends on shared_types, object_runtime, parser)

**Wave 6** (1 component):
7. interpreter (depends on all above)

**Wave 7** (1 component):
8. runtime_cli (depends on all above)

Total waves: 7
Max parallelism: 2 components (Wave 2 only)
With 7 max parallel agents, this sequence is optimal.

## Technology Stack

**Language**: Python 3.11+
- Chosen for rapid development, clear code, extensive standard library
- Production engines use C/C++/Rust, but Python sufficient for educational/prototype runtime

**Key Libraries**:
- dataclasses, enums (shared_types)
- ctypes (value_system - pointer manipulation)
- tracemalloc (memory_gc - memory profiling)
- argparse (runtime_cli - command-line parsing)
- pytest (testing framework)

**Testing**:
- Unit tests: pytest (80%+ coverage required)
- Integration tests: Cross-component integration
- Conformance tests: Test262 suite (target 1000 passing tests Phase 1)

**Version Control**:
- Single git repository
- Component-prefixed commits: `[parser] Add function declaration support`

## API Contracts

Each component exports a well-defined API used by dependent components. Contracts are defined in `contracts/` directory using YAML (OpenAPI style) or Python type hints.

Example contract (`contracts/value_system.yaml`):
```yaml
component: value_system
version: 0.1.0
exports:
  - name: Value
    type: class
    description: Tagged value representation
    methods:
      - name: __init__
        params:
          - name: raw
            type: int
        returns: Value
      - name: IsNumber
        params: []
        returns: bool
      - name: IsObject
        params: []
        returns: bool
```

## Token Budget

Each component allocated token budget based on estimated complexity:

| Component | Estimated Tokens | Status |
|-----------|-----------------|--------|
| shared_types | ~20k | Optimal |
| value_system | ~30k | Optimal |
| memory_gc | ~50k | Optimal |
| object_runtime | ~70k | Optimal |
| parser | ~70k | Optimal |
| bytecode | ~60k | Optimal |
| interpreter | ~70k | Optimal |
| runtime_cli | ~20k | Optimal |
| **Total** | **~390k** | **Avg: 49k/component** |

All components well within limits (optimal: 70k, warning: 90k, split: 110k).

## Phase 1 Success Criteria

✅ All 8 components implemented
✅ All component tests passing (100% pass rate)
✅ Test coverage ≥ 80% per component
✅ Integration tests passing (100% pass rate)
✅ Test262 core subset: **1000+ passing tests**
✅ REPL functional (interactive JavaScript execution)
✅ File execution functional (`runtime --file script.js`)
✅ All contracts validated
✅ All quality gates passed

**Deliverables**:
- 8 working components with complete implementation
- Comprehensive test suite
- Working CLI/REPL
- Documentation (README, API docs, architecture)
- Test262 conformance report

## Future Phases (Not Implemented in This Session)

**Phase 2** (Month 2-4): ES6 features, async/await, modules, generational GC
**Phase 3** (Month 5-6): Browser integration, Web APIs, Workers
**Phase 4** (Month 7-9): JIT compilation, inline caching, hidden classes
**Phase 5** (Month 10-12): Service Workers, WebAssembly, DevTools Protocol

This architecture provides a solid foundation for a production JavaScript runtime while keeping the initial implementation scope manageable (Phase 1 = Month 1-2 roadmap from spec).

---

**Document Version**: 1.0
**Date**: 2025-11-14
**Status**: Architecture Approved - Ready for Implementation
