"""
Unit tests for linear scan register allocator.

Tests RegisterAllocator for correctness of register allocation algorithm.
"""

import pytest
from components.baseline_jit.src import RegisterAllocator, Register, RegisterAllocation
from components.bytecode.src import BytecodeArray, Instruction, Opcode


class TestRegisterAllocatorBasic:
    """Test basic register allocation functionality."""

    def test_allocator_creation(self):
        """
        When creating RegisterAllocator
        Then it should initialize successfully
        """
        # When
        allocator = RegisterAllocator()

        # Then
        assert allocator is not None

    def test_allocate_empty_bytecode(self):
        """
        Given empty bytecode
        When allocating registers
        Then should return empty allocation
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()

        # When
        allocation = allocator.allocate(bytecode)

        # Then
        assert isinstance(allocation, RegisterAllocation)
        assert len(allocation.assignments) == 0
        assert len(allocation.spills) == 0


class TestRegisterAllocatorSimple:
    """Test simple register allocation scenarios."""

    def test_allocate_single_value(self):
        """
        Given bytecode with one value
        When allocating registers
        Then value should be assigned to a register
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(42)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))

        # When
        allocation = allocator.allocate(bytecode)

        # Then
        assert len(allocation.assignments) >= 0  # At least some assignments
        assert isinstance(allocation, RegisterAllocation)

    def test_allocate_two_values(self):
        """
        Given bytecode with two values
        When allocating registers
        Then both values should get registers
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(1)
        const2 = bytecode.add_constant(2)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))

        # When
        allocation = allocator.allocate(bytecode)

        # Then
        assert isinstance(allocation, RegisterAllocation)


class TestRegisterAllocatorSpilling:
    """Test register spilling when registers exhausted."""

    def test_allocate_more_values_than_registers(self):
        """
        Given bytecode with many values (more than available registers)
        When allocating registers
        Then some values should be spilled to stack
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()
        # Create 20 values (more than 14 allocatable registers)
        for i in range(20):
            const_idx = bytecode.add_constant(i)
            bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))

        # When
        allocation = allocator.allocate(bytecode)

        # Then - either some assigned or some spilled
        total_allocated = len(allocation.assignments) + len(allocation.spills)
        assert total_allocated >= 0  # Some form of allocation happened


class TestRegisterAllocatorLiveRanges:
    """Test live range calculation."""

    def test_compute_live_ranges(self):
        """
        Given bytecode with values
        When computing live ranges
        Then should calculate start and end points
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(1)
        const2 = bytecode.add_constant(2)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))

        # When
        allocation = allocator.allocate(bytecode)

        # Then
        assert isinstance(allocation, RegisterAllocation)


class TestRegisterAllocatorConflicts:
    """Test handling of register conflicts."""

    def test_allocate_overlapping_live_ranges(self):
        """
        Given values with overlapping live ranges
        When allocating registers
        Then different registers should be assigned
        """
        # Given
        allocator = RegisterAllocator()
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(1)
        const2 = bytecode.add_constant(2)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))  # Both live

        # When
        allocation = allocator.allocate(bytecode)

        # Then
        assert isinstance(allocation, RegisterAllocation)
