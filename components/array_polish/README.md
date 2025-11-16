# Array Polish - ES2024 Wave D

**Component Type**: Core
**Language**: Python
**Version**: 0.1.0

## Responsibility

Complete Array/TypedArray edge case handling for ES2024 compliance. Provides robust implementations of array methods with comprehensive edge case coverage for empty arrays, sparse arrays, boundary conditions, and iteration edge cases.

## Requirements Implemented

- **FR-ES24-D-010**: Array method edge cases (empty, sparse)
- **FR-ES24-D-011**: TypedArray boundary conditions
- **FR-ES24-D-012**: Array.prototype.at() edge cases
- **FR-ES24-D-013**: Array.prototype.findLast/findLastIndex edge cases
- **FR-ES24-D-014**: Array iteration edge cases

## Structure

```
├── src/
│   ├── __init__.py
│   ├── edge_cases.py          # Main ArrayEdgeCases class
│   ├── sparse_handling.py     # Sparse array utilities
│   └── typed_array.py         # TypedArray boundary handling
├── tests/
│   ├── unit/
│   └── integration/
└── README.md
```

## Key Features

- **Array.prototype.at()** - Comprehensive edge case handling with negative indices
- **Array.prototype.findLast()** - Search from end with predicate
- **Array.prototype.findLastIndex()** - Find last matching index
- **Sparse Array Handling** - Multiple modes (remove, preserve, explicit undefined)
- **Edge Case Detection** - Analyze arrays for special values and conditions
- **TypedArray Support** - All TypedArray types with boundary handling

## Performance Targets

- All operations: <1ms for arrays <10K elements
- at(): O(1) complexity
- find_last/find_last_index: O(n) complexity
- handle_sparse: O(n) complexity

## Usage

```python
from components.array_polish.src.edge_cases import ArrayEdgeCases

ec = ArrayEdgeCases()

# Array.prototype.at() with negative indices
result = ec.at([1, 2, 3], -1)  # Returns 3

# findLast with predicate
result = ec.find_last([1, 2, 3, 2, 1], lambda x, i, a: x == 2)  # Returns 2 (last occurrence)

# Handle sparse arrays
result = ec.handle_sparse([1, None, 3], mode='remove_holes')  # Returns [1, 3]

# Detect edge cases
info = ec.detect_edge_cases([1, float('nan'), float('-0'), float('inf')])
# Returns EdgeCaseInfo with flags
```

## Development

See contract at `/contracts/array_polish.yaml` for complete API specification.
