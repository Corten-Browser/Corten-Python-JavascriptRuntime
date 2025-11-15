# object_methods

ES2024 Object static method implementations for JavaScript runtime.

## Overview

Implements missing Object static methods to achieve ES2024 compliance:
- `Object.fromEntries()` - Create object from [key, value] pairs
- `Object.entries()` - Get enumerable [key, value] pairs
- `Object.values()` - Get enumerable values
- `Object.getOwnPropertyDescriptors()` - Get all property descriptors
- `Object.setPrototypeOf()` - Set prototype with edge case handling
- `Object.is()` - SameValue equality comparison
- `Object.assign()` - Copy properties with edge cases
- `Object[Symbol.iterator]` - Iterator for object entries

## Requirements

Implements 8 functional requirements:
- FR-ES24-036: Object.fromEntries()
- FR-ES24-037: Object.entries()
- FR-ES24-038: Object.values()
- FR-ES24-039: Object.getOwnPropertyDescriptors()
- FR-ES24-040: Object.setPrototypeOf() edge cases
- FR-ES24-041: Object.is()
- FR-ES24-042: Object.assign() edge cases
- FR-ES24-043: Object[Symbol.iterator]

## Usage

```python
from components.object_methods.src.object_methods import ObjectMethods
from components.object_runtime.src.js_object import JSObject

# Object.fromEntries
entries = [["a", 1], ["b", 2]]
obj = ObjectMethods.from_entries(entries)

# Object.entries
obj_dict = {"x": 10, "y": 20}
pairs = ObjectMethods.entries(obj_dict)  # [["x", 10], ["y", 20]]

# Object.values
values = ObjectMethods.values(obj_dict)  # [10, 20]

# Object.is
ObjectMethods.is_equal(+0, -0)  # False
ObjectMethods.is_equal(NaN, NaN)  # True
```

## Architecture

### Components

- `ObjectMethods` - Static methods (entries, values, fromEntries, etc.)
- `ObjectIteration` - Iterator support for objects
- Property descriptor handling
- SameValue equality implementation

### Performance

- Property enumeration: O(n) time complexity
- Target: <1ms for <1000 properties
- Efficient key/value extraction

## Testing

**Coverage Target:** ≥85%
**Test Types:**
- Unit tests (40+ tests)
- Integration tests with object_runtime
- Test262 compliance tests (~200 tests)
- Edge case tests

```bash
# Run tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html --cov-fail-under=85

# Run integration tests
pytest tests/integration/ -v
```

## Development

Built using TDD methodology:
1. **RED:** Write failing tests
2. **GREEN:** Implement minimal code
3. **REFACTOR:** Optimize and clean

See contract at `/contracts/object_methods.yaml` for API specification.
