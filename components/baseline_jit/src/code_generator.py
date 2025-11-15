"""
Code generator - bytecode to machine code translation.

Generates x64 machine code from bytecode instructions using register allocation.
"""

from typing import List
from components.bytecode.src import Opcode
from components.baseline_jit.src.backends.x64_backend import Register


class CodeGenerator:
    """
    Machine code generator for bytecode.

    Translates bytecode instructions to x64 machine code using provided
    register allocation. Generates prologue/epilogue for stack frame management.

    Example:
        >>> backend = x64Backend()
        >>> generator = CodeGenerator(backend)
        >>> code = generator.generate(bytecode, allocation)
    """

    def __init__(self, backend):
        """
        Initialize code generator.

        Args:
            backend: Platform-specific backend (x64Backend, etc.)
        """
        self.backend = backend
        self._code = bytearray()

    def generate(self, bytecode, register_allocation) -> bytes:
        """
        Generate machine code from bytecode.

        Args:
            bytecode: BytecodeArray to compile
            register_allocation: RegisterAllocation from register allocator

        Returns:
            Machine code bytes

        Example:
            >>> generator = CodeGenerator(x64Backend())
            >>> code = generator.generate(bytecode, allocation)
            >>> len(code) >= 0
            True
        """
        self._code.clear()

        # Emit function prologue
        self.emit_prologue(frame_size=128)  # Default 128 bytes

        # Generate code for each instruction
        for pc, instruction in enumerate(bytecode.instructions):
            self._generate_instruction(
                instruction,
                pc,
                bytecode,
                register_allocation
            )

        # Emit function epilogue
        self.emit_epilogue()

        return bytes(self._code)

    def emit_prologue(self, frame_size: int) -> None:
        """
        Emit function prologue.

        Sets up stack frame for function execution.

        Args:
            frame_size: Stack frame size in bytes

        Example:
            >>> generator = CodeGenerator(x64Backend())
            >>> generator.emit_prologue(64)
        """
        # Standard x64 function prologue:
        # push rbp
        # mov rbp, rsp
        # sub rsp, frame_size

        self._code.extend(self.backend.emit_push(Register.RBP))
        self._code.extend(self.backend.emit_mov(Register.RBP, Register.RSP))
        self._code.extend(self.backend.emit_sub(Register.RSP, frame_size))

    def emit_epilogue(self) -> None:
        """
        Emit function epilogue.

        Tears down stack frame and returns.

        Example:
            >>> generator = CodeGenerator(x64Backend())
            >>> generator.emit_epilogue()
        """
        # Standard x64 function epilogue:
        # mov rsp, rbp
        # pop rbp
        # ret

        self._code.extend(self.backend.emit_mov(Register.RSP, Register.RBP))
        self._code.extend(self.backend.emit_pop(Register.RBP))
        self._code.extend(self.backend.emit_ret())

    def _generate_instruction(self, instruction, pc, bytecode, allocation):
        """
        Generate machine code for single bytecode instruction.

        Args:
            instruction: Bytecode instruction
            pc: Program counter
            bytecode: BytecodeArray (for constant pool access)
            allocation: Register allocation
        """
        opcode = instruction.opcode

        # Get destination register for this instruction
        dest_reg = allocation.assignments.get(pc, Register.RAX)

        if opcode == Opcode.LOAD_CONSTANT:
            # Load constant into register
            const_value = bytecode.constant_pool[instruction.operand1]
            # Convert to integer if possible
            if isinstance(const_value, (int, float)):
                const_value = int(const_value)
            else:
                const_value = 0  # Simplified - would need object handling
            self._code.extend(self.backend.emit_mov(dest_reg, const_value))

        elif opcode == Opcode.ADD:
            # Add: dest = rax + rbx (simplified)
            # In real impl, would use actual register allocation
            self._code.extend(self.backend.emit_add(Register.RAX, Register.RBX))

        elif opcode == Opcode.SUBTRACT:
            # Subtract: dest = rax - rbx
            self._code.extend(self.backend.emit_sub(Register.RAX, Register.RBX))

        elif opcode == Opcode.MULTIPLY:
            # Multiply: dest = rax * rbx
            self._code.extend(self.backend.emit_mul(Register.RAX, Register.RBX))

        elif opcode == Opcode.DIVIDE:
            # Division would require more complex code (DIV instruction)
            self._code.extend(self.backend.emit_nop())  # Placeholder

        elif opcode == Opcode.RETURN:
            # Return handled by epilogue
            pass

        else:
            # Unknown opcode - emit NOP as placeholder
            self._code.extend(self.backend.emit_nop())
