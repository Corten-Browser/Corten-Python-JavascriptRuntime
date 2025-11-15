"""
Placeholder Shape class for inline caching development.

This will be replaced with the real Shape class from hidden_classes
component once it's implemented.
"""


class Shape:
    """
    Placeholder for hidden class Shape.

    Represents the structure/layout of an object (hidden class).
    Each unique property layout gets a unique shape ID.
    """

    _next_shape_id = 1

    def __init__(self, properties=None):
        """
        Initialize a Shape with given properties.

        Args:
            properties: Dict of property names to offsets, or None
        """
        self.shape_id = Shape._next_shape_id
        Shape._next_shape_id += 1
        self.properties = properties or {}

    def __eq__(self, other):
        """Check shape equality by ID."""
        if not isinstance(other, Shape):
            return False
        return self.shape_id == other.shape_id

    def __hash__(self):
        """Hash by shape ID."""
        return hash(self.shape_id)

    def __repr__(self):
        """String representation."""
        return f"Shape(id={self.shape_id}, properties={self.properties})"

    def get_property_offset(self, prop_name):
        """
        Get property offset in the object's property array.

        Args:
            prop_name: Property name

        Returns:
            Offset (int) or None if property doesn't exist
        """
        return self.properties.get(prop_name)
