"""
PrivateMethodManager - Manages private class methods and accessors.

Implements FR-ES24-070: Private methods (#method())
Implements FR-ES24-071: Private getters/setters (#get, #set)
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PrivateMethod:
    """Descriptor for a private method."""

    method_name: str
    class_id: int
    method_fn: Callable
    is_static: bool = False


@dataclass
class PrivateAccessor:
    """Descriptor for a private accessor (getter/setter)."""

    accessor_name: str
    class_id: int
    getter: Optional[Callable]
    setter: Optional[Callable]
    is_static: bool = False


class PrivateMethodManager:
    """Manages private class methods and accessors."""

    def __init__(self):
        """Initialize private method manager."""
        # Map: (class_id, method_name) -> PrivateMethod
        self._method_definitions: Dict[tuple, PrivateMethod] = {}

        # Map: (class_id, accessor_name) -> PrivateAccessor
        self._accessor_definitions: Dict[tuple, PrivateAccessor] = {}

    def define_private_method(
        self,
        class_id: int,
        method_name: str,
        method_fn: Callable,
        is_static: bool = False,
    ) -> PrivateMethod:
        """
        Define a private method for a class.

        Args:
            class_id: Class identifier
            method_name: Private method name (with #)
            method_fn: Method function
            is_static: True if static method

        Returns:
            PrivateMethod descriptor
        """
        if not method_name.startswith("#"):
            raise ValueError(f"Private method name must start with #: {method_name}")

        key = (class_id, method_name)
        method = PrivateMethod(
            method_name=method_name,
            class_id=class_id,
            method_fn=method_fn,
            is_static=is_static,
        )

        self._method_definitions[key] = method
        return method

    def call_private_method(
        self, instance: Any, method_name: str, args: List[Any]
    ) -> Any:
        """
        Call private method on instance.

        Args:
            instance: Class instance
            method_name: Private method name
            args: Method arguments

        Returns:
            Method result

        Raises:
            TypeError: If method not accessible from this instance
        """
        if instance is None:
            raise TypeError("Cannot call private method on null/undefined")

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, method_name)

        # Check if method is defined for this class
        if key not in self._method_definitions:
            raise TypeError(
                f"Cannot access private method {method_name}"
            )

        method = self._method_definitions[key]

        if method.is_static:
            raise TypeError(f"Cannot call static method {method_name} on instance")

        # Call method with instance as self
        return method.method_fn(instance, *args)

    def call_static_private_method(
        self, class_id: int, method_name: str, args: List[Any]
    ) -> Any:
        """
        Call static private method.

        Args:
            class_id: Class identifier
            method_name: Private method name
            args: Method arguments

        Returns:
            Method result
        """
        key = (class_id, method_name)

        if key not in self._method_definitions:
            raise TypeError(f"Private method {method_name} not defined")

        method = self._method_definitions[key]

        if not method.is_static:
            raise TypeError(f"Method {method_name} is not static")

        # Call static method (no self)
        return method.method_fn(*args)

    def define_private_accessor(
        self,
        class_id: int,
        accessor_name: str,
        getter: Optional[Callable],
        setter: Optional[Callable],
        is_static: bool = False,
    ) -> PrivateAccessor:
        """
        Define a private accessor (getter/setter) for a class.

        Args:
            class_id: Class identifier
            accessor_name: Private accessor name (with #)
            getter: Getter function
            setter: Setter function
            is_static: True if static accessor

        Returns:
            PrivateAccessor descriptor
        """
        if not accessor_name.startswith("#"):
            raise ValueError(
                f"Private accessor name must start with #: {accessor_name}"
            )

        key = (class_id, accessor_name)
        accessor = PrivateAccessor(
            accessor_name=accessor_name,
            class_id=class_id,
            getter=getter,
            setter=setter,
            is_static=is_static,
        )

        self._accessor_definitions[key] = accessor
        return accessor

    def get_private_accessor(self, instance: Any, accessor_name: str) -> Any:
        """
        Get value via private accessor (call getter).

        Args:
            instance: Class instance
            accessor_name: Private accessor name

        Returns:
            Accessor value

        Raises:
            TypeError: If accessor not accessible from this instance
        """
        if instance is None:
            raise TypeError("Cannot access private accessor on null/undefined")

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, accessor_name)

        # Check if accessor is defined for this class
        if key not in self._accessor_definitions:
            raise TypeError(
                f"Cannot access private accessor {accessor_name}"
            )

        accessor = self._accessor_definitions[key]

        if accessor.is_static:
            raise TypeError(
                f"Cannot access static accessor {accessor_name} on instance"
            )

        if accessor.getter is None:
            raise TypeError(f"Accessor {accessor_name} has no getter")

        # Call getter with instance as self
        return accessor.getter(instance)

    def set_private_accessor(
        self, instance: Any, accessor_name: str, value: Any
    ) -> None:
        """
        Set value via private accessor (call setter).

        Args:
            instance: Class instance
            accessor_name: Private accessor name
            value: New value

        Raises:
            TypeError: If accessor not accessible or read-only
        """
        if instance is None:
            raise TypeError("Cannot set private accessor on null/undefined")

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, accessor_name)

        # Check if accessor is defined for this class
        if key not in self._accessor_definitions:
            raise TypeError(
                f"Cannot access private accessor {accessor_name}"
            )

        accessor = self._accessor_definitions[key]

        if accessor.is_static:
            raise TypeError(
                f"Cannot set static accessor {accessor_name} on instance"
            )

        if accessor.setter is None:
            raise TypeError(f"Cannot set read-only accessor {accessor_name}")

        # Call setter with instance as self
        accessor.setter(instance, value)
