"""
Unit tests for IC state machine (RED phase).

Tests verify IC state transitions:
UNINITIALIZED → MONOMORPHIC → POLYMORPHIC → MEGAMORPHIC
"""
import pytest
from components.inline_caching.src.ic_state import ICState


class TestICState:
    """Test ICState enum values and transitions."""

    def test_ic_state_enum_has_four_states(self):
        """
        Given the ICState enum
        When checking available states
        Then it should have exactly 4 states
        """
        # Verify all states exist
        assert hasattr(ICState, 'UNINITIALIZED')
        assert hasattr(ICState, 'MONOMORPHIC')
        assert hasattr(ICState, 'POLYMORPHIC')
        assert hasattr(ICState, 'MEGAMORPHIC')

    def test_ic_state_values_are_distinct(self):
        """
        Given the ICState enum
        When comparing state values
        Then each state should have a unique value
        """
        states = [
            ICState.UNINITIALIZED,
            ICState.MONOMORPHIC,
            ICState.POLYMORPHIC,
            ICState.MEGAMORPHIC
        ]
        assert len(set(states)) == 4, "All states should be unique"

    def test_ic_state_can_be_compared(self):
        """
        Given IC states
        When comparing them
        Then equality should work correctly
        """
        assert ICState.UNINITIALIZED == ICState.UNINITIALIZED
        assert ICState.MONOMORPHIC == ICState.MONOMORPHIC
        assert ICState.UNINITIALIZED != ICState.MONOMORPHIC
