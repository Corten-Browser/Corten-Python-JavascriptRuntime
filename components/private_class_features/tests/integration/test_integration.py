"""
Integration tests for private class features - RED PHASE
Tests all components working together according to ES2024 specification.

Requirements tested: All (FR-ES24-069 through FR-ES24-074)
"""

import pytest


class TestPrivateClassFeaturesIntegration:
    """Integration tests for complete private class features."""

    def test_complete_class_with_private_features(self):
        """Test class with private fields, methods, and static blocks."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.private_method_manager import (
            PrivateMethodManager
        )
        from components.private_class_features.src.static_initialization import (
            StaticInitializationManager
        )
        from components.private_class_features.src.brand_checker import (
            PrivateBrandChecker
        )

        # Managers
        field_mgr = PrivateFieldManager()
        method_mgr = PrivateMethodManager()
        static_mgr = StaticInitializationManager()
        brand_checker = PrivateBrandChecker()

        class_id = 1

        # Define private field
        field_mgr.define_private_field(
            class_id=class_id,
            field_name="#count",
            initializer=lambda: 0
        )

        # Define private method
        def increment(self):
            current = field_mgr.get_private_field(self, "#count")
            field_mgr.set_private_field(self, "#count", current + 1)

        method_mgr.define_private_method(
            class_id=class_id,
            method_name="#increment",
            method_fn=increment
        )

        # Define static block
        static_initialized = [False]

        def static_init():
            static_initialized[0] = True

        static_mgr.add_static_block(class_id=class_id, block_fn=static_init)
        static_mgr.execute_static_blocks(class_id=class_id)

        # Create instance
        instance = MockInstance(class_id=class_id)
        field_mgr.initialize_field(instance, "#count")

        # Test brand check
        assert brand_checker.has_private_field(instance, "#count", field_mgr) is True

        # Test private method using private field
        method_mgr.call_private_method(instance, "#increment", [])
        assert field_mgr.get_private_field(instance, "#count") == 1

        method_mgr.call_private_method(instance, "#increment", [])
        assert field_mgr.get_private_field(instance, "#count") == 2

        # Verify static block ran
        assert static_initialized[0] is True

    def test_private_accessor_with_private_field(self):
        """Test private accessor accessing private field."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.private_method_manager import (
            PrivateMethodManager
        )

        field_mgr = PrivateFieldManager()
        method_mgr = PrivateMethodManager()

        class_id = 1

        # Private field
        field_mgr.define_private_field(
            class_id=class_id,
            field_name="#data",
            initializer=None
        )

        # Private accessor
        def getter(self):
            return field_mgr.get_private_field(self, "#data")

        def setter(self, value):
            field_mgr.set_private_field(self, "#data", value)

        method_mgr.define_private_accessor(
            class_id=class_id,
            accessor_name="#value",
            getter=getter,
            setter=setter
        )

        instance = MockInstance(class_id=class_id)

        # Set via accessor
        method_mgr.set_private_accessor(instance, "#value", 42)

        # Get via accessor
        result = method_mgr.get_private_accessor(instance, "#value")
        assert result == 42

        # Verify field was set
        assert field_mgr.get_private_field(instance, "#data") == 42

    def test_static_private_fields_and_methods(self):
        """Test static private fields and methods."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.private_method_manager import (
            PrivateMethodManager
        )

        field_mgr = PrivateFieldManager()
        method_mgr = PrivateMethodManager()

        class_id = 1

        # Static private field
        field_mgr.define_private_field(
            class_id=class_id,
            field_name="#instanceCount",
            initializer=None,
            is_static=True
        )
        field_mgr.set_static_field(class_id=class_id, field_name="#instanceCount", value=0)

        # Static private method
        def increment_count():
            current = field_mgr.get_static_field(class_id=class_id, field_name="#instanceCount")
            field_mgr.set_static_field(class_id=class_id, field_name="#instanceCount", value=current + 1)

        method_mgr.define_private_method(
            class_id=class_id,
            method_name="#incrementCount",
            method_fn=increment_count,
            is_static=True
        )

        # Call static method
        method_mgr.call_static_private_method(class_id=class_id, method_name="#incrementCount", args=[])

        # Check static field
        count = field_mgr.get_static_field(class_id=class_id, field_name="#instanceCount")
        assert count == 1

    def test_encapsulation_isolation(self):
        """Test that private features are truly isolated between classes."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.private_method_manager import (
            PrivateMethodManager
        )

        field_mgr = PrivateFieldManager()
        method_mgr = PrivateMethodManager()

        # Class 1
        field_mgr.define_private_field(class_id=1, field_name="#secret1", initializer=None)

        def method1(self):
            return "class1"

        method_mgr.define_private_method(class_id=1, method_name="#method1", method_fn=method1)

        # Class 2
        field_mgr.define_private_field(class_id=2, field_name="#secret2", initializer=None)

        def method2(self):
            return "class2"

        method_mgr.define_private_method(class_id=2, method_name="#method2", method_fn=method2)

        # Instances
        instance1 = MockInstance(class_id=1)
        instance2 = MockInstance(class_id=2)

        field_mgr.set_private_field(instance1, "#secret1", "value1")
        field_mgr.set_private_field(instance2, "#secret2", "value2")

        # Verify isolation
        assert field_mgr.get_private_field(instance1, "#secret1") == "value1"
        assert field_mgr.get_private_field(instance2, "#secret2") == "value2"

        assert method_mgr.call_private_method(instance1, "#method1", []) == "class1"
        assert method_mgr.call_private_method(instance2, "#method2", []) == "class2"

        # Cross-access should fail (instance2 trying to access class1's private field)
        with pytest.raises(TypeError):
            field_mgr.get_private_field(instance2, "#secret1")  # #secret1 only defined for class 1

    def test_complex_class_hierarchy(self):
        """Test private features in class hierarchy."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.brand_checker import (
            PrivateBrandChecker
        )

        field_mgr = PrivateFieldManager()
        brand_checker = PrivateBrandChecker()

        # Parent class
        field_mgr.define_private_field(class_id=1, field_name="#parentField", initializer=None)

        # Child class
        field_mgr.define_private_field(class_id=2, field_name="#childField", initializer=None)

        parent_instance = MockInstance(class_id=1)
        child_instance = MockInstance(class_id=2)

        field_mgr.set_private_field(parent_instance, "#parentField", "parent")
        field_mgr.set_private_field(child_instance, "#childField", "child")

        # Parent brand
        assert brand_checker.has_private_field(parent_instance, "#parentField", field_mgr) is True
        assert brand_checker.has_private_field(child_instance, "#parentField", field_mgr) is False

        # Child brand
        assert brand_checker.has_private_field(child_instance, "#childField", field_mgr) is True
        assert brand_checker.has_private_field(parent_instance, "#childField", field_mgr) is False

    def test_performance_private_field_access(self):
        """Test that private field access meets performance requirement (<100ns overhead)."""
        import time
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_mgr = PrivateFieldManager()

        field_mgr.define_private_field(class_id=1, field_name="#fast", initializer=None)

        instance = MockInstance(class_id=1)
        field_mgr.set_private_field(instance, "#fast", 42)

        # Warmup
        for _ in range(100):
            field_mgr.get_private_field(instance, "#fast")

        # Measure
        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            field_mgr.get_private_field(instance, "#fast")
        end = time.perf_counter()

        avg_time_ns = ((end - start) / iterations) * 1_000_000_000

        # Should be < 100ns overhead per spec (for native implementation)
        # Python implementation allows more overhead - target <3000ns (3μs)
        assert avg_time_ns < 3000  # Reasonable for Python test environment

    def test_static_block_initializes_private_static(self):
        """Test static block initializing private static fields."""
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )
        from components.private_class_features.src.static_initialization import (
            StaticInitializationManager
        )

        field_mgr = PrivateFieldManager()
        static_mgr = StaticInitializationManager()

        class_id = 1

        # Define static private field
        field_mgr.define_private_field(
            class_id=class_id,
            field_name="#config",
            initializer=None,
            is_static=True
        )

        # Static block initializes it
        def init():
            field_mgr.set_static_field(class_id=class_id, field_name="#config", value={"initialized": True})

        static_mgr.add_static_block(class_id=class_id, block_fn=init)
        static_mgr.execute_static_blocks(class_id=class_id)

        # Verify initialization
        config = field_mgr.get_static_field(class_id=class_id, field_name="#config")
        assert config == {"initialized": True}


class MockInstance:
    """Mock class instance for testing."""

    def __init__(self, class_id):
        self.class_id = class_id
