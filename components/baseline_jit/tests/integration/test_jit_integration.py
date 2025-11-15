"""
Integration tests for baseline JIT compiler.

Tests end-to-end compilation and execution pipeline.
"""

import pytest
from components.baseline_jit.src import BaselineJITCompiler, CodeCache
from components.bytecode.src import BytecodeArray, Instruction, Opcode


class TestJITCompilationPipeline:
    """Test complete JIT compilation pipeline."""

    def test_compile_and_cache(self):
        """
        Given a JIT compiler and code cache
        When compiling and caching function
        Then code should be retrievable from cache
        """
        # Given
        compiler = BaselineJITCompiler()
        cache = CodeCache()
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(42)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))

        # When
        compiled = compiler.compile_function(bytecode)
        cache.insert(function_id=1, code=compiled)

        # Then
        cached_code = cache.lookup(function_id=1)
        assert cached_code is not None
        assert cached_code.size == compiled.size

    def test_tier_up_workflow(self):
        """
        Given a hot function
        When checking tier-up and compiling
        Then compiled code should be available
        """
        # Given
        compiler = BaselineJITCompiler()
        cache = CodeCache()
        function_id = 42
        call_count = 1500  # Hot function

        # When - check tier-up decision
        should_compile = compiler.should_compile(function_id, call_count)

        # Then
        assert should_compile is True

        # When - compile
        bytecode = BytecodeArray()
        const_idx = bytecode.add_constant(100)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        compiled = compiler.compile_function(bytecode)
        cache.insert(function_id, compiled)

        # Then
        assert cache.lookup(function_id) is not None


class TestEndToEndScenarios:
    """Test realistic end-to-end scenarios."""

    def test_compile_arithmetic_function(self):
        """
        Given arithmetic bytecode
        When compiling end-to-end
        Then should produce machine code
        """
        # Given
        compiler = BaselineJITCompiler()
        bytecode = BytecodeArray()

        # Build: x = 10 + 20
        const1 = bytecode.add_constant(10)
        const2 = bytecode.add_constant(20)
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const1))
        bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const2))
        bytecode.add_instruction(Instruction(opcode=Opcode.ADD))
        bytecode.add_instruction(Instruction(opcode=Opcode.RETURN))

        # When
        compiled = compiler.compile_function(bytecode)

        # Then
        assert compiled.size > 0
        assert len(compiled.code) > 0

    def test_cache_eviction_workflow(self):
        """
        Given cache with many functions
        When cache fills up
        Then LRU eviction should work
        """
        # Given
        cache = CodeCache(max_size=5000)  # Small cache
        compiler = BaselineJITCompiler()

        # When - fill cache
        for i in range(20):
            bytecode = BytecodeArray()
            const_idx = bytecode.add_constant(i)
            bytecode.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
            compiled = compiler.compile_function(bytecode)
            cache.insert(function_id=i, code=compiled)

        # Then - cache should have evicted old entries
        assert cache.size <= cache.max_size

    def test_multiple_functions_compilation(self):
        """
        Given multiple different functions
        When compiling each
        Then all should compile successfully
        """
        # Given
        compiler = BaselineJITCompiler()
        functions = []

        # Function 1: Load constant
        bytecode1 = BytecodeArray()
        const_idx = bytecode1.add_constant(42)
        bytecode1.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=const_idx))
        functions.append(bytecode1)

        # Function 2: Arithmetic
        bytecode2 = BytecodeArray()
        c1 = bytecode2.add_constant(5)
        c2 = bytecode2.add_constant(10)
        bytecode2.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=c1))
        bytecode2.add_instruction(Instruction(opcode=Opcode.LOAD_CONSTANT, operand1=c2))
        bytecode2.add_instruction(Instruction(opcode=Opcode.MULTIPLY))
        functions.append(bytecode2)

        # When - compile all
        compiled_functions = [compiler.compile_function(bc) for bc in functions]

        # Then - all compiled successfully
        assert len(compiled_functions) == 2
        assert all(c.size > 0 for c in compiled_functions)
