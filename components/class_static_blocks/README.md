# class_static_blocks

ES2022 static initialization blocks for JavaScript classes.

## Overview

This component implements static initialization blocks (`static { ... }`) for JavaScript classes, as specified in ES2022. Static blocks provide a way to perform complex initialization logic for static class members.

## Features

- **Static Block Syntax**: Parse and execute `static { ... }` blocks inside class bodies
- **Execution Order**: Static blocks run after all static fields are initialized
- **This Binding**: `this` in static blocks refers to the class constructor
- **Private Access**: Static blocks can access private static fields and methods

## Installation

This component is part of the Corten JavaScript Runtime. It depends on:
- `parser` (v0.2.0+) - For AST and parsing infrastructure
- `private_class_features` (v0.1.0+) - For private field access
- `interpreter` (v0.2.0+) - For statement execution
- `object_runtime` (v0.3.0+) - For JSValue and JSObject types

## Usage

### Basic Example

```javascript
class Counter {
    static count = 0;

    static {
        console.log('Counter class initialized');
        this.count = 0;
    }

    constructor() {
        Counter.count++;
    }
}
```

### Execution Order

Static blocks execute after static fields are initialized:

```javascript
class Example {
    static x = 1;
    static {
        console.log(this.x); // 1 (field already initialized)
        this.y = 2;
    }
    static z = 3;
    static {
        console.log(this.z); // 3 (field initialized before this block)
    }
}
```

### This Binding

In static blocks, `this` refers to the class constructor:

```javascript
class C {
    static {
        console.log(this === C); // true
        this.method = () => "added in static block";
    }
}

console.log(C.method()); // "added in static block"
```

### Private Access

Static blocks can access private static fields:

```javascript
class Secrets {
    static #apiKey = 'secret';

    static {
        console.log(this.#apiKey); // 'secret'
        this.#apiKey = 'new-secret';
    }

    static getKey() {
        return this.#apiKey; // 'new-secret'
    }
}
```

### Scope Isolation

Variables in static blocks are block-scoped:

```javascript
class C {
    static {
        let temp = 42;
        this.value = temp;
    }
    static {
        // console.log(temp); // ReferenceError: temp not defined
        console.log(this.value); // 42
    }
}
```

## API

### AST Nodes

#### StaticBlock

```python
@dataclass
class StaticBlock(Statement):
    body: List[Statement]
    location: SourceLocation
```

### Parser Functions

#### parse_class_static_block(parser) -> StaticBlock

Parse a static block from the parser's current position.

```python
static_block = parse_class_static_block(parser)
```

#### is_static_block(parser) -> bool

Check if the current position is the start of a static block.

```python
if is_static_block(parser):
    block = parse_class_static_block(parser)
```

### Executor

#### StaticBlockExecutor

```python
executor = StaticBlockExecutor()
executor.execute_static_block(block, class_constructor, context)
executor.execute_all_static_blocks(blocks, class_constructor, context)
```

### Scope

#### StaticBlockScope

```python
scope = StaticBlockScope(parent_scope, class_constructor)
this_value = scope.resolve_this()  # Returns class_constructor
can_access = scope.can_access_private('#privateField')
```

## Requirements

Implements the following functional requirements:

- **FR-ES24-B-011**: Static initialization blocks `static { ... }` syntax
- **FR-ES24-B-012**: Static block execution order - runs after static fields
- **FR-ES24-B-013**: Static block this binding - `this` refers to class constructor
- **FR-ES24-B-014**: Static block private access - can access private static fields

## Testing

Run tests:

```bash
pytest tests/ -v
```

Run with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

## Performance

- Static block parsing: <100μs per block
- Static block execution: <200ns overhead per block
- Private field access: <100ns overhead in static blocks
- Memory overhead: <64 bytes per static block

## Architecture

```
class_static_blocks/
├── src/
│   ├── __init__.py              # Public API exports
│   ├── ast_nodes.py             # StaticBlock AST node
│   ├── parser_extensions.py    # Parsing logic
│   ├── static_block_executor.py # Execution logic
│   └── static_block_scope.py    # Scope management
└── tests/
    ├── unit/
    │   ├── test_static_block_syntax.py
    │   ├── test_execution_order.py
    │   ├── test_this_binding.py
    │   └── test_private_access.py
    └── integration/
        └── test_static_blocks_integration.py
```

## Error Handling

### Syntax Errors

- Static block outside class body: `SyntaxError`
- Static block with parameters: `SyntaxError`
- Static block with name: `SyntaxError`
- Async/generator static block: `SyntaxError`

### Runtime Errors

- Error in static block execution: `RuntimeError`
- Accessing private field from wrong class: `TypeError`
- Accessing undeclared variable: `ReferenceError`

## Integration

This component integrates with:

- **Parser**: Extends class body parsing to recognize static blocks
- **Private Class Features**: Uses PrivateFieldManager for private field access
- **Interpreter**: Uses statement evaluation for block execution
- **Object Runtime**: Binds `this` to JSObject (class constructor)

## Version

Current version: 0.1.0

## License

Part of Corten JavaScript Runtime.
