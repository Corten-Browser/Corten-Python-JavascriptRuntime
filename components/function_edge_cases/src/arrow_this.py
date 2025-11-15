"""
Arrow function this binding implementation (FR-ES24-B-044)

Arrow functions have lexical this binding:
- This is captured from enclosing scope at creation time
- call/apply/bind cannot change this
- No own this binding
- No arguments object
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field


@dataclass
class ArrowThisContext:
    """Context for resolving arrow function this"""
    enclosing_this: Any
    enclosing_arguments: Optional[List[Any]] = None


def resolve_arrow_this(
    arrow_function: Dict[str, Any],
    context: Optional[ArrowThisContext]
) -> Dict[str, Any]:
    """
    Resolve the this value for an arrow function.

    Arrow functions use lexical this, captured from enclosing scope.

    Args:
        arrow_function: Arrow function object
        context: Enclosing scope context

    Returns:
        Dictionary with this_value and source

    Raises:
        TypeError: If function is not an arrow function

    Examples:
        >>> arrow = {"type": "arrow", "lexical_this": {"value": 42}}
        >>> result = resolve_arrow_this(arrow, None)
        >>> result["this_value"]
        {'value': 42}
    """
    # Verify it's an arrow function
    if arrow_function.get("type") != "arrow":
        raise TypeError("Not an arrow function")

    # Arrow functions have lexical this captured at creation
    if "lexical_this" in arrow_function:
        return {
            "this_value": arrow_function["lexical_this"],
            "source": "lexical"
        }

    # If not already captured, use enclosing context
    if context:
        enclosing_this = context.enclosing_this

        # Determine source
        if enclosing_this and enclosing_this.get("__type__") == "global":
            source = "lexical"  # Still lexical, just happens to be global
        else:
            source = "lexical"

        return {
            "this_value": enclosing_this,
            "source": source
        }

    # No context - shouldn't normally happen, but return global
    return {
        "this_value": {"__type__": "global"},
        "source": "global"
    }


def capture_lexical_this(
    arrow_function: Dict[str, Any],
    enclosing_this: Any
) -> None:
    """
    Capture lexical this value at arrow function creation time.

    This mutates the arrow function object to store the lexical this.

    Args:
        arrow_function: Arrow function object to modify
        enclosing_this: This value from enclosing scope
    """
    arrow_function["lexical_this"] = enclosing_this


def arrow_has_own_this() -> bool:
    """
    Check if arrow functions have their own this binding.

    Returns:
        Always False - arrow functions never have own this
    """
    return False


def arrow_has_arguments_object() -> bool:
    """
    Check if arrow functions have arguments object.

    Returns:
        Always False - arrow functions don't have arguments object
    """
    return False
