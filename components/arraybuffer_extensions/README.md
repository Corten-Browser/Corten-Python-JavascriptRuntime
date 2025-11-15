# ArrayBuffer Extensions

**Type**: feature
**Tech Stack**: Python
**Version**: 0.1.0

## Responsibility

Implements ES2024 ArrayBuffer and TypedArray extensions including transfer operations, resizable buffers, and non-mutating TypedArray methods.

## Features

- ArrayBuffer.prototype.transfer() - Transfer ownership with optional resize
- ArrayBuffer.prototype.transferToFixedLength() - Transfer to fixed-length buffer
- ArrayBuffer.prototype.detached getter - Check detachment status
- ArrayBuffer.prototype.maxByteLength getter - Get maximum size for resizable buffers
- ResizableArrayBuffer - Dynamic buffer sizing
- GrowableSharedArrayBuffer - Thread-safe growable buffers
- TypedArray.prototype.toReversed() - Non-mutating reverse
- TypedArray.prototype.toSorted() - Non-mutating sort

## Structure

```
├── src/                          # Source code
│   ├── __init__.py              # Package exports
│   ├── arraybuffer_extensions.py # ArrayBuffer extensions
│   ├── resizable_buffer.py       # ResizableArrayBuffer implementation
│   ├── growable_shared_buffer.py # GrowableSharedArrayBuffer
│   └── typedarray_extensions.py  # TypedArray extensions
├── tests/                        # Tests
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
└── README.md                     # This file
```

## Requirements Implemented

- FR-ES24-001: ArrayBuffer.prototype.transfer()
- FR-ES24-002: ArrayBuffer.prototype.transferToFixedLength()
- FR-ES24-003: ArrayBuffer.prototype.detached getter
- FR-ES24-004: ArrayBuffer.prototype.maxByteLength getter
- FR-ES24-005: Resizable ArrayBuffer support
- FR-ES24-006: GrowableSharedArrayBuffer
- FR-ES24-007: TypedArray.prototype.toReversed()
- FR-ES24-008: TypedArray.prototype.toSorted()

## Usage

```python
from components.arraybuffer_extensions import (
    ArrayBufferExtensions,
    ResizableArrayBuffer,
    GrowableSharedArrayBuffer,
    TypedArrayExtensions
)

# Transfer buffer
ext = ArrayBufferExtensions()
new_buffer = ext.transfer(original_buffer, new_byte_length=1024)

# Resizable buffer
resizable = ResizableArrayBuffer(byte_length=512, max_byte_length=2048)
resizable.resize(1024)

# Non-mutating TypedArray operations
typed_ext = TypedArrayExtensions()
reversed_array = typed_ext.to_reversed(original_array)
sorted_array = typed_ext.to_sorted(original_array)
```

## Development

See component contract at `contracts/arraybuffer_extensions.yaml` for complete API specification.

## Testing

- Run tests: `pytest tests/`
- Coverage: `pytest --cov=src --cov-report=term-missing tests/`
- Target: ≥80% coverage, 100% pass rate
