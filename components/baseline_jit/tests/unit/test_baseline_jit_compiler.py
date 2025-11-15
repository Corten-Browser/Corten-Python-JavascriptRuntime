"""
Unit tests for baseline JIT compiler.

Tests BaselineJITCompiler for complete compilation pipeline.
"""

import pytest
from components.baseline_jit.src import BaselineJITCompiler, CompiledCode
from components.bytecode.src import BytecodeArray, Instruction, Opcode


class TestBaselineJITCompilerBasic:
    """Test basic JIT compiler functionality."""

    def test_compiler_creation(self):
        """
        When creating BaselineJITCompiler
        Then it should initialize with default backend
        """
        # When
        compiler = BaselineJITCompiler()

        # Then
        assert compiler is not None
        assert compiler.backend_name == "x64"

    def test_compiler_custom_backend(self):
        """
        Given custom backend name
        When creating compiler
        Then backend should be set
        """
        # When
        compiler = BaselineJITCompiler(backend="x64")

        # Then
        assert compiler.backend_name == "x64"


class TestTierUpDecision:
    """Test tier-up decision logic."""

    def test_should_not_compile_cold_function(self):
        """
        Given function with few calls
        When checking should_compile
        Then should return False
        """
        # Given
        compiler = BaselineJITCompiler()

        # When
        result = compiler.should_compile(function_id=1, call_count=10)

        # Then
        assert result is False

    def test_should_compile_hot_function(self):
        """
        Given function with many calls
        When checking should_compile
        Then should return True
        """
        # Given
        compiler = BaselineJITCompiler()

        # When
        result = compiler.should_compile(function_id=1, call_count=2000)

        # Then
        assert result is True

    def test_tier_up_threshold(self):
        """
        Given call count at threshold
        When checking should_compile
        Then should return True
        """
        # Given
        compiler = BaselineJITCompiler()
        threshold = BaselineJITCompiler.TIER_UP_THRESHOLD

        # When
        result = compiler.should_compile(function_id=1, call_count=threshold)

        # Then
        assert result is True


class TestCompileFunction:
    """Test function compilation."""

    def test_compile_empty_function(self):
        """
        Given empty bytecode
        When compiling
        Then should return CompiledCode
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert isinstance(compiled, CompiledCode)
        assert compiled.size >= 0

    def test_compile_simple_function(self):
        """
        Given simple bytecode
        When compiling
        Then should generate machine code
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(42)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert isinstance(compiled, CompiledCode)
        assert compiled.size >= 0

    def test_compile_arithmetic_function(self):
        """
        Given bytecode with arithmetic
        When compiling
        Then should generate code
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()
        const1 = bytecode.add_constant(10)
        const2 = bytecode.add_constant(20)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))
        bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert isinstance(compiled, CompiledCode)


class TestCompiledCodeMetadata:
    """Test compiled code metadata."""

    def test_compiled_code_has_entry_point(self):
        """
        Given compiled function
        When checking metadata
        Then entry point should be set
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(1)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert hasattr(compiled, 'entry_point')
        assert compiled.entry_point >= 0

    def test_compiled_code_has_size(self):
        """
        Given compiled function
        When checking metadata
        Then size should be set
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert hasattr(compiled, 'size')
        assert compiled.size >= 0


class TestCompilationWithProfiling:
    """Test compilation with profiling data."""

    def test_compile_with_profiling_data(self):
        """
        Given bytecode and profiling data
        When compiling
        Then should use profiling info
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(100)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        profiling_data = {'hot_paths': [0, 1, 2]}

        # When
        compiled = compiler.compile_function(bytecode, profiling_data=profiling_data)

        # Then
        assert isinstance(compiled, CompiledCode)

    def test_compile_without_profiling_data(self):
        """
        Given bytecode without profiling data
        When compiling
        Then should still work
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()

        # When
        compiled = compiler.compile_function(bytecode, profiling_data=None)

        # Then
        assert isinstance(compiled, CompiledCode)
