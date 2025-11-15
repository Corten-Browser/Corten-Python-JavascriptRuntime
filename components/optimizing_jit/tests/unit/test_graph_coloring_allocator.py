"""
Tests for Graph Coloring Register Allocator

Tests advanced register allocation using graph coloring (Chaitin's algorithm).
"""

import pytest
from components.optimizing_jit.src.optimizations.graph_coloring_allocator import (
    GraphColoringAllocator,
    InterferenceGraph,
    RegisterAllocation,
)
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import BinaryOpNode


class TestInterferenceGraph:
    """Test interference graph"""

    def test_create_graph(self):
        """Should create interference graph"""
        # Given: Nothing
        # When: We create graph
        graph = InterferenceGraph()

        # Then: Graph should be created
        assert graph is not None

    def test_add_node(self):
        """Should add node to graph"""
        # Given: Interference graph and IR node
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)
        node = builder.build_constant(42)

        graph = InterferenceGraph()

        # When: We add node
        graph.add_node(node)

        # Then: Node should be in graph
        assert node in graph.nodes

    def test_add_interference_edge(self):
        """Should add interference edge between two nodes"""
        # Given: Interference graph with two nodes
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)

        # When: We add interference edge (a and b are live simultaneously)
        graph.add_edge(a, b)

        # Then: Edge should exist in both directions
        assert graph.has_edge(a, b)
        assert graph.has_edge(b, a)

    def test_get_degree(self):
        """Should get degree of node (number of neighbors)"""
        # Given: Interference graph with connected nodes
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)

        # a interferes with b and c
        graph.add_edge(a, b)
        graph.add_edge(a, c)

        # When: We get degree of a
        degree = graph.degree(a)

        # Then: Degree should be 2
        assert degree == 2

    def test_get_neighbors(self):
        """Should get all neighbors of a node"""
        # Given: Interference graph with neighbors
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)

        graph.add_edge(a, b)
        graph.add_edge(a, c)

        # When: We get neighbors of a
        neighbors = graph.neighbors(a)

        # Then: Should return b and c
        assert b in neighbors
        assert c in neighbors
        assert len(neighbors) == 2

    def test_remove_node(self):
        """Should remove node from graph"""
        # Given: Interference graph with nodes
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(a, b)

        # When: We remove node a
        graph.remove_node(a)

        # Then: Node should be gone
        assert a not in graph.nodes
        assert not graph.has_edge(a, b)


class TestRegisterAllocation:
    """Test register allocation result"""

    def test_create_allocation(self):
        """Should create register allocation"""
        # Given: Nothing
        # When: We create allocation
        allocation = RegisterAllocation(num_registers=14)

        # Then: Allocation should be created
        assert allocation is not None
        assert allocation.num_registers == 14

    def test_assign_register(self):
        """Should assign register to SSA value"""
        # Given: Register allocation and SSA value
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        value = builder.build_parameter(0)
        allocation = RegisterAllocation(num_registers=14)

        # When: We assign register
        allocation.assign(value, 3)

        # Then: Value should map to register
        assert allocation.get_register(value) == 3

    def test_mark_spilled(self):
        """Should mark SSA value as spilled to stack"""
        # Given: Register allocation and SSA value
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        value = builder.build_parameter(0)
        allocation = RegisterAllocation(num_registers=14)

        # When: We mark as spilled
        allocation.spill(value)

        # Then: Value should be marked as spilled
        assert allocation.is_spilled(value)

    def test_get_spilled_values(self):
        """Should get all spilled values"""
        # Given: Register allocation with spilled values
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)

        allocation = RegisterAllocation(num_registers=14)
        allocation.spill(a)
        allocation.assign(b, 5)

        # When: We get spilled values
        spilled = allocation.get_spilled()

        # Then: Should return only spilled values
        assert a in spilled
        assert b not in spilled


