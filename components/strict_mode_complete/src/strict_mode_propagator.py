"""
Strict Mode Propagator

Manages strict mode scope propagation.
Implements FR-ES24-B-059: Strict mode scope propagation.
"""

from typing import Any, Optional
from .strict_mode_validator import ScopeType


class Scope:
    """Scope object with strict mode flag"""

    def __init__(self, is_strict: bool, scope_type: ScopeType, parent: Optional['Scope'] = None):
        self.is_strict = is_strict
        self.scope_type = scope_type
        self.parent = parent


class StrictModePropagator:
    """
    Manages strict mode scope propagation.

    Rules:
    1. Global scope is strict if it has "use strict" directive
    2. Function scope is strict if:
       - It has own "use strict" directive, OR
       - Parent scope is strict
    3. Block scope inherits strict mode from parent
    4. Module scope is ALWAYS strict
    5. Eval scope can have own "use strict" directive

    Specification: ECMA-262 §10.2.1 - Strict Mode Code
    """

    def __init__(self):
        """Initialize strict mode propagator"""
        pass

    def create_scope(
        self,
        parent_scope: Optional[Any],
        has_directive: bool,
        scope_type: ScopeType
    ) -> Scope:
        """
        Create scope with propagated strict mode.

        Args:
            parent_scope: Parent scope (may be None for global)
            has_directive: Whether this scope has "use strict" directive
            scope_type: Type of scope

        Returns:
            New scope with correct strict mode flag

        Notes:
            - Module scope is always strict, even without directive
            - Block scope inherits from parent
            - Function scope can have own directive or inherit
        """
        # Module scope is always strict
        if scope_type == ScopeType.MODULE:
            return Scope(is_strict=True, scope_type=scope_type, parent=parent_scope)

        # Determine if this scope is strict
        is_strict = has_directive

        # If no local directive, check parent scope
        if not is_strict and parent_scope is not None:
            if hasattr(parent_scope, 'is_strict'):
                is_strict = parent_scope.is_strict

        return Scope(is_strict=is_strict, scope_type=scope_type, parent=parent_scope)

    def is_strict_scope(self, scope: Any) -> bool:
        """
        Check if scope has strict mode active.

        Args:
            scope: Scope to check

        Returns:
            True if scope is strict mode
        """
        if scope is None:
            return False

        if hasattr(scope, 'is_strict'):
            return scope.is_strict

        # Check scope type - modules are always strict
        if hasattr(scope, 'scope_type') and scope.scope_type == ScopeType.MODULE:
            return True

        return False

    def propagate_to_nested_function(
        self,
        parent_scope: Any,
        nested_function: Any
    ) -> bool:
        """
        Determine if nested function inherits strict mode.

        Args:
            parent_scope: Parent function scope
            nested_function: Nested function expression/declaration

        Returns:
            True if nested function should be strict

        Notes:
            - If parent is strict, nested is strict (unless explicitly non-strict)
            - If nested has own "use strict", it's strict
            - Otherwise, not strict
        """
        # Check if nested function has its own directive
        if hasattr(nested_function, 'has_strict_directive'):
            if nested_function.has_strict_directive:
                return True

        # Check if parent scope is strict
        if self.is_strict_scope(parent_scope):
            return True

        return False
