# Error Stack Polish Component

**Version**: 0.1.0
**Status**: Complete
**ES2024 Wave**: D (Error Handling)

Complete Error.prototype.stack and error formatting implementation for ES2024.

## Requirements Implemented

### FR-ES24-D-015: Error.prototype.stack formatting
- Stack trace formatting with function names, filenames, line numbers, and column numbers
- Support for constructor calls (`new Constructor`)
- Support for native code (`Array.forEach (native)`)
- Support for eval'd code
- Support for anonymous functions (`<anonymous>`)
- Performance: <100µs per stack trace (achieved <0.1ms)

### FR-ES24-D-016: Error cause chain formatting
- Nested error cause formatting with "Caused by" prefix
- Circular reference detection
- Configurable max depth (default: 10, max: 100)
- Optional stack trace inclusion for each error in chain
- Truncation support when max depth exceeded

### FR-ES24-D-017: Source map support preparation
- Source location data structure preparation
- Source map URL generation (filename + ".map")
- Metadata preparation for source map resolution
- Support for source root directories
- Validation of line (1-indexed) and column (0-indexed) values

## API

### ErrorStackFormatter

```python
from components.error_stack_polish.src import ErrorStackFormatter

formatter = ErrorStackFormatter()

error = {
    "name": "TypeError",
    "message": "Cannot read property 'foo' of undefined",
    "stack_frames": [
        {
            "function": "processData",
            "filename": "app.js",
            "line": 42,
            "column": 15
        },
        {
            "function": "main",
            "filename": "app.js",
            "line": 100,
            "column": 5
        }
    ]
}

result = formatter.format_stack(error)
# Returns:
# {
#     "formatted_stack": "TypeError: Cannot read property 'foo' of undefined\n    at processData (app.js:42:15)\n    at main (app.js:100:5)",
#     "frame_count": 2,
#     "performance_ms": 0.045
# }
```

### CauseChainFormatter

```python
from components.error_stack_polish.src import CauseChainFormatter

formatter = CauseChainFormatter()

error = {
    "name": "ValidationError",
    "message": "Invalid user data",
    "cause": {
        "name": "TypeError",
        "message": "Expected string, got number"
    }
}

result = formatter.format_cause_chain(error, include_stack=False, max_depth=10)
# Returns:
# {
#     "formatted_chain": "ValidationError: Invalid user data\nCaused by: TypeError: Expected string, got number",
#     "depth": 2,
#     "total_errors": 2,
#     "truncated": False
# }
```

### SourceMapPreparer

```python
from components.error_stack_polish.src import SourceMapPreparer

preparer = SourceMapPreparer()

result = preparer.prepare_source_map(
    filename="dist/bundle.js",
    line=42,
    column=15,
    source_root="/app/src"
)
# Returns:
# {
#     "generated_location": {
#         "filename": "dist/bundle.js",
#         "line": 42,
#         "column": 15
#     },
#     "source_map_url": "dist/bundle.js.map",
#     "ready_for_resolution": True,
#     "metadata": {
#         "source_root": "/app/src",
#         "original_filename": "dist/bundle.js"
#     }
# }
```

## Performance

- **Stack formatting**: <100µs per stack trace (target met)
- **Cause chain formatting**: <200µs for typical chains (depth ≤5)
- **Source map preparation**: <50µs per location

## Test Coverage

- **Total tests**: 48
- **Coverage**: 97%
- **Test categories**:
  - Stack Formatting: 18 tests (12 functional + 6 edge cases)
  - Cause Chain Formatting: 14 tests (10 functional + 4 edge cases)
  - Source Map Preparation: 16 tests (8 functional + 8 edge cases)

## Usage

### Direct Import

```python
from components.error_stack_polish.src import (
    ErrorStackFormatter,
    CauseChainFormatter,
    SourceMapPreparer
)
```

### Component Integration

This component integrates with:
- Error handling runtime
- Debugger tools
- Logging systems
- Source map processors

## Testing

```bash
# Run all tests
python -m pytest components/error_stack_polish/tests/

# Run with coverage
python -m pytest components/error_stack_polish/tests/ --cov=components/error_stack_polish/src --cov-report=term-missing

# Run specific test file
python -m pytest components/error_stack_polish/tests/unit/test_stack_formatter.py -v
```

## File Structure

```
components/error_stack_polish/
├── src/
│   ├── __init__.py              # Public API exports
│   ├── stack_formatter.py       # ErrorStackFormatter class
│   ├── cause_chain.py           # CauseChainFormatter class
│   └── source_map.py            # SourceMapPreparer class
├── tests/
│   ├── unit/
│   │   ├── test_stack_formatter.py     # 18 tests
│   │   ├── test_cause_chain.py         # 14 tests
│   │   └── test_source_map.py          # 16 tests
│   └── integration/
│       └── test_integration.py         # Integration tests
└── README.md                    # This file
```

## Contract

See `/home/user/Corten-JavascriptRuntime/contracts/error_stack_polish.yaml` for complete OpenAPI specification.

## Requirements Traceability

| Requirement | Implementation | Tests | Status |
|-------------|---------------|-------|--------|
| FR-ES24-D-015 | ErrorStackFormatter | 18 tests | ✅ Complete |
| FR-ES24-D-016 | CauseChainFormatter | 14 tests | ✅ Complete |
| FR-ES24-D-017 | SourceMapPreparer | 16 tests | ✅ Complete |

## Notes

- Stack frames use 1-indexed line numbers (standard for stack traces)
- Columns use 0-indexed values (standard for character positions)
- Circular cause references are detected using Python's `id()` function
- Source map URLs follow the convention: `{filename}.map`
- All validation errors raise `ValueError` or `TypeError` with descriptive messages

## Version History

- **0.1.0** (2025-11-15): Initial implementation
  - Complete Error.prototype.stack formatting
  - Error cause chain formatting with circular detection
  - Source map support preparation
  - 48 tests, 97% coverage
  - Performance targets met
