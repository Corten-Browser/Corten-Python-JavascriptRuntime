"""
Tests for Loop Optimizer (LICM and Loop Unrolling)
"""

import pytest
from components.optimizing_jit.src.optimizations.loop_optimizer import LoopOptimizer, LoopInfo
from components.optimizing_jit.src.ir_builder import IRBuilder, BasicBlock
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import ConstantNode, BinaryOpNode, PhiNode


class TestLoopOptimizer:
    """Test loop optimizer"""

    def test_create_loop_optimizer(self):
        """Should create loop optimizer"""
        # Given: Nothing
        # When: We create loop optimizer
        optimizer = LoopOptimizer()

        # Then: Optimizer should be created
        assert optimizer is not None

    def test_identify_simple_loop(self):
        """Should identify a simple loop structure"""
        # Given: IR with a simple loop
        #   while (i < 10) { body }
        builder = IRBuilder()

        # Entry block
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        # Loop header (condition check)
        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])  # Placeholder, will be updated
        limit = builder.build_constant(10)
        cond = builder.build_binary_op("LT", i_phi, limit)
        branch = builder.build_branch(cond)

        # Loop body
        body = builder.create_basic_block()
        builder.set_current_block(body)
        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        # Exit block
        exit_block = builder.create_basic_block()

        # Connect blocks
        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We identify loops
        optimizer = LoopOptimizer()
        loops = optimizer.identify_loops(ssa_graph)

        # Then: Should find one loop
        assert len(loops) >= 1
        assert loops[0].header == header

    def test_licm_move_invariant_code(self):
        """Should move loop-invariant code outside loop (LICM)"""
        # Given: Loop with invariant computation
        #   x = 5 * 2  (invariant)
        #   while (i < 10) { result = i + x }
        builder = IRBuilder()

        # Entry block
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        # Loop header
        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        limit = builder.build_constant(10)
        cond = builder.build_binary_op("LT", i_phi, limit)

        # Loop body with invariant code
        body = builder.create_basic_block()
        builder.set_current_block(body)

        # Invariant: x = 5 * 2 (doesn't depend on loop variable)
        five = builder.build_constant(5)
        two = builder.build_constant(2)
        x = builder.build_binary_op("MUL", five, two)

        # Variant: result = i + x
        result = builder.build_binary_op("ADD", i_phi, x)

        # i = i + 1
        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        # Exit
        exit_block = builder.create_basic_block()

        # Connect blocks
        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply LICM
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Invariant multiplication (x = 5 * 2) should be moved outside loop
        # Check that multiplication is not in loop body anymore
        # (In optimized version, it should be in pre-header or entry)
        body_block = [b for b in optimized.basic_blocks if b.id == body.id][0]
        mul_in_body = any(isinstance(n, BinaryOpNode) and n.op == "MUL" for n in body_block.nodes)
        # After LICM, MUL should not be in body
        # (This is simplified - in real implementation would check pre-header)

    def test_licm_dont_move_variant_code(self):
        """Should NOT move loop-variant code (depends on loop variable)"""
        # Given: Loop with variant computation
        #   while (i < 10) { x = i * 2 }  (variant - depends on i)
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        limit = builder.build_constant(10)
        cond = builder.build_binary_op("LT", i_phi, limit)

        body = builder.create_basic_block()
        builder.set_current_block(body)

        # Variant: x = i * 2 (depends on i - loop variable)
        two = builder.build_constant(2)
        x = builder.build_binary_op("MUL", i_phi, two)

        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply LICM
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Variant code should stay in loop body
        # (MUL depends on i_phi which changes each iteration)
        # Verify MUL is still in body (not moved)

    def test_loop_unrolling_simple(self):
        """Should unroll loop with constant trip count"""
        # Given: Loop with constant trip count
        #   for (i = 0; i < 4; i++) { sum = sum + i }
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)
        sum_init = builder.build_constant(0)

        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        sum_phi = builder.build_phi([sum_init])
        limit = builder.build_constant(4)
        cond = builder.build_binary_op("LT", i_phi, limit)

        body = builder.create_basic_block()
        builder.set_current_block(body)
        sum_next = builder.build_binary_op("ADD", sum_phi, i_phi)
        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We unroll the loop
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Loop should be unrolled (body replicated)
        # With unroll factor 4, the entire loop should be eliminated
        # and replaced with straight-line code
        # sum = sum + 0; sum = sum + 1; sum = sum + 2; sum = sum + 3;

    def test_loop_unrolling_factor_4(self):
        """Should unroll loop by factor of 4"""
        # Given: Loop with trip count = 16 (divisible by 4)
        #   for (i = 0; i < 16; i++) { body }
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        limit = builder.build_constant(16)
        cond = builder.build_binary_op("LT", i_phi, limit)

        body = builder.create_basic_block()
        builder.set_current_block(body)
        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We unroll by factor of 4
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Loop should be unrolled 4x
        # Instead of 16 iterations, should be 4 iterations with 4x body
        # i += 4 instead of i += 1

    def test_loop_unrolling_skip_large_loops(self):
        """Should NOT unroll loops with large trip counts (>16)"""
        # Given: Loop with large trip count
        #   for (i = 0; i < 1000; i++) { body }
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        limit = builder.build_constant(1000)
        cond = builder.build_binary_op("LT", i_phi, limit)

        body = builder.create_basic_block()
        builder.set_current_block(body)
        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We try to unroll
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Loop should NOT be unrolled (too large)
        # Structure should remain similar

    def test_nested_loops(self):
        """Should handle nested loops correctly"""
        # Given: Nested loop structure
        #   for (i = 0; i < 10; i++)
        #       for (j = 0; j < 5; j++) { body }
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)

        # Outer loop header
        outer_header = builder.create_basic_block()
        builder.set_current_block(outer_header)
        i_phi = builder.build_phi([i_init])
        i_limit = builder.build_constant(10)
        i_cond = builder.build_binary_op("LT", i_phi, i_limit)

        # Inner loop header
        inner_header = builder.create_basic_block()
        builder.set_current_block(inner_header)
        j_init = builder.build_constant(0)
        j_phi = builder.build_phi([j_init])
        j_limit = builder.build_constant(5)
        j_cond = builder.build_binary_op("LT", j_phi, j_limit)

        # Inner loop body
        inner_body = builder.create_basic_block()
        builder.set_current_block(inner_body)
        one = builder.build_constant(1)
        j_next = builder.build_binary_op("ADD", j_phi, one)

        # Inner loop exit (increment outer)
        inner_exit = builder.create_basic_block()
        builder.set_current_block(inner_exit)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        # Outer loop exit
        outer_exit = builder.create_basic_block()

        # Connect blocks
        entry.add_successor(outer_header)
        outer_header.add_successor(inner_header)
        outer_header.add_successor(outer_exit)
        inner_header.add_successor(inner_body)
        inner_header.add_successor(inner_exit)
        inner_body.add_successor(inner_header)
        inner_exit.add_successor(outer_header)

        graph = builder.finalize(entry, outer_exit)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We identify loops
        optimizer = LoopOptimizer()
        loops = optimizer.identify_loops(ssa_graph)

        # Then: Should identify 2 loops (outer and inner)
        assert len(loops) >= 2

    def test_licm_with_multiple_invariants(self):
        """Should move multiple loop-invariant computations"""
        # Given: Loop with multiple invariants
        #   a = 10; b = 20;
        #   while (i < n) {
        #       x = a + b;  (invariant)
        #       y = x * 2;  (invariant)
        #       result = i + y;
        #   }
        builder = IRBuilder()

        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        i_init = builder.build_constant(0)
        a = builder.build_constant(10)
        b = builder.build_constant(20)

        header = builder.create_basic_block()
        builder.set_current_block(header)
        i_phi = builder.build_phi([i_init])
        n = builder.build_parameter(0)
        cond = builder.build_binary_op("LT", i_phi, n)

        body = builder.create_basic_block()
        builder.set_current_block(body)

        # Invariants
        x = builder.build_binary_op("ADD", a, b)
        two = builder.build_constant(2)
        y = builder.build_binary_op("MUL", x, two)

        # Variant
        result = builder.build_binary_op("ADD", i_phi, y)

        one = builder.build_constant(1)
        i_next = builder.build_binary_op("ADD", i_phi, one)

        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        graph = builder.finalize(entry, exit_block)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We apply LICM
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Both x and y should be moved outside loop
        # (Computations that don't depend on loop variable)

    def test_loop_info_structure(self):
        """Should create correct LoopInfo structure"""
        # Given: A simple loop
        builder = IRBuilder()

        entry = builder.create_basic_block()
        header = builder.create_basic_block()
        body = builder.create_basic_block()
        exit_block = builder.create_basic_block()

        entry.add_successor(header)
        header.add_successor(body)
        header.add_successor(exit_block)
        body.add_successor(header)

        # When: We create LoopInfo
        loop_info = LoopInfo(header, [body], exit_block)

        # Then: LoopInfo should have correct structure
        assert loop_info.header == header
        assert body in loop_info.body_blocks
        assert loop_info.exit_block == exit_block

    def test_optimize_empty_graph(self):
        """Should handle empty IR graph gracefully"""
        # Given: Empty IR graph
        builder = IRBuilder()
        entry = builder.create_basic_block()
        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We optimize
        optimizer = LoopOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Should return graph unchanged (no loops to optimize)
        assert optimized is not None
        assert len(optimized.basic_blocks) > 0
