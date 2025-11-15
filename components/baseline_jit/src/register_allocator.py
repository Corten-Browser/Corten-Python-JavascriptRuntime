"""
Linear scan register allocator.

Implements simple linear scan algorithm for fast register allocation.
Spills to stack when registers are exhausted.
"""

from typing import Dict, List, Tuple
from components.baseline_jit.src.backends.x64_backend import Register


class RegisterAllocator:
    """
    Linear scan register allocator.

    Allocates registers for bytecode values using linear scan algorithm.
    Complexity: O(n) where n is number of values.

    Algorithm:
        1. Compute live ranges for each value
        2. Sort ranges by start point
        3. For each range:
           - Find free register
           - If available: assign register
           - If not: spill to stack
        4. Return assignments and spills
    """

    # Allocatable registers (excluding RSP, RBP which are reserved)
    ALLOCATABLE_REGISTERS = [
        Register.RAX,
        Register.RBX,
        Register.RCX,
        Register.RDX,
        Register.RSI,
        Register.RDI,
        Register.R8,
        Register.R9,
        Register.R10,
        Register.R11,
        Register.R12,
        Register.R13,
        Register.R14,
        Register.R15,
    ]

    def __init__(self):
        """Initialize register allocator."""
        pass

    def allocate(self, bytecode):
        """
        Allocate registers for bytecode values.

        Uses linear scan algorithm for fast allocation.

        Args:
            bytecode: BytecodeArray to allocate registers for

        Returns:
            RegisterAllocation with register assignments and spills

        Example:
            >>> allocator = RegisterAllocator()
            >>> allocation = allocator.allocate(bytecode)
            >>> allocation.assignments.get(0)  # Register for value 0
            Register.RAX
        """
        # Import here to avoid circular dependency
        from components.baseline_jit.src.jit_compiler import RegisterAllocation

        if not bytecode.instructions:
            # Empty bytecode
            return RegisterAllocation(assignments={}, spills=[])

        # Compute live ranges
        live_ranges = self._compute_live_ranges(bytecode)

        # Sort by start point for linear scan
        sorted_ranges = sorted(live_ranges.items(), key=lambda x: x[1][0])

        # Allocate registers
        assignments: Dict[int, Register] = {}
        spills: List[int] = []
        active: List[Tuple[int, int, Register]] = []  # (value_id, end, reg)

        for value_id, (start, end) in sorted_ranges:
            # Remove expired ranges from active list
            active = [(v, e, r) for v, e, r in active if e > start]

            # Try to find free register
            used_registers = {reg for _, _, reg in active}
            free_registers = [r for r in self.ALLOCATABLE_REGISTERS
                              if r not in used_registers]

            if free_registers:
                # Assign first free register
                reg = free_registers[0]
                assignments[value_id] = reg
                active.append((value_id, end, reg))
            else:
                # No free register - spill to stack
                spills.append(value_id)

        # Import here to avoid circular dependency (already imported above)
        from components.baseline_jit.src.jit_compiler import RegisterAllocation
        return RegisterAllocation(assignments=assignments, spills=spills)

    def _compute_live_ranges(self, bytecode) -> Dict[int, Tuple[int, int]]:
        """
        Compute live ranges for bytecode values.

        A value is live from its definition to its last use.

        Args:
            bytecode: BytecodeArray to analyze

        Returns:
            Dict mapping value_id to (start_pc, end_pc) tuple

        Time Complexity: O(n) where n is number of instructions
        """
        live_ranges: Dict[int, Tuple[int, int]] = {}

        # Track value definitions and uses
        definitions: Dict[int, int] = {}  # value_id -> pc where defined
        uses: Dict[int, List[int]] = {}    # value_id -> [pc where used]

        # Simple heuristic: each instruction produces value with index = pc
        # Values are used by subsequent instructions
        for pc, instruction in enumerate(bytecode.instructions):
            # Define value at this pc
            definitions[pc] = pc

            # Track uses (simplified - in real impl would parse operands)
            # For now, assume instruction uses previous values
            if pc > 0:
                # Use previous value
                if pc - 1 not in uses:
                    uses[pc - 1] = []
                uses[pc - 1].append(pc)

        # Compute live ranges
        for value_id in definitions:
            start = definitions[value_id]
            # End is last use, or start if no uses
            end = max(uses.get(value_id, [start]) + [start])
            live_ranges[value_id] = (start, end)

        return live_ranges
