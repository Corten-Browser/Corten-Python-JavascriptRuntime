"""
Unit tests for StaticInitializationManager - RED PHASE
Tests static initialization blocks according to ES2024 specification.

Requirements tested:
- FR-ES24-072: Static initialization blocks
"""

import pytest
from components.private_class_features.src.static_initialization import (
    StaticInitializationManager,
)


class TestStaticInitializationManager:
    """Test StaticInitializationManager class."""

    def test_init(self):
        """Test StaticInitializationManager initialization."""
        manager = StaticInitializationManager()
        assert manager is not None

    def test_add_static_block_basic(self):
        """Test adding a static initialization block."""
        manager = StaticInitializationManager()
        executed = []

        def block():
            executed.append(1)

        manager.add_static_block(class_id=1, block_fn=block)
        manager.execute_static_blocks(class_id=1)

        assert executed == [1]

    def test_execute_static_blocks_in_order(self):
        """Test that static blocks execute in order of definition."""
        manager = StaticInitializationManager()
        order = []

        def block1():
            order.append(1)

        def block2():
            order.append(2)

        def block3():
            order.append(3)

        manager.add_static_block(class_id=1, block_fn=block1)
        manager.add_static_block(class_id=1, block_fn=block2)
        manager.add_static_block(class_id=1, block_fn=block3)

        manager.execute_static_blocks(class_id=1)

        assert order == [1, 2, 3]

    def test_static_blocks_execute_once(self):
        """Test that static blocks execute only once per class."""
        manager = StaticInitializationManager()
        count = [0]

        def block():
            count[0] += 1

        manager.add_static_block(class_id=1, block_fn=block)

        # Execute multiple times
        manager.execute_static_blocks(class_id=1)
        manager.execute_static_blocks(class_id=1)
        manager.execute_static_blocks(class_id=1)

        # Should only execute once
        assert count[0] == 1

    def test_different_classes_different_blocks(self):
        """Test that different classes have isolated static blocks."""
        manager = StaticInitializationManager()
        class1_executed = []
        class2_executed = []

        def block1():
            class1_executed.append(1)

        def block2():
            class2_executed.append(2)

        manager.add_static_block(class_id=1, block_fn=block1)
        manager.add_static_block(class_id=2, block_fn=block2)

        manager.execute_static_blocks(class_id=1)
        assert class1_executed == [1]
        assert class2_executed == []

        manager.execute_static_blocks(class_id=2)
        assert class2_executed == [2]

    def test_static_block_with_side_effects(self):
        """Test static block that modifies class state."""
        manager = StaticInitializationManager()
        class_state = {"initialized": False, "value": 0}

        def init_block():
            class_state["initialized"] = True
            class_state["value"] = 42

        manager.add_static_block(class_id=1, block_fn=init_block)
        manager.execute_static_blocks(class_id=1)

        assert class_state["initialized"] is True
        assert class_state["value"] == 42

    def test_static_block_can_access_private_static_fields(self):
        """Test that static blocks can initialize private static fields."""
        manager = StaticInitializationManager()
        from components.private_class_features.src.private_field_manager import (
            PrivateFieldManager
        )

        field_manager = PrivateFieldManager()
        field_manager.define_private_field(
            class_id=1,
            field_name="#staticCounter",
            initializer=None,
            is_static=True
        )

        def init_block():
            # Static block initializes static private field
            field_manager.set_static_field(class_id=1, field_name="#staticCounter", value=100)

        manager.add_static_block(class_id=1, block_fn=init_block)
        manager.execute_static_blocks(class_id=1)

        value = field_manager.get_static_field(class_id=1, field_name="#staticCounter")
        assert value == 100

    def test_static_block_error_propagates(self):
        """Test that errors in static blocks propagate."""
        manager = StaticInitializationManager()

        def error_block():
            raise ValueError("Initialization error")

        manager.add_static_block(class_id=1, block_fn=error_block)

        with pytest.raises(ValueError, match="Initialization error"):
            manager.execute_static_blocks(class_id=1)

    def test_multiple_static_blocks_one_class(self):
        """Test multiple static blocks on one class."""
        manager = StaticInitializationManager()
        results = []

        def block1():
            results.append("a")

        def block2():
            results.append("b")

        def block3():
            results.append("c")

        manager.add_static_block(class_id=1, block_fn=block1)
        manager.add_static_block(class_id=1, block_fn=block2)
        manager.add_static_block(class_id=1, block_fn=block3)

        manager.execute_static_blocks(class_id=1)

        assert results == ["a", "b", "c"]

    def test_no_static_blocks_no_error(self):
        """Test executing static blocks when none defined doesn't error."""
        manager = StaticInitializationManager()

        # Should not raise error
        manager.execute_static_blocks(class_id=999)

    def test_static_block_return_value_ignored(self):
        """Test that static block return values are ignored."""
        manager = StaticInitializationManager()

        def block_with_return():
            return "ignored"

        manager.add_static_block(class_id=1, block_fn=block_with_return)
        result = manager.execute_static_blocks(class_id=1)

        # execute_static_blocks should return None
        assert result is None
