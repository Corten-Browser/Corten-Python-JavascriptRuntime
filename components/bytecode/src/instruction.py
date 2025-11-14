"""
Bytecode instruction representation.

This module defines the Instruction dataclass which represents a single
bytecode instruction with an opcode and optional operands.

Public API:
    - Instruction: Dataclass representing a bytecode instruction
"""

from dataclasses import dataclass
from typing import Optional

from .opcode import Opcode
from components.shared_types.src.location import SourceLocation


@dataclass
class Instruction:
    """
    Single bytecode instruction.

    Represents one bytecode instruction with an opcode and up to three operands.
    Operands typically represent register indices, constant pool indices,
    or jump offsets depending on the opcode.

    Attributes:
        opcode: The operation code
        operand1: First operand (optional)
        operand2: Second operand (optional)
        operand3: Third operand (optional)
        location: Source code location for debugging (optional)

    Example:
        >>> from components.bytecode.src.opcode import Opcode
        >>> instr = Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=0)
        >>> instr.opcode == Opcode.LOAD_CONSTANT
        True
        >>> instr.operand1
        0
    """

    opcode: Opcode
    operand1: Optional[int] = None
    operand2: Optional[int] = None
    operand3: Optional[int] = None
    location: Optional[SourceLocation] = None

    def __repr__(self) -> str:
        """Return string representation of instruction."""
        parts = [f"Instruction(opcode={self.opcode.name}"]

        if self.operand1 is not None:
            parts.append(f", operand1={self.operand1}")
        if self.operand2 is not None:
            parts.append(f", operand2={self.operand2}")
        if self.operand3 is not None:
            parts.append(f", operand3={self.operand3}")
        if self.location is not None:
            parts.append(f", location={self.location}")

        return "".join(parts) + ")"
