"""
Baseline JIT compiler - main compiler implementation.

Provides:
- BaselineJITCompiler: Main JIT compiler class
- CompiledCode: Compiled machine code data structure
- RegisterAllocation: Register allocation results
- OSREntry: OSR entry point information
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from components.baseline_jit.src.backends.x64_backend import Register, x64Backend
from components.baseline_jit.src.register_allocator import RegisterAllocator
from components.baseline_jit.src.code_generator import CodeGenerator


@dataclass
class CompiledCode:
    """
    Compiled machine code with metadata.

    Attributes:
        code: Machine code bytes
        entry_point: Entry point address
        size: Code size in bytes
        deopt_info: Deoptimization metadata (optional)
        ic_sites: Inline cache sites in code
    """
    code: bytes
    entry_point: int
    size: int
    deopt_info: Optional[Any]
    ic_sites: List[Dict[str, Any]]


@dataclass
class RegisterAllocation:
    """
    Register allocation results from linear scan allocator.

    Attributes:
        assignments: Map from bytecode value ID to assigned register
        spills: List of bytecode value IDs spilled to stack
    """
    assignments: Dict[int, Register]
    spills: List[int]


@dataclass
class OSREntry:
    """
    On-stack replacement entry point.

    Allows tier-up from interpreter to JIT code during execution.

    Attributes:
        bytecode_offset: Bytecode offset for OSR
        compiled_offset: Compiled code offset
        state_map: Interpreter state mapping
    """
    bytecode_offset: int
    compiled_offset: int
    state_map: Dict[str, Any]


class BaselineJITCompiler:
    """
    Baseline JIT compiler.

    Compiles bytecode to machine code with simple optimizations.
    Implements tier-up from interpreter for hot functions.

    Target: 5-10x speedup over interpreter
    Compilation latency: <100ms
    """

    # Tier-up threshold: compile after this many calls
    TIER_UP_THRESHOLD = 1000

    def __init__(self, backend: str = "x64"):
        """
        Initialize baseline JIT compiler.

        Args:
            backend: Platform backend ("x64" or "arm64")
        """
        self.backend_name = backend
        self._call_counts: Dict[int, int] = {}  # function_id -> call count

        # Initialize backend
        if backend == "x64":
            self._backend = x64Backend()
        else:
            raise ValueError(f"Unsupported backend: {backend}")

        # Initialize sub-components
        self._allocator = RegisterAllocator()
        self._code_generator = CodeGenerator(self._backend)

    def should_compile(self, function_id: int, call_count: int) -> bool:
        """
        Determine if function should be JIT compiled.

        Tier-up decision based on call count threshold.

        Args:
            function_id: Function ID
            call_count: Number of times function has been called

        Returns:
            True if should tier-up to baseline JIT

        Example:
            >>> compiler = BaselineJITCompiler()
            >>> compiler.should_compile(1, 100)
            False
            >>> compiler.should_compile(1, 1500)
            True
        """
        return call_count >= self.TIER_UP_THRESHOLD

    def compile_function(self, bytecode, profiling_data=None) -> CompiledCode:
        """
        Compile bytecode to machine code.

        Full compilation pipeline:
        1. Register allocation (linear scan)
        2. Code generation (bytecode → machine code)
        3. IC site tracking
        4. Deopt info generation

        Args:
            bytecode: BytecodeArray to compile
            profiling_data: Optional profiling feedback

        Returns:
            CompiledCode with compiled machine code

        Example:
            >>> from components.bytecode.src import BytecodeArray
            >>> compiler = BaselineJITCompiler()
            >>> bytecode = BytecodeArray()
            >>> compiled = compiler.compile_function(bytecode)
            >>> compiled.size >= 0
            True
        """
        # Step 1: Register allocation
        allocation = self._allocator.allocate(bytecode)

        # Step 2: Code generation
        machine_code = self._code_generator.generate(bytecode, allocation)

        # Step 3: Create CompiledCode with metadata
        compiled = CompiledCode(
            code=machine_code,
            entry_point=0,  # Entry point is start of code
            size=len(machine_code),
            deopt_info=None,  # Would be populated in real implementation
            ic_sites=[]  # Would be populated with IC sites
        )

        return compiled
