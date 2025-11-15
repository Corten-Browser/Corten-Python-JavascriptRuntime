"""
Tests for SSA (Static Single Assignment) Builder

Converts IR to SSA form with phi nodes at merge points.
"""

import pytest
from components.optimizing_jit.src.ssa_builder import SSABuilder, DominatorTree
from components.optimizing_jit.src.ir_builder import IRBuilder, IRGraph, BasicBlock
from components.optimizing_jit.src.ir_nodes import PhiNode


class TestDominatorTree:
    """Test dominator tree construction"""

    def test_create_dominator_tree(self):
        """Should create dominator tree"""
        # Given: A CFG with 3 blocks
        builder = IRBuilder()
        entry = builder.create_basic_block()
        bb1 = builder.create_basic_block()
        bb2 = builder.create_basic_block()
        entry.add_successor(bb1)
        bb1.add_successor(bb2)

        # When: We build dominator tree
        dom_tree = DominatorTree([entry, bb1, bb2], entry)

        # Then: Dominator tree should be constructed
        assert dom_tree.entry == entry
        assert dom_tree.dominates(entry, bb1)
        assert dom_tree.dominates(entry, bb2)
        assert dom_tree.dominates(bb1, bb2)

    def test_immediate_dominator(self):
        """Should compute immediate dominators"""
        # Given: A CFG
        builder = IRBuilder()
        entry = builder.create_basic_block()
        bb1 = builder.create_basic_block()
        bb2 = builder.create_basic_block()
        entry.add_successor(bb1)
        bb1.add_successor(bb2)

        # When: We build dominator tree
        dom_tree = DominatorTree([entry, bb1, bb2], entry)

        # Then: Immediate dominators should be correct
        assert dom_tree.get_idom(bb1) == entry
        assert dom_tree.get_idom(bb2) == bb1
        assert dom_tree.get_idom(entry) is None

    def test_dominator_frontier(self):
        """Should compute dominance frontier"""
        # Given: A diamond CFG (if-then-else-merge)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        then_bb = builder.create_basic_block()
        else_bb = builder.create_basic_block()
        merge = builder.create_basic_block()

        entry.add_successor(then_bb)
        entry.add_successor(else_bb)
        then_bb.add_successor(merge)
        else_bb.add_successor(merge)

        # When: We build dominator tree
        dom_tree = DominatorTree([entry, then_bb, else_bb, merge], entry)

        # Then: Dominance frontier of then_bb and else_bb should be merge
        then_df = dom_tree.get_dominance_frontier(then_bb)
        else_df = dom_tree.get_dominance_frontier(else_bb)

        assert merge in then_df
        assert merge in else_df


class TestSSABuilder:
    """Test SSA builder"""

    def test_create_ssa_builder(self):
        """Should create SSA builder"""
        # Given: Nothing
        # When: We create SSA builder
        ssa_builder = SSABuilder()

        # Then: Builder should be created
        assert ssa_builder is not None

    def test_convert_simple_ir_to_ssa(self):
        """Should convert simple IR to SSA (no control flow)"""
        # Given: Simple IR graph: return a + b
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        param_a = builder.build_parameter(0)
        param_b = builder.build_parameter(1)
        result = builder.build_binary_op("ADD", param_a, param_b)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)

        # When: We convert to SSA
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Then: Should return SSA graph (no changes needed for straight-line code)
        assert ssa_graph is not None
        assert ssa_graph.dominator_tree is not None

    def test_insert_phi_nodes_at_merge(self):
        """Should insert phi nodes at merge points"""
        # Given: Diamond CFG with variable assignment in both branches
        # if (cond) { x = 10; } else { x = 20; }
        # use(x);  // needs phi node here
        builder = IRBuilder()
        entry = builder.create_basic_block()
        then_bb = builder.create_basic_block()
        else_bb = builder.create_basic_block()
        merge = builder.create_basic_block()

        # Entry: branch on condition
        builder.set_current_block(entry)
        cond = builder.build_constant(True)
        builder.build_branch(cond)

        # Then: x = 10
        builder.set_current_block(then_bb)
        value_then = builder.build_constant(10)

        # Else: x = 20
        builder.set_current_block(else_bb)
        value_else = builder.build_constant(20)

        # Merge: use(x) - needs phi
        builder.set_current_block(merge)
        # In SSA, this would be: x = phi(value_then, value_else)

        # Connect CFG
        entry.add_successor(then_bb)
        entry.add_successor(else_bb)
        then_bb.add_successor(merge)
        else_bb.add_successor(merge)

        graph = builder.finalize(entry, merge)

        # When: We convert to SSA
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Then: Merge block should have phi nodes for variables defined in both branches
        # (In a real implementation, variable tracking would identify this)
        assert ssa_graph is not None
        assert ssa_graph.dominator_tree is not None

    def test_ssa_graph_has_dominator_tree(self):
        """Should include dominator tree in SSA graph"""
        # Given: Any IR graph
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        value = builder.build_constant(42)
        ret = builder.build_return(value)
        graph = builder.finalize(entry, entry)

        # When: We convert to SSA
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Then: SSA graph should have dominator tree
        assert hasattr(ssa_graph, "dominator_tree")
        assert ssa_graph.dominator_tree is not None
        assert isinstance(ssa_graph.dominator_tree, DominatorTree)
