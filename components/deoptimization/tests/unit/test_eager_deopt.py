"""Tests for eager deoptimization."""
import pytest
from unittest.mock import Mock
from components.deoptimization.src.eager_deopt import EagerDeoptimizer
from components.deoptimization.src.deopt_types import JITState


class TestEagerDeoptimizer:
    def setup_method(self):
        self.mock_manager = Mock()
        self.deoptimizer = EagerDeoptimizer(self.mock_manager)

    def test_create_eager_deoptimizer(self):
        assert self.deoptimizer is not None

    def test_bailout_immediate(self):
        jit_state = JITState(registers={}, stack_pointer=0x7fff, instruction_pointer=0x1000)
        result = self.deoptimizer.bailout(
            function_id=1,
            bailout_point=100,
            jit_state=jit_state
        )
        assert result is not None

    def test_bailout_calls_manager(self):
        jit_state = JITState(registers={}, stack_pointer=0x7fff, instruction_pointer=0x1000)
        self.deoptimizer.bailout(1, 100, jit_state)
        assert self.mock_manager.deoptimize.called

    def test_bailout_critical_failures(self):
        jit_state = JITState(registers={}, stack_pointer=0x7fff, instruction_pointer=0x1000)
        result = self.deoptimizer.bailout(1, 50, jit_state)
        assert result is not None

    def test_multiple_bailouts(self):
        jit_state = JITState(registers={}, stack_pointer=0x7fff, instruction_pointer=0x1000)
        for i in range(3):
            self.deoptimizer.bailout(i, i * 10, jit_state)
        assert self.mock_manager.deoptimize.call_count == 3
