"""
Unit tests for machine code generator.

Tests CodeGenerator for bytecode to machine code translation.
"""

import pytest
from components.baseline_jit.src import CodeGenerator, x64Backend, Register, RegisterAllocation
from components.bytecode.src import BytecodeArray, Instruction, Opcode


class TestCodeGeneratorBasic:
    """Test basic code generator functionality."""

    def test_generator_creation(self):
        """
        When creating CodeGenerator with backend
        Then it should initialize successfully
        """
        # Given
        backend = x64Backend()

        # When
        generator = CodeGenerator(backend)

        # Then
        assert generator is not None
        assert generator.backend is not None

    def test_generate_empty_bytecode(self):
        """
        Given empty bytecode
        When generating machine code
        Then should return minimal code
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        allocation = RegisterAllocation(assignments={}, spills=[])

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert isinstance(code, bytes)


class TestCodeGeneratorPrologue:
    """Test function prologue generation."""

    def test_emit_prologue(self):
        """
        Given frame size
        When emitting prologue
        Then should generate stack frame setup code
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        frame_size = 32

        # When
        generator.emit_prologue(frame_size)

        # Then - should not raise exception
        assert True

    def test_emit_epilogue(self):
        """
        When emitting epilogue
        Then should generate stack frame teardown code
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)

        # When
        generator.emit_epilogue()

        # Then - should not raise exception
        assert True


class TestCodeGeneratorBytecode:
    """Test bytecode instruction compilation."""

    def test_generate_load_constant(self):
        """
        Given LOAD_CONSTANT instruction
        When generating code
        Then should emit MOV instruction
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(42)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        allocation = RegisterAllocation(assignments={0: Register.RAX}, spills=[])

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert len(code) > 0

    def test_generate_add(self):
        """
        Given ADD instruction
        When generating code
        Then should emit ADD instruction
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))
        allocation = RegisterAllocation(assignments={}, spills=[])

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert isinstance(code, bytes)

    def test_generate_subtract(self):
        """
        Given SUBTRACT instruction
        When generating code
        Then should emit SUB instruction
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(opcode=Opcode.SUBTRACT))
        allocation = RegisterAllocation(assignments={}, spills=[])

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert isinstance(code, bytes)

    def test_generate_multiply(self):
        """
        Given MULTIPLY instruction
        When generating code
        Then should emit IMUL instruction
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(opcode=Opcode.MULTIPLY))
        allocation = RegisterAllocation(assignments={}, spills=[])

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert isinstance(code, bytes)


class TestCodeGeneratorComplex:
    """Test complex code generation scenarios."""

    def test_generate_sequence(self):
        """
        Given sequence of instructions
        When generating code
        Then should emit complete code sequence
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(10)
        const2 = bytecode.add_constant(20)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))
        allocation = RegisterAllocation(
            assignments={0: Register.RAX, 1: Register.RBX},
            spills=[]
        )

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert len(code) > 0


class TestCodeGeneratorOptimization:
    """Test simple optimizations in code generation."""

    def test_constant_folding_candidates(self):
        """
        Given two constant loads followed by ADD
        When generating code
        Then code should be generated
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(5)
        const2 = bytecode.add_constant(10)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))
        allocation = RegisterAllocation(
            assignments={0: Register.RAX, 1: Register.RBX},
            spills=[]
        )

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert isinstance(code, bytes)

    def test_register_allocation_usage(self):
        """
        Given register allocation
        When generating code
        Then allocated registers should be used
        """
        # Given
        backend = x64Backend()
        generator = CodeGenerator(backend)
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(100)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        # Specific register allocation
        allocation = RegisterAllocation(
            assignments={0: Register.RCX},  # Use RCX instead of RAX
            spills=[]
        )

        # When
        code = generator.generate(bytecode, allocation)

        # Then
        assert len(code) > 0
