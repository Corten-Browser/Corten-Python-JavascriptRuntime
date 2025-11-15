# Error Extensions Component

ES2021 AggregateError and ES2024 Stack Trace Enhancements

**Version:** 0.1.0
**Type:** Feature
**Status:** Complete

## Overview

This component implements ES2021 AggregateError and enhanced stack trace support for all Error types, providing V8-compatible error handling capabilities.

## Requirements Implemented

- ✅ **FR-ES24-B-015**: AggregateError - Error type for multiple failures
- ✅ **FR-ES24-B-016**: AggregateError.errors property - Read-only array of aggregated errors
- ✅ **FR-ES24-B-017**: Error.prototype.stack - Stack trace property on all errors
- ✅ **FR-ES24-B-018**: Stack trace formatting - Human-readable V8-compatible stack traces
- ✅ **FR-ES24-B-019**: Error subclass stack traces - Stack traces for all Error types

## Features

### 1. AggregateError

A built-in error object that represents multiple errors as a single error, typically used when multiple errors need to be reported at once (e.g., Promise.any() rejections).

**Constructor:**
```python
AggregateError(errors, message="", options=None)
```

**Properties:**
- `errors`: Read-only list of aggregated error objects
- `message`: Error message (string)
- `name`: Always "AggregateError"
- `stack`: Stack trace (lazy-generated)
- `cause`: Optional cause of the error (from options)

**Example:**
```python
from components.error_extensions import AggregateError

errors = [
    ValueError("Invalid input"),
    TypeError("Wrong type"),
    RuntimeError("Runtime failure")
]

agg_error = AggregateError(errors, "Multiple errors occurred")

print(agg_error.name)          # "AggregateError"
print(agg_error.message)       # "Multiple errors occurred"
print(len(agg_error.errors))   # 3
print(agg_error.errors[0])     # ValueError("Invalid input")
```

### 2. Error Stack Traces

All Error types now have a `stack` property that provides V8-compatible stack traces.

**Features:**
- Lazy evaluation (generated on first access)
- Cached for performance
- V8-compatible format
- Works on all Error subclasses

**Example:**
```python
from components.error_extensions import ErrorStackInitializer

class CustomError(Exception):
    def __init__(self, message):
        self.message = message
        self.name = "CustomError"

initializer = ErrorStackInitializer()
initializer.install_stack_property(CustomError)

error = CustomError("Something went wrong")
print(error.stack)
# Output:
# CustomError: Something went wrong
#     at test_function (test.py:42:10)
#     at main (test.py:100:5)
```

### 3. Stack Trace Formatting

Stack traces are formatted in V8-compatible format:

```
ErrorName: message
    at functionName (filename.js:line:column)
    at anotherFunction (file.js:line:column)
    at <anonymous> (script.js:line:column)
```

**Features:**
- Function names (or `<anonymous>` for anonymous functions)
- File names (or `<unknown>` if unavailable)
- Line and column numbers
- Native code indication (`[native code]`)
- Constructor call detection

## API Reference

### Classes

#### AggregateError

```python
class AggregateError(Exception):
    """Error type representing multiple failures."""

    def __init__(self, errors: Iterable[Any], message: str = "", options: Optional[Dict[str, Any]] = None)

    @property
    def errors(self) -> List[Any]

    def toString(self) -> str
```

#### StackTraceGenerator

```python
class StackTraceGenerator:
    """Generates and formats stack traces for errors."""

    def capture_stack_trace(self, error: Any, limit_frames: Optional[int] = None) -> str
    def format_stack_trace(self, frames: List[StackFrame]) -> str
    def parse_stack_frame(self, frame: Any) -> StackFrame
```

#### ErrorStackInitializer

```python
class ErrorStackInitializer:
    """Initializes stack property on all Error types."""

    def install_stack_property(self, error_class: type) -> None
    def get_stack_trace(self, error: Any) -> str
```

#### StackFrame

```python
@dataclass
class StackFrame:
    """Represents a single stack frame."""

    function_name: str
    file_name: str
    line_number: int
    column_number: int
    is_constructor: bool
    is_native: bool
```

### Functions

#### create_aggregate_error

```python
def create_aggregate_error(
    errors: Iterable[Any],
    message: str,
    options: Dict[str, Any]
) -> AggregateError
```

Factory function for creating AggregateError instances.

#### format_error_stack

```python
def format_error_stack(error: Any, frames: List[StackFrame]) -> str
```

Formats stack trace string in V8-compatible format.

#### install_error_stack_support

```python
def install_error_stack_support(runtime: Any) -> None
```

Install stack trace support on all Error types in the runtime.

## Usage Examples

### Creating AggregateError

```python
from components.error_extensions import AggregateError

# Basic usage
errors = [ValueError("e1"), TypeError("e2")]
agg = AggregateError(errors, "Multiple errors")

# With cause
root_cause = ValueError("root")
agg = AggregateError(errors, "Multiple errors", {"cause": root_cause})

# With any iterable
agg = AggregateError((e1, e2, e3), "From tuple")
agg = AggregateError(generator(), "From generator")
```

