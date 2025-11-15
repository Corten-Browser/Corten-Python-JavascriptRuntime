"""
Unit tests for ShapeTree class

RED phase: Tests written before implementation
"""
import pytest


class TestShapeTreeCreation:
    """Test ShapeTree creation and root shape"""

    def test_shape_tree_creation(self):
        """Test creating shape tree"""
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        assert tree is not None

    def test_get_root_shape(self):
        """Test getting root shape (empty object)"""
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        root = tree.get_root_shape()

        assert root is not None
        assert root.parent is None
        assert root.property_count == 0

    def test_root_shape_is_singleton(self):
        """Test root shape is the same instance every time"""
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        root1 = tree.get_root_shape()
        root2 = tree.get_root_shape()

        assert root1 is root2  # Same instance


class TestShapeTransitions:
    """Test shape transitions via get_or_create_child"""

    def test_create_first_property_shape(self):
        """Test creating first property shape from root"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        shape_x = tree.get_or_create_child(root, "x", attrs)

        assert shape_x.parent is root
        assert shape_x.property_name == "x"
        assert shape_x.property_count == 1

    def test_reuse_existing_child_shape(self):
        """Test that same transition returns same shape (shape reuse)"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # First transition: root -> {x}
        shape_x1 = tree.get_or_create_child(root, "x", attrs)

        # Same transition again: root -> {x}
        shape_x2 = tree.get_or_create_child(root, "x", attrs)

        # Should be the same shape instance (cached)
        assert shape_x1 is shape_x2

    def test_different_properties_create_different_shapes(self):
        """Test different properties create different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        shape_x = tree.get_or_create_child(root, "x", attrs)
        shape_y = tree.get_or_create_child(root, "y", attrs)

        assert shape_x is not shape_y
        assert shape_x.property_name == "x"
        assert shape_y.property_name == "y"

    def test_different_attributes_create_different_shapes(self):
        """Test different attributes create different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()

        attrs1 = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        attrs2 = PropertyAttributes(writable=False, enumerable=True, configurable=True)

        shape1 = tree.get_or_create_child(root, "x", attrs1)
        shape2 = tree.get_or_create_child(root, "x", attrs2)

        # Same property name but different attributes -> different shapes
        assert shape1 is not shape2

    def test_nested_transitions(self):
        """Test nested shape transitions (multiple properties)"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # {} -> {x}
        shape_x = tree.get_or_create_child(root, "x", attrs)

        # {x} -> {x, y}
        shape_xy = tree.get_or_create_child(shape_x, "y", attrs)

        # {x, y} -> {x, y, z}
        shape_xyz = tree.get_or_create_child(shape_xy, "z", attrs)

        assert shape_x.property_count == 1
        assert shape_xy.property_count == 2
        assert shape_xyz.property_count == 3

    def test_transition_path_independence(self):
        """Test that different property addition orders create different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # Path 1: {} -> {x} -> {x, y}
        shape_x1 = tree.get_or_create_child(root, "x", attrs)
        shape_xy1 = tree.get_or_create_child(shape_x1, "y", attrs)

        # Path 2: {} -> {y} -> {y, x}
        shape_y2 = tree.get_or_create_child(root, "y", attrs)
        shape_yx2 = tree.get_or_create_child(shape_y2, "x", attrs)

        # Different shapes (different property order)
        assert shape_xy1 is not shape_yx2

        # But offsets are different
        assert shape_xy1.get_property_offset("x") == 0
        assert shape_xy1.get_property_offset("y") == 1

        assert shape_yx2.get_property_offset("y") == 0
        assert shape_yx2.get_property_offset("x") == 1


class TestShapeDeprecation:
    """Test shape deprecation via ShapeTree"""

    def test_deprecate_shape(self):
        """Test deprecating a shape"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        old_shape = tree.get_or_create_child(root, "x", attrs)
        new_shape = tree.get_or_create_child(root, "y", attrs)

        tree.deprecate_shape(old_shape, new_shape)

        assert old_shape.is_deprecated() is True
        assert old_shape.get_migration_target() is new_shape

    def test_deprecated_shape_still_accessible(self):
        """Test that deprecated shapes are still in tree (for existing objects)"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        old_shape = tree.get_or_create_child(root, "x", attrs)
        new_shape = tree.get_or_create_child(root, "y", attrs)

        tree.deprecate_shape(old_shape, new_shape)

        # Old shape should still be in tree
        shape_again = tree.get_or_create_child(root, "x", attrs)
        assert shape_again is old_shape  # Still cached


class TestShapeReuse:
    """Test shape caching and reuse for performance"""

    def test_common_pattern_reuses_shapes(self):
        """Test that common property patterns reuse shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # Simulate two objects with same property sequence
        # obj1: {} -> {x} -> {x, y}
        obj1_x = tree.get_or_create_child(root, "x", attrs)
        obj1_xy = tree.get_or_create_child(obj1_x, "y", attrs)

        # obj2: {} -> {x} -> {x, y}
        obj2_x = tree.get_or_create_child(root, "x", attrs)
        obj2_xy = tree.get_or_create_child(obj2_x, "y", attrs)

        # Should share the same shapes
        assert obj1_x is obj2_x
        assert obj1_xy is obj2_xy

    def test_different_patterns_different_shapes(self):
        """Test that different patterns use different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()
        attrs = PropertyAttributes()

        # obj1: {x, y}
        obj1_x = tree.get_or_create_child(root, "x", attrs)
        obj1_xy = tree.get_or_create_child(obj1_x, "y", attrs)

        # obj2: {x, z}
        obj2_x = tree.get_or_create_child(root, "x", attrs)
        obj2_xz = tree.get_or_create_child(obj2_x, "z", attrs)

        # Share first shape but not second
        assert obj1_x is obj2_x
        assert obj1_xy is not obj2_xz
