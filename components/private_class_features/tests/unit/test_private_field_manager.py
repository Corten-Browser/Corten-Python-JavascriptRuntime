"""
Unit tests for PrivateFieldManager - RED PHASE
Tests private field management according to ES2024 specification.

Requirements tested:
- FR-ES24-069: Private fields (#field)
- FR-ES24-073: Private static fields
"""

import pytest
from components.private_class_features.src.private_field_manager import (
    PrivateFieldManager,
    PrivateField,
)


class TestPrivateFieldManager:
    """Test PrivateFieldManager class."""

    def test_init(self):
        """Test PrivateFieldManager initialization."""
        manager = PrivateFieldManager()
        assert manager is not None

    def test_define_private_field_basic(self):
        """Test defining a basic private field."""
        manager = PrivateFieldManager()
        field = manager.define_private_field(
            class_id=1,
            field_name="#count",
            initializer=None
        )
        assert field is not None
        assert field.field_name == "#count"
        assert field.class_id == 1
        assert field.is_static is False

    def test_define_private_field_with_initializer(self):
        """Test defining private field with initializer function."""
        manager = PrivateFieldManager()

        def init_zero():
            return 0

        field = manager.define_private_field(
            class_id=1,
            field_name="#value",
            initializer=init_zero
        )
        assert field.initializer == init_zero

    def test_define_static_private_field(self):
        """Test defining static private field."""
        manager = PrivateFieldManager()
        field = manager.define_private_field(
            class_id=1,
            field_name="#staticField",
            initializer=None,
            is_static=True
        )
        assert field.is_static is True

    def test_get_private_field_instance(self):
        """Test getting private field value from instance."""
        manager = PrivateFieldManager()

        # Define field
        manager.define_private_field(
            class_id=1,
            field_name="#count",
            initializer=lambda: 0
        )

        # Create mock instance
        instance = MockInstance(class_id=1)

        # Set and get
        manager.set_private_field(instance, "#count", 42)
        value = manager.get_private_field(instance, "#count")
        assert value == 42

    def test_set_private_field_instance(self):
        """Test setting private field value on instance."""
        manager = PrivateFieldManager()

        manager.define_private_field(
            class_id=1,
            field_name="#name",
            initializer=None
        )

        instance = MockInstance(class_id=1)
        manager.set_private_field(instance, "#name", "test")

        value = manager.get_private_field(instance, "#name")
        assert value == "test"

    def test_get_private_field_throws_on_wrong_class(self):
        """Test that accessing private field from wrong class throws TypeError."""
        manager = PrivateFieldManager()

        # Define field for class 1
        manager.define_private_field(
            class_id=1,
            field_name="#secret",
            initializer=None
        )

        # Try to access from class 2 instance
        instance = MockInstance(class_id=2)

        with pytest.raises(TypeError, match="Cannot access private field"):
            manager.get_private_field(instance, "#secret")

    def test_set_private_field_throws_on_wrong_class(self):
        """Test that setting private field from wrong class throws TypeError."""
        manager = PrivateFieldManager()

        manager.define_private_field(
            class_id=1,
            field_name="#data",
            initializer=None
        )

        instance = MockInstance(class_id=2)

        with pytest.raises(TypeError, match="Cannot access private field"):
            manager.set_private_field(instance, "#data", 100)

    def test_multiple_fields_same_class(self):
        """Test multiple private fields on same class."""
        manager = PrivateFieldManager()

        manager.define_private_field(class_id=1, field_name="#x", initializer=None)
        manager.define_private_field(class_id=1, field_name="#y", initializer=None)

        instance = MockInstance(class_id=1)
        manager.set_private_field(instance, "#x", 10)
        manager.set_private_field(instance, "#y", 20)

        assert manager.get_private_field(instance, "#x") == 10
        assert manager.get_private_field(instance, "#y") == 20

    def test_same_field_name_different_classes(self):
        """Test same field name in different classes (should be isolated)."""
        manager = PrivateFieldManager()

        manager.define_private_field(class_id=1, field_name="#value", initializer=None)
        manager.define_private_field(class_id=2, field_name="#value", initializer=None)

        instance1 = MockInstance(class_id=1)
        instance2 = MockInstance(class_id=2)

        manager.set_private_field(instance1, "#value", "class1")
        manager.set_private_field(instance2, "#value", "class2")

        assert manager.get_private_field(instance1, "#value") == "class1"
        assert manager.get_private_field(instance2, "#value") == "class2"

    def test_private_field_not_defined(self):
        """Test accessing undefined private field throws error."""
        manager = PrivateFieldManager()
        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot access private field"):
            manager.get_private_field(instance, "#undefined")

    def test_weakmap_behavior_instance_cleanup(self):
        """Test that private fields use WeakMap-like behavior."""
        manager = PrivateFieldManager()
        manager.define_private_field(class_id=1, field_name="#temp", initializer=None)

        instance = MockInstance(class_id=1)
        manager.set_private_field(instance, "#temp", "data")

        # Verify field exists
        assert manager.get_private_field(instance, "#temp") == "data"

        # After instance is deleted, WeakMap should allow garbage collection
        # (Implementation detail - can't directly test GC in Python)

    def test_private_field_with_complex_value(self):
        """Test private field storing complex objects."""
        manager = PrivateFieldManager()
        manager.define_private_field(class_id=1, field_name="#data", initializer=None)

        instance = MockInstance(class_id=1)
        complex_value = {"nested": [1, 2, 3], "obj": {"a": "b"}}

        manager.set_private_field(instance, "#data", complex_value)
        retrieved = manager.get_private_field(instance, "#data")

        assert retrieved == complex_value

    def test_private_field_initializer_called(self):
        """Test that initializer is called when field is first accessed."""
        manager = PrivateFieldManager()

        call_count = [0]

        def initializer():
            call_count[0] += 1
            return 42

        manager.define_private_field(
            class_id=1,
            field_name="#lazy",
            initializer=initializer
        )

        instance = MockInstance(class_id=1)

        # Initialize field
        manager.initialize_field(instance, "#lazy")

        value = manager.get_private_field(instance, "#lazy")
        assert value == 42
        assert call_count[0] == 1


class MockInstance:
    """Mock class instance for testing."""

    def __init__(self, class_id):
        self.class_id = class_id
        self._private_fields = {}
