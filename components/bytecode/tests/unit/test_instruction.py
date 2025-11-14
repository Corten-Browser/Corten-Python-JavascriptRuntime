"""
Tests for Instruction dataclass.

These tests verify the Instruction dataclass correctly stores bytecode instructions
with opcodes and operands.
"""

import pytest


def test_instruction_imports():
    """Test that Instruction can be imported."""
    from components.bytecode.src.instruction import Instruction

    assert Instruction is not None


def test_instruction_creation_with_opcode_only():
    """Test creating instruction with only an opcode."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr = Instruction(opcode=Opcode.RETURN)

    assert instr.opcode == Opcode.RETURN
    assert instr.operand1 is None
    assert instr.operand2 is None
    assert instr.operand3 is None
    assert instr.location is None


def test_instruction_creation_with_one_operand():
    """Test creating instruction with one operand."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr = Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=0)

    assert instr.opcode == Opcode.LOAD_CONSTANT
    assert instr.operand1 == 0
    assert instr.operand2 is None
    assert instr.operand3 is None


def test_instruction_creation_with_two_operands():
    """Test creating instruction with two operands."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr = Instruction(opcode=Opcode.LOAD_LOCAL, operand1=5, operand2=10)

    assert instr.opcode == Opcode.LOAD_LOCAL
    assert instr.operand1 == 5
    assert instr.operand2 == 10
    assert instr.operand3 is None


def test_instruction_creation_with_three_operands():
    """Test creating instruction with three operands."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr = Instruction(
        opcode=Opcode.STORE_PROPERTY, operand1=1, operand2=2, operand3=3
    )

    assert instr.opcode == Opcode.STORE_PROPERTY
    assert instr.operand1 == 1
    assert instr.operand2 == 2
    assert instr.operand3 == 3


def test_instruction_with_source_location():
    """Test creating instruction with source location."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction
    from components.shared_types.src.location import SourceLocation

    location = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    instr = Instruction(opcode=Opcode.ADD, location=location)

    assert instr.opcode == Opcode.ADD
    assert instr.location == location
    assert instr.location.filename == "test.js"
    assert instr.location.line == 1
    assert instr.location.column == 1


def test_instruction_is_dataclass():
    """Test that Instruction is a dataclass."""
    from dataclasses import is_dataclass
    from components.bytecode.src.instruction import Instruction

    assert is_dataclass(Instruction)


def test_instruction_repr():
    """Test instruction string representation."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr = Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=42)
    repr_str = repr(instr)

    assert "Instruction" in repr_str
    assert "LOAD_CONSTANT" in repr_str


def test_instruction_equality():
    """Test that two instructions with same values are equal."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr1 = Instruction(opcode=Opcode.ADD, operand1=1)
    instr2 = Instruction(opcode=Opcode.ADD, operand1=1)

    assert instr1 == instr2


def test_instruction_inequality():
    """Test that two instructions with different values are not equal."""
    from components.bytecode.src.opcode import Opcode
    from components.bytecode.src.instruction import Instruction

    instr1 = Instruction(opcode=Opcode.ADD, operand1=1)
    instr2 = Instruction(opcode=Opcode.SUBTRACT, operand1=1)

    assert instr1 != instr2
