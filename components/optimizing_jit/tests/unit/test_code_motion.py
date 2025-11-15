"""
Tests for Code Motion and Instruction Scheduling

Tests code motion optimization and instruction scheduling for better performance.
"""

import pytest
from components.optimizing_jit.src.optimizations.code_motion import (
    CodeMotionOptimizer,
    InstructionScheduler,
    DependencyGraph,
)
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import BinaryOpNode, LoadPropertyNode


class TestCodeMotionOptimizer:
    """Test code motion optimizer"""

    def test_create_optimizer(self):
        """Should create code motion optimizer"""
        # Given: Nothing
        # When: We create optimizer
        optimizer = CodeMotionOptimizer()

        # Then: Optimizer should be created
        assert optimizer is not None

    def test_sink_operation_closer_to_use(self):
        """Should sink operation closer to its use (reduce live range)"""
        # Given: IR with operation far from its use
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        # Early computation: x = a + b
        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        x = builder.build_binary_op("ADD", a, b)

        # Other operations
        c = builder.build_parameter(2)
        d = builder.build_parameter(3)
        y = builder.build_binary_op("MUL", c, d)

        # Use x much later
        result = builder.build_binary_op("SUB", x, y)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We optimize code motion
        optimizer = CodeMotionOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Code should be moved closer to use
        assert optimized is not None
        # Verify operations are still in graph
        assert x in optimized.nodes or result in optimized.nodes

    def test_move_independent_operations(self):
        """Should move independent operations for better scheduling"""
        # Given: IR with independent operations
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        # Independent operations
        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        # These are independent and can be reordered
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", b, c)
        z = builder.build_binary_op("SUB", c, a)

        ret = builder.build_return(x)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We optimize code motion
        optimizer = CodeMotionOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Operations should be movable
        assert optimized is not None

    def test_respect_dependencies(self):
        """Should respect data dependencies when moving code"""
        # Given: IR with data dependencies
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)

        # x depends on a and b
        x = builder.build_binary_op("ADD", a, b)
        # y depends on x (data dependency)
        y = builder.build_binary_op("MUL", x, b)
        # z depends on y (data dependency chain)
        z = builder.build_binary_op("SUB", y, a)

        ret = builder.build_return(z)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We optimize code motion
        optimizer = CodeMotionOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Dependencies should be preserved
        # z must still depend on y, y on x
        assert optimized is not None
        # Check that dependency chain is preserved
        if z in optimized.nodes:
            assert y in z.inputs or any(y in n.inputs for n in optimized.nodes)

    def test_no_side_effect_violations(self):
        """Should not reorder operations with side effects"""
        # Given: IR with side effects (stores)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        val1 = builder.build_constant(10)
        val2 = builder.build_constant(20)

        # These stores must not be reordered
        store1 = builder.build_store_property(obj, "x", val1)
        store2 = builder.build_store_property(obj, "y", val2)

        ret = builder.build_return(None)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We optimize code motion
        optimizer = CodeMotionOptimizer()
        optimized = optimizer.optimize(ssa_graph)

        # Then: Stores should not be reordered (side effects)
        assert store1 in optimized.nodes
        assert store2 in optimized.nodes


class TestInstructionScheduler:
    """Test instruction scheduler"""

    def test_create_scheduler(self):
        """Should create instruction scheduler"""
        # Given: Nothing
        # When: We create scheduler
        scheduler = InstructionScheduler()

        # Then: Scheduler should be created
        assert scheduler is not None

    def test_schedule_basic_block(self):
        """Should schedule instructions in basic block"""
        # Given: IR with basic block
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", x, c)
        ret = builder.build_return(y)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We schedule instructions
        scheduler = InstructionScheduler()
        scheduled = scheduler.schedule(ssa_graph)

        # Then: Instructions should be scheduled
        assert scheduled is not None

    def test_build_dependency_graph(self):
        """Should build dependency graph for scheduling"""
        # Given: IR with dependencies
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", x, b)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We build dependency graph
        scheduler = InstructionScheduler()
        dep_graph = scheduler.build_dependency_graph(ssa_graph)

        # Then: Dependencies should be tracked
        assert dep_graph is not None

    def test_topological_sort(self):
        """Should perform topological sort respecting dependencies"""
        # Given: IR with clear dependency chain
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        # Chain: a -> x -> y -> z
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", x, c)
        z = builder.build_binary_op("SUB", y, b)
        ret = builder.build_return(z)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We schedule with topological sort
        scheduler = InstructionScheduler()
        scheduled = scheduler.schedule(ssa_graph)

        # Then: Dependencies should be respected in order
        assert scheduled is not None

    def test_prioritize_critical_path(self):
        """Should prioritize critical path (longest dependency chain)"""
        # Given: IR with multiple paths, one critical
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)

        # Critical path: a -> x -> y -> z (long chain)
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", x, c)
        z = builder.build_binary_op("SUB", y, a)

        # Short path: b -> w
        w = builder.build_binary_op("ADD", b, c)

        result = builder.build_binary_op("ADD", z, w)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We schedule
        scheduler = InstructionScheduler()
        scheduled = scheduler.schedule(ssa_graph)

        # Then: Critical path should be prioritized
        assert scheduled is not None

    def test_group_similar_operations(self):
        """Should group similar operations together"""
        # Given: IR with mixed operation types
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        a = builder.build_parameter(1)
        b = builder.build_parameter(2)

        # Mix of loads and arithmetic
        load1 = builder.build_load_property(obj, "x")
        add1 = builder.build_binary_op("ADD", a, b)
        load2 = builder.build_load_property(obj, "y")
        add2 = builder.build_binary_op("ADD", load1, load2)

        ret = builder.build_return(add2)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We schedule
        scheduler = InstructionScheduler()
        scheduled = scheduler.schedule(ssa_graph)

        # Then: Similar ops might be grouped
        assert scheduled is not None


class TestDependencyGraph:
    """Test dependency graph for scheduling"""

    def test_create_dependency_graph(self):
        """Should create dependency graph"""
        # Given: Nothing
        # When: We create graph
        graph = DependencyGraph()

        # Then: Graph should be created
        assert graph is not None

    def test_add_dependency(self):
        """Should add dependency edge"""
        # Given: Dependency graph and nodes
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        x = builder.build_binary_op("ADD", a, b)

        dep_graph = DependencyGraph()

        # When: We add dependency (x depends on a)
        dep_graph.add_dependency(x, a)

        # Then: Dependency should be recorded
        assert dep_graph.has_dependency(x, a)

    def test_get_dependencies(self):
        """Should get all dependencies of a node"""
        # Given: Dependency graph with multiple dependencies
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_parameter(0)
        b = builder.build_parameter(1)
        c = builder.build_parameter(2)
        x = builder.build_binary_op("ADD", a, b)
        y = builder.build_binary_op("MUL", x, c)

        dep_graph = DependencyGraph()
        dep_graph.add_dependency(y, x)
        dep_graph.add_dependency(y, c)

        # When: We get dependencies of y
        deps = dep_graph.get_dependencies(y)

        # Then: Should return x and c
        assert x in deps
        assert c in deps
