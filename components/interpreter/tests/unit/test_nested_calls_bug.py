"""
Test suite for nested function call bug.

This test suite reproduces and verifies the fix for a critical bug where
multiple function calls from the same parent function cause the interpreter
to hang.
"""

import pytest
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from components.bytecode.src import BytecodeArray, Opcode, Instruction
from components.interpreter.src.interpreter import Interpreter


class TestNestedFunctionCalls:
    """Test cases for nested function call scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.gc = GarbageCollector()
        self.interpreter = Interpreter(self.gc)

    def test_single_function_call_works(self):
        """
        Given a function that calls another function once
        When the parent function is executed
        Then it should complete successfully
        """
        # Create bytecode for function a() that returns 1
        a_bytecode = BytecodeArray(local_count=0)
        a_bytecode.add_constant(1)
        a_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 1
        a_bytecode.add_instruction(Instruction(Opcode.RETURN))             # Return

        # Create bytecode for outer() that calls a() once
        outer_bytecode = BytecodeArray(local_count=1)
        outer_bytecode.add_constant('a')
        outer_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, a_bytecode))  # Create closure for a()
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 0))    # Store as 'a'
        outer_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'a'
        outer_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call with 0 args
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))     # Store in local 0 (x)
        outer_bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))      # Return x
        outer_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Execute
        result = self.interpreter.execute(outer_bytecode)

        # Verify
        assert result.is_success()
        assert result.value.to_smi() == 1

    def test_two_function_calls_from_same_parent(self):
        """
        Given a function that calls two different functions
        When the parent function is executed
        Then both calls should complete successfully (CURRENTLY HANGS)
        """
        # Create bytecode for function a() that returns 1
        a_bytecode = BytecodeArray(local_count=0)
        a_bytecode.add_constant(1)
        a_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 1
        a_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Create bytecode for function b() that returns 2
        b_bytecode = BytecodeArray(local_count=0)
        b_bytecode.add_constant(2)
        b_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 2
        b_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Create bytecode for outer() that calls both a() and b()
        outer_bytecode = BytecodeArray(local_count=2)
        outer_bytecode.add_constant('a')
        outer_bytecode.add_constant('b')
        outer_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, a_bytecode))   # Create closure for a()
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 0))    # Store as 'a'
        outer_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, b_bytecode))   # Create closure for b()
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 1))    # Store as 'b'
        outer_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'a'
        outer_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call with 0 args
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 0))     # Store in local 0 (x)
        outer_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 1))     # Load 'b'
        outer_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call with 0 args - HANGS HERE
        outer_bytecode.add_instruction(Instruction(Opcode.STORE_LOCAL, 1))     # Store in local 1 (y)
        outer_bytecode.add_instruction(Instruction(Opcode.LOAD_LOCAL, 0))      # Return x
        outer_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Execute (this should complete but currently hangs)
        result = self.interpreter.execute(outer_bytecode)

        # Verify
        assert result.is_success()
        assert result.value.to_smi() == 1

    def test_function_call_chain(self):
        """
        Given functions that call each other in a chain (a→b→c)
        When the chain is executed
        Then all calls should complete successfully
        """
        # Create bytecode for function c() that returns 3
        c_bytecode = BytecodeArray(local_count=0)
        c_bytecode.add_constant(3)
        c_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 3
        c_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Create bytecode for function b() that calls c() and returns result
        b_bytecode = BytecodeArray(local_count=0)
        b_bytecode.add_constant('c')
        b_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'c'
        b_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call c()
        b_bytecode.add_instruction(Instruction(Opcode.RETURN))             # Return result

        # Create bytecode for function a() that calls b() and returns result
        a_bytecode = BytecodeArray(local_count=0)
        a_bytecode.add_constant('b')
        a_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'b'
        a_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call b()
        a_bytecode.add_instruction(Instruction(Opcode.RETURN))             # Return result

        # Create bytecode for main() that sets up and calls a()
        main_bytecode = BytecodeArray(local_count=0)
        main_bytecode.add_constant('c')
        main_bytecode.add_constant('b')
        main_bytecode.add_constant('a')
        main_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, c_bytecode))  # Create closure for c()
        main_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 0))    # Store as 'c'
        main_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, b_bytecode))  # Create closure for b()
        main_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 1))    # Store as 'b'
        main_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, a_bytecode))  # Create closure for a()
        main_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 2))    # Store as 'a'
        main_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 2))     # Load 'a'
        main_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call a()
        main_bytecode.add_instruction(Instruction(Opcode.RETURN))             # Return result

        # Execute
        result = self.interpreter.execute(main_bytecode)

        # Verify
        assert result.is_success()
        assert result.value.to_smi() == 3

    def test_multiple_calls_to_same_function(self):
        """
        Given a parent function that calls the same function multiple times
        When executed
        Then all calls should complete successfully
        """
        # Create bytecode for function f() that returns 42
        f_bytecode = BytecodeArray(local_count=0)
        f_bytecode.add_constant(42)
        f_bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load constant 42
        f_bytecode.add_instruction(Instruction(Opcode.RETURN))

        # Create bytecode for main() that calls f() three times
        main_bytecode = BytecodeArray(local_count=0)
        main_bytecode.add_constant('f')
        main_bytecode.add_instruction(Instruction(Opcode.CREATE_CLOSURE, 0, f_bytecode))  # Create closure for f()
        main_bytecode.add_instruction(Instruction(Opcode.STORE_GLOBAL, 0))    # Store as 'f'
        main_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'f'
        main_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call
        main_bytecode.add_instruction(Instruction(Opcode.POP))                # Discard result
        main_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'f'
        main_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call
        main_bytecode.add_instruction(Instruction(Opcode.POP))                # Discard result
        main_bytecode.add_instruction(Instruction(Opcode.LOAD_GLOBAL, 0))     # Load 'f'
        main_bytecode.add_instruction(Instruction(Opcode.CALL_FUNCTION, 0))   # Call
        main_bytecode.add_instruction(Instruction(Opcode.RETURN))             # Return result

        # Execute
        result = self.interpreter.execute(main_bytecode)

        # Verify
        assert result.is_success()
        assert result.value.to_smi() == 42
