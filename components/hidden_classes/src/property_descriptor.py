"""
Property descriptor attributes for hidden classes

Represents the attributes (writable, enumerable, configurable) of a property.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PropertyAttributes:
    """
    Property descriptor attributes

    Represents the three fundamental property attributes from ECMAScript:
    - writable: Can the property value be changed?
    - enumerable: Does the property show up in for...in loops?
    - configurable: Can the property be deleted or attributes changed?

    This is immutable (frozen) to allow use as dictionary keys.
    """

    writable: bool = True
    enumerable: bool = True
    configurable: bool = True

    def __repr__(self) -> str:
        """String representation of property attributes"""
        return (
            f"PropertyAttributes("
            f"writable={self.writable}, "
            f"enumerable={self.enumerable}, "
            f"configurable={self.configurable})"
        )
