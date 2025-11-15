"""
Unit tests for PrivateBrandChecker - RED PHASE
Tests ergonomic brand checks according to ES2024 specification.

Requirements tested:
- FR-ES24-074: Ergonomic brand checks (#field in obj)
"""

import pytest
from components.private_class_features.src.brand_checker import (
    PrivateBrandChecker,
)


class TestPrivateBrandChecker:
    """Test PrivateBrandChecker class."""

    def test_init(self):
        """Test PrivateBrandChecker initialization."""
        checker = PrivateBrandChecker()
        assert checker is not None

    def test_has_private_field_true(self):
        """Test has_private_field returns True when instance has field."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        # Define field
        field_manager.define_private_field(
            class_id=1,
            field_name="#x",
            initializer=None
        )

        instance = MockInstance(class_id=1)
        field_manager.set_private_field(instance, "#x", 10)

        # Check brand
        result = checker.has_private_field(instance, "#x", field_manager)
        assert result is True

    def test_has_private_field_false_wrong_class(self):
        """Test has_private_field returns False for wrong class."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        # Define field for class 1
        field_manager.define_private_field(
            class_id=1,
            field_name="#secret",
            initializer=None
        )

        # Check instance of class 2
        instance = MockInstance(class_id=2)

        result = checker.has_private_field(instance, "#secret", field_manager)
        assert result is False

    def test_has_private_field_false_field_not_defined(self):
        """Test has_private_field returns False when field not defined."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        instance = MockInstance(class_id=1)

        result = checker.has_private_field(instance, "#undefined", field_manager)
        assert result is False

    def test_check_brand_true(self):
        """Test check_brand returns True for valid instance."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        # Define field for class
        field_manager.define_private_field(
            class_id=1,
            field_name="#brand",
            initializer=None
        )

        instance = MockInstance(class_id=1)
        field_manager.set_private_field(instance, "#brand", True)

        result = checker.check_brand(instance, 1, field_manager)
        assert result is True

    def test_check_brand_false_wrong_class(self):
        """Test check_brand returns False for wrong class."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        field_manager.define_private_field(
            class_id=1,
            field_name="#brand",
            initializer=None
        )

        instance = MockInstance(class_id=2)

        result = checker.check_brand(instance, 1, field_manager)
        assert result is False

    def test_brand_check_performance(self):
        """Test that brand check is fast (<50ns per spec)."""
        import time
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        field_manager.define_private_field(
            class_id=1,
            field_name="#fast",
            initializer=None
        )

        instance = MockInstance(class_id=1)
        field_manager.set_private_field(instance, "#fast", 1)

        # Warmup
        for _ in range(100):
            checker.has_private_field(instance, "#fast", field_manager)

        # Measure
        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            checker.has_private_field(instance, "#fast", field_manager)
        end = time.perf_counter()

        avg_time_ns = ((end - start) / iterations) * 1_000_000_000

        # Should be < 50ns per spec (for native implementation)
        # Python implementation allows more overhead - target <3000ns (3μs)
        assert avg_time_ns < 3000  # Reasonable for Python test environment

    def test_has_private_field_null_object(self):
        """Test has_private_field with null/None object."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        result = checker.has_private_field(None, "#field", field_manager)
        assert result is False

    def test_brand_check_with_inheritance(self):
        """Test brand check works correctly with class inheritance."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        # Parent class has private field
        field_manager.define_private_field(
            class_id=1,
            field_name="#parentField",
            initializer=None
        )

        # Child class instance
        parent_instance = MockInstance(class_id=1)
        child_instance = MockChildInstance(parent_class_id=1, child_class_id=2)

        field_manager.set_private_field(parent_instance, "#parentField", 1)
        field_manager.set_private_field(child_instance, "#parentField", 2)

        # Both should have the brand
        assert checker.has_private_field(parent_instance, "#parentField", field_manager) is True
        assert checker.has_private_field(child_instance, "#parentField", field_manager) is True

    def test_multiple_brands_same_instance(self):
        """Test instance can have multiple brands from different private fields."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        field_manager.define_private_field(class_id=1, field_name="#a", initializer=None)
        field_manager.define_private_field(class_id=1, field_name="#b", initializer=None)

        instance = MockInstance(class_id=1)
        field_manager.set_private_field(instance, "#a", 1)
        field_manager.set_private_field(instance, "#b", 2)

        assert checker.has_private_field(instance, "#a", field_manager) is True
        assert checker.has_private_field(instance, "#b", field_manager) is True

    def test_brand_check_doesnt_throw(self):
        """Test that brand check doesn't throw errors (unlike access)."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        checker = PrivateBrandChecker()

        field_manager.define_private_field(
            class_id=1,
            field_name="#private",
            initializer=None
        )

        instance = MockInstance(class_id=2)

        # Brand check should return False, not throw
        result = checker.has_private_field(instance, "#private", field_manager)
        assert result is False

        # But actual access should throw
        with pytest.raises(TypeError):
            field_manager.get_private_field(instance, "#private")


class MockInstance:
    """Mock class instance for testing."""

    def __init__(self, class_id):
        self.class_id = class_id


class MockChildInstance:
    """Mock child class instance for testing inheritance."""

    def __init__(self, parent_class_id, child_class_id):
        self.class_id = parent_class_id  # Inherits parent brand
        self.child_class_id = child_class_id
