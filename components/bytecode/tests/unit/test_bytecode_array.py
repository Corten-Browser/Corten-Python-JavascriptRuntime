"""
Tests for BytecodeArray class.

These tests verify the BytecodeArray class correctly manages bytecode instructions,
constant pool, and local variables.
"""

import pytest


def test_bytecode_array_imports():
    """Test that BytecodeArray can be imported."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    assert BytecodeArray is not None


def test_bytecode_array_creation():
    """Test creating an empty BytecodeArray."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray()

    assert bytecode.instructions == []
    assert bytecode.constant_pool == []
    assert bytecode.local_count == 0
    assert bytecode.parameter_count == 0


def test_bytecode_array_add_instruction():
    """Test adding an instruction to BytecodeArray."""
    from components.bytecode.src.bytecode_array import BytecodeArray
    from components.bytecode.src.instruction import Instruction
    from components.bytecode.src.opcode import Opcode

    bytecode = BytecodeArray()
    instr = Instruction(opcode=Opcode.RETURN)

    index = bytecode.add_instruction(instr)

    assert index == 0
    assert len(bytecode.instructions) == 1
    assert bytecode.instructions[0] == instr


def test_bytecode_array_add_multiple_instructions():
    """Test adding multiple instructions returns correct indices."""
    from components.bytecode.src.bytecode_array import BytecodeArray
    from components.bytecode.src.instruction import Instruction
    from components.bytecode.src.opcode import Opcode

    bytecode = BytecodeArray()

    idx0 = bytecode.add_instruction(
        Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=0)
    )
    idx1 = bytecode.add_instruction(
        Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=1)
    )
    idx2 = bytecode.add_instruction(Instruction(opcode=Opcode.ADD))

    assert idx0 == 0
    assert idx1 == 1
    assert idx2 == 2
    assert len(bytecode.instructions) == 3


def test_bytecode_array_add_constant():
    """Test adding a constant to constant pool."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray()

    index = bytecode.add_constant(42)

    assert index == 0
    assert len(bytecode.constant_pool) == 1
    assert bytecode.constant_pool[0] == 42


def test_bytecode_array_add_multiple_constants():
    """Test adding multiple constants returns correct indices."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray()

    idx0 = bytecode.add_constant("hello")
    idx1 = bytecode.add_constant(3.14)
    idx2 = bytecode.add_constant(True)

    assert idx0 == 0
    assert idx1 == 1
    assert idx2 == 2
    assert bytecode.constant_pool == ["hello", 3.14, True]


def test_bytecode_array_get_instruction():
    """Test retrieving an instruction by index."""
    from components.bytecode.src.bytecode_array import BytecodeArray
    from components.bytecode.src.instruction import Instruction
    from components.bytecode.src.opcode import Opcode

    bytecode = BytecodeArray()
    instr = Instruction(opcode=Opcode.RETURN)
    bytecode.add_instruction(instr)

    retrieved = bytecode.get_instruction(0)

    assert retrieved == instr


def test_bytecode_array_get_instruction_out_of_bounds():
    """Test that getting instruction with invalid index raises error."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray()

    with pytest.raises(IndexError):
        bytecode.get_instruction(0)


def test_bytecode_array_patch_jump():
    """Test patching jump instruction with target index."""
    from components.bytecode.src.bytecode_array import BytecodeArray
    from components.bytecode.src.instruction import Instruction
    from components.bytecode.src.opcode import Opcode

    bytecode = BytecodeArray()

    # Add jump instruction with placeholder operand
    jump_idx = bytecode.add_instruction(Instruction(opcode=Opcode.JUMP, operand1=9999))

    # Add some more instructions
    bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=0))
    target_idx = bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))

    # Patch the jump to point to return instruction
    bytecode.patch_jump(jump_idx, target_idx)

    # Verify jump was patched
    patched_instr = bytecode.get_instruction(jump_idx)
    assert patched_instr.opcode == Opcode.JUMP
    assert patched_instr.operand1 == target_idx


def test_bytecode_array_with_locals_and_parameters():
    """Test BytecodeArray with local variables and parameters."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray(local_count=5, parameter_count=2)

    assert bytecode.local_count == 5
    assert bytecode.parameter_count == 2


def test_bytecode_array_constant_pool_can_store_any_values():
    """Test that constant pool can store various Python types."""
    from components.bytecode.src.bytecode_array import BytecodeArray

    bytecode = BytecodeArray()

    bytecode.add_constant(None)
    bytecode.add_constant(42)
    bytecode.add_constant(3.14)
    bytecode.add_constant("string")
    bytecode.add_constant([1, 2, 3])
    bytecode.add_constant({"key": "value"})

    assert len(bytecode.constant_pool) == 6
    assert bytecode.constant_pool[0] is None
    assert bytecode.constant_pool[1] == 42
    assert bytecode.constant_pool[2] == 3.14
    assert bytecode.constant_pool[3] == "string"
    assert bytecode.constant_pool[4] == [1, 2, 3]
    assert bytecode.constant_pool[5] == {"key": "value"}
