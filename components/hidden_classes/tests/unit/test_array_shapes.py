"""
Unit tests for ArrayShape specialization

RED phase: Tests written before implementation
"""
import pytest


class TestArrayShapeCreation:
    """Test ArrayShape creation"""

    def test_create_array_shape_smi(self):
        """Test creating array shape with SMI elements"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.SMI_ELEMENTS

    def test_create_array_shape_double(self):
        """Test creating array shape with DOUBLE elements"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        shape = ArrayShape(element_kind=ElementKind.DOUBLE_ELEMENTS)
        assert shape.element_kind == ElementKind.DOUBLE_ELEMENTS

    def test_create_array_shape_object(self):
        """Test creating array shape with OBJECT elements"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        shape = ArrayShape(element_kind=ElementKind.OBJECT_ELEMENTS)
        assert shape.element_kind == ElementKind.OBJECT_ELEMENTS

    def test_create_holey_array_shape(self):
        """Test creating holey array shape"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        shape = ArrayShape(element_kind=ElementKind.HOLEY_SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.HOLEY_SMI_ELEMENTS


class TestElementKindTransitions:
    """Test element kind transitions (SMI -> DOUBLE -> OBJECT)"""

    def test_transition_smi_to_double(self):
        """Test transitioning from SMI to DOUBLE (adding float)"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        smi_shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        double_shape = smi_shape.transition_element_kind(ElementKind.DOUBLE_ELEMENTS)

        assert smi_shape.element_kind == ElementKind.SMI_ELEMENTS
        assert double_shape.element_kind == ElementKind.DOUBLE_ELEMENTS
        assert smi_shape is not double_shape  # Different shape

    def test_transition_smi_to_object(self):
        """Test transitioning from SMI to OBJECT (adding non-numeric)"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        smi_shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        object_shape = smi_shape.transition_element_kind(ElementKind.OBJECT_ELEMENTS)

        assert object_shape.element_kind == ElementKind.OBJECT_ELEMENTS

    def test_transition_double_to_object(self):
        """Test transitioning from DOUBLE to OBJECT"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        double_shape = ArrayShape(element_kind=ElementKind.DOUBLE_ELEMENTS)
        object_shape = double_shape.transition_element_kind(ElementKind.OBJECT_ELEMENTS)

        assert object_shape.element_kind == ElementKind.OBJECT_ELEMENTS

    def test_transition_packed_to_holey(self):
        """Test transitioning from packed to holey (creating holes)"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        packed_shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        holey_shape = packed_shape.transition_element_kind(ElementKind.HOLEY_SMI_ELEMENTS)

        assert packed_shape.element_kind == ElementKind.SMI_ELEMENTS
        assert holey_shape.element_kind == ElementKind.HOLEY_SMI_ELEMENTS

    def test_transition_holey_smi_to_holey_double(self):
        """Test transitioning holey SMI to holey DOUBLE"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        holey_smi = ArrayShape(element_kind=ElementKind.HOLEY_SMI_ELEMENTS)
        holey_double = holey_smi.transition_element_kind(ElementKind.HOLEY_DOUBLE_ELEMENTS)

        assert holey_double.element_kind == ElementKind.HOLEY_DOUBLE_ELEMENTS

    def test_transition_holey_double_to_holey_object(self):
        """Test transitioning holey DOUBLE to holey OBJECT"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        holey_double = ArrayShape(element_kind=ElementKind.HOLEY_DOUBLE_ELEMENTS)
        holey_object = holey_double.transition_element_kind(ElementKind.HOLEY_OBJECT_ELEMENTS)

        assert holey_object.element_kind == ElementKind.HOLEY_OBJECT_ELEMENTS


class TestArrayShapeInheritance:
    """Test that ArrayShape inherits from Shape"""

    def test_array_shape_is_shape(self):
        """Test ArrayShape is a subclass of Shape"""
        from components.hidden_classes.src.shape import ArrayShape, Shape, ElementKind

        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        assert isinstance(shape, Shape)

    def test_array_shape_has_property_methods(self):
        """Test ArrayShape has property methods from Shape"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        attrs = PropertyAttributes()

        # Should be able to add properties like regular Shape
        new_shape = shape.add_property("length", attrs)
        assert new_shape.get_property_offset("length") is not None


class TestElementKindEnum:
    """Test ElementKind enum"""

    def test_element_kind_values(self):
        """Test ElementKind enum has all required values"""
        from components.hidden_classes.src.shape import ElementKind

        # Packed variants
        assert hasattr(ElementKind, "SMI_ELEMENTS")
        assert hasattr(ElementKind, "DOUBLE_ELEMENTS")
        assert hasattr(ElementKind, "OBJECT_ELEMENTS")

        # Holey variants
        assert hasattr(ElementKind, "HOLEY_SMI_ELEMENTS")
        assert hasattr(ElementKind, "HOLEY_DOUBLE_ELEMENTS")
        assert hasattr(ElementKind, "HOLEY_OBJECT_ELEMENTS")

    def test_element_kind_distinct(self):
        """Test ElementKind values are distinct"""
        from components.hidden_classes.src.shape import ElementKind

        kinds = [
            ElementKind.SMI_ELEMENTS,
            ElementKind.DOUBLE_ELEMENTS,
            ElementKind.OBJECT_ELEMENTS,
            ElementKind.HOLEY_SMI_ELEMENTS,
            ElementKind.HOLEY_DOUBLE_ELEMENTS,
            ElementKind.HOLEY_OBJECT_ELEMENTS,
        ]

        # All should be unique
        assert len(kinds) == len(set(kinds))


class TestArrayShapeOptimization:
    """Test array shape optimization scenarios"""

    def test_homogeneous_integer_array(self):
        """Test array with only integers uses SMI_ELEMENTS"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3, 4, 5] - all SMIs
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.SMI_ELEMENTS

    def test_adding_float_transitions_to_double(self):
        """Test adding float to SMI array transitions to DOUBLE"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3] - SMI elements
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)

        # arr[3] = 3.14 - add float, transitions to DOUBLE
        shape = shape.transition_element_kind(ElementKind.DOUBLE_ELEMENTS)
        assert shape.element_kind == ElementKind.DOUBLE_ELEMENTS

    def test_adding_string_transitions_to_object(self):
        """Test adding non-numeric transitions to OBJECT"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3] - SMI elements
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)

        # arr[3] = "hello" - add string, transitions to OBJECT
        shape = shape.transition_element_kind(ElementKind.OBJECT_ELEMENTS)
        assert shape.element_kind == ElementKind.OBJECT_ELEMENTS

    def test_creating_hole_transitions_to_holey(self):
        """Test creating hole transitions to holey variant"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, 2, 3] - packed SMI
        shape = ArrayShape(element_kind=ElementKind.SMI_ELEMENTS)

        # arr[5] = 6 (skipping index 4) - creates hole
        shape = shape.transition_element_kind(ElementKind.HOLEY_SMI_ELEMENTS)
        assert shape.element_kind == ElementKind.HOLEY_SMI_ELEMENTS

    def test_mixed_types_use_object_elements(self):
        """Test array with mixed types uses OBJECT_ELEMENTS"""
        from components.hidden_classes.src.shape import ArrayShape, ElementKind

        # [1, "hello", 3.14, {}, null] - mixed types
        shape = ArrayShape(element_kind=ElementKind.OBJECT_ELEMENTS)
        assert shape.element_kind == ElementKind.OBJECT_ELEMENTS
