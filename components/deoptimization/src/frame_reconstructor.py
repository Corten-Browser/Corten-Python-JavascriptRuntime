"""
Frame reconstruction - convert JIT frames to interpreter frames.
"""
from typing import Dict, List, Any

from components.deoptimization.src.deopt_types import (
    JITFrame,
    InterpreterFrame,
    DeoptInfo,
    ValueLocation,
)
from components.deoptimization.src.state_materializer import (
    StateMaterializer,
    JSValue,
    JITState,
)


class FrameReconstructor:
    """Reconstruct interpreter stack frames from JIT state."""

    def __init__(self):
        """Initialize frame reconstructor."""
        self.materializer = StateMaterializer()

    def reconstruct_frame(
        self,
        jit_frame: JITFrame,
        deopt_info: DeoptInfo
    ) -> InterpreterFrame:
        """
        Reconstruct interpreter frame from JIT frame.

        Args:
            jit_frame: JIT stack frame
            deopt_info: Deoptimization metadata

        Returns:
            Reconstructed interpreter frame
        """
        # Convert JIT frame to JIT state for materialization
        jit_state = JITState(
            registers=jit_frame.registers,
            stack_pointer=0x7fff,  # Dummy stack pointer
            instruction_pointer=jit_frame.return_address
        )
        jit_state.stack = jit_frame.stack

        # Materialize values
        locals_list = []
        stack_list = []

        # Get stack map if available
        stack_map = getattr(deopt_info, "stack_map", [])
        constants = getattr(deopt_info, "constants", {})

        # Process each value in value map
        for name, location in deopt_info.value_map.items():
            # Read value from location
            raw_value = self._read_value(jit_state, location, constants)
            # Convert to JSValue
            js_value = self.materializer._convert_value(raw_value, location.value_type)

            # Check if this is a stack value or local
            if name in stack_map:
                stack_list.append(js_value)
            else:
                locals_list.append(js_value)

        # Create interpreter frame
        frame = InterpreterFrame(
            bytecode_offset=deopt_info.bytecode_offset,
            locals=locals_list,
            stack=stack_list
        )

        return frame

    def materialize_values(
        self,
        value_map: Dict[str, ValueLocation],
        deopt_info: DeoptInfo
    ) -> List[JSValue]:
        """
        Materialize values from JIT locations to interpreter values.

        Args:
            value_map: Map of value names to locations
            deopt_info: Deoptimization metadata

        Returns:
            List of materialized JSValues
        """
        # Get jit_frame if stored in deopt_info
        jit_frame = getattr(deopt_info, "jit_frame", None)
        if jit_frame is None:
            # Create dummy JIT state
            jit_state = JITState(
                registers={},
                stack_pointer=0x7fff,
                instruction_pointer=0x1000
            )
            jit_state.stack = []
        else:
            # Convert jit_frame to jit_state
            jit_state = JITState(
                registers=jit_frame.registers,
                stack_pointer=0x7fff,
                instruction_pointer=jit_frame.return_address
            )
            jit_state.stack = jit_frame.stack

        constants = getattr(deopt_info, "constants", {})

        # Materialize each value
        values = []
        for name, location in value_map.items():
            raw_value = self._read_value(jit_state, location, constants)
            js_value = self.materializer._convert_value(raw_value, location.value_type)
            values.append(js_value)

        return values

    def _read_value(
        self,
        jit_state: JITState,
        location: ValueLocation,
        constants: Dict[int, Any]
    ) -> Any:
        """
        Read raw value from JIT state location.

        Args:
            jit_state: JIT execution state
            location: Value location descriptor
            constants: Constant values

        Returns:
            Raw value from location
        """
        if location.location_type == "register":
            # Read from register
            reg_name = location.location_id
            return jit_state.registers.get(reg_name, 0)

        elif location.location_type == "stack":
            # Read from stack
            stack_offset = location.location_id
            if hasattr(jit_state, "stack") and stack_offset < len(jit_state.stack):
                return jit_state.stack[stack_offset]
            return 0

        elif location.location_type == "constant":
            # Read constant
            const_id = location.location_id
            return constants.get(const_id, 0)

        else:
            # Unknown location type - return default
            return 0
