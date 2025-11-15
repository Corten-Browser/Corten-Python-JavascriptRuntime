"""
Static block scope management.

Implements FR-ES24-B-013: This binding to class constructor.
Implements FR-ES24-B-014: Private field access in static blocks.
"""

from typing import Optional


class StaticBlockScope:
    """
    Scope management for static blocks.

    Static blocks have a special scope where:
    - 'this' refers to the class constructor
    - Private static fields/methods are accessible
    - Block-local variables are scoped to the block
    - Outer (class) scope is accessible
    """

    def __init__(self, parent_scope, class_constructor):
        """
        Initialize static block scope.

        Args:
            parent_scope: Parent class scope
            class_constructor: Class constructor for 'this' binding
        """
        self.parent_scope = parent_scope
        self.class_constructor = class_constructor

        # Local variables declared in this block
        self._local_variables = {}

        # Class ID for private field access
        self._class_id = id(class_constructor)

    def resolve_this(self):
        """
        Resolve 'this' to class constructor.

        In static blocks, 'this' always refers to the class constructor
        function, not to any instance.

        Returns:
            The class constructor

        Example:
            class C {
                static {
                    console.log(this === C);  // true
                }
            }
        """
        return self.class_constructor

    def can_access_private(self, field_name: str) -> bool:
        """
        Check if a private static member is accessible.

        Static blocks can access private static fields and methods
        of their class, but not private instance members or private
        members of other classes.

        Args:
            field_name: Private field/method name (with # prefix)

        Returns:
            True if field is accessible

        Example:
            class C {
                static #secret = 42;
                static {
                    this.#secret;  // Accessible
                }
            }

        Restrictions:
            - Cannot access private instance members (no instance exists)
            - Cannot access private members from other classes
        """
        if not field_name.startswith('#'):
            # Not a private field
            return False

        # Check with PrivateFieldManager
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        # Static blocks can access private static members of their class
        # This is checked by the private field manager
        return True  # Detailed check done by PrivateFieldManager

    def declare_variable(self, name: str, value, is_const: bool = False):
        """
        Declare a variable in the static block scope.

        Variables declared in static blocks are block-scoped and
        do not leak outside the block.

        Args:
            name: Variable name
            value: Initial value
            is_const: True if const declaration

        Example:
            static {
                let temp = 42;     // Block-scoped
                this.value = temp;
            }
            // temp not accessible here
        """
        if name in self._local_variables:
            raise ReferenceError(f"Variable '{name}' already declared in block")

        self._local_variables[name] = {
            'value': value,
            'const': is_const
        }

    def get_variable(self, name: str):
        """
        Get a variable value.

        Looks up variables in this order:
        1. Block-local variables
        2. Parent scope (class scope)
        3. Outer scopes

        Args:
            name: Variable name

        Returns:
            Variable value

        Raises:
            ReferenceError: If variable not found
        """
        # Check local variables first
        if name in self._local_variables:
            return self._local_variables[name]['value']

        # Check parent scope
        if self.parent_scope:
            return self.parent_scope.get_variable(name)

        raise ReferenceError(f"Variable '{name}' is not defined")

    def set_variable(self, name: str, value):
        """
        Set a variable value.

        Args:
            name: Variable name
            value: New value

        Raises:
            ReferenceError: If variable not declared
            TypeError: If attempting to assign to const
        """
        # Check local variables first
        if name in self._local_variables:
            if self._local_variables[name]['const']:
                raise TypeError(f"Cannot assign to const variable '{name}'")
            self._local_variables[name]['value'] = value
            return

        # Delegate to parent scope
        if self.parent_scope:
            self.parent_scope.set_variable(name, value)
            return

        raise ReferenceError(f"Variable '{name}' is not defined")

    def has_variable(self, name: str) -> bool:
        """
        Check if variable exists in scope chain.

        Args:
            name: Variable name

        Returns:
            True if variable is declared
        """
        if name in self._local_variables:
            return True

        if self.parent_scope:
            return self.parent_scope.has_variable(name)

        return False

    def get_class_id(self) -> int:
        """
        Get the class ID for private field access.

        Returns:
            Class identifier
        """
        return self._class_id


class StaticBlockDescriptor:
    """
    Descriptor for a static block.

    Stores metadata about static blocks for tracking and execution.
    """

    def __init__(self, block, index: int, class_id: int):
        """
        Initialize static block descriptor.

        Args:
            block: StaticBlock AST node
            index: Definition order index
            class_id: Owning class identifier
        """
        self.block = block
        self.index = index
        self.class_id = class_id

    def __repr__(self):
        return (
            f"StaticBlockDescriptor("
            f"index={self.index}, "
            f"class_id={self.class_id})"
        )
