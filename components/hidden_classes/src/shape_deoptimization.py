"""
Shape Deoptimization - Trigger deoptimization on shape changes

Invalidates JIT code when shape assumptions are violated.
Provides deoptimization triggers for shape transitions.

FR-P4-022: Shape deoptimization
"""

from typing import Callable, List, Dict, Any
from .shape import Shape
from .shape_tree import ShapeTree


class ShapeDeoptTrigger:
    """
    Deoptimization trigger reasons

    These constants identify why deoptimization was triggered:
    - SHAPE_CHANGED: Object's shape changed unexpectedly
    - SHAPE_DEPRECATED: Shape was marked as deprecated
    - SHAPE_MISMATCH: Shape doesn't match JIT's assumption
    - PROPERTY_ADDED: Property was added (shape transition)
    - PROPERTY_DELETED: Property was deleted
    """

    SHAPE_CHANGED = "shape_changed"
    SHAPE_DEPRECATED = "shape_deprecated"
    SHAPE_MISMATCH = "shape_mismatch"
    PROPERTY_ADDED = "property_added"
    PROPERTY_DELETED = "property_deleted"


class ShapeDeoptimization:
    """
    Shape-based deoptimization coordinator

    JIT-compiled code makes assumptions about object shapes:
    - "This object has shape X"
    - "Property 'x' is at offset 0"
    - "This shape won't change"

    When these assumptions are violated, we must deoptimize:
    1. Detect shape change
    2. Trigger deoptimization
    3. Invalidate JIT code
    4. Return to interpreter

    This class provides:
    - Deoptimization listener registration
    - Shape guard checking
    - Deoptimization triggers for various events

    Example:
        deopt = ShapeDeoptimization(shape_tree)

        # Register listener (e.g., JIT compiler)
        def on_deopt(shape, reason, details):
            invalidate_jit_code(shape)
            return_to_interpreter()

        deopt.register_deopt_listener(on_deopt)

        # In JIT code: Check shape guard
        if not deopt.check_shape_guard(expected_shape, obj.shape):
            # Deoptimization triggered automatically
            deoptimize()

        # When shape changes: Trigger deopt
        deopt.on_property_added(old_shape, "x", new_shape)
    """

    def __init__(self, shape_tree: ShapeTree):
        """
        Create shape deoptimization coordinator

        Args:
            shape_tree: Shape tree for shape management
        """
        self.shape_tree = shape_tree
        self.deopt_listeners: List[Callable] = []

    def register_deopt_listener(self, callback: Callable):
        """
        Register callback for shape deoptimization

        Callback signature: callback(shape, reason, details)

        Args:
            shape: Shape that triggered deoptimization
            reason: ShapeDeoptTrigger constant
            details: Dictionary with additional information

        Args:
            callback: Function to call on deoptimization
        """
        self.deopt_listeners.append(callback)

    def trigger_deopt(self, shape: Shape, reason: str, details: Dict[str, Any]):
        """
        Trigger deoptimization for shape change

        Calls all registered listeners with deoptimization information.

        Args:
            shape: Shape that triggered deoptimization
            reason: ShapeDeoptTrigger constant (why deopt happened)
            details: Additional information (e.g., old/new shape IDs)
        """
        for listener in self.deopt_listeners:
            listener(shape, reason, details)

    def check_shape_guard(self, expected_shape: Shape, actual_shape: Shape) -> bool:
        """
        Check if shape guard is satisfied

        Shape guards are used in JIT code to verify assumptions:
        - "This object has shape X"
        - If guard fails: Deoptimize

        Args:
            expected_shape: Shape JIT code expects
            actual_shape: Object's actual shape

        Returns:
            True if guard satisfied (shapes match)
            False if guard failed (triggers deoptimization)
        """
        if expected_shape is actual_shape:
            return True

        # Shape mismatch - trigger deoptimization
        self.trigger_deopt(
            actual_shape,
            ShapeDeoptTrigger.SHAPE_MISMATCH,
            {
                "expected": id(expected_shape),
                "actual": id(actual_shape),
            },
        )
        return False

    def on_shape_deprecation(self, old_shape: Shape, new_shape: Shape):
        """
        Called when shape is deprecated

        Shape deprecation means:
        - Old shape is no longer recommended
        - Objects should migrate to new shape
        - JIT code for old shape should be invalidated

        Args:
            old_shape: Shape being deprecated
            new_shape: Target shape for migration
        """
        self.trigger_deopt(
            old_shape,
            ShapeDeoptTrigger.SHAPE_DEPRECATED,
            {
                "old_shape": id(old_shape),
                "new_shape": id(new_shape),
            },
        )

    def on_property_added(
        self,
        shape: Shape,
        property_name: str,
        new_shape: Shape
    ):
        """
        Called when property is added (shape transition)

        Adding a property creates a new shape:
        - Old shape: {x}
        - New shape: {x, y}

        JIT code assuming old shape must deoptimize.

        Args:
            shape: Old shape (before property added)
            property_name: Property being added
            new_shape: New shape (after property added)
        """
        self.trigger_deopt(
            shape,
            ShapeDeoptTrigger.PROPERTY_ADDED,
            {
                "property": property_name,
                "new_shape": id(new_shape),
            },
        )

    def on_property_deleted(
        self,
        shape: Shape,
        property_name: str,
        new_shape: Shape
    ):
        """
        Called when property is deleted

        Property deletion is a shape change:
        - Old shape: {x, y}
        - New shape: {x}

        JIT code must deoptimize.

        Args:
            shape: Old shape (before property deleted)
            property_name: Property being deleted
            new_shape: New shape (after property deleted)
        """
        self.trigger_deopt(
            shape,
            ShapeDeoptTrigger.PROPERTY_DELETED,
            {
                "property": property_name,
                "new_shape": id(new_shape),
            },
        )
