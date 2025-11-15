"""
Unit tests for PropertyAttributes class

RED phase: Tests written before implementation
"""
import pytest


class TestPropertyAttributes:
    """Test property descriptor attributes"""

    def test_default_attributes(self):
        """Test default property attributes (all true)"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes()
        assert attrs.writable is True
        assert attrs.enumerable is True
        assert attrs.configurable is True

    def test_custom_attributes(self):
        """Test custom property attributes"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(writable=False, enumerable=False, configurable=True)
        assert attrs.writable is False
        assert attrs.enumerable is False
        assert attrs.configurable is True

    def test_readonly_property(self):
        """Test read-only property (writable=False)"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(writable=False)
        assert attrs.writable is False
        assert attrs.enumerable is True
        assert attrs.configurable is True

    def test_non_enumerable_property(self):
        """Test non-enumerable property"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(enumerable=False)
        assert attrs.writable is True
        assert attrs.enumerable is False
        assert attrs.configurable is True

    def test_non_configurable_property(self):
        """Test non-configurable property"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(configurable=False)
        assert attrs.writable is True
        assert attrs.enumerable is True
        assert attrs.configurable is False

    def test_frozen_property(self):
        """Test frozen property (writable=False, configurable=False)"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(writable=False, configurable=False)
        assert attrs.writable is False
        assert attrs.configurable is False

    def test_equality(self):
        """Test PropertyAttributes equality"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs1 = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        attrs2 = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        attrs3 = PropertyAttributes(writable=False, enumerable=True, configurable=True)

        assert attrs1 == attrs2
        assert attrs1 != attrs3

    def test_hash(self):
        """Test PropertyAttributes can be hashed (for use in dicts)"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs1 = PropertyAttributes(writable=True, enumerable=True, configurable=True)
        attrs2 = PropertyAttributes(writable=True, enumerable=True, configurable=True)

        # Should be hashable
        attrs_dict = {attrs1: "value"}
        assert attrs_dict[attrs2] == "value"

    def test_repr(self):
        """Test PropertyAttributes string representation"""
        from components.hidden_classes.src.property_descriptor import PropertyAttributes

        attrs = PropertyAttributes(writable=True, enumerable=False, configurable=True)
        repr_str = repr(attrs)

        assert "PropertyAttributes" in repr_str
        assert "writable=True" in repr_str
        assert "enumerable=False" in repr_str
        assert "configurable=True" in repr_str
