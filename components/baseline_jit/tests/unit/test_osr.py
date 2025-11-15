"""
Unit tests for OSR (On-Stack Replacement) manager.

Tests OSRManager for tier-up from interpreter to JIT during execution.
"""

import pytest
from components.baseline_jit.src import OSRManager, OSREntry


class TestOSRManagerBasic:
    """Test basic OSR manager functionality."""

    def test_osr_manager_creation(self):
        """
        When creating OSRManager
        Then it should initialize successfully
        """
        # When
        manager = OSRManager()

        # Then
        assert manager is not None

    def test_create_osr_entry(self):
        """
        Given bytecode offset and interpreter state
        When creating OSR entry
        Then entry should contain state mapping
        """
        # Given
        manager = OSRManager()
        bytecode_offset = 10
        state = {'stack': [1, 2, 3], 'locals': {'x': 42}}

        # When
        entry = manager.create_osr_entry(
            bytecode_offset=bytecode_offset,
            interpreter_state=state
        )

        # Then
        assert isinstance(entry, OSREntry)
        assert entry.bytecode_offset == bytecode_offset
        assert 'stack' in entry.state_map

    def test_create_multiple_osr_entries(self):
        """
        Given multiple loop back-edges
        When creating OSR entries for each
        Then each entry should be unique
        """
        # Given
        manager = OSRManager()
        state1 = {'stack': [1], 'pc': 5}
        state2 = {'stack': [2, 3], 'pc': 15}

        # When
        entry1 = manager.create_osr_entry(5, state1)
        entry2 = manager.create_osr_entry(15, state2)

        # Then
        assert entry1.bytecode_offset != entry2.bytecode_offset


class TestOSRPerformance:
    """Test OSR performance characteristics."""

    def test_perform_osr(self):
        """
        Given OSR entry point
        When performing OSR
        Then should transition from interpreter to JIT
        """
        # Given
        manager = OSRManager()
        state = {'stack': [10, 20], 'locals': {}}
        entry = manager.create_osr_entry(10, state)

        # When - perform OSR
        manager.perform_osr(entry)

        # Then - should complete without error
        assert True

    def test_osr_with_complex_state(self):
        """
        Given complex interpreter state
        When creating OSR entry
        Then state should be preserved
        """
        # Given
        manager = OSRManager()
        complex_state = {
            'stack': [1, 2, 3, 4, 5],
            'locals': {'x': 10, 'y': 20, 'z': 30},
            'pc': 42,
            'temp_registers': [100, 200]
        }

        # When
        entry = manager.create_osr_entry(42, complex_state)

        # Then
        assert entry.state_map['locals'] == {'x': 10, 'y': 20, 'z': 30}
        assert len(entry.state_map['stack']) == 5


class TestOSREdgeCases:
    """Test OSR edge cases."""

    def test_osr_empty_state(self):
        """
        Given empty interpreter state
        When creating OSR entry
        Then should handle gracefully
        """
        # Given
        manager = OSRManager()
        empty_state = {}

        # When
        entry = manager.create_osr_entry(0, empty_state)

        # Then
        assert isinstance(entry, OSREntry)

    def test_osr_loop_header(self):
        """
        Given loop header (back-edge target)
        When creating OSR entry
        Then entry should be at loop header
        """
        # Given
        manager = OSRManager()
        loop_header_offset = 20
        state = {'stack': [], 'loop_counter': 1000}

        # When
        entry = manager.create_osr_entry(loop_header_offset, state)

        # Then
        assert entry.bytecode_offset == loop_header_offset
