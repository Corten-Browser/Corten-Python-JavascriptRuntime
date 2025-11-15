"""
Integration tests for hidden classes system

Tests the complete workflow: ShapeTree + Shape + PropertyAttributes
"""
import pytest


class TestObjectLifecycle:
    """Test complete object lifecycle with shapes"""

    def test_create_empty_object(self):
        """Test creating empty object with root shape"""
        from components.hidden_classes.src.shape_tree import ShapeTree

        tree = ShapeTree()
        obj_shape = tree.get_root_shape()

        assert obj_shape.property_count == 0

    def test_add_properties_sequentially(self):
        """Test adding properties one by one (common pattern)"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # let obj = {}
        shape = tree.get_root_shape()
        assert shape.property_count == 0

        # obj.x = 1
        shape = tree.get_or_create_child(shape, "x", attrs)
        assert shape.property_count == 1
        assert shape.get_property_offset("x") == 0

        # obj.y = 2
        shape = tree.get_or_create_child(shape, "y", attrs)
        assert shape.property_count == 2
        assert shape.get_property_offset("x") == 0
        assert shape.get_property_offset("y") == 1

        # obj.z = 3
        shape = tree.get_or_create_child(shape, "z", attrs)
        assert shape.property_count == 3
        assert shape.get_property_offset("x") == 0
        assert shape.get_property_offset("y") == 1
        assert shape.get_property_offset("z") == 2

    def test_multiple_objects_same_shape(self):
        """Test multiple objects with same properties share shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Object 1: {x, y}
        obj1_shape = tree.get_root_shape()
        obj1_shape = tree.get_or_create_child(obj1_shape, "x", attrs)
        obj1_shape = tree.get_or_create_child(obj1_shape, "y", attrs)

        # Object 2: {x, y}
        obj2_shape = tree.get_root_shape()
        obj2_shape = tree.get_or_create_child(obj2_shape, "x", attrs)
        obj2_shape = tree.get_or_create_child(obj2_shape, "y", attrs)

        # Should share shapes
        assert obj1_shape is obj2_shape

    def test_different_property_order_different_shapes(self):
        """Test different property order creates different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Object 1: {x, y}
        obj1 = tree.get_root_shape()
        obj1 = tree.get_or_create_child(obj1, "x", attrs)
        obj1 = tree.get_or_create_child(obj1, "y", attrs)

        # Object 2: {y, x}
        obj2 = tree.get_root_shape()
        obj2 = tree.get_or_create_child(obj2, "y", attrs)
        obj2 = tree.get_or_create_child(obj2, "x", attrs)

        # Different shapes
        assert obj1 is not obj2

        # Different offsets
        assert obj1.get_property_offset("x") == 0
        assert obj1.get_property_offset("y") == 1

        assert obj2.get_property_offset("y") == 0
        assert obj2.get_property_offset("x") == 1


class TestPropertyAttributes:
    """Test property attributes in shape system"""

    def test_readonly_property(self):
        """Test read-only property attributes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        readonly_attrs = PropertyAttributes(writable=False, enumerable=True, configurable=True)

        shape = tree.get_root_shape()
        shape = tree.get_or_create_child(shape, "PI", readonly_attrs)

        attrs = shape.get_property_attributes("PI")
        assert attrs.writable is False
        assert attrs.enumerable is True
        assert attrs.configurable is True

    def test_different_attributes_different_shapes(self):
        """Test properties with different attributes create different shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        root = tree.get_root_shape()

        writable = PropertyAttributes(writable=True)
        readonly = PropertyAttributes(writable=False)

        shape1 = tree.get_or_create_child(root, "x", writable)
        shape2 = tree.get_or_create_child(root, "x", readonly)

        # Different shapes
        assert shape1 is not shape2

        # Different attributes
        assert shape1.get_property_attributes("x").writable is True
        assert shape2.get_property_attributes("x").writable is False


class TestArrayShapeIntegration:
    """Test array shapes in the shape system"""

    def test_array_element_kind_evolution(self):
        """Test array transitioning through element kinds"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3] - SMI array
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.SMI_ELEMENTS

        # Add 3.14 -> DOUBLE array
        shape = shape.transition_element_kind(ElementKind.DOUBLE_ELEMENTS)
        assert shape.element_kind == ElementKind.DOUBLE_ELEMENTS

        # Add "hello" -> OBJECT array
        shape = shape.transition_element_kind(ElementKind.OBJECT_ELEMENTS)
        assert shape.element_kind == ElementKind.OBJECT_ELEMENTS

    def test_array_with_holes(self):
        """Test array with holes transitions to holey variant"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3] - packed SMI
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)

        # arr[10] = 11 (creates holes) -> holey SMI
        shape = shape.transition_element_kind(ElementKind.HOLEY_SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.HOLEY_SMI_ELEMENTS

    def test_array_can_have_properties(self):
        """Test arrays can have properties like normal objects"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        array_shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        attrs = PropertyAttributes()

        # arr.customProperty = "value"
        new_shape = array_shape.add_property("customProperty", attrs)

        assert new_shape.get_property_offset("customProperty") is not None


