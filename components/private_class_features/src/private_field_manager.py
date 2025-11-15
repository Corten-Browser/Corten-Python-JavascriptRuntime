"""
PrivateFieldManager - Manages private class fields.

Implements FR-ES24-069: Private fields (#field)
Implements FR-ES24-073: Private static fields

Uses WeakMap-like storage to ensure proper encapsulation.
"""

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional
import weakref


@dataclass
class PrivateField:
    """Descriptor for a private field."""

    field_name: str
    class_id: int
    initializer: Optional[Callable[[], Any]]
    is_static: bool = False


class PrivateFieldManager:
    """Manages private class fields with WeakMap-based storage."""

    def __init__(self):
        """Initialize private field manager."""
        # Map: (class_id, field_name) -> PrivateField
        self._field_definitions: Dict[tuple, PrivateField] = {}

        # Instance fields: WeakKeyDictionary for automatic cleanup
        # Map: instance -> {(class_id, field_name) -> value}
        self._instance_fields = weakref.WeakKeyDictionary()

        # Static fields: Map: (class_id, field_name) -> value
        self._static_fields: Dict[tuple, Any] = {}

    def define_private_field(
        self,
        class_id: int,
        field_name: str,
        initializer: Optional[Callable[[], Any]],
        is_static: bool = False,
    ) -> PrivateField:
        """
        Define a private field for a class.

        Args:
            class_id: Class identifier
            field_name: Private field name (with #)
            initializer: Optional initializer function
            is_static: True if static field

        Returns:
            PrivateField descriptor
        """
        if not field_name.startswith("#"):
            raise ValueError(f"Private field name must start with #: {field_name}")

        key = (class_id, field_name)
        field = PrivateField(
            field_name=field_name,
            class_id=class_id,
            initializer=initializer,
            is_static=is_static,
        )

        self._field_definitions[key] = field
        return field

    def get_private_field(self, instance: Any, field_name: str) -> Any:
        """
        Get private field value from instance.

        Args:
            instance: Class instance
            field_name: Private field name

        Returns:
            Field value

        Raises:
            TypeError: If field not accessible from this instance
        """
        if instance is None:
            raise TypeError("Cannot read private field from null/undefined")

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, field_name)

        # Check if field is defined for this class
        if key not in self._field_definitions:
            raise TypeError(f"Cannot access private field {field_name}")

        # Get instance field storage
        if instance not in self._instance_fields:
            raise TypeError(f"Cannot access private field {field_name}")

        instance_storage = self._instance_fields[instance]

        if key not in instance_storage:
            raise TypeError(f"Cannot access private field {field_name}")

        return instance_storage[key]

    def set_private_field(self, instance: Any, field_name: str, value: Any) -> None:
        """
        Set private field value on instance.

        Args:
            instance: Class instance
            field_name: Private field name
            value: New value

        Raises:
            TypeError: If field not accessible from this instance
        """
        if instance is None:
            raise TypeError("Cannot write private field to null/undefined")

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, field_name)

        # Check if field is defined for this class
        if key not in self._field_definitions:
            raise TypeError(f"Cannot access private field {field_name}")

        # Initialize instance storage if needed
        if instance not in self._instance_fields:
            self._instance_fields[instance] = {}

        instance_storage = self._instance_fields[instance]
        instance_storage[key] = value

    def initialize_field(self, instance: Any, field_name: str) -> None:
        """
        Initialize a private field with its initializer.

        Args:
            instance: Class instance
            field_name: Private field name
        """
        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            raise TypeError("Instance does not have class_id")

        key = (class_id, field_name)

        if key not in self._field_definitions:
            raise TypeError(f"Private field {field_name} not defined")

        field = self._field_definitions[key]

        # Initialize if initializer exists
        if field.initializer is not None:
            initial_value = field.initializer()
            self.set_private_field(instance, field_name, initial_value)
        else:
            # Initialize with undefined (None in Python)
            self.set_private_field(instance, field_name, None)

    def get_static_field(self, class_id: int, field_name: str) -> Any:
        """
        Get static private field value.

        Args:
            class_id: Class identifier
            field_name: Private field name

        Returns:
            Field value
        """
        key = (class_id, field_name)

        if key not in self._field_definitions:
            raise TypeError(f"Private static field {field_name} not defined")

        field = self._field_definitions[key]
        if not field.is_static:
            raise TypeError(f"Field {field_name} is not static")

        if key not in self._static_fields:
            raise TypeError(f"Static field {field_name} not initialized")

        return self._static_fields[key]

    def set_static_field(self, class_id: int, field_name: str, value: Any) -> None:
        """
        Set static private field value.

        Args:
            class_id: Class identifier
            field_name: Private field name
            value: New value
        """
        key = (class_id, field_name)

        if key not in self._field_definitions:
            raise TypeError(f"Private static field {field_name} not defined")

        field = self._field_definitions[key]
        if not field.is_static:
            raise TypeError(f"Field {field_name} is not static")

        self._static_fields[key] = value

    def has_field(self, instance: Any, field_name: str) -> bool:
        """
        Check if instance has private field (for brand checking).

        Args:
            instance: Object to check
            field_name: Private field name

        Returns:
            True if instance has the field
        """
        if instance is None:
            return False

        class_id = getattr(instance, "class_id", None)
        if class_id is None:
            return False

        key = (class_id, field_name)

        # Check if field is defined for this class
        if key not in self._field_definitions:
            return False

        # Check if instance has been initialized with this field
        if instance not in self._instance_fields:
            return False

        instance_storage = self._instance_fields[instance]
        return key in instance_storage
