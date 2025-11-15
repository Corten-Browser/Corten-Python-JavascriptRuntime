"""
Unit tests for x64 backend instruction emission.

Tests x64Backend class for correctness of machine code generation.
"""

import pytest
from components.baseline_jit.src import x64Backend, Register


class TestX64BackendMOV:
    """Test MOV instruction emission."""

    def test_emit_mov_register_to_register(self):
        """
        Given two registers
        When emitting MOV dest, src
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_mov(Register.RAX, Register.RBX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 3  # REX + opcode + ModR/M
        assert code[0] == 0x48  # REX.W prefix
        assert code[1] == 0x89  # MOV opcode
        # ModR/M: mod=11, reg=RBX(3), rm=RAX(0) = 11_011_000 = 0xD8
        assert code[2] == 0xD8

    def test_emit_mov_immediate_to_register(self):
        """
        Given a register and immediate value
        When emitting MOV dest, imm
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_mov(Register.RAX, 42)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 7  # REX + opcode + ModR/M + imm32
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0xC7  # MOV r/m64, imm32
        assert code[2] == 0xC0  # ModR/M for RAX

    def test_emit_mov_different_registers(self):
        """
        Given various register pairs
        When emitting MOV for each pair
        Then each should generate valid code
        """
        # Given
        backend = x64Backend()
        pairs = [
            (Register.RCX, Register.RDX),
            (Register.RSI, Register.RDI),
            (Register.R8, Register.R9),
        ]

        # When/Then
        for dest, src in pairs:
            code = backend.emit_mov(dest, src)
            assert len(code) == 3
            assert code[0] == 0x48  # REX.W


class TestX64BackendADD:
    """Test ADD instruction emission."""

    def test_emit_add_register_to_register(self):
        """
        Given two registers
        When emitting ADD dest, src
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_add(Register.RAX, Register.RBX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 3
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0x01  # ADD opcode

    def test_emit_add_immediate_to_register(self):
        """
        Given a register and immediate value
        When emitting ADD dest, imm
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_add(Register.RAX, 100)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 7  # REX + opcode + ModR/M + imm32
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0x81  # ADD r/m64, imm32


class TestX64BackendSUB:
    """Test SUB instruction emission."""

    def test_emit_sub_register_to_register(self):
        """
        Given two registers
        When emitting SUB dest, src
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_sub(Register.RAX, Register.RBX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 3
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0x29  # SUB opcode

    def test_emit_sub_immediate_to_register(self):
        """
        Given a register and immediate value
        When emitting SUB dest, imm
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_sub(Register.RAX, 50)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 7  # REX + opcode + ModR/M + imm32
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0x81  # SUB r/m64, imm32


class TestX64BackendMUL:
    """Test IMUL instruction emission."""

    def test_emit_mul_register_to_register(self):
        """
        Given two registers
        When emitting IMUL dest, src
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_mul(Register.RAX, Register.RBX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 4  # REX + 0x0F + opcode + ModR/M
        assert code[0] == 0x48  # REX.W
        assert code[1] == 0x0F  # Two-byte opcode prefix
        assert code[2] == 0xAF  # IMUL opcode


class TestX64BackendControlFlow:
    """Test control flow instructions (CALL, RET)."""

    def test_emit_call(self):
        """
        Given a relative call target
        When emitting CALL instruction
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()
        target = 100  # Relative offset

        # When
        code = backend.emit_call(target)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 5  # opcode + rel32
        assert code[0] == 0xE8  # CALL rel32

    def test_emit_ret(self):
        """
        When emitting RET instruction
        Then correct x64 machine code should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_ret()

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 1
        assert code[0] == 0xC3  # RET


class TestX64BackendStackOps:
    """Test stack operations (PUSH, POP)."""

    def test_emit_push_low_register(self):
        """
        Given a low register (RAX-RDI)
        When emitting PUSH
        Then single-byte opcode should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_push(Register.RAX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 1  # No REX needed for low registers
        assert code[0] == 0x50  # PUSH RAX

    def test_emit_push_high_register(self):
        """
        Given a high register (R8-R15)
        When emitting PUSH
        Then REX prefix should be included
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_push(Register.R8)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 2  # REX + opcode
        assert code[0] == 0x41  # REX.B

    def test_emit_pop_low_register(self):
        """
        Given a low register
        When emitting POP
        Then single-byte opcode should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_pop(Register.RAX)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 1
        assert code[0] == 0x58  # POP RAX

    def test_emit_pop_high_register(self):
        """
        Given a high register
        When emitting POP
        Then REX prefix should be included
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_pop(Register.R8)

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 2  # REX + opcode
        assert code[0] == 0x41  # REX.B


class TestX64BackendNOP:
    """Test NOP instruction emission."""

    def test_emit_nop(self):
        """
        When emitting NOP instruction
        Then single 0x90 byte should be generated
        """
        # Given
        backend = x64Backend()

        # When
        code = backend.emit_nop()

        # Then
        assert isinstance(code, bytes)
        assert len(code) == 1
        assert code[0] == 0x90  # NOP


class TestX64BackendCodeSequences:
    """Test emission of code sequences."""

    def test_emit_multiple_instructions(self):
        """
        Given a backend
        When emitting multiple instructions
        Then each should produce correct code
        """
        # Given
        backend = x64Backend()

        # When - emit a simple function prologue
        push_rbp = backend.emit_push(Register.RBP)
        mov_rbp_rsp = backend.emit_mov(Register.RBP, Register.RSP)
        sub_rsp = backend.emit_sub(Register.RSP, 32)

        # Then
        assert len(push_rbp) > 0
        assert len(mov_rbp_rsp) > 0
        assert len(sub_rsp) > 0

        # Total code size
        total_size = len(push_rbp) + len(mov_rbp_rsp) + len(sub_rsp)
        assert total_size > 0

    def test_emit_arithmetic_sequence(self):
        """
        Given a backend
        When emitting arithmetic operations
        Then all operations should work correctly
        """
        # Given
        backend = x64Backend()

        # When
        mov = backend.emit_mov(Register.RAX, 10)
        add = backend.emit_add(Register.RAX, 20)
        sub = backend.emit_sub(Register.RAX, 5)
        mul = backend.emit_mul(Register.RAX, Register.RBX)

        # Then
        assert len(mov) == 7
        assert len(add) == 7
        assert len(sub) == 7
        assert len(mul) == 4
