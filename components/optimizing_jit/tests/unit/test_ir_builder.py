"""
Tests for IR Builder

Builds high-level IR graph from bytecode
"""

import pytest
from components.optimizing_jit.src.ir_builder import IRBuilder, IRGraph, BasicBlock
from components.optimizing_jit.src.ir_nodes import (
    IRNodeType,
    ConstantNode,
    ParameterNode,
    BinaryOpNode,
    ReturnNode,
)


class TestBasicBlock:
    """Test basic block structure"""

    def test_create_basic_block(self):
        """Should create a basic block"""
        # Given: Basic block ID
        block_id = 0

        # When: We create a basic block
        bb = BasicBlock(block_id)

        # Then: Block should be created correctly
        assert bb.id == 0
        assert bb.nodes == []
        assert bb.predecessors == []
        assert bb.successors == []

    def test_add_node_to_basic_block(self):
        """Should add IR node to basic block"""
        # Given: A basic block
        bb = BasicBlock(0)
        node = ConstantNode(42)

        # When: We add a node
        bb.add_node(node)

        # Then: Node should be in block
        assert node in bb.nodes

    def test_add_successor(self):
        """Should add successor basic block"""
        # Given: Two basic blocks
        bb1 = BasicBlock(0)
        bb2 = BasicBlock(1)

        # When: We add bb2 as successor of bb1
        bb1.add_successor(bb2)

        # Then: bb2 should be successor of bb1, bb1 predecessor of bb2
        assert bb2 in bb1.successors
        assert bb1 in bb2.predecessors


class TestIRGraph:
    """Test IR graph structure"""

    def test_create_ir_graph(self):
        """Should create an IR graph"""
        # Given: Nothing
        # When: We create an IR graph
        graph = IRGraph()

        # Then: Graph should be initialized
        assert graph.nodes == []
        assert graph.basic_blocks == []
        assert graph.entry is None
        assert graph.exit is None

    def test_add_node_to_graph(self):
        """Should add node to IR graph"""
        # Given: An IR graph
        graph = IRGraph()
        node = ConstantNode(42)

        # When: We add a node
        graph.add_node(node)

        # Then: Node should be in graph
        assert node in graph.nodes

    def test_add_basic_block_to_graph(self):
        """Should add basic block to graph"""
        # Given: An IR graph
        graph = IRGraph()
        bb = BasicBlock(0)

        # When: We add a basic block
        graph.add_basic_block(bb)

        # Then: Block should be in graph
        assert bb in graph.basic_blocks

    def test_set_entry_exit(self):
        """Should set entry and exit blocks"""
        # Given: An IR graph with blocks
        graph = IRGraph()
        entry_bb = BasicBlock(0)
        exit_bb = BasicBlock(1)
        graph.add_basic_block(entry_bb)
        graph.add_basic_block(exit_bb)

        # When: We set entry and exit
        graph.set_entry(entry_bb)
        graph.set_exit(exit_bb)

        # Then: Entry and exit should be set
        assert graph.entry == entry_bb
        assert graph.exit == exit_bb


