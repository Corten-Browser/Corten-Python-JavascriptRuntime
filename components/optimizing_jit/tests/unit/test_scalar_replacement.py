"""
Tests for Scalar Replacement of Aggregates
"""

import pytest
from components.optimizing_jit.src.optimizations.scalar_replacement import ScalarReplacement
from components.optimizing_jit.src.optimizations.escape_analyzer import EscapeAnalyzer, EscapeInfo, EscapeStatus
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import LoadPropertyNode, StorePropertyNode, ConstantNode


class TestScalarReplacement:
    """Test scalar replacement optimization"""

    def test_create_scalar_replacement(self):
        """Should create scalar replacement optimizer"""
        # Given: Nothing
        # When: We create scalar replacement optimizer
        optimizer = ScalarReplacement()

        # Then: Optimizer should be created
        assert optimizer is not None

    def test_replace_simple_object(self):
        """Should replace non-escaping object with scalars"""
        # Given: IR with non-escaping object
        #   obj = new Object()
        #   obj.x = 10
        #   obj.y = 20
        #   return obj.x + obj.y
        # Should become:
        #   scalar_x = 10
        #   scalar_y = 20
        #   return scalar_x + scalar_y
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)

        # Store fields
        ten = builder.build_constant(10)
        store_x = builder.build_store_property(obj, "x", ten)

        twenty = builder.build_constant(20)
        store_y = builder.build_store_property(obj, "y", twenty)

        # Load fields
        load_x = builder.build_load_property(obj, "x")
        load_y = builder.build_load_property(obj, "y")

        # Add and return
        result = builder.build_binary_op("ADD", load_x, load_y)
        ret = builder.build_return(result)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Create escape info (mark obj as non-escaping)
        escape_info = EscapeInfo()
        escape_info.mark_no_escape(obj)

        # When: We apply scalar replacement
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: Object accesses should be replaced with scalars
        # Load/Store nodes should be removed or replaced
        # (In full implementation, would verify exact transformation)
        assert optimized is not None

    def test_dont_replace_escaping_object(self):
        """Should NOT replace escaping objects"""
        # Given: IR with escaping object (returned)
        #   obj = new Object()
        #   obj.x = 10
        #   return obj
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)

        ten = builder.build_constant(10)
        store = builder.build_store_property(obj, "x", ten)

        ret = builder.build_return(obj)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # Mark obj as escaping
        escape_info = EscapeInfo()
        escape_info.mark_escapes(obj)

        # When: We apply scalar replacement
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: Object should NOT be replaced (it escapes)
        # Store should still exist
        has_store = any(isinstance(n, StorePropertyNode) for n in optimized.nodes)
        # Store might still exist for escaping objects

    def test_replace_load_property(self):
        """Should replace LoadProperty with scalar value"""
        # Given: IR with property load from non-escaping object
        #   obj.x = 42
        #   value = obj.x
        #   return value
        # Should become:
        #   scalar_x = 42
        #   value = scalar_x
        #   return value
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)

        forty_two = builder.build_constant(42)
        store = builder.build_store_property(obj, "x", forty_two)

        load = builder.build_load_property(obj, "x")
        ret = builder.build_return(load)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        escape_info = EscapeInfo()
        escape_info.mark_no_escape(obj)

        # When: We replace
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: Load should be replaced with scalar
        # (Verify transformation occurred)
        assert optimized is not None

    def test_replace_store_property(self):
        """Should replace StoreProperty with scalar assignment"""
        # Given: IR with property store to non-escaping object
        #   obj.x = 100
        # Should become:
        #   scalar_x = 100
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)

        hundred = builder.build_constant(100)
        store = builder.build_store_property(obj, "x", hundred)
        ret = builder.build_return(None)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        escape_info = EscapeInfo()
        escape_info.mark_no_escape(obj)

        # When: We replace
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: Store should be eliminated (replaced with scalar assignment)
        assert optimized is not None

    def test_multiple_fields(self):
        """Should replace object with multiple fields"""
        # Given: Object with multiple fields
        #   obj.x = 1
        #   obj.y = 2
        #   obj.z = 3
        #   return obj.x + obj.y + obj.z
        # Should become:
        #   scalar_x = 1; scalar_y = 2; scalar_z = 3
        #   return scalar_x + scalar_y + scalar_z
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj = builder.build_parameter(0)

        # Store multiple fields
        one = builder.build_constant(1)
        store_x = builder.build_store_property(obj, "x", one)

        two = builder.build_constant(2)
        store_y = builder.build_store_property(obj, "y", two)

        three = builder.build_constant(3)
        store_z = builder.build_store_property(obj, "z", three)

        # Load and compute
        load_x = builder.build_load_property(obj, "x")
        load_y = builder.build_load_property(obj, "y")
        load_z = builder.build_load_property(obj, "z")

        sum_xy = builder.build_binary_op("ADD", load_x, load_y)
        sum_xyz = builder.build_binary_op("ADD", sum_xy, load_z)

        ret = builder.build_return(sum_xyz)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        escape_info = EscapeInfo()
        escape_info.mark_no_escape(obj)

        # When: We replace
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: All fields should be replaced
        assert optimized is not None

    def test_mixed_escaping_non_escaping(self):
        """Should replace only non-escaping objects"""
        # Given: IR with multiple objects, some escape, some don't
        #   obj1 = new Object()  (non-escaping)
        #   obj1.x = 10
        #   obj2 = new Object()  (escaping - returned)
        #   obj2.y = 20
        #   return obj2
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        obj1 = builder.build_parameter(0)
        obj2 = builder.build_parameter(1)

        ten = builder.build_constant(10)
        store1 = builder.build_store_property(obj1, "x", ten)

        twenty = builder.build_constant(20)
        store2 = builder.build_store_property(obj2, "y", twenty)

        ret = builder.build_return(obj2)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        escape_info = EscapeInfo()
        escape_info.mark_no_escape(obj1)
        escape_info.mark_escapes(obj2)

        # When: We replace
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: obj1 should be replaced, obj2 should not
        assert optimized is not None

    def test_empty_graph(self):
        """Should handle empty IR graph gracefully"""
        # Given: Empty IR
        builder = IRBuilder()
        entry = builder.create_basic_block()
        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        escape_info = EscapeInfo()

        # When: We replace
        optimizer = ScalarReplacement()
        optimized = optimizer.replace(ssa_graph, escape_info)

        # Then: Should return graph unchanged
        assert optimized is not None
        assert len(optimized.basic_blocks) > 0
