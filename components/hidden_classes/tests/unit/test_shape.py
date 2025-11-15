"""
Unit tests for Shape class

RED phase: Tests written before implementation
"""
import pytest


class TestShapeCreation:
    """Test Shape creation and basic properties"""

    def test_root_shape_creation(self):
        """Test creating root shape (no parent, no properties)"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        assert root.parent is None
        assert root.property_name is None
        assert root.property_count == 0

    def test_child_shape_creation(self):
        """Test creating child shape with property"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        child = Shape(parent=root, property_name="x", property_attributes=attrs)

        assert child.parent is root
        assert child.property_name == "x"
        assert child.property_count == 1

    def test_nested_shape_creation(self):
        """Test creating nested shapes (multiple properties)"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        # obj.x = 1
        shape1 = Shape(parent=root, property_name="x", property_attributes=attrs)
        assert shape1.property_count == 1

        # obj.y = 2
        shape2 = Shape(parent=shape1, property_name="y", property_attributes=attrs)
        assert shape2.property_count == 2

        # obj.z = 3
        shape3 = Shape(parent=shape2, property_name="z", property_attributes=attrs)
        assert shape3.property_count == 3


class TestPropertyOffset:
    """Test property offset calculation (O(1) access)"""

    def test_root_shape_no_properties(self):
        """Test root shape has no properties"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        assert root.get_property_offset("x") is None
        assert root.get_property_offset("y") is None

    def test_single_property_offset(self):
        """Test offset for single property"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        shape = Shape(parent=root, property_name="x", property_attributes=attrs)

        assert shape.get_property_offset("x") == 0
        assert shape.get_property_offset("y") is None

    def test_multiple_property_offsets(self):
        """Test offsets for multiple properties"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        shape1 = Shape(parent=root, property_name="x", property_attributes=attrs)
        shape2 = Shape(parent=shape1, property_name="y", property_attributes=attrs)
        shape3 = Shape(parent=shape2, property_name="z", property_attributes=attrs)

        # All properties should be accessible from shape3
        assert shape3.get_property_offset("x") == 0
        assert shape3.get_property_offset("y") == 1
        assert shape3.get_property_offset("z") == 2
        assert shape3.get_property_offset("w") is None

    def test_property_offset_order_independence(self):
        """Test that property order matters for offsets"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        # Shape: {x, y}
        shape_xy = Shape(parent=root, property_name="x", property_attributes=attrs)
        shape_xy = Shape(parent=shape_xy, property_name="y", property_attributes=attrs)

        # Shape: {y, x} - different order
        shape_yx = Shape(parent=root, property_name="y", property_attributes=attrs)
        shape_yx = Shape(parent=shape_yx, property_name="x", property_attributes=attrs)

        # Different shapes, different offsets
        assert shape_xy.get_property_offset("x") == 0
        assert shape_xy.get_property_offset("y") == 1

        assert shape_yx.get_property_offset("y") == 0
        assert shape_yx.get_property_offset("x") == 1


class TestPropertyAttributes:
    """Test property attributes retrieval"""

    def test_get_property_attributes_root(self):
        """Test root shape has no property attributes"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        assert root.get_property_attributes("x") is None

    def test_get_property_attributes_single(self):
        """Test getting property attributes for single property"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes(writable=False, enumerable=True, configurable=False)
        shape = Shape(parent=root, property_name="x", property_attributes=attrs)

        retrieved = shape.get_property_attributes("x")
        assert retrieved == attrs
        assert retrieved.writable is False
        assert retrieved.enumerable is True
        assert retrieved.configurable is False

    def test_get_property_attributes_multiple(self):
        """Test getting property attributes for multiple properties"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs_x = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        attrs_y = PropertyAttributes(writable=False, enumerable=False, configurable=False)

        shape1 = Shape(parent=root, property_name="x", property_attributes=attrs_x)
        shape2 = Shape(parent=shape1, property_name="y", property_attributes=attrs_y)

        assert shape2.get_property_attributes("x") == attrs_x
        assert shape2.get_property_attributes("y") == attrs_y
        assert shape2.get_property_attributes("z") is None


class TestShapeTransitions:
    """Test shape transitions (adding properties)"""

    def test_add_property_from_root(self):
        """Test adding property to root shape"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        new_shape = root.add_property("x", attrs)
        assert new_shape.parent is root
        assert new_shape.property_name == "x"
        assert new_shape.property_count == 1
        assert new_shape.get_property_offset("x") == 0

    def test_add_multiple_properties(self):
        """Test adding multiple properties"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        shape1 = root.add_property("x", attrs)
        shape2 = shape1.add_property("y", attrs)
        shape3 = shape2.add_property("z", attrs)

        assert shape1.property_count == 1
        assert shape2.property_count == 2
        assert shape3.property_count == 3

    def test_add_property_creates_new_shape(self):
        """Test that adding property creates new shape (doesn't modify original)"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()

        shape1 = root.add_property("x", attrs)
        assert root.property_count == 0  # Original unchanged
        assert shape1.property_count == 1  # New shape has property


class TestShapeDeprecation:
    """Test shape deprecation and migration"""

    def test_shape_not_deprecated_by_default(self):
        """Test shapes are not deprecated by default"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        assert root.is_deprecated() is False

    def test_deprecate_shape(self):
        """Test deprecating a shape"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        old_shape = root.add_property("x", attrs)
        new_shape = root.add_property("y", attrs)

        # Deprecate old_shape in favor of new_shape
        old_shape.deprecate(new_shape)

        assert old_shape.is_deprecated() is True
        assert old_shape.get_migration_target() is new_shape

    def test_get_migration_target_none_when_not_deprecated(self):
        """Test migration target is None when shape not deprecated"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        assert root.get_migration_target() is None


class TestShapeRepresentation:
    """Test shape string representation"""

    def test_root_shape_repr(self):
        """Test root shape string representation"""
        from components.hidden_classes.src.shape import Shape

        root = Shape(parent=None, property_name=None, property_attributes=None)
        repr_str = repr(root)

        assert "Shape" in repr_str
        assert "properties=0" in repr_str or "property_count=0" in repr_str

    def test_child_shape_repr(self):
        """Test child shape string representation"""
        from components.hidden_classes.src.shape import Shape
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        root = Shape(parent=None, property_name=None, property_attributes=None)
        attrs = PropertyAttributes()
        shape = root.add_property("x", attrs)

        repr_str = repr(shape)
        assert "Shape" in repr_str
        assert "x" in repr_str
