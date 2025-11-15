"""
Shape (Hidden Class) implementation

Represents the structure of an object for optimization.
Shapes form a transition tree where adding a property creates a new child shape.
"""

from typing import Optional, Dict
from enum import Enum
from .property_descriptor import PropertyAttributes


class Shape:
    """
    Shape (Hidden Class) representing object structure

    Shapes form a transition tree:
    - Root shape: Empty object {}
    - Child shapes: Add one property at a time

    Example:
        {} -> {x} -> {x, y} -> {x, y, z}

    Each shape caches:
    - Property offsets (for O(1) array-based property access)
    - Property attributes (writable, enumerable, configurable)

    This enables fast property access without hash lookups.
    """

    def __init__(
        self,
        parent: Optional["Shape"],
        property_name: Optional[str],
        property_attributes: Optional[PropertyAttributes],
    ):
        """
        Create a new shape

        Args:
            parent: Parent shape in transition tree (None for root)
            property_name: Property added in this transition (None for root)
            property_attributes: Attributes of the property (None for root)
        """
        self.parent = parent
        self.property_name = property_name
        self.property_attributes = property_attributes

        # Deprecation support (for shape migration)
        self._deprecated = False
        self._migration_target: Optional[Shape] = None

        # Cache property information
        self._property_map: Optional[Dict[str, int]] = None  # name -> offset
        self._attribute_map: Optional[Dict[str, PropertyAttributes]] = None

    @property
    def property_count(self) -> int:
        """Get the number of properties in this shape"""
        if self.parent is None:
            return 0
        return self.parent.property_count + 1

    def _build_property_maps(self):
        """Build property offset and attribute maps by walking up the tree"""
        if self._property_map is not None:
            return  # Already built

        self._property_map = {}
        self._attribute_map = {}

        # Walk up the transition tree, collecting properties
        properties = []
        current = self
        while current is not None and current.property_name is not None:
            properties.append(
                (current.property_name, current.property_attributes)
            )
            current = current.parent

        # Reverse to get root-to-leaf order (property addition order)
        properties.reverse()

        # Assign offsets in order
        for offset, (name, attrs) in enumerate(properties):
            self._property_map[name] = offset
            self._attribute_map[name] = attrs

    def get_property_offset(self, name: str) -> Optional[int]:
        """
        Get property offset for O(1) access

        Args:
            name: Property name

        Returns:
            Property offset (0-based index) or None if not found
        """
        self._build_property_maps()
        return self._property_map.get(name)

    def get_property_attributes(self, name: str) -> Optional[PropertyAttributes]:
        """
        Get cached property descriptor

        Args:
            name: Property name

        Returns:
            Property attributes or None if not found
        """
        self._build_property_maps()
        return self._attribute_map.get(name)

    def add_property(
        self, name: str, attributes: PropertyAttributes
    ) -> "Shape":
        """
        Add property and return new shape (creates transition)

        This creates a new child shape in the transition tree.
        The original shape is not modified.

        Args:
            name: Property name
            attributes: Property attributes

        Returns:
            New shape with property added
        """
        return Shape(parent=self, property_name=name, property_attributes=attributes)

    def is_deprecated(self) -> bool:
        """
        Check if shape has been deprecated

        Returns:
            True if shape deprecated
        """
        return self._deprecated

    def get_migration_target(self) -> Optional["Shape"]:
        """
        Get target shape for migration if deprecated

        Returns:
            New shape to migrate to, or None
        """
        return self._migration_target

    def deprecate(self, target: "Shape"):
        """
        Mark shape as deprecated

        Args:
            target: Target shape for migration
        """
        self._deprecated = True
        self._migration_target = target

    def __repr__(self) -> str:
        """String representation of shape"""
        if self.parent is None:
            return f"Shape(properties=0, root=True)"

        # Build property list
        self._build_property_maps()
        props = list(self._property_map.keys())

        return f"Shape(properties={self.property_count}, props={props})"


class ElementKind(Enum):
    """
    Array element representations

    Arrays are specialized based on their element types:
    - SMI: Small integers (31-bit signed integers)
    - DOUBLE: Floating-point numbers
    - OBJECT: Generic objects (strings, objects, etc.)

    Each type has a "holey" variant for arrays with gaps:
    - HOLEY_SMI: SMI array with holes
    - HOLEY_DOUBLE: DOUBLE array with holes
    - HOLEY_OBJECT: OBJECT array with holes

    Element kind transitions are one-way:
    SMI -> DOUBLE -> OBJECT (more general)
    PACKED -> HOLEY (once holey, always holey)
    """

    SMI_ELEMENTS = "SMI_ELEMENTS"
    DOUBLE_ELEMENTS = "DOUBLE_ELEMENTS"
    OBJECT_ELEMENTS = "OBJECT_ELEMENTS"
    HOLEY_SMI_ELEMENTS = "HOLEY_SMI_ELEMENTS"
    HOLEY_DOUBLE_ELEMENTS = "HOLEY_DOUBLE_ELEMENTS"
    HOLEY_OBJECT_ELEMENTS = "HOLEY_OBJECT_ELEMENTS"


class ArrayShape(Shape):
    """
    Specialized shape for arrays

    Arrays have element kind specialization for optimization:
    - [1, 2, 3] uses SMI_ELEMENTS (fast integer array)
    - [1.1, 2.2, 3.3] uses DOUBLE_ELEMENTS (fast float array)
    - ["a", "b", "c"] uses OBJECT_ELEMENTS (generic array)

    Element kind transitions are one-way and permanent:
    - Adding a float to SMI array -> DOUBLE array
    - Adding a string to DOUBLE array -> OBJECT array
    - Creating a hole -> HOLEY variant

    This allows the JIT to generate specialized code for each element kind.
    """

    def __init__(self, element_kind: ElementKind):
        """
        Create array shape

        Args:
            element_kind: Type of elements (SMI, DOUBLE, OBJECT, or holey variants)
        """
        # Initialize base Shape (arrays start with no properties, but have 'length' etc.)
        super().__init__(parent=None, property_name=None, property_attributes=None)

        self.element_kind = element_kind

    def transition_element_kind(self, new_kind: ElementKind) -> "ArrayShape":
        """
        Transition to different element representation

        Element kind transitions are one-way:
        - SMI -> DOUBLE -> OBJECT (more general)
        - PACKED -> HOLEY (once holey, always holey)

        Args:
            new_kind: New element kind

        Returns:
            New array shape with different element kind
        """
        return ArrayShape(element_kind=new_kind)

    def __repr__(self) -> str:
        """String representation of array shape"""
        return f"ArrayShape(element_kind={self.element_kind.value})"
