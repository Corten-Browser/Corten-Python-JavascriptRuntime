"""
Bytecode array with constant pool and metadata.

This module defines the BytecodeArray class which holds compiled bytecode
instructions along with a constant pool and local variable information.

Public API:
    - BytecodeArray: Container for compiled bytecode
"""

from typing import List, Any

from .instruction import Instruction


class BytecodeArray:
    """
    Compiled bytecode with constant pool and metadata.

    This class represents the output of bytecode compilation. It contains
    the instruction sequence, constant pool, and information about local
    variables and function parameters.

    Attributes:
        instructions: List of bytecode instructions
        constant_pool: List of constant values
        local_count: Number of local variables
        parameter_count: Number of function parameters

    Example:
        >>> from components.bytecode.src.bytecode_array import BytecodeArray
        >>> from components.bytecode.src.instruction import Instruction
        >>> from components.bytecode.src.opcode import Opcode
        >>>
        >>> bytecode = BytecodeArray()
        >>> const_idx = bytecode.add_constant(42)
        >>> instr_idx = bytecode.add_instruction(
        ...     Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx)
        ... )
        >>> bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))
        >>> len(bytecode.instructions)
        2
    """

    def __init__(self, local_count: int = 0, parameter_count: int = 0):
        """
        Initialize BytecodeArray.

        Args:
            local_count: Number of local variables (default: 0)
            parameter_count: Number of function parameters (default: 0)
        """
        self.instructions: List[Instruction] = []
        self.constant_pool: List[Any] = []
        self.local_count = local_count
        self.parameter_count = parameter_count

    def add_instruction(self, instruction: Instruction) -> int:
        """
        Add instruction to bytecode array.

        Args:
            instruction: Instruction to add

        Returns:
            Index of added instruction

        Example:
            >>> bytecode = BytecodeArray()
            >>> from components.bytecode.src.instruction import Instruction
            >>> from components.bytecode.src.opcode import Opcode
            >>> idx = bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))
            >>> idx
            0
        """
        self.instructions.append(instruction)
        return len(self.instructions) - 1

    def add_constant(self, value: Any) -> int:
        """
        Add constant to constant pool.

        Args:
            value: Constant value to add (can be any Python type)

        Returns:
            Index of added constant in constant pool

        Example:
            >>> bytecode = BytecodeArray()
            >>> idx = bytecode.add_constant(42)
            >>> bytecode.constant_pool[idx]
            42
        """
        self.constant_pool.append(value)
        return len(self.constant_pool) - 1

    def get_instruction(self, index: int) -> Instruction:
        """
        Get instruction by index.

        Args:
            index: Instruction index

        Returns:
            Instruction at given index

        Raises:
            IndexError: If index is out of bounds

        Example:
            >>> bytecode = BytecodeArray()
            >>> from components.bytecode.src.instruction import Instruction
            >>> from components.bytecode.src.opcode import Opcode
            >>> bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))
            0
            >>> instr = bytecode.get_instruction(0)
            >>> instr.opcode.name
            'RETURN'
        """
        return self.instructions[index]

    def patch_jump(self, jump_index: int, target_index: int) -> None:
        """
        Patch jump instruction with target index.

        Updates a jump instruction's operand1 to point to the target instruction.
        This is used for forward references where the jump target isn't known
        at the time the jump instruction is emitted.

        Args:
            jump_index: Index of jump instruction to patch
            target_index: Target instruction index

        Example:
            >>> bytecode = BytecodeArray()
            >>> from components.bytecode.src.instruction import Instruction
            >>> from components.bytecode.src.opcode import Opcode
            >>>
            >>> # Emit jump with placeholder
            >>> jump_idx = bytecode.add_instruction(
            ...     Instruction(opcode=Opcode.JUMP, operand1=9999)
            ... )
            >>>
            >>> # Emit target instruction
            >>> target_idx = bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))
            >>>
            >>> # Patch jump to point to target
            >>> bytecode.patch_jump(jump_idx, target_idx)
            >>> bytecode.get_instruction(jump_idx).operand1 == target_idx
            True
        """
        jump_instr = self.instructions[jump_index]
        # Create new instruction with updated operand1
        patched_instr = Instruction(
            opcode=jump_instr.opcode,
            operand1=target_index,
            operand2=jump_instr.operand2,
            operand3=jump_instr.operand3,
            location=jump_instr.location,
        )
        self.instructions[jump_index] = patched_instr