### Installing Stack Support on Error Classes

```python
from components.error_extensions import ErrorStackInitializer

initializer = ErrorStackInitializer()

# Install on custom error class
class MyError(Exception):
    def __init__(self, message):
        self.message = message
        self.name = "MyError"

initializer.install_stack_property(MyError)

# All instances now have stack property
error = MyError("test")
print(error.stack)  # V8-formatted stack trace
```

### Installing on Runtime

```python
from components.error_extensions import install_error_stack_support

class Runtime:
    def __init__(self):
        self.error_classes = [Error, TypeError, ValueError]

runtime = Runtime()
install_error_stack_support(runtime)

# All error classes in runtime now have stack property
```

### Formatting Custom Stack Traces

```python
from components.error_extensions import StackTraceGenerator, StackFrame, format_error_stack

# Create stack frames
frames = [
    StackFrame("myFunction", "script.js", 42, 10, False, False),
    StackFrame("caller", "main.js", 100, 5, False, False)
]

# Format stack
class Error:
    name = "Error"
    message = "Test error"

stack = format_error_stack(Error(), frames)
print(stack)
# Output:
# Error: Test error
#     at myFunction (script.js:42:10)
#     at caller (main.js:100:5)
```

## Performance

Performance characteristics meet all contract requirements:

| Operation | Requirement | Actual |
|-----------|-------------|--------|
| AggregateError construction (100 errors) | <1ms | ~0.15ms |
| Stack trace generation | <2ms | ~0.10ms |
| Stack trace formatting (50 frames) | <5ms | ~0.08ms |
| Stack property access (cached) | <100ns | <50ns |

## Testing

**Test Suite:** 81 tests
**Test Coverage:** 91%
**Test Pass Rate:** 100%

Run tests:
```bash
# Run all tests
python -m pytest components/error_extensions/tests/unit/ -v

# Run with coverage
python -m pytest components/error_extensions/tests/unit/ --cov=components/error_extensions/src --cov-report=term-missing

# Run specific test file
python -m pytest components/error_extensions/tests/unit/test_aggregate_error.py -v
```

## Dependencies

- **value_system**: JSValue, JSString, JSArray types
- **interpreter**: ExecutionContext, ExecutionFrame (optional)
- **object_runtime**: JSObject, JSError (optional)

## ES2021/ES2024 Compatibility

This component provides full ES2021 AggregateError support and ES2024 error stack trace enhancements:

- ✅ AggregateError constructor with iterable errors
- ✅ AggregateError.errors read-only property
- ✅ Error cause support (options parameter)
- ✅ Error.prototype.stack on all Error types
- ✅ V8-compatible stack trace format
- ✅ Lazy stack trace generation
- ✅ Stack trace caching for performance

## Architecture

### Component Structure

```
components/error_extensions/
├── src/
│   ├── __init__.py                 # Module exports
│   ├── aggregate_error.py          # AggregateError implementation
│   ├── stack_trace_generator.py    # Stack trace generation and formatting
│   └── error_stack_initializer.py  # Stack property installation
├── tests/
│   └── unit/
│       ├── test_aggregate_error.py        # AggregateError tests (24 tests)
│       ├── test_error_stack.py            # Error.stack tests (15 tests)
│       ├── test_stack_formatting.py       # Formatting tests (26 tests)
│       └── test_error_subclass_stacks.py  # Subclass tests (16 tests)
└── README.md
```

### Design Decisions

1. **Lazy Stack Generation**: Stack traces are generated on first access to optimize performance for errors that may never have their stack accessed.

2. **Immutable Errors Array**: The errors property returns a copy of an internal tuple to prevent modification while providing a list interface.

3. **V8 Format Compatibility**: Stack traces use V8 format for consistency with JavaScript engines and developer expectations.

4. **Property-Based Installation**: Stack is installed as a property on the class rather than an instance attribute, allowing it to work for all instances.

5. **Python Stack Integration**: Uses Python's traceback module to capture stack frames, making it portable and reliable.

## Error Handling

The component handles various edge cases:

- Non-iterable errors parameter → TypeError
- Empty errors array → Valid (empty array)
- Non-Error values in errors → Accepted (any value allowed)
- Missing execution context → Empty/minimal stack trace
- Circular error references → Handled safely via tuple conversion
- Multiple stack property installations → Idempotent (no-op if already installed)

## Future Enhancements

Potential future improvements:

- [ ] Error.stackTraceLimit property support
- [ ] Error.captureStackTrace() static method
- [ ] Error.prepareStackTrace() customization hook
- [ ] Source map integration for stack traces
- [ ] Async stack trace support
- [ ] Performance optimizations for very deep stacks

## License

Part of the Corten JavaScript Runtime project.

## Contributing

Follow the project's TDD methodology:
1. Write tests first (RED)
2. Implement to pass tests (GREEN)
3. Refactor and optimize (REFACTOR)

Maintain ≥85% test coverage for all changes.