class TestShapeDeprecationIntegration:
    """Test shape deprecation and migration"""

    def test_deprecate_and_migrate(self):
        """Test deprecating a shape guides objects to new shape"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Old pattern: {x, y}
        old_shape = tree.get_root_shape()
        old_shape = tree.get_or_create_child(old_shape, "x", attrs)
        old_shape = tree.get_or_create_child(old_shape, "y", attrs)

        # New pattern: {a, b} (after refactoring)
        new_shape = tree.get_root_shape()
        new_shape = tree.get_or_create_child(new_shape, "a", attrs)
        new_shape = tree.get_or_create_child(new_shape, "b", attrs)

        # Deprecate old in favor of new
        tree.deprecate_shape(old_shape, new_shape)

        assert old_shape.is_deprecated() is True
        assert old_shape.get_migration_target() is new_shape


class TestPerformanceCharacteristics:
    """Test performance characteristics of shape system"""

    def test_property_access_is_constant_time(self):
        """Test property offset lookup is O(1)"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Create object with many properties
        shape = tree.get_root_shape()
        for i in range(100):
            shape = tree.get_or_create_child(shape, f"prop{i}", attrs)

        # Access should be fast (O(1)) regardless of number of properties
        # The offset map is built once and cached
        assert shape.get_property_offset("prop0") == 0
        assert shape.get_property_offset("prop50") == 50
        assert shape.get_property_offset("prop99") == 99

    def test_shape_reuse_saves_memory(self):
        """Test that shape reuse reduces memory usage"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Create 1000 objects with same shape
        shapes = []
        for _ in range(1000):
            shape = tree.get_root_shape()
            shape = tree.get_or_create_child(shape, "x", attrs)
            shape = tree.get_or_create_child(shape, "y", attrs)
            shapes.append(shape)

        # All should reference the same shape instances
        first_shape = shapes[0]
        assert all(shape is first_shape for shape in shapes)


class TestComplexScenarios:
    """Test complex real-world scenarios"""

    def test_constructor_pattern(self):
        """Test constructor pattern creates consistent shapes"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        def Point(x, y):
            """Constructor function for Point objects"""
            shape = tree.get_root_shape()
            shape = tree.get_or_create_child(shape, "x", attrs)
            shape = tree.get_or_create_child(shape, "y", attrs)
            return shape

        # Create multiple Point objects
        p1 = Point(1, 2)
        p2 = Point(3, 4)
        p3 = Point(5, 6)

        # All should have the same shape
        assert p1 is p2 is p3

    def test_class_hierarchy(self):
        """Test class hierarchy with shape transitions"""
        from components.hidden_classes.src.shape_tree import ShapeTree
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        tree = ShapeTree()
        attrs = PropertyAttributes()

        # Base class: Animal
        def Animal():
            shape = tree.get_root_shape()
            shape = tree.get_or_create_child(shape, "name", attrs)
            return shape

        # Derived class: Dog
        def Dog():
            shape = Animal()  # Inherit shape
            shape = tree.get_or_create_child(shape, "breed", attrs)
            return shape

        dog1 = Dog()
        dog2 = Dog()

        # Both dogs should have same shape
        assert dog1 is dog2
        assert dog1.property_count == 2
        assert dog1.get_property_offset("name") == 0
        assert dog1.get_property_offset("breed") == 1