class TestIRBuilder:
    """Test IR builder"""

    def test_create_ir_builder(self):
        """Should create an IR builder"""
        # Given: Nothing
        # When: We create an IR builder
        builder = IRBuilder()

        # Then: Builder should be initialized
        assert builder is not None

    def test_build_constant(self):
        """Should build constant node"""
        # Given: An IR builder
        builder = IRBuilder()

        # When: We build a constant
        node = builder.build_constant(42)

        # Then: Should create constant node
        assert isinstance(node, ConstantNode)
        assert node.value == 42

    def test_build_parameter(self):
        """Should build parameter node"""
        # Given: An IR builder
        builder = IRBuilder()

        # When: We build a parameter
        node = builder.build_parameter(0)

        # Then: Should create parameter node
        assert isinstance(node, ParameterNode)
        assert node.index == 0

    def test_build_binary_op(self):
        """Should build binary operation node"""
        # Given: An IR builder with operands
        builder = IRBuilder()
        left = builder.build_constant(10)
        right = builder.build_constant(20)

        # When: We build an ADD operation
        node = builder.build_binary_op("ADD", left, right)

        # Then: Should create binary op node
        assert isinstance(node, BinaryOpNode)
        assert node.op == "ADD"
        assert left in node.inputs
        assert right in node.inputs

    def test_build_return(self):
        """Should build return node"""
        # Given: An IR builder with value
        builder = IRBuilder()
        value = builder.build_constant(42)

        # When: We build a return
        node = builder.build_return(value)

        # Then: Should create return node
        assert isinstance(node, ReturnNode)
        assert value in node.inputs

    def test_create_basic_block(self):
        """Should create basic block in builder"""
        # Given: An IR builder
        builder = IRBuilder()

        # When: We create a basic block
        bb = builder.create_basic_block()

        # Then: Block should be created with unique ID
        assert isinstance(bb, BasicBlock)
        assert bb.id == 0

    def test_create_multiple_basic_blocks(self):
        """Should create multiple basic blocks with unique IDs"""
        # Given: An IR builder
        builder = IRBuilder()

        # When: We create multiple blocks
        bb0 = builder.create_basic_block()
        bb1 = builder.create_basic_block()
        bb2 = builder.create_basic_block()

        # Then: Each should have unique ID
        assert bb0.id == 0
        assert bb1.id == 1
        assert bb2.id == 2

    def test_set_current_block(self):
        """Should set current insertion block"""
        # Given: An IR builder with a block
        builder = IRBuilder()
        bb = builder.create_basic_block()

        # When: We set current block
        builder.set_current_block(bb)

        # Then: Current block should be set
        assert builder.current_block == bb

    def test_insert_in_current_block(self):
        """Should insert node in current block"""
        # Given: An IR builder with current block
        builder = IRBuilder()
        bb = builder.create_basic_block()
        builder.set_current_block(bb)

        # When: We build a constant (auto-inserts in current block)
        node = builder.build_constant(42)

        # Then: Node should be in current block
        assert node in bb.nodes

    def test_build_simple_function(self):
        """Should build IR for simple function: function(a, b) { return a + b; }"""
        # Given: An IR builder
        builder = IRBuilder()
        entry_bb = builder.create_basic_block()
        builder.set_current_block(entry_bb)

        # When: We build the function
        # function(a, b) { return a + b; }
        param_a = builder.build_parameter(0)
        param_b = builder.build_parameter(1)
        add_result = builder.build_binary_op("ADD", param_a, param_b)
        ret = builder.build_return(add_result)

        # Then: IR should be created correctly
        assert param_a.index == 0
        assert param_b.index == 1
        assert add_result.op == "ADD"
        assert add_result.inputs == [param_a, param_b]
        assert ret.inputs == [add_result]
        # All nodes should be in entry block
        assert param_a in entry_bb.nodes
        assert param_b in entry_bb.nodes
        assert add_result in entry_bb.nodes
        assert ret in entry_bb.nodes

    def test_build_function_with_branches(self):
        """Should build IR for function with branches"""
        # Given: An IR builder
        builder = IRBuilder()

        # When: We build a function with if-else
        # function(x) {
        #     if (x > 0) {
        #         return x + 1;
        #     } else {
        #         return x - 1;
        #     }
        # }
        entry_bb = builder.create_basic_block()
        then_bb = builder.create_basic_block()
        else_bb = builder.create_basic_block()
        merge_bb = builder.create_basic_block()

        # Entry block
        builder.set_current_block(entry_bb)
        param_x = builder.build_parameter(0)
        zero = builder.build_constant(0)
        cond = builder.build_binary_op("GT", param_x, zero)
        branch = builder.build_branch(cond)

        # Connect control flow
        entry_bb.add_successor(then_bb)
        entry_bb.add_successor(else_bb)

        # Then block: return x + 1
        builder.set_current_block(then_bb)
        one = builder.build_constant(1)
        then_result = builder.build_binary_op("ADD", param_x, one)
        then_ret = builder.build_return(then_result)
        then_bb.add_successor(merge_bb)

        # Else block: return x - 1
        builder.set_current_block(else_bb)
        minus_one = builder.build_constant(1)
        else_result = builder.build_binary_op("SUB", param_x, minus_one)
        else_ret = builder.build_return(else_result)
        else_bb.add_successor(merge_bb)

        # Then: CFG should be correctly structured
        assert then_bb in entry_bb.successors
        assert else_bb in entry_bb.successors
        assert entry_bb in then_bb.predecessors
        assert entry_bb in else_bb.predecessors
        assert merge_bb in then_bb.successors
        assert merge_bb in else_bb.successors

    def test_finalize_graph(self):
        """Should finalize IR graph"""
        # Given: An IR builder with blocks
        builder = IRBuilder()
        entry_bb = builder.create_basic_block()
        exit_bb = builder.create_basic_block()

        builder.set_current_block(entry_bb)
        value = builder.build_constant(42)
        builder.set_current_block(exit_bb)
        ret = builder.build_return(value)

        # When: We finalize the graph
        graph = builder.finalize(entry_bb, exit_bb)

        # Then: Should return IR graph with all blocks and nodes
        assert isinstance(graph, IRGraph)
        assert graph.entry == entry_bb
        assert graph.exit == exit_bb
        assert entry_bb in graph.basic_blocks
        assert exit_bb in graph.basic_blocks
        # All nodes from all blocks should be in graph
        assert value in graph.nodes
        assert ret in graph.nodes
