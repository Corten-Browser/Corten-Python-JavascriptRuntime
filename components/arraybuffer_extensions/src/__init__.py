"""
ArrayBuffer Extensions Component
ES2024 ArrayBuffer and TypedArray extensions

Exports:
    - ArrayBufferExtensions: Transfer and buffer status operations
    - ResizableArrayBuffer: Dynamic buffer sizing
    - GrowableSharedArrayBuffer: Thread-safe growable buffers
    - TypedArrayExtensions: Non-mutating TypedArray operations
"""

from .arraybuffer_extensions import ArrayBufferExtensions
from .resizable_buffer import ResizableArrayBuffer
from .growable_shared_buffer import GrowableSharedArrayBuffer
from .typedarray_extensions import TypedArrayExtensions

__all__ = [
    'ArrayBufferExtensions',
    'ResizableArrayBuffer',
    'GrowableSharedArrayBuffer',
    'TypedArrayExtensions',
]

__version__ = '0.1.0'
