"""
Tests for Range Analysis
"""

import pytest
from components.optimizing_jit.src.optimizations.range_analysis import RangeAnalyzer, ValueRange
from components.optimizing_jit.src.ir_builder import IRBuilder
from components.optimizing_jit.src.ssa_builder import SSABuilder
from components.optimizing_jit.src.ir_nodes import ConstantNode


class TestValueRange:
    """Test ValueRange class"""

    def test_create_value_range(self):
        """Should create value range"""
        # Given: Nothing
        # When: We create range [0, 10]
        r = ValueRange(0, 10)

        # Then: Range should be created
        assert r.min_value == 0
        assert r.max_value == 10

    def test_is_always_positive(self):
        """Should detect always positive ranges"""
        # Given: Range [5, 10]
        r = ValueRange(5, 10)

        # Then: Should be always positive
        assert r.is_always_positive() is True

        # Given: Range [-5, 10]
        r2 = ValueRange(-5, 10)

        # Then: Should not be always positive
        assert r2.is_always_positive() is False

    def test_is_in_range(self):
        """Should check if range is within bounds"""
        # Given: Range [5, 10]
        r = ValueRange(5, 10)

        # Then: Should be in range [0, 20]
        assert r.is_in_range(0, 20) is True

        # Then: Should not be in range [0, 8]
        assert r.is_in_range(0, 8) is False

    def test_constant_range(self):
        """Should create single-value range for constants"""
        # Given: Range [42, 42] (constant)
        r = ValueRange(42, 42)

        # Then: Should be in any range containing 42
        assert r.is_in_range(40, 50) is True
        assert r.is_in_range(0, 100) is True


class TestRangeAnalysis:
    """Test range analysis"""

    def test_create_range_analyzer(self):
        """Should create range analyzer"""
        # Given: Nothing
        # When: We create analyzer
        analyzer = RangeAnalyzer()

        # Then: Analyzer should be created
        assert analyzer is not None

    def test_analyze_constant(self):
        """Should determine range for constant"""
        # Given: IR with constant 42
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        const = builder.build_constant(42)
        ret = builder.build_return(const)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Constant should have range [42, 42]
        assert const in range_info
        r = range_info[const]
        assert r.min_value == 42
        assert r.max_value == 42

    def test_analyze_addition(self):
        """Should compute range for addition"""
        # Given: IR with 10 + 20
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(10)
        right = builder.build_constant(20)
        add = builder.build_binary_op("ADD", left, right)
        ret = builder.build_return(add)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Addition should have range [30, 30]
        assert add in range_info
        r = range_info[add]
        assert r.min_value == 30
        assert r.max_value == 30

    def test_analyze_subtraction(self):
        """Should compute range for subtraction"""
        # Given: IR with 50 - 10
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(50)
        right = builder.build_constant(10)
        sub = builder.build_binary_op("SUB", left, right)
        ret = builder.build_return(sub)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Subtraction should have range [40, 40]
        assert sub in range_info
        r = range_info[sub]
        assert r.min_value == 40
        assert r.max_value == 40

    def test_analyze_multiplication(self):
        """Should compute range for multiplication"""
        # Given: IR with 5 * 6
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(5)
        right = builder.build_constant(6)
        mul = builder.build_binary_op("MUL", left, right)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Multiplication should have range [30, 30]
        assert mul in range_info
        r = range_info[mul]
        assert r.min_value == 30
        assert r.max_value == 30

    def test_analyze_parameter_unknown_range(self):
        """Should use unknown range for parameters"""
        # Given: IR with parameter
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        param = builder.build_parameter(0)
        ret = builder.build_return(param)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Parameter should have unknown range (very large)
        assert param in range_info
        r = range_info[param]
        # Unknown range is represented as very large range
        assert r.min_value <= -1000000
        assert r.max_value >= 1000000

    def test_analyze_phi_node(self):
        """Should compute range for phi node (merge of ranges)"""
        # Given: IR with phi node (merge two constants)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        const1 = builder.build_constant(10)
        const2 = builder.build_constant(20)

        from components.optimizing_jit.src.ir_nodes import PhiNode
        phi = PhiNode([const1, const2])
        builder.current_block.add_node(phi)
        # Also add to graph nodes explicitly
        builder.current_block.nodes.append(phi)

        ret = builder.build_return(phi)

        graph = builder.finalize(entry, entry)
        # Explicitly add phi to graph
        graph.nodes.append(phi)

        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Phi should have range [10, 20] (union of both values)
        assert phi in range_info
        r = range_info[phi]
        assert r.min_value == 10
        assert r.max_value == 20

    def test_analyze_comparison(self):
        """Should compute range for comparison result"""
        # Given: IR with comparison (result is boolean)
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(10)
        right = builder.build_constant(20)
        lt = builder.build_binary_op("LT", left, right)
        ret = builder.build_return(lt)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Comparison result should have range [0, 1] (boolean)
        assert lt in range_info
        r = range_info[lt]
        assert r.min_value == 0
        assert r.max_value == 1

    def test_analyze_division_range(self):
        """Should compute range for division"""
        # Given: IR with 100 / 5
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        left = builder.build_constant(100)
        right = builder.build_constant(5)
        div = builder.build_binary_op("DIV", left, right)
        ret = builder.build_return(div)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Division should have range [20, 20]
        assert div in range_info
        r = range_info[div]
        assert r.min_value == 20
        assert r.max_value == 20

    def test_analyze_complex_expression(self):
        """Should analyze ranges for complex expression"""
        # Given: IR with (10 + 20) * 2
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        c10 = builder.build_constant(10)
        c20 = builder.build_constant(20)
        c2 = builder.build_constant(2)

        add = builder.build_binary_op("ADD", c10, c20)
        mul = builder.build_binary_op("MUL", add, c2)
        ret = builder.build_return(mul)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        # When: We analyze ranges
        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # Then: Result should have range [60, 60]
        assert mul in range_info
        r = range_info[mul]
        assert r.min_value == 60
        assert r.max_value == 60

    def test_get_range_for_node(self):
        """Should retrieve range for specific node"""
        # Given: Analyzed graph
        builder = IRBuilder()
        entry = builder.create_basic_block()
        builder.set_current_block(entry)

        const = builder.build_constant(42)
        ret = builder.build_return(const)

        graph = builder.finalize(entry, entry)
        ssa_builder = SSABuilder()
        ssa_graph = ssa_builder.build_ssa(graph)

        analyzer = RangeAnalyzer()
        range_info = analyzer.analyze(ssa_graph)

        # When: We get range for node
        r = analyzer.get_range(const, range_info)

        # Then: Should return correct range
        assert r.min_value == 42
        assert r.max_value == 42
