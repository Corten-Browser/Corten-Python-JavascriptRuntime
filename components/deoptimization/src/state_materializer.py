"""
State materialization - recreate interpreter state from JIT state.
"""
from typing import Any, Dict, Optional
from dataclasses import dataclass

from components.deoptimization.src.deopt_types import (
    JITState,
    DeoptInfo,
    InterpreterFrame,
    ValueLocation,
)


# Placeholder JSValue types (simplified until full object_runtime integration)
@dataclass
class JSValue:
    """Simplified JSValue placeholder."""
    value: Any
    type_tag: str


@dataclass
class JSObject:
    """Simplified JSObject placeholder."""
    properties: Dict[str, Any]
    shape: Optional[Any] = None


@dataclass
class InterpreterState:
    """Complete interpreter execution state."""
    frame: InterpreterFrame
    context: Optional[Any] = None


class StateMaterializer:
    """Materialize interpreter state from JIT execution state."""

    def __init__(self):
        """Initialize state materializer."""
        pass

    def materialize(self, jit_state: JITState, deopt_info: DeoptInfo) -> InterpreterState:
        """
        Create complete interpreter state from JIT state.

        Args:
            jit_state: Current JIT execution state
            deopt_info: Deoptimization metadata

        Returns:
            InterpreterState ready for interpreter execution

        Raises:
            ValueError: If location type is unknown
        """
        # Materialize local variables
        locals_list = []
        stack_list = []

        # Ensure jit_state has stack attribute
        if not hasattr(jit_state, "stack"):
            jit_state.stack = []

        # Get constants if available
        constants = getattr(deopt_info, "constants", {})

        # Materialize each value in the value map
        for name, location in deopt_info.value_map.items():
            value = self._read_value_from_location(
                jit_state, location, constants
            )
            js_value = self._convert_value(value, location.value_type)

            # Check if this is a stack value or local
            if hasattr(deopt_info, "stack_map") and name in deopt_info.stack_map:
                stack_list.append(js_value)
            else:
                locals_list.append(js_value)

        # Create interpreter frame
        frame = InterpreterFrame(
            bytecode_offset=deopt_info.bytecode_offset,
            locals=locals_list,
            stack=stack_list
        )

        # Create interpreter state
        return InterpreterState(frame=frame)

    def _read_value_from_location(
        self,
        jit_state: JITState,
        location: ValueLocation,
        constants: Dict[int, Any]
    ) -> Any:
        """
        Read raw value from JIT state location.

        Args:
            jit_state: JIT state
            location: Value location descriptor
            constants: Constant values

        Returns:
            Raw value from JIT state

        Raises:
            ValueError: If location type is unknown
        """
        if location.location_type == "register":
            # Read from register
            reg_name = location.location_id
            return jit_state.registers.get(reg_name, 0)

        elif location.location_type == "stack":
            # Read from stack
            stack_offset = location.location_id
            if stack_offset < len(jit_state.stack):
                return jit_state.stack[stack_offset]
            return 0

        elif location.location_type == "constant":
            # Read constant value
            const_id = location.location_id
            return constants.get(const_id, 0)

        else:
            raise ValueError(f"Unknown location type: {location.location_type}")

    def _convert_value(self, raw_value: Any, value_type: str) -> JSValue:
        """
        Convert raw JIT value to JSValue.

        Args:
            raw_value: Raw value from JIT state
            value_type: Expected value type

        Returns:
            JSValue representation
        """
        if value_type == "int":
            # Smi - small integer
            return JSValue(value=raw_value, type_tag="number")

        elif value_type == "float":
            # Float64
            return JSValue(value=float(raw_value), type_tag="number")

        elif value_type == "object":
            # Object pointer - for now, just wrap the pointer
            # In real implementation, would dereference and materialize object
            return JSValue(value=raw_value, type_tag="object")

        else:
            # Default: treat as generic value
            return JSValue(value=raw_value, type_tag="unknown")

    def materialize_object(self, object_data: Dict[str, Any], shape: Any) -> JSObject:
        """
        Materialize JSObject from escaped allocation data.

        Args:
            object_data: Object field values
            shape: Object shape (hidden class)

        Returns:
            Materialized JSObject
        """
        # Create JSObject with properties from data
        obj = JSObject(
            properties=object_data.copy(),
            shape=shape
        )
        return obj
