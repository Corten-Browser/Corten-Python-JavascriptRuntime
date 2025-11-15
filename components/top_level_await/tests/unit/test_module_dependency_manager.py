"""
Unit tests for ModuleDependencyManager
Tests FR-ES24-068: Proper module dependency handling with TLA
"""
import pytest
from components.top_level_await.src.module_dependency_manager import ModuleDependencyManager


class TestModuleDependencyManager:
    """Test ModuleDependencyManager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ModuleDependencyManager()

    def test_init(self):
        """Test manager initialization"""
        manager = ModuleDependencyManager()
        assert manager is not None
        assert hasattr(manager, 'dependencies')

    def test_add_dependency(self):
        """Test adding a dependency"""
        self.manager.add_dependency("module_a", "module_b")
        # module_a depends on module_b
        assert "module_a" in self.manager.dependencies

    def test_add_multiple_dependencies(self):
        """Test adding multiple dependencies for same module"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_a", "module_c")

        deps = self.manager.dependencies.get("module_a", [])
        assert "module_b" in deps
        assert "module_c" in deps

    def test_add_dependency_different_modules(self):
        """Test adding dependencies for different modules"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_c", "module_d")

        assert "module_a" in self.manager.dependencies
        assert "module_c" in self.manager.dependencies

    def test_get_evaluation_order_simple(self):
        """Test getting evaluation order for simple dependency"""
        # module_a depends on module_b
        self.manager.add_dependency("module_a", "module_b")

        order = self.manager.get_evaluation_order("module_a")

        # module_b should be evaluated before module_a
        assert order.index("module_b") < order.index("module_a")

    def test_get_evaluation_order_chain(self):
        """Test evaluation order for chain: A -> B -> C"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_b", "module_c")

        order = self.manager.get_evaluation_order("module_a")

        # C before B before A
        assert order.index("module_c") < order.index("module_b")
        assert order.index("module_b") < order.index("module_a")

    def test_get_evaluation_order_diamond(self):
        """Test evaluation order for diamond: A -> B,C -> D"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_a", "module_c")
        self.manager.add_dependency("module_b", "module_d")
        self.manager.add_dependency("module_c", "module_d")

        order = self.manager.get_evaluation_order("module_a")

        # D before B and C, A last
        assert order.index("module_d") < order.index("module_b")
        assert order.index("module_d") < order.index("module_c")
        assert order.index("module_a") == len(order) - 1

    def test_get_evaluation_order_no_dependencies(self):
        """Test evaluation order for module with no dependencies"""
        order = self.manager.get_evaluation_order("standalone")
        assert order == ["standalone"]

    def test_detect_cycles_no_cycle(self):
        """Test cycle detection with no cycles"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_b", "module_c")

        cycles = self.manager.detect_cycles()
        assert len(cycles) == 0

    def test_detect_cycles_simple_cycle(self):
        """Test detecting simple cycle: A -> B -> A"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_b", "module_a")

        cycles = self.manager.detect_cycles()
        assert len(cycles) > 0
        # Cycle should contain both modules
        assert any("module_a" in cycle and "module_b" in cycle for cycle in cycles)

    def test_detect_cycles_self_cycle(self):
        """Test detecting self-cycle: A -> A"""
        self.manager.add_dependency("module_a", "module_a")

        cycles = self.manager.detect_cycles()
        assert len(cycles) > 0

    def test_detect_cycles_longer_cycle(self):
        """Test detecting longer cycle: A -> B -> C -> A"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_b", "module_c")
        self.manager.add_dependency("module_c", "module_a")

        cycles = self.manager.detect_cycles()
        assert len(cycles) > 0

    def test_detect_cycles_multiple_cycles(self):
        """Test detecting multiple independent cycles"""
        # Cycle 1: A -> B -> A
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_b", "module_a")

        # Cycle 2: C -> D -> C
        self.manager.add_dependency("module_c", "module_d")
        self.manager.add_dependency("module_d", "module_c")

        cycles = self.manager.detect_cycles()
        # Should detect both cycles
        assert len(cycles) >= 2

    def test_evaluation_order_complex_graph(self):
        """Test evaluation order for complex dependency graph"""
        # Create a complex graph
        self.manager.add_dependency("app", "ui")
        self.manager.add_dependency("app", "api")
        self.manager.add_dependency("ui", "components")
        self.manager.add_dependency("api", "database")
        self.manager.add_dependency("api", "auth")
        self.manager.add_dependency("auth", "database")

        order = self.manager.get_evaluation_order("app")

        # Verify dependencies are evaluated before dependents
        assert order.index("database") < order.index("api")
        assert order.index("database") < order.index("auth")
        assert order.index("auth") < order.index("api")
        assert order.index("components") < order.index("ui")
        assert order.index("ui") < order.index("app")
        assert order.index("api") < order.index("app")

    def test_evaluation_order_includes_all_dependencies(self):
        """Test that evaluation order includes all transitive dependencies"""
        self.manager.add_dependency("a", "b")
        self.manager.add_dependency("b", "c")
        self.manager.add_dependency("c", "d")

        order = self.manager.get_evaluation_order("a")

        assert "a" in order
        assert "b" in order
        assert "c" in order
        assert "d" in order

    def test_evaluation_order_large_graph(self):
        """Test evaluation order for large dependency graph (100+ modules)"""
        # Create a large graph
        for i in range(100):
            if i > 0:
                # Each module depends on previous module
                self.manager.add_dependency(f"module_{i}", f"module_{i-1}")

        order = self.manager.get_evaluation_order("module_99")

        # Should include all 100 modules
        assert len(order) == 100

        # Should be in correct order
        for i in range(99):
            assert order.index(f"module_{i}") < order.index(f"module_{i+1}")

    def test_add_dependency_idempotent(self):
        """Test that adding same dependency multiple times is idempotent"""
        self.manager.add_dependency("module_a", "module_b")
        self.manager.add_dependency("module_a", "module_b")

        deps = self.manager.dependencies.get("module_a", [])
        # Should only have one entry for module_b
        assert deps.count("module_b") == 1
