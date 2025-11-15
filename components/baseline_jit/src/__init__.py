"""
Baseline JIT - Fast JIT compiler for bytecode → machine code translation.

This module provides baseline JIT compilation infrastructure for 5-10x speedup
over interpreter execution through simple 1:1 bytecode-to-machine-code translation.

Public API:
    Classes:
        - BaselineJITCompiler: Main JIT compiler
        - CodeGenerator: Machine code generation
        - RegisterAllocator: Linear scan register allocation
        - OSRManager: On-stack replacement for tier-up
        - CodeCache: Compiled code caching
        - x64Backend: x64 machine code backend

    Enums:
        - Register: x64 register enumeration

    Data Structures:
        - CompiledCode: Compiled machine code with metadata
        - RegisterAllocation: Register assignment results
        - OSREntry: OSR entry point information

Example:
    >>> from components.baseline_jit.src import BaselineJITCompiler
    >>> compiler = BaselineJITCompiler(backend="x64")
    >>> compiled = compiler.compile_function(bytecode_array)
    >>> compiled.size
    1024
"""

# Export enums
from .backends.x64_backend import Register

# Export data structures
from .jit_compiler import CompiledCode, RegisterAllocation, OSREntry

# Export classes
from .jit_compiler import BaselineJITCompiler
from .code_generator import CodeGenerator
from .register_allocator import RegisterAllocator
from .osr import OSRManager
from .code_cache import CodeCache
from .backends.x64_backend import x64Backend

__all__ = [
    # Enums
    "Register",
    # Data structures
    "CompiledCode",
    "RegisterAllocation",
    "OSREntry",
    # Classes
    "BaselineJITCompiler",
    "CodeGenerator",
    "RegisterAllocator",
    "OSRManager",
    "CodeCache",
    "x64Backend",
]

__version__ = "0.1.0"
