"""
Function Edge Cases Component

Implements ES2024 function API completeness and edge cases:
- Function.prototype.name inference (FR-ES24-B-039)
- Function.prototype.toString() (FR-ES24-B-040)
- Function.prototype.bind() edge cases (FR-ES24-B-041)
- Function.prototype.call/apply edge cases (FR-ES24-B-042)
- Function length property (FR-ES24-B-043)
- Arrow function this binding (FR-ES24-B-044)
- Function constructor edge cases (FR-ES24-B-045)
- Generator function edge cases (FR-ES24-B-046)
"""

from .name_inference import infer_function_name, NameInferenceContext
from .tostring import function_to_string, ToStringOptions
from .bind import bind_function, BindOptions
from .call_apply import call_function, apply_function, CallApplyOptions
from .length import calculate_length, LengthCalculation
from .arrow_this import resolve_arrow_this, ArrowThisContext
from .function_constructor import create_dynamic_function, FunctionConstructorOptions
from .generator_metadata import get_generator_metadata, GeneratorFunctionMetadata

__all__ = [
    # Name inference
    "infer_function_name",
    "NameInferenceContext",
    # toString
    "function_to_string",
    "ToStringOptions",
    # bind
    "bind_function",
    "BindOptions",
    # call/apply
    "call_function",
    "apply_function",
    "CallApplyOptions",
    # length
    "calculate_length",
    "LengthCalculation",
    # Arrow this
    "resolve_arrow_this",
    "ArrowThisContext",
    # Function constructor
    "create_dynamic_function",
    "FunctionConstructorOptions",
    # Generator metadata
    "get_generator_metadata",
    "GeneratorFunctionMetadata",
]

__version__ = "0.1.0"
