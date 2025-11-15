"""
Additional tests to boost coverage to ≥85%.
Tests edge cases and error conditions.
"""

import pytest
from components.private_class_features.src.private_field_manager import PrivateFieldManager
from components.private_class_features.src.private_method_manager import PrivateMethodManager
from components.private_class_features.src.brand_checker import PrivateBrandChecker


class MockInstance:
    """Mock instance for testing."""

    def __init__(self, class_id):
        self.class_id = class_id


class TestAdditionalCoverage:
    """Additional tests for coverage."""

    def test_private_field_invalid_name(self):
        """Test that field name without # throws ValueError."""
        manager = PrivateFieldManager()

        with pytest.raises(ValueError, match="must start with #"):
            manager.define_private_field(
                class_id=1,
                field_name="noHash",
                initializer=None
            )

    def test_private_method_invalid_name(self):
        """Test that method name without # throws ValueError."""
        manager = PrivateMethodManager()

        def fn(self):
            pass

        with pytest.raises(ValueError, match="must start with #"):
            manager.define_private_method(
                class_id=1,
                method_name="noHash",
                method_fn=fn
            )

    def test_private_accessor_invalid_name(self):
        """Test that accessor name without # throws ValueError."""
        manager = PrivateMethodManager()

        def getter(self):
            return 1

        with pytest.raises(ValueError, match="must start with #"):
            manager.define_private_accessor(
                class_id=1,
                accessor_name="noHash",
                getter=getter,
                setter=None
            )

    def test_get_private_field_null_instance(self):
        """Test getting field from None instance."""
        manager = PrivateFieldManager()

        with pytest.raises(TypeError, match="Cannot read private field from null"):
            manager.get_private_field(None, "#field")

    def test_set_private_field_null_instance(self):
        """Test setting field on None instance."""
        manager = PrivateFieldManager()

        with pytest.raises(TypeError, match="Cannot write private field to null"):
            manager.set_private_field(None, "#field", 42)

    def test_get_private_field_no_class_id(self):
        """Test getting field from instance without class_id."""
        manager = PrivateFieldManager()
        instance = object()  # No class_id attribute

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.get_private_field(instance, "#field")

    def test_set_private_field_no_class_id(self):
        """Test setting field on instance without class_id."""
        manager = PrivateFieldManager()
        instance = object()  # No class_id attribute

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.set_private_field(instance, "#field", 42)

    def test_call_private_method_null_instance(self):
        """Test calling method on None instance."""
        manager = PrivateMethodManager()

        with pytest.raises(TypeError, match="Cannot call private method on null"):
            manager.call_private_method(None, "#method", [])

    def test_call_private_method_no_class_id(self):
        """Test calling method on instance without class_id."""
        manager = PrivateMethodManager()
        instance = object()

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.call_private_method(instance, "#method", [])

    def test_call_static_method_on_instance_throws(self):
        """Test that calling static method on instance throws error."""
        manager = PrivateMethodManager()

        def static_fn():
            return "static"

        manager.define_private_method(
            class_id=1,
            method_name="#static",
            method_fn=static_fn,
            is_static=True
        )

        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot call static method"):
            manager.call_private_method(instance, "#static", [])

    def test_call_static_private_method_not_static_throws(self):
        """Test calling non-static method as static throws error."""
        manager = PrivateMethodManager()

        def instance_method(self):
            return "instance"

        manager.define_private_method(
            class_id=1,
            method_name="#instance",
            method_fn=instance_method,
            is_static=False
        )

        with pytest.raises(TypeError, match="is not static"):
            manager.call_static_private_method(1, "#instance", [])

    def test_call_static_private_method_undefined(self):
        """Test calling undefined static method throws error."""
        manager = PrivateMethodManager()

        with pytest.raises(TypeError, match="not defined"):
            manager.call_static_private_method(1, "#undefined", [])

    def test_get_accessor_null_instance(self):
        """Test getting accessor from None instance."""
        manager = PrivateMethodManager()

        with pytest.raises(TypeError, match="Cannot access private accessor on null"):
            manager.get_private_accessor(None, "#prop")

    def test_get_accessor_no_class_id(self):
        """Test getting accessor from instance without class_id."""
        manager = PrivateMethodManager()
        instance = object()

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.get_private_accessor(instance, "#prop")

    def test_get_accessor_no_getter(self):
        """Test accessor with no getter throws error."""
        manager = PrivateMethodManager()

        def setter(self, value):
            pass

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#writeonly",
            getter=None,
            setter=setter
        )

        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="has no getter"):
            manager.get_private_accessor(instance, "#writeonly")

    def test_set_accessor_null_instance(self):
        """Test setting accessor on None instance."""
        manager = PrivateMethodManager()

        with pytest.raises(TypeError, match="Cannot set private accessor on null"):
            manager.set_private_accessor(None, "#prop", 42)

    def test_set_accessor_no_class_id(self):
        """Test setting accessor on instance without class_id."""
        manager = PrivateMethodManager()
        instance = object()

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.set_private_accessor(instance, "#prop", 42)

    def test_get_accessor_static_on_instance_throws(self):
        """Test getting static accessor on instance throws error."""
        manager = PrivateMethodManager()

        def getter():
            return 1

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#static",
            getter=getter,
            setter=None,
            is_static=True
        )

        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot access static accessor"):
            manager.get_private_accessor(instance, "#static")

    def test_set_accessor_static_on_instance_throws(self):
        """Test setting static accessor on instance throws error."""
        manager = PrivateMethodManager()

        def getter():
            return 1

        def setter(value):
            pass

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#static",
            getter=getter,
            setter=setter,
            is_static=True
        )

        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot set static accessor"):
            manager.set_private_accessor(instance, "#static", 42)

    def test_initialize_field_no_class_id(self):
        """Test initializing field on instance without class_id."""
        manager = PrivateFieldManager()
        instance = object()

        with pytest.raises(TypeError, match="does not have class_id"):
            manager.initialize_field(instance, "#field")

    def test_initialize_field_undefined(self):
        """Test initializing undefined field throws error."""
        manager = PrivateFieldManager()
        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="not defined"):
            manager.initialize_field(instance, "#undefined")

    def test_get_static_field_not_static(self):
        """Test getting non-static field as static throws error."""
        manager = PrivateFieldManager()

        manager.define_private_field(
            class_id=1,
            field_name="#instance",
            initializer=None,
            is_static=False
        )

        with pytest.raises(TypeError, match="is not static"):
            manager.get_static_field(1, "#instance")

    def test_set_static_field_not_static(self):
        """Test setting non-static field as static throws error."""
        manager = PrivateFieldManager()

        manager.define_private_field(
            class_id=1,
            field_name="#instance",
            initializer=None,
            is_static=False
        )

        with pytest.raises(TypeError, match="is not static"):
            manager.set_static_field(1, "#instance", 42)

    def test_get_static_field_not_initialized(self):
        """Test getting uninitialized static field throws error."""
        manager = PrivateFieldManager()

        manager.define_private_field(
            class_id=1,
            field_name="#static",
            initializer=None,
            is_static=True
        )

        with pytest.raises(TypeError, match="not initialized"):
            manager.get_static_field(1, "#static")

    def test_get_static_field_undefined(self):
        """Test getting undefined static field throws error."""
        manager = PrivateFieldManager()

        with pytest.raises(TypeError, match="not defined"):
            manager.get_static_field(1, "#undefined")

    def test_set_static_field_undefined(self):
        """Test setting undefined static field throws error."""
        manager = PrivateFieldManager()

        with pytest.raises(TypeError, match="not defined"):
            manager.set_static_field(1, "#undefined", 42)
