"""
ShapeTree - Transition tree for shape evolution

Manages the global tree of shapes and ensures shape reuse for performance.
"""

from typing import Dict, Tuple
from .shape import Shape
from .property_descriptor import PropertyAttributes


class ShapeTree:
    """
    Transition tree for shape evolution

    Manages a global tree of shapes where:
    - Root shape represents empty object {}
    - Each transition (adding a property) creates or reuses a child shape
    - Shapes with the same property sequence share the same shape instance

    This enables:
    - Shape reuse (objects with same structure share shapes)
    - Efficient property access (O(1) via shape-based offsets)
    - Memory efficiency (many objects share few shapes)

    Example:
        tree = ShapeTree()
        root = tree.get_root_shape()

        # Two objects with same properties share shapes
        obj1_shape = tree.get_or_create_child(root, "x", attrs)
        obj2_shape = tree.get_or_create_child(root, "x", attrs)
        assert obj1_shape is obj2_shape  # Shared!
    """

    def __init__(self):
        """Create shape tree with root shape"""
        self._root_shape = Shape(
            parent=None, property_name=None, property_attributes=None
        )

        # Cache of child shapes: (parent_id, property_name, attributes) -> shape
        # This ensures shape reuse for same transitions
        self._shape_cache: Dict[Tuple[int, str, PropertyAttributes], Shape] = {}

    def get_root_shape(self) -> Shape:
        """
        Get root shape for empty objects

        Returns:
            Root shape (empty object)
        """
        return self._root_shape

    def get_or_create_child(
        self,
        parent: Shape,
        property_name: str,
        attributes: PropertyAttributes,
    ) -> Shape:
        """
        Get or create child shape in transition tree

        This is the key method for shape transitions. When adding a property:
        1. Check if this transition already exists (cache hit)
        2. If yes, return existing shape (reuse)
        3. If no, create new child shape and cache it

        Args:
            parent: Parent shape
            property_name: Property being added
            attributes: Property attributes

        Returns:
            Child shape (existing or newly created)
        """
        # Create cache key: (parent identity, property name, attributes)
        # Use id(parent) for parent identity (each shape has unique identity)
        cache_key = (id(parent), property_name, attributes)

        # Check cache first
        if cache_key in self._shape_cache:
            return self._shape_cache[cache_key]

        # Not in cache - create new child shape
        child_shape = Shape(
            parent=parent,
            property_name=property_name,
            property_attributes=attributes,
        )

        # Cache it for future reuse
        self._shape_cache[cache_key] = child_shape

        return child_shape

    def deprecate_shape(self, shape: Shape, target: Shape):
        """
        Mark shape as deprecated

        When a shape's structure changes significantly (e.g., property deleted),
        we deprecate the old shape and guide objects to migrate to a new shape.

        Args:
            shape: Shape to deprecate
            target: Target shape for migration
        """
        shape.deprecate(target)
