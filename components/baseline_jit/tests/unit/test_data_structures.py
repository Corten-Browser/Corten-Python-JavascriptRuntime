"""
Unit tests for baseline JIT data structures.

Tests CompiledCode, RegisterAllocation, OSREntry structures.
Following TDD RED phase - these tests will fail initially.
"""

import pytest
from components.baseline_jit.src import CompiledCode, RegisterAllocation, OSREntry, Register


class TestRegisterEnum:
    """Test Register enumeration."""

    def test_register_enum_has_rax(self):
        """
        Given the Register enum
        When accessing RAX register
        Then it should be defined
        """
        # When/Then
        assert hasattr(Register, 'RAX')

    def test_register_enum_has_all_gp_registers(self):
        """
        Given the Register enum
        When checking for all general-purpose registers
        Then all x64 GP registers should be defined
        """
        # When/Then
        gp_registers = ['RAX', 'RBX', 'RCX', 'RDX', 'RSI', 'RDI',
                        'R8', 'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15']

        for reg in gp_registers:
            assert hasattr(Register, reg), f"Register.{reg} not defined"

    def test_register_enum_values_are_unique(self):
        """
        Given all defined registers
        When checking their values
        Then each should have a unique value
        """
        # Given
        registers = [Register.RAX, Register.RBX, Register.RCX, Register.RDX,
                     Register.RSI, Register.RDI, Register.R8, Register.R9,
                     Register.R10, Register.R11, Register.R12, Register.R13,
                     Register.R14, Register.R15]

        # When
        values = [reg.value for reg in registers]

        # Then
        assert len(values) == len(set(values)), "Register values not unique"


class TestCompiledCode:
    """Test CompiledCode data structure."""

    def test_compiled_code_creation(self):
        """
        Given machine code bytes and metadata
        When creating CompiledCode instance
        Then all fields should be set correctly
        """
        # Given
        code_bytes = b'\x48\x89\xc3'  # mov rbx, rax
        entry_point = 0x1000
        size = len(code_bytes)

        # When
        compiled = CompiledCode(
            code=code_bytes,
            entry_point=entry_point,
            size=size,
            deopt_info=None,
            ic_sites=[]
        )

        # Then
        assert compiled.code == code_bytes
        assert compiled.entry_point == entry_point
        assert compiled.size == size
        assert compiled.deopt_info is None
        assert compiled.ic_sites == []

    def test_compiled_code_with_ic_sites(self):
        """
        Given machine code with IC sites
        When creating CompiledCode
        Then IC sites should be stored
        """
        # Given
        code_bytes = b'\x90' * 10
        ic_sites = [{'offset': 5, 'type': 'property_load'}]

        # When
        compiled = CompiledCode(
            code=code_bytes,
            entry_point=0,
            size=10,
            deopt_info=None,
            ic_sites=ic_sites
        )

        # Then
        assert len(compiled.ic_sites) == 1
        assert compiled.ic_sites[0]['offset'] == 5


class TestRegisterAllocation:
    """Test RegisterAllocation data structure."""

    def test_register_allocation_creation(self):
        """
        Given register assignments and spills
        When creating RegisterAllocation
        Then all fields should be set correctly
        """
        # Given
        assignments = {0: Register.RAX, 1: Register.RBX}
        spills = [2, 3]

        # When
        allocation = RegisterAllocation(
            assignments=assignments,
            spills=spills
        )

        # Then
        assert allocation.assignments == assignments
        assert allocation.spills == spills

    def test_register_allocation_empty(self):
        """
        Given no assignments or spills
        When creating RegisterAllocation
        Then fields should be empty
        """
        # When
        allocation = RegisterAllocation(
            assignments={},
            spills=[]
        )

        # Then
        assert len(allocation.assignments) == 0
        assert len(allocation.spills) == 0

    def test_register_allocation_lookup_assigned_register(self):
        """
        Given a bytecode value assigned to register
        When looking up the assignment
        Then correct register should be returned
        """
        # Given
        assignments = {0: Register.RAX, 1: Register.RBX, 2: Register.RCX}
        allocation = RegisterAllocation(assignments=assignments, spills=[])

        # When
        reg = allocation.assignments.get(1)

        # Then
        assert reg == Register.RBX


class TestOSREntry:
    """Test OSREntry data structure."""

    def test_osr_entry_creation(self):
        """
        Given OSR metadata
        When creating OSREntry
        Then all fields should be set correctly
        """
        # Given
        bytecode_offset = 10
        compiled_offset = 128
        state_map = {'stack': [1, 2, 3], 'locals': {'x': 42}}

        # When
        entry = OSREntry(
            bytecode_offset=bytecode_offset,
            compiled_offset=compiled_offset,
            state_map=state_map
        )

        # Then
        assert entry.bytecode_offset == bytecode_offset
        assert entry.compiled_offset == compiled_offset
        assert entry.state_map == state_map

    def test_osr_entry_state_map_access(self):
        """
        Given OSREntry with state map
        When accessing state map
        Then state should be retrievable
        """
        # Given
        state_map = {'stack': [10, 20], 'pc': 5}
        entry = OSREntry(
            bytecode_offset=0,
            compiled_offset=0,
            state_map=state_map
        )

        # When
        stack = entry.state_map.get('stack')
        pc = entry.state_map.get('pc')

        # Then
        assert stack == [10, 20]
        assert pc == 5
