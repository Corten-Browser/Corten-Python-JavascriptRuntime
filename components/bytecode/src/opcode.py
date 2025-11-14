"""
Bytecode opcodes for JavaScript runtime engine.

This module defines all bytecode operation codes used by the virtual machine.
The opcodes represent register-based instructions for executing JavaScript code.

Public API:
    - Opcode: Enum containing all opcode definitions
"""

from enum import Enum, auto


class Opcode(Enum):
    """
    Bytecode instruction opcodes for JavaScript runtime.

    This enum defines all available opcodes for the register-based bytecode format.
    Each opcode represents a single VM instruction.

    Opcode Categories:
        - Literals: Load constant values
        - Variables: Access local and global variables
        - Arithmetic: Mathematical operations
        - Comparison: Relational operations
        - Logical: Boolean operations
        - Control Flow: Jumps and returns
        - Objects: Object property operations
        - Arrays: Array element operations
        - Functions: Function creation and calls
        - Stack: Stack manipulation
    """

    # Literals - Load constant values
    LOAD_CONSTANT = auto()  # Load constant from constant pool
    LOAD_UNDEFINED = auto()  # Load undefined value
    LOAD_NULL = auto()  # Load null value
    LOAD_TRUE = auto()  # Load true value
    LOAD_FALSE = auto()  # Load false value

    # Variables - Access local and global variables
    LOAD_GLOBAL = auto()  # Load global variable by name
    STORE_GLOBAL = auto()  # Store to global variable by name
    LOAD_LOCAL = auto()  # Load local variable by index
    STORE_LOCAL = auto()  # Store to local variable by index

    # Arithmetic operations
    ADD = auto()  # Addition
    SUBTRACT = auto()  # Subtraction
    MULTIPLY = auto()  # Multiplication
    DIVIDE = auto()  # Division
    MODULO = auto()  # Modulo
    NEGATE = auto()  # Unary negation

    # Comparison operations
    EQUAL = auto()  # Equality (==)
    NOT_EQUAL = auto()  # Inequality (!=)
    LESS_THAN = auto()  # Less than (<)
    LESS_EQUAL = auto()  # Less than or equal (<=)
    GREATER_THAN = auto()  # Greater than (>)
    GREATER_EQUAL = auto()  # Greater than or equal (>=)

    # Logical operations
    LOGICAL_AND = auto()  # Logical AND (&&)
    LOGICAL_OR = auto()  # Logical OR (||)
    LOGICAL_NOT = auto()  # Logical NOT (!)

    # Control flow
    JUMP = auto()  # Unconditional jump to target
    JUMP_IF_TRUE = auto()  # Jump if top of stack is true
    JUMP_IF_FALSE = auto()  # Jump if top of stack is false
    RETURN = auto()  # Return from function

    # Object operations
    CREATE_OBJECT = auto()  # Create empty object
    LOAD_PROPERTY = auto()  # Load object property
    STORE_PROPERTY = auto()  # Store object property
    DELETE_PROPERTY = auto()  # Delete object property

    # Array operations
    CREATE_ARRAY = auto()  # Create empty array
    LOAD_ELEMENT = auto()  # Load array element
    STORE_ELEMENT = auto()  # Store array element

    # Function operations
    CREATE_CLOSURE = auto()  # Create function closure
    CALL_FUNCTION = auto()  # Call function
    NEW = auto()  # Create instance: stack[constructor, ...args] -> instance

    # Async/Await operations
    CREATE_ASYNC_FUNCTION = auto()  # Create async function (returns Promise)
    AWAIT = auto()  # Suspend execution at await point

    # Stack manipulation
    POP = auto()  # Pop value from stack
    DUP = auto()  # Duplicate top of stack

    def __repr__(self) -> str:
        """Return string representation of opcode."""
        return f"Opcode.{self.name}"
