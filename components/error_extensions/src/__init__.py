"""
Error Extensions Module

Implements ES2021 AggregateError and ES2024 stack trace enhancements.

Components:
- AggregateError: Error type for representing multiple failures
- StackTraceGenerator: Generates and formats stack traces
- ErrorStackInitializer: Installs stack property on all Error types

Requirements:
- FR-ES24-B-015: AggregateError - Error for multiple failures
- FR-ES24-B-016: AggregateError.errors property - Array of aggregated errors
- FR-ES24-B-017: Error.prototype.stack - Stack trace property
- FR-ES24-B-018: Stack trace formatting - Human-readable stack traces
- FR-ES24-B-019: Error subclass stack traces - For all Error types
"""

from components.error_extensions.src.aggregate_error import (
    AggregateError,
    create_aggregate_error
)
from components.error_extensions.src.stack_trace_generator import (
    StackTraceGenerator,
    StackFrame,
    format_error_stack
)
from components.error_extensions.src.error_stack_initializer import (
    ErrorStackInitializer,
    install_error_stack_support
)

__all__ = [
    "AggregateError",
    "create_aggregate_error",
    "StackTraceGenerator",
    "StackFrame",
    "format_error_stack",
    "ErrorStackInitializer",
    "install_error_stack_support"
]

__version__ = "0.1.0"
