"""
Tests for Strength Reduction Optimization
"""

import pytest
from components.optimizing_jit.src.optimizations.strength_reduction import StrengthReducer
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import BinaryOpNode, ConstantNode


class TestStrengthReduction:
    """Test strength reduction optimization"""

    def test_create_strength_reducer(self):
        """Should create strength reducer"""
        # Given: Nothing
        # When: We create strength reducer
        reducer = StrengthReducer()

        # Then: Reducer should be created
        assert reducer is not None

    def test_reduce_multiply_by_2_to_shift(self):
        """Should replace x * 2 with x << 1"""
        # Given: IR with x * 2
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        two = builder.build_constant(2)
        mul = builder.build_binary_op("MUL", x, two)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Multiply should be replaced with shift left
        shift_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "SHL"]
        assert len(shift_nodes) > 0
        # Should have constant 1 for shift amount
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode) and n.value == 1]
        assert len(constants) > 0

    def test_reduce_multiply_by_4_to_shift(self):
        """Should replace x * 4 with x << 2"""
        # Given: IR with x * 4
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        four = builder.build_constant(4)
        mul = builder.build_binary_op("MUL", x, four)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Multiply should be replaced with shift left by 2
        shift_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "SHL"]
        assert len(shift_nodes) > 0
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode) and n.value == 2]
        assert len(constants) > 0

    def test_reduce_divide_by_2_to_shift(self):
        """Should replace x / 2 with x >> 1"""
        # Given: IR with x / 2
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        two = builder.build_constant(2)
        div = builder.build_binary_op("DIV", x, two)
        ret = builder.build_return(div)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Divide should be replaced with shift right
        shift_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "SHR"]
        assert len(shift_nodes) > 0

    def test_reduce_modulo_by_2_to_and(self):
        """Should replace x % 2 with x & 1"""
        # Given: IR with x % 2
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        two = builder.build_constant(2)
        mod = builder.build_binary_op("MOD", x, two)
        ret = builder.build_return(mod)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Modulo should be replaced with AND
        and_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "AND"]
        assert len(and_nodes) > 0
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode) and n.value == 1]
        assert len(constants) > 0

    def test_dont_reduce_multiply_by_3(self):
        """Should not reduce multiplication by non-power-of-2"""
        # Given: IR with x * 3 (not a power of 2)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        three = builder.build_constant(3)
        mul = builder.build_binary_op("MUL", x, three)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Multiply should NOT be replaced (3 is not a power of 2)
        mul_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "MUL"]
        assert len(mul_nodes) > 0  # Original multiply should remain

    def test_reduce_multiple_operations(self):
        """Should reduce multiple operations in same graph"""
        # Given: IR with x * 2 and y * 4
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        y = builder.build_parameter(1)
        two = builder.build_constant(2)
        four = builder.build_constant(4)

        mul1 = builder.build_binary_op("MUL", x, two)
        mul2 = builder.build_binary_op("MUL", y, four)
        add = builder.build_binary_op("ADD", mul1, mul2)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Both multiplications should be reduced to shifts
        shift_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "SHL"]
        assert len(shift_nodes) >= 2

    def test_reduce_modulo_by_8_to_and(self):
        """Should replace x % 8 with x & 7"""
        # Given: IR with x % 8
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        x = builder.build_parameter(0)
        eight = builder.build_constant(8)
        mod = builder.build_binary_op("MOD", x, eight)
        ret = builder.build_return(mod)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply strength reduction
        reducer = StrengthReducer()
        optimized = reducer.reduce(ssa_graph)

        # Then: Modulo should be replaced with AND 7
        and_nodes = [n for n in optimized.nodes if isinstance(n, BinaryOpNode) and n.op == "AND"]
        assert len(and_nodes) > 0
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode) and n.value == 7]
        assert len(constants) > 0
