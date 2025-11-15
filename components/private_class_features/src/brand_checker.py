"""
PrivateBrandChecker - Ergonomic brand checks for private fields.

Implements FR-ES24-074: Ergonomic brand checks (#field in obj)

Brand checks allow checking if an object has a private field without
throwing an error (unlike access which throws TypeError).
"""

from typing import Any


class PrivateBrandChecker:
    """Performs ergonomic brand checks for private fields."""

    def __init__(self):
        """Initialize brand checker."""
        pass

    def has_private_field(
        self, instance: Any, field_name: str, field_manager: Any
    ) -> bool:
        """
        Check if instance has private field (#field in obj).

        Args:
            instance: Object to check
            field_name: Private field name
            field_manager: PrivateFieldManager instance

        Returns:
            True if instance has the private field, False otherwise

        Note:
            This does NOT throw an error, unlike field access.
        """
        if instance is None:
            return False

        # Use field_manager's has_field method
        return field_manager.has_field(instance, field_name)

    def check_brand(
        self, instance: Any, class_id: int, field_manager: Any
    ) -> bool:
        """
        Check if instance is of a specific class (has class brand).

        Args:
            instance: Object to check
            class_id: Class identifier
            field_manager: PrivateFieldManager instance

        Returns:
            True if instance belongs to the class

        Note:
            This checks if the instance has any private fields from the class.
        """
        if instance is None:
            return False

        instance_class_id = getattr(instance, "class_id", None)
        if instance_class_id is None:
            return False

        # Check if instance's class matches
        if instance_class_id == class_id:
            # Verify instance has been initialized with private fields
            # (has at least one field from this class)
            return instance in field_manager._instance_fields

        return False
