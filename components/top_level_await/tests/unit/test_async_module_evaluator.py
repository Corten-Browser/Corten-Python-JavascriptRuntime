"""
Unit tests for AsyncModuleEvaluator
Tests FR-ES24-067: Async module evaluation order
"""
import pytest
from unittest.mock import Mock, MagicMock
from components.top_level_await.src.async_module_evaluator import AsyncModuleEvaluator, DependencyGraph


class TestAsyncModuleEvaluator:
    """Test AsyncModuleEvaluator functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.evaluator = AsyncModuleEvaluator()
        self.mock_module = Mock()
        self.mock_module.id = "test_module"
        self.mock_module.dependencies = []

    def test_init(self):
        """Test evaluator initialization"""
        evaluator = AsyncModuleEvaluator()
        assert evaluator is not None

    def test_evaluate_returns_promise(self):
        """Test evaluate returns a promise"""
        promise = self.evaluator.evaluate(self.mock_module)
        assert promise is not None
        assert hasattr(promise, 'then')

    def test_evaluate_simple_module(self):
        """Test evaluating a module with no dependencies"""
        self.mock_module.dependencies = []
        promise = self.evaluator.evaluate(self.mock_module)
        assert promise is not None

    def test_evaluate_module_with_dependencies(self):
        """Test evaluating a module with dependencies"""
        dep_module = Mock()
        dep_module.id = "dependency"
        dep_module.dependencies = []

        self.mock_module.dependencies = [dep_module]
        promise = self.evaluator.evaluate(self.mock_module)
        assert promise is not None

    def test_resolve_dependency_graph_simple(self):
        """Test resolving dependency graph for simple module"""
        self.mock_module.dependencies = []
        graph = self.evaluator.resolve_dependency_graph(self.mock_module)
        assert isinstance(graph, DependencyGraph)
        assert self.mock_module.id in graph.nodes

    def test_resolve_dependency_graph_with_dependencies(self):
        """Test dependency graph includes all dependencies"""
        dep1 = Mock()
        dep1.id = "dep1"
        dep1.dependencies = []

        dep2 = Mock()
        dep2.id = "dep2"
        dep2.dependencies = []

        self.mock_module.dependencies = [dep1, dep2]
        graph = self.evaluator.resolve_dependency_graph(self.mock_module)

        assert self.mock_module.id in graph.nodes
        assert "dep1" in graph.nodes
        assert "dep2" in graph.nodes

    def test_dependency_graph_has_edges(self):
        """Test dependency graph includes edges"""
        dep = Mock()
        dep.id = "dep"
        dep.dependencies = []

        self.mock_module.dependencies = [dep]
        graph = self.evaluator.resolve_dependency_graph(self.mock_module)

        assert hasattr(graph, 'edges')
        assert self.mock_module.id in graph.edges

    def test_dependency_graph_evaluation_order(self):
        """Test dependency graph has evaluation order"""
        dep = Mock()
        dep.id = "dep"
        dep.dependencies = []

        self.mock_module.dependencies = [dep]
        graph = self.evaluator.resolve_dependency_graph(self.mock_module)

        assert hasattr(graph, 'evaluation_order')
        assert len(graph.evaluation_order) > 0
        # Dependencies should come before dependents
        assert graph.evaluation_order.index("dep") < graph.evaluation_order.index(self.mock_module.id)

    def test_evaluate_respects_dependency_order(self):
        """Test evaluation respects dependency order"""
        dep = Mock()
        dep.id = "dep"
        dep.dependencies = []
        dep.evaluate_count = 0

        self.mock_module.dependencies = [dep]
        self.mock_module.evaluate_count = 0

        def mock_dep_evaluate():
            dep.evaluate_count += 1

        def mock_module_evaluate():
            # Dependency should be evaluated first
            assert dep.evaluate_count > 0
            self.mock_module.evaluate_count += 1

        dep.evaluate = mock_dep_evaluate
        self.mock_module.evaluate = mock_module_evaluate

        self.evaluator.evaluate(self.mock_module)

    def test_evaluate_async_dependencies(self):
        """Test evaluating modules with async dependencies"""
        async_dep = Mock()
        async_dep.id = "async_dep"
        async_dep.dependencies = []
        async_dep.has_top_level_await = True

        self.mock_module.dependencies = [async_dep]
        promise = self.evaluator.evaluate(self.mock_module)
        assert promise is not None

    def test_dependency_graph_chain(self):
        """Test dependency graph with chain: A -> B -> C"""
        dep_c = Mock()
        dep_c.id = "C"
        dep_c.dependencies = []

        dep_b = Mock()
        dep_b.id = "B"
        dep_b.dependencies = [dep_c]

        dep_a = Mock()
        dep_a.id = "A"
        dep_a.dependencies = [dep_b]

        graph = self.evaluator.resolve_dependency_graph(dep_a)

        # All modules should be in graph
        assert "A" in graph.nodes
        assert "B" in graph.nodes
        assert "C" in graph.nodes

        # Order should be C, B, A
        order = graph.evaluation_order
        assert order.index("C") < order.index("B")
        assert order.index("B") < order.index("A")

    def test_dependency_graph_diamond(self):
        """Test dependency graph with diamond: A -> B,C -> D"""
        dep_d = Mock()
        dep_d.id = "D"
        dep_d.dependencies = []

        dep_b = Mock()
        dep_b.id = "B"
        dep_b.dependencies = [dep_d]

        dep_c = Mock()
        dep_c.id = "C"
        dep_c.dependencies = [dep_d]

        dep_a = Mock()
        dep_a.id = "A"
        dep_a.dependencies = [dep_b, dep_c]

        graph = self.evaluator.resolve_dependency_graph(dep_a)

        # All modules should be in graph
        assert len(graph.nodes) == 4

        # D should be evaluated before B and C
        order = graph.evaluation_order
        assert order.index("D") < order.index("B")
        assert order.index("D") < order.index("C")
        # A should be evaluated last
        assert order.index("A") == len(order) - 1

    def test_dependency_graph_struct_fields(self):
        """Test DependencyGraph has all required fields"""
        graph = DependencyGraph(nodes={}, edges={}, evaluation_order=[])
        assert hasattr(graph, 'nodes')
        assert hasattr(graph, 'edges')
        assert hasattr(graph, 'evaluation_order')
