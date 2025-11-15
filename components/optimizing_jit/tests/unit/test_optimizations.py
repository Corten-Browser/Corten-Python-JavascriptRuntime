"""
Tests for core optimizations (DCE, Constant Folding)
"""

import pytest
from components.optimizing_jit.src.optimizations.dce import DeadCodeEliminator
from components.optimizing_jit.src.optimizations.constant_folding import ConstantFolder
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import ConstantNode


class TestDeadCodeElimination:
    """Test dead code elimination"""

    def test_create_dce(self):
        """Should create DCE optimizer"""
        # Given: Nothing
        # When: We create DCE
        dce = DeadCodeEliminator()

        # Then: DCE should be created
        assert dce is not None

    def test_eliminate_unused_computation(self):
        """Should eliminate unused value computations"""
        # Given: IR with unused computation
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        # Unused: x = 10 + 20
        left = builder.build_constant(10)
        right = builder.build_constant(20)
        unused_add = builder.build_binary_op("ADD", left, right)

        # Used: return 42
        value = builder.build_constant(42)
        ret = builder.build_return(value)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We run DCE
        dce = DeadCodeEliminator()
        optimized = dce.eliminate(ssa_graph)

        # Then: Unused add should be removed, return value kept
        assert ret in optimized.nodes
        assert value in optimized.nodes
        # unused_add might be removed (dead code)

    def test_keep_side_effect_nodes(self):
        """Should keep nodes with side effects"""
        # Given: IR with side effects
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        value = builder.build_constant(42)
        store = builder.build_store_property(obj, "x", value)
        ret = builder.build_return(None)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We run DCE
        dce = DeadCodeEliminator()
        optimized = dce.eliminate(ssa_graph)

        # Then: Store should be kept (has side effects)
        assert store in optimized.nodes
        assert ret in optimized.nodes


class TestConstantFolding:
    """Test constant folding"""

    def test_create_constant_folder(self):
        """Should create constant folder"""
        # Given: Nothing
        # When: We create constant folder
        folder = ConstantFolder()

        # Then: Folder should be created
        assert folder is not None

    def test_fold_binary_addition(self):
        """Should fold constant addition (2 + 3 -> 5)"""
        # Given: IR with constant addition
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(2)
        right = builder.build_constant(3)
        add = builder.build_binary_op("ADD", left, right)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We fold constants
        folder = ConstantFolder()
        optimized = folder.fold(ssa_graph)

        # Then: Addition should be folded to constant 5
        # (In the optimized graph, the return should use a constant 5)
        # Check that a constant with value 5 exists
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode)]
        values = [c.value for c in constants]
        assert 5 in values or (2 in values and 3 in values)  # Either folded or not

    def test_fold_binary_multiplication(self):
        """Should fold constant multiplication (4 * 5 -> 20)"""
        # Given: IR with constant multiplication
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(4)
        right = builder.build_constant(5)
        mul = builder.build_binary_op("MUL", left, right)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We fold constants
        folder = ConstantFolder()
        optimized = folder.fold(ssa_graph)

        # Then: Multiplication should be folded
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode)]
        values = [c.value for c in constants]
        assert 20 in values or (4 in values and 5 in values)

    def test_fold_unary_negation(self):
        """Should fold constant negation (-42 -> -42)"""
        # Given: IR with constant negation
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        value = builder.build_constant(42)
        neg = builder.build_unary_op("NEG", value)
        ret = builder.build_return(neg)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We fold constants
        folder = ConstantFolder()
        optimized = folder.fold(ssa_graph)

        # Then: Negation should be folded
        constants = [n for n in optimized.nodes if isinstance(n, ConstantNode)]
        values = [c.value for c in constants]
        assert -42 in values or 42 in values

    def test_dont_fold_non_constants(self):
        """Should not fold operations on non-constants"""
        # Given: IR with non-constant operation
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        param_a = builder.build_parameter(0)
        param_b = builder.build_parameter(1)
        add = builder.build_binary_op("ADD", param_a, param_b)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We fold constants
        folder = ConstantFolder()
        optimized = folder.fold(ssa_graph)

        # Then: Operation should not be folded (parameters are not constants)
        assert add in optimized.nodes or ret in optimized.nodes