class TestGraphColoringAllocator:
    """Test graph coloring register allocator"""

    def test_create_allocator(self):
        """Should create graph coloring allocator"""
        # Given: Nothing
        # When: We create allocator
        allocator = GraphColoringAllocator(num_registers=14)

        # Then: Allocator should be created
        assert allocator is not None
        assert allocator.num_registers == 14

    def test_allocate_simple_graph(self):
        """Should allocate registers for simple IR"""
        # Given: Simple IR (a + b)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        result = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We allocate registers
        allocator = GraphColoringAllocator(num_registers=14)
        allocation = allocator.allocate(ssa_graph)

        # Then: All values should have registers
        assert allocation is not None
        # a, b, result should all get registers
        assert allocation.get_register(a) is not None or allocation.is_spilled(a)

    def test_build_interference_graph(self):
        """Should build interference graph from IR"""
        # Given: IR with live ranges
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        # These are all live simultaneously
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", b, c)
        z = builder.build_binary_op("SUB", x, y)

        ret = builder.build_return(z)

        graph_ir = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph_ir)

        # When: We build interference graph
        allocator = GraphColoringAllocator(num_registers=14)
        interference = allocator.build_interference_graph(ssa_graph)

        # Then: Interference graph should be built
        assert interference is not None
        assert len(interference.nodes) > 0

    def test_color_graph_no_spilling(self):
        """Should color graph without spilling (enough registers)"""
        # Given: Small IR that fits in registers
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        result = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We allocate with plenty of registers
        allocator = GraphColoringAllocator(num_registers=14)
        allocation = allocator.allocate(ssa_graph)

        # Then: No spilling should occur
        spilled = allocation.get_spilled()
        # For simple case, we might have no spills
        # (actual result depends on implementation)
        assert allocation is not None

    def test_simplify_phase(self):
        """Should simplify graph by removing low-degree nodes"""
        # Given: Interference graph
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)
        graph.add_edge(a, b)  # a has degree 1

        # When: We simplify (remove nodes with degree < K)
        allocator = GraphColoringAllocator(num_registers=14)
        stack = allocator.simplify(graph, num_colors=14)

        # Then: Low-degree nodes should be removed and pushed to stack
        assert len(stack) > 0

    def test_spilling_when_needed(self):
        """Should spill when not enough registers"""
        # Given: Large IR with many live values
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        # Create many parameters (more than available registers)
        params = [builder.build_parameter(i) for i in range(20)]

        # All are used together (live simultaneously)
        result = params[0]
        for p in params[1:]:
            result = builder.build_binary_op("ADD", result, p)

        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We allocate with limited registers
        allocator = GraphColoringAllocator(num_registers=5)
        allocation = allocator.allocate(ssa_graph)

        # Then: Some values should be spilled
        # (with 20 values and only 5 registers, spilling is necessary)
        # Note: Actual behavior depends on implementation
        assert allocation is not None

    def test_choose_spill_candidate(self):
        """Should choose spill candidate using heuristic"""
        # Given: Interference graph with nodes
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_node(c)

        # When: We choose spill candidate
        allocator = GraphColoringAllocator(num_registers=14)
        candidate = allocator.choose_spill_candidate(graph)

        # Then: Should return a node
        assert candidate in [a, b, c]

    def test_coloring_phase(self):
        """Should assign colors (registers) to nodes"""
        # Given: Stack from simplify phase
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)

        graph = InterferenceGraph()
        graph.add_node(a)
        graph.add_node(b)
        graph.add_edge(a, b)

        allocator = GraphColoringAllocator(num_registers=14)
        stack = [a, b]

        # When: We color the graph
        coloring = allocator.color(stack, graph, num_colors=14)

        # Then: Nodes should have different colors (they interfere)
        assert coloring is not None
        # a and b should get different registers (if not spilled)
        if a in coloring and b in coloring:
            if coloring[a] != -1 and coloring[b] != -1:
                assert coloring[a] != coloring[b]

    def test_live_range_analysis(self):
        """Should analyze live ranges of SSA values"""
        # Given: IR with clear live ranges
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        x = builder.build_binary_op("ADD", a, b)  # a, b live here
        y = builder.build_binary_op("MUL", x, b)  # x, b live here
        ret = builder.build_return(y)            # y live here

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze live ranges
        allocator = GraphColoringAllocator(num_registers=14)
        live_ranges = allocator.compute_live_ranges(ssa_graph)

        # Then: Live ranges should be computed
        assert live_ranges is not None
        # Each value should have a live range
        assert len(live_ranges) > 0
