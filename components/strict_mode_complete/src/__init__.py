"""
Strict Mode Complete - ES2024 Strict Mode Implementation

This module provides comprehensive strict mode support including:
- "use strict" directive detection
- Strict mode validation and enforcement
- Scope propagation
- Arguments object behavior
- This binding handling
"""

from .strict_mode_detector import StrictModeDetector, DirectivePrologueInfo
from .strict_mode_validator import StrictModeValidator, StrictModeContext
from .strict_mode_propagator import StrictModePropagator, ScopeType
from .arguments_validator import ArgumentsObjectValidator
from .this_binding import ThisBindingHandler, CallType
from .errors import (
    StrictModeReferenceError,
    StrictModeSyntaxError,
    StrictModeTypeError,
    StrictModeErrorType,
)

__all__ = [
    # Detector
    "StrictModeDetector",
    "DirectivePrologueInfo",
    # Validator
    "StrictModeValidator",
    "StrictModeContext",
    # Propagator
    "StrictModePropagator",
    "ScopeType",
    # Arguments
    "ArgumentsObjectValidator",
    # This binding
    "ThisBindingHandler",
    "CallType",
    # Errors
    "StrictModeReferenceError",
    "StrictModeSyntaxError",
    "StrictModeTypeError",
    "StrictModeErrorType",
]
