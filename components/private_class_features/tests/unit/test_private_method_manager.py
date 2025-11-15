"""
Unit tests for PrivateMethodManager - RED PHASE
Tests private method management according to ES2024 specification.

Requirements tested:
- FR-ES24-070: Private methods (#method())
- FR-ES24-071: Private getters/setters (#get, #set)
"""

import pytest
from components.private_class_features.src.private_method_manager import (
    PrivateMethodManager,
    PrivateMethod,
    PrivateAccessor,
)


class TestPrivateMethodManager:
    """Test PrivateMethodManager class."""

    def test_init(self):
        """Test PrivateMethodManager initialization."""
        manager = PrivateMethodManager()
        assert manager is not None

    def test_define_private_method_basic(self):
        """Test defining a basic private method."""
        manager = PrivateMethodManager()

        def test_method(self):
            return "result"

        method = manager.define_private_method(
            class_id=1,
            method_name="#calculate",
            method_fn=test_method
        )

        assert method is not None
        assert method.method_name == "#calculate"
        assert method.class_id == 1
        assert method.method_fn == test_method
        assert method.is_static is False

    def test_define_static_private_method(self):
        """Test defining static private method."""
        manager = PrivateMethodManager()

        def static_method():
            return "static"

        method = manager.define_private_method(
            class_id=1,
            method_name="#staticMethod",
            method_fn=static_method,
            is_static=True
        )

        assert method.is_static is True

    def test_call_private_method_basic(self):
        """Test calling private method on instance."""
        manager = PrivateMethodManager()

        def add(self, a, b):
            return a + b

        manager.define_private_method(
            class_id=1,
            method_name="#add",
            method_fn=add
        )

        instance = MockInstance(class_id=1)
        result = manager.call_private_method(instance, "#add", [5, 3])

        assert result == 8

    def test_call_private_method_with_self(self):
        """Test that private method receives 'self' as first argument."""
        manager = PrivateMethodManager()

        def get_value(self):
            return self.value

        manager.define_private_method(
            class_id=1,
            method_name="#getValue",
            method_fn=get_value
        )

        instance = MockInstance(class_id=1)
        instance.value = 42

        result = manager.call_private_method(instance, "#getValue", [])
        assert result == 42

    def test_call_private_method_throws_on_wrong_class(self):
        """Test that calling private method from wrong class throws TypeError."""
        manager = PrivateMethodManager()

        def method(self):
            return "secret"

        manager.define_private_method(
            class_id=1,
            method_name="#secret",
            method_fn=method
        )

        instance = MockInstance(class_id=2)

        with pytest.raises(TypeError, match="Cannot access private method"):
            manager.call_private_method(instance, "#secret", [])

    def test_call_undefined_private_method(self):
        """Test calling undefined private method throws error."""
        manager = PrivateMethodManager()
        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot access private method"):
            manager.call_private_method(instance, "#undefined", [])

    def test_define_private_accessor_getter_only(self):
        """Test defining private accessor with getter only."""
        manager = PrivateMethodManager()

        def getter(self):
            return self._internal_value

        accessor = manager.define_private_accessor(
            class_id=1,
            accessor_name="#value",
            getter=getter,
            setter=None
        )

        assert accessor is not None
        assert accessor.accessor_name == "#value"
        assert accessor.getter == getter
        assert accessor.setter is None

    def test_define_private_accessor_both(self):
        """Test defining private accessor with getter and setter."""
        manager = PrivateMethodManager()

        def getter(self):
            return self._internal_value

        def setter(self, value):
            self._internal_value = value

        accessor = manager.define_private_accessor(
            class_id=1,
            accessor_name="#property",
            getter=getter,
            setter=setter
        )

        assert accessor.getter == getter
        assert accessor.setter == setter

    def test_call_private_getter(self):
        """Test calling private getter."""
        manager = PrivateMethodManager()

        def getter(self):
            return self._value

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#x",
            getter=getter,
            setter=None
        )

        instance = MockInstance(class_id=1)
        instance._value = 100

        result = manager.get_private_accessor(instance, "#x")
        assert result == 100

    def test_call_private_setter(self):
        """Test calling private setter."""
        manager = PrivateMethodManager()

        def getter(self):
            return self._value

        def setter(self, value):
            self._value = value * 2

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#double",
            getter=getter,
            setter=setter
        )

        instance = MockInstance(class_id=1)
        instance._value = 0

        manager.set_private_accessor(instance, "#double", 5)
        assert instance._value == 10

    def test_call_private_setter_read_only_throws(self):
        """Test that calling setter on read-only accessor throws error."""
        manager = PrivateMethodManager()

        def getter(self):
            return 42

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#readonly",
            getter=getter,
            setter=None
        )

        instance = MockInstance(class_id=1)

        with pytest.raises(TypeError, match="Cannot set read-only accessor"):
            manager.set_private_accessor(instance, "#readonly", 100)

    def test_private_accessor_throws_on_wrong_class(self):
        """Test that accessing private accessor from wrong class throws error."""
        manager = PrivateMethodManager()

        def getter(self):
            return 1

        manager.define_private_accessor(
            class_id=1,
            accessor_name="#prop",
            getter=getter,
            setter=None
        )

        instance = MockInstance(class_id=2)

        with pytest.raises(TypeError, match="Cannot access private accessor"):
            manager.get_private_accessor(instance, "#prop")

    def test_multiple_private_methods_same_class(self):
        """Test multiple private methods on same class."""
        manager = PrivateMethodManager()

        def method1(self):
            return "one"

        def method2(self):
            return "two"

        manager.define_private_method(class_id=1, method_name="#m1", method_fn=method1)
        manager.define_private_method(class_id=1, method_name="#m2", method_fn=method2)

        instance = MockInstance(class_id=1)

        assert manager.call_private_method(instance, "#m1", []) == "one"
        assert manager.call_private_method(instance, "#m2", []) == "two"

    def test_private_method_with_multiple_args(self):
        """Test private method with multiple arguments."""
        manager = PrivateMethodManager()

        def multiply(self, a, b, c):
            return a * b * c

        manager.define_private_method(
            class_id=1,
            method_name="#multiply",
            method_fn=multiply
        )

        instance = MockInstance(class_id=1)
        result = manager.call_private_method(instance, "#multiply", [2, 3, 4])

        assert result == 24

    def test_private_method_returns_none(self):
        """Test private method that returns None."""
        manager = PrivateMethodManager()

        def void_method(self):
            self.side_effect = True
            return None

        manager.define_private_method(
            class_id=1,
            method_name="#void",
            method_fn=void_method
        )

        instance = MockInstance(class_id=1)
        instance.side_effect = False

        result = manager.call_private_method(instance, "#void", [])

        assert result is None
        assert instance.side_effect is True


class MockInstance:
    """Mock class instance for testing."""

    def __init__(self, class_id):
        self.class_id = class_id
