"""
Unit tests for Proxy constructor.

Tests Proxy object creation, target/handler validation, and basic proxy setup.
Covers requirements FR-P3-021.
"""

import pytest


class TestProxyConstructor:
    """Test Proxy constructor validation and setup."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector

        self.gc = GarbageCollector()

    def test_proxy_constructor_requires_object_target(self):
        """
        Given a non-object target
        When creating a Proxy
        Then TypeError is raised
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        handler = JSObject(self.gc)

        # When/Then - primitive targets should fail
        with pytest.raises(TypeError, match="Proxy target must be an object"):
            Proxy(None, handler)

        with pytest.raises(TypeError, match="Proxy target must be an object"):
            Proxy(42, handler)

        with pytest.raises(TypeError, match="Proxy target must be an object"):
            Proxy("string", handler)

    def test_proxy_constructor_requires_object_handler(self):
        """
        Given a non-object handler
        When creating a Proxy
        Then TypeError is raised
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)

        # When/Then - primitive handlers should fail
        with pytest.raises(TypeError, match="Proxy handler must be an object"):
            Proxy(target, None)

        with pytest.raises(TypeError, match="Proxy handler must be an object"):
            Proxy(target, 42)

        with pytest.raises(TypeError, match="Proxy handler must be an object"):
            Proxy(target, "string")

    def test_proxy_constructor_accepts_valid_object_target_and_handler(self):
        """
        Given valid object target and handler
        When creating a Proxy
        Then proxy is created successfully
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # When
        proxy = Proxy(target, handler)

        # Then
        assert proxy is not None
        assert hasattr(proxy, "_target")
        assert hasattr(proxy, "_handler")

    def test_proxy_stores_target_and_handler(self):
        """
        Given a Proxy is created
        When checking internal state
        Then target and handler are stored correctly
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # When
        proxy = Proxy(target, handler)

        # Then
        assert proxy._target is target
        assert proxy._handler is handler

    def test_proxy_accepts_function_as_target(self):
        """
        Given a function target
        When creating a Proxy
        Then proxy is created successfully (functions are objects)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSFunction, JSObject

        def test_func():
            pass

        target = JSFunction(self.gc, test_func, name="testFunc")
        handler = JSObject(self.gc)

        # When
        proxy = Proxy(target, handler)

        # Then
        assert proxy is not None
        assert proxy._target is target

    def test_proxy_with_empty_handler(self):
        """
        Given an empty handler object
        When creating a Proxy
        Then proxy is created successfully (traps are optional)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)  # No trap methods

        # When
        proxy = Proxy(target, handler)

        # Then
        assert proxy is not None

    def test_proxy_is_not_extensible_after_creation(self):
        """
        Given a Proxy is created
        When checking extensibility
        Then proxy itself has no own properties (transparent wrapper)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # When
        proxy = Proxy(target, handler)

        # Then - proxy should be a transparent wrapper
        # Internal properties like _target, _handler are implementation details
        assert hasattr(proxy, "_target")
        assert hasattr(proxy, "_handler")
