"""
Unit tests for TopLevelAwaitManager
Tests FR-ES24-066: Top-level await in modules
"""
import pytest
from unittest.mock import Mock, MagicMock
from components.top_level_await.src.top_level_await_manager import TopLevelAwaitManager, ModuleState, ModuleStatus


class TestTopLevelAwaitManager:
    """Test TopLevelAwaitManager functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = TopLevelAwaitManager()
        self.mock_module = Mock()
        self.mock_module.id = "test_module"

    def test_init(self):
        """Test manager initialization"""
        manager = TopLevelAwaitManager()
        assert manager is not None
        assert hasattr(manager, 'module_states')

    def test_enable_top_level_await(self):
        """Test enabling top-level await for a module"""
        self.manager.enable_top_level_await(self.mock_module)
        # Module should be marked as async-capable
        state = self.manager.get_module_state(self.mock_module.id)
        assert state is not None

    def test_enable_top_level_await_sets_async_flag(self):
        """Test that enabling TLA sets async flag on module"""
        self.manager.enable_top_level_await(self.mock_module)
        assert self.mock_module.id in self.manager.async_modules

    def test_execute_module_async_returns_promise(self):
        """Test async module execution returns promise"""
        self.manager.enable_top_level_await(self.mock_module)
        promise = self.manager.execute_module_async(self.mock_module)
        assert promise is not None
        assert hasattr(promise, 'then')

    def test_execute_module_async_without_enable_raises_error(self):
        """Test executing async module without enabling raises error"""
        with pytest.raises(ValueError, match="not enabled for top-level await"):
            self.manager.execute_module_async(self.mock_module)

    def test_get_module_state_returns_state(self):
        """Test getting module state"""
        self.manager.enable_top_level_await(self.mock_module)
        state = self.manager.get_module_state(self.mock_module.id)
        assert isinstance(state, ModuleState)
        assert state.module_id == self.mock_module.id

    def test_get_module_state_nonexistent_returns_none(self):
        """Test getting state of nonexistent module returns None"""
        state = self.manager.get_module_state("nonexistent")
        assert state is None

    def test_module_state_initial_status(self):
        """Test module starts in UNINSTANTIATED state"""
        self.manager.enable_top_level_await(self.mock_module)
        state = self.manager.get_module_state(self.mock_module.id)
        assert state.status == ModuleStatus.UNINSTANTIATED

    def test_module_state_transitions_to_evaluating_async(self):
        """Test module transitions to EVALUATING_ASYNC during execution"""
        self.manager.enable_top_level_await(self.mock_module)
        self.manager.execute_module_async(self.mock_module)
        state = self.manager.get_module_state(self.mock_module.id)
        assert state.status in [ModuleStatus.EVALUATING_ASYNC, ModuleStatus.EVALUATED]

    def test_execute_module_async_stores_promise(self):
        """Test async execution stores promise in state"""
        self.manager.enable_top_level_await(self.mock_module)
        promise = self.manager.execute_module_async(self.mock_module)
        state = self.manager.get_module_state(self.mock_module.id)
        assert state.promise is promise

    def test_execute_module_async_handles_errors(self):
        """Test async execution handles errors properly"""
        self.mock_module.evaluate = Mock(side_effect=Exception("Test error"))
        self.manager.enable_top_level_await(self.mock_module)
        promise = self.manager.execute_module_async(self.mock_module)
        # Promise should exist even if error occurred
        assert promise is not None

    def test_module_state_error_handling(self):
        """Test module state captures errors"""
        self.mock_module.evaluate = Mock(side_effect=Exception("Test error"))
        self.manager.enable_top_level_await(self.mock_module)
        try:
            self.manager.execute_module_async(self.mock_module)
        except:
            pass
        state = self.manager.get_module_state(self.mock_module.id)
        # State should track error or status should be ERRORED
        assert state.status == ModuleStatus.ERRORED or state.error is not None

    def test_multiple_modules(self):
        """Test managing multiple modules"""
        module1 = Mock()
        module1.id = "module1"
        module2 = Mock()
        module2.id = "module2"

        self.manager.enable_top_level_await(module1)
        self.manager.enable_top_level_await(module2)

        state1 = self.manager.get_module_state("module1")
        state2 = self.manager.get_module_state("module2")

        assert state1.module_id == "module1"
        assert state2.module_id == "module2"

    def test_module_state_promise_field(self):
        """Test ModuleState has promise field"""
        state = ModuleState(
            module_id="test",
            status=ModuleStatus.UNINSTANTIATED,
            promise=None,
            error=None
        )
        assert hasattr(state, 'promise')

    def test_module_state_error_field(self):
        """Test ModuleState has error field"""
        state = ModuleState(
            module_id="test",
            status=ModuleStatus.UNINSTANTIATED,
            promise=None,
            error=None
        )
        assert hasattr(state, 'error')

    def test_module_status_enum(self):
        """Test ModuleStatus enum has all required values"""
        assert hasattr(ModuleStatus, 'UNINSTANTIATED')
        assert hasattr(ModuleStatus, 'INSTANTIATING')
        assert hasattr(ModuleStatus, 'INSTANTIATED')
        assert hasattr(ModuleStatus, 'EVALUATING')
        assert hasattr(ModuleStatus, 'EVALUATING_ASYNC')
        assert hasattr(ModuleStatus, 'EVALUATED')
        assert hasattr(ModuleStatus, 'ERRORED')
