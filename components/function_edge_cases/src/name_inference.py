"""
Function name inference implementation (FR-ES24-B-039)

Implements name inference for functions based on context:
- Assignment expressions
- Object literal keys
- Class method names
- Property assignments
- Default exports
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class NameInferenceContext:
    """Context for inferring function name"""
    assignment_target: Optional[str] = None
    object_literal_key: Optional[str] = None
    class_method_name: Optional[str] = None
    default_name: Optional[str] = ""


def infer_function_name(
    function: Optional[Dict[str, Any]],
    context: Optional[NameInferenceContext]
) -> str:
    """
    Infer function name from context.

    Args:
        function: Function object (may have explicit name)
        context: Inference context

    Returns:
        Inferred or explicit name

    Examples:
        >>> infer_function_name(None, NameInferenceContext(assignment_target="foo"))
        'foo'
        >>> infer_function_name({"name": "explicit"}, None)
        'explicit'
    """
    # Priority 1: Explicit name (named function expression)
    if function and function.get("name"):
        return function["name"]

    # Priority 2: Context-based inference
    if context:
        # Assignment: const foo = function() {}
        if context.assignment_target:
            return context.assignment_target

        # Object literal: {bar: function() {}}
        if context.object_literal_key:
            # Handle computed properties with symbols
            key = context.object_literal_key
            if key.startswith("[") and key.endswith("]"):
                # Computed property - check if it's a symbol
                if "Symbol" in key:
                    return ""  # Symbols result in empty name
                # Otherwise use the computed value
                return key[1:-1] if len(key) > 2 else ""
            return key

        # Class method: class C { baz() {} }
        if context.class_method_name:
            return context.class_method_name

        # Default name
        if context.default_name is not None:
            return context.default_name

    # No name could be inferred
    return ""
