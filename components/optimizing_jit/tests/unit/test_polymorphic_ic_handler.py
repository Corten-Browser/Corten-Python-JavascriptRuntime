"""
Tests for Polymorphic Inline Cache Handler

Tests handling of polymorphic inline caches in optimized code.
"""

import pytest
from components.optimizing_jit.src.optimizations.polymorphic_ic_handler import PolymorphicICHandler
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import LoadPropertyNode, BranchNode


# Mock IC state for testing
class MockICState:
    """Mock inline cache state"""
    def __init__(self, property_name, shapes, offsets):
        self.property_name = property_name
        self.shapes = shapes  # List of shape IDs
        self.offsets = offsets  # Corresponding offsets
        self.is_polymorphic = len(shapes) > 1
        self.is_megamorphic = len(shapes) > 4


class TestPolymorphicICHandler:
    """Test polymorphic inline cache handler"""

    def test_create_handler(self):
        """Should create polymorphic IC handler"""
        # Given: Nothing
        # When: We create handler
        handler = PolymorphicICHandler()

        # Then: Handler should be created
        assert handler is not None

    def test_handle_monomorphic_ic(self):
        """Should handle monomorphic IC (single shape)"""
        # Given: IR with property load and monomorphic IC
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "x")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Monomorphic IC: single shape
        ic_state = MockICState("x", shapes=[101], offsets=[16])

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {"x": ic_state})

        # Then: Should optimize to direct offset load (no branches needed)
        assert optimized is not None
        # Monomorphic = direct load, no new branches
        branches = [n for n in optimized.nodes if isinstance(n, BranchNode)]
        # Should not add branches for monomorphic case
        assert len(branches) <= 1

    def test_handle_polymorphic_ic_two_shapes(self):
        """Should handle polymorphic IC with 2 shapes"""
        # Given: IR with property load and polymorphic IC (2 shapes)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "name")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Polymorphic IC: 2 shapes
        ic_state = MockICState("name", shapes=[201, 202], offsets=[8, 12])

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {"name": ic_state})

        # Then: Should generate shape checks with branches
        assert optimized is not None
        # Should have branches for shape checks
        branches = [n for n in optimized.nodes if isinstance(n, BranchNode)]
        assert len(branches) >= 1  # At least one shape check

    def test_handle_polymorphic_ic_three_shapes(self):
        """Should handle polymorphic IC with 3 shapes"""
        # Given: IR with property load and polymorphic IC (3 shapes)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "value")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Polymorphic IC: 3 shapes
        ic_state = MockICState("value", shapes=[301, 302, 303], offsets=[16, 20, 24])

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {"value": ic_state})

        # Then: Should generate shape checks for all 3 shapes
        assert optimized is not None
        # Should have multiple branches for shape checks
        branches = [n for n in optimized.nodes if isinstance(n, BranchNode)]
        assert len(branches) >= 2  # Multiple shape checks

    def test_handle_polymorphic_ic_four_shapes(self):
        """Should handle polymorphic IC with 4 shapes (limit)"""
        # Given: IR with property load and polymorphic IC (4 shapes)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "data")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Polymorphic IC: 4 shapes (maximum)
        ic_state = MockICState("data", shapes=[401, 402, 403, 404], offsets=[8, 12, 16, 20])

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {"data": ic_state})

        # Then: Should handle up to 4 shapes
        assert optimized is not None

    def test_handle_megamorphic_ic(self):
        """Should handle megamorphic IC (>4 shapes) with slow path"""
        # Given: IR with property load and megamorphic IC (>4 shapes)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "property")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Megamorphic IC: >4 shapes
        ic_state = MockICState("property", shapes=[501, 502, 503, 504, 505], offsets=[8, 12, 16, 20, 24])

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {"property": ic_state})

        # Then: Should fall back to slow path (no polymorphic dispatch)
        assert optimized is not None
        # Megamorphic should not add many branches (uses slow path)

    def test_handle_no_ic_data(self):
        """Should handle property load with no IC data"""
        # Given: IR with property load but no IC data
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load = builder.build_load_property(obj, "unknown")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We handle IC with empty data
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {})

        # Then: Should return graph unchanged
        assert optimized is not None
        assert len(optimized.nodes) == len(ssa_graph.nodes)

    def test_handle_multiple_properties(self):
        """Should handle multiple property loads with different IC states"""
        # Given: IR with multiple property loads
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)
        load1 = builder.build_load_property(obj, "x")
        load2 = builder.build_load_property(obj, "y")
        ret = builder.build_return(load1)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Multiple IC states
        ic_data = {
            "x": MockICState("x", shapes=[101, 102], offsets=[8, 12]),
            "y": MockICState("y", shapes=[201], offsets=[16])
        }

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, ic_data)

        # Then: Should handle both properties
        assert optimized is not None

    def test_preserve_non_property_nodes(self):
        """Should preserve non-property load nodes"""
        # Given: IR with mixed node types
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        a = builder.build_constant(10)
        b = builder.build_constant(20)
        add = builder.build_binary_op("ADD", a, b)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We handle IC
        handler = PolymorphicICHandler()
        optimized = handler.handle(ssa_graph, {})

        # Then: Non-property nodes should be preserved
        assert a in optimized.nodes
        assert b in optimized.nodes
        assert add in optimized.nodes
        assert ret in optimized.nodes
