"""
TopLevelAwaitManager - Manages top-level await in module execution
Implements FR-ES24-066: Top-level await in modules
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Dict, Any


class ModuleStatus(Enum):
    """Module execution status"""
    UNINSTANTIATED = "uninstantiated"
    INSTANTIATING = "instantiating"
    INSTANTIATED = "instantiated"
    EVALUATING = "evaluating"
    EVALUATING_ASYNC = "evaluating_async"
    EVALUATED = "evaluated"
    ERRORED = "errored"


@dataclass
class ModuleState:
    """Module state information"""
    module_id: str
    status: ModuleStatus
    promise: Optional[Any] = None
    error: Optional[Exception] = None


class Promise:
    """Simple promise implementation for async operations"""

    def __init__(self, executor=None):
        self._state = 'pending'
        self._value = None
        self._error = None
        self._then_callbacks = []
        self._catch_callbacks = []

        if executor:
            try:
                executor(self._resolve, self._reject)
            except Exception as e:
                self._reject(e)

    def _resolve(self, value):
        """Resolve the promise with a value"""
        if self._state == 'pending':
            self._state = 'fulfilled'
            self._value = value
            for callback in self._then_callbacks:
                try:
                    callback(value)
                except:
                    pass

    def _reject(self, error):
        """Reject the promise with an error"""
        if self._state == 'pending':
            self._state = 'rejected'
            self._error = error
            for callback in self._catch_callbacks:
                try:
                    callback(error)
                except:
                    pass

    def then(self, on_fulfilled=None, on_rejected=None):
        """Register callbacks for promise resolution"""
        if self._state == 'fulfilled' and on_fulfilled:
            try:
                on_fulfilled(self._value)
            except:
                pass
        elif self._state == 'rejected' and on_rejected:
            try:
                on_rejected(self._error)
            except:
                pass
        else:
            if on_fulfilled:
                self._then_callbacks.append(on_fulfilled)
            if on_rejected:
                self._catch_callbacks.append(on_rejected)
        return self

    def catch(self, on_rejected):
        """Register error callback"""
        return self.then(None, on_rejected)


class TopLevelAwaitManager:
    """
    Manages top-level await in module execution
    Implements FR-ES24-066: Top-level await in modules
    """

    def __init__(self):
        """Initialize top-level await manager"""
        self.module_states: Dict[str, ModuleState] = {}
        self.async_modules: set = set()

    def enable_top_level_await(self, module) -> None:
        """
        Enable top-level await for module

        Args:
            module: ES module to enable TLA for
        """
        self.async_modules.add(module.id)

        # Create initial module state
        state = ModuleState(
            module_id=module.id,
            status=ModuleStatus.UNINSTANTIATED,
            promise=None,
            error=None
        )
        self.module_states[module.id] = state

    def execute_module_async(self, module) -> Promise:
        """
        Execute module with top-level await support

        Args:
            module: ES module with top-level await

        Returns:
            Promise that resolves when module completes

        Raises:
            ValueError: If module not enabled for top-level await
        """
        if module.id not in self.async_modules:
            raise ValueError(f"Module {module.id} not enabled for top-level await")

        # Update state to evaluating async
        state = self.module_states[module.id]
        state.status = ModuleStatus.EVALUATING_ASYNC

        # Create promise for async execution
        def executor(resolve, reject):
            try:
                # Execute module
                if hasattr(module, 'evaluate') and callable(module.evaluate):
                    result = module.evaluate()
                    state.status = ModuleStatus.EVALUATED
                    resolve(result)
                else:
                    state.status = ModuleStatus.EVALUATED
                    resolve(None)
            except Exception as e:
                state.status = ModuleStatus.ERRORED
                state.error = e
                reject(e)

        promise = Promise(executor)
        state.promise = promise

        return promise

    def get_module_state(self, module_id: str) -> Optional[ModuleState]:
        """
        Get module execution state

        Args:
            module_id: Module identifier

        Returns:
            Current module state or None if not found
        """
        return self.module_states.get(module_id)
