"""
Integration tests for top-level await functionality
Tests complete workflow with multiple modules and async dependencies
"""
import pytest
from unittest.mock import Mock
from components.top_level_await.src.top_level_await_manager import TopLevelAwaitManager
from components.top_level_await.src.async_module_evaluator import AsyncModuleEvaluator
from components.top_level_await.src.module_dependency_manager import ModuleDependencyManager


class TestTopLevelAwaitIntegration:
    """Integration tests for complete TLA workflow"""

    def setup_method(self):
        """Set up test fixtures"""
        self.tla_manager = TopLevelAwaitManager()
        self.evaluator = AsyncModuleEvaluator()
        self.dep_manager = ModuleDependencyManager()

    def test_simple_async_module_execution(self):
        """Test executing a simple module with top-level await"""
        module = Mock()
        module.id = "async_module"
        module.dependencies = []

        # Enable TLA
        self.tla_manager.enable_top_level_await(module)

        # Execute
        promise = self.tla_manager.execute_module_async(module)

        # Verify promise returned
        assert promise is not None

        # Verify state
        state = self.tla_manager.get_module_state(module.id)
        assert state is not None

    def test_module_with_dependencies_execution(self):
        """Test executing module with dependencies"""
        # Create dependency
        dep_module = Mock()
        dep_module.id = "dependency"
        dep_module.dependencies = []

        # Create main module
        main_module = Mock()
        main_module.id = "main"
        main_module.dependencies = [dep_module]

        # Enable TLA for both
        self.tla_manager.enable_top_level_await(dep_module)
        self.tla_manager.enable_top_level_await(main_module)

        # Add dependency relationship
        self.dep_manager.add_dependency("main", "dependency")

        # Get evaluation order
        order = self.dep_manager.get_evaluation_order("main")

        # Verify dependency evaluated first
        assert order.index("dependency") < order.index("main")

        # Evaluate with proper order
        promise = self.evaluator.evaluate(main_module)
        assert promise is not None

    def test_complex_dependency_graph_execution(self):
        """Test executing complex dependency graph"""
        # Create modules: app -> ui, api -> database
        database = Mock()
        database.id = "database"
        database.dependencies = []

        api = Mock()
        api.id = "api"
        api.dependencies = [database]

        ui = Mock()
        ui.id = "ui"
        ui.dependencies = []

        app = Mock()
        app.id = "app"
        app.dependencies = [ui, api]

        # Enable TLA for all
        for module in [database, api, ui, app]:
            self.tla_manager.enable_top_level_await(module)

        # Add dependencies
        self.dep_manager.add_dependency("app", "ui")
        self.dep_manager.add_dependency("app", "api")
        self.dep_manager.add_dependency("api", "database")

        # Get evaluation order
        order = self.dep_manager.get_evaluation_order("app")

        # Verify correct order
        assert order.index("database") < order.index("api")
        assert order.index("api") < order.index("app")
        assert order.index("ui") < order.index("app")

        # Evaluate
        promise = self.evaluator.evaluate(app)
        assert promise is not None

    def test_cycle_detection_prevents_execution(self):
        """Test that cyclic dependencies are detected"""
        # Create cycle: A -> B -> A
        self.dep_manager.add_dependency("module_a", "module_b")
        self.dep_manager.add_dependency("module_b", "module_a")

        # Detect cycles
        cycles = self.dep_manager.detect_cycles()

        # Should detect cycle
        assert len(cycles) > 0

    def test_large_dependency_graph(self):
        """Test handling large dependency graph (100+ modules)"""
        # Create 100 modules in a chain
        modules = []
        for i in range(100):
            module = Mock()
            module.id = f"module_{i}"
            module.dependencies = []
            modules.append(module)

            if i > 0:
                module.dependencies = [modules[i-1]]
                self.dep_manager.add_dependency(f"module_{i}", f"module_{i-1}")

        # Get evaluation order for last module
        order = self.dep_manager.get_evaluation_order("module_99")

        # Should include all modules
        assert len(order) == 100

        # Should be in correct order
        for i in range(99):
            assert order.index(f"module_{i}") < order.index(f"module_{i+1}")

    def test_async_module_state_tracking(self):
        """Test tracking state of async modules during execution"""
        module = Mock()
        module.id = "async_module"
        module.dependencies = []

        # Enable and execute
        self.tla_manager.enable_top_level_await(module)
        promise = self.tla_manager.execute_module_async(module)

        # Check state
        state = self.tla_manager.get_module_state(module.id)

        # State should track execution
        assert state.module_id == module.id
        assert state.promise is not None

    def test_error_handling_in_async_execution(self):
        """Test error handling during async module execution"""
        module = Mock()
        module.id = "error_module"
        module.dependencies = []
        module.evaluate = Mock(side_effect=Exception("Test error"))

        # Enable TLA
        self.tla_manager.enable_top_level_await(module)

        # Execute should handle error gracefully
        promise = self.tla_manager.execute_module_async(module)

        # Promise should exist
        assert promise is not None

    def test_diamond_dependency_resolution(self):
        """Test resolving diamond dependency pattern"""
        # D is shared dependency
        d = Mock()
        d.id = "D"
        d.dependencies = []

        # B and C both depend on D
        b = Mock()
        b.id = "B"
        b.dependencies = [d]

        c = Mock()
        c.id = "C"
        c.dependencies = [d]

        # A depends on B and C
        a = Mock()
        a.id = "A"
        a.dependencies = [b, c]

        # Add dependencies
        self.dep_manager.add_dependency("A", "B")
        self.dep_manager.add_dependency("A", "C")
        self.dep_manager.add_dependency("B", "D")
        self.dep_manager.add_dependency("C", "D")

        # Get evaluation order
        order = self.dep_manager.get_evaluation_order("A")

        # D should be evaluated before B and C
        assert order.index("D") < order.index("B")
        assert order.index("D") < order.index("C")

        # A should be last
        assert order.index("A") == len(order) - 1

        # Resolve dependency graph
        graph = self.evaluator.resolve_dependency_graph(a)

        # Should include all modules
        assert len(graph.nodes) == 4
