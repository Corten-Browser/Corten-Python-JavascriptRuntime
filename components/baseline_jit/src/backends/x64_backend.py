"""
x64 backend for baseline JIT compiler.

Provides x64-specific machine code generation including:
- Register enumeration
- Instruction emission (MOV, ADD, SUB, CALL, RET, etc.)
- Calling conventions (System V ABI for Linux/macOS)
"""

from enum import Enum
from typing import Union


class Register(Enum):
    """
    x64 general-purpose registers.

    Enum values correspond to register encoding in x64 instruction format.
    """
    RAX = 0  # Accumulator, return value
    RCX = 1  # Counter (4th argument in Windows)
    RDX = 2  # Data (3rd argument in Windows)
    RBX = 3  # Base
    RSP = 4  # Stack pointer (not allocatable)
    RBP = 5  # Base pointer (frame pointer)
    RSI = 6  # Source index (2nd argument in Unix)
    RDI = 7  # Destination index (1st argument in Unix)
    R8 = 8   # 5th argument
    R9 = 9   # 6th argument
    R10 = 10  # Temporary
    R11 = 11  # Temporary
    R12 = 12  # Saved
    R13 = 13  # Saved
    R14 = 14  # Saved
    R15 = 15  # Saved


class x64Backend:
    """
    x64 machine code generation backend.

    Generates x64 machine code for bytecode operations.
    Implements System V ABI calling convention (Linux/macOS).
    """

    def __init__(self):
        """Initialize x64 backend."""
        self.code = bytearray()

    def emit_mov(self, dest: Register, src: Union[Register, int]) -> bytes:
        """
        Emit MOV instruction.

        Generates machine code for MOV dest, src instruction.

        Args:
            dest: Destination register
            src: Source register or immediate value

        Returns:
            Machine code bytes for MOV instruction

        Example:
            >>> backend = x64Backend()
            >>> code = backend.emit_mov(Register.RAX, Register.RBX)
            >>> len(code) > 0
            True
        """
        if isinstance(src, Register):
            # MOV dest, src (register to register)
            # REX.W prefix + opcode + ModR/M
            rex = 0x48  # REX.W (64-bit operand)
            opcode = 0x89  # MOV r/m64, r64
            modrm = 0xC0 | (src.value << 3) | dest.value  # mod=11 (register mode)

            return bytes([rex, opcode, modrm])
        else:
            # MOV dest, imm32 (immediate to register)
            # REX.W prefix + opcode + immediate
            rex = 0x48  # REX.W
            opcode = 0xC7  # MOV r/m64, imm32
            modrm = 0xC0 | dest.value  # mod=11, reg=000

            # Sign-extend 32-bit immediate to 64-bit
            imm = src & 0xFFFFFFFF
            imm_bytes = imm.to_bytes(4, byteorder='little', signed=True)

            return bytes([rex, opcode, modrm]) + imm_bytes

    def emit_add(self, dest: Register, src: Union[Register, int]) -> bytes:
        """
        Emit ADD instruction.

        Args:
            dest: Destination register (also first operand)
            src: Source register or immediate value

        Returns:
            Machine code bytes for ADD instruction
        """
        if isinstance(src, Register):
            # ADD dest, src (register to register)
            rex = 0x48  # REX.W
            opcode = 0x01  # ADD r/m64, r64
            modrm = 0xC0 | (src.value << 3) | dest.value

            return bytes([rex, opcode, modrm])
        else:
            # ADD dest, imm32
            rex = 0x48  # REX.W
            opcode = 0x81  # ADD r/m64, imm32
            modrm = 0xC0 | dest.value  # reg=000 for ADD

            imm = src & 0xFFFFFFFF
            imm_bytes = imm.to_bytes(4, byteorder='little', signed=True)

            return bytes([rex, opcode, modrm]) + imm_bytes

    def emit_sub(self, dest: Register, src: Union[Register, int]) -> bytes:
        """
        Emit SUB instruction.

        Args:
            dest: Destination register
            src: Source register or immediate value

        Returns:
            Machine code bytes for SUB instruction
        """
        if isinstance(src, Register):
            # SUB dest, src (register to register)
            rex = 0x48  # REX.W
            opcode = 0x29  # SUB r/m64, r64
            modrm = 0xC0 | (src.value << 3) | dest.value

            return bytes([rex, opcode, modrm])
        else:
            # SUB dest, imm32
            rex = 0x48  # REX.W
            opcode = 0x81  # SUB r/m64, imm32
            modrm = 0xE8 | dest.value  # reg=101 for SUB

            imm = src & 0xFFFFFFFF
            imm_bytes = imm.to_bytes(4, byteorder='little', signed=True)

            return bytes([rex, opcode, modrm]) + imm_bytes

    def emit_mul(self, dest: Register, src: Register) -> bytes:
        """
        Emit IMUL instruction (signed multiply).

        Args:
            dest: Destination register
            src: Source register

        Returns:
            Machine code bytes for IMUL instruction
        """
        # IMUL dest, src (two-operand form)
        rex = 0x48  # REX.W
        opcode1 = 0x0F  # Two-byte opcode prefix
        opcode2 = 0xAF  # IMUL r64, r/m64
        modrm = 0xC0 | (dest.value << 3) | src.value

        return bytes([rex, opcode1, opcode2, modrm])

    def emit_call(self, target: int) -> bytes:
        """
        Emit CALL instruction.

        Generates relative call instruction. Target is relative offset.

        Args:
            target: Relative call target offset (signed 32-bit)

        Returns:
            Machine code bytes for CALL instruction
        """
        # CALL rel32
        opcode = 0xE8
        offset = target & 0xFFFFFFFF
        offset_bytes = offset.to_bytes(4, byteorder='little', signed=True)

        return bytes([opcode]) + offset_bytes

    def emit_ret(self) -> bytes:
        """
        Emit RET instruction.

        Returns:
            Machine code bytes for RET instruction
        """
        # RET (near return)
        return bytes([0xC3])

    def emit_push(self, reg: Register) -> bytes:
        """
        Emit PUSH instruction.

        Args:
            reg: Register to push

        Returns:
            Machine code bytes for PUSH instruction
        """
        # PUSH r64
        if reg.value >= 8:
            # Need REX prefix for R8-R15
            rex = 0x41  # REX.B
            opcode = 0x50 | (reg.value - 8)
            return bytes([rex, opcode])
        else:
            opcode = 0x50 | reg.value
            return bytes([opcode])

    def emit_pop(self, reg: Register) -> bytes:
        """
        Emit POP instruction.

        Args:
            reg: Register to pop

        Returns:
            Machine code bytes for POP instruction
        """
        # POP r64
        if reg.value >= 8:
            # Need REX prefix for R8-R15
            rex = 0x41  # REX.B
            opcode = 0x58 | (reg.value - 8)
            return bytes([rex, opcode])
        else:
            opcode = 0x58 | reg.value
            return bytes([opcode])

    def emit_nop(self) -> bytes:
        """
        Emit NOP instruction.

        Returns:
            Machine code bytes for NOP instruction
        """
        return bytes([0x90])
