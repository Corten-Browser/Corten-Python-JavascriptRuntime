"""
Unit tests for ShapeDeoptimization class

RED phase: Tests written before implementation
Tests for FR-P4-022: Shape deoptimization
"""
import pytest


class TestShapeDeoptimizationCreation:
    """Test ShapeDeoptimization initialization"""

    def test_deopt_creation(self):
        """Test creating shape deoptimization"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        assert deopt is not None
        assert deopt.shape_tree is tree
        assert deopt.deopt_listeners == []


class TestDeoptListenerRegistration:
    """Test registering deoptimization listeners"""

    def test_register_listener(self):
        """Test registering deopt listener"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called = []

        def listener(shape, reason, details):
            called.append((shape, reason, details))

        deopt.register_deopt_listener(listener)
        assert len(deopt.deopt_listeners) == 1

    def test_register_multiple_listeners(self):
        """Test registering multiple listeners"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        def listener1(shape, reason, details):
            pass

        def listener2(shape, reason, details):
            pass

        deopt.register_deopt_listener(listener1)
        deopt.register_deopt_listener(listener2)
        assert len(deopt.deopt_listeners) == 2


class TestDeoptTrigger:
    """Test triggering deoptimization"""

    def test_trigger_deopt_calls_listener(self):
        """Test triggering deopt calls registered listeners"""
        from components.hidden_classes.src.shape_deoptimization import (
            ShapeDeoptimization,
            ShapeDeoptTrigger,
        )
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called = []

        def listener(shape, reason, details):
            called.append((shape, reason, details))

        deopt.register_deopt_listener(listener)

        shape = tree.get_root_shape()
        deopt.trigger_deopt(shape, ShapeDeoptTrigger.SHAPE_CHANGED, {"test": "data"})

        assert len(called) == 1
        assert called[0][0] is shape
        assert called[0][1] == ShapeDeoptTrigger.SHAPE_CHANGED
        assert called[0][2] == {"test": "data"}

    def test_trigger_deopt_calls_all_listeners(self):
        """Test triggering deopt calls all listeners"""
        from components.hidden_classes.src.shape_deoptimization import (
            ShapeDeoptimization,
            ShapeDeoptTrigger,
        )
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called1 = []
        called2 = []

        def listener1(shape, reason, details):
            called1.append(True)

        def listener2(shape, reason, details):
            called2.append(True)

        deopt.register_deopt_listener(listener1)
        deopt.register_deopt_listener(listener2)

        shape = tree.get_root_shape()
        deopt.trigger_deopt(shape, ShapeDeoptTrigger.SHAPE_CHANGED, {})

        assert len(called1) == 1
        assert len(called2) == 1


class TestShapeGuard:
    """Test shape guard validation"""

    def test_check_shape_guard_same_shape(self):
        """Test shape guard passes with same shape"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        shape = tree.get_root_shape()
        assert deopt.check_shape_guard(shape, shape) is True

    def test_check_shape_guard_different_shape(self):
        """Test shape guard fails with different shape"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        child = tree.get_or_create_child(root, "x", attrs)

        # Different shapes should fail guard
        assert deopt.check_shape_guard(root, child) is False

    def test_check_shape_guard_triggers_deopt(self):
        """Test shape guard failure triggers deoptimization"""
        from components.hidden_classes.src.shape_deoptimization import (
            ShapeDeoptimization,
            ShapeDeoptTrigger,
        )
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called = []

        def listener(shape, reason, details):
            called.append((shape, reason, details))

        deopt.register_deopt_listener(listener)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        child = tree.get_or_create_child(root, "x", attrs)

        # Check guard with different shape
        result = deopt.check_shape_guard(root, child)

        assert result is False
        assert len(called) == 1
        assert called[0][1] == ShapeDeoptTrigger.SHAPE_MISMATCH


class TestShapeDeprecationDeopt:
    """Test deoptimization on shape deprecation"""

    def test_on_shape_deprecation(self):
        """Test deprecation triggers deopt"""
        from components.hidden_classes.src.shape_deoptimization import (
            ShapeDeoptimization,
            ShapeDeoptTrigger,
        )
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called = []

        def listener(shape, reason, details):
            called.append((shape, reason, details))

        deopt.register_deopt_listener(listener)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        old_shape = tree.get_or_create_child(root, "x", attrs)
        new_shape = tree.get_or_create_child(root, "y", attrs)

        deopt.on_shape_deprecation(old_shape, new_shape)

        assert len(called) == 1
        assert called[0][0] is old_shape
        assert called[0][1] == ShapeDeoptTrigger.SHAPE_DEPRECATED
        assert called[0][2]["old_shape"] == id(old_shape)
        assert called[0][2]["new_shape"] == id(new_shape)


class TestPropertyAddedDeopt:
    """Test deoptimization on property addition"""

    def test_on_property_added(self):
        """Test property addition triggers deopt"""
        from components.hidden_classes.src.shape_deoptimization import (
            ShapeDeoptimization,
            ShapeDeoptTrigger,
        )
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        called = []

        def listener(shape, reason, details):
            called.append((shape, reason, details))

        deopt.register_deopt_listener(listener)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()
        new_shape = tree.get_or_create_child(root, "x", attrs)

        deopt.on_property_added(root, "x", new_shape)

        assert len(called) == 1
        assert called[0][0] is root
        assert called[0][1] == ShapeDeoptTrigger.PROPERTY_ADDED
        assert called[0][2]["property"] == "x"
        assert called[0][2]["new_shape"] == id(new_shape)


class TestDeoptTriggerConstants:
    """Test deoptimization trigger constants"""

    def test_trigger_constants_exist(self):
        """Test all trigger constants are defined"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptTrigger

        assert hasattr(ShapeDeoptTrigger, "SHAPE_CHANGED")
        assert hasattr(ShapeDeoptTrigger, "SHAPE_DEPRECATED")
        assert hasattr(ShapeDeoptTrigger, "SHAPE_MISMATCH")
        assert hasattr(ShapeDeoptTrigger, "PROPERTY_ADDED")
        assert hasattr(ShapeDeoptTrigger, "PROPERTY_DELETED")

    def test_trigger_constants_values(self):
        """Test trigger constant values are strings"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptTrigger

        assert isinstance(ShapeDeoptTrigger.SHAPE_CHANGED, str)
        assert isinstance(ShapeDeoptTrigger.SHAPE_DEPRECATED, str)
        assert isinstance(ShapeDeoptTrigger.SHAPE_MISMATCH, str)
        assert isinstance(ShapeDeoptTrigger.PROPERTY_ADDED, str)
        assert isinstance(ShapeDeoptTrigger.PROPERTY_DELETED, str)


class TestDeoptWorkflow:
    """Test complete deoptimization workflows"""

    def test_jit_guard_workflow(self):
        """Test JIT guard check workflow"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        deopt_triggered = []

        def deopt_listener(shape, reason, details):
            deopt_triggered.append(True)

        deopt.register_deopt_listener(deopt_listener)

        # JIT compiled code expects root shape
        expected_shape = tree.get_root_shape()

        # Object has child shape (property added)
        attrs = PropertyAttributes()
        actual_shape = tree.get_or_create_child(expected_shape, "x", attrs)

        # Guard check should fail and trigger deopt
        if not deopt.check_shape_guard(expected_shape, actual_shape):
            # Deoptimization triggered
            assert len(deopt_triggered) == 1

    def test_shape_transition_workflow(self):
        """Test shape transition deopt workflow"""
        from components.hidden_classes.src.shape_deoptimization import ShapeDeoptimization
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        deopt = ShapeDeoptimization(tree)

        deopts = []

        def listener(shape, reason, details):
            deopts.append(reason)

        deopt.register_deopt_listener(listener)

        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # Simulate property addition (shape transition)
        new_shape = tree.get_or_create_child(root, "x", attrs)
        deopt.on_property_added(root, "x", new_shape)

        assert len(deopts) == 1
